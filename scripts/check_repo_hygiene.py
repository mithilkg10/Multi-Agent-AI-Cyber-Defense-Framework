#!/usr/bin/env python3
"""Fail CI when generated/runtime artifacts are accidentally tracked."""

from __future__ import annotations

import subprocess
import sys
from pathlib import PurePosixPath


FORBIDDEN_PREFIXES = (
    "captures/",
    "db_exports/",
    "honeypot_logs/",
    "scratch/",
)

FORBIDDEN_EXACT = {
    "directory_structure.txt",
    "project_diagnostics.txt",
    "db_dump_summary.json",
    "test_predict_output.json",
}

FORBIDDEN_SUFFIXES = (
    ".bak",
    ".db",
    ".db-wal",
    ".db-shm",
    ".pcap",
    ".pcapng",
    ".pyc",
)


def tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        check=True,
        capture_output=True,
    )
    return [
        entry.decode("utf-8", errors="surrogateescape")
        for entry in result.stdout.split(b"\0")
        if entry
    ]


def is_forbidden(path: str) -> bool:
    normalized = str(PurePosixPath(path))
    if normalized in FORBIDDEN_EXACT:
        return True
    if normalized.startswith(FORBIDDEN_PREFIXES):
        return True
    return normalized.lower().endswith(FORBIDDEN_SUFFIXES)


def main() -> int:
    violations = sorted(path for path in tracked_files() if is_forbidden(path))
    if not violations:
        print("Repository hygiene check passed.")
        return 0

    print("Repository hygiene check failed. Remove generated/runtime artifacts:")
    for path in violations:
        print(f"  - {path}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
