# kafka_consumer_writer_test.py
from kafka import KafkaConsumer
import json, sqlite3, datetime, os, sys

print("cwd:", os.getcwd())
consumer = KafkaConsumer(
    'network-traffic',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='latest',
    enable_auto_commit=True,
    group_id='test-writer-group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)
print("consumer-writer started, waiting for a message... (send via producer)")

for msg in consumer:
    print("RECV:", msg.value)
    data = msg.value
    username = data.get("username", "unknown")
    ip = data.get("ip", data.get("ip_address", "unknown"))
    event = data.get("event", "unknown")
    timestamp = data.get("timestamp", datetime.datetime.now().isoformat())

    try:
        conn = sqlite3.connect("cyber_defense.db", timeout=30, check_same_thread=False)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS login_log_stream (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                ip_address TEXT,
                event TEXT,
                timestamp TEXT
            )
        """)
        cur.execute("INSERT INTO login_log_stream (username, ip_address, event, timestamp) VALUES (?, ?, ?, ?)",
                    (username, ip, event, timestamp))
        conn.commit()
        conn.close()
        print("WROTE to cyber_defense.db login_log_stream:", username)
    except Exception as e:
        print("DB write error:", e)
    # exit after first write for test
    break
print("exiting test consumer-writer")
sys.exit(0)
