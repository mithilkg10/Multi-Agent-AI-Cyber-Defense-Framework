# ABHEDYA Threat Model

## Purpose

This document describes the security assumptions and trust boundaries of the current ABHEDYA research prototype. It is intentionally conservative: it records what the implementation is designed to protect, what it currently assumes, and where additional hardening is required before any internet-facing or production deployment.

## System scope

ABHEDYA combines several security-sensitive components:

- packet capture through TShark/PyShark workflows;
- Kafka-based event transport;
- XGBoost, CNN-LSTM and DQN inference components;
- SQLite-backed detection, response and authentication state;
- a Flask SIEM-style dashboard and administrative surface;
- a separate Flask honeypot/deception service;
- automated response records and blocklist workflows.

The current deployment model is a controlled local/lab environment rather than a hostile multi-tenant production network.

## Assets

The most important assets are:

1. **Detection integrity** — model inputs, scores, thresholds and response decisions must not be silently altered.
2. **Model artifacts** — trained model files, scalers, feature lists and label encoders must remain trustworthy.
3. **Administrative access** — dashboard sessions and administrator credentials must not be forged or reused by unauthorized users.
4. **Telemetry confidentiality and integrity** — packet-derived events, login records, detection records and honeypot events may contain security-sensitive information.
5. **Kafka event integrity** — forged or modified messages can influence downstream detection or deception behavior.
6. **Detection-log integrity** — stored detection metadata and its HMAC signature should remain verifiable.
7. **Deception isolation** — the honeypot must not become a bridge into protected or real data stores.
8. **Response integrity** — blocklist and honeypot-routing decisions must not be triggered by unauthorized control paths.

## Trust boundaries

### Browser / operator -> main Flask application

Requests cross from an untrusted client into the dashboard, authentication routes, APIs and administrative workflows.

Primary concerns:

- authentication bypass;
- session forgery;
- CSRF on state-changing actions;
- authorization gaps;
- malicious form or JSON input;
- information leakage through error responses.

### Main application -> SQLite

The application persists users, login activity, detections, configuration, captures, blocklist entries and responses.

Primary concerns:

- credential exposure;
- database tampering;
- unsafe runtime copies or exports;
- concurrency/locking failure;
- unauthorized reads of sensitive telemetry.

### Capture pipeline -> application/model pipeline

Network data is attacker-influenced by definition. Packet-derived features must therefore be treated as untrusted inputs.

Primary concerns:

- malformed traffic causing parser failures;
- adversarial traffic crafted to evade or manipulate classifiers;
- resource exhaustion;
- poisoned telemetry entering online adaptation paths.

### Application/services -> Kafka

Kafka transports login and model-processing events between services.

Primary concerns:

- unauthenticated publishers injecting events;
- consumers trusting forged payloads;
- message tampering or disclosure on an unencrypted broker;
- replay or unexpected backlog behavior.

The current local default is `localhost:9092`; broker authentication and transport encryption are outside the current prototype configuration.

### Hybrid decision layer -> model artifacts

The decision layer trusts local model files and preprocessing artifacts.

Primary concerns:

- malicious or stale model replacement;
- schema drift between feature builders and trained artifacts;
- silent fallback behavior masking model-load failures;
- disagreement between models being interpreted as confidence.

### Main application -> honeypot service

Suspicious activity may be redirected to the honeypot service.

Primary concerns:

- session or identifier leakage between services;
- accidental use of real sensitive data in decoys;
- honeypot compromise reaching protected resources;
- attacker-controlled payloads being stored or rendered unsafely.

The honeypot accesses its intelligence-data source using a read-only SQLite URI when that source is available. Network/process isolation should still be enforced externally for a hardened deployment.

## Attacker profiles

### Unauthenticated remote attacker

Capabilities may include:

- repeated login attempts;
- malformed usernames/passwords;
- crafted HTTP requests;
- probing exposed routes;
- attempts to trigger deception or response behavior.

### Network attacker / hostile traffic source

Capabilities may include:

- arbitrary packet patterns;
- DDoS-like traffic;
- scanning;
- brute-force attempts;
- traffic crafted to exploit feature extraction or model weaknesses.

### Kafka-capable attacker

If an attacker gains access to the broker, they may be able to inject or consume event streams. The current prototype does not assume a hostile shared Kafka deployment.

### Authenticated malicious or compromised user

An authenticated user may attempt to reach administrative functionality, alter configuration, inspect telemetry or manipulate response controls outside their role.

### Local filesystem attacker

