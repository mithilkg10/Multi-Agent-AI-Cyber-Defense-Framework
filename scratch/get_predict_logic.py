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
match = re.search(r'def predict\(\):', content)
if match:
    start = match.start()
    lines = content[start:start+4000].splitlines()
    for l in lines:
        if "@app.route" in l or (l.startswith("def ") and "predict" not in l):
            break
        print(l)
else:
    print("Not found")
