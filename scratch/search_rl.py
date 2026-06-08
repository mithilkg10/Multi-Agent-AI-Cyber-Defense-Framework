import os

keywords = ["retrain", "q_network", "fit", "DQN", "dqn", "retraining"]
for root, dirs, files in os.walk("."):
    if "venv" in root or ".git" in root or "__pycache__" in root or ".venv" in root:
        continue
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                found = [kw for kw in keywords if kw in content]
                if found:
                    print(f"File: {path} contains keywords: {found}")
            except Exception as e:
                pass
