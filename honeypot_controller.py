#!/usr/bin/env python3
"""Kafka-driven honeypot routing controller for ABHEDYA.

The controller consumes ``honeypot_triggers`` events, validates the attacker IP,
applies a platform-specific routing/firewall action, records the response in the
SQLite response log, and writes a local forensic JSONL record.

System-level routing commands require elevated privileges. Use ``--dry-run`` while
validating configuration in a development environment.
"""

import argparse
import ipaddress
import json
import os
import sqlite3
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

from kafka import KafkaConsumer


# ---------- Configuration ----------
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")
KAFKA_TOPIC = os.getenv(
    "KAFKA_HONEYPOT_TOPIC",
    os.getenv("HONEYPOT_TOPIC", "honeypot_triggers"),
)
KAFKA_GROUP = os.getenv("HONEYPOT_GROUP", "honeypot-controller-group")
SQLITE_DB_PATH = os.getenv("ABHEDYA_DB", "cyber_defense.db")
INTELLIGENCE_DB_PATH = os.getenv("INTELLIGENCE_DB", "intelligence_assets.db")
HONEYPOT_PORT = int(os.getenv("HONEYPOT_PORT", "5001"))
HONEYPOT_LOG_DIR = Path(os.getenv("HONEYPOT_LOG_DIR", "honeypot_logs"))
DRY_RUN = os.getenv("HONEYPOT_DRY_RUN", "false").lower() in ("1", "true", "yes")

HONEYPOT_LOG_DIR.mkdir(parents=True, exist_ok=True)


# ---------- Helpers ----------
def now_ts():
    return datetime.now(timezone.utc).isoformat()


def normalize_ip(value):
    """Return a canonical IPv4/IPv6 string or ``None`` for invalid input."""
    if value is None:
        return None
    try:
        return str(ipaddress.ip_address(str(value).strip()))
    except ValueError:
        return None


