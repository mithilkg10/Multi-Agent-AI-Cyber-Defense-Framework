# backend/hybrid_decision.py
from backend.xgboost_module import predict_xgb
from backend.cnn_lstm_module import predict_cnn_lstm
from backend.dqn_module import predict_dqn
from backend.feature_builder import build_for_models
import numpy as np
import pandas as pd
import sqlite3
import os

# -----------------------------
# DQN ACTION MAPPING
# -----------------------------
DQN_ACTION_MAP = {
    0: ("ignore", 0),
    1: ("watch", 0),
    2: ("block", 1),
}

def dqn_label_to_action(lbl):
    try:
        lbl = int(lbl)
    except:
        return ("watch", 0)
    return DQN_ACTION_MAP.get(lbl, ("watch", 0))

# -----------------------------
# DYNAMIC CONFIG HELPER
# -----------------------------
def _get_dynamic_threshold():
    """
    Safely retrieves the dynamic threat threshold from SQLite.
    Falls back to 0.65 if unavailable.
    """
    # find database file path
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cyber_defense.db")
    try:
        conn = sqlite3.connect(db_path, timeout=5)
        cur = conn.cursor()
        # check if config table exists and has a row
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='config'")
        if cur.fetchone():
            cur.execute("SELECT val FROM config WHERE key='threat_threshold'")
            row = cur.fetchone()
            if row:
                conn.close()
                return float(row[0])
        conn.close()
    except Exception:
        pass
    return 0.65

# -----------------------------
# EXPLAINABLE AI (XAI) ENGINE
# -----------------------------
def explain_decision(features: dict, final_score: float):
    """
    Computes rule-based feature contribution highlights (simulating LIME/SHAP).
    """
    if final_score < 0.35:
        return "Normal network traffic signature."
        
    reasons = []
    
    # Check rate
    rate = float(features.get("Rate", 0.0) or 0.0)
    if rate > 90.0:
        reasons.append(f"High traffic ingestion rate ({rate} pkts/s)")
    elif rate > 40.0:
        reasons.append(f"Elevated traffic rate ({rate} pkts/s)")
        
    # Check SYN flag
    syn = int(features.get("syn_flag_number", 0) or 0)
    if syn == 1:
        reasons.append("Active TCP SYN handshake flag")
        
    # Check RST/FIN flag
    rst = int(features.get("rst_flag_number", 0) or 0)
    fin = int(features.get("fin_flag_number", 0) or 0)
    if rst == 1:
        reasons.append("Connection Reset (RST) flag set")
    if fin == 1:
        reasons.append("Connection Finish (FIN) flag set")
        
    # Check Protocol / Port
    proto = str(features.get("Protocol Type", "")).upper()
    if "ICMP" in proto:
        reasons.append("ICMP ping sweep pattern")
    elif "ARP" in proto:
        reasons.append("ARP broadcast sequence")
        
    # TTL
    ttl = int(features.get("Time_To_Live", 0) or 0)
    if 0 < ttl < 40:
        reasons.append(f"Low Time-to-Live (TTL = {ttl}) indicating spoofing")
        
    # Size
    size = int(features.get("Tot size", 0) or 0)
    if size > 1300:
        reasons.append(f"Large payload size ({size} bytes)")
        
    if not reasons:
        reasons.append("General network traffic anomaly flagged by ML classifiers")
        
    # Return top 2 contributions
    return " | ".join(reasons[:2])

# -----------------------------
# MAIN HYBRID PREDICT FUNCTION
# -----------------------------
def predict_combined(features: dict):
    """
    features: raw input dict
    returns: xgb, cnn_score, dqn_label, dqn_action, final_score, should_honeypot, xai_explanation
    """
    # 1. Build aligned model inputs
    xgb_df, cnn_df, dqn_obs = build_for_models(features)

    # 2. XGBoost Prediction
    try:
        xgb_input = xgb_df.iloc[0].to_dict()
        xgb_result = predict_xgb(xgb_input)
        xgb_probs = np.array(xgb_result["probabilities"])
        xgb_score = float(np.max(xgb_probs))
    except Exception as e:
        print("[predict_combined] XGB error:", e)
        xgb_probs = np.array([0.5, 0.5])
        xgb_score = 0.5
        xgb_result = {
            "prediction": 0,
            "probabilities": [0.5, 0.5],
            "score": 0.5,
        }

    # 3. CNN-LSTM Prediction
    try:
        cnn_score = predict_cnn_lstm(cnn_df)
    except Exception as e:
        print("[predict_combined] CNN error:", str(e))
        cnn_score = 0.5

    # 4. DQN Prediction
    try:
        dqn_input_df = pd.DataFrame([features])
        dqn_label = predict_dqn(dqn_input_df)
    except Exception as e:
        print("[predict_combined] DQN error:", str(e))
        dqn_label = 0

    dqn_action, dqn_binary = dqn_label_to_action(dqn_label)
    dqn_score = 1 if dqn_binary == 1 else 0

    # 5. Final Hybrid Score
    final_score = (
        0.4 * xgb_score +
        0.4 * cnn_score +
        0.2 * dqn_score
    )

    # 6. Dynamically check dynamic threshold
    THRESH = _get_dynamic_threshold()
    should_honeypot = final_score >= THRESH

    # 7. Generate Explainable AI output
    xai_explanation = explain_decision(features, final_score)

    # 8. Build Result Object
    result = {
        "xgb": {
            "prediction": int(np.argmax(xgb_probs)),
            "probabilities": xgb_probs.tolist(),
            "score": xgb_score
        },
        "cnn_score": float(cnn_score),
        "dqn_label": int(dqn_label),
        "dqn_action": dqn_action,
        "final_score": float(final_score),
        "should_honeypot": bool(should_honeypot),
        "xai_explanation": xai_explanation
    }

    # 9. Publish Honeypot Trigger to Kafka if flagged
    if should_honeypot:
        try:
            from producer import get_kafka_producer
            import datetime, json

            producer = get_kafka_producer()

            honeypot_msg = {
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "xgb_prediction": int(np.argmax(xgb_probs)),
                "xgb_score": xgb_score,
                "cnn_score": float(cnn_score),
                "dqn_label": int(dqn_label),
                "dqn_action": dqn_action,
                "final_score": float(final_score),
                "should_honeypot": True,
                "xai_explanation": xai_explanation
            }

            producer.send("honeypot_triggers", value=honeypot_msg)
            try:
                producer.flush(timeout=3)
            except:
                pass

            print("[hybrid_decision] Honeypot event published.")
        except Exception as e:
            print("[hybrid_decision] Kafka publish failed:", e)

    return result
