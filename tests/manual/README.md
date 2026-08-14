# Manual Integration and Security Checks

These scripts exercise a locally running ABHEDYA environment. They are intentionally kept outside the automated CI suite because they require local services such as Flask, Kafka, TShark/Wireshark, SQLite runtime state, or the honeypot service.

They were moved from the repository root without changing their executable content.

## Included checks

- `test_tshark_capture.py` — captures a small number of packets from the configured local interface using PyShark.
- `test_login_rate_limit.py` — sends a short series of invalid login attempts to the local dashboard.
- `test_local_request_burst.py` — generates a bounded local HTTP request burst for resilience testing.
- `test_honeypot_e2e.py` — exercises suspicious-login redirection and inspects recent honeypot database events.

## Safety

Run these scripts only against a local lab or another system for which you have explicit authorization. The current scripts are hard-coded to loopback addresses and are intended for ABHEDYA development/testing.

## Automated tests

The dependency-light automated regression checks live in `tests/test_behavior_contracts.py` and run in GitHub Actions. They protect behavior-sensitive constants and pipeline defaults without requiring the full ML/network stack.
