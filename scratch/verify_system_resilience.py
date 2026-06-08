import requests
import sqlite3
import time
import datetime
import random
import sys

# Configure UTF-8 stdout
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

PREDICT_URL = "http://127.0.0.1:5000/predict"

print("==========================================================")
print("🛡️  ABHEDYA SYSTEM RESILIENCE & ENFORCEMENT VERIFIER")
print("==========================================================\n")

# Clear old entries for test IPs in detections/blocklist to prevent collision
print("🧹 Cleaning old simulation records from SQLite tables...")
conn = sqlite3.connect("cyber_defense.db")
cur = conn.cursor()
cur.execute("DELETE FROM detections WHERE traffic_id IN ('198.51.100.5', '198.51.100.6', '198.51.100.8')")
cur.execute("DELETE FROM blocklist WHERE ip IN ('198.51.100.7', '198.51.100.5', '198.51.100.6', '198.51.100.8')")
cur.execute("DELETE FROM login_log WHERE ip_address = '198.51.100.7'")
cur.execute("DELETE FROM honeypot_events WHERE ip = '198.51.100.7'")
conn.commit()
conn.close()

# ----------------- 1. DDOS ATTACK SIMULATION -----------------
print("\n🔥 [STEP 1/4] Simulating DDoS Attack payload (IP: 198.51.100.5)...")
for i in range(5):
    flow = {
        "Rate": round(random.uniform(120.0, 200.0), 2),
        "Tot size": random.randint(1200, 1500),
        "Protocol Type": "TCP",
        "syn_flag_number": 1,
        "ack_flag_number": 0,
        "Time_To_Live": 32,
        "traffic_id": "198.51.100.5"
    }
    try:
        r = requests.post(PREDICT_URL, json=flow, timeout=3)
        print(f"  [DDoS Payload {i+1}] Status: {r.status_code} | final_score: {r.json().get('final_score'):.4f} | honeypot: {r.json().get('should_honeypot')}")
    except Exception as e:
        print(f"  [DDoS Payload {i+1}] Failed: {e}")
    time.sleep(0.1)


# ----------------- 2. SQLi ATTACK SIMULATION -----------------
print("\n🔥 [STEP 2/4] Simulating SQL Injection payload (IP: 198.51.100.6)...")
flow_sqli = {
    "Rate": 1.2,
    "Tot size": 340,
    "Protocol Type": "TCP",
    "syn_flag_number": 0,
    "ack_flag_number": 1,
    "Time_To_Live": 64,
    "traffic_id": "198.51.100.6",
    "username": "' OR 1=1 --"
}
try:
    r = requests.post(PREDICT_URL, json=flow_sqli, timeout=3)
    print(f"  [SQLi Payload] Status: {r.status_code} | final_score: {r.json().get('final_score'):.4f} | honeypot: {r.json().get('should_honeypot')}")
except Exception as e:
    print(f"  [SQLi Payload] Failed: {e}")


# ----------------- 3. SCAN ATTACK SIMULATION -----------------
print("\n🔥 [STEP 3/4] Simulating Network Scan payload (IP: 198.51.100.8)...")
for i, port in enumerate([22, 80, 443]):
    flow_scan = {
        "Rate": 5.0,
        "Tot size": 64,
        "Protocol Type": "TCP",
        "syn_flag_number": 1,
        "ack_flag_number": 0,
        "Time_To_Live": 64,
        "traffic_id": "198.51.100.8",
        "dst_port": port
    }
    try:
        r = requests.post(PREDICT_URL, json=flow_scan, timeout=3)
        print(f"  [Scan Port {port}] Status: {r.status_code} | final_score: {r.json().get('final_score'):.4f} | honeypot: {r.json().get('should_honeypot')}")
    except Exception as e:
        print(f"  [Scan Payload] Failed: {e}")
    time.sleep(0.1)


# ----------------- 4. BRUTEFORCE ATTACK & ANOMALY DETECTOR LOOP -----------------
print("\n🔥 [STEP 4/4] Simulating Bruteforce logs directly to DB (IP: 198.51.100.7)...")
print("  Inserting 5 failed login records to 'login_log' table...")
conn = sqlite3.connect("cyber_defense.db")
cur = conn.cursor()
ts_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
for i in range(5):
    cur.execute("""
        INSERT INTO login_log (user_id, ip_address, status, login_time)
        VALUES (NULL, '198.51.100.7', 'fail (admin)', ?)
    """, (ts_now,))
conn.commit()
conn.close()

print("  Waiting 5 seconds for background anomaly detector loop to evaluate and trigger enforcement...")
time.sleep(5)


# ----------------- VERIFICATION -----------------
print("\n==========================================================")
print("📊 VERIFYING ENFORCEMENT & SYSTEM RESILIENCE OUTPUTS")
print("==========================================================")

conn = sqlite3.connect("cyber_defense.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# 1. Check detections
print("\n📁 Checking detections table for model-logged telemetry:")
cur.execute("SELECT id, created_at, traffic_id, model_used, prediction, final_score, should_honeypot, mitre_id, xai_explanation FROM detections WHERE traffic_id IN ('198.51.100.5', '198.51.100.6', '198.51.100.8') ORDER BY id ASC")
det_rows = cur.fetchall()
print(f"  Detections Count: {len(det_rows)} (Expected: 9)")
for r in det_rows:
    print(f"  - IP: {r['traffic_id']} | Model: {r['model_used']} | Pred: {r['prediction']} | Score: {r['final_score']:.4f} | Honeypot: {r['should_honeypot']} | MITRE: {r['mitre_id']} | XAI: {r['xai_explanation']}")

# 2. Check anomaly detector logs & blocklist
print("\n📁 Checking blocklist table for automated IP blocks:")
cur.execute("SELECT * FROM blocklist WHERE ip = '198.51.100.7'")
block_rows = cur.fetchall()
print(f"  Blocked IPs: {len(block_rows)} (Expected: 1)")
for b in block_rows:
    print(f"  - IP: {b['ip']} | Reason: {b['reason']} | Blocked At: {b['created_at']} | Expires At: {b['expires_at']}")

print("\n📁 Checking honeypot_events table for anomaly flags:")
cur.execute("SELECT * FROM honeypot_events WHERE ip = '198.51.100.7'")
event_rows = cur.fetchall()
print(f"  Anomaly Events Count: {len(event_rows)} (Expected: >= 1)")
for ev in event_rows:
    print(f"  - IP: {ev['ip']} | Event: {ev['event']} | Anomaly Score: {ev['score']:.4f} | Detected At: {ev['created_at']}")

conn.close()
print("\n==========================================================")
print("✅ Resilience Verification Session Completed.")
print("==========================================================")