def log_honeypot_event(src_ip, payload, status, extra=None):
    """Append one forensic JSON record for a validated attacker IP."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    safe_ip = src_ip.replace(":", "-")
    filename = HONEYPOT_LOG_DIR / f"{safe_ip}_{ts}.jsonl"
    entry = {
        "timestamp": now_ts(),
        "src_ip": src_ip,
        "payload": payload,
        "status": status,
    }
    if extra:
        entry["extra"] = extra
    with open(filename, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return str(filename)


def find_intel_by_asset_or_op(asset_id=None, op_code=None, intel_db_path=None):
    if not asset_id and not op_code:
        return None

    db_path = intel_db_path or INTELLIGENCE_DB_PATH
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    if asset_id:
        cur.execute("SELECT id FROM intelligence_assets WHERE asset_id=?", (asset_id,))
    else:
        cur.execute(
            "SELECT id FROM intelligence_assets WHERE operation_code=?", (op_code,)
        )
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None


def insert_response_row(db_path, detection_id, action, status, intel_id=None):
    conn = sqlite3.connect(db_path, timeout=10)
    try:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                detection_id TEXT,
                action TEXT,
                status TEXT,
                timestamp TEXT,
                intel_id INTEGER
            )
            """
        )
        cur.execute(
            "INSERT INTO responses (detection_id, action, status, timestamp, intel_id) VALUES (?, ?, ?, ?, ?)",
            (detection_id, action, status, now_ts(), intel_id),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def _run_cmd(cmd):
    if DRY_RUN:
        return {"ok": True, "cmd": " ".join(cmd), "output": "(dry-run)"}
    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        return {
            "ok": proc.returncode == 0,
            "cmd": " ".join(cmd),
            "stdout": proc.stdout.strip(),
            "stderr": proc.stderr.strip(),
            "rc": proc.returncode,
        }
    except Exception as exc:
        return {"ok": False, "cmd": " ".join(cmd), "error": str(exc)}


def apply_routing_linux(attacker_ip, honeypot_port):
    """Redirect HTTP traffic from one validated source IP to the local honeypot."""
    cmd = [
        "iptables",
        "-t",
        "nat",
        "-A",
        "PREROUTING",
        "-s",
        attacker_ip,
        "-p",
        "tcp",
        "--dport",
        "80",
        "-j",
        "REDIRECT",
        "--to-ports",
        str(honeypot_port),
    ]
    return _run_cmd(cmd)


def remove_routing_linux(attacker_ip, honeypot_port):
    cmd = [
        "iptables",
        "-t",
        "nat",
        "-D",
        "PREROUTING",
        "-s",
        attacker_ip,
        "-p",
        "tcp",
        "--dport",
        "80",
        "-j",
        "REDIRECT",
        "--to-ports",
        str(honeypot_port),
    ]
    return _run_cmd(cmd)


def apply_firewall_windows(attacker_ip, honeypot_port):
    """Create the Windows firewall rule used by the local deception workflow."""
    powershell_cmd = (
        f"New-NetFirewallRule -DisplayName 'ABHEDYA-Honeypot-Allow-{attacker_ip}' "
        f"-Direction Inbound -Action Allow -Protocol TCP -LocalPort {honeypot_port} "
        f"-RemoteAddress {attacker_ip}"
    )
    return _run_cmd(["powershell", "-Command", powershell_cmd])


def determine_platform_and_apply(attacker_ip, honeypot_port):
    """Apply the existing platform-specific response strategy."""
    from sys import platform

    if platform.startswith("linux"):
        return apply_routing_linux(attacker_ip, honeypot_port)
    if platform.startswith("win"):
        return apply_firewall_windows(attacker_ip, honeypot_port)
    return {"ok": False, "error": f"Unsupported platform: {platform}"}


# ---------- Kafka consumer ----------
def run_consumer():
    import sys

    print(f"[honeypot_controller] Starting (dry-run={DRY_RUN})")
    print(
        f"[honeypot_controller] Kafka: {KAFKA_BOOTSTRAP} "
        f"topic: {KAFKA_TOPIC} group: {KAFKA_GROUP}"
    )

    consumer = None
    retries = 10
    while retries > 0:
        try:
            consumer = KafkaConsumer(
                KAFKA_TOPIC,
                bootstrap_servers=[KAFKA_BOOTSTRAP],
                group_id=KAFKA_GROUP,
                value_deserializer=lambda message: (
                    message.decode("utf-8") if message is not None else None
                ),
                auto_offset_reset="earliest",
                enable_auto_commit=True,
                consumer_timeout_ms=1000,
            )
            break
        except Exception as exc:
            print(
                f"[honeypot_controller] Kafka consumer init failed: {exc}. "
                "Retrying in 3s..."
            )
            time.sleep(3)
            retries -= 1

    if not consumer:
        print("[honeypot_controller] [FATAL] Could not connect to Kafka. Exiting.")
        sys.exit(1)

    try:
        while True:
            for msg in consumer:
                if msg.value is None:
                    print("[honeypot_controller] empty message received, skipping")
                    continue

                try:
                    payload = json.loads(msg.value)
                except Exception as exc:
                    print(f"[honeypot_controller] invalid JSON, skipping: {exc}")
                    continue

                if not isinstance(payload, dict):
                    print("[honeypot_controller] non-object JSON payload, skipping")
                    continue

                raw_ip = (
                    payload.get("src_ip")
                    or payload.get("ip")
                    or payload.get("attacker_ip")
                )
                attacker_ip = normalize_ip(raw_ip)
                if not attacker_ip:
                    print(
                        "[honeypot_controller] message missing a valid attacker IP, "
                        "skipping. payload:",
                        payload,
                    )
                    continue

                detection_id = payload.get("detection_id")
                asset_id = payload.get("asset_id")
                op_code = payload.get("operation_code")
                intel_id = find_intel_by_asset_or_op(
                    asset_id=asset_id,
                    op_code=op_code,
                    intel_db_path=INTELLIGENCE_DB_PATH,
                )

                print(
                    f"[honeypot_controller] Trigger received for IP={attacker_ip} "
                    f"detection_id={detection_id}"
                )

                result = determine_platform_and_apply(attacker_ip, HONEYPOT_PORT)
                status = (
                    "applied"
                    if result.get("ok")
                    else f"failed: {result.get('error') or result.get('stderr') or result.get('rc')}"
                )
                print(f"[honeypot_controller] routing result: {result}")

                try:
                    response_row_id = insert_response_row(
                        SQLITE_DB_PATH,
                        detection_id,
                        "send_to_honeypot",
                        status,
                        intel_id=intel_id,
                    )
                    print(
                        f"[honeypot_controller] inserted responses row id={response_row_id}"
                    )
                except Exception as exc:
                    print(f"[honeypot_controller] failed to insert responses row: {exc}")
                    log_honeypot_event(
                        attacker_ip,
                        payload,
                        "db_insert_failed",
                        extra={"error": str(exc)},
                    )
                    continue

                log_file = log_honeypot_event(
                    attacker_ip,
                    payload,
                    status,
                    extra={"cmd_result": result},
                )
                print(f"[honeypot_controller] honeypot log written: {log_file}")

            time.sleep(0.5)
    except KeyboardInterrupt:
        print("[honeypot_controller] interrupted, shutting down")
    finally:
        consumer.close()


# ---------- CLI ----------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ABHEDYA honeypot routing controller")
    parser.add_argument(
        "--kafka", default=KAFKA_BOOTSTRAP, help="Kafka bootstrap server (host:port)"
    )
    parser.add_argument(
        "--topic", default=KAFKA_TOPIC, help="Kafka honeypot trigger topic"
    )
    parser.add_argument(
        "--db", default=SQLITE_DB_PATH, help="Path to the ABHEDYA SQLite database"
    )
    parser.add_argument(
        "--port",
        default=HONEYPOT_PORT,
        type=int,
        help="Local honeypot port used by the routing rule",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not execute system routing/firewall commands",
    )
    args = parser.parse_args()

    KAFKA_BOOTSTRAP = args.kafka
    KAFKA_TOPIC = args.topic
    SQLITE_DB_PATH = args.db
    HONEYPOT_PORT = args.port
    if args.dry_run:
        DRY_RUN = True

    run_consumer()
