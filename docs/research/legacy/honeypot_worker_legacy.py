# honeypot_worker.py
import json, time, requests
from kafka import KafkaConsumer, KafkaProducer

KAFKA_BOOTSTRAP = "localhost:9092"
CONSUME_TOPIC = "predictions"
HONEYPOT_TOPIC = "honeypot_triggers"
GROUP_ID = "honeypot-worker-group"

# Thresholds - tune as needed
FINAL_SCORE_THRESHOLD = 0.65
# Or rely on the model's 'should_honeypot' boolean if present

HONEYPOT_API = "http://127.0.0.1:5000/honeypot/trigger"  # example - replace if you have real API

def make_producer():
    return KafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP,
                         value_serializer=lambda v: json.dumps(v).encode("utf-8"))

def make_consumer():
    return KafkaConsumer(
        CONSUME_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP,
        group_id=GROUP_ID,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset="latest",
        enable_auto_commit=True
    )

def call_honeypot_api(payload):
    try:
        r = requests.post(HONEYPOT_API, json=payload, timeout=5)
        return r.status_code, r.text
    except Exception as e:
        return None, str(e)

def main():
    cons = make_consumer()
    prod = make_producer()
    print("[honeypot_worker] listening for predictions...")
    for msg in cons:
        try:
            item = msg.value
            pred = item.get("prediction", item.get("prediction", item.get("prediction", {})))
            # If your message has 'prediction' nested, adapt; we saved prediction under 'prediction' key in model_worker
            final_score = item.get("prediction", item).get("final_score") if isinstance(item.get("prediction", None), dict) else item.get("final_score", 0)
            should_honeypot = item.get("prediction", {}).get("should_honeypot", False) if isinstance(item.get("prediction", None), dict) else item.get("should_honeypot", False)
            # fallback if top-level:
            final_score = final_score or item.get("final_score", 0)

            trigger = False
            if should_honeypot:
                trigger = True
            elif final_score and float(final_score) >= FINAL_SCORE_THRESHOLD:
                trigger = True

            if trigger:
                payload = {
                    "ts": item.get("ts", time.time()),
                    "final_score": final_score,
                    "should_honeypot": should_honeypot,
                    "raw": item.get("raw", {}),
                    "prediction": item.get("prediction", item.get("prediction", {}))
                }
                # log to Kafka topic for record
                prod.send(HONEYPOT_TOPIC, payload)
                prod.flush()
                print("[honeypot_worker] TRIGGERED -> final_score:", final_score)
                # call local honeypot API (optional)
                status, text = call_honeypot_api(payload)
                print("[honeypot_worker] honeypot api:", status, text)
        except Exception as e:
            print("[honeypot_worker] err:", e)

if __name__ == "__main__":
    main()
