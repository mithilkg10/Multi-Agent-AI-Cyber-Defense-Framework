# send_kafka_test.py
import json
from kafka import KafkaProducer
import time

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

payload = {
    "src_ip":"10.0.0.99",
    "dst_ip":"172.16.0.8",
    "Protocol Type":"TCP",
    "Rate":9999,
    "IAT":0.00001,
    "syn_flag_number": 1,
    "ack_flag_number": 0,
    "_ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
}

producer.send("network-traffic", payload)
producer.flush()
print("sent:", payload)
producer.close()
