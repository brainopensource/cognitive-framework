"""Load packs/code-default manifests and compile a FrozenHarness."""

from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path
from typing import Any, Mapping

_TOOLS = Path(__file__).resolve().parents[2] / "tools"
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

from simple_yaml import load as load_yaml  # noqa: E402

from layer0.compose.compiler import compose
from vanguard.packages.domain.wire.types_gen import FrozenHarness

__all__ = [
    "PACK_ROOT",
    "compile_pack",
    "discover_plugins",
    "load_declared_entry",
    "load_entry",
    "load_harness",
]

PACK_ROOT = Path(__file__).resolve().parent


def load_harness(path: Path | None = None) -> dict[str, Any]:
    target = path or (PACK_ROOT / "harness.yaml")
    data = load_yaml(target.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("harness.yaml must be a mapping")
    return data


def discover_plugins(pack_root: Path | None = None) -> dict[str, dict[str, Any]]:
    root = pack_root or PACK_ROOT
    catalog = load_yaml((root / "plugin.yaml").read_text(encoding="utf-8"))
    found: dict[str, dict[str, Any]] = {}
    listed = catalog.get("plugins") if isinstance(catalog, dict) else []
    for rel in listed or []:
        path = root / str(rel)
        plugin = load_yaml(path.read_text(encoding="utf-8"))
        if isinstance(plugin, dict) and plugin.get("id"):
            plugin["_path"] = str(path)
            found[str(plugin["id"])] = plugin
    return found


def plugin_digest(plugin: Mapping[str, Any]) -> str:
    raw = f"{plugin.get('id')}:{plugin.get('version')}:{plugin.get('entry')}".encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def compile_pack(pack_root: Path | None = None) -> FrozenHarness:
    root = pack_root or PACK_ROOT
    harness = load_harness(root / "harness.yaml")
    plugins = discover_plugins(root)
    known = {ident: ident for ident in plugins}
    digests = {ident: plugin_digest(plugin) for ident, plugin in plugins.items()}
    ceilings = {}
    for ident, plugin in plugins.items():
        caps = plugin.get("capabilities") or []
        if isinstance(caps, list):
            ceilings[ident] = tuple(item for item in caps if isinstance(item, dict))
    return compose(harness, known_plugins=known, plugin_digests=digests, plugin_ceilings=ceilings)


def load_declared_entry(plugin_id: str, pack_root: Path | None = None) -> Any:
    """Resolve a plugin class from its manifest entry (no hardcoded toolkit imports)."""
    plugins = discover_plugins(pack_root)
    if plugin_id not in plugins:
        raise KeyError(plugin_id)
    return load_entry(str(plugins[plugin_id]["entry"]), pack_root)


def load_entry(entry: str, pack_root: Path | None = None) -> Any:
    root = pack_root or PACK_ROOT
    module_part, _, attr = entry.partition(":")
    if "/" in module_part or module_part.endswith(".py"):
        path = root / module_part
        spec = importlib.util.spec_from_file_location(path.stem, path)
        if spec is None or spec.loader is None:
            raise ImportError(f"cannot load {path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return getattr(module, attr)
    module = importlib.import_module(module_part)
    return getattr(module, attr)
