import sqlite3
import json

conn = sqlite3.connect("cyber_defense.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute("SELECT id, created_at, traffic_id, model_used, prediction, final_score FROM detections ORDER BY id DESC LIMIT 10")
rows = cur.fetchall()
print("=== LAST 10 DETECTIONS ===")
for r in rows:
    print(dict(r))

cur.execute("SELECT COUNT(*) FROM detections")
print("Total detections in DB:", cur.fetchone()[0])

conn.close()
