with open("app.py", "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if "app = Flask" in line:
            print(f"Line {i+1}: {line.strip()}")
