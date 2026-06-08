# save as inspect_honeypot.py and run: python inspect_honeypot.py
import sqlite3, os
DB = os.path.join(os.getcwd(), 'cyber_defense.db')
if not os.path.exists(DB):
    DB = os.path.join(os.getcwd(), 'honeypot.db') if os.path.exists('honeypot.db') else 'cyber_defense.db'
print("Using DB:", DB)
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
cur = conn.cursor()
def show_table(name):
    try:
        cols = cur.execute("PRAGMA table_info(%s)" % name).fetchall()
        print(f"\n{name} columns:")
        for c in cols:
            print(" ", c)
        rows = cur.execute(f"SELECT * FROM {name} LIMIT 5").fetchall()
        print(f"\nSample rows from {name}:")
        for r in rows:
            print(dict(r))
    except Exception as e:
        print(f"\n{name} not found or error:", e)

show_table('honeypot_events')
show_table('detections')
show_table('registration_requests')
show_table('honeypot_access')
conn.close()
