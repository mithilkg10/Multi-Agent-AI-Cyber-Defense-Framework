import os
import json
import sys

# Configure UTF-8 stdout
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

log_dir = r"C:\Users\Mithil K Gowda\.gemini\antigravity\brain\c9d31b9e-e66b-4e5f-8154-7888d90e94c9\.system_generated\logs"
transcript_path = os.path.join(log_dir, "transcript.jsonl")

if not os.path.exists(transcript_path):
    print(f"Transcript not found at {transcript_path}")
    sys.exit(0)

print(f"Searching transcript: {transcript_path}")
keywords = ["RL", "retrain", "continuous", "feedback", "loop", "update"]

count = 0
with open(transcript_path, "r", encoding="utf-8") as f:
    for line in f:
        try:
            step = json.loads(line)
            content = str(step.get("content", ""))
            # Also check tool calls
            tool_calls = str(step.get("tool_calls", ""))
            combined = content + " " + tool_calls
            found = [kw for kw in keywords if kw.lower() in combined.lower()]
            if found:
                print(f"--- Step {step.get('step_index')} (Source: {step.get('source')}, Type: {step.get('type')}) ---")
                # print snippet of content
                snippet = content[:500].replace("\n", " ")
                print(f"Content: {snippet} ... [Keywords: {found}]")
                count += 1
                if count > 30:
                    print("Truncating search output to first 30 matches.")
                    break
        except Exception as e:
            print("Error parsing line:", e)
