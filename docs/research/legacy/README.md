# Legacy Development Artifacts

This directory preserves historical development material that is **not** part of the current runtime or recommended setup path.

Files are kept for research traceability only. Do not use them as authoritative deployment or initialization instructions.

In particular, `db_setup_legacy.py` creates an older simplified users schema and seeds a development credential. The active application initializes its own schema in `app.py`; the legacy script is retained only to preserve project history without presenting it as a current setup utility.
