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
                            "guardrails", "evaluation", "undeletable"})
_SPI_KINDS = frozenset({"IPlanner", "IMemoryEngine", "IToolkit", "IContextManager", "IEvaluationGate", "ICompletionPolicy"})
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
    metadata = {
        key: raw[key] for key in ("model_routes", "budget", "system_prompt", "approval_policy",
                                  "guardrails", "evaluation", "undeletable") if key in raw
    }
    metadata["evaluation"] = _parse_evaluation_policy(raw.get("evaluation"))
    return NamedManifest(raw["id"], tuple(components), tuple(bindings), tuple(raw["entrypoints"]), raw.get("profiles", {}), ceiling,
                         metadata=metadata)


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
               "guardrails", "evaluation", "undeletable"}
    unknown = set(raw) - allowed
    if unknown: raise ManifestError(f"manifest has unread fields: {sorted(unknown)}")
    if raw.get("api") != "mhf.manifest/2" or not isinstance(raw.get("id"), str) or not raw["id"]:
        raise ManifestError("mhf.manifest/2 requires api and id")
    components: list[NamedComponent] = []
    names: set[str] = set()
    kind_map = {"planner": "IPlanner", "context": "IContextManager", "memory": "IMemoryEngine",
                "toolkit": "IToolkit", "evaluation": "IEvaluationGate", "completion": "ICompletionPolicy"}
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
                                           "guardrails", "evaluation", "undeletable") if key in raw}
    metadata["evaluation"] = _parse_evaluation_policy(raw.get("evaluation"))
    metadata["entrypoints"] = entrypoint_identity
    if capabilities:
        metadata["capabilities"] = capabilities
    return NamedManifest(raw["id"], tuple(components), tuple(bindings), tuple(entrypoint_names), profiles, ceiling,
                         metadata=metadata)


def _parse_evaluation_policy(value: object) -> Mapping[str, Any]:
    """Parse the pre-execution evidence guardrail without creating a verdict."""
    if value is None:
        return {"mode": "exterior"}
    if value == "none":
        raise ManifestError("evaluation: none requires an explicit absence reason")
    if not isinstance(value, dict):
        raise ManifestError("evaluation must be 'none' or an object")
    if set(value) - {"mode", "absence_reason", "assurance_class", "oracle"}:
        raise ManifestError("evaluation has unread fields")
    mode = value.get("mode")
    if mode not in {"none", "exterior"}:
        raise ManifestError("evaluation mode must be none or exterior")
    if mode == "none":
        reason = value.get("absence_reason")
        assurance = value.get("assurance_class")
        if not isinstance(reason, str) or not reason or not isinstance(assurance, str) or not assurance:
            raise ManifestError("declared evaluation absence requires reason and assurance_class")
        if "oracle" in value:
            raise ManifestError("declared evaluation absence cannot name an oracle")
    elif "absence_reason" in value or "assurance_class" in value:
        raise ManifestError("absence fields are only valid for evaluation mode none")
    return dict(value)


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
        # `sink` and `risk` decide which kernel pipeline a verb takes, so `/2`
        # states them exactly as `/1` always has. Without them the authored
        # dialect could not express a harness the compatibility dialect can,
        # and the two ingress routes could never reach one `D_H` (RF-79).
        if not isinstance(item, dict) or set(item) - {"verb", "selector", "sink", "risk"}:
            raise ManifestError(
                f"capabilities[{index}] may contain only verb, selector, sink, and risk")
        if not {"verb", "selector"} <= set(item):
            raise ManifestError(f"capabilities[{index}] requires verb and selector")
        if not isinstance(item["verb"], str) or not item["verb"] or not isinstance(item["selector"], dict):
            raise ManifestError(f"capabilities[{index}] is malformed")
        selector = canonicalise_selector(parse_selector(item["selector"]))
        row = {"verb": item["verb"], "selector": selector}
        for key in ("sink", "risk"):
            if key in item:
                if not isinstance(item[key], str) or not item[key]:
                    raise ManifestError(f"capabilities[{index}] {key} must be a non-empty string")
                row[key] = item[key]
        result.append(row)
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


