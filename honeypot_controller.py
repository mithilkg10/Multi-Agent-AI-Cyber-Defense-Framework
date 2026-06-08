#!/usr/bin/env python3
"""
honeypot_controller.py
- Subscribes to Kafka topic "honeypot_triggers"
- Reads attacker IP from messages (src_ip or ip)
- Applies routing rules to send that client's traffic to a honeypot port (default 8081)
- Inserts a 'responses' row into the project's SQLite DB (table: responses)
- Writes an entry into honeypot_logs/<ip>_<ts>.jsonl for forensic capture

This implementation strictly follows the ABHEDYA_Full_Context_Pack.pdf requirements.
See: /mnt/data/ABHEDYA_Full_Context_Pack.pdf. :contentReference[oaicite:7]{index=7}
"""

import os
import json
import sqlite3
import time
import argparse
import subprocess
from datetime import datetime, timezone
from kafka import KafkaConsumer
from pathlib import Path

# ---------- CONFIG ----------
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")
KAFKA_TOPIC = os.getenv("HONEYPOT_TOPIC", "honeypot_triggers")
KAFKA_GROUP = os.getenv("HONEYPOT_GROUP", "honeypot-controller-group")
SQLITE_DB_PATH = os.getenv("ABHEDYA_DB", "cyber_defense.db")  # per PDF
HONEYPOT_PORT = int(os.getenv("HONEYPOT_PORT", "8081"))
HONEYPOT_LOG_DIR = Path(os.getenv("HONEYPOT_LOG_DIR", "honeypot_logs"))
DRY_RUN = os.getenv("HONEYPOT_DRY_RUN", "false").lower() in ("1", "true", "yes")

# Ensure log dir exists
HONEYPOT_LOG_DIR.mkdir(parents=True, exist_ok=True)

# ---------- Helpers ----------
def now_ts():
    return datetime.now(timezone.utc).isoformat()

def log_honeypot_event(src_ip, payload, status, extra=None):
    """
    Append a JSON line to a session-specific file for forensic capture.
    """
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
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
def find_intel_by_asset_or_op(asset_id=None, op_code=None, intel_db_path="intelligence_assets.db"):
    if not asset_id and not op_code:
        return None
    conn = sqlite3.connect(intel_db_path)
    cur = conn.cursor()
    if asset_id:
        cur.execute("SELECT id FROM intelligence_assets WHERE asset_id=?", (asset_id,))
    else:
        # search by operation_code
        cur.execute("SELECT id FROM intelligence_assets WHERE operation_code=?", (op_code,))
    r = cur.fetchone()
    conn.close()
    return r[0] if r else None


