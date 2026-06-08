# scratch/inspect_app.py
import re

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

keywords = ["overlord", "retrain", "dqn_retraining_log", "reputation", "anomaly_threshold", "fail_rate", "anomaly"]
lines = content.splitlines()

for kw in keywords:
    print(f"\n--- Searching for: '{kw}' ---")
    matches = [i for i, line in enumerate(lines) if kw in line]
    print(f"Found {len(matches)} matches.")
    # Show first 3 matches and surrounding 5 lines
    for idx in matches[:5]:
        print(f"Line {idx+1}:")
        start = max(0, idx - 3)
        end = min(len(lines), idx + 4)
        for j in range(start, end):
            prefix = "-> " if j == idx else "   "
            print(f"{prefix}{j+1}: {lines[j]}")
