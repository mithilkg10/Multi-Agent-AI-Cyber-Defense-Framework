# scratch/search_login_route.py
with open("app.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

print("--- Line 1120-1165 ---")
for idx in range(1119, min(len(lines), 1165)):
    print(f"{idx+1}: {lines[idx]}", end="")
