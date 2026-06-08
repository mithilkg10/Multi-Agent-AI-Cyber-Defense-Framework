import sys

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

with open(r"C:\Users\Mithil K Gowda\.gemini\antigravity\brain\c9d31b9e-e66b-4e5f-8154-7888d90e94c9\.system_generated\tasks\task-1066.log", "r", encoding="utf-8") as f:
    for line in f:
        if "[SNIFFER]" in line:
            print(line.strip())
