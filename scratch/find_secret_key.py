with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

import re
matches = [line for line in content.splitlines() if "secret_key" in line]
print("=== secret_key matches in app.py ===")
for m in matches:
    print(m)
