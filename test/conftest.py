"""Test-suite fixtures that keep runs from mutating tracked files.

Consolidates setup through `test.establish_test_environment` so both
`pytest` and `unittest` share identical isolation guarantees.
"""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_TRACKED_LAM_DB = _ROOT / "tools" / "002_LLM_API_MOCK" / "lam.sqlite"


def pytest_configure(config: object = None) -> None:
    """Configure pytest to reuse the consolidated runner-independent environment."""
    from test import establish_test_environment
    establish_test_environment()


def probe_bwrap_available() -> bool:
    """Check if bubblewrap executable is available on PATH and runnable."""
    bwrap = shutil.which("bwrap")
    if not bwrap:
        return False
    try:
        import subprocess
        true_bin = shutil.which("true") or "/usr/bin/true"
        for probe_args in (
            [bwrap, "--unshare-user", "--ro-bind", "/", "/", "--", true_bin],
            [bwrap, "--unshare-user", "--ro-bind", "/usr", "/usr", "--", true_bin],
            [bwrap, "--unshare-user", "--ro-bind", "/usr", "/usr", "--", "/bin/true"],
        ):
            try:
                res = subprocess.run(
                    probe_args,
                    check=False,
                    capture_output=True,
                    timeout=2,
                )
                if res.returncode == 0:
                    return True
            except (OSError, Exception):
                continue
        return False
    except (OSError, Exception):
        return False


def probe_lda_index_available() -> bool:
    """Check if LDA SQLite database is initialized and non-empty."""
    lda_db = _ROOT / ".lda" / "index.db"
    return lda_db.is_file() and lda_db.stat().st_size > 0


def require_bwrap(*, allow_skip: bool = False) -> None:
    """Ensure bubblewrap containment is available; fail closed if absent (NT-B03)."""
    if not probe_bwrap_available():
        msg = "Bubblewrap (bwrap) not available or user namespaces restricted on host"
        if allow_skip:
            import unittest
            raise unittest.SkipTest(msg)
        raise RuntimeError(f"BLOCKER: {msg}")


def require_lda(*, allow_skip: bool = False) -> None:
    """Ensure LDA index is initialized and non-empty; fail closed if absent (NT-B03)."""
    if not probe_lda_index_available():
        msg = "LDA index (.lda/index.db) not built or empty"
        if allow_skip:
            import unittest
            raise unittest.SkipTest(msg)
        raise RuntimeError(f"BLOCKER: {msg}")



