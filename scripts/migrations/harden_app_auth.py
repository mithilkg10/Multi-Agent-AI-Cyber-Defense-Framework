#!/usr/bin/env python3
"""Apply the compatibility-preserving ABHEDYA authentication hardening patch.

This migration intentionally edits only exact, known snippets in ``app.py``. It
aborts if the expected legacy source is not present, which prevents a broad or
ambiguous rewrite of the monolithic Flask application.

The migration preserves existing user-facing login behavior:

* the historical Flask session secret remains the fallback when no environment
  override is configured;
* the historical default administrator password remains the fallback for a new
  local database, but is stored as a Werkzeug password hash;
* existing plaintext admin/user rows continue to authenticate and are upgraded
  to a password hash after the first successful login.
"""

from __future__ import annotations

from pathlib import Path
import sys


APP_PATH = Path(__file__).resolve().parents[2] / "app.py"


def replace_exact(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise RuntimeError(
            f"{label}: expected exactly one legacy snippet, found {count}. "
            "Refusing to modify app.py."
        )
    return source.replace(old, new, 1)


def main() -> int:
    source = APP_PATH.read_text(encoding="utf-8")

    # Idempotent success when the migration has already been applied.
    if (
        'ABHEDYA_FLASK_SECRET' in source
        and 'generate_password_hash' in source
        and '_password_matches_and_upgrade' in source
    ):
        print("Authentication hardening is already applied.")
        return 0

    source = replace_exact(
        source,
        "import logging\n\nproducer = None",
        "import logging\n"
        "import hmac as _password_hmac\n"
        "from werkzeug.security import check_password_hash, generate_password_hash\n\n"
        "producer = None",
        "security imports",
    )

    source = replace_exact(
        source,
        'app = Flask(__name__)\napp.secret_key = "supersecretkey"\n',
        'app = Flask(__name__)\n'
        '_LEGACY_FLASK_SECRET = "supersecretkey"\n'
        'app.secret_key = os.environ.get("ABHEDYA_FLASK_SECRET", _LEGACY_FLASK_SECRET)\n'
        'if app.secret_key == _LEGACY_FLASK_SECRET:\n'
        '    print("⚠️ ABHEDYA_FLASK_SECRET is not configured; using the legacy development session secret.")\n',
        "Flask session secret",
    )

    legacy_admin_block = '''def create_default_admin():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admins WHERE username='admin'")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO admins (username, password, full_name) VALUES (?, ?, ?)",
            ("admin", "Admin@123", "System Administrator")
        )
        conn.commit()
        print("✅ Default admin created: admin / Admin@123")
    conn.close()
'''

    hardened_admin_block = '''def _password_matches_and_upgrade(cursor, table, row, candidate_password):
    """Verify a password and transparently migrate legacy plaintext rows."""
    stored = str(row["password"] or "")
    candidate = str(candidate_password or "")

    if stored.startswith(("scrypt:", "pbkdf2:")):
        try:
            return check_password_hash(stored, candidate)
        except (ValueError, TypeError):
            return False

    if not _password_hmac.compare_digest(stored, candidate):
        return False

    upgraded = generate_password_hash(candidate)
    if table == "admins":
        cursor.execute("UPDATE admins SET password=? WHERE id=?", (upgraded, row["id"]))
    elif table == "users":
        cursor.execute("UPDATE users SET password=? WHERE id=?", (upgraded, row["id"]))
    else:
        raise ValueError(f"Unsupported credential table: {table}")
    return True


def create_default_admin():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admins WHERE username='admin'")
    if not cursor.fetchone():
        default_password = os.environ.get("ABHEDYA_DEFAULT_ADMIN_PASSWORD", "Admin@123")
        cursor.execute(
            "INSERT INTO admins (username, password, full_name) VALUES (?, ?, ?)",
            ("admin", generate_password_hash(default_password), "System Administrator")
        )
        conn.commit()
        if default_password == "Admin@123":
            print("⚠️ Default admin created with the legacy development password. Set ABHEDYA_DEFAULT_ADMIN_PASSWORD before first run.")
        else:
            print("✅ Default admin created using ABHEDYA_DEFAULT_ADMIN_PASSWORD.")
    conn.close()
'''

    source = replace_exact(
        source,
        legacy_admin_block,
        hardened_admin_block,
        "default admin and password migration helper",
    )

    legacy_check_user = '''# -------------------- Authentication checks --------------------
def check_user(username, password):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM admins WHERE username=?", (username,))
    admin = cursor.fetchone()
    if admin:
        if admin["password"] == password:
            cursor.execute("UPDATE admins SET last_login=? WHERE id=?", 
                           (datetime.datetime.now().isoformat(), admin["id"]))
            conn.commit()
            conn.close()
            return {"username": admin["username"], "role": "admin"}
        conn.close()
        return None

    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    if user:
        if user["password"] == password:
            cursor.execute("UPDATE users SET last_login=? WHERE id=?", 
                           (datetime.datetime.now().isoformat(), user["id"]))
            conn.commit()
            conn.close()
            return {"username": user["username"], "role": "user"}
        conn.close()
        return None

    conn.close()
    return None
'''

    hardened_check_user = '''# -------------------- Authentication checks --------------------
def check_user(username, password):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM admins WHERE username=?", (username,))
    admin = cursor.fetchone()
    if admin:
        if _password_matches_and_upgrade(cursor, "admins", admin, password):
            cursor.execute("UPDATE admins SET last_login=? WHERE id=?",
                           (datetime.datetime.now().isoformat(), admin["id"]))
            conn.commit()
            conn.close()
            return {"username": admin["username"], "role": "admin"}
        conn.close()
        return None

    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    if user:
        if _password_matches_and_upgrade(cursor, "users", user, password):
            cursor.execute("UPDATE users SET last_login=? WHERE id=?",
                           (datetime.datetime.now().isoformat(), user["id"]))
            conn.commit()
            conn.close()
            return {"username": user["username"], "role": "user"}
        conn.close()
        return None

    conn.close()
    return None
'''

    source = replace_exact(
        source,
        legacy_check_user,
        hardened_check_user,
        "credential verification",
    )

    # Guardrails: the migration must remove the exact unsafe runtime assignments
    # while retaining compatibility strings only as explicit fallbacks.
    if 'app.secret_key = "supersecretkey"' in source:
        raise RuntimeError("Hard-coded Flask secret assignment still present after migration")
    if 'admin["password"] == password' in source or 'user["password"] == password' in source:
        raise RuntimeError("Plaintext credential comparison still present after migration")

    APP_PATH.write_text(source, encoding="utf-8", newline="\n")
    print("Applied compatibility-preserving authentication hardening to app.py.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"Migration failed safely: {exc}", file=sys.stderr)
        sys.exit(1)
