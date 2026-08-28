"""Test-suite fixtures that keep runs from mutating tracked files.

`tools/002_LLM_API_MOCK/lam.sqlite` is a tracked corpus, and the harness ladder
opens it for writing at import time. A test run that edits a tracked file makes
`git status` report work nobody did, and that is how a batch of build artifacts
was staged by accident once already.

The redirect happens in `pytest_configure` rather than in a fixture because the
ladder builds its store during module import, which is collection time -- before
any fixture runs.
"""

from __future__ import annotations

import atexit
import os
import shutil
import tempfile
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_TRACKED_LAM_DB = _ROOT / "tools" / "002_LLM_API_MOCK" / "lam.sqlite"


def pytest_configure(config) -> None:
    if os.environ.get("LAM_DB_PATH"):
        return
    directory = tempfile.mkdtemp(prefix="lam-db-")
    scratch = Path(directory) / "lam.sqlite"
    if _TRACKED_LAM_DB.is_file():
        shutil.copy2(_TRACKED_LAM_DB, scratch)
    os.environ["LAM_DB_PATH"] = str(scratch)
    atexit.register(shutil.rmtree, directory, True)
