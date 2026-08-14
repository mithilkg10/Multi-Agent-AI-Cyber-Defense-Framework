# honeypot_test.py
import requests
r = requests.get("http://127.0.0.1:5001/test123", headers={"User-Agent":"MaliciousAgent"})
print("Honeypot status:", r.status_code)
print("Response length:", len(r.content))