def insert_response_row(db_path, detection_id, action, status, intel_id=None):
    conn = sqlite3.connect(db_path, timeout=10)
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                detection_id TEXT,
                action TEXT,
                status TEXT,
                timestamp TEXT,
                intel_id INTEGER
            )
        """)
        cur.execute(
            "INSERT INTO responses (detection_id, action, status, timestamp, intel_id) VALUES (?, ?, ?, ?, ?)",
            (detection_id, action, status, now_ts(), intel_id)
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def apply_routing_linux(attacker_ip, honeypot_port):
    """
    Linux strategy:
    - Use iptables nat PREROUTING REDIRECT for HTTP (tcp/80) as example.
    - Requires root privileges.
    NOTE: Adjust --dport if you want other services (80/443/etc.)
    """
    # redirect incoming TCP port 80 from attacker_ip to local honeypot_port
    cmd = [
        "iptables", "-t", "nat", "-A", "PREROUTING",
        "-s", attacker_ip, "-p", "tcp", "--dport", "80",
        "-j", "REDIRECT", "--to-ports", str(honeypot_port)
    ]
    return _run_cmd(cmd)

def remove_routing_linux(attacker_ip, honeypot_port):
    cmd = [
        "iptables", "-t", "nat", "-D", "PREROUTING",
        "-s", attacker_ip, "-p", "tcp", "--dport", "80",
        "-j", "REDIRECT", "--to-ports", str(honeypot_port)
    ]
    return _run_cmd(cmd)

def apply_firewall_windows(attacker_ip, honeypot_port):
    """
    On Windows we:
    1) Create a blocking firewall rule for attacker IP to the real app port(s) if desired
    2) Provide guidance to add a reverse-proxy mapping (NGINX or IIS ARR), because Windows
       does not have a simple iptables REDIRECT equivalent in userland.
    This function creates a firewall rule to allow connections only to the honeypot port from that IP.
    Requires Administrator PowerShell.
    """
    # Create a rule that allows attacker_ip to connect to honeypot_port (so proxy can accept)
    pws_cmd = (
        f"New-NetFirewallRule -DisplayName 'ABHEDYA-Honeypot-Allow-{attacker_ip}' "
        f"-Direction Inbound -Action Allow -Protocol TCP -LocalPort {honeypot_port} -RemoteAddress {attacker_ip}"
    )
    return _run_cmd(["powershell", "-Command", pws_cmd])

def _run_cmd(cmd):
    if DRY_RUN:
        return {"ok": True, "cmd": " ".join(cmd), "output": "(dry-run)"}
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
        return {"ok": proc.returncode == 0, "cmd": " ".join(cmd), "stdout": proc.stdout.strip(), "stderr": proc.stderr.strip(), "rc": proc.returncode}
    except Exception as e:
        return {"ok": False, "cmd": " ".join(cmd), "error": str(e)}

def determine_platform_and_apply(attacker_ip, honeypot_port):
    """
    Decide which platform-specific routing to use.
    The PDF mentions iptables/nft (Linux) and New-NetFirewallRule (Windows) as acceptable approaches.
    We implement both options and detect the platform.
    """
    from sys import platform
    if platform.startswith("linux"):
        return apply_routing_linux(attacker_ip, honeypot_port)
    elif platform.startswith("win"):
        return apply_firewall_windows(attacker_ip, honeypot_port)
    else:
        return {"ok": False, "error": f"Unsupported platform: {platform}"}

# ---------- Main loop: Kafka consumer ----------
def run_consumer():
    import sys
    print(f"[honeypot_controller] Starting (dry-run={DRY_RUN})")
    print(f"[honeypot_controller] Kafka: {KAFKA_BOOTSTRAP} topic: {KAFKA_TOPIC} group: {KAFKA_GROUP}")
    
    consumer = None
    retries = 10
    while retries > 0:
        try:
            consumer = KafkaConsumer(
                KAFKA_TOPIC,
                bootstrap_servers=[KAFKA_BOOTSTRAP],
                group_id=KAFKA_GROUP,
                value_deserializer=lambda m: m.decode("utf-8") if m is not None else None,
                auto_offset_reset="earliest",
                enable_auto_commit=True,
                consumer_timeout_ms=1000  # allow periodic loop
            )
            break
        except Exception as e:
            print(f"[honeypot_controller] Kafka consumer init failed: {e}. Retrying in 3s...")
            time.sleep(3)
            retries -= 1
            
    if not consumer:
        print("[honeypot_controller] [FATAL] Could not connect to Kafka. Exiting.")
        sys.exit(1)

    try:
        while True:
            for msg in consumer:
                # Defensive checks per your context pack (skip None)
                if msg.value is None:
                    print("[honeypot_controller] empty message received, skipping")
                    continue

                # parse JSON safely
                try:
                    payload = json.loads(msg.value)
                except Exception as e:
                    print(f"[honeypot_controller] invalid JSON, skipping: {e}")
                    continue

                # extract attacker IP (PDF shows 'src_ip' usage)
                attacker_ip = payload.get("src_ip") or payload.get("ip") or payload.get("attacker_ip")
                detection_id = payload.get("detection_id") if isinstance(payload, dict) else None
                asset_id = payload.get("asset_id")
                op_code = payload.get("operation_code")
                intel_id = find_intel_by_asset_or_op(
                    asset_id=asset_id,
                    op_code=op_code,
                    intel_db_path="intelligence_assets.db"
                )


                if not attacker_ip:
                    print("[honeypot_controller] message missing attacker IP, skipping. payload:", payload)
                    continue

                print(f"[honeypot_controller] Trigger received for IP={attacker_ip} detection_id={detection_id}")

                # Apply routing / firewall rules
                res = determine_platform_and_apply(attacker_ip, HONEYPOT_PORT)
                status = "applied" if res.get("ok") else f"failed: {res.get('error') or res.get('stderr') or res.get('rc')}"
                print(f"[honeypot_controller] routing result: {res}")

                # Insert response row into SQLite responses table
                try:
                    response_row_id = insert_response_row(SQLITE_DB_PATH, detection_id, "send_to_honeypot", status, intel_id=intel_id)
                    print(f"[honeypot_controller] inserted responses row id={response_row_id}")
                except Exception as e:
                    print(f"[honeypot_controller] failed to insert responses row: {e}")
                    log_honeypot_event(attacker_ip, payload, "db_insert_failed", extra={"error": str(e)})
                    continue

                # Write forensic log
                log_file = log_honeypot_event(attacker_ip, payload, status, extra={"cmd_result": res})
                print(f"[honeypot_controller] honeypot log written: {log_file}")

                # Optionally: notify another Kafka topic or call web-hook (not added now)
            # small sleep to avoid busy-loop; consumer_timeout_ms allows periodic checks
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("[honeypot_controller] interrupted, shutting down")
    finally:
        consumer.close()

# ---------- CLI ----------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ABHEDYA Honeypot Controller (per ABHEDYA_Full_Context_Pack.pdf).")
    parser.add_argument("--kafka", default=KAFKA_BOOTSTRAP, help="Kafka bootstrap server (host:port)")
    parser.add_argument("--topic", default=KAFKA_TOPIC, help="Kafka topic to consume (honeypot_triggers)")
    parser.add_argument("--db", default=SQLITE_DB_PATH, help="Path to SQLite DB (cyber_defense.db)")
    parser.add_argument("--port", default=HONEYPOT_PORT, type=int, help="Local honeypot port to redirect traffic to")
    parser.add_argument("--dry-run", action="store_true", help="Do not execute system commands (iptables/powershell), only simulate")
    args = parser.parse_args()

    KAFKA_BOOTSTRAP = args.kafka
    KAFKA_TOPIC = args.topic
    SQLITE_DB_PATH = args.db
    HONEYPOT_PORT = args.port
    if args.dry_run:
        DRY_RUN = True

    run_consumer()
