import requests
import time
import random

url = "http://127.0.0.1:5000/predict"
ip = "198.51.100.9"

print("Triggering 5 manual DDoS POSTs to /predict...")
for i in range(5):
    flow = {
        "Rate": round(random.uniform(120.0, 200.0), 2),
        "Tot size": random.randint(1200, 1500),
        "Protocol Type": "TCP",
        "syn_flag_number": 1,
        "ack_flag_number": 0,
        "Time_To_Live": 32,
        "traffic_id": ip
    }
    try:
        r = requests.post(url, json=flow, timeout=3)
        print(f"POST {i+1} Status: {r.status_code}, Response: {r.text[:100]}")
    except Exception as e:
        print(f"POST {i+1} Failed: {e}")
    time.sleep(0.1)

print("\nVerifying if they got logged...")
import sqlite3
conn = sqlite3.connect("cyber_defense.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()
cur.execute("SELECT id, created_at, traffic_id, model_used, prediction, final_score FROM detections WHERE traffic_id = ?", (ip,))
rows = cur.fetchall()
print(f"Found {len(rows)} detections in DB.")
for r in rows:
    print(dict(r))
conn.close()
