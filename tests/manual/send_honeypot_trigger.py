from kafka import KafkaProducer
import json, time
p = KafkaProducer(bootstrap_servers=["localhost:9092"], value_serializer=lambda v: json.dumps(v).encode("utf-8"))
msg = {
  "src_ip": "10.0.0.55",
  "detection_id": "det-TEST-001",
  "final_score": 0.82,
  "asset_id": "AST-XXXX",    # replace with an actual asset_id from your intelligence_assets DB to test linking
  "operation_code": None
}
p.send("honeypot_triggers", msg)
p.flush()
print("sent")
