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

## Engineering documentation

The repository deliberately separates implementation, security assumptions and research claims:

- [`ARCHITECTURE.md`](ARCHITECTURE.md) — component boundaries, data flow and behavior-sensitive interfaces
- [`docs/THREAT_MODEL.md`](docs/THREAT_MODEL.md) — assets, trust boundaries, attacker profiles, known security debt and abuse cases
- [`docs/EVALUATION.md`](docs/EVALUATION.md) — reproducible ML/security evaluation protocol and claims policy
- [`SECURITY.md`](SECURITY.md) — deployment boundaries, secret handling and responsible-use guidance
- [`docs/research/`](docs/research/) — preserved academic/research artifacts kept separate from runtime source

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

These distinctions are intentional: claims in this repository are limited to behavior that can be traced to the implementation. See [`docs/EVALUATION.md`](docs/EVALUATION.md) for the evidence standard used by the project.

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

### Python environment

Create and activate a virtual environment, then install the focused project dependencies:

```bash
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

The repository also contains model/runtime integrations whose exact compatibility should be validated against the environment used to train or export the supplied model artifacts.

### Environment configuration

`.env.example` documents environment variables that are read by the current code. The application does **not** automatically load `.env` files, so export/set these values in the process environment before starting the services.

For example, in PowerShell:

```powershell
$env:ABHEDYA_FLASK_SECRET = "replace-with-a-long-random-value"
$env:ABHEDYA_DEFAULT_ADMIN_PASSWORD = "replace-with-a-strong-unique-password"
$env:HONEYPOT_SECRET = "replace-with-a-long-random-value"
$env:HONEYPOT_HOST = "http://127.0.0.1:5001"
$env:KAFKA_BOOTSTRAP = "localhost:9092"
$env:ABHEDYA_LOG_HMAC_KEY = "replace-with-a-long-random-value"
```

Never commit real credentials or secret keys.

For compatibility with existing local/demo databases, the application retains explicit development fallbacks when the main session/admin/HMAC environment values are omitted. Configure the environment values above before any untrusted deployment.

### Authentication compatibility

Newly provisioned administrator credentials are stored using Werkzeug password hashing. Existing local databases that still contain legacy plaintext admin/user rows remain usable: after a successful legacy login, the stored credential is transparently upgraded to a password hash.

This migration keeps existing login behavior intact while removing plaintext comparison from the normal authentication path.

### Start

For the Windows-oriented integrated local workflow:

```bash
python start_abhedya.py
```

Individual services can also be started separately while debugging or testing their respective pipelines.

## Continuous integration

The lightweight GitHub Actions pipeline is intentionally dependency-light and protects repository/refactoring quality by checking:

- tracked runtime/generated artifacts are not reintroduced;
- core Python source files compile successfully;
- behavior-sensitive contracts such as ensemble weights, fallback threshold, Kafka topics and response action names remain unchanged;
- main-session configuration and compatibility-preserving password hardening remain present.

These checks do not replace full integration testing with Kafka, TShark, model artifacts and SQLite, but they provide a safe baseline for repository maintenance.

## Security status

ABHEDYA is a research prototype. Repository hardening separates development defaults, runtime data, debug artifacts and security-sensitive configuration from source-controlled application code. The main Flask session secret and first-run administrator password can be supplied through the environment; new administrator credentials are hashed, and legacy plaintext rows are upgraded on successful authentication.

See [`docs/THREAT_MODEL.md`](docs/THREAT_MODEL.md) and [`SECURITY.md`](SECURITY.md) for the current security boundaries and remaining debt.

## Repository hygiene

Runtime databases, packet captures, logs, local environment files, caches and generated diagnostics should not be committed. The repository `.gitignore` documents the intended boundary between source code and runtime state, and CI rejects the most important generated/runtime artifact classes if they are tracked again.

## Current limitations

- The application is currently optimized for a local Windows development environment.
- Several services expect locally running Kafka/ZooKeeper infrastructure.
- SQLite remains the primary persistence layer and is suitable for this prototype workload rather than horizontally scaled deployment.
- The DQN online retraining path does not currently provide an independent hold-out validation benchmark.
- Rule-based decision explanations are exposed as `xai_explanation`; SHAP/LIME attribution is not currently implemented.
- Development compatibility fallbacks remain available for session/admin/HMAC secrets when environment configuration is omitted; hardened deployments should explicitly configure those values.
- `app.py` remains a large historical Flask module and should only be decomposed incrementally behind regression tests.
- Production-grade CSRF protection, systematic route-authorization testing, authenticated/encrypted Kafka transport, deployment isolation and observability require additional hardening before internet-facing deployment.

## Responsible use

This repository is intended for defensive security research, controlled lab environments and authorized testing. Only capture, analyze or interact with systems for which you have explicit permission.
