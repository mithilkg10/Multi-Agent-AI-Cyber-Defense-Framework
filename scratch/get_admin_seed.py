import sys
import re

# Configure UTF-8 stdout
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

match = re.search(r'INSERT INTO admins', content)
if match:
    start_idx = match.start()
    lines = content[max(0, start_idx-500):start_idx+500].splitlines()
    for l in lines:
        print(l)
else:
    print("Not found")
