with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

lines = content.splitlines()
for idx, line in enumerate(lines):
    if "backend.hybrid_decision" in line:
        print(f"Line {idx+1}: {line}")
