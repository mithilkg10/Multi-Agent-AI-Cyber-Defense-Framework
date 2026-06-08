# scratch/inspect_templates.py
with open("templates/dashboard.html", "r", encoding="utf-8") as f:
    content = f.read()

lines = content.splitlines()
matches = [i for i, line in enumerate(lines) if "overlord" in line.lower() or "altkey" in line.lower()]
print(f"Found {len(matches)} matches.")
for idx in matches:
    print(f"Line {idx+1}: {lines[idx].strip()}")
