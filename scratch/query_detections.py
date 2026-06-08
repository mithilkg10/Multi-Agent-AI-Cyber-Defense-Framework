# scratch/query_detections.py
import sqlite3

conn = sqlite3.connect("cyber_defense.db")
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM detections")
count = cur.fetchone()[0]
print("Total rows in detections table:", count)

cur.execute("SELECT COUNT(*) FROM detections WHERE raw IS NOT NULL AND traffic_id IS NOT NULL")
count_raw = cur.fetchone()[0]
print("Rows with non-null raw and traffic_id:", count_raw)

if count_raw > 0:
    cur.execute("SELECT raw, prediction, final_score FROM detections WHERE raw IS NOT NULL AND traffic_id IS NOT NULL LIMIT 1")
    row = cur.fetchone()
    print("Sample raw detection row:")
    print("Raw features:", row[0][:200] + "...")
    print("Prediction:", row[1])
    print("Final Score:", row[2])

conn.close()