# ---------------------------------------------------------------------------
# Canonical composition — ADR-0088 Decision 1
# ---------------------------------------------------------------------------
#
# The one production chain is
#
#     mhf.manifest/2 bytes -> CanonicalManifest -> FrozenComposition [D_H]
#
# `CanonicalManifest` is the sole schema-authoritative normalized value. Both
# supported dialects terminate here: `mhf.harness/1` bytes stop at
# `canonical_from_legacy` and `mhf.manifest/2` bytes stop at `canonical_from_v2`.
# Nothing downstream may read a dialect-specific value, which is what makes the
# compatibility reader ingress rather than a second execution authority.

#: Legacy `mhf.harness/1` component role -> the SPI interface that consumes it.
#:
#: This table *is* the declared meaning of the legacy dialect, not an invented
#: default. `/1` names a role, and the runtime has always resolved that role to
#: exactly one consumer; writing the resolution down is what lets a `/1` pack
#: and the authored `/2` statement of the same harness reach one `D_H` (RF-79).
#: A role with no row is unconsumed authority and denies at ingress, matching
#: the loader's own `REGISTERED_COMPONENT_CONSUMERS` rule.
LEGACY_ROLE_INTERFACE: Mapping[str, str] = {
    "system_prompt": "IContextManager",
    "context_policy": "IContextManager",
    "routing_policy": "IContextManager",
    "compaction_policy": "IContextManager",
    "approval_policy": "IEvaluationGate",
    "retrieval_policy": "IMemoryEngine",
    "repo_index": "IMemoryEngine",
    "index_component": "IMemoryEngine",
    "skill": "IMemoryEngine",
    "skills": "IMemoryEngine",
    "tools": "IToolkit",
}

#: `/1` had no isolation tier and every shipped `/1` pack runs in the host
#: process. Normalizing to `in_process` records what the dialect already meant;
#: it never grants a legacy pack a tier it did not declare.
LEGACY_ISOLATION = "in_process"

#: Verbs that parse and digest but have no live code path before their
#: milestone. Refusing them at ingress keeps the reservation identity-bearing
#: (ADR-0085). M-6 activates `agent.spawn`.
_INERT_VERBS: Mapping[str, str] = {}


@dataclass(frozen=True, slots=True)
class CanonicalManifest:
    """The sole schema-authoritative normalized manifest value (ADR-0088 §1.1).

    Every behaviour-affecting fact a composition can declare is resolved once,
    here, in dialect-independent form. Two manifests that state the same facts
    in different dialects normalize to equal values and therefore to one `D_H`.
    """

    manifest_id: str
    components: tuple[NamedComponent, ...]
    bindings: tuple[TypedBinding, ...]
    entrypoints: tuple[str, ...]
    ceiling: tuple[str, ...]
    capabilities: tuple[CapabilityRequirement, ...]
    evaluators: tuple[str, ...]
    budget_policy: str
    evaluation: Mapping[str, Any] = field(default_factory=lambda: {"mode": "exterior"})
    profiles: Mapping[str, Any] = field(default_factory=dict)
    system_prompt: str | None = None
    approval_policy: str | None = None
    model_routes: tuple[str, ...] = ()
    guardrails: Mapping[str, Any] = field(default_factory=dict)
    undeletable: bool = False

    def component(self, name: str) -> NamedComponent:
        for item in self.components:
            if item.name == name:
                return item
        raise ManifestError(f"composition declares no component named {name!r}")

    def components_for(self, interface: str) -> tuple[NamedComponent, ...]:
        """Every component consumed through `interface`, in declaration order."""
        return tuple(item for item in self.components if interface in item.interfaces)

    @property
    def verbs(self) -> tuple[str, ...]:
        return tuple(item.verb for item in self.capabilities)

    @property
    def artifact_refs(self) -> tuple[str, ...]:
        """Every artifact path this composition names, deduplicated in order.

        Composition reads exactly this set. A file the manifest does not name
        cannot enter `D_H`, and a named file that does not resolve denies.
        """
        refs: list[str] = []
        for item in self.components:
            for ref in (item.implementation, item.config):
                if isinstance(ref, str) and ref and ref not in refs:
                    refs.append(ref)
        for ref in (self.budget_policy, self.system_prompt, self.approval_policy):
            if isinstance(ref, str) and ref and ref not in refs:
                refs.append(ref)
        for ref in self.model_routes:
            if ref not in refs:
                refs.append(ref)
        return tuple(refs)

    def identity_preimage(self) -> Mapping[str, Any]:
        """The dialect-independent facts, before artifact resolution.

        Kept separate from `FrozenComposition` so that normalization can be
        compared between two ingress routes without composing either.
        """
        return {
            "id": self.manifest_id,
            "components": [
                {
                    "name": item.name,
                    "kind": item.kind,
                    "isolation": item.isolation,
                    "ceiling": list(item.ceiling),
                    "interfaces": list(item.interfaces),
                    "entrypoints": list(item.entrypoints),
                    "authority": item.authority,
                }
                for item in self.components
            ],
            "bindings": [asdict(item) for item in self.bindings],
            "entrypoints": list(self.entrypoints),
            "ceiling": list(self.ceiling),
            "capabilities": [
                [item.verb, item.sink, item.selector, item.risk] for item in self.capabilities
            ],
            "evaluators": list(self.evaluators),
            "evaluation": dict(self.evaluation),
            "profiles": dict(self.profiles),
            "guardrails": dict(self.guardrails),
            "undeletable": self.undeletable,
        }


