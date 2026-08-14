# Legacy Development Artifacts

This directory preserves historical development material that is **not** part of the current runtime or recommended setup/evaluation path.

Files are kept for research traceability only. Do not use them as authoritative deployment, initialization, model-evaluation, or event-pipeline instructions.

## Why these files are archived

- `db_setup_legacy.py` creates an older simplified users schema and seeds a development credential. The active application initializes its own schema in `app.py`.
- `insert_honeypot_events_legacy.py` uses an older honeypot-event schema that does not match the current application tables.
- `accuracy_report_legacy.py`, `temp_metrics_legacy.py`, and `xgboost_accuracy_legacy.py` are historical evaluation helpers with assumptions that do not represent the current evaluation standard. In particular, some use local dataset paths or fixed classification cutoffs rather than the current configured decision threshold.
- `model_worker_legacy.py` and `honeypot_worker_legacy.py` represent an older two-worker Kafka flow. The integrated launcher currently uses `kafka_models_consumer.py` and `honeypot_controller.py` instead.

The current, implementation-aligned evaluation policy is documented in [`../EVALUATION.md`](../EVALUATION.md), and the active runtime components are documented in the repository root [`README.md`](../../../README.md) and [`ARCHITECTURE.md`](../../../ARCHITECTURE.md).
