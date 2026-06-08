import time
import sqlite3
import os
import datetime
import random
import math

DB_NAME = "cyber_defense.db"

# ---------------------------------------------------
# Ensure blocklist + honeypot_events table exists
# ---------------------------------------------------
def init_anomaly_tables():
    conn = sqlite3.connect(DB_NAME, timeout=20)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS blocklist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT,
            reason TEXT,
            created_at TEXT,
            expires_at TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS honeypot_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT,
            sid TEXT,
            event TEXT,
            score REAL,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


# ---------------------------------------------------
# Simple anomaly scoring model
# ---------------------------------------------------
def compute_score(ip, recent_rows):
    # Retrieve configuration parameters from SQLite dynamically
    coeff_rep = 0.35
    coeff_fail = 0.40
    try:
        conn = sqlite3.connect(DB_NAME, timeout=5)
        cur = conn.cursor()
        cur.execute("SELECT val FROM config WHERE key = 'bruteforce_reputation_coeff'")
        row_rep = cur.fetchone()
        if row_rep:
            coeff_rep = float(row_rep[0])
        cur.execute("SELECT val FROM config WHERE key = 'bruteforce_failrate_coeff'")
        row_fail = cur.fetchone()
        if row_fail:
            coeff_fail = float(row_fail[0])
        conn.close()
    except Exception:
        pass

    # ip -> string, recent_rows -> list of recent login_log rows for that ip/account
    score = 0.0
    # IP reputation check
    is_malicious_ip = ip.startswith("45.") or ip.startswith("144.") or ip.startswith("23.") or ip.startswith("198.51.100.")
    if is_malicious_ip:
        score += coeff_rep
        
    # failed rate
    fails = sum(1 for r in recent_rows if "fail" in (r.get("status") or "").lower())
    tot = max(1, len(recent_rows))
    fail_rate = fails / tot
    score += coeff_fail * fail_rate  # weight for fail rate
    
    # unusual UA detection (example)
    uas = {r.get("ua","") for r in recent_rows}
    if len(uas) > 1:
        score += 0.15
        
    # time-based weight (night scan indicator)
    hour = datetime.datetime.now().hour
    if 1 <= hour <= 4:
        score += 0.10
    return min(1.0, score)


# ---------------------------------------------------
# Insert into blocklist
# ---------------------------------------------------
def block_ip(ip, reason, hours=6):
    expires = (datetime.datetime.now() +
               datetime.timedelta(hours=hours)).isoformat()

    conn = sqlite3.connect(DB_NAME, timeout=20)
    cur = conn.cursor()
    # Check if already blocked to prevent constraint violation or redundancy
    cur.execute("SELECT id FROM blocklist WHERE ip = ? AND (expires_at IS NULL OR expires_at > ?)", (ip, datetime.datetime.now().isoformat()))
    if not cur.fetchone():
        cur.execute("""
            INSERT INTO blocklist (ip, reason, created_at, expires_at)
            VALUES (?, ?, ?, ?)
        """, (ip, reason, datetime.datetime.now().isoformat(), expires))
        conn.commit()
    conn.close()

    print(f"🚫 BLOCKED IP: {ip} | reason={reason}")


# ---------------------------------------------------
# Log anomaly/score into honeypot_events table
# ---------------------------------------------------
def log_event(ip, sid, score):
    conn = sqlite3.connect(DB_NAME, timeout=20)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO honeypot_events (ip, sid, event, score, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (ip, sid, "anomaly_detected", score, datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()


# ---------------------------------------------------
# MAIN LOOP
# ---------------------------------------------------
def run_anomaly_detector():
    init_anomaly_tables()
    print("🔍 Anomaly detector running...")

    while True:
        time.sleep(3)  # don't overload CPU

        try:
            # Query block threshold dynamically
            block_threshold = 0.90
            try:
                conn_cfg = sqlite3.connect(DB_NAME, timeout=5)
                cur_cfg = conn_cfg.cursor()
                cur_cfg.execute("SELECT val FROM config WHERE key = 'bruteforce_block_threshold'")
                row_t = cur_cfg.fetchone()
                if row_t:
                    block_threshold = float(row_t[0])
                conn_cfg.close()
            except Exception:
                pass

            conn = sqlite3.connect(DB_NAME, timeout=20)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("""
                SELECT ip_address
                FROM login_log
                ORDER BY id DESC
                LIMIT 10
            """)
            recent_ips = [r["ip_address"] for r in cur.fetchall() if r["ip_address"]]
            
            for ip in set(recent_ips):
                cur.execute("""
                    SELECT ip_address, status
                    FROM login_log
                    WHERE ip_address = ?
                    ORDER BY id DESC
                    LIMIT 5
                """, (ip,))
                recent_rows = [dict(row) for row in cur.fetchall()]
                
                score = compute_score(ip, recent_rows)
                # store anomaly event
                log_event(ip, None, score)

                if score >= block_threshold:
                    block_ip(ip, f"High anomaly score: {score:.2f}")
            conn.close()
        except Exception as e:
            print("⚠️ Anomaly detector loop error:", e)



# ---------------------------------------------------
# Run standalone
# ---------------------------------------------------
if __name__ == "__main__":
    run_anomaly_detector()
