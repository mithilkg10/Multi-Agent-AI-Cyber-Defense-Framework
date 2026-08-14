# Manual Integration and Security Checks

These scripts exercise a locally running ABHEDYA environment. They are intentionally kept outside the automated CI suite because they require local services such as Flask, Kafka, TShark/Wireshark, SQLite runtime state, model artifacts, or the honeypot service.

Most were moved from the repository root without changing their executable content. They are retained as explicit lab utilities rather than production runtime components.

## Included checks

### Pipeline and model checks

- `test_tshark_capture.py` — captures a small number of packets from the configured local interface using PyShark.
- `test_hybrid_prediction.py` — runs a sample through the complete hybrid prediction pipeline and writes a local result artifact.
- `test_kafka_producer.py` — publishes a small login event to the local Kafka ingress topic.
- `test_kafka_consumer_writer.py` — consumes one local Kafka event and verifies the SQLite writer path.
- `send_high_rate_kafka_event.py` — publishes a deliberately high-rate feature payload for local pipeline testing.
- `send_anomaly_kafka_event.py` — publishes an event intended to exercise anomaly-scoring behavior.
- `send_honeypot_trigger.py` — publishes a controlled honeypot trigger to the local Kafka topic.

### Authentication and resilience checks

- `test_login_rate_limit.py` — sends a short sequence of invalid login attempts to the local dashboard.
- `test_rate_limit_burst.py` — exercises the configured login-rate threshold.
- `test_local_request_burst.py` — generates a bounded local HTTP request burst.
- `test_login_load.py` — generates a substantially heavier loopback-only login load. **Run this only in an isolated lab when you explicitly want a load test.**
- `test_force_block.py` — inserts a controlled test block into the local SQLite blocklist.

### Honeypot and input-handling checks

- `test_honeypot_e2e.py` — exercises suspicious-login redirection and inspects recent honeypot database events.
- `test_honeypot_endpoint.py` — probes the local honeypot endpoint with a test user agent.
- `test_beacon_simulation.py` — simulates periodic loopback beacon requests to the honeypot.
- `test_upload_rejection.py` — submits a synthetic PHP-like upload payload to the local application to test upload handling.
- `test_sql_injection_inputs.py` — submits common SQL-injection strings to the local application as defensive input-handling probes.

## Safety boundary

These utilities are for **controlled local or explicitly authorized environments only**. Their current targets are loopback/local ABHEDYA services. Do not repoint load, injection, or traffic-generation scripts at systems you do not own or have explicit permission to test.

Several scripts intentionally create local database rows or generated output. Runtime databases, captures, logs and generated test output remain excluded from version control.

## Automated tests

The dependency-light automated regression checks live in `tests/test_behavior_contracts.py` and run in GitHub Actions. They protect behavior-sensitive constants and pipeline defaults without requiring the full ML/network stack.
