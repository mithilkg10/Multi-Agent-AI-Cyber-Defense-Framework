import sqlite3
import json

conn = sqlite3.connect("cyber_defense.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()
cur.execute("SELECT * FROM detections ORDER BY id DESC LIMIT 2")
rows = cur.fetchall()
for r in rows:
    print(dict(r))
conn.close()
