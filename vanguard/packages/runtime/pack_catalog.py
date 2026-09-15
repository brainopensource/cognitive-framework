"""Single resolution point for the installed product pack and preset catalog.

T-102. The CLI, the stdio entrypoint, :class:`ApplicationService` and the
Coding Max facade previously each carried their own copy of three things:
a ``spec_from_file_location`` loader for ``packs/code-default/load.py``, a
``{"fast", "balanced", "max"}`` allowlist, and a filesystem walk to the
installed manifests. Three copies are three chances to disagree about which
budget a preset declares. This module owns each of them exactly once, and
resolves installed resources through the supported package API
(:func:`importlib.util.find_spec` for the pack, :mod:`importlib.resources`
for the agency manifests) rather than by counting ``parents[N]``.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

__all__ = [
    "DEFAULT_TURN_CEILING",
    "InvalidPreset",
    "catalog",
    "manifest_path",
    "pack_root",
    "preset_manifest_path",
    "preset_names",
    "resolve_preset",
    "turn_ceiling",
]

# The generic (non-preset) product compositions -- ``explain`` and an explicit
# ``--harness`` override -- have no catalog row to read a bound from. One
# named constant, not a bare ``40`` repeated at every call site.
DEFAULT_TURN_CEILING = 40

_PACK_MODULE: Any = None
_MANIFEST_ANCHOR = "vanguard.packages.agency"


class InvalidPreset(ValueError):
    """The caller requested a preset outside the frozen product catalog."""


def pack_root(pack: str = "code-default") -> Path:
    """Locate an installed pack through the ``packs`` package's own search path."""
    spec = importlib.util.find_spec("packs")
    locations = list(getattr(spec, "submodule_search_locations", ()) or ()) if spec else []
    for location in locations:
        candidate = Path(str(location)) / pack
        if candidate.is_dir():
            return candidate
    raise ImportError(f"pack {pack!r} is not installed (searched {locations})")


def catalog() -> Any:
    """The one ``packs/code-default/load.py`` module object in the process.

    ``code-default`` is not a valid module identifier, so the pack cannot be
    imported by dotted name; the file loader below is the single permitted
    exception and it is memoised on :data:`sys.modules` like any import.
    """
    global _PACK_MODULE
    if _PACK_MODULE is None:
        existing = sys.modules.get("code_default_load")
        if existing is not None:
            _PACK_MODULE = existing
            return _PACK_MODULE
        path = pack_root() / "load.py"
        spec = importlib.util.spec_from_file_location("code_default_load", path)
        if spec is None or spec.loader is None:
            raise ImportError(f"cannot load preset catalog from {path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        _PACK_MODULE = module
    return _PACK_MODULE


def preset_names() -> tuple[str, ...]:
    """The frozen catalog's preset names -- the only allowlist."""
    return tuple(catalog().PRESET_NAMES)


def resolve_preset(name: str | None) -> Any:
    """Validate a preset name and return its immutable declared policy."""
    chosen = (name or "balanced").strip().lower()
    if chosen not in preset_names():
        raise InvalidPreset(f"unknown Coding Max preset {chosen!r}")
    return catalog().resolve_preset_policy(chosen)


def turn_ceiling(preset: str | None, explicit: Any = None) -> int:
    """Loop bound: omitted uses the declared catalog, explicit may only attenuate."""
    policy = resolve_preset(preset)
    parsed = None if explicit in (None, "") else int(explicit)
    return int(catalog().effective_limit(policy.turns, parsed))


def manifest_path(name: str) -> Path:
    """Resolve an installed agency manifest through the package resource API."""
    from importlib.resources import files

    return Path(str(files(_MANIFEST_ANCHOR).joinpath("manifests", name, "manifest.json")))


def preset_manifest_path(preset: str | None) -> Path:
    """The manifest a validated preset selects."""
    return manifest_path(f"vg-code-{resolve_preset(preset).name}")
