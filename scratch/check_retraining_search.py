import os
import re

patterns = [
    re.compile(r"def\s+retrain", re.IGNORECASE),
    re.compile(r"model\.learn", re.IGNORECASE),
    re.compile(r"model\.fit", re.IGNORECASE),
    re.compile(r"dqn_threat_detection", re.IGNORECASE),
    re.compile(r"retrain_supervised_from_data", re.IGNORECASE),
]

matches = []
for root, dirs, files in os.walk("."):
    # skip venv, .venv, git, etc.
    dirs[:] = [d for d in dirs if d not in ("venv", ".venv", ".git", "__pycache__", "captures")]
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    for i, line in enumerate(f, 1):
                        for pat in patterns:
                            if pat.search(line):
                                matches.append(f"{path}:{i}: {line.strip()}")
            except Exception as e:
                pass

print(f"Total matches: {len(matches)}")
for m in matches[:50]:
    print(m)
