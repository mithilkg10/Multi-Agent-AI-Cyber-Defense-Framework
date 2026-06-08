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
    "dst_port": 80,
    "Tot size": 500,
    "Protocol Type": "TCP",
    "Time_To_Live": 32,
    "Rate": 150.0,
    "traffic_id": "192.168.1.50"
}

print("POSTing to /predict with sample data...")
try:
    r = requests.post(url, json=sample, timeout=5)
    print(f"Status Code: {r.status_code}")
    print("Response text:", r.text[:500])
except Exception as e:
    print("Error:", e)
