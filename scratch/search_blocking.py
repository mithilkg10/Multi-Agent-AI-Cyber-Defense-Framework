# scratch/search_blocking.py
with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

lines = content.splitlines()
matches = [i for i, line in enumerate(lines) if "before_request" in line or "ip_address" in line]
print(f"Found {len(matches)} matches.")
for idx in matches:
    if "before_request" in lines[idx] or "blocked" in lines[idx]:
        print(f"Line {idx+1}: {lines[idx].strip()}")
