"""Runtime workspace root and path validation contracts."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Mapping

ENV_WORKSPACE_ROOT = "AETHER_WORKSPACE_ROOT"
DEFAULT_WORKSPACE_ROOT = str(Path.home() / ".vanguard" / "workspace")
_CONFIG_FILENAME = ".vanguard/workspace.toml"


def _discover_workspace_root() -> Path | None:
    """Walk upward from CWD (and the script's directory) looking for
    `.vanguard/workspace.toml` and return the ``root`` value declared in it.
    Returns None if no config file is found.
    """
    search_dirs: list[Path] = []
    search_dirs.append(Path.cwd())
    if sys.argv and sys.argv[0]:
        search_dirs.append(Path(sys.argv[0]).resolve().parent)

    seen: set[Path] = set()
    for start in search_dirs:
        candidate = start.resolve()
        while True:
            if candidate in seen:
                break
            seen.add(candidate)
            cfg = candidate / _CONFIG_FILENAME
            if cfg.is_file():
                raw = cfg.read_text(encoding="utf-8")
                # Minimal TOML parse – avoids third-party dependency.
                for line in raw.splitlines():
                    line = line.strip()
                    if line.startswith("root"):
                        _, _, value = line.partition("=")
                        value = value.strip().strip('"').strip("'")
                        if value:
                            return Path(value)
            parent = candidate.parent
            if parent == candidate:
                break
            candidate = parent
    return None


def get_workspace_root() -> Path:
    """Return the absolute Path to the workspace root.

    Resolution order (first match wins):
    1. ``AETHER_WORKSPACE_ROOT`` environment variable.
    2. ``root`` key inside the nearest ``.vanguard/workspace.toml`` found
       by walking upward from the current working directory.

    Raises RuntimeError if neither source is available.
    """
    raw_root = os.environ.get(ENV_WORKSPACE_ROOT)
    if not raw_root:
        discovered = _discover_workspace_root()
        if discovered is not None:
            raw_root = str(discovered)
    if not raw_root:
        raise RuntimeError(
            f"{ENV_WORKSPACE_ROOT} is not set and no .vanguard/workspace.toml "
            f"was found in the directory tree; cannot determine workspace root"
        )
    root = Path(raw_root).resolve()
    if not root.is_dir():
        try:
            root.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise RuntimeError(
                f"failed to create workspace directory at {root}: {exc}"
            ) from exc
    return root


def get_workspace_path(category: str, *subpaths: str) -> Path:
    """Return a category subdirectory within AETHER_WORKSPACE_ROOT.

    Categories include: 'tmp', 'benchmarks', 'evaluators', 'sandboxes', 'state', 'cache', 'logs'.
    """
    root = get_workspace_root()
    target = root / category
    for part in subpaths:
        target = target / part
    resolved = target.resolve()
    if not resolved.is_relative_to(root):
        raise RuntimeError(f"runtime path escapes {ENV_WORKSPACE_ROOT}: {resolved}")
    try:
        resolved.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise RuntimeError(
            f"failed to create subdirectory {resolved} in {ENV_WORKSPACE_ROOT}: {exc}"
        ) from exc
    return resolved


def validate_workspace_path(
    configured_path: Path | str, category: str | None = None
) -> Path:
    """Validate that configured_path resolves strictly inside AETHER_WORKSPACE_ROOT."""
    root = get_workspace_root()
    resolved = Path(configured_path).resolve()
    if not resolved.is_relative_to(root):
        raise RuntimeError(f"runtime path escapes {ENV_WORKSPACE_ROOT}: {resolved}")
    if category is not None:
        cat_root = (root / category).resolve()
        if not resolved.is_relative_to(cat_root):
            raise RuntimeError(
                f"runtime path {resolved} is not inside category {category} ({cat_root})"
            )
    return resolved


def controlled_environment(
    base: Mapping[str, str] | None = None,
    extra: Mapping[str, str] | None = None,
) -> dict[str, str]:
    """Produce an environment dictionary overriding all standard temporary and cache directories."""
    root = get_workspace_root()
    tmp = get_workspace_path("tmp")
    cache = get_workspace_path("cache")
    state = get_workspace_path("state")

    env = dict(os.environ if base is None else base)
    env[ENV_WORKSPACE_ROOT] = str(root)
    env["TMPDIR"] = str(tmp)
    env["TMP"] = str(tmp)
    env["TEMP"] = str(tmp)
    env["XDG_CACHE_HOME"] = str(cache)
    env["XDG_STATE_HOME"] = str(state)
    env["PYTHONPYCACHEPREFIX"] = str(cache / "python")
    env["npm_config_cache"] = str(cache / "npm")

    if extra:
        env.update(extra)
    return env
