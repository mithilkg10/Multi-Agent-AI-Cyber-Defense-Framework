import requests, threading, time

URL = "http://127.0.0.1:5000/"   # your Flask login endpoint
THREADS = 60
REQUESTS_PER_THREAD = 500

def spam(tid):
    for i in range(REQUESTS_PER_THREAD):
        try:
            r = requests.post(URL, data={"username": "testuser", "password": "badpass"})
            if i % 25 == 0:
                print(f"[T{tid}] {i} -> {r.status_code}")
        except Exception as e:
            print(f"[T{tid}] error:", e)
        time.sleep(0.005)

threads = []
for t in range(THREADS):
    th = threading.Thread(target=spam, args=(t,))
    th.start()
    threads.append(th)

for th in threads:
    th.join()

print("✅ Test completed.")
