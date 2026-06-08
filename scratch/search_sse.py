with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

import re
matches = [m.start() for m in re.finditer(r"event-stream", content)]
if not matches:
    print("No event-stream matches found.")
for m in matches:
    start = max(0, m - 100)
    end = min(len(content), m + 200)
    print("--- MATCH ---")
    print(content[start:end])
