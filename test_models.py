# test_predict.py
"""
Runs a complete end-to-end prediction using the hybrid pipeline:
XGBoost + CNN-LSTM + DQN

This file is ONLY for testing your backend modules.
"""

import os
import json
from pprint import pprint

try:
    from backend.hybrid_decision import predict_combined
except Exception as e:
    raise SystemExit(
        f"❌ Failed to import hybrid_decision.\n"
        f"Run this file from project ROOT (same folder as app.py)\nError: {e}"
    )

# ------------------------------
# 1. SIMPLE, SAFE TEST PAYLOAD
# ------------------------------

sample = {
    "Header_Length": 20,
    "Time_To_Live": 64,
    "Rate": 100.0,
    "IAT": 0.01,
    "Tot sum": 500,
    "Tot size": 1024,
    "AVG": 50.0,
    "Std": 10.0,
    "Variance": 25.0,
    "Min": 1.0,
    "Max": 200.0,
    "Number": 5,

    # TCP flag-like fields
    "fin_flag_number": 0,
    "syn_flag_number": 1,
    "rst_flag_number": 0,
    "psh_flag_number": 0,
    "ack_flag_number": 1,
    "cwr_flag_number": 0,
    "ece_flag_number": 0,

    "ack_count": 5,
    "syn_count": 1,
    "fin_count": 0,
    "rst_count": 0,

    # protocol
    "Protocol Type": "TCP",

    # one-hot fields (if present in your model)
    "HTTP": 0,
    "HTTPS": 0,
    "DNS": 0,
    "Telnet": 0,
    "SMTP": 0,
    "SSH": 0,
    "IRC": 0,
    "TCP": 1,
    "UDP": 0,
    "DHCP": 0,
    "ARP": 0,
    "ICMP": 0,
    "IGMP": 0,
    "IPv": 0,
    "LLC": 0
}

print("\n============================")
print("🚀 Running Full Hybrid Prediction")
print("============================\n")

# ------------------------------
# 2. RUN HYBRID PIPELINE
# ------------------------------

try:
    result = predict_combined(sample)
except Exception as e:
    raise SystemExit(f"❌ predict_combined() FAILED\n{e}")

# ------------------------------
# 3. PRINT RESULT
# ------------------------------
print("✅ Prediction Completed!\n")
print(result)

# ------------------------------
# 4. SAVE OUTPUT FOR SLIDES
# ------------------------------
output_path = "test_predict_output.json"
with open(output_path, "w") as f:
    json.dump(result, f, indent=4)

print(f"\n📁 Output saved to {output_path}\n")
print("👉 Use this JSON in your interim PPT demo.")
