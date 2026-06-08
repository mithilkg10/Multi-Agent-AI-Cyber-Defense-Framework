with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

import re
match = re.search(r'@app\.route\("/predict"', content)
if match:
    start_idx = match.start()
    lines_after = content[start_idx:start_idx+1500].splitlines()
    for i, l in enumerate(lines_after):
        if i > 2 and ("@app.route" in l or ("def " in l and not l.startswith("    "))):
            break
        print(l)
else:
    print("Not found")
