"""BaaC Hermetic Cache and Scratch Workspace Management.

Guarantees:
1. Deterministic state wipes between benchmark runs.
2. Complete purge of ephemeral scratch directories.
3. Clean elimination of bytecode, WAL, and intermediate test artifacts.
"""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import tempfile
from typing import Dict, List, Tuple


def clean_scratch_directories(prefix: str = "baac-scratch-") -> int:
    """Safely find and wipe all temporary scratch workspaces."""
    tmp = Path(tempfile.gettempdir())
    cleaned = 0
    for p in tmp.glob(f"{prefix}*"):
        if p.is_dir():
            shutil.rmtree(p, ignore_errors=True)
            cleaned += 1

    return cleaned


def purge_bytecode_caches(target_dir: Path) -> int:
    """Recursively delete all __pycache__ folders and .pyc files."""
    cleaned = 0
    if not target_dir.exists():
        return cleaned

    for root, dirs, files in os.walk(target_dir, topdown=False):
        for d in dirs:
            if d == "__pycache__":
                shutil.rmtree(Path(root, d), ignore_errors=True)
                cleaned += 1
        for f in files:
            if f.endswith(".pyc") or f.endswith(".pyo"):
                try:
                    Path(root, f).unlink(missing_ok=True)
                    cleaned += 1
                except Exception:
                    pass
    return cleaned


def purge_ephemeral_state(target_dir: Path) -> None:
    """Purge WAL, journal, and ephemeral test files."""
    if not target_dir.exists():
        return
    for ext in ("*.sqlite-wal", "*.sqlite-shm", "*.sqlite-journal", "*.log", "*.coverage"):
        for p in target_dir.rglob(ext):
            try:
                p.unlink(missing_ok=True)
            except Exception:
                pass


def reset_environment(target_dir: Path | None = None) -> Dict[str, int]:
    """Execute complete reset and cache purge."""
    scratch_count = clean_scratch_directories()
    bytecode_count = 0
    if target_dir and target_dir.exists():
        bytecode_count = purge_bytecode_caches(target_dir)
        purge_ephemeral_state(target_dir)
    return {
        "scratch_workspaces_cleaned": scratch_count,
        "bytecode_artifacts_purged": bytecode_count,
    }
