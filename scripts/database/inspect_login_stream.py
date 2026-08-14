import sqlite3

DB = "cyber_defense.db"   # change to honeypot.db when needed

conn = sqlite3.connect(DB)
cur = conn.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("TABLES:", cur.fetchall())

cur.execute("SELECT * FROM login_log_stream ORDER BY id DESC LIMIT 20")
rows = cur.fetchall()
for r in rows:
    print(r)

conn.close()
