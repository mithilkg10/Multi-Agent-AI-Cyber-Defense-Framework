with open("templates/dashboard.html", "r", encoding="utf-8") as f:
    content = f.read()

import re
matches = [m.start() for m in re.finditer(r"function renderTopIps|function renderAttackPie", content)]
for m in matches:
    start = max(0, m - 50)
    end = min(len(content), m + 300)
    print("--- MATCH ---")
    print(content[start:end])
