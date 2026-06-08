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

if not os.path.exists(transcript_path):
    print("Transcript not found")
    sys.exit(0)

with open(transcript_path, "r", encoding="utf-8") as f:
    for line in f:
        try:
            step = json.loads(line)
            content = str(step.get("content", ""))
            if "blueprint" in content.lower() or "transformation" in content.lower():
                print(f"--- STEP {step.get('step_index')} ---")
                # find where RL or retrain is mentioned in this content
                lines = content.splitlines()
                for l in lines:
                    if any(x in l.lower() for x in ["rl", "retrain", "reinforc", "continuous"]):
                        print(l.strip())
        except Exception as e:
            pass
