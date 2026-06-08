with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

# Search for references to pyshark_to_predict.py or sniffer
import re
matches = [line for line in content.splitlines() if "pyshark" in line.lower() or "predict.py" in line.lower() or "sniffer" in line.lower() or "scapy" in line.lower()]
print("=== SNIFFER REFERENCES IN APP.PY ===")
for m in matches:
    print(m)