@dataclass(frozen=True, slots=True)
class FrozenComposition:
    """The one immutable composition value; its JCS digest is `D_H` (ADR-0088 §1.2).

    Freezing resolves every artifact reference the manifest names to immutable
    content, so `D_H` is a function of *what the composition is*, never of where
    its bytes happen to sit. Two ingress dialects that declare the same facts
    over the same bytes therefore reach the same digest (RF-79).

    `episode_id` is instance identity and is deliberately excluded from `D_H`
    (ADR-0076 §4): the same harness composed for two episodes is one harness.
    """

    manifest: CanonicalManifest
    episode_id: str
    #: component name -> (implementation digest, config digest or inline value)
    component_digests: tuple[tuple[str, str, Any], ...]
    #: The budget policy as a resolved value, never as the ref that carried it.
    budget: Mapping[str, Any]
    #: Closure digest over the artifacts this composition read. Carried for
    #: attribution and replay, deliberately *not* part of `D_H`: a manifest that
    #: names the same inputs must not change identity because an unnamed file
    #: sits beside it, and an inline value must digest as its file-borne twin.
    graph_digest: str = ""
    identity: Mapping[str, Any] = field(default_factory=dict)
    composition_digest: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "composition_digest", digest_of(self.identity_preimage()))

    def identity_preimage(self) -> Mapping[str, Any]:
        """Return the JSON-shaped facts whose JCS digest is ``D_H``."""
        preimage = dict(self.manifest.identity_preimage())
        preimage["resolved"] = [
            {"name": name, "implementation": implementation, "config": config}
            for name, implementation, config in self.component_digests
        ]
        preimage["budget"] = dict(self.budget)
        preimage.update(dict(self.identity))
        return preimage

    # -- the facts callers read -------------------------------------------
    #
    # Exposed on the composition rather than reached through `.manifest` so
    # that a caller cannot accidentally bind to a dialect-shaped value.

    @property
    def harness(self) -> str:
        return self.manifest.manifest_id

    @property
    def components(self) -> tuple[NamedComponent, ...]:
        return self.manifest.components

    @property
    def capabilities(self) -> tuple[CapabilityRequirement, ...]:
        return self.manifest.capabilities

    @property
    def evaluators(self) -> tuple[str, ...]:
        return self.manifest.evaluators

    @property
    def budget_policy(self) -> Any:
        """The policy as declared: an artifact ref, or an inline object."""
        return self.manifest.budget_policy

    @property
    def bindings(self) -> tuple[TypedBinding, ...]:
        return self.manifest.bindings

    @property
    def entrypoints(self) -> tuple[str, ...]:
        return self.manifest.entrypoints

    @property
    def ceiling(self) -> tuple[str, ...]:
        return self.manifest.ceiling

    def capability(self, verb: str) -> CapabilityRequirement:
        matches = tuple(item for item in self.capabilities if item.verb == verb)
        if len(matches) != 1:
            raise ManifestError(f"expected one capability for {verb}, found {len(matches)}")
        return matches[0]


