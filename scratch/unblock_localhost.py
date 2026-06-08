# scratch/unblock_localhost.py
import sqlite3

conn = sqlite3.connect("cyber_defense.db")
cur = conn.cursor()

# Remove localhost blocks
cur.execute("DELETE FROM blocklist WHERE ip = '127.0.0.1'")
conn.commit()
print("Successfully removed 127.0.0.1 from blocklist.")

# Check current active blocklist
cur.execute("SELECT * FROM blocklist ORDER BY id DESC LIMIT 5")
for r in cur.fetchall():
    print(r)

conn.close()
