"""Kafka producer factory used by ABHEDYA services."""

import json
import os

from kafka import KafkaProducer


DEFAULT_KAFKA_BOOTSTRAP = "localhost:9092"


def _bootstrap_servers():
    """Return configured Kafka brokers while preserving the historical local default."""
    raw = os.environ.get("KAFKA_BOOTSTRAP", DEFAULT_KAFKA_BOOTSTRAP)
    servers = [server.strip() for server in raw.split(",") if server.strip()]
    return servers or [DEFAULT_KAFKA_BOOTSTRAP]


def get_kafka_producer():
    """Create a JSON Kafka producer, returning ``None`` when Kafka is unavailable."""
    try:
        producer = KafkaProducer(
            bootstrap_servers=_bootstrap_servers(),
            value_serializer=lambda value: json.dumps(value).encode("utf-8"),
        )
        print("✅ Kafka Producer Connected")
        return producer
    except Exception as exc:
        print("❌ Kafka Producer Error:", exc)
        return None
