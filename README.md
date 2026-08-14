# ABHEDYA — Multi-Agent AI Cyber Defense Framework

ABHEDYA is a research and engineering prototype for network-security monitoring, multi-model threat scoring, deception, and response orchestration. The system combines packet-derived telemetry, supervised and reinforcement-learning components, Kafka-based event flow, a Flask SIEM-style dashboard, and a standalone honeypot service.

The repository is intended to demonstrate the architecture and implementation of an end-to-end cyber-defense pipeline. It is not presented as a production SIEM or as a replacement for independently validated security controls.

## What the system implements

### Hybrid threat scoring

`backend/hybrid_decision.py` combines three model outputs:

- **XGBoost** for tabular traffic features
- **CNN-LSTM** for learned traffic-pattern scoring
- **DQN** for policy/action selection

The current ensemble score is calculated as:

```text
0.4 × XGBoost score + 0.4 × CNN-LSTM score + 0.2 × DQN action score
```

The final score is evaluated against a configurable threat threshold stored in SQLite. When the threshold is crossed, the decision layer can publish a honeypot trigger through Kafka.

### Network telemetry and event pipeline

The project includes:

- TShark/PyShark packet-capture integration
- Kafka producers and consumers for event transport
- SQLite-backed telemetry and detection records
- server-sent-event and dashboard endpoints for live views
- capture management and PCAP handling

### Active deception

`honeypot_app.py` runs as a separate Flask service and supports multiple decoy personas, including finance, SCADA-like, and military-themed datasets. Accesses are logged to a dedicated honeypot database and can be correlated with the main application workflow.

### Response and administration

The application contains mechanisms for:

- IP blocklisting and timed expiry
- honeypot redirection
- detection and response history
- administrator views and manual controls
- login-event monitoring
- configurable thresholds

## Architecture

```text
Network traffic
      |
      v
TShark / PyShark capture
      |
      v
Feature preparation
      |
      +-----------------------------+
      |                             |
      v                             v
Kafka event flow             Direct prediction path
      |                             |
      +--------------+--------------+
                     |
                     v
             Hybrid decision layer
         XGBoost + CNN-LSTM + DQN
                     |
          +----------+----------+
          |                     |
          v                     v
   SIEM/dashboard          Deception trigger
                                |
                                v
                         Honeypot service
```

See [`ARCHITECTURE.md`](ARCHITECTURE.md) for component boundaries and data flow.

## Key components

| Path | Responsibility |
|---|---|
| `app.py` | Main Flask dashboard, API routes, persistence helpers, capture orchestration and administrative workflows |
| `backend/feature_builder.py` | Aligns raw telemetry with model input schemas |
| `backend/xgboost_module.py` | XGBoost inference wrapper |
| `backend/cnn_lstm_module.py` | CNN-LSTM inference wrapper |
| `backend/dqn_module.py` | DQN inference wrapper |
| `backend/hybrid_decision.py` | Ensemble scoring, threshold decision and honeypot trigger publication |
| `backend/dqn_retrain.py` | Experimental online DQN adaptation using recent stored detections |
| `anomaly_detector.py` | Anomaly-monitoring workflow |
| `kafka_models_consumer.py` | Kafka-driven model-processing path |
| `honeypot_app.py` | Standalone deception service |
| `honeypot_controller.py` | Honeypot-control workflow |
| `start_abhedya.py` | Windows-oriented local service orchestrator |

## Model and evaluation notes

The repository contains trained model artifacts and scripts used to inspect model performance. The online DQN retraining path uses recent detection records as training telemetry and may derive pseudo-labels from existing predictions/scores when a label is unavailable.

For that reason, the retraining `accuracy` value should be interpreted as an **adaptation/training diagnostic**, not an independent generalization benchmark.

The current `xai_explanation` output is a **rule-based explanation layer** that highlights selected traffic features. It is not a SHAP or LIME implementation.

These distinctions are intentional: claims in this repository are limited to behavior that can be traced to the implementation.

## Technology

- **Backend:** Python, Flask, SQLite
- **Streaming:** Apache Kafka
- **Network analysis:** TShark, PyShark, Wireshark-compatible PCAP workflows
- **ML:** XGBoost / scikit-learn ecosystem, TensorFlow/Keras-compatible CNN-LSTM artifacts, Stable-Baselines3 DQN
- **Frontend:** Jinja templates, HTML, CSS, JavaScript
- **Concurrency:** Python threads, queues, SQLite WAL-oriented access patterns

## Local development

### Prerequisites

The current startup orchestrator is Windows-oriented and expects:

- Python 3
- TShark/Wireshark available on the host
- Apache Kafka and ZooKeeper available locally
- Kafka configured at `localhost:9092`

`start_abhedya.py` currently assumes a Kafka installation under:

```text
C:\kafka\kafka
```

Adjust that local configuration for your environment before using the orchestrator.

### Environment configuration

Copy the example file and replace placeholder secrets where supported by your runtime configuration:

```bash
copy .env.example .env
```

Never commit real credentials or secret keys.

### Start

For the Windows-oriented integrated local workflow:

```bash
python start_abhedya.py
```

Individual services can also be started separately while debugging or testing their respective pipelines.

## Security status

ABHEDYA is a research prototype. The hardening branch is actively separating development defaults, runtime data, debug artifacts and security-sensitive configuration from source-controlled application code.

See [`SECURITY.md`](SECURITY.md) for responsible-use and security notes.

## Repository hygiene

Runtime databases, packet captures, logs, local environment files, caches and generated diagnostics should not be committed. The repository `.gitignore` documents the intended boundary between source code and runtime state.

## Current limitations

- The application is currently optimized for a local Windows development environment.
- Several services expect locally running Kafka/ZooKeeper infrastructure.
- SQLite remains the primary persistence layer and is suitable for this prototype workload rather than horizontally scaled deployment.
- The DQN online retraining path does not currently provide an independent hold-out validation benchmark.
- Rule-based decision explanations are exposed as `xai_explanation`; SHAP/LIME attribution is not currently implemented.
- Production-grade identity, secret management, deployment isolation and observability require additional hardening before internet-facing deployment.

## Responsible use

This repository is intended for defensive security research, controlled lab environments and authorized testing. Only capture, analyze or interact with systems for which you have explicit permission.
