"""Compile the formal SAT pack through the ordinary pack composition seam."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from typing import Any, Mapping

_ROOT = Path(__file__).resolve().parents[2]
for _path in (_ROOT / "tools" / "common", _ROOT / "tools"):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

from simple_yaml import load as load_yaml  # noqa: E402

from vanguard.packages.runtime.registry.compiler import compose  # noqa: E402

PACK_ROOT = Path(__file__).resolve().parent


def _read(path: Path) -> dict[str, Any]:
    value = load_yaml(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.name} must contain a mapping")
    return value


def discover_plugins() -> dict[str, dict[str, Any]]:
    catalog = _read(PACK_ROOT / "plugin.yaml")
    found: dict[str, dict[str, Any]] = {}
    for relative in catalog.get("plugins", ()):
        plugin = _read(PACK_ROOT / str(relative))
        found[str(plugin["id"])] = plugin
    return found


def _digest(plugin: Mapping[str, Any]) -> str:
    body = f"{plugin.get('id')}:{plugin.get('version')}:{plugin.get('entry')}".encode()
    return "sha256:" + hashlib.sha256(body).hexdigest()


def compile_pack():
    harness = _read(PACK_ROOT / "harness.yaml")
    plugins = discover_plugins()
    return compose(
        harness,
        known_plugins={name: name for name in plugins},
        plugin_digests={name: _digest(plugin) for name, plugin in plugins.items()},
        plugin_ceilings={
            name: tuple(plugin.get("capabilities") or ())
            for name, plugin in plugins.items()
        },
    )
