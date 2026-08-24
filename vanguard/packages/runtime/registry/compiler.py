"""Plugin-ref resolution over the generated wire values (`H-1`).

**Not a composition authority (`ADR-0088 §1`, A4).** The one production chain is
`Runtime.compose` -> `CanonicalManifest` -> `FrozenComposition`, and `D_H` is
issued there and nowhere else. This module resolves plugin refs and validates
`/2` bytes against the wire schema; the `mhf.frozen-harness/1` digest it
returns is a *wire representation*, never an execution identity, and no
production caller reads it. Retained as bounded ingress/validation through the
compatibility sunset reviewed at M-5.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Mapping

from vanguard.packages.domain.selectors.resource_selector import decide
from vanguard.packages.domain.canonicalisation.digest import digest_of
from vanguard.packages.domain.artifacts.graph import ArtifactGraph
from vanguard.packages.domain.artifacts.manifest import (
    NamedManifest,
    compose_named_manifest,
    parse_named_manifest,
)
from vanguard.packages.domain.wire.types_gen import (
    FrozenHarness,
    HarnessManifest,
    ModelRoute,
    PluginBindings,
    PluginRef,
    Reservation,
)

__all__ = ["ComposeError", "compose", "compose_named"]


class ComposeError(ValueError):
    """Fail-fast composition error. `path` names the unknown ref/alias."""

    def __init__(self, message: str, path: str) -> None:
        super().__init__(f"{path}: {message}")
        self.path = path


_SPI_SLOTS = ("planner", "context", "memory", "evaluation")


def compose(
    manifest: HarnessManifest | Mapping[str, object],
    *,
    known_plugins: Mapping[str, str] | None = None,
    plugin_digests: Mapping[str, str] | None = None,
    plugin_ceilings: Mapping[str, tuple[Mapping[str, object], ...]] | None = None,
    graph: ArtifactGraph | None = None,
) -> FrozenHarness | NamedManifest:
    if isinstance(manifest, Mapping) and manifest.get("api") == "mhf.manifest/2":
        if graph is None:
            raise ComposeError("mhf.manifest/2 requires an artifact graph", "graph")
        return compose_named(manifest, graph)
    parsed = manifest if isinstance(manifest, HarnessManifest) else _parse(manifest)
    if parsed.api != "mhf.harness/1":
        raise ComposeError(f"unsupported api {parsed.api!r}", "api")
    resolved: dict[str, str] = {}
    bindings = parsed.plugins
    for slot in _SPI_SLOTS:
        ref = getattr(bindings, slot)
        if ref is None:
            continue
        resolved[slot] = _resolve(ref, known_plugins or {}, path=f"plugins.{slot}")
    for index, ref in enumerate(bindings.toolkits):
        resolved[f"toolkits[{index}]"] = _resolve(ref, known_plugins or {}, path=f"plugins.toolkits[{index}]")
    for index, route in enumerate(bindings.model_routes):
        _ = route
        resolved[f"model_routes[{index}]"] = f"{route.provider}:{route.model}"

    ceiling_items = _effective_ceiling(parsed.capabilities, resolved, plugin_ceilings or {})
    if parsed.capabilities and not ceiling_items:
        raise ComposeError("declared capability ceiling has no comparable plugin intersection",
                           "capabilities")

    digest_body = {
        "manifest": {
            "api": parsed.api,
            "id": parsed.id,
            "plugins": resolved,
            "declared_bindings": asdict(parsed.plugins),
            "system_prompt": parsed.system_prompt,
            "capabilities": ceiling_items,
            "budget": asdict(parsed.budget) if parsed.budget is not None else None,
            "approval_policy": parsed.approval_policy,
            "undeletable": parsed.undeletable,
        },
        "plugin_digests": {
            plugin_id: digest for plugin_id, digest in (plugin_digests or {}).items()
            if plugin_id in set(resolved.values())
        },
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


def compose_named(raw: Mapping[str, object], graph: ArtifactGraph) -> NamedManifest:
    """Parse, validate, resolve, and freeze one ``mhf.manifest/2`` graph."""
    return compose_named_manifest(parse_named_manifest(raw), graph)


def _parse(raw: Mapping[str, object]) -> HarnessManifest:
    allowed = {
        "api", "id", "plugins", "system_prompt", "capabilities", "budget",
        "approval_policy", "undeletable",
    }
    unknown = set(raw) - allowed
    if unknown:
        raise ComposeError(f"unread fields {sorted(unknown)}", "manifest")
    plugins_raw = raw.get("plugins")
    if not isinstance(plugins_raw, dict):
        raise ComposeError("plugins is required", "plugins")
    route_rows = plugins_raw.get("model_routes") or []
    if not isinstance(route_rows, list):
        raise ComposeError("model_routes must be an array", "plugins.model_routes")
    routes: list[ModelRoute] = []
    for index, item in enumerate(route_rows):
        if not isinstance(item, dict):
            raise ComposeError("model route must be an object", f"plugins.model_routes[{index}]")
        unknown_route = set(item) - {"tier", "provider", "model", "escalate_on"}
        if unknown_route:
            raise ComposeError(f"unread fields {sorted(unknown_route)}", f"plugins.model_routes[{index}]")
        try:
            routes.append(ModelRoute(
                tier=int(item["tier"]), provider=str(item["provider"]), model=str(item["model"]),
                escalate_on=tuple(str(value) for value in item.get("escalate_on", []) or []),
            ))
        except KeyError as exc:
            raise ComposeError(f"missing {exc.args[0]}", f"plugins.model_routes[{index}]") from exc
    bindings = PluginBindings(
        planner=_ref(plugins_raw.get("planner")),
        context=_ref(plugins_raw.get("context")),
        memory=_ref(plugins_raw.get("memory")),
        evaluation=_ref(plugins_raw.get("evaluation")),
        toolkits=tuple(_ref(item) for item in list(plugins_raw.get("toolkits") or []) if item),
        model_routes=tuple(routes),
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
    capabilities_raw = raw.get("capabilities") or []
    if not isinstance(capabilities_raw, list) or any(not isinstance(item, dict) for item in capabilities_raw):
        raise ComposeError("capabilities must be an object array", "capabilities")
    capabilities = tuple(dict(item) for item in capabilities_raw if isinstance(item, dict))
    for index, item in enumerate(capabilities):
        if set(item) != {"verb", "selector"} or not isinstance(item["verb"], str) or not item["verb"]:
            raise ComposeError("capability requires only verb and selector", f"capabilities[{index}]")
        if not isinstance(item["selector"], dict):
            raise ComposeError("selector must be an object", f"capabilities[{index}].selector")
    return HarnessManifest(
        api=str(raw.get("api") or ""),
        id=str(raw.get("id") or ""),
        plugins=bindings,
        system_prompt=str(raw["system_prompt"]) if raw.get("system_prompt") is not None else None,
        capabilities=capabilities,
        budget=budget,
        approval_policy=str(raw["approval_policy"]) if raw.get("approval_policy") is not None else None,
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


def _effective_ceiling(
    harness: tuple[Mapping[str, Any], ...],
    resolved: Mapping[str, str],
    plugin_ceilings: Mapping[str, tuple[Mapping[str, object], ...]],
) -> list[Mapping[str, Any]]:
    """Union of each plugin's intersection with the harness ceiling."""
    if not harness:
        return []
    declared = [item for plugin_id in resolved.values()
                for item in plugin_ceilings.get(plugin_id, ())]
    kept: list[Mapping[str, Any]] = []
    for harness_item in harness:
        verb = harness_item.get("verb")
        harness_selector = harness_item.get("selector")
        for plugin_item in declared:
            if plugin_item.get("verb") != verb:
                continue
            plugin_selector = plugin_item.get("selector")
            plugin_inside = decide(harness_selector, plugin_selector).included
            harness_inside = decide(plugin_selector, harness_selector).included
            if not (plugin_inside or harness_inside):
                continue
            selected = plugin_item if plugin_inside else harness_item
            candidate = {"verb": str(verb), "selector": selected.get("selector")}
            if candidate not in kept:
                kept.append(candidate)
    return kept
