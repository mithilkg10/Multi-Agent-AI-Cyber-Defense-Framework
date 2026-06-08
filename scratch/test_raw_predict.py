# scratch/test_raw_predict.py
import requests
import time

PREDICT_URL = "http://127.0.0.1:5000/predict"

flow = {
    "Rate": 150.0,
    "Tot size": 1300,
    "Protocol Type": "TCP",
    "syn_flag_number": 1,
    "ack_flag_number": 0,
    "Time_To_Live": 32,
    "traffic_id": "198.51.100.5"
}

start_time = time.time()
try:
    print("Sending POST request to /predict (timeout=30)...")
    r = requests.post(PREDICT_URL, json=flow, timeout=30, allow_redirects=False)
    duration = time.time() - start_time
    print(f"Status Code: {r.status_code} (took {duration:.2f} seconds)")
    print("Headers:", r.headers)
    if "Location" in r.headers:
        print("Redirect Location:", r.headers["Location"])
    else:
        print("Content (first 500 chars):")
        print(r.text[:500])
except Exception as e:
    duration = time.time() - start_time
    print(f"Request failed after {duration:.2f} seconds: {e}")
