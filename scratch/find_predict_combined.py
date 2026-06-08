with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

import re
matches = [line for line in content.splitlines() if "predict_combined" in line]
print("=== predict_combined matches in app.py ===")
for m in matches:
    print(m)
