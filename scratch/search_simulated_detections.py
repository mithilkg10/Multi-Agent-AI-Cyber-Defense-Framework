import sqlite3

conn = sqlite3.connect("cyber_defense.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute("SELECT id, created_at, traffic_id, model_used, prediction, final_score, should_honeypot, mitre_id, xai_explanation FROM detections WHERE traffic_id LIKE '198.51.100.%'")
rows = cur.fetchall()
print(f"Found {len(rows)} detections for simulated IPs:")
for r in rows:
    print(dict(r))

cur.execute("SELECT * FROM blocklist WHERE ip LIKE '198.51.100.%'")
blocks = cur.fetchall()
print(f"\nFound {len(blocks)} blocklist entries for simulated IPs:")
for b in blocks:
    print(dict(b))

conn.close()
