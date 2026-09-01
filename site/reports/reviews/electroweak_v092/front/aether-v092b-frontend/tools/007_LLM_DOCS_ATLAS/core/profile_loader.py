"""Deterministic profile resolution for LDA.

Precedence (highest first):

1. ``profile: <name>`` key in ``lda.yaml`` / ``lda.yml`` / ``lda.toml``
   (explicit project configuration)
2. ``LDA_PROFILE`` environment variable
3. Built-in generic profile (zero project-specific assumptions)

There is deliberately NO side-channel detection (e.g. "if some generated
artifact exists, assume project X"). A profile is applied only when it is
explicitly named. Profile files are looked up in this order:

- ``<repo>/profiles/lda/<name>.{toml,yaml,yml}``   (repo-local, wins)
- ``<repo>/.lda/profiles/<name>.{toml,yaml,yml}``  (repo-local)
- bundled ``profiles/<name>.{toml,yaml,yml}``      (shipped with LDA)
"""
from __future__ import annotations

import os
import tomllib
from pathlib import Path
from typing import Any, Mapping

from .profile import RepositoryProfile, profile_from_mapping

BUNDLED_PROFILES_DIR = Path(__file__).resolve().parents[1] / "profiles"
_REPO_PROFILE_DIRS = ("profiles/lda", ".lda/profiles")
_PROFILE_EXTENSIONS = (".toml", ".yaml", ".yml")


def _optional_yaml():
    try:
        import yaml  # type: ignore[import-not-found]
    except ImportError:
        return None
    return yaml


def load_profile_file(path: Path) -> Mapping[str, Any]:
    suffix = path.suffix.lower()
    if suffix == ".toml":
        with path.open("rb") as handle:
            return tomllib.load(handle)
    if suffix in (".yaml", ".yml"):
        yaml = _optional_yaml()
        if yaml is None:
            raise RuntimeError(
                f"LDA profile '{path}' is YAML but PyYAML is not installed; "
                "use a TOML profile (stdlib tomllib) for a zero-dependency setup"
            )
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    raise ValueError(f"unsupported LDA profile format: {path}")


def find_profile_file(base: Path, name: str) -> Path | None:
    safe = str(name)
    if not safe or "/" in safe or "\\" in safe or safe in (".", ".."):
        raise ValueError(f"invalid LDA profile name: {name!r}")
    for directory in (base / relative for relative in _REPO_PROFILE_DIRS):
        for ext in _PROFILE_EXTENSIONS:
            candidate = directory / f"{safe}{ext}"
            if candidate.is_file():
                return candidate
    for ext in _PROFILE_EXTENSIONS:
        candidate = BUNDLED_PROFILES_DIR / f"{safe}{ext}"
        if candidate.is_file():
            return candidate
    return None


def resolve_profile(base: Path, config: Mapping[str, Any]) -> RepositoryProfile:
    """Resolve the active profile for a repository (see module precedence doc).

    Raises ValueError when a named profile cannot be found: an explicitly
    configured but missing profile must fail closed, never silently degrade
    to the generic profile.
    """
    name = config.get("profile") or os.environ.get("LDA_PROFILE")
    if not name:
        return RepositoryProfile()
    path = find_profile_file(base, str(name))
    if path is None:
        raise ValueError(
            f"LDA profile '{name}' not found (searched repo 'profiles/lda/' and "
            "'.lda/profiles/ plus bundled profiles/); fix the lda.yaml 'profile:' "
            "key or the LDA_PROFILE environment variable"
        )
    mapping = dict(load_profile_file(path))
    mapping.setdefault("name", str(name))
    return profile_from_mapping(mapping)