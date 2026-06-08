import os

def search_todos():
    project_dir = r"c:\Users\Mithil K Gowda\OneDrive\Desktop\PROJECT 7TH SEM\PROJECT"
    for root, dirs, files in os.walk(project_dir):
        if "venv" in root or ".git" in root or "__pycache__" in root:
            continue
        for file in files:
            if file.endswith((".py", ".html", ".js", ".css")):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        lines = f.readlines()
                    for idx, line in enumerate(lines, 1):
                        if "todo" in line.lower() or "fixme" in line.lower() or "under development" in line.lower():
                            rel_path = os.path.relpath(filepath, project_dir)
                            print(f"{rel_path}:{idx}: {line.strip()}")
                except Exception as e:
                    pass

if __name__ == "__main__":
    search_todos()
