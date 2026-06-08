with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

lines = content.splitlines()
for idx, line in enumerate(lines):
    if "CREATE TABLE IF NOT EXISTS detections" in line:
        # Print lines around it
        print(f"=== Found at line {idx+1} ===")
        for i in range(max(0, idx-5), min(len(lines), idx+30)):
            print(f"{i+1}: {lines[i]}")
