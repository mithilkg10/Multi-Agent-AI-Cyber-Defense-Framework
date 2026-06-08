with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

import re
matches = re.finditer(r'CREATE TABLE IF NOT EXISTS \w+', content, re.IGNORECASE)
print("=== TABLE CREATION BLOCKS IN APP.PY ===")
for m in matches:
    start = max(0, m.start() - 10)
    end = min(len(content), m.end() + 200)
    print(content[start:end])
    print("-" * 50)
