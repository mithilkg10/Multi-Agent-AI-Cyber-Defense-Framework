# insert_honeypot_events_correct.py
import sqlite3, os, random, datetime, json

DB = os.path.join(os.getcwd(), "cyber_defense.db")
if not os.path.exists(DB):
    DB = "cyber_defense.db"
conn = sqlite3.connect(DB)
cur = conn.cursor()

# create table if not present with the schema you have (non-destructive)
cur.execute("""
CREATE TABLE IF NOT EXISTS honeypot_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ip TEXT,
  sid TEXT,
  event TEXT,
  score REAL,
  created_at TEXT
)
""")
now = datetime.datetime.utcnow()
ips = ["103.23.5.12", "45.33.32.9", "117.197.138.1", "196.1.2.3", "34.120.10.5"]
for i in range(20):
    ip = random.choice(ips)
    sid = f"sid_{random.randint(1000,9999)}"
    ev = random.choice(["anomaly_detected", "recon", "bruteforce", "sql_injection"])
    score = round(random.random(), 4)
    t = (now - datetime.timedelta(minutes=random.randint(0,720))).isoformat()
    cur.execute("INSERT INTO honeypot_events (ip, sid, event, score, created_at) VALUES (?,?,?,?,?)", (ip, sid, ev, score, t))
conn.commit()
conn.close()
print("Inserted 20 sample rows into honeypot_events at", DB)
