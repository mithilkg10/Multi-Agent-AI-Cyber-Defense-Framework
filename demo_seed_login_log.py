# demo_seed_login_log.py
import sqlite3, time, random, datetime, os, sys

DB = os.path.join(os.getcwd(), "cyber_defense.db")
IP_POOL = [
  "103.21.45.12", "49.36.120.5", "14.139.23.77", "117.197.22.5",
  "8.8.8.8", "51.15.123.45", "203.0.113.5", "140.238.0.1",
  "144.91.76.21", "45.77.34.2", "58.65.200.10", "144.76.6.1",
  "196.201.17.5", "52.58.123.12", "223.25.10.12"
]

def seed_loop(interval=5):
    print("Demo seeder starting — writing to", DB, "every", interval, "s. Ctrl-C to stop.")
    while True:
        try:
            conn = sqlite3.connect(DB, timeout=10)
            cur = conn.cursor()
            ip = random.choice(IP_POOL)
            ts = datetime.datetime.utcnow().isoformat()
            # status field included for compatibility
            cur.execute("INSERT INTO login_log (user_id, login_time, ip_address, status) VALUES (?, ?, ?, ?)",
                        (None, ts, ip, "success"))
            conn.commit()
            conn.close()
            print(f"[{ts}] Inserted {ip}")
        except Exception as e:
            print("Seeder DB error:", e)
        time.sleep(interval)

if __name__ == "__main__":
    interval = 5
    if len(sys.argv) > 1:
        try:
            interval = int(sys.argv[1])
        except:
            pass
    seed_loop(interval)
