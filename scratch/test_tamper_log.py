import sqlite3
import requests
import json
import sys

# Configure UTF-8 stdout
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# 1. Login
session = requests.Session()
data = {"username": "admin", "password": "Admin@123"}
session.post("http://127.0.0.1:5000/", data=data, timeout=5)

# 2. Get most recent detection row ID and original values
conn = sqlite3.connect("cyber_defense.db")
cur = conn.cursor()
cur.execute("SELECT id, final_score FROM detections ORDER BY id DESC LIMIT 1")
row = cur.fetchone()
if not row:
    print("No detections found to tamper with.")
    conn.close()
    sys.exit(0)

row_id, orig_score = row
print(f"Altering detection row ID {row_id}: changing score {orig_score} -> 0.999")

# Tamper with the score in the DB
cur.execute("UPDATE detections SET final_score = 0.999 WHERE id = ?", (row_id,))
conn.commit()
conn.close()

# 3. Call verify_logs
print("\nVerifying logs after database tampering...")
r_verify = session.post("http://127.0.0.1:5000/admin/verify_logs", timeout=5)
print(f"Verify Logs Status: {r_verify.status_code}")
print("Verify Logs JSON:", json.dumps(r_verify.json(), indent=2))

# 4. Revert tampering
conn = sqlite3.connect("cyber_defense.db")
cur = conn.cursor()
cur.execute("UPDATE detections SET final_score = ? WHERE id = ?", (orig_score, row_id))
conn.commit()
conn.close()
print(f"\n[REVERTED] Restored original score {orig_score} on row ID {row_id}.")

# 5. Verify again (should pass now)
print("\nVerifying logs after restoring database integrity...")
r_verify_revert = session.post("http://127.0.0.1:5000/admin/verify_logs", timeout=5)
print("Verify Logs JSON:", json.dumps(r_verify_revert.json(), indent=2))
