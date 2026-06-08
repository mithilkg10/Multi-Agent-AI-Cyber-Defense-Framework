# scratch/print_before_request.py
with open("app.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

print("--- Line 1280-1340 ---")
for idx in range(1279, min(len(lines), 1340)):
    print(f"{idx+1}: {lines[idx]}", end="")
