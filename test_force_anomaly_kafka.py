# test_force_anomaly_kafka.py
# Purpose: inject a crafted login event into Kafka that should cause anomaly_detector
# to compute a high score (IP prefix rule + noise + optional night-time boost).

from kafka import KafkaProducer
import json, time, datetime

p = KafkaProducer(bootstrap_servers=['localhost:9092'],
                  value_serializer=lambda v: json.dumps(v).encode('utf-8'))

# Choose a suspicious ip prefix your detector checks (45., 144., 23.)
event = {
    "username": "normal-looking-user",
    "ip_address": "45.0.0.55",
    "event": "login_success",
    "timestamp": datetime.datetime.now().isoformat()
}

print("Sending suspicious-kafka event:", event)
p.send("network-traffic", event)
p.flush()
print("SENT")
