# scratch/update_db_defaults.py
import sqlite3

conn = sqlite3.connect("cyber_defense.db")
cur = conn.cursor()

# Set highly resilient defaults
cur.execute("INSERT OR REPLACE INTO config (key, val) VALUES ('bruteforce_reputation_coeff', '0.35')")
cur.execute("INSERT OR REPLACE INTO config (key, val) VALUES ('bruteforce_failrate_coeff', '0.60')")
cur.execute("INSERT OR REPLACE INTO config (key, val) VALUES ('bruteforce_block_threshold', '0.55')")
cur.execute("INSERT OR REPLACE INTO config (key, val) VALUES ('threat_threshold', '0.65')")

conn.commit()
print("Successfully updated database config defaults.")

# Print updated config
cur.execute("SELECT * FROM config")
for r in cur.fetchall():
    print(r)

conn.close()