def _canonical_capabilities(rows: object, *, dialect: str) -> tuple[CapabilityRequirement, ...]:
    """Normalize capability rows from either dialect.

    `sink` and `risk` are behaviour-affecting: the sink class decides which
    kernel pipeline a verb takes. A dialect that cannot state them cannot state
    the harness, so `/2` carries them exactly as `/1` always has.
    """
    if rows is None:
        return ()
    if not isinstance(rows, (list, tuple)):
        raise ManifestError("capabilities must be an array")
    result: list[CapabilityRequirement] = []
    seen: set[str] = set()
    for index, item in enumerate(rows):
        if not isinstance(item, Mapping):
            raise ManifestError(f"capabilities[{index}] must be an object")
        unread = set(item) - {"verb", "sink", "selector", "risk"}
        if unread:
            raise ManifestError(
                f"capabilities[{index}] has unread fields: {sorted(unread)}")
        verb = item.get("verb")
        if not isinstance(verb, str) or not verb:
            raise ManifestError(f"capabilities[{index}] requires a verb")
        if verb in seen:
            raise ManifestError(f"capability {verb} is declared twice")
        seen.add(verb)
        if verb in _INERT_VERBS:
            raise ManifestError(_INERT_VERBS[verb])
        sink = item.get("sink")
        risk = item.get("risk")
        if not isinstance(sink, str) or sink not in {"pure", "observation", "privileged"}:
            raise ManifestError(
                f"capabilities[{index}] ({verb}) requires sink pure|observation|privileged; "
                f"{dialect} states no default")
        if not isinstance(risk, str) or not risk:
            raise ManifestError(f"capabilities[{index}] ({verb}) requires a risk class")
        # A selector arrives either as authored JSON or already canonicalised
        # by the `/2` parser. Both are accepted; both end as one canonical form,
        # because the selector string is what enters `D_H`.
        selector = item.get("selector")
        if isinstance(selector, str) and selector:
            source: Any = _selector_object(selector)
        elif isinstance(selector, Mapping):
            source = dict(selector)
        else:
            raise ManifestError(f"capabilities[{index}] ({verb}) requires a selector")
        try:
            canonical = canonicalise_selector(parse_selector(source))
        except (TypeError, ValueError) as exc:
            raise ManifestError(
                f"capabilities[{index}] ({verb}) selector is invalid: {exc}") from exc
        result.append(CapabilityRequirement(verb, sink, canonical, risk))
    return tuple(result)


def _sorted_components(components: tuple[NamedComponent, ...]) -> tuple[NamedComponent, ...]:
    """Canonical component order.

    Dialects disagree about order: `/1` sorts roles, `/2` preserves authoring
    order. Order is not a behaviour-affecting fact, so normalization fixes it
    rather than letting it fork `D_H`.
    """
    names = [item.name for item in components]
    if len(set(names)) != len(names):
        raise ManifestError("component names must be unique")
    return tuple(sorted(components, key=lambda item: item.name))


def _split_evaluation(evaluation: Mapping[str, Any]) -> tuple[Mapping[str, Any], tuple[str, ...]]:
    """Hoist the named oracle out of the evaluation policy.

    `/1` names oracles in `evaluators`; `/2` names one in `evaluation.oracle`.
    Both mean "this exterior judge", so the canonical value carries the judge in
    one place and leaves mode/absence semantics in the policy.
    """
    policy = {key: value for key, value in evaluation.items() if key != "oracle"}
    oracle = evaluation.get("oracle")
    return policy, ((oracle,) if isinstance(oracle, str) and oracle else ())


