"""State directory product contract and validation (BETA-03).

The state directory (.vanguard) holds durable event ledgers, blob stores,
checkpoint projections, and operator key material.

Invariants:
- State location is explicit, inspectable, creatable, and never silently changed.
- No silent fallback to in-memory/ephemeral when durable execution is requested.
- Unwritable state directories fail closed before model or tool execution.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Any


class StateDirectoryError(RuntimeError):
    """Base exception for state directory contract violations."""


class StateDirectoryUnwritableError(StateDirectoryError):
    """Raised when the state directory exists or is requested but cannot be written to."""


class StateDirectoryNotInitializedError(StateDirectoryError):
    """Raised when an operation requires an initialized state directory."""


@dataclass(frozen=True, slots=True)
class StateDirectoryReport:
    """Inspectable diagnostic report for a state directory."""

    path: Path
    exists: bool
    is_directory: bool
    writable: bool
    db_path: Path
    db_exists: bool
    blobs_path: Path
    blobs_exists: bool
    durability_mode: str
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": str(self.path),
            "exists": self.exists,
            "isDirectory": self.is_directory,
            "writable": self.writable,
            "dbPath": str(self.db_path),
            "dbExists": self.db_exists,
            "blobsPath": str(self.blobs_path),
            "blobsExists": self.blobs_exists,
            "durabilityMode": self.durability_mode,
            "error": self.error,
        }


def resolve_state_directory(
    workspace: Path | str | None = None,
    state_dir: Path | str | None = None,
) -> Path:
    """Resolve the canonical state directory path.

    Precedence:
    1. Explicit `state_dir` argument (absolute or relative to workspace/CWD).
    2. Environment variable `VANGUARD_STATE_DIR`.
    3. `.vanguard` subfolder under resolved `workspace`.
    4. Fallback to `~/.vanguard/state` if no workspace is provided.
    """
    if state_dir is not None:
        p = Path(state_dir)
        if p.is_absolute():
            return p.resolve()
        base = Path(workspace).resolve() if workspace is not None else Path.cwd()
        return (base / p).resolve()

    env_state = os.environ.get("VANGUARD_STATE_DIR")
    if env_state:
        return Path(env_state).resolve()

    if workspace is not None:
        return (Path(workspace).resolve() / ".vanguard").resolve()

    return (Path.home() / ".vanguard" / "state").resolve()


def inspect_state_directory(
    state_dir: Path | str,
    *,
    durability_mode: str = "sqlite-wal",
) -> StateDirectoryReport:
    """Inspect state directory status without mutating anything on disk."""
    p = Path(state_dir).resolve()
    db_path = p / "events.sqlite3"
    blobs_path = p / "blobs"

    exists = p.exists()
    is_dir = p.is_dir() if exists else False
    writable = False
    error: str | None = None

    if exists:
        if not is_dir:
            error = f"state path {p} exists and is not a directory"
        else:
            writable = os.access(p, os.W_OK | os.X_OK)
            if not writable:
                error = f"state directory {p} is not writable"
    else:
        # Check nearest existing parent for writability
        parent = p
        while not parent.exists() and parent != parent.parent:
            parent = parent.parent
        writable = os.access(parent, os.W_OK | os.X_OK) if parent.exists() else False
        if not writable:
            error = f"cannot create state directory {p}: parent {parent} is not writable"

    return StateDirectoryReport(
        path=p,
        exists=exists,
        is_directory=is_dir,
        writable=writable,
        db_path=db_path,
        db_exists=db_path.exists() if is_dir else False,
        blobs_path=blobs_path,
        blobs_exists=blobs_path.is_dir() if is_dir else False,
        durability_mode=durability_mode,
        error=error,
    )


def ensure_state_directory(
    state_dir: Path | str,
    *,
    durability_mode: str = "sqlite-wal",
) -> Path:
    """Ensure the state directory and required subdirectories exist and are writable.

    Raises StateDirectoryUnwritableError if creation or writability fails.
    """
    p = Path(state_dir).resolve()
    report = inspect_state_directory(p, durability_mode=durability_mode)
    if not report.writable:
        raise StateDirectoryUnwritableError(
            report.error or f"state directory {p} is not writable; durable execution cannot proceed"
        )

    try:
        p.mkdir(parents=True, exist_ok=True)
        (p / "blobs").mkdir(parents=True, exist_ok=True)
    except (PermissionError, OSError) as exc:
        raise StateDirectoryUnwritableError(
            f"failed to initialize state directory at {p}: {exc}"
        ) from exc

    # Final probe write
    probe_file = p / ".write_probe"
    try:
        probe_file.write_bytes(b"")
        probe_file.unlink(missing_ok=True)
    except (PermissionError, OSError) as exc:
        raise StateDirectoryUnwritableError(
            f"state directory {p} is unwritable: {exc}"
        ) from exc

    return p
