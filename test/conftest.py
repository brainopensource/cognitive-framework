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


class ContainmentBlocker(RuntimeError):
    """Typed blocker raised when required containment or sandbox isolation is unsupported."""


def probe_bwrap_containment() -> tuple[bool, str | None]:
    """Qualify the exact bubblewrap containment operation required by execution.

    Verifies that bubblewrap exists AND can successfully create an unshared
    user, pid, IPC, and network namespace (including loopback setup via netlink).
    Returns (True, None) if supported, or (False, failure_reason) if unsupported.
    """
    bwrap = shutil.which("bwrap")
    if not bwrap:
        return False, "bubblewrap executable (bwrap) not found on PATH"

    true_bin = shutil.which("true") or "/usr/bin/true"
    # Exact containment operation required: unshare user, network, mounts, and loopback setup
    cmd = [
        bwrap,
        "--unshare-all",
        "--unshare-user",
        "--ro-bind", "/", "/",
        "--",
        true_bin,
    ]
    try:
        import subprocess
        res = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
            timeout=3,
        )
        if res.returncode == 0:
            return True, None
        err = res.stderr.strip() or f"exit code {res.returncode}"
        return False, f"bubblewrap containment failed: {err}"
    except Exception as exc:
        return False, f"bubblewrap containment execution error: {exc}"


def probe_bwrap_available() -> bool:
    """Check if bubblewrap containment is fully supported on the current host."""
    ok, _ = probe_bwrap_containment()
    return ok


def probe_lda_index_available() -> bool:
    """Check if LDA SQLite database is initialized and non-empty."""
    lda_db = _ROOT / ".lda" / "index.db"
    return lda_db.is_file() and lda_db.stat().st_size > 0


def require_bwrap(*, allow_skip: bool = False) -> None:
    """Ensure bubblewrap containment is available; fail closed with ContainmentBlocker if absent."""
    ok, reason = probe_bwrap_containment()
    if not ok:
        if allow_skip:
            import unittest
            raise unittest.SkipTest(f"Bubblewrap containment unavailable: {reason}")
        raise ContainmentBlocker(f"BLOCKER: Bubblewrap containment unsupported: {reason}")


def require_lda(*, allow_skip: bool = False) -> None:
    """Ensure LDA index is initialized and non-empty; fail closed if absent (NT-B03)."""
    if not probe_lda_index_available():
        msg = "LDA index (.lda/index.db) not built or empty"
        if allow_skip:
            import unittest
            raise unittest.SkipTest(msg)
        raise RuntimeError(f"BLOCKER: {msg}")




