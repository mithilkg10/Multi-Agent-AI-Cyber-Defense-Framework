# producer.py
from kafka import KafkaProducer
import json

def get_kafka_producer():
    try:
        producer = KafkaProducer(
            bootstrap_servers=['localhost:9092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        print("✅ Kafka Producer Connected")
        return producer
    except Exception as e:
        print("❌ Kafka Producer Error:", e)
        return None
