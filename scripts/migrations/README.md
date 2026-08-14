# Compatibility Migrations

This directory contains narrowly scoped, assertion-based migration utilities used to harden legacy ABHEDYA state without changing the behavior-sensitive detection pipeline.

## `harden_app_auth.py`

This migration was used to update the historical authentication implementation in the monolithic `app.py` without replacing the entire file through an external editor.

It is intentionally idempotent and fail-closed:

- exact legacy snippets must match before a modification is made;
- the main Flask secret becomes runtime-configurable while retaining the historical local fallback;
- newly created administrator passwords are hashed before storage;
- existing plaintext admin/user rows remain compatible and are re-hashed after the first successful login;
- direct plaintext password comparisons are removed from the active authentication path.

The migration script remains in the repository as an auditable record of how compatibility was preserved. It is not part of normal application startup.
