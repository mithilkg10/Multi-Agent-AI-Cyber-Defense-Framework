with open("templates/dashboard.html", "r", encoding="utf-8") as f:
    content = f.read()

import re
matches = [m.start() for m in re.finditer(r"Chart", content)]
if not matches:
    print("No Chart matches found in dashboard.html.")
for m in matches:
    start = max(0, m - 50)
    end = min(len(content), m + 150)
    print("--- MATCH ---")
    print(content[start:end])
