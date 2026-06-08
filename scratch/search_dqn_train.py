import os

for root, dirs, files in os.walk("."):
    if "venv" in root or ".git" in root or "__pycache__" in root or ".venv" in root:
        continue
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                if "dqn_model" in content or "ThreatDetectionEnv" in content:
                    print(f"Found reference in {path}")
            except Exception as e:
                pass
