# scratch/search_login_insert.py
with open("app.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "login_log" in line and "insert" in line.lower():
        print(f"Line {idx+1}: {line.strip()}")
        # print surrounding 5 lines
        start = max(0, idx - 3)
        end = min(len(lines), idx + 6)
        for j in range(start, end):
            print(f"   {j+1}: {lines[j]}", end="")
