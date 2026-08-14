# e2e_test.py
import requests, time, sqlite3, sys
base = "http://127.0.0.1:5000"
honeypot_db = "honeypot.db"

s = requests.Session()
# 1. do suspicious login
r = s.post(base + "/", data={"username":"x","password":"whatever"}, allow_redirects=True)
print("login status", r.status_code, "url=", r.url)

# 2. if redirected to fake_dashboard, click Intelligence Database link
if "/fake_dashboard" in r.url or "fake_dashboard" in r.text:
    # find the link — assume honeypot_link present as href in template
    # fallback: manually build honeypot url with sid if present as cookie or session param
    # For simple test, call honeypot directly:
    sid = None
    # Try to read sid cookie
    for k,v in s.cookies.items():
        if k == 'sid':
            sid = v
    if not sid:
        sid = "testrun-" + str(int(time.time()))
    hp = f"http://127.0.0.1:5001/?sid={sid}"
    r2 = s.get(hp)
    print("Accessed honeypot:", r2.status_code, hp)
    time.sleep(1)

# 3. Inspect honeypot.db
try:
    conn = sqlite3.connect(honeypot_db)
    cur = conn.cursor()
    cur.execute("SELECT id, sid, ip_address, endpoint, created_at FROM honeypot_access ORDER BY id DESC LIMIT 5")
    rows = cur.fetchall()
    print("Honeypot recent entries:", rows)
    conn.close()
except Exception as e:
    print("Could not read honeypot DB:", e)
    sys.exit(1)
