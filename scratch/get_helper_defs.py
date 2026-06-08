with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

import re
matches = re.finditer(r'def (calculate_log_signature|get_mitre_mapping)\([^)]*\):', content)
print("=== DEFINITIONS IN APP.PY ===")
for m in matches:
    start = m.start()
    lines_after = content[start:start+1200].splitlines()
    for l in lines_after:
        if l.startswith("def ") and not m.group(1) in l:
            break
        print(l)
    print("-" * 50)
