# fix_sqlite.py
import sqlite3, os, sys, time

DB = "cyber_defense.db"

def show_files():
    for name in sorted([DB, DB + "-wal", DB + "-shm"]):
        if os.path.exists(name):
            print(f"{name}: {os.path.getsize(name):,} bytes")
        else:
            print(f"{name}: (not present)")

def do_checkpoint():
    print("Opening DB and running PRAGMA wal_checkpoint(TRUNCATE);")
    conn = sqlite3.connect(DB, timeout=10, check_same_thread=False)
    cur = conn.cursor()
    try:
        cur.execute("PRAGMA wal_checkpoint(TRUNCATE);")
        res = cur.fetchall()
        print("checkpoint result:", res)
    except Exception as e:
        print("checkpoint error:", e)
    finally:
        try:
            conn.commit()
            conn.close()
        except:
            pass

def try_vacuum():
    print("\nAttempting VACUUM (this may need extra disk space).")
    conn = sqlite3.connect(DB, timeout=10, check_same_thread=False)
    cur = conn.cursor()
    try:
        cur.execute("VACUUM;")
        print("VACUUM completed.")
    except Exception as e:
        print("VACUUM failed:", e)
    finally:
        try:
            conn.commit()
            conn.close()
        except:
            pass

if __name__ == "__main__":
    print("Before:")
    show_files()
    do_checkpoint()
    print("\nAfter checkpoint:")
    show_files()

    # Only run VACUUM if you explicitly want to (pass arg 'vacuum')
    if len(sys.argv) > 1 and sys.argv[1].lower() == "vacuum":
        try_vacuum()
        print("\nAfter VACUUM:")
        show_files()
    else:
        print("\nIf you want VACUUM as well, run: python fix_sqlite.py vacuum")
        print("But DON'T run VACUUM if you don't have significantly more free disk space.")
