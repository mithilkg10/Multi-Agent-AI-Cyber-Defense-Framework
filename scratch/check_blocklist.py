# scratch/check_blocklist.py
import sqlite3

conn = sqlite3.connect("cyber_defense.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("--- blocklist table ---")
cur.execute("SELECT * FROM blocklist")
rows = cur.fetchall()
for r in rows:
    print(dict(r))

print("\n--- honeypot_events table (last 5) ---")
cur.execute("SELECT * FROM honeypot_events ORDER BY id DESC LIMIT 5")
rows = cur.fetchall()
for r in rows:
    print(dict(r))

conn.close()
