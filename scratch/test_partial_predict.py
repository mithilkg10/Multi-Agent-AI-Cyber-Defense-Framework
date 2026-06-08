import requests
import json
import sys

# Configure UTF-8 stdout
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

url = "http://127.0.0.1:5000/predict"
sample = {
    "packet_rate": 150,
    "entropy": 0.85,
    "syn_flag": 1,
    "ttl": 32,
    "dst_port": 80
}

print("POSTing to /predict with partial live_packets sample...")
try:
    r = requests.post(url, json=sample, timeout=5)
    print(f"Status Code: {r.status_code}")
    print("Response text:", r.text)
except Exception as e:
    print("Error:", e)
