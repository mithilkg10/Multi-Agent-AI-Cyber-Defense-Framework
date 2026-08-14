import requests
import time

URL = "http://127.0.0.1:5000/"
IP = "127.0.0.1"

for i in range(12):
    data = {"username": "wronguser", "password": "wrongpass"}
    r = requests.post(URL, data=data)
    print(i+1, "status:", r.status_code, "redirected to:", r.url)
    time.sleep(0.2)
