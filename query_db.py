# query_db.py
import sqlite3, sys, json

if len(sys.argv) < 3:
    print("Usage: python query_db.py <db_path> \"<SQL>\"")
    sys.exit(1)

db = sys.argv[1]
sql = sys.argv[2]

conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row
cur = conn.cursor()
try:
    cur.execute(sql)
    rows = cur.fetchall()
    if rows:
        cols = rows[0].keys()
        # Print header
        print(" | ".join(cols))
        print("-" * 80)
        for r in rows:
            print(" | ".join(str(r[c]) for c in cols))
    else:
        print("No rows returned.")
except Exception as e:
    print("SQL error:", e)
finally:
    conn.close()
