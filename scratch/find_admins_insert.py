with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

import re
matches = [line for line in content.splitlines() if "admins" in line.lower() and "insert" in line.lower()]
print("=== admins INSERT matches in app.py ===")
for m in matches:
    print(m)
