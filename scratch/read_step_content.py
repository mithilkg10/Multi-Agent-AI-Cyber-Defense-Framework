import os
import json
import sys

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

log_dir = r"C:\Users\Mithil K Gowda\.gemini\antigravity\brain\c9d31b9e-e66b-4e5f-8154-7888d90e94c9\.system_generated\logs"
transcript_path = os.path.join(log_dir, "transcript.jsonl")

with open(transcript_path, "r", encoding="utf-8") as f:
    for line in f:
        try:
            step = json.loads(line)
            if step.get("step_index") == 348:
                print(step.get("content"))
                break
        except Exception:
            pass
