# safe_vacuum.py
import sqlite3, time, sys, os

DB = "cyber_defense.db"
RETRIES = 6
SLEEP = 2  # seconds

def try_checkpoint(conn):
    cur = conn.cursor()
    cur.execute("PRAGMA wal_checkpoint(TRUNCATE);")
    return cur.fetchone()

def try_vacuum():
    conn = sqlite3.connect(DB, timeout=10)
    try:
        print("running VACUUM ... (needs free disk space)")
        conn.execute("VACUUM;")
        conn.commit()
        print("VACUUM OK")
    finally:
        conn.close()

if __name__ == "__main__":
    # ensure DB file exists
    if not os.path.exists(DB):
        print("DB not found:", DB); sys.exit(1)

    for attempt in range(1, RETRIES+1):
        try:
            conn = sqlite3.connect(DB, timeout=3)
            print(f"Attempt {attempt}: PRAGMA wal_checkpoint(TRUNCATE)")
            print("result:", try_checkpoint(conn))
            conn.close()
            break
        except sqlite3.OperationalError as e:
            print("checkpoint failed:", e)
            time.sleep(SLEEP)
    else:
        print("checkpoint retries failed - exiting")
        sys.exit(1)

    # Try VACUUM with retries for locked errors
    for attempt in range(1, RETRIES+1):
        try:
            try_vacuum()
            break
        except sqlite3.OperationalError as e:
            print(f"VACUUM attempt {attempt} failed:", e)
            if "database is locked" in str(e).lower():
                print("Database locked — ensure all app/consumer processes are stopped and retry.")
                time.sleep(SLEEP)
            else:
                raise
    print("Done")
