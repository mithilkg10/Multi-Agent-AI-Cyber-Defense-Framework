import requests
import json

url = "http://127.0.0.1:5000/predict"
flow = {
    "Rate": 150.0,
    "Tot size": 1400,
    "Protocol Type": "TCP",
    "syn_flag_number": 1,
    "ack_flag_number": 0,
    "Time_To_Live": 32,
    "traffic_id": "198.51.100.5"
}

try:
    print(f"Sending POST to {url}...")
    r = requests.post(url, json=flow, timeout=5)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")
except Exception as e:
    print(f"Error: {e}")
