import requests
import sys

# Configure UTF-8 stdout
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

url = "http://127.0.0.1:5000/predict"
print("GETting /predict...")
try:
    r = requests.get(url, timeout=5)
    print(f"Status Code: {r.status_code}")
    print("Content-Type:", r.headers.get("Content-Type"))
    print("Body snippet:")
    print(r.text[:300])
except Exception as e:
    print("Error:", e)
