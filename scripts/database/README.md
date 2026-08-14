# Database Maintenance Utilities

These scripts are standalone local maintenance and diagnostic tools for ABHEDYA's SQLite data stores. They are not imported by the application runtime.

Run them from the repository root so their existing relative database paths continue to resolve as originally written.

## Utilities

- `check_users.py` — prints rows from the local `users` table for development inspection.
- `check_login_log_stream.py` — prints the most recent Kafka-derived login events.
- `db_integrity_check.py` — runs SQLite `PRAGMA integrity_check` and lists tables.
- `db_tables_summary.py` — prints table schemas and row counts as JSON.
- `db_write_test.py` — performs a local SQLite write/lock smoke test.
- `create_intelligence_indexes.py` — creates indexes used by the local intelligence-assets database.
- `dump_sqlite_all.py` — development-only SQLite inspection/export helper.

These tools operate on local runtime databases, which are excluded from Git by repository hygiene rules.
