# consumer.py
"""
Consume messages from Kafka topic 'network-traffic', run hybrid prediction
(predict_combined), write prediction to 'predictions' topic and to SQLite DB.
If should_honeypot is True, create a 'responses' row and also publish a
message to 'honeypot_triggers' topic.

Run with same venv where your app/models live.
"""

import os
import json
import sqlite3
import time
from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError

# Import your existing model function (must be importable from project root)
try:
    from backend.hybrid_decision import predict_combined
except Exception as e:
    raise SystemExit(f"Failed to import predict_combined: {e}")

KAFKA_BOOTSTRAP = os.environ.get("KAFKA_BOOTSTRAP", "localhost:9092")
IN_TOPIC = os.environ.get("KAFKA_IN_TOPIC", "network-traffic")
PRED_TOPIC = os.environ.get("KAFKA_PRED_TOPIC", "predictions")
HONEYPOT_TOPIC = os.environ.get("KAFKA_HONEYPOT_TOPIC", "honeypot_triggers")

SQLITE_DB = os.environ.get("SQLITE_DB", "cyber_defense.db")
GROUP_ID = "models-prediction-consumer-1"

def db_connect():
    conn = sqlite3.connect(SQLITE_DB, timeout=10, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

import hmac
import hashlib

SECRET_KEY = "supersecretkey"

def calculate_log_signature(created_at, traffic_id, model_used, prediction, final_score):
    msg = f"{created_at}|{traffic_id}|{model_used}|{prediction}|{final_score}"
    return hmac.new(SECRET_KEY.encode('utf-8'), msg.encode('utf-8'), hashlib.sha256).hexdigest()

def get_mitre_mapping(prediction, model_used, final_score):
    pred_str = str(prediction).lower()
    if "ddos" in pred_str or "dos" in pred_str:
        return "T1498", "DDoS (Network Denial of Service)"
    elif "bruteforce" in pred_str or "brute" in pred_str:
        return "T1110", "Brute Force Authentication"
    elif "sqli" in pred_str or "sql" in pred_str:
        return "T1190", "SQL Injection Exploit"
    elif "recon" in pred_str or "scan" in pred_str:
        return "T1046", "Network Service Discovery"
    else:
        if final_score > 0.85:
            return "T1498", "DDoS Attack"
        elif final_score > 0.65:
            return "T1046", "Port Scan Recon"
        else:
            return "T1595", "Active Scanning"

def save_detection(conn, input_payload, result_json):
    cur = conn.cursor()
    traffic_id = input_payload.get("capture_id") or input_payload.get("traffic_id") or input_payload.get("src_ip") or input_payload.get("src") or None
    model_used = result_json.get("model") or "hybrid:xgb+cnn+dqn"
    
    # prediction
    prediction = None
    try:
        prediction = result_json.get("prediction") or (result_json.get("xgb") or {}).get("prediction") or result_json.get("dqn_label")
    except Exception:
        prediction = str(result_json.get("prediction", ""))
        
    dqn_action = result_json.get("dqn_action") or result_json.get("action") or None
    final_score = float(result_json.get("final_score") or result_json.get("anomaly_score") or 0.0)
    should_honeypot = 1 if result_json.get("should_honeypot") else 0
    raw = json.dumps(result_json, default=str)
    created_at = result_json.get("_ts") or time.strftime("%Y-%m-%d %H:%M:%S")
    
    # Explainable AI, HMAC Signing, MITRE Mapping
    xai_explanation = result_json.get("xai_explanation") or "General network traffic anomaly flagged by ML classifiers"
    mitre_id, attack_type = get_mitre_mapping(prediction, model_used, final_score)
    log_signature = calculate_log_signature(created_at, traffic_id, model_used, prediction, final_score)

    cur.execute(
        """
        INSERT INTO detections (
            created_at, traffic_id, model_used, prediction, dqn_action, 
            final_score, should_honeypot, raw, xai_explanation, log_signature, mitre_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (created_at, traffic_id, model_used, prediction, dqn_action,
         final_score, should_honeypot, raw, xai_explanation, log_signature, mitre_id)
    )
    conn.commit()
    return cur.lastrowid

def save_response(conn, detection_id, action):
    cur = conn.cursor()
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    status = "created"
    cur.execute(
        "INSERT INTO responses (detection_id, action, status, timestamp) VALUES (?, ?, ?, ?)",
        (detection_id, action, status, ts)
    )
    conn.commit()
    return cur.lastrowid
def safe_json_deserializer(m):
    if m is None:
        return None
    try:
        s = m.decode("utf-8").strip()
        if not s:
            # ignore empty blank messages
            return None
        return json.loads(s)
    except Exception:
        print("[consumer] Skipping invalid JSON:", m)
        return None

def main():
    import sys
    print(f"[consumer] Connecting to Kafka {KAFKA_BOOTSTRAP}, topic {IN_TOPIC}")
    
    # Retry loop for Kafka Consumer
    consumer = None
    retries = 10
    while retries > 0:
        try:
            consumer = KafkaConsumer(
                IN_TOPIC,
                bootstrap_servers=[KAFKA_BOOTSTRAP],
                auto_offset_reset='latest',
                enable_auto_commit=True,
                group_id=GROUP_ID,
                value_deserializer=safe_json_deserializer,
            )
            break
        except Exception as e:
            print(f"[consumer] Kafka consumer init failed: {e}. Retrying in 3s...")
            time.sleep(3)
            retries -= 1
            
    if not consumer:
        print("[consumer] [FATAL] Could not connect to Kafka. Exiting.")
        sys.exit(1)

    # Retry loop for Kafka Producer
    producer = None
    retries = 10
    while retries > 0:
        try:
            producer = KafkaProducer(
                bootstrap_servers=[KAFKA_BOOTSTRAP],
                value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8')
            )
            break
        except Exception as e:
            print(f"[consumer] Kafka producer init failed: {e}. Retrying in 3s...")
            time.sleep(3)
            retries -= 1
            
    if not producer:
        print("[consumer] [FATAL] Could not initialize Kafka producer. Exiting.")
        sys.exit(1)

    conn = db_connect()

    try:
        for msg in consumer:
            try:
                payload = msg.value
            except Exception as e:
                print("[consumer] Failed to decode msg:", e)
                continue

            # optional: add timestamp for traceability
            payload["_ts"] = payload.get("_ts") or time.strftime("%Y-%m-%dT%H:%M:%SZ")

            # Run your existing hybrid prediction
            try:
                result = predict_combined(payload)
            except Exception as e:
                print("[consumer] predict_combined failed:", e)
                continue

            # attach original features for context
            out_msg = {
                "input": {
                    "summary": {
                        "src": payload.get("src_ip"),
                        "dst": payload.get("dst_ip"),
                        "protocol": payload.get("Protocol Type") or payload.get("protocol")
                    }
                },
                "result": result,
                "_ts": payload["_ts"]
            }

            # produce to predictions topic
            try:
                producer.send(PRED_TOPIC, out_msg)
                producer.flush(timeout=5)
            except KafkaError as ke:
                print("[producer] Failed to write prediction to Kafka:", ke)

            # save into DB (detections table)
            try:
                det_id = save_detection(conn, payload, result)
            except Exception as e:
                print("[db] Failed to save detection:", e)
                det_id = None

            # If honeypot trigger, create response row and publish to honeypot topic
            if result.get("should_honeypot"):
                action = "send_to_honeypot"  # or "block_and_honeypot" depending on your design
                try:
                    resp_id = save_response(conn, det_id, action)
                except Exception as e:
                    print("[db] Failed to save response:", e)
                    resp_id = None

                # create honeypot event
                hp_event = {
                    "detection_id": det_id,
                    "response_id": resp_id,
                    "action": action,
                    "result": result,
                    "_ts": payload["_ts"]
                }
                try:
                    producer.send(HONEYPOT_TOPIC, hp_event)
                    producer.flush(timeout=5)
                except KafkaError as ke:
                    print("[producer] Failed to write honeypot trigger:", ke)

            # quick console log
            print(f"[processed] ts={payload['_ts']} final_score={result.get('final_score')}, honeypot={result.get('should_honeypot')}")

    except KeyboardInterrupt:
        print("Stopped by user")
    finally:
        try:
            producer.close()
        except:
            pass
        try:
            consumer.close()
        except:
            pass
        conn.close()
        print("Exiting")

if __name__ == "__main__":
    main()
