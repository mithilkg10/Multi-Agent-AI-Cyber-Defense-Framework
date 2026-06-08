import re

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

keywords = ["/admin/set_threshold", "/admin/set_persona", "/admin/get_config", "/admin/verify_logs", "/admin/simulate_attack", "/admin/block_ip_manual"]
lines = content.splitlines()

for kw in keywords:
    print(f"\n=== Implementation for: {kw} ===")
    match = re.search(r'@app\.route\("' + kw + r'"', content)
    if match:
        start_idx = match.start()
        # Grab about 30 lines after the match
        lines_after = content[start_idx:start_idx+2000].splitlines()
        brace_count = 0
        for i, l in enumerate(lines_after):
            if i > 2 and ("@app.route" in l or ("def " in l and not l.startswith("    "))):
                break
            print(l)
    else:
        print(f"Not found: {kw}")
