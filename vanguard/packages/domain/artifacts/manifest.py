"""Harness manifest parsing and freeze-at-composition semantics."""

from __future__ import annotations

from dataclasses import dataclass, field
from ..canonicalisation.digest import digest_of
from ..selectors.resource_selector import canonicalise_selector, parse_selector
from .graph import ArtifactGraph


class ManifestError(ValueError):
    pass


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
    composition_digest: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "composition_digest", digest_of({
            "harness": self.harness, "episodeId": self.episode_id,
            "components": self.components,
            "capabilities": tuple((item.verb, item.sink, item.selector, item.risk)
                                  for item in self.capabilities),
            "evaluators": self.evaluators, "budgetPolicy": self.budget_policy,
            "graphDigest": self.graph_digest,
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


def compose(manifest: HarnessManifest, graph: ArtifactGraph, episode_id: str) -> FrozenHarness:
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
                         files[manifest.budget_policy].digest, closure_digest)
