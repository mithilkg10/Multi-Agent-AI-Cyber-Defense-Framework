with open("templates/dashboard.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "liveIpChart = new Chart" in line:
        # Print 20 lines before
        start = max(0, i - 25)
        for idx in range(start, i + 5):
            print(f"Line {idx+1}: {lines[idx].strip()}")
