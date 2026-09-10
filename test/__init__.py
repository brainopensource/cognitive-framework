"""Runner-independent test isolation and disposable state configuration."""
from __future__ import annotations

import atexit
import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Mapping, MutableMapping

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

_TRACKED_LAM_DB = _ROOT / "tools" / "002_LLM_API_MOCK" / "lam.sqlite"
_CLEANUP_DIRS: list[Path] = []


def _cleanup_registered_dirs() -> None:
    for d in _CLEANUP_DIRS:
        if d.is_dir():
            shutil.rmtree(d, ignore_errors=True)


atexit.register(_cleanup_registered_dirs)


def establish_test_environment(
    workspace_root: str | Path | None = None,
    target_env: MutableMapping[str, str] | None = None,
    *,
    scrub_credentials: bool = False,
    deny_network: bool = False,
) -> dict[str, str]:
    """Consolidate runner-independent safe temporary and disposable state.

    Redirects LAM, BAAC, Python bytecode cache, npm cache, XDG directories,
    temporary directories, and runtime state to disposable paths.
    """
    env = os.environ if target_env is None else target_env

    # 1. Determine disposable workspace root
    if workspace_root is not None:
        ws = Path(workspace_root).resolve()
    else:
        existing_ws = env.get("AETHER_WORKSPACE_ROOT")
        if existing_ws and Path(existing_ws).resolve() != _ROOT.resolve():
            ws = Path(existing_ws).resolve()
        else:
            ws_tmp = tempfile.mkdtemp(prefix="aether_ws_")
            ws = Path(ws_tmp).resolve()
            _CLEANUP_DIRS.append(ws)

    ws.mkdir(parents=True, exist_ok=True)
    env["AETHER_WORKSPACE_ROOT"] = str(ws)

    # 2. Redirect Temporary directories
    tmp_dir = ws / "tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    env["TMPDIR"] = str(tmp_dir)
    env["TMP"] = str(tmp_dir)
    env["TEMP"] = str(tmp_dir)

    # 3. Redirect XDG directories
    cache_dir = ws / "cache"
    state_dir = ws / "state"
    config_dir = ws / "config"
    data_dir = ws / "data"
    runtime_dir = ws / "run"
    for d in (cache_dir, state_dir, config_dir, data_dir, runtime_dir):
        d.mkdir(parents=True, exist_ok=True)

    env["XDG_CACHE_HOME"] = str(cache_dir)
    env["XDG_STATE_HOME"] = str(state_dir)
    env["XDG_CONFIG_HOME"] = str(config_dir)
    env["XDG_DATA_HOME"] = str(data_dir)
    env["XDG_RUNTIME_DIR"] = str(runtime_dir)

    # 4. Redirect Python bytecode cache and npm cache
    pycache_dir = cache_dir / "python"
    pycache_dir.mkdir(parents=True, exist_ok=True)
    env["PYTHONPYCACHEPREFIX"] = str(pycache_dir)

    npm_cache_dir = cache_dir / "npm"
    npm_cache_dir.mkdir(parents=True, exist_ok=True)
    env["npm_config_cache"] = str(npm_cache_dir)

    # 5. Redirect LAM database to disposable copy
    current_lam = env.get("LAM_DB_PATH")
    if not current_lam or Path(current_lam).resolve() == _TRACKED_LAM_DB.resolve() or not str(Path(current_lam).resolve()).startswith(str(ws)):
        lam_scratch_dir = tempfile.mkdtemp(prefix="lam-db-", dir=str(tmp_dir))
        lam_scratch = Path(lam_scratch_dir) / "lam.sqlite"
        if _TRACKED_LAM_DB.is_file():
            shutil.copy2(_TRACKED_LAM_DB, lam_scratch)
        env["LAM_DB_PATH"] = str(lam_scratch)

    # 6. Redirect BAAC runs
    baac_runs = ws / "baac_runs"
    baac_runs.mkdir(parents=True, exist_ok=True)
    env["BAAC_RUNS_DIR"] = str(baac_runs)

    # 7. Redirect Vanguard runtime state
    vanguard_state = ws / "vanguard_state"
    vanguard_state.mkdir(parents=True, exist_ok=True)
    env["VANGUARD_STATE_DIR"] = str(vanguard_state)

    # 8. Scrub credentials if requested
    if scrub_credentials:
        from tools.linters.check_test_hygiene import PROVIDER_KEYS, _GENERIC_KEY_PATTERN
        for k in list(env.keys()):
            if k in PROVIDER_KEYS or (_GENERIC_KEY_PATTERN.match(k) and not k.startswith("VANGUARD_TEST_")):
                del env[k]

    # 9. Deny network if requested
    if deny_network:
        env["http_proxy"] = "http://127.0.0.1:0"
        env["https_proxy"] = "http://127.0.0.1:0"
        env["all_proxy"] = "http://127.0.0.1:0"
        env["HTTP_PROXY"] = "http://127.0.0.1:0"
        env["HTTPS_PROXY"] = "http://127.0.0.1:0"
        env["ALL_PROXY"] = "http://127.0.0.1:0"
        env["NO_PROXY"] = ""

    return dict(env)


def build_hermetic_test_env(
    workspace_root: str | Path | None = None,
    base_env: Mapping[str, str] | None = None,
) -> dict[str, str]:
    """Build an isolated environment with credentials scrubbed and network denied."""
    base = dict(os.environ if base_env is None else base_env)
    return establish_test_environment(
        workspace_root=workspace_root,
        target_env=base,
        scrub_credentials=True,
        deny_network=True,
    )


# Establish safe environment before test module imports
establish_test_environment()

from test.conftest import (
    probe_bwrap_available,
    probe_lda_index_available,
    require_bwrap,
    require_lda,
)



