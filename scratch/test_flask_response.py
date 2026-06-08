# scratch/test_flask_response.py
import requests

try:
    r = requests.get("http://127.0.0.1:5000/", timeout=5)
    print("Status Code:", r.status_code)
    print("Content (first 200 chars):")
    print(r.text[:200])
except Exception as e:
    print("Request failed:", e)
