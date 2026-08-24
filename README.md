# ABHEDYA

## Multi Agent AI Cyber Defense Framework

ABHEDYA is a research and engineering prototype for network security monitoring, hybrid threat scoring, deception, automated response, and security telemetry analysis.

The project combines packet derived telemetry, machine learning, reinforcement learning, Kafka event transport, Flask based security workflows, SQLite persistence, and a standalone honeypot service.

ABHEDYA is intended for defensive security research, controlled laboratories, academic demonstrations, and authorized testing. It is not presented as a production SIEM or as a replacement for independently validated security controls.

## What the system implements

### Hybrid threat scoring

The decision layer combines three model outputs:

* XGBoost for tabular traffic features
* CNN LSTM for learned traffic pattern scoring
* DQN for policy and action selection

The current ensemble is:

```text
0.4 × XGBoost score + 0.4 × CNN LSTM score + 0.2 × DQN action score
```

The final score is compared with a configurable threat threshold stored in SQLite. When the threshold is crossed, the decision layer can publish a deception trigger through Kafka.

### Network telemetry

The project includes:

* TShark and PyShark packet capture integration
* Kafka producers and consumers
* SQLite backed telemetry and detection records
* Server Sent Events for live views
* PCAP workflows
* Detection and response history

### Active deception

`honeypot_app.py` runs as a separate Flask service and supports multiple synthetic decoy personas. Honeypot interactions are logged independently and can be correlated with the main security workflow.

### Response workflows

The application includes:

* IP blocklisting and timed expiry
* Honeypot redirection
* Detection history
* Response history
* Administrative controls
* Login event monitoring
* Configurable threat thresholds

## Architecture

```text
Network traffic
      |
      v
TShark and PyShark
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
        XGBoost + CNN LSTM + DQN
                     |
          +----------+----------+
          |                     |
          v                     v
 Security dashboard       Deception trigger
                                |
                                v
                         Honeypot service
```

See `ARCHITECTURE.md` for component boundaries and data flow.

## Key components

| Path | Responsibility |
| --- | --- |
| `app.py` | Main Flask dashboard, API routes, persistence helpers, capture orchestration, and administrative workflows |
| `backend/feature_builder.py` | Aligns telemetry with model input schemas |
| `backend/xgboost_module.py` | XGBoost inference wrapper |
| `backend/cnn_lstm_module.py` | CNN LSTM inference wrapper |
| `backend/dqn_module.py` | DQN inference wrapper |
| `backend/hybrid_decision.py` | Ensemble scoring, threshold decision, and deception trigger publication |
| `backend/dqn_retrain.py` | Experimental DQN adaptation using recent stored detections |
| `kafka_models_consumer.py` | Kafka driven model processing path |
| `honeypot_app.py` | Standalone deception service |
| `honeypot_controller.py` | Honeypot control workflow |
| `start_abhedya.py` | Windows oriented local service orchestrator |

## Engineering documentation

The repository separates implementation, research claims, security assumptions, and evaluation boundaries.

* `ARCHITECTURE.md`: component boundaries and data flow
* `docs/THREAT_MODEL.md`: assets, trust boundaries, attacker profiles, abuse cases, and known debt
* `docs/EVALUATION.md`: evaluation protocol and claims policy
* `SECURITY.md`: deployment boundaries, secrets, and responsible use
* `docs/research/`: preserved academic and research artifacts

## Model and evaluation boundaries

The online DQN adaptation path may use recent detection records and pseudo labels derived from existing outputs when a ground truth label is unavailable.

For that reason, any retraining accuracy value should be interpreted as an adaptation or training diagnostic rather than an independent generalization benchmark.

The current `xai_explanation` output is a rule based explanation layer. It is not a SHAP or LIME attribution implementation.

These distinctions are intentional and are documented so the repository does not make claims that exceed its evidence.

## Technology

* Python
* Flask
* SQLite
* Apache Kafka
* TShark
* PyShark
* XGBoost
* TensorFlow and Keras compatible model artifacts
* Stable Baselines3 DQN
* Jinja templates
* HTML, CSS, and JavaScript

## Local development

### Prerequisites

The current integrated startup workflow is Windows oriented and expects:

* Python 3
* TShark or Wireshark available on the host
* Apache Kafka and ZooKeeper available locally
* Kafka available at `localhost:9092`

The orchestrator currently assumes a Kafka installation under:

```text
C:\kafka\kafka
```

Adjust that local path for your own environment.

### Python environment

```bash
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Environment configuration

`.env.example` documents the environment variables read by the current application.

Example PowerShell configuration:

```powershell
$env:ABHEDYA_FLASK_SECRET = "replace-with-a-long-random-value"
$env:ABHEDYA_DEFAULT_ADMIN_PASSWORD = "replace-with-a-strong-unique-password"
$env:HONEYPOT_SECRET = "replace-with-a-long-random-value"
$env:HONEYPOT_HOST = "http://127.0.0.1:5001"
$env:KAFKA_BOOTSTRAP = "localhost:9092"
$env:ABHEDYA_LOG_HMAC_KEY = "replace-with-a-long-random-value"
```

Never commit real credentials, secrets, private keys, sensitive packet captures, or production database content.

### Start

```bash
python start_abhedya.py
```

## Continuous integration

The GitHub Actions baseline checks:

* Repository hygiene
* Python source compilation
* Behavior sensitive contracts
* Authentication hardening expectations
* Kafka topic and response contract stability

The current lightweight contract tests are intentionally dependency light. They do not replace full integration testing with Kafka, TShark, trained model artifacts, and SQLite.

## Security status

ABHEDYA is a research prototype.

The repository documents its current hardening state, secret handling expectations, authentication compatibility behavior, model security considerations, honeypot isolation requirements, and known production gaps.

See `SECURITY.md` and `docs/THREAT_MODEL.md`.

## Current limitations

* The integrated startup workflow is currently Windows oriented.
* Several services expect locally running Kafka and ZooKeeper infrastructure.
* SQLite is appropriate for the current prototype workload rather than horizontal production scale.
* DQN adaptation does not currently provide an independent holdout validation benchmark.
* The explanation layer is rule based rather than SHAP or LIME.
* Development compatibility fallbacks remain available for selected secrets.
* `app.py` remains a large historical Flask module.
* Production grade CSRF protection, route authorization testing, Kafka transport security, deployment isolation, and observability require further hardening.

## Responsible use

Use ABHEDYA only on systems, networks, accounts, and data for which you have explicit authorization.

See `SHOWCASE.md` for a concise reviewer path.
