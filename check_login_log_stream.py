import sqlite3, time

def tail_last(n=10):
    conn = sqlite3.connect("cyber_defense.db")
    cur = conn.cursor()
    cur.execute("SELECT id, username, ip_address, event, timestamp FROM login_log_stream ORDER BY id DESC LIMIT ?", (n,))
    rows = cur.fetchall()
    conn.close()
    return rows

print("Last rows in login_log_stream:")
for r in tail_last(10):
    print(r)
