# force_block_test.py
import sqlite3, datetime
DB = "cyber_defense.db"
ip="45.0.0.55"
conn=sqlite3.connect(DB)
cur=conn.cursor()
cur.execute("INSERT INTO blocklist (ip, reason, created_at, expires_at) VALUES (?, ?, ?, ?)",
            (ip, "forced-test-block", datetime.datetime.now().isoformat(),
             (datetime.datetime.now()+datetime.timedelta(hours=6)).isoformat()))
conn.commit()
conn.close()
print("Inserted block for", ip)
