import os
import re

for root, dirs, files in os.walk("."):
    if "venv" in root or ".git" in root or "__pycache__" in root:
        continue
    for file in files:
        if file.endswith(".py"):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                # Find CREATE TABLE
                matches = re.findall(r'CREATE TABLE.*', content, re.IGNORECASE)
                if matches:
                    print(f"Found in {filepath}:")
                    for m in matches[:5]:
                        print("  ", m[:100])
            except Exception:
                pass
