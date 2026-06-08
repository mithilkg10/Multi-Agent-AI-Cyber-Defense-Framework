# scratch/search_predict_route.py
with open("app.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

print("--- Line 1600-1645 ---")
for idx in range(1599, min(len(lines), 1645)):
    print(f"{idx+1}: {lines[idx]}", end="")
