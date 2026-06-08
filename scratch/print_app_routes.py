# scratch/print_app_routes.py
with open("app.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

# Print lines 2620 to 2750 (0-indexed: 2619 to 2749)
for idx in range(2620, min(len(lines), 2750)):
    print(f"{idx+1}: {lines[idx]}", end="")
