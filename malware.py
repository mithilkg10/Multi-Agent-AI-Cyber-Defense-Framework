import requests, time
for i in range(20):
    requests.get("http://127.0.0.1:5001/c2check?sid=test")
    time.sleep(2)   # simulate periodic beaconing
