# scratch/query_retraining_log.py
import sqlite3

conn = sqlite3.connect("cyber_defense.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("--- config table contents ---")
try:
    cur.execute("SELECT * FROM config")
    for row in cur.fetchall():
        print(dict(row))
except Exception as e:
    print("Error querying config:", e)

print("\n--- dqn_retraining_log table contents ---")
try:
    cur.execute("SELECT * FROM dqn_retraining_log")
    for row in cur.fetchall():
        print(dict(row))
except Exception as e:
    print("Error querying dqn_retraining_log:", e)

conn.close()
