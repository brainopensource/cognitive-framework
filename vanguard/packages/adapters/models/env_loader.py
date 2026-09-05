"""Protected process-edge loader for operator secrets (`SEC-01`, S6B-SEC-003).

The adapter never logs secret values. Callers at the process edge load a
single allowlisted key after the file has been checked: regular file, not a
symlink, mode ``0600`` or stricter, untracked, no interpolation. Trust-spine
code must not import this module.
"""

from __future__ import annotations

import os
import stat
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence
import re

from ...ports.event_store import Result

__all__ = [
    "ALLOWED_KEY",
    "ALLOWED_KEYS",
    "EnvLoadResult",
    "ProtectedEnvError",
    "inject_into_environ",
    "ensure_openrouter_key_loaded",
    "load_api_key",
    "load_local_inference_env",
    "load_protected_env",
    "LOCAL_INFERENCE_KEYS",
]

ALLOWED_KEY = "OPENROUTER_API_KEY"
ALLOWED_KEYS = frozenset({ALLOWED_KEY})
LOCAL_INFERENCE_KEYS = frozenset({
    "VANGUARD_LLAMA_ENDPOINT",
    "VANGUARD_LLAMA_MODEL",
})
_MAX_PERMS = 0o600
_MAX_BYTES = 1024
_KEY_NAME = re.compile(r"^[A-Z][A-Z0-9_]*$")
_INTERPOLATION = ("$", "`")


class ProtectedEnvError(ValueError):
    """The secret file is missing, too permissive, or malformed."""


@dataclass(frozen=True, slots=True)
class EnvLoadResult:
    """Name of the loaded key. Never carries the secret value."""

    key_ref: str
    loaded: bool


def _is_tracked(path: Path) -> bool:
    completed = subprocess.run(
        ["git", "ls-files", "--error-unmatch", str(path.name)],
        cwd=path.parent,
        capture_output=True,
        check=False,
    )
    return completed.returncode == 0


def inject_into_environ(secret: str) -> dict[str, str]:
    """Return a minimal environ fragment. Does not mutate ``os.environ``."""
    return {ALLOWED_KEY: secret}


def ensure_openrouter_key_loaded(search_roots: Sequence[str | os.PathLike[str]]) -> str:
    """Product-edge dotenv: put ``OPENROUTER_API_KEY`` on ``os.environ``.

    Returns ``"environ"`` if already set, ``"dotenv"`` if loaded from a
    protected ``.env``, or ``"missing"``. Never logs or returns the secret.
    Runtime selection must not call this; tests stay hermetic unless a
    process entrypoint (standalone daemon) opts in.
    """
    existing = os.environ.get(ALLOWED_KEY, "").strip()
    if existing:
        return "environ"
    seen: set[Path] = set()
    for root in search_roots:
        resolved = Path(root).resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        result = load_api_key(resolved)
        if result.ok and result.value:
            os.environ[ALLOWED_KEY] = result.value
            return "dotenv"
    return "missing"


def load_local_inference_env(
    environ: Mapping[str, str] | None = None,
) -> dict[str, str]:
    """Return only the supported native llama.cpp process-edge settings."""
    source = os.environ if environ is None else environ
    return {
        key: value.strip()
        for key in LOCAL_INFERENCE_KEYS
        if isinstance((value := source.get(key)), str) and value.strip()
    }


def load_api_key(root: str | os.PathLike[str]) -> Result[str]:
    """Load ``OPENROUTER_API_KEY`` from ``<root>/.env``. Fail closed."""
    env_path = Path(root) / ".env"
    if not env_path.exists():
        return Result.fail("not_found", "secret file not found")
    if env_path.is_symlink() or not env_path.is_file():
        return Result.fail("invalid_request", "secret path must not be a symlink")
    try:
        info = env_path.stat()
    except OSError:
        return Result.fail("not_found", "secret file not found")
    if stat.S_IMODE(info.st_mode) & 0o177:
        return Result.fail("denied", "secret file has permissive permissions")
    if info.st_size > _MAX_BYTES:
        return Result.fail("invalid_request", "secret file exceeds size limit")
    if _is_tracked(env_path):
        return Result.fail("denied", "tracked .env is forbidden")

    try:
        text = env_path.read_text(encoding="utf-8")
    except OSError:
        return Result.fail("not_found", "secret file not found")

    found: str | None = None
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            return Result.fail("invalid_request", "secret file contains a malformed line")
        key, value = line.split("=", 1)
        key = key.strip()
        if not _KEY_NAME.fullmatch(key):
            return Result.fail("invalid_request", "secret file contains a malformed line")
        value = value.strip().strip('"').strip("'")
        if key != ALLOWED_KEY:
            continue
        if found is not None:
            return Result.fail("invalid_request", "duplicate key is forbidden")
        if not value:
            return Result.fail("invalid_request", "empty value is forbidden")
        if any(token in value for token in _INTERPOLATION):
            return Result.fail("invalid_request", "interpolation is forbidden")
        if len(value) > _MAX_BYTES:
            return Result.fail("invalid_request", "secret value exceeds size limit")
        found = value
    if found is None:
        return Result.fail("not_found", "allowlisted key not found")
    return Result.success(found)


def load_protected_env(path: str | os.PathLike[str]) -> dict[str, str]:
    """Compatibility wrapper around ``load_api_key`` for a direct file path."""
    result = load_api_key(Path(path).parent)
    if not result.ok:
        raise ProtectedEnvError(result.error.message if result.error else "load failed")
    return {ALLOWED_KEY: result.value or ""}