def canonical_from_v2(raw: object) -> CanonicalManifest:
    """Normalize authored `mhf.manifest/2` bytes.

    Delegates every `/2` rule to `parse_named_manifest`, which stays the sole
    `/2` parser; this function only projects that value onto the canonical one.
    """
    named = parse_named_manifest(raw)
    metadata = dict(named.metadata)
    evaluation, evaluators = _split_evaluation(metadata.get("evaluation") or {"mode": "exterior"})
    capabilities = _canonical_capabilities(metadata.get("capabilities"), dialect="mhf.manifest/2")
    budget = metadata.get("budget")
    if budget is not None and not isinstance(budget, (Mapping, str)):
        raise ManifestError("budget must be an object or an artifact ref")
    model_routes = metadata.get("model_routes") or ()
    if not isinstance(model_routes, (list, tuple)):
        raise ManifestError("model_routes must be an array")
    return CanonicalManifest(
        manifest_id=named.manifest_id,
        components=_sorted_components(named.components),
        bindings=tuple(named.bindings),
        entrypoints=tuple(named.entrypoints),
        ceiling=tuple(named.ceiling),
        capabilities=capabilities,
        evaluators=evaluators,
        budget_policy=budget if budget is not None else {},
        evaluation=evaluation,
        profiles=dict(named.profiles),
        system_prompt=metadata.get("system_prompt"),
        approval_policy=metadata.get("approval_policy"),
        model_routes=tuple(str(item) for item in model_routes),
        guardrails=dict(metadata.get("guardrails") or {}),
        undeletable=metadata.get("undeletable") is True,
    )


def canonical_from_legacy(raw: object) -> CanonicalManifest:
    """Normalize supported `mhf.harness/1` bytes at the compatibility boundary.

    This is ingress, not an execution authority (ADR-0088 §1.1, §1.6): it reads
    the legacy dialect and emits the canonical value directly. No
    `HarnessManifest` is constructed, so no legacy value can cross into
    composition and become a second identity.
    """
    if not isinstance(raw, Mapping):
        raise ManifestError("manifest must be an object")
    unread = set(raw) - {"harness", "components", "capabilities", "evaluators",
                         "budgetPolicy", "undeletable", "api"}
    if unread:
        raise ManifestError(f"manifest has unread fields: {sorted(unread)}")
    harness = raw.get("harness")
    if not isinstance(harness, str) or not harness:
        raise ManifestError("harness must be a non-empty string")
    rows = raw.get("components")
    if not isinstance(rows, Mapping) or not rows:
        raise ManifestError("components must be a non-empty object")
    budget_policy = raw.get("budgetPolicy")
    if not isinstance(budget_policy, str) or not budget_policy:
        raise ManifestError("budgetPolicy must be a non-empty artifact path")

    capabilities = _canonical_capabilities(raw.get("capabilities"), dialect="mhf.harness/1")
    if not capabilities:
        raise ManifestError("a harness must declare at least one capability")
    ceiling = tuple(item.selector for item in capabilities)

    components: list[NamedComponent] = []
    for role in sorted(rows):
        interface = LEGACY_ROLE_INTERFACE.get(role)
        if interface is None:
            raise ManifestError(
                f"component role {role!r} has no registered consumer; unread "
                "components are forbidden at composition")
        paths = _strings(rows[role], f"components.{role}")
        for index, path in enumerate(paths):
            # One role may carry several artifacts. The suffix is positional and
            # stable, so a `/2` author can state the same graph by name.
            name = role if len(paths) == 1 else f"{role}.{index}"
            components.append(NamedComponent(
                name=name, kind=interface, implementation=path, config=path,
                isolation=LEGACY_ISOLATION, ceiling=ceiling,
                interfaces=(interface,), entrypoints=(name,), authority=False))

    entrypoints = tuple(item.name for item in components if "IToolkit" in item.interfaces)
    if not entrypoints:
        # A pack that declares no toolkit is entered through everything it
        # declares; deriving nothing would make the composition unreachable.
        entrypoints = tuple(item.name for item in components)

    return CanonicalManifest(
        manifest_id=harness,
        components=_sorted_components(tuple(components)),
        bindings=(),
        entrypoints=tuple(sorted(entrypoints)),
        ceiling=ceiling,
        capabilities=capabilities,
        evaluators=_strings(raw.get("evaluators", []), "evaluators")
        if raw.get("evaluators") else (),
        budget_policy=budget_policy,
        evaluation={"mode": "exterior"},
        undeletable=raw.get("undeletable") is True,
    )


