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
                content = step.get("content", "")
                lines = content.splitlines()
                # print lines matching dqn, rl, retrain, training
                for i, l in enumerate(lines):
                    if any(x in l.lower() for x in ["dqn", "rl", "retrain", "reinforce"]):
                        # print context (before and after)
                        start = max(0, i - 2)
                        end = min(len(lines), i + 3)
                        print(f"--- Line {i+1} ---")
                        for idx in range(start, end):
                            print(f"{idx+1}: {lines[idx]}")
                break
        except Exception as e:
            pass
