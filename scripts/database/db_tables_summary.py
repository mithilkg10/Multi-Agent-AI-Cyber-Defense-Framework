import sqlite3
import json

DB = "cyber_defense.db"

conn = sqlite3.connect(DB)
cur = conn.cursor()

tables = cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()

output = {}

for (t,) in tables:
    cols = [c[1] for c in cur.execute(f"PRAGMA table_info({t})")]
    count = cur.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
    output[t] = {"columns": cols, "rows_count": count}

print(json.dumps(output, indent=2))

conn.close()
