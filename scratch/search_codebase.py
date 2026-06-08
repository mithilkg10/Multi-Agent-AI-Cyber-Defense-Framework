import os

for root, dirs, files in os.walk("."):
    if "venv" in root or ".git" in root or "__pycache__" in root:
        continue
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                if "/events/" in content:
                    print(f"Found /events/ in {path}")
            except Exception as e:
                pass
