import sqlite3
import json
import sys

DB = "cyber_defense.db"

print("\n--- RUNNING SQLITE INTEGRITY CHECK ---\n")

try:
    conn = sqlite3.connect(DB, timeout=5)
    cur = conn.cursor()

    # Integrity
    result = cur.execute("PRAGMA integrity_check;").fetchone()
    print("integrity_check:", result)

    # Tables
    tables = cur.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    print("\ntables:", tables)

    conn.close()
    print("\nOK — DB is readable and not locked.\n")

except Exception as e:
    print("\nERROR:", e)
    sys.exit(1)
