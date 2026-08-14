# model_worker.py
import json
import time
from kafka import KafkaConsumer, KafkaProducer
from backend.hybrid_decision import predict_combined

KAFKA_BOOTSTRAP = "localhost:9092"
CONSUME_TOPIC = "network-traffic"   # source topic (pyshark -> network-traffic)
PRODUCE_TOPIC = "predictions"
GROUP_ID = "model-worker-group"

def make_producer():
    return KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP,
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )

def make_consumer():
    return KafkaConsumer(
        CONSUME_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP,
        group_id=GROUP_ID,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset="latest",
        enable_auto_commit=True
    )

def main():
    prod = make_producer()
    cons = make_consumer()
    print("[model_worker] Listening on", CONSUME_TOPIC)
    for msg in cons:
        try:
            raw = msg.value
            # raw is expected to be a dict of features (same shape as your test payload)
            result = predict_combined(raw)
            # enrich with original timestamp & raw
            out = {
                "ts": raw.get("_ts") or time.time(),
                "raw": raw,
                "prediction": result
            }
            prod.send(PRODUCE_TOPIC, out)
            prod.flush()
            print("[model_worker] produced prediction ->", out["prediction"]["final_score"])
        except Exception as e:
            print("[model_worker] Error:", e)

if __name__ == "__main__":
    main()
