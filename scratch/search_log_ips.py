with open(r"C:\Users\Mithil K Gowda\.gemini\antigravity\brain\c9d31b9e-e66b-4e5f-8154-7888d90e94c9\.system_generated\tasks\task-1433.log", "r", encoding="utf-8") as f:
    for i, line in enumerate(f, 1):
        if "198.51.100." in line:
            print(f"Line {i}: {line.strip()}")