def read_canonical_manifest(raw: object) -> CanonicalManifest:
    """The one production ingress. Dialect is decided here and nowhere else."""
    if not isinstance(raw, Mapping):
        raise ManifestError("manifest must be an object")
    api = raw.get("api")
    if api == "mhf.manifest/2":
        return canonical_from_v2(raw)
    if api is None or api == "mhf.harness/1":
        return canonical_from_legacy(raw)
    raise ManifestError(f"unsupported manifest api: {api!r}")


#: SPI interface -> the registered artifact kind its component files carry.
#:
#: `kind` participates in an artifact's digest, so the two dialects must agree
#: on it or identical bytes would digest differently. Deriving it from the
#: canonical interface — rather than from the `/1` role name — is what keeps
#: that agreement, and every value here is already a `BUILTIN_KINDS` row.
SPI_ARTIFACT_KIND: Mapping[str, str] = {
    "IToolkit": "tool_schema",
    "IContextManager": "context_policy",
    "IMemoryEngine": "retrieval_policy",
    "IPlanner": "routing_policy",
    "IEvaluationGate": "approval_policy",
    "ICompletionPolicy": "completion_policy",
}


def artifact_kind_for(component: NamedComponent) -> str:
    kind = SPI_ARTIFACT_KIND.get(component.kind)
    if kind is None:
        raise ManifestError(
            f"component {component.name} declares unknown SPI kind {component.kind!r}")
    return kind


def freeze_composition(manifest: CanonicalManifest, graph: ArtifactGraph, episode_id: str,
                       identity: Mapping[str, Any] | None = None) -> FrozenComposition:
    """Resolve every named reference and freeze one composition (`D_H`).

    Every failure here is a failure *before* a run: an unresolved ref, a
    component ceiling that widens the harness ceiling, or a budget policy that
    is not readable all deny at composition rather than at first effect.
    """
    if not episode_id:
        raise ManifestError("composition requires an episode id")
    files = graph.by_path()

    harness_ceiling = [_selector_object(item) for item in manifest.ceiling]
    resolved: list[tuple[str, str, Any]] = []
    for component in manifest.components:
        implementation = component.implementation
        if implementation not in files:
            raise ManifestError(f"component reference does not resolve: {implementation}")
        if isinstance(component.config, str):
            if component.config not in files:
                raise ManifestError(
                    f"component config reference does not resolve: {component.config}")
            config: Any = files[component.config].digest
        else:
            config = component.config
        for selector in component.ceiling:
            # Monotonic attenuation is a composition-time property: a component
            # may narrow the harness ceiling, never widen it.
            if not ceiling_allows(harness_ceiling, _selector_object(selector)).included:
                raise ManifestError(
                    f"component ceiling widens harness ceiling: {component.name}")
        resolved.append((component.name, files[implementation].digest, config))

    budget = manifest.budget_policy
    if isinstance(budget, str):
        if budget not in files:
            raise ManifestError(f"budget policy does not resolve: {budget}")
        try:
            budget = parse_json_text(files[budget].content)
        except (TypeError, ValueError) as exc:
            raise ManifestError(f"budget policy is not JSON: {manifest.budget_policy}") from exc
    if not isinstance(budget, Mapping):
        raise ManifestError("budget policy must resolve to an object")

    closure = graph.closure(tuple(ref for ref in manifest.artifact_refs if ref in files))
    graph_digest = digest_of([(item.path, item.kind, item.digest) for item in closure])

    return FrozenComposition(
        manifest=manifest,
        episode_id=episode_id,
        component_digests=tuple(resolved),
        budget=dict(budget),
        graph_digest=graph_digest,
        identity=dict(identity or {}),
    )
