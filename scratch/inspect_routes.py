import re

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

# Find all routes
routes = re.findall(r'@app\.route\([^)]+\)\s+def\s+\w+\([^)]*\):', content)
print("=== FOUND FLASK ROUTES ===")
for r in routes:
    print(r)

# Find specific setting routes or thresholds
print("\n=== SEARCHING FOR SETTINGS / SIMULATION / PERSONA / VERIFY ===")
for line in content.splitlines():
    if any(keyword in line for keyword in ["threshold", "persona", "simulate", "verify_logs", "manual_block", "block"]):
        if "@app.route" in line or "def " in line or "route" in line:
            print(line)
