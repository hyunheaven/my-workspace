"""Offline, conservative pre-commit audit. It does not replace human/security review.

Usage (after git add): python scripts/check_before_commit.py
"""
from __future__ import annotations
import re
import subprocess
import sys
from pathlib import Path

MAX_BYTES = 2_000_000
FORBIDDEN_PARTS = {"data", "userdata", "attachments", "uploads", "exports", "backups", "local-data", "secrets", "credentials", ".venv", "node_modules", "__pycache__", ".pytest_cache"}
FORBIDDEN_SUFFIXES = {".db", ".sqlite", ".sqlite3", ".bak", ".zip", ".pfx", ".p12", ".pem", ".key", ".kdbx", ".mp3", ".mp4", ".mov", ".avi", ".wav", ".webm", ".ogg"}
SECRET_MARKERS = [
    ("private-key block", re.compile(r"-----BEGIN (?:OPENSSH |RSA |EC |DSA )?PRIVATE KEY-----")),
    ("GitHub token prefix", re.compile(r"(?:ghp_|gho_|ghu_|ghs_|ghr_)[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,}")),
    ("OpenAI-style key prefix", re.compile(r"(?<![A-Za-z0-9_-])sk-(?:proj-)?[A-Za-z0-9_-]{24,}")),
    ("AWS access key pattern", re.compile(r"(?:AKIA|ASIA)[0-9A-Z]{16}")),
]


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(["git", "diff", "--cached", "--name-only", "-z"], cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode:
        print("FAIL: staging area not available. Run git init and git add first.")
        return 2
    paths = [Path(p.decode("utf-8", errors="replace")) for p in result.stdout.split(b"\0") if p]
    if not paths:
        print("FAIL: no staged files")
        return 1
    failures = []
    for relative in paths:
        if relative.is_absolute() or ".." in relative.parts:
            failures.append(f"unsafe path: {relative}")
            continue
        parts = {p.lower() for p in relative.parts}
        p = root / relative
        if parts & FORBIDDEN_PARTS or relative.suffix.lower() in FORBIDDEN_SUFFIXES or relative.name.lower() in {".env", "id_rsa", "id_ed25519"}:
            failures.append(f"forbidden path or file type: {relative}")
            continue
        staged = subprocess.run(["git", "show", ":" + relative.as_posix()], cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if staged.returncode:
            # Removed paths have no blob at stage 0; still require manual diff review.
            if not p.exists():
                continue
            failures.append(f"could not inspect staged blob: {relative}")
            continue
        data = staged.stdout
        if len(data) > MAX_BYTES:
            failures.append(f"large file ({len(data)} bytes): {relative}")
        if b"\0" in data:
            failures.append(f"binary/NUL bytes: {relative}")
            continue
        text = data.decode("utf-8", errors="replace")
        for label, pattern in SECRET_MARKERS:
            if pattern.search(text):
                failures.append(f"possible {label}: {relative}")
    print(f"Staged files checked: {len(paths)}")
    for issue in failures:
        print(f"BLOCK: {issue}")
    if failures:
        print("FAILED: do not commit/push until reviewed and fixed.")
        return 1
    print("PASS: no forbidden paths or obvious token patterns found; human review is still required.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
