# Database Maintenance Utilities

These scripts are standalone local maintenance and diagnostic tools for ABHEDYA's SQLite data stores. They are not imported by the application runtime.

Run them from the repository root so their existing relative database paths continue to resolve as originally written.

## Inspection

- `check_users.py` — prints rows from the local `users` table for development inspection.
- `check_login_log_stream.py` — prints recent Kafka-derived login events.
- `inspect_login_stream.py` — lists SQLite tables and recent login-stream rows.
- `inspect_honeypot.py` — inspects the local honeypot database/state.
- `list_intelligence_tables.py` — lists tables in the intelligence-assets database.
- `db_tables_summary.py` — prints table schemas and row counts as JSON.
- `query_db.py` — executes an explicitly supplied local SQLite query for debugging.

## Integrity and maintenance

- `db_integrity_check.py` — runs SQLite `PRAGMA integrity_check` and lists tables.
- `db_write_test.py` — performs a local SQLite write/lock smoke test.
- `sqlite_maintenance.py` — performs a WAL checkpoint and optional `VACUUM`.
- `safe_vacuum.py` — retries WAL checkpoint / `VACUUM` operations when locks are present.

## Setup and generated development data

- `create_intelligence_indexes.py` — creates indexes used by the local intelligence-assets database.
- `generate_intelligence_db.py` — builds the development intelligence-assets database used by the deception workflow.
- `dump_sqlite_all.py` — development-only SQLite inspection/export helper.

These utilities operate on local runtime databases, which are excluded from Git by repository hygiene rules. Maintenance commands that mutate or compact a database should be run only after backing up important local data and stopping conflicting writers.
