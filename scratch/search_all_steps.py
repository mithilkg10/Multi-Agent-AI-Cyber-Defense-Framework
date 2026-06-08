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
            content = step.get("content", "")
            # check if it contains keywords of interest
            keywords = ["retrain", "q-learning", "reinforce", "continuous update", "learning loop"]
            found = [kw for kw in keywords if kw.lower() in content.lower()]
            if found and step.get("source") == "MODEL":
                print(f"=== STEP {step.get('step_index')} (Keywords: {found}) ===")
                # Print lines containing the keywords
                lines = content.splitlines()
                for i, l in enumerate(lines):
                    if any(kw.lower() in l.lower() for kw in keywords):
                        print(f"  Line {i+1}: {l.strip()}")
        except Exception:
            pass
