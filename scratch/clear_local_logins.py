# scratch/clear_local_logins.py
import sqlite3

conn = sqlite3.connect("cyber_defense.db")
cur = conn.cursor()

# Delete login log attempts for localhost
cur.execute("DELETE FROM login_log WHERE ip_address = '127.0.0.1'")
# Delete blocklist entries for localhost
cur.execute("DELETE FROM blocklist WHERE ip = '127.0.0.1'")
conn.commit()

print("Cleaned up localhost login history and active blocks.")

# Verify
cur.execute("SELECT COUNT(*) FROM login_log WHERE ip_address = '127.0.0.1'")
print("Localhost login log count:", cur.fetchone()[0])
cur.execute("SELECT COUNT(*) FROM blocklist WHERE ip = '127.0.0.1'")
print("Localhost blocklist count:", cur.fetchone()[0])

conn.close()
