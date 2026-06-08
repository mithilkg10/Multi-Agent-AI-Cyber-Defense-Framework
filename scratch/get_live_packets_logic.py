import sys

# Configure UTF-8 stdout
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

import re
match = re.search(r'def live_packets\(\):', content)
if match:
    start = match.start()
    lines = content[start:start+1200].splitlines()
    for l in lines:
        if "@app.route" in l or (l.startswith("def ") and "live_packets" not in l):
            break
        print(l)
else:
    print("Not found")