A user with write access to the repository/runtime directory may be able to replace model artifacts, databases or configuration and therefore alter system behavior.

## Existing controls visible in the implementation

The repository currently includes several defensive mechanisms:

- rate tracking for repeated login attempts and automatic blocklist insertion;
- role-based session state used by the dashboard workflow;
- environment-configurable Flask session signing with an explicit local-compatibility fallback;
- Werkzeug password hashing for newly provisioned administrator credentials;
- transparent upgrade of legacy plaintext admin/user rows to password hashes after a successful login;
- SQLite parameterized statements in many persistence paths;
- WAL-oriented SQLite configuration for concurrent local access;
- a separate deception service rather than rendering all decoy behavior inside the primary dashboard process;
- Kafka JSON deserialization that rejects invalid/blank messages;
- HMAC-SHA256 signatures for stored detection metadata;
- environment-configurable HMAC signing key with a compatibility fallback;
- configurable Kafka endpoints/topics with stable local defaults;
- validated/canonicalized attacker IP values before honeypot-controller firewall and forensic-log operations;
- read-only access mode for the honeypot intelligence source where used;
- repository controls that prevent runtime databases, PCAPs and exported telemetry from being committed again;
- CI guards for behavior-sensitive model/pipeline/security contracts.

These controls reduce risk but do not make the prototype production-ready.

## Known security debt

### Development compatibility fallbacks

The application now supports `ABHEDYA_FLASK_SECRET`, `ABHEDYA_DEFAULT_ADMIN_PASSWORD`, and `ABHEDYA_LOG_HMAC_KEY` through the runtime environment. To preserve the behavior of existing local/demo deployments, legacy development values remain explicit fallbacks when those variables are absent.

For any untrusted deployment, all three security values must be configured externally. A future production profile should fail closed rather than accepting development fallbacks.

Existing plaintext credential rows are accepted only as a migration path: a successful legacy login upgrades the stored value to a Werkzeug password hash. Newly provisioned administrator credentials are hashed before storage.

### Kafka transport security

The current local Kafka path does not configure TLS, SASL authentication or broker ACLs. A production-like environment must add those controls without changing application topic contracts.

### CSRF and browser hardening

State-changing browser routes should be reviewed for CSRF protection, secure cookie flags, SameSite behavior, session lifetime and cache-control headers.

### Route-level authorization review

Administrative endpoints should be systematically enumerated and verified to enforce the intended role checks. This should be covered by regression tests rather than inferred from route names.

### Main application maintainability

`app.py` remains a large monolithic Flask module with historical duplicate imports and development-era comments. Refactoring should be incremental and protected by route/auth/database regression tests so cleanup does not change behavior.

### Model and online-adaptation risk

Recent detections can feed the DQN adaptation workflow, including pseudo-labels derived from existing predictions/scores. A hostile telemetry source could therefore influence later adaptation if the training path is enabled without data-quality controls.

## Abuse cases to test

A security regression suite should eventually include:

- forged or expired sessions;
- unauthorized requests to every administrative route;
- CSRF attempts against state-changing routes;
- SQL/meta-character input in login and administrative fields;
- migration of legacy plaintext credential rows;
- malformed Kafka values and unexpected payload types;
- replayed detection events;
- corrupted or missing model artifacts;
- model exceptions and fallback behavior;
- malformed PCAP/packet input;
- honeypot payloads containing HTML/script content;
- invalid/non-IP honeypot-routing inputs;
- database-lock and partial-write scenarios;
- tampering with signed detection rows;
- attempts to access or mutate the honeypot's read-only intelligence source.

## Security objectives for future releases

Before describing ABHEDYA as deployment-ready, the project should be able to demonstrate:

- mandatory externally managed session/HMAC/admin secrets with development fallbacks disabled;
- explicit administrator authorization tests;
- CSRF and secure-cookie protections;
- authenticated/encrypted Kafka transport;
- isolated honeypot networking and storage;
- reproducible model evaluation on independent data;
- dependency/security scanning in CI;
- documented backup/recovery procedures;
- removal/rotation of any sensitive values exposed in historical Git commits;
- no sensitive runtime artifacts in the current source tree.

## Non-goals

This prototype does not claim to provide:

- guaranteed prevention of compromise;
- cryptographic integrity of the entire event pipeline;
- a replacement for enterprise IAM, EDR, NDR or SIEM products;
- independently validated zero-day detection;
- immunity to adversarial machine-learning attacks.

Those claims require substantially different evidence and deployment controls.
