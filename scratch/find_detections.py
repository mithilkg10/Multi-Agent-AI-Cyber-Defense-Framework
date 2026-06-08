with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

import re
matches = [line for line in content.splitlines() if "detections" in line.lower() and "create table" in line.lower()]
print("=== detections CREATE TABLE matches in app.py ===")
for m in matches:
    print(m)
