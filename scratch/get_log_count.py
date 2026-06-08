import os
import sys

# Configure UTF-8 stdout
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

log_file = r"C:\Users\Mithil K Gowda\.gemini\antigravity\brain\c9d31b9e-e66b-4e5f-8154-7888d90e94c9\.system_generated\tasks\task-962.log"
if os.path.exists(log_file):
    with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    print(f"Total lines in log: {len(lines)}")
    print("=== NEWEST 30 LINES OF LOG ===")
    for l in lines[-30:]:
        print(l, end="")
else:
    print("Log file not found.")
