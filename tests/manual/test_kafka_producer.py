from kafka import KafkaProducer
import json, time

p = KafkaProducer(bootstrap_servers=['localhost:9092'],
                  value_serializer=lambda v: json.dumps(v).encode('utf-8'))
msg = {
    "username": "kafka_e2e_test_user",
    "ip_address": "127.0.0.1",
    "event": "login_test",
    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
}
p.send('network-traffic', value=msg)
p.flush()
print("SENT:", msg)
