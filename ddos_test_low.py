# ddos_test_low.py (safe small burst)
import requests, threading, time

URL = "http://127.0.0.1:5000/"
def hit(n):
    s = requests.Session()
    for i in range(n):
        try:
            s.get(URL)
        except Exception as e:
            print("err", e)

threads = []
for _ in range(10):           # 10 threads
    t = threading.Thread(target=hit, args=(200,))  # each makes 200 requests -> 2000 total
    t.start()
    threads.append(t)
for t in threads:
    t.join()
print("done")
