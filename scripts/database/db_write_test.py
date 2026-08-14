import sqlite3
import sys

DB = "cyber_defense.db"

print("\n--- RUNNING SQLITE WRITE TEST ---\n")

try:
    conn = sqlite3.connect(DB, timeout=5)
    cur = conn.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS _lock_test (id INTEGER PRIMARY KEY)")
    conn.commit()

    cur.execute("INSERT INTO _lock_test DEFAULT VALUES")
    conn.commit()

    print("Write test OK — DB is NOT LOCKED.")

    conn.close()
except Exception as e:
    print("ERROR opening DB:", e)
    sys.exit(1)
