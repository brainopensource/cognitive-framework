"""Safe .env credential loader for live test runs.

Owning contract: S6B-SEC-003, REQ-TRUST-001.
Invariants:
- Never source, print, log, serialize, or shell-expand .env contents.
- Strictly parse only OPENROUTER_API_KEY from the repository-root .env.
- Reject: duplicate keys, interpolation, commands, malformed records,
  permissive permissions, symlinks, tracked files, non-root-local paths.
- Inject the value only into the model-adapter process at the last
  responsible moment.
- Missing credentials produce a clear protected-live-test failure,
  never a skip presented as PASS.
"""

from __future__ import annotations

import os
import re
import stat
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from ...ports.event_store import Result

__all__ = [
    "EnvLoadResult",
    "load_api_key",
    "inject_into_environ",
    "ALLOWED_KEY",
]

ALLOWED_KEY = "OPENROUTER_API_KEY"

# Reject lines that look like shell expansion, interpolation, or commands
_INTERPOLATION = re.compile(r"[$`]|\\[nrt]|\$\{|\$\(")
# Valid key=value line: KEY=VALUE or KEY="VALUE" or KEY='VALUE'
_LINE_PATTERN = re.compile(
    r"^([A-Z_][A-Z0-9_]*)=(.*)$"
)
# Maximum .env file size (1 KiB is more than sufficient for a single key)
_MAX_ENV_SIZE = 1024
# Maximum allowed permission bits (owner read/write only)
_MAX_PERMS = 0o600


@dataclass(frozen=True, slots=True)
class EnvLoadResult:
    """Outcome of loading the API key from .env."""

    key_ref: str  # "OPENROUTER_API_KEY" (never the value)
    loaded: bool
    failure_reason: str = ""


def _find_env_path(search_root: Path | str | None = None) -> Path:
    """Locate the repository-root .env file."""
    if search_root is not None:
        root = Path(search_root).resolve()
    else:
        # Walk up from this file to find the repository root
        root = Path(__file__).resolve()
        while root != root.parent:
            if (root / ".git").is_dir():
                break
            root = root.parent
        else:
            raise FileNotFoundError("cannot locate repository root")
    return root / ".env"


def _is_tracked(env_path: Path) -> bool:
    """Check whether the .env file is tracked by git."""
    try:
        result = subprocess.run(
            ["git", "ls-files", "--error-unmatch", str(env_path)],
            cwd=env_path.parent,
            capture_output=True,
            timeout=5,
            check=False,
        )
        return result.returncode == 0
    except (OSError, subprocess.SubprocessError):
        # If git is unavailable, err on the side of caution
        return True


def load_api_key(
    search_root: Path | str | None = None,
) -> Result[str]:
    """Load OPENROUTER_API_KEY from the repository-root .env.

    Returns Result.success(key_value) on success, or Result.fail on any
    security or format violation. The failure message never contains the
    key value — only structural diagnostics.
    """
    try:
        env_path = _find_env_path(search_root)
    except FileNotFoundError as exc:
        return Result.fail(
            kind="instrument_error",
            message=f"protected-live-test: {exc}",
        )

    # --- Path safety checks ---

    if not env_path.exists():
        return Result.fail(
            kind="instrument_error",
            message="protected-live-test: .env file not found at repository root",
        )

    # Reject symlinks
    if env_path.is_symlink():
        return Result.fail(
            kind="instrument_error",
            message="protected-live-test: .env is a symlink (rejected for safety)",
        )

    # Check permissions (owner read/write only)
    file_stat = env_path.stat()
    mode = stat.S_IMODE(file_stat.st_mode)
    if mode & ~_MAX_PERMS:
        return Result.fail(
            kind="instrument_error",
            message=(
                f"protected-live-test: .env has permissive permissions "
                f"({oct(mode)}); expected {oct(_MAX_PERMS)} or stricter"
            ),
        )

    # Reject tracked files
    if _is_tracked(env_path):
        return Result.fail(
            kind="instrument_error",
            message="protected-live-test: .env is tracked by git (rejected)",
        )

    # --- Content safety checks ---

    raw = env_path.read_bytes()
    if len(raw) > _MAX_ENV_SIZE:
        return Result.fail(
            kind="instrument_error",
            message=f"protected-live-test: .env exceeds {_MAX_ENV_SIZE} bytes",
        )

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return Result.fail(
            kind="instrument_error",
            message="protected-live-test: .env contains non-UTF-8 content",
        )

    found_key: Optional[str] = None
    found_count = 0

    for line_num, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        # Skip empty lines and comments
        if not stripped or stripped.startswith("#"):
            continue

        # Check for shell interpolation/expansion
        if _INTERPOLATION.search(stripped):
            return Result.fail(
                kind="instrument_error",
                message=(
                    f"protected-live-test: .env line {line_num} contains "
                    f"interpolation or command syntax (rejected)"
                ),
            )

        match = _LINE_PATTERN.match(stripped)
        if not match:
            return Result.fail(
                kind="instrument_error",
                message=(
                    f"protected-live-test: .env line {line_num} is malformed "
                    f"(expected KEY=VALUE format)"
                ),
            )

        key_name = match.group(1)
        value = match.group(2)

        # Strip surrounding quotes if present
        if (
            len(value) >= 2
            and (
                (value.startswith('"') and value.endswith('"'))
                or (value.startswith("'") and value.endswith("'"))
            )
        ):
            value = value[1:-1]

        if key_name == ALLOWED_KEY:
            found_count += 1
            if found_count > 1:
                return Result.fail(
                    kind="instrument_error",
                    message=(
                        f"protected-live-test: .env contains duplicate "
                        f"{ALLOWED_KEY} entries (rejected)"
                    ),
                )
            if not value:
                return Result.fail(
                    kind="instrument_error",
                    message=(
                        f"protected-live-test: {ALLOWED_KEY} is empty "
                        f"in .env"
                    ),
                )
            found_key = value

    if found_key is None:
        return Result.fail(
            kind="instrument_error",
            message=(
                f"protected-live-test: {ALLOWED_KEY} not found in .env"
            ),
        )

    return Result.success(found_key)


def inject_into_environ(
    key_value: str,
    *,
    key_name: str = ALLOWED_KEY,
) -> dict[str, str]:
    """Create a minimal environment dict containing only the API key.

    This is used to construct the model-adapter process environment.
    The returned dict contains ONLY the key; no other host environment
    variables leak to the adapter.

    Returns a new dict; does NOT modify os.environ.
    """
    return {key_name: key_value}
