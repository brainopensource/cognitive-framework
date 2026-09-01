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
    default_ws = str(Path(tempfile.gettempdir()) / "aether_workspace")
    ws_root = os.environ.get("AETHER_WORKSPACE_ROOT", default_ws)
    os.environ["AETHER_WORKSPACE_ROOT"] = ws_root
    tmp_dir = Path(ws_root) / "tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("TMPDIR", str(tmp_dir))
    os.environ.setdefault("TMP", str(tmp_dir))
    os.environ.setdefault("TEMP", str(tmp_dir))
    os.environ.setdefault("XDG_CACHE_HOME", str(Path(ws_root) / "cache"))
    os.environ.setdefault("XDG_STATE_HOME", str(Path(ws_root) / "state"))

    if os.environ.get("LAM_DB_PATH"):
        return
    directory = tempfile.mkdtemp(prefix="lam-db-", dir=tmp_dir)
    scratch = Path(directory) / "lam.sqlite"
    if _TRACKED_LAM_DB.is_file():
        shutil.copy2(_TRACKED_LAM_DB, scratch)
    os.environ["LAM_DB_PATH"] = str(scratch)
    atexit.register(shutil.rmtree, directory, True)
