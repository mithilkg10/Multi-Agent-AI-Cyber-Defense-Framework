with open("templates/dashboard.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "function renderTopIps" in line or "function renderAttackPie" in line or "function renderLiveIpSeries" in line:
        print(f"Line {i+1}: {line.strip()}")
