# save and run: python insert_honeypot_events.py
import sqlite3, os, datetime, random, json
DB = os.path.join(os.getcwd(), 'cyber_defense.db')
if not os.path.exists(DB):
    DB = 'cyber_defense.db'
conn = sqlite3.connect(DB)
cur = conn.cursor()
# create if missing (non-destructive)
cur.execute("""CREATE TABLE IF NOT EXISTS honeypot_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT,
    model TEXT,
    prediction TEXT,
    score REAL,
    meta TEXT,
    created_at TEXT
)""")
now = datetime.datetime.utcnow()
for i in range(12):
    eid = f"evt_{random.randint(1000,9999)}"
    model = random.choice(['hybrid','dqn','xgboost'])
    pred = random.choice(['suspicious','normal'])
    score = round(random.random(), 3)
    meta = json.dumps({"src_ip": random.choice(['103.23.5.12','45.33.32.9','117.197.138.1'])})
    t = (now - datetime.timedelta(minutes=random.randint(0,720))).isoformat()
    cur.execute("INSERT INTO honeypot_events (event_id, model, prediction, score, meta, created_at) VALUES (?,?,?,?,?,?)", (eid,model,pred,score,meta,t))
conn.commit()
conn.close()
print("Inserted sample honeypot_events")
