"""HarnessManifest → FrozenHarness compiler. Unknown refs fail at compose (H-1)."""

from __future__ import annotations

from typing import Mapping

from layer0.registry.grants import intersect_ceilings
from vanguard.packages.domain.canonicalisation.digest import digest_of
from vanguard.packages.domain.wire.types_gen import (
    FrozenHarness,
    HarnessManifest,
    PluginBindings,
    PluginRef,
    Reservation,
)

__all__ = ["ComposeError", "compose"]


class ComposeError(ValueError):
    """Fail-fast composition error. `path` names the unknown ref/alias."""

    def __init__(self, message: str, path: str) -> None:
        super().__init__(f"{path}: {message}")
        self.path = path


_SPI_SLOTS = ("planner", "context", "memory", "evaluation")


def compose(
    manifest: HarnessManifest | Mapping[str, object],
    *,
    known_plugins: Mapping[str, str],
    plugin_digests: Mapping[str, str] | None = None,
    plugin_ceilings: Mapping[str, tuple[Mapping[str, object], ...]] | None = None,
) -> FrozenHarness:
    parsed = manifest if isinstance(manifest, HarnessManifest) else _parse(manifest)
    if parsed.api != "mhf.harness/1":
        raise ComposeError(f"unsupported api {parsed.api!r}", "api")
    resolved: dict[str, str] = {}
    bindings = parsed.plugins
    for slot in _SPI_SLOTS:
        ref = getattr(bindings, slot)
        if ref is None:
            continue
        resolved[slot] = _resolve(ref, known_plugins, path=f"plugins.{slot}")
    for index, ref in enumerate(bindings.toolkits):
        resolved[f"toolkits[{index}]"] = _resolve(ref, known_plugins, path=f"plugins.toolkits[{index}]")
    for index, route in enumerate(bindings.model_routes):
        _ = route
        resolved[f"model_routes[{index}]"] = f"{route.provider}:{route.model}"

    ceiling_items: list[Mapping[str, object]] = list(parsed.capabilities)
    if plugin_ceilings:
        for slot, plugin_id in list(resolved.items()):
            if plugin_id in plugin_ceilings:
                intersect_ceilings(parsed.capabilities, plugin_ceilings[plugin_id])
                _ = slot

    digest_body = {
        "manifest": {
            "api": parsed.api,
            "id": parsed.id,
            "plugins": resolved,
            "undeletable": parsed.undeletable,
        },
        "plugin_digests": dict(plugin_digests or {}),
    }
    digest = digest_of(digest_body)
    budget = parsed.budget or Reservation(0, 0, 0, 0, 0, 0)
    return FrozenHarness(
        api="mhf.frozen-harness/1",
        id=parsed.id,
        digest=digest,
        resolved_refs=resolved,
        budget=budget,
        capability_ceiling=tuple(ceiling_items),
        undeletable=parsed.undeletable,
    )


def _resolve(ref: PluginRef, known: Mapping[str, str], *, path: str) -> str:
    ident = ref.ref.split("@", 1)[0]
    if ident not in known and ref.ref not in known:
        raise ComposeError(f"unknown plugin ref {ref.ref!r}", path)
    return known.get(ident) or known[ref.ref]


def _parse(raw: Mapping[str, object]) -> HarnessManifest:
    plugins_raw = raw.get("plugins")
    if not isinstance(plugins_raw, dict):
        raise ComposeError("plugins is required", "plugins")
    bindings = PluginBindings(
        planner=_ref(plugins_raw.get("planner")),
        context=_ref(plugins_raw.get("context")),
        memory=_ref(plugins_raw.get("memory")),
        evaluation=_ref(plugins_raw.get("evaluation")),
        toolkits=tuple(_ref(item) for item in list(plugins_raw.get("toolkits") or []) if item),
    )
    budget_raw = raw.get("budget")
    budget = None
    if isinstance(budget_raw, dict):
        budget = Reservation(
            usd_micros=int(budget_raw.get("usd_micros") or 0),
            millis=int(budget_raw.get("millis") or 0),
            tokens=int(budget_raw.get("tokens") or 0),
            bytes=int(budget_raw.get("bytes") or 0),
            turns=int(budget_raw.get("turns") or 0),
            depth=int(budget_raw.get("depth") or 0),
        )
    return HarnessManifest(
        api=str(raw.get("api") or ""),
        id=str(raw.get("id") or ""),
        plugins=bindings,
        budget=budget,
        undeletable=bool(raw.get("undeletable") or False),
    )


def _ref(value: object) -> PluginRef | None:
    if value is None:
        return None
    if isinstance(value, PluginRef):
        return value
    if isinstance(value, dict) and "ref" in value:
        config = value.get("config")
        return PluginRef(ref=str(value["ref"]), config=dict(config) if isinstance(config, dict) else {})
    raise ComposeError("plugin ref must be {ref, config?}", "plugins")
