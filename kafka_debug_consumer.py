from kafka import KafkaConsumer
import json

consumer = KafkaConsumer('network-traffic', bootstrap_servers=['localhost:9092'],
                         auto_offset_reset='latest', enable_auto_commit=True,
                         group_id='debug-consumer', value_deserializer=lambda x: json.loads(x.decode('utf-8')))

print("DEBUG CONSUMER STARTED")
for m in consumer:
    print("RECEIVED:", m.value)
