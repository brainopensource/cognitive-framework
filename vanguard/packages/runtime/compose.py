"""Harness composition: freeze a manifest into a `Harness` (`2.2-C`).

`Runtime.compose` is the one composition path. `execute_harness` is the one
runtime authority that then hands the episode to `HarnessSession`.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, ClassVar, Mapping, Sequence

from ..agency import RunTermination
from ..agency.manifests.loader import ManifestLoader, ManifestLoadError
from ..domain.artifacts.graph import ArtifactFile, LogicalEdit, Workspace
from ..domain.artifacts.skill_index import SkillCard, SkillIndexError, parse_skill_card
from ..domain.artifacts.manifest import (
    FrozenHarness,
    ManifestError,
    compose,
)
from ..kernel import (
    Event,
    SinkClass,
    SinkMismatch,
    SinkRegistry,
)
from ..ports.evaluator import Verdict
from ..ports.event_store import EventStorePort
from .telemetry import RunTelemetry
from .wiring import BindingContext, CompositionError, DEFAULT_BINDINGS, EffectBinding

#: Manifest component role → artifact kind. The manifest names roles; the
#: artifact graph types them. Declared here because it is the one mapping the
#: two vocabularies do not share, and it is a table rather than a function so
#: that a new role is a row.
ROLE_KIND: Mapping[str, str] = {
    "system_prompt": "system_prompt",
    "tools": "tool_schema",
    "context_policy": "context_policy",
    "routing_policy": "routing_policy",
    "approval_policy": "approval_policy",
    "skills": "skills",
    "retrieval_policy": "retrieval_policy",
    "compaction_policy": "compaction_policy",
}

#: Budget-policy key → `Reservation` dimension. Keys absent from the policy
#: get no ceiling, and a dimension with no ceiling denies on first use rather
#: than defaulting to generous (`F-12`).
BUDGET_DIMENSION: Mapping[str, str] = {
    "usdMicros": "usd_micros",
    "costMicros": "usd_micros",
    "wallClockMillis": "millis",
    "tokens": "tokens",
    "bytes": "bytes",
}


# ---------------------------------------------------------------------------
# Values
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class TaskContext:
    """What the caller wants done, and against what."""

    brief: str
    repo_path: Path | str
    run_id: str = "run-1"
    episode_id: str = "episode-1"
    principal: str = "agent-1"
    #: $P(\\text{success} \\mid \\text{task})$, recorded before turn 1
    #: (`S5-SA-002`). `None` records nothing rather than recording a guess.
    competence_prior: float | None = None
    max_turns: int = 8
    #: 1.2-C, settled at the M-1 gate: `project_id` is **config-declared**,
    #: never derived from workspace identity. A workspace fingerprint (path,
    #: git remote, inode) would make the ledger's `prev_digest` chain a
    #: function of *where the repo happens to sit*, so the same project would
    #: fork into a new chain on every clone, move, or container mount, and
    #: cold replay (F-02) could not reattach to a chain it did not itself
    #: create. Identity of the subject under evaluation must be declared by
    #: the caller and carried, like `run_id` and `episode_id` beside it.
    project_id: str = "project-default"
    parent_principal_id: str | None = None
    parent_episode_id: str | None = None


@dataclass(frozen=True, slots=True)
class Receipt:
    """One effect that actually happened, as the root observed it."""

    verb: str
    descriptor_digest: str
    outcome: str
    detail: str = ""
    lease_id: str | None = None
    grant_digest: str | None = None


@dataclass(frozen=True, slots=True)
class RunResult:
    """What the run did, what it cost, and which harness produced it.

    `harness` and `composition_digest` are not decoration: attribution
    (`GTS-13C Ch.11 §2`) cannot answer *which component caused this* against a
    trajectory that does not say which components were active.
    """

    harness: str
    composition_digest: str
    terminal: RunTermination
    receipts: tuple[Receipt, ...]
    events: tuple[Event, ...]
    store: EventStorePort
    verdict: Verdict | None = None
    detail: str = ""
    #: `S9-A-01`. Per-component digests, so attribution can name a component
    #: rather than a run. Empty means the harness carried none, and that is a
    #: replay gap, not a default.
    gene_digests: Mapping[str, str] = field(default_factory=dict)
    #: `S9-A-02`. Integers or absent, never floats and never a fabricated zero.
    telemetry: RunTelemetry = field(default_factory=lambda: RunTelemetry(turns=0))
    #: `S9-A-01`. Why this arm produced no usable measurement. `None` means the
    #: instrument worked -- it does not mean the run succeeded.
    instrument_error: str | None = None
    #: `S9-A-04`. The ledger reduction Lane C's paired runner pairs on.
    state_digest: str = ""
    trajectory: Mapping[str, Any] | None = None

    #: Digests a benchmarked run must carry to be replayable (Phase 4 `V5-A`).
    #: `ClassVar` -- a constant, not a field.
    REPLAY_REQUIRED: ClassVar[tuple[str, ...]] = (
        "composition_digest", "gene_digests", "state_digest")

    def replay_gaps(self) -> tuple[str, ...]:
        """Which replay inputs this result is missing. Empty means replayable.

        `S9-A-03`. An executable audit rather than a prose claim: a run that
        cannot be replayed should say so in its own result, at the moment it is
        produced, not be discovered unreplayable a sprint later when the corpus
        is being re-derived.
        """
        return tuple(name for name in self.REPLAY_REQUIRED
                     if not getattr(self, name, None))


@dataclass(frozen=True, slots=True)
class Harness:
    """A composed, frozen harness. Nothing here varies after composition."""

    harness: str
    frozen: FrozenHarness
    verbs: tuple[str, ...]
    sinks: SinkRegistry
    risk_of: Mapping[str, str]
    system_core: str
    tool_schemas: tuple[Mapping[str, Any], ...]
    budget: Mapping[str, int]
    effect_budget: int
    #: `W11-A`. Component path the pack declared for its repository index, or
    #: `None`. Declared, never inferred: a harness that did not ask for an
    #: index must not silently acquire one.
    index_component: str | None
    evaluators: tuple[str, ...]
    bindings: Mapping[str, EffectBinding]
    translator: Any = None
    gene_digests: Mapping[str, str] = field(default_factory=dict)
    #: `W12-B`. Parsed skill cards, or `()` if the pack declared no
    #: `skill`/`skills` component. Rendered into `L3` by `ContextCompiler`
    #: itself (`format_skill_index`), not pre-rendered here.
    skill_cards: tuple[SkillCard, ...] = ()
    capability_ceiling: tuple[str, ...] = ()

    @property
    def composition_digest(self) -> str:
        return self.frozen.composition_digest

    def sink_class_of(self, verb: str) -> SinkClass:
        return self.sinks.sink_class(verb)

    def diff_verb(self) -> str | None:
        """The verb whose approvals are descriptor-bound to a diff."""
        for verb in self.verbs:
            binding = self.bindings.get(verb)
            if binding is not None and binding.carries_diff:
                return verb
        return None



class Runtime:
    """Assembles a harness from a manifest and runs one episode against it."""

    @classmethod
    def compose(
        cls,
        manifest_path: str | Path,
        *,
        episode_id: str = "episode-1",
        bindings: Mapping[str, EffectBinding] | None = None,
    ) -> Harness:
        """Freeze one harness. Every failure here is a failure *before* a run."""
        table = DEFAULT_BINDINGS if bindings is None else bindings
        loader = ManifestLoader()
        path = Path(manifest_path)
        if not path.is_absolute() and not path.exists():
            candidate = loader.base_dir / path
            if candidate.exists():
                path = candidate
        if path.is_dir():
            path = path / "manifest.json"

        try:
            pack = loader.load_pack(path.parent if path.name == "manifest.json" else path)
            manifest = pack.manifest
            translator = pack.translator
        except ManifestLoadError as exc:
            raise CompositionError(str(exc)) from exc
        except (OSError, json.JSONDecodeError) as exc:
            raise CompositionError(f"manifest does not load: {path}: {exc}") from exc

        directory = path.parent
        artifacts, contents = cls._artifacts(manifest, directory)
        workspace = Workspace.empty().apply(
            LogicalEdit(f"compose {manifest.harness}", artifacts))
        components = dict(manifest.components)
        system_core = "\n".join(contents[p] for p in components.get("system_prompt", ()))
        approval_policy = "\n".join(
            contents[p] for p in components.get("approval_policy", ()) if p in contents)
        model_routes = tuple(
            contents[p] for p in components.get("routing_policy", ()) if p in contents)
        ceiling = tuple(capability.selector for capability in manifest.capabilities)
        try:
            frozen = compose(
                manifest, workspace.graph, episode_id,
                identity={
                    "systemPrompt": system_core,
                    "ceiling": ceiling,
                    "approvalPolicy": approval_policy,
                    "modelRoutes": model_routes,
                },
            )
        except ManifestError as exc:
            raise CompositionError(str(exc)) from exc

        verbs = tuple(capability.verb for capability in manifest.capabilities)
        missing = [verb for verb in verbs if verb not in table]
        if missing:
            raise CompositionError(
                f"{manifest.harness}: no adapter bound for {sorted(missing)}; a harness "
                "that cannot be wired must fail at composition")

        sinks = SinkRegistry()
        for capability in manifest.capabilities:
            try:
                sinks.register(capability.verb, SinkClass(capability.sink))
            except (SinkMismatch, ValueError) as exc:
                raise CompositionError(
                    f"{manifest.harness}: {capability.verb} declares "
                    f"{capability.sink!r}: {exc}") from exc

        schemas = []
        for tool_path in components.get("tools", ()):
            try:
                schemas.append(json.loads(contents[tool_path]))
            except json.JSONDecodeError as exc:
                raise CompositionError(f"tool schema is not JSON: {tool_path}: {exc}") from exc
        schemas = cls._schemas_with_aliases(schemas, pack.translator)

        gene_digests = {
            relative: "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()
            for relative, text in contents.items()
        }
        aliases_file = directory / "aliases.json"
        if aliases_file.is_file():
            gene_digests["aliases.json"] = "sha256:" + hashlib.sha256(
                aliases_file.read_bytes()
            ).hexdigest()

        skill_raw = pack.components_data.get("skill") or pack.components_data.get("skills") or ()
        try:
            skill_cards = tuple(parse_skill_card(card) for card in skill_raw if isinstance(card, Mapping))
        except SkillIndexError as exc:
            raise CompositionError(f"{manifest.harness}: bad skill card: {exc}") from exc

        return Harness(
            harness=manifest.harness,
            frozen=frozen,
            verbs=verbs,
            sinks=sinks,
            risk_of={c.verb: c.risk for c in manifest.capabilities},
            system_core=system_core,
            tool_schemas=tuple(schemas),
            budget=cls._budget(contents[manifest.budget_policy], manifest.budget_policy),
            effect_budget=cls._effect_budget(
                contents[manifest.budget_policy], manifest.budget_policy),
            index_component=next(
                (path for role, paths in manifest.components
                 if role in {"repo_index", "index_component"} for path in paths),
                None),
            evaluators=manifest.evaluators,
            bindings={verb: table[verb] for verb in verbs},
            translator=translator,
            gene_digests=gene_digests,
            skill_cards=skill_cards,
            capability_ceiling=ceiling,
        )


    # -- composition internals -------------------------------------------

    @staticmethod
    def _artifacts(manifest: Any, directory: Path) -> tuple[tuple[ArtifactFile, ...],
                                                            dict[str, str]]:
        """Read every component the manifest names, relative to its own dir."""
        root = directory.parent
        contents: dict[str, str] = {}
        artifacts: list[ArtifactFile] = []
        wanted = [(role, path) for role, paths in manifest.components for path in paths]
        wanted.append(("budget_policy", manifest.budget_policy))
        for role, relative in wanted:
            kind = ROLE_KIND.get(role, role)
            source = root / relative
            if not source.exists():
                source = directory / Path(relative).name
            try:
                text = source.read_text(encoding="utf-8")
            except OSError as exc:
                raise CompositionError(f"component does not resolve: {relative}: {exc}") from exc
            contents[relative] = text
            artifacts.append(ArtifactFile(relative, kind, text))
        return tuple(artifacts), contents

    @staticmethod
    def _schemas_with_aliases(schemas: list[dict[str, Any]], translator: Any) -> list[dict[str, Any]]:
        """Expose pack aliases as extra tool names. Canonical verbs stay bound."""
        aliases = getattr(translator, "to_canonical_map", None) or {}
        by_verb = {str(item.get("verb")): item for item in schemas if item.get("verb")}
        names = {str(item.get("name")) for item in schemas}
        extra: list[dict[str, Any]] = []
        for name, verb in aliases.items():
            if name in names or verb not in by_verb:
                continue
            clone = dict(by_verb[verb])
            clone["name"] = name
            extra.append(clone)
        return schemas + extra

    @staticmethod
    def _effect_budget(raw: str, path: str) -> int:
        """How many effects the policy budgets for one run.

        `F-12`: a policy that declines to bound its effect count gets 1, so the
        first dispatch reserves the whole ceiling and the second is denied.
        An absent bound is not a generous bound.
        """
        try:
            policy = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise CompositionError(f"budget policy is not JSON: {path}: {exc}") from exc
        if "effects" not in policy:
            return 1
        try:
            return max(int(policy["effects"]), 1)
        except (TypeError, ValueError) as exc:
            raise CompositionError(
                f"budget policy effects is not an integer: {path}") from exc

    @staticmethod
    def _budget(raw: str, path: str) -> Mapping[str, int]:
        """Budget ceilings, as `Reservation` dimensions (`CT-06`: int strings)."""
        try:
            policy = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise CompositionError(f"budget policy is not JSON: {path}: {exc}") from exc
        ceilings: dict[str, int] = {"usd_micros": 1_000_000}
        for key, dimension in BUDGET_DIMENSION.items():
            if key in policy:
                try:
                    ceilings[dimension] = int(policy[key])
                except (TypeError, ValueError) as exc:
                    raise CompositionError(
                        f"budget policy {key} is not an integer: {path}") from exc
        return ceilings

