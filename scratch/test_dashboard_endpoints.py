import requests
import json
import sys

# Configure UTF-8 stdout
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

session = requests.Session()

# 1. Login to Flask app
print("Attempting to login to http://127.0.0.1:5000/ ...")
login_url = "http://127.0.0.1:5000/"
data = {"username": "admin", "password": "Admin@123"}
r_login = session.post(login_url, data=data, timeout=5)
print(f"Login status code: {r_login.status_code}")

# 2. Test get_config
print("\nTesting GET /admin/get_config ...")
r_config = session.get("http://127.0.0.1:5000/admin/get_config", timeout=5)
print(f"Config Status: {r_config.status_code}")
if r_config.status_code == 200:
    try:
        print("Config JSON:", json.dumps(r_config.json(), indent=2))
    except Exception as e:
        print("Failed parsing config JSON:", e)

# 3. Test verify_logs
print("\nTesting POST /admin/verify_logs ...")
r_verify = session.post("http://127.0.0.1:5000/admin/verify_logs", timeout=5)
print(f"Verify Logs Status: {r_verify.status_code}")
if r_verify.status_code == 200:
    try:
        print("Verify Logs JSON:", json.dumps(r_verify.json(), indent=2))
    except Exception as e:
        print("Failed parsing verify logs JSON:", e)
