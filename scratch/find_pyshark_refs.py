import os

keywords = ["pyshark_to_predict"]
for root, dirs, files in os.walk("."):
    if "venv" in root or ".git" in root or "__pycache__" in root:
        continue
    for file in files:
        if file.endswith((".py", ".bat", ".sh", ".txt", ".json")):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                for kw in keywords:
                    if kw in content:
                        print(f"Found reference in {filepath}")
            except Exception:
                pass
