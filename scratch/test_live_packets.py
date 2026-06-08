import requests
import sys

# Configure UTF-8 stdout
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

url = "http://127.0.0.1:5000/live_packets"
print("Connecting to /live_packets stream...")
try:
    # We use stream=True and read line by line
    r = requests.get(url, stream=True, timeout=5)
    print(f"Status Code: {r.status_code}")
    print("Mimetype:", r.headers.get("Content-Type"))
    count = 0
    for line in r.iter_lines():
        if line:
            decoded = line.decode('utf-8')
            print(f"Event: {decoded}")
            count += 1
            if count >= 3:
                break
except Exception as e:
    print("Error:", e)
