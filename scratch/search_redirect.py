# scratch/search_redirect.py
with open("app.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "def redirect_to_honeypot" in line:
        print(f"Line {idx+1}: {line.strip()}")
        # print next 15 lines
        for j in range(idx+1, min(len(lines), idx+16)):
            print(f"   {j+1}: {lines[j]}", end="")
