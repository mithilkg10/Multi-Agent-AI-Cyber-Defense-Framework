# ABHEDYA Architecture

## Purpose

ABHEDYA is structured as a local, multi-process defensive-security prototype. It combines network telemetry, model inference, event streaming, persistence, deception, and administrative response workflows.

This document describes the implementation boundaries that exist in the repository today. It intentionally avoids presenting experimental components as production controls.

## Runtime topology

The integrated local workflow is orchestrated by `start_abhedya.py` and currently assumes a Windows development host.

```text
                    +----------------------+
                    | Network / PCAP input |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | TShark / PyShark     |
                    | capture & extraction |
                    +----------+-----------+
                               |
                +--------------+--------------+
                |                             |
                v                             v
       +------------------+          +------------------+
       | Kafka event path |          | Direct app path  |
       +--------+---------+          +---------+--------+
                |                              |
                +--------------+---------------+
                               |
                               v
                    +----------------------+
                    | Feature alignment    |
                    | feature_builder.py   |
                    +----------+-----------+
                               |
            +------------------+------------------+
            |                  |                  |
            v                  v                  v
       +---------+        +----------+       +---------+
       | XGBoost |        | CNN-LSTM |       |   DQN   |
       +----+----+        +----+-----+       +----+----+
            |                  |                  |
            +------------------+------------------+
                               |
                               v
                    +----------------------+
                    | Hybrid decision      |
                    | 0.4 / 0.4 / 0.2      |
                    +----------+-----------+
                               |
                    +----------+----------+
                    |                     |
                    v                     v
              +-----------+         +------------+
              | Dashboard |         | Honeypot   |
              | & history |         | trigger    |
              +-----------+         +-----+------+
                                          |
                                          v
                                   +-------------+
                                   | Decoy Flask |
                                   | service     |
                                   +-------------+
```

## Components

### Main Flask application

`app.py` currently owns several responsibilities:

- web routes and template rendering
- administrator workflows
- authentication and session handling
- SQLite initialization and access helpers
- login and detection telemetry
- blocklist state
- capture orchestration
- SSE/live-data endpoints
- Kafka consumer startup helpers

The file is intentionally documented as a refactoring candidate. Splitting it into blueprints/services would improve maintainability, but that change should be performed incrementally with route and behavior regression tests because the existing application is tightly coupled.

### Feature preparation

`backend/feature_builder.py` aligns raw traffic data with the feature schemas expected by the model wrappers. This layer is a critical compatibility boundary: changes to feature names, ordering, defaults, or encoding can change model output and must therefore be regression-tested.

### Model wrappers

The inference wrappers are:

- `backend/xgboost_module.py`
- `backend/cnn_lstm_module.py`
- `backend/dqn_module.py`

`backend/hybrid_decision.py` coordinates these outputs.

The ensemble currently calculates:

```text
final_score = 0.4 * xgb_score + 0.4 * cnn_score + 0.2 * dqn_score
```

A threshold is read from the `config` table, with a fallback of `0.65`.

Model exceptions currently fall back to neutral/default values inside the decision path. This preserves availability in the prototype but should be treated carefully in any production design because degraded-model state can affect decision confidence.

### Explanation layer

`explain_decision()` in `backend/hybrid_decision.py` provides rule-based feature highlights. It is intended to make dashboard decisions easier to inspect, but it is not a feature-attribution algorithm such as SHAP or LIME.

### Online DQN adaptation

`backend/dqn_retrain.py` can retrain a DQN policy from recent detection telemetry.

Important implementation properties:

- recent rows are read from SQLite;
- pseudo-labels may be derived from existing prediction/final-score data;
- the existing DQN model is loaded when available;
- the model is saved back to the configured model path;
- the reported post-training accuracy is calculated against samples from the same collected telemetry.

Accordingly, this metric is useful as a training/adaptation diagnostic but is not an independent test-set estimate of generalization.

### Kafka

Kafka is used for local event transport between components. The default producer targets `localhost:9092`. The startup orchestrator currently manages local ZooKeeper and Kafka processes and assumes a Windows Kafka installation.

Kafka failure is generally handled as a recoverable local-service condition in the application, allowing portions of the dashboard to continue operating while event-stream functionality is unavailable.

### Persistence

SQLite databases are used for prototype persistence, including:

- application users/admin state;
- login telemetry;
- detections and responses;
- blocklist/configuration state;
- DQN retraining records;
- honeypot access data;
- decoy/intelligence fixture data.

WAL and busy-timeout settings are used in several access paths to reduce contention from threaded workers.

Runtime database files are local state and should not be committed to source control.

### Deception service

`honeypot_app.py` is a standalone Flask application. It supports multiple personas and records access telemetry separately from the main dashboard database.

The service can generate deterministic decoy datasets from a session identifier and can expose finance-, SCADA-, or military-themed decoy records.

## Trust boundaries

### Browser to main application

Inputs reaching Flask routes should be treated as untrusted. Authentication, authorization, validation, and CSRF protections belong at this boundary.

### Main application to SQLite

SQL parameterization is required for values. Dynamic table/column construction should remain tightly constrained to known identifiers.

### Capture process to model pipeline

Packet-derived values are untrusted telemetry. Feature extraction must tolerate malformed, missing, or unexpected protocol fields without allowing arbitrary command or file access.

### Main application to Kafka

Kafka messages should be treated as untrusted unless the broker and producer identities are authenticated. Schema validation should be applied before persistence or response decisions in a production deployment.

### Main application to honeypot

The honeypot is intentionally exposed to suspicious interactions. It should remain isolated from sensitive production data and credentials. Decoy content must not become an accidental bridge to protected resources.

## Behavior-preservation constraints

The following are considered behavior-sensitive and should not be changed during repository cleanup without explicit regression validation:

- model feature ordering and preprocessing;
- trained model artifacts;
- ensemble weights;
- threat threshold semantics;
- Kafka topic/message contracts;
- detection and response schema semantics;
- packet-capture command behavior;
- honeypot persona behavior;
- public route and JSON response contracts.

## Recommended future decomposition

A future maintainability refactor could split `app.py` into modules such as:

```text
abhedya/
  auth/
  api/
  capture/
  detection/
  deception/
  persistence/
  reporting/
  streaming/
```

That refactor should be driven by tests rather than performed as a cosmetic rewrite.
