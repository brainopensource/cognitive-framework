"""Harness manifest parsing and freeze-at-composition semantics."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping
from ..canonicalisation.digest import digest_of
from ..canonicalisation.jcs import parse_json_text
from ..selectors.resource_selector import canonicalise_selector, ceiling_allows, parse_selector
from .graph import ArtifactGraph


class ManifestError(ValueError):
    pass


_V2_COMPONENT_FIELDS = frozenset({
    "name", "kind", "implementation", "config", "isolation", "ceiling",
    "interfaces", "entrypoints", "authority",
})
_V2_TOP_FIELDS = frozenset({"api", "id", "components", "bindings", "entrypoints", "profiles", "ceiling",
                            "capabilities", "model_routes", "budget", "system_prompt", "approval_policy",
                            "guardrails", "undeletable"})
_SPI_KINDS = frozenset({"IPlanner", "IMemoryEngine", "IToolkit", "IContextManager", "IEvaluationGate"})
_ISOLATION = frozenset({"in_process", "subprocess", "container", "wasm"})


@dataclass(frozen=True, slots=True)
class NamedComponent:
    name: str
    kind: str
    implementation: str
    config: Any
    isolation: str
    ceiling: tuple[str, ...]
    interfaces: tuple[str, ...]
    entrypoints: tuple[str, ...]
    authority: bool = False


@dataclass(frozen=True, slots=True)
class TypedBinding:
    source: str
    target: str
    interface: str
    lazy: bool = False


@dataclass(frozen=True, slots=True)
class NamedManifest:
    manifest_id: str
    components: tuple[NamedComponent, ...]
    bindings: tuple[TypedBinding, ...]
    entrypoints: tuple[str, ...]
    profiles: Mapping[str, Any]
    ceiling: tuple[str, ...]
    api: str = "mhf.manifest/2"
    metadata: Mapping[str, Any] = field(default_factory=dict)
    digest: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "digest", digest_of({
            "api": self.api, "id": self.manifest_id,
            "components": [asdict(c) for c in self.components],
            "bindings": [asdict(b) for b in self.bindings],
            "entrypoints": self.entrypoints, "profiles": self.profiles,
            "ceiling": self.ceiling, "metadata": self.metadata,
        }))


def _v2_strings(value: object, label: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value or any(not isinstance(x, str) or not x for x in value):
        raise ManifestError(f"{label} must be a non-empty string array")
    return tuple(value)


def parse_named_manifest(raw: object) -> NamedManifest:
    """The sole parser for ``mhf.manifest/2``; all authority is consumed here."""
    if not isinstance(raw, dict) or set(raw) - _V2_TOP_FIELDS:
        raise ManifestError("manifest has unknown or unread top-level fields")
    if raw.get("api") != "mhf.manifest/2" or not isinstance(raw.get("id"), str) or not raw["id"]:
        raise ManifestError("mhf.manifest/2 requires api and id")
    rows = raw.get("components")
    if not isinstance(rows, list) or not rows:
        if isinstance(rows, dict) and rows:
            return _parse_named_component_map(raw, rows)
        raise ManifestError("components must be a non-empty array or named object")
    components: list[NamedComponent] = []
    names: set[str] = set()
    for row in rows:
        if not isinstance(row, dict) or set(row) - _V2_COMPONENT_FIELDS:
            raise ManifestError("component has unknown or unread fields")
        required = ("name", "kind", "implementation", "config", "isolation", "ceiling", "interfaces", "entrypoints")
        if any(key not in row for key in required): raise ManifestError("component is incomplete")
        name = row["name"]
        if not isinstance(name, str) or not name or name in names: raise ManifestError("component names must be unique")
        kind = row["kind"]
        if kind not in _SPI_KINDS: raise ManifestError(f"unknown SPI kind: {kind}")
        if row["isolation"] not in _ISOLATION: raise ManifestError("invalid isolation")
        if not isinstance(row["implementation"], str) or not row["implementation"] or not isinstance(row["config"], str) or not row["config"]:
            raise ManifestError("implementation/config refs are required")
        components.append(NamedComponent(name, kind, row["implementation"], row["config"], row["isolation"],
                                         _v2_strings(row["ceiling"], "ceiling"), _v2_strings(row["interfaces"], "interfaces"),
                                         _v2_strings(row["entrypoints"], "entrypoints"), row.get("authority") is True))
        names.add(name)
    binding_rows = raw.get("bindings", [])
    if not isinstance(binding_rows, list): raise ManifestError("bindings must be an array")
    bindings: list[TypedBinding] = []
    for row in binding_rows:
        if not isinstance(row, dict) or set(row) - {"from", "to", "interface", "lazy"} or not all(isinstance(row.get(x), str) and row[x] for x in ("from", "to", "interface")):
            raise ManifestError("binding is malformed")
        if row["from"] == row["to"] or row["from"] not in names or row["to"] not in names: raise ManifestError("binding endpoint is unknown or self-referential")
        source = next(c for c in components if c.name == row["from"]); target = next(c for c in components if c.name == row["to"])
        if row["interface"] not in target.interfaces: raise ManifestError("binding interface is not declared")
        bindings.append(TypedBinding(row["from"], row["to"], row["interface"], row.get("lazy") is True))
    if not isinstance(raw.get("entrypoints"), list) or not raw["entrypoints"] or any(x not in names for x in raw["entrypoints"]):
        raise ManifestError("entrypoints must name components")
    profiles = raw.get("profiles", {})
    if not isinstance(profiles, dict): raise ManifestError("profiles must be an object")
    ceiling = _v2_strings(raw.get("ceiling"), "harness ceiling")
    authority_names = {c.name for c in components if c.authority}
    consumed = {b.source for b in bindings} | set(raw["entrypoints"])
    if authority_names - consumed: raise ManifestError("authority-bearing component is unconsumed")
    # A non-lazy cycle is an eager construction cycle; lazy cycles are allowed.
    edges = [(b.source, b.target) for b in bindings if not b.lazy]
    visiting: set[str] = set(); visited: set[str] = set()
    def visit(name: str) -> None:
        if name in visiting: raise ManifestError("eager dependency cycle")
        if name in visited: return
        visiting.add(name)
        for left, right in edges:
            if left == name: visit(right)
        visiting.remove(name); visited.add(name)
    for name in names: visit(name)
    return NamedManifest(raw["id"], tuple(components), tuple(bindings), tuple(raw["entrypoints"]), raw.get("profiles", {}), ceiling)


def compose_named_manifest(manifest: NamedManifest, graph: ArtifactGraph) -> NamedManifest:
    """Resolve immutable refs and return the already-frozen composition value."""
    files = graph.by_path()
    for component in manifest.components:
        if component.implementation not in files:
            raise ManifestError(f"component reference does not resolve: {component.implementation}")
        if isinstance(component.config, str) and component.config not in files:
            raise ManifestError(f"component config reference does not resolve: {component.config}")
        for component_selector in component.ceiling:
            if not ceiling_allows(
                [_selector_object(item) for item in manifest.ceiling],
                _selector_object(component_selector),
            ).included:
                raise ManifestError(f"component ceiling widens harness ceiling: {component.name}")
    capabilities = manifest.metadata.get("capabilities", ())
    if any(item.get("verb") == "agent.spawn" for item in capabilities
           if isinstance(item, Mapping)):
        raise ManifestError("agent.spawn not implemented before M-6")
    # Re-freeze with resolved implementation/config digests in the identity.
    resolved = [{"name": c.name, "kind": c.kind, "implementation": files[c.implementation].digest,
                 "config": (files[c.config].digest if isinstance(c.config, str) and c.config in files
                            else c.config), "isolation": c.isolation, "ceiling": c.ceiling,
                 "interfaces": c.interfaces, "entrypoints": c.entrypoints, "authority": c.authority}
                for c in manifest.components]
    return replace_named_digest(manifest, resolved)


def replace_named_digest(manifest: NamedManifest, resolved: list[Mapping[str, Any]]) -> NamedManifest:
    value = NamedManifest(manifest.manifest_id, manifest.components, manifest.bindings,
                          manifest.entrypoints, manifest.profiles, manifest.ceiling,
                          manifest.api, manifest.metadata)
    object.__setattr__(value, "digest", digest_of({"api": value.api, "id": value.manifest_id, "components": resolved,
                                                    "bindings": [asdict(b) for b in value.bindings], "entrypoints": value.entrypoints,
                                                    "profiles": value.profiles, "ceiling": value.ceiling,
                                                    "metadata": value.metadata}))
    return value


def _parse_named_component_map(raw: Mapping[str, Any], rows: Mapping[str, Any]) -> NamedManifest:
    """Normalize the ratified open-map `/2` surface to the domain value."""
    allowed = {"api", "id", "components", "bindings", "entrypoints", "profiles", "ceiling",
               "capabilities", "model_routes", "budget", "system_prompt", "approval_policy",
               "guardrails", "undeletable"}
    unknown = set(raw) - allowed
    if unknown: raise ManifestError(f"manifest has unread fields: {sorted(unknown)}")
    if raw.get("api") != "mhf.manifest/2" or not isinstance(raw.get("id"), str) or not raw["id"]:
        raise ManifestError("mhf.manifest/2 requires api and id")
    components: list[NamedComponent] = []
    names: set[str] = set()
    kind_map = {"planner": "IPlanner", "context": "IContextManager", "memory": "IMemoryEngine",
                "toolkit": "IToolkit", "evaluation": "IEvaluationGate"}
    for name, row in rows.items():
        if not isinstance(name, str) or not name or name in names or not isinstance(row, dict):
            raise ManifestError("components must be unique named objects")
        allowed_component = {"kind", "spi", "role", "ref", "implementation", "config", "ceiling",
                             "isolation", "interfaces", "entrypoints", "authority"}
        extra = set(row) - allowed_component
        if extra: raise ManifestError(f"component {name} has unread fields: {sorted(extra)}")
        kind = row.get("kind", row.get("spi", row.get("role")))
        kind = kind_map.get(kind, kind)
        if kind not in _SPI_KINDS: raise ManifestError(f"unknown SPI kind: {kind}")
        implementation = row.get("implementation", row.get("ref"))
        if not isinstance(implementation, str) or not implementation:
            raise ManifestError(f"component {name} requires ref")
        if "isolation" not in row:
            raise ManifestError(f"component {name} requires isolation")
        isolation = row["isolation"]
        if isolation not in _ISOLATION: raise ManifestError(f"component {name} has invalid isolation")
        if "ceiling" not in row:
            raise ManifestError(f"component {name} requires a non-empty ceiling")
        ceiling_raw = row["ceiling"]
        ceiling = _canonical_selectors(_selector_values(ceiling_raw), f"components.{name}.ceiling")
        if "interfaces" not in row:
            raise ManifestError(f"component {name} requires declared interfaces")
        interfaces = row["interfaces"]
        if not isinstance(interfaces, (list, tuple)) or any(not isinstance(x, str) or not x for x in interfaces):
            raise ManifestError(f"component {name} interfaces are invalid")
        if "config" not in row:
            raise ManifestError(f"component {name} requires config")
        config = row["config"]
        if not isinstance(config, (str, dict)) or (isinstance(config, str) and not config):
            raise ManifestError(f"component {name} config must be an object or artifact ref")
        entrypoints = row.get("entrypoints", (name,))
        if not isinstance(entrypoints, (list, tuple)) or any(not isinstance(x, str) or not x for x in entrypoints):
            raise ManifestError(f"component {name} entrypoints are invalid")
        components.append(NamedComponent(name, kind, implementation, config, isolation,
                                         ceiling, tuple(interfaces), tuple(entrypoints),
                                         row.get("authority") is True))
        names.add(name)
    entrypoints = raw.get("entrypoints")
    entrypoint_identity: object
    if isinstance(entrypoints, list):
        if not entrypoints or any(not isinstance(x, str) or x not in names for x in entrypoints):
            raise ManifestError("entrypoints must name declared components")
        entrypoint_names = tuple(entrypoints)
        entrypoint_identity = tuple(entrypoints)
    elif isinstance(entrypoints, dict):
        if not entrypoints:
            raise ManifestError("entrypoints must not be empty")
        entrypoint_names_list: list[str] = []
        for interface, endpoint in entrypoints.items():
            if not isinstance(interface, str) or not interface:
                raise ManifestError("entrypoint interface names must be non-empty")
            component_name = endpoint.get("component") if isinstance(endpoint, dict) else endpoint
            if not isinstance(component_name, str) or component_name not in names:
                raise ManifestError("entrypoint endpoint names an unknown component")
            if isinstance(endpoint, dict) and set(endpoint) - {"component", "interface"}:
                raise ManifestError("entrypoint has unread fields")
            if isinstance(endpoint, dict) and endpoint.get("interface", interface) != interface:
                raise ManifestError("entrypoint interface does not match its key")
            entrypoint_names_list.append(component_name)
        entrypoint_names = tuple(entrypoint_names_list)
        entrypoint_identity = entrypoints
    else:
        raise ManifestError("entrypoints must be a non-empty list or named object")
    bindings = _parse_named_bindings(raw.get("bindings", []), names, tuple(components))
    profiles = raw.get("profiles", {})
    if not isinstance(profiles, dict): raise ManifestError("profiles must be an object")
    if "ceiling" not in raw and "capabilities" not in raw:
        raise ManifestError("manifest requires a non-empty harness ceiling")
    ceiling_value = raw.get("ceiling", raw.get("capabilities"))
    ceiling = _canonical_selectors(_selector_values(ceiling_value), "ceiling")
    capabilities = _parse_capabilities(raw.get("capabilities", []))
    if capabilities and tuple(item["selector"] for item in capabilities) != ceiling:
        raise ManifestError("capability selectors must equal the declared harness ceiling")
    authority_names = {c.name for c in components if c.authority}
    consumed = {b.source for b in bindings} | set(entrypoint_names)
    if authority_names - consumed: raise ManifestError("authority-bearing component is unconsumed")
    _reject_eager_cycles(bindings, names)
    metadata = {key: raw[key] for key in ("model_routes", "budget", "system_prompt", "approval_policy",
                                           "guardrails", "undeletable") if key in raw}
    metadata["entrypoints"] = entrypoint_identity
    if capabilities:
        metadata["capabilities"] = capabilities
    return NamedManifest(raw["id"], tuple(components), tuple(bindings), tuple(entrypoint_names), profiles, ceiling,
                         metadata=metadata)


def _canonical_selectors(value: object, label: str, *, allow_empty: bool = False) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)) or (not allow_empty and not value):
        raise ManifestError(f"{label} must be a selector array")
    result: list[str] = []
    for index, item in enumerate(value):
        if isinstance(item, str):
            try:
                result.append(canonicalise_selector(parse_selector(parse_json_text(item))))
            except (TypeError, ValueError) as exc:
                raise ManifestError(f"{label}[{index}] is not a canonical selector") from exc
        elif isinstance(item, dict):
            try:
                result.append(canonicalise_selector(parse_selector(item)))
            except (TypeError, ValueError) as exc:
                raise ManifestError(f"{label}[{index}] is not a valid selector") from exc
        else:
            raise ManifestError(f"{label}[{index}] is not a selector")
    return tuple(result)


def _selector_object(value: str) -> Mapping[str, Any]:
    try:
        parsed = parse_json_text(value)
        if not isinstance(parsed, dict):
            raise TypeError("selector is not an object")
        return parsed
    except (TypeError, ValueError) as exc:
        raise ManifestError("stored selector is not canonical JSON") from exc


def _selector_values(value: object) -> object:
    if isinstance(value, (list, tuple)) and all(isinstance(item, dict) and "selector" in item for item in value):
        return [item["selector"] for item in value]
    return value


def _parse_capabilities(value: object) -> tuple[Mapping[str, Any], ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise ManifestError("capabilities must be an array")
    result: list[Mapping[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict) or set(item) != {"verb", "selector"}:
            raise ManifestError(f"capabilities[{index}] must contain only verb and selector")
        if not isinstance(item["verb"], str) or not item["verb"] or not isinstance(item["selector"], dict):
            raise ManifestError(f"capabilities[{index}] is malformed")
        selector = canonicalise_selector(parse_selector(item["selector"]))
        result.append({"verb": item["verb"], "selector": selector})
    return tuple(result)


def _parse_named_bindings(value: object, names: set[str], components: tuple[NamedComponent, ...]) -> list[TypedBinding]:
    if not isinstance(value, list): raise ManifestError("bindings must be an array")
    interfaces = {c.name: set(c.interfaces) for c in components}
    result: list[TypedBinding] = []
    for index, row in enumerate(value):
        if not isinstance(row, dict) or set(row) - {"from", "to", "interface", "relation", "channel", "lazy"}:
            raise ManifestError(f"bindings[{index}] has unread fields")
        source, target = row.get("from"), row.get("to")
        relation = row.get("interface", row.get("relation", row.get("channel")))
        if not isinstance(source, str) or not isinstance(target, str) or not isinstance(relation, str):
            raise ManifestError(f"bindings[{index}] requires from, to, and typed relation")
        if source == target or source not in names or target not in names:
            raise ManifestError(f"bindings[{index}] has unknown or self endpoint")
        if relation not in interfaces[target] and relation not in interfaces[source]:
            raise ManifestError(f"bindings[{index}] relation is undeclared")
        result.append(TypedBinding(source, target, relation, row.get("lazy") is True))
    return result


def _reject_eager_cycles(bindings: list[TypedBinding], names: set[str]) -> None:
    edges = [(b.source, b.target) for b in bindings if not b.lazy]
    visiting: set[str] = set(); visited: set[str] = set()
    def visit(name: str) -> None:
        if name in visiting: raise ManifestError("eager dependency cycle")
        if name in visited: return
        visiting.add(name)
        for source, target in edges:
            if source == name: visit(target)
        visiting.remove(name); visited.add(name)
    for name in names: visit(name)


@dataclass(frozen=True, slots=True)
class RegisteredManifest:
    name: str
    path: str
    undeletable: bool
    role: str


@dataclass(frozen=True, slots=True)
class ManifestRegistry:
    entries: tuple[RegisteredManifest, ...]

    @classmethod
    def parse(cls, raw: object) -> "ManifestRegistry":
        if not isinstance(raw, dict) or not isinstance(raw.get("manifests"), list):
            raise ManifestError("manifest registry requires a manifests array")
        entries = []
        for item in raw["manifests"]:
            if not isinstance(item, dict):
                raise ManifestError("manifest registry entries must be objects")
            try:
                entries.append(RegisteredManifest(str(item["name"]), str(item["path"]),
                                                  item["undeletable"] is True, str(item["role"])))
            except KeyError as exc:
                raise ManifestError(f"manifest registry entry missing {exc.args[0]}") from exc
        if len({entry.name for entry in entries}) != len(entries):
            raise ManifestError("manifest registry names must be unique")
        return cls(tuple(entries))

    def remove(self, name: str) -> "ManifestRegistry":
        target = next((entry for entry in self.entries if entry.name == name), None)
        if target is None:
            raise ManifestError(f"manifest is not registered: {name}")
        if target.undeletable:
            raise ManifestError(f"manifest is undeletable: {name}")
        return ManifestRegistry(tuple(entry for entry in self.entries if entry.name != name))


@dataclass(frozen=True, slots=True)
class CapabilityRequirement:
    verb: str
    sink: str
    selector: str
    risk: str


@dataclass(frozen=True, slots=True)
class HarnessManifest:
    harness: str
    components: tuple[tuple[str, tuple[str, ...]], ...]
    capabilities: tuple[CapabilityRequirement, ...]
    evaluators: tuple[str, ...]
    budget_policy: str
    undeletable: bool = False


@dataclass(frozen=True, slots=True)
class FrozenHarness:
    harness: str
    episode_id: str
    components: tuple[tuple[str, tuple[str, ...]], ...]
    capabilities: tuple[CapabilityRequirement, ...]
    evaluators: tuple[str, ...]
    budget_policy: str
    graph_digest: str
    identity: Mapping[str, Any] = field(default_factory=dict)
    composition_digest: str = field(init=False)

    def __post_init__(self) -> None:
        # D_H (ADR-0076 §4): episode_id is instance identity, not composition
        # identity. Extra identity keys (prompt, ceiling, approval, routes)
        # are supplied by Runtime.compose.
        object.__setattr__(self, "composition_digest", digest_of({
            "harness": self.harness,
            "components": self.components,
            "capabilities": tuple((item.verb, item.sink, item.selector, item.risk)
                                  for item in self.capabilities),
            "evaluators": self.evaluators,
            "budgetPolicy": self.budget_policy,
            "graphDigest": self.graph_digest,
            **dict(self.identity),
        }))

    def capability(self, verb: str) -> CapabilityRequirement:
        matches = tuple(item for item in self.capabilities if item.verb == verb)
        if len(matches) != 1:
            raise ManifestError(f"expected one capability for {verb}, found {len(matches)}")
        return matches[0]


def _strings(value: object, label: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        raise ManifestError(f"{label} must be an array of non-empty strings")
    return tuple(value)


def parse_manifest(raw: object) -> HarnessManifest:
    if not isinstance(raw, dict):
        raise ManifestError("manifest must be an object")
    required = {"harness", "components", "capabilities", "evaluators", "budgetPolicy"}
    missing = required - raw.keys()
    if missing:
        raise ManifestError(f"manifest missing {sorted(missing)}")
    if not isinstance(raw["harness"], str) or not raw["harness"]:
        raise ManifestError("harness must be a non-empty string")
    if not isinstance(raw["components"], dict):
        raise ManifestError("components must be an object")
    components = tuple(sorted((role, _strings(paths, f"components.{role}"))
                              for role, paths in raw["components"].items()))
    if not isinstance(raw["capabilities"], list):
        raise ManifestError("capabilities must be an array")
    capabilities = []
    for index, item in enumerate(raw["capabilities"]):
        if not isinstance(item, dict):
            raise ManifestError(f"capabilities[{index}] must be an object")
        try:
            verb, sink, selector, risk = (item[key] for key in ("verb", "sink", "selector", "risk"))
        except KeyError as exc:
            raise ManifestError(f"capabilities[{index}] missing {exc.args[0]}") from exc
        if not all(isinstance(value, str) and value for value in (verb, sink, risk)):
            raise ManifestError(f"capabilities[{index}] has invalid scalar fields")
        if sink not in {"pure", "observation", "privileged"}:
            raise ManifestError(f"capabilities[{index}] has invalid sink")
        parsed_selector = parse_selector(selector)
        capabilities.append(CapabilityRequirement(verb, sink,
                                                   canonicalise_selector(parsed_selector), risk))
    budget = raw["budgetPolicy"]
    if not isinstance(budget, str) or not budget:
        raise ManifestError("budgetPolicy must be a non-empty artifact path")
    return HarnessManifest(str(raw["harness"]), components, tuple(capabilities),
                           _strings(raw["evaluators"], "evaluators"), budget,
                           raw.get("undeletable") is True)


def compose(manifest: HarnessManifest, graph: ArtifactGraph, episode_id: str,
            identity: Mapping[str, Any] | None = None) -> FrozenHarness:
    if not episode_id:
        raise ManifestError("composition requires an episode id")
    files = graph.by_path()
    resolved: list[tuple[str, tuple[str, ...]]] = []
    for role, paths in manifest.components:
        digests = []
        for path in paths:
            if path not in files:
                raise ManifestError(f"component does not resolve: {path}")
            digests.append(files[path].digest)
        resolved.append((role, tuple(digests)))
    if manifest.budget_policy not in files:
        raise ManifestError(f"budget policy does not resolve: {manifest.budget_policy}")
    roots = tuple(path for _, paths in manifest.components for path in paths) + (manifest.budget_policy,)
    closure = graph.closure(roots)
    closure_digest = digest_of([(artifact.path, artifact.kind, artifact.digest)
                                for artifact in closure])
    return FrozenHarness(manifest.harness, episode_id, tuple(resolved),
                         manifest.capabilities, manifest.evaluators,
                         files[manifest.budget_policy].digest, closure_digest,
                         dict(identity or {}))
