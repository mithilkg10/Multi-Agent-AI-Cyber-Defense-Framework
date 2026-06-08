import requests
import json
import sys
import time

# Configure UTF-8 stdout
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

session = requests.Session()

# 1. Login as Admin
print("Logging in to Abhedya...")
login_url = "http://127.0.0.1:5000/"
credentials = {"username": "admin", "password": "Admin@123"}
r_login = session.post(login_url, data=credentials, timeout=5)
print(f"Login status: {r_login.status_code}")
if r_login.status_code != 200 or "Invalid" in r_login.text:
    print("❌ Failed to login!")
    sys.exit(1)

# 2. Trigger each attack simulation
attacks = ["ddos", "sqli", "bruteforce", "scan"]
attacker_ips = {
    "ddos": "198.51.100.5",
    "sqli": "198.51.100.6",
    "bruteforce": "198.51.100.7",
    "scan": "198.51.100.8"
}

print("\nStarting attack simulations...")
for attack in attacks:
    ip = attacker_ips[attack]
    print(f"\nTriggering {attack.upper()} simulation from IP {ip}...")
    sim_url = "http://127.0.0.1:5000/admin/simulate_attack"
    data = {"type": attack, "ip": ip}
    r_sim = session.post(sim_url, data=data, timeout=5)
    print(f"Simulation trigger status: {r_sim.status_code}")
    print(f"Response: {r_sim.text}")
    time.sleep(1)

print("\nWaiting 5 seconds for background simulation threads to execute...")
time.sleep(5)

# 3. Check detections in SQL database for these IPs
print("\nVerifying database logging & security enforcement...")
import sqlite3
conn = sqlite3.connect("cyber_defense.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()

for attack, ip in attacker_ips.items():
    cur.execute("SELECT id, created_at, traffic_id, model_used, prediction, final_score, should_honeypot, mitre_id, xai_explanation FROM detections WHERE traffic_id = ? ORDER BY id DESC", (ip,))
    rows = cur.fetchall()
    print(f"\n[IP: {ip} - {attack.upper()}] Log count: {len(rows)}")
    if rows:
        print("Last logged detection:")
        print(dict(rows[0]))
    else:
        print(f"⚠️ No detections found in detections table for {ip}!")

# Also check blocklist
print("\nChecking blocklist entries...")
cur.execute("SELECT * FROM blocklist ORDER BY id DESC LIMIT 5")
block_rows = cur.fetchall()
for b in block_rows:
    print(dict(b))

conn.close()
print("\nDone.")
