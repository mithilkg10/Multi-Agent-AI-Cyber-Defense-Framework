# scratch/view_app_seeding.py
with open("app.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx in range(740, min(len(lines), 765)):
    print(f"{idx+1}: {lines[idx]}", end="")
