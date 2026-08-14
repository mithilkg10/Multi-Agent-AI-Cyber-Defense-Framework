# Security Policy

## Scope

ABHEDYA is a defensive-security research prototype intended for controlled laboratories, academic work, demonstrations, and authorized testing environments.

It should not be exposed directly to the public internet or used as the sole security control for production systems without additional hardening, deployment isolation, identity controls, monitoring, and independent validation.

## Responsible use

Use the project only on networks, hosts, accounts, and data for which you have explicit authorization. Packet capture, active response, blocking, and deception features can affect network behavior and should be tested in isolated or approved environments.

## Secrets

Do not commit:

- Flask session secrets;
- honeypot session secrets;
- detection-log HMAC keys;
- API tokens;
- private keys;
- real credentials;
- production database files;
- sensitive packet captures;
- exported login or event telemetry.

Use `.env.example` as a configuration reference and supply real values through the runtime environment or an appropriate secret-management system. Important runtime values include `ABHEDYA_FLASK_SECRET`, `ABHEDYA_DEFAULT_ADMIN_PASSWORD`, `HONEYPOT_SECRET`, and `ABHEDYA_LOG_HMAC_KEY`.

If a secret has ever been committed to a public repository, removing it from the current tree is not sufficient. Treat it as compromised and rotate it.

## Credential compatibility migration

Newly provisioned administrator credentials are stored with Werkzeug password hashing. Existing local databases containing legacy plaintext admin/user rows remain compatible: after a successful authentication, the matching row is rewritten with a password hash.

The project retains explicit legacy development values as fallbacks when the corresponding environment variables are omitted so existing local/demo workflows do not fail unexpectedly. Do not rely on those fallbacks for an untrusted deployment.

## Runtime data

The application generates security-sensitive runtime state, including databases, packet captures, honeypot logs, login events, and diagnostic output. These files should remain outside source control.

The repository `.gitignore` defines the expected boundary for common generated artifacts, and CI rejects the most important runtime/generated artifact classes if they are tracked again.

## Deployment boundaries

A hardened deployment should provide, at minimum:

- TLS termination;
- externally managed session, administrator and HMAC secrets;
- development compatibility fallbacks disabled or rejected;
- credential rotation policies;
- CSRF protection for state-changing browser actions;
- authenticated/authorized administrative routes;
- broker authentication and encryption for Kafka;
- network isolation between the honeypot and protected systems;
- restricted filesystem permissions for databases and model artifacts;
- structured security logging;
- dependency and container/image scanning;
- least-privilege service accounts;
- independent backups outside the application repository.

## Model-security considerations

Model outputs should be treated as signals rather than unquestionable security decisions. Production use should explicitly account for:

- false positives and false negatives;
- model failure/degraded-operation modes;
- data drift;
- poisoned or adversarial telemetry;
- validation-set separation;
- reproducibility of reported metrics;
- operator override and incident review.

See `docs/EVALUATION.md` for the repository's claims and evaluation standard.

## Honeypot isolation

The deception service is designed to receive suspicious interactions. Never populate it with real secrets or data that would create additional exposure. Any use of real-looking decoy records should remain synthetic, sanitized, or otherwise safe to disclose.

The controller validates attacker IP values before they are used in routing/firewall operations or forensic log filenames. This input validation does not replace process/network isolation around the honeypot.

## Reporting a vulnerability

If you identify a vulnerability in this project, avoid including real credentials, personal data, or sensitive packet content in a public issue. Provide a minimal reproduction and enough technical detail to understand the affected component and expected impact.
