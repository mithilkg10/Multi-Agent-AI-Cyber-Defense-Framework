import sys

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

import re
match = re.search(r"def start_anomaly_detector", content)
if match:
    start = match.start()
    print(content[start:start+1000])
else:
    print("Not found")
