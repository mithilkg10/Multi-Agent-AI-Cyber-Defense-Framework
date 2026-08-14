# bruteforce_test.py — run against your local app, small burst only
import requests, time
url = "http://127.0.0.1:5000/"
for username in ["admin", "admin1", "test", "x", "unknown"]:
    r = requests.post(url, data={"username":username, "password":"badpass"})
    print(username, r.status_code)
    time.sleep(0.5)  # gentle pace
