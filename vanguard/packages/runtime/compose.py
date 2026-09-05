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
from ..agency.manifests.loader import AliasTranslator, ManifestLoader
from ..domain.artifacts.graph import ArtifactFile, GraphError, LogicalEdit, Workspace
from ..domain.artifacts.skill_index import SkillCard, SkillIndexError, parse_skill_card
from ..domain.artifacts.manifest import (
    FrozenComposition,
    ManifestError,
    artifact_kind_for,
    freeze_composition,
    read_canonical_manifest,
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
from .wiring import (
    BindingContext,
    BindingResolver,
    CompositionError,
    DEFAULT_BINDINGS,
    EffectBinding,
    default_resolver,
)

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

#: Structural ceilings declared on the policy. They appear on
#: ``EpisodeStarted.budgetCeiling`` and MUST NOT enter ``Governor``.
STRUCTURAL_BUDGET_DIMENSION: Mapping[str, str] = {
    "turns": "turns",
    "depth": "depth",
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
    #: Immutable preregistration values supplied by the trust lane.  Runtime
    #: treats this as a wire mapping and never imports its implementation.
    preregistration: Mapping[str, Any] | None = None
    #: Ancestor chain, root first. Empty means "this episode is the root", and
    #: the session substitutes `(episode_id,)`. Carried explicitly so a cold
    #: reader can rebuild the tree without a live parent object (`RF-59`).
    lineage: tuple[str, ...] = ()
    #: Optional authority-free M-7 topology routing data.
    topology: Mapping[str, Any] | None = None
    #: Runtime-only attenuated child scope.  Public callers leave this unset;
    #: the child runner supplies it after Kernel attenuation.
    scope_override: Any = None
    #: Authority-free references admitted by a mediated topology edge.
    artifact_refs: tuple[Mapping[str, str], ...] = ()
    #: Reconstructed semantic state supplied only on cold continuation.
    resume_state: Mapping[str, Any] | None = None


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
    run_digest: str = ""
    activation_digest: str = ""
    foundation_evidence: Any = None

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
    frozen: FrozenComposition
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
    #: `ADR-0106 §4`. Tool-policy preset intent declared by the manifest via
    #: an optional `tool-policy.json` (`{"mode": "phased", "preset": "code"}`).
    #: `None` keeps the episode loop ungated: presets declare intent, never
    #: inferred by the runtime (`ADR-0060`).
    tool_policy_preset: str | None = None

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
        resolver: BindingResolver | None = None,
    ) -> Harness:
        """Freeze one harness. Every failure here is a failure *before* a run.

        This is the one public composition path (`ADR-0088 §1`). Bytes are
        normalized to a `CanonicalManifest` before any semantic validation, so
        the dialect a pack happens to be written in stops at ingress and never
        becomes an execution value.
        """
        path = cls._manifest_file(manifest_path)
        directory = path.parent
        try:
            content_text = path.read_text(encoding="utf-8")
            if path.suffix.lower() in {".yaml", ".yml"}:
                import yaml
                raw = yaml.safe_load(content_text)
            else:
                try:
                    raw = json.loads(content_text)
                except json.JSONDecodeError:
                    import yaml
                    raw = yaml.safe_load(content_text)
        except OSError as exc:
            raise CompositionError(f"manifest does not load: {path}: {exc}") from exc
        except Exception as exc:
            raise CompositionError(f"manifest does not load: {path}: {exc}") from exc

        try:
            canonical = read_canonical_manifest(raw)
        except ManifestError as exc:
            raise CompositionError(f"{path.name}: {exc}") from exc

        artifacts, contents = cls._artifacts(canonical, directory)
        workspace = Workspace.empty().apply(
            LogicalEdit(f"compose {canonical.manifest_id}", artifacts))

        system_core = cls._role_text(canonical, contents, "system_prompt") or (
            contents.get(canonical.system_prompt or "", ""))
        approval_policy = cls._role_text(canonical, contents, "approval_policy") or (
            contents.get(canonical.approval_policy or "", ""))
        model_routes = cls._role_texts(canonical, contents, "routing_policy") + tuple(
            contents[ref] for ref in canonical.model_routes if ref in contents)

        try:
            frozen = freeze_composition(
                canonical, workspace.graph, episode_id,
                identity={
                    "systemPrompt": system_core,
                    "approvalPolicy": approval_policy,
                    "modelRoutes": model_routes,
                },
            )
        except (ManifestError, GraphError) as exc:
            raise CompositionError(str(exc)) from exc

        verbs = canonical.verbs
        # An explicitly supplied table is the *whole* table: a caller that names
        # its bindings is stating the complete wiring, so provider fallback
        # would silently widen it. Only the default path consults providers.
        if resolver is None:
            resolver = (BindingResolver(dict(bindings), ()) if bindings is not None
                        else default_resolver())
        table = resolver.resolve_all(verbs, harness=canonical.manifest_id)

        sinks = SinkRegistry()
        for capability in canonical.capabilities:
            try:
                sinks.register(capability.verb, SinkClass(capability.sink))
            except (SinkMismatch, ValueError) as exc:
                raise CompositionError(
                    f"{canonical.manifest_id}: {capability.verb} declares "
                    f"{capability.sink!r}: {exc}") from exc

        translator = cls._translator(canonical, directory)
        schemas = cls._tool_schemas(canonical, contents, translator)
        skill_cards = cls._skill_cards(canonical, contents)

        gene_digests = {
            relative: "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()
            for relative, text in contents.items()
        }
        aliases_file = directory / "aliases.json"
        if aliases_file.is_file():
            gene_digests["aliases.json"] = "sha256:" + hashlib.sha256(
                aliases_file.read_bytes()).hexdigest()

        return Harness(
            harness=canonical.manifest_id,
            frozen=frozen,
            verbs=verbs,
            sinks=sinks,
            risk_of={item.verb: item.risk for item in canonical.capabilities},
            system_core=system_core,
            tool_schemas=tuple(schemas),
            budget=cls._budget(frozen.budget),
            effect_budget=cls._effect_budget(frozen.budget),
            index_component=next(
                (component.implementation for component in canonical.components
                 if cls._role_of(component.name) in {"repo_index", "index_component"}),
                None),
            evaluators=canonical.evaluators,
            bindings=table,
            translator=translator,
            gene_digests=gene_digests,
            skill_cards=skill_cards,
            capability_ceiling=canonical.ceiling,
            tool_policy_preset=cls._tool_policy_preset(directory),
        )

    # -- composition internals -------------------------------------------

    @staticmethod
    def _tool_policy_preset(directory: Path) -> str | None:
        """Read the optional manifest-level tool-policy declaration.

        Absent, malformed, or non-phased declarations all compose to `None`:
        the ungated generic loop. Only an explicit `{"mode": "phased"}`
        declaration opts a preset into the state-dependent phase ladder.
        """
        declaration = directory / "tool-policy.json"
        if not declaration.is_file():
            return None
        try:
            declared = json.loads(declaration.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None
        if not isinstance(declared, Mapping):
            return None
        if declared.get("mode") != "phased":
            return None
        preset = declared.get("preset")
        return str(preset) if preset else None

    @staticmethod
    def _manifest_file(manifest_path: str | Path) -> Path:
        """Locate a pack's manifest by path or by registered pack name.

        Pack *location* is an asset service, not manifest authority: the loader
        is asked where a pack lives and nothing else.
        """
        path = Path(manifest_path)
        if not path.is_absolute() and not path.exists():
            candidate = ManifestLoader().base_dir / path
            if candidate.exists():
                path = candidate
        if path.is_dir():
            for candidate in ("manifest.json", "manifest.yaml", "manifest.yml", "harness.yaml", "harness.json"):
                if (path / candidate).is_file():
                    path = path / candidate
                    break
            else:
                path = path / "manifest.json"
        return path

    @staticmethod
    def _role_of(name: str) -> str:
        """The role a canonical component name carries.

        Compatibility ingress names a component after the `/1` role it came
        from, suffixing only when a role carried several artifacts, so the role
        is the name up to the first positional suffix.
        """
        head, _, tail = name.rpartition(".")
        return head if head and tail.isdigit() else name

    @classmethod
    def _components_for(cls, canonical: Any, role: str) -> tuple[Any, ...]:
        return tuple(component for component in canonical.components
                     if cls._role_of(component.name) == role)

    @classmethod
    def _role_texts(cls, canonical: Any, contents: Mapping[str, str],
                    role: str) -> tuple[str, ...]:
        return tuple(contents[component.implementation]
                     for component in cls._components_for(canonical, role)
                     if component.implementation in contents)

    @classmethod
    def _role_text(cls, canonical: Any, contents: Mapping[str, str], role: str) -> str:
        return "\n".join(cls._role_texts(canonical, contents, role))

    @staticmethod
    def _artifacts(canonical: Any, directory: Path) -> tuple[tuple[ArtifactFile, ...],
                                                             dict[str, str]]:
        """Read every artifact the canonical manifest names, and only those.

        A file the manifest does not name is not a composition input and must
        not reach `D_H`. Kinds come from the component's SPI interface rather
        than from a dialect's role vocabulary, so identical bytes carry an
        identical artifact digest whichever dialect named them.
        """
        directory = directory.resolve()
        root = directory.parent
        wanted: list[tuple[str, str]] = []
        for component in canonical.components:
            kind = artifact_kind_for(component)
            wanted.append((component.implementation, kind))
            if isinstance(component.config, str):
                wanted.append((component.config, kind))
        if isinstance(canonical.budget_policy, str):
            wanted.append((canonical.budget_policy, "budget_policy"))
        if canonical.system_prompt:
            wanted.append((canonical.system_prompt, "system_prompt"))
        if canonical.approval_policy:
            wanted.append((canonical.approval_policy, "approval_policy"))
        for ref in canonical.model_routes:
            wanted.append((ref, "routing_policy"))

        contents: dict[str, str] = {}
        artifacts: list[ArtifactFile] = []
        for relative, kind in wanted:
            if relative in contents:
                continue
            source = root / relative
            if not source.exists():
                source = directory / Path(relative).name
            try:
                text = source.read_text(encoding="utf-8")
            except OSError as exc:
                raise CompositionError(
                    f"component does not resolve: {relative}: {exc}") from exc
            contents[relative] = text
            artifacts.append(ArtifactFile(relative, kind, text))
        return tuple(artifacts), contents

    @classmethod
    def _translator(cls, canonical: Any, directory: Path) -> AliasTranslator:
        """Pack aliases, fail-closed against the declared capability verbs."""
        declared = set(canonical.verbs)
        aliases_file = directory / "aliases.json"
        if not aliases_file.is_file():
            identity = {verb: verb for verb in declared}
            return AliasTranslator(identity, identity)
        try:
            translator = AliasTranslator.from_dict(json.loads(
                aliases_file.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            raise CompositionError(f"aliases do not load: {aliases_file}: {exc}") from exc
        for alias, verb in translator.to_canonical_map.items():
            if verb not in declared:
                raise CompositionError(
                    f"{canonical.manifest_id}: alias {alias!r} targets {verb!r}, which is "
                    f"not a declared capability verb: {sorted(declared)}")
        return translator

    @classmethod
    def _tool_schemas(cls, canonical: Any, contents: Mapping[str, str],
                      translator: Any) -> list[dict[str, Any]]:
        schemas: list[dict[str, Any]] = []
        selectors = {
            c.verb: c.selector
            for c in getattr(canonical, "capabilities", ())
            if getattr(c, "selector", None) is not None
        }
        for component in cls._components_for(canonical, "tools"):
            text = contents.get(component.implementation)
            if text is None:
                continue
            try:
                schema_dict = json.loads(text)
                verb = schema_dict.get("verb")
                if verb and verb in selectors and "selector" not in schema_dict:
                    schema_dict["selector"] = selectors[verb]
                schemas.append(schema_dict)
            except json.JSONDecodeError as exc:
                raise CompositionError(
                    f"tool schema is not JSON: {component.implementation}: {exc}") from exc
        return cls._schemas_with_aliases(schemas, translator)

    @classmethod
    def _skill_cards(cls, canonical: Any, contents: Mapping[str, str]) -> tuple[SkillCard, ...]:
        cards: list[SkillCard] = []
        for role in ("skill", "skills"):
            for component in cls._components_for(canonical, role):
                text = contents.get(component.implementation)
                if text is None:
                    continue
                try:
                    cards.append(parse_skill_card(json.loads(text)))
                except (json.JSONDecodeError, SkillIndexError) as exc:
                    raise CompositionError(
                        f"{canonical.manifest_id}: bad skill card: {exc}") from exc
        return tuple(cards)

    @staticmethod
    def _schemas_with_aliases(schemas: list[dict[str, Any]], translator: Any) -> list[dict[str, Any]]:
        """Return one outbound schema per canonical tool.

        Aliases are an inbound compatibility concern.  Advertising every
        alias as a second schema duplicates tools in provider requests and
        lets provider selection change the wire surface.  The translator is
        still attached to the loaded pack, so legacy model responses continue
        to resolve through ``ProposalTranslator``.
        """
        del translator
        unique: list[dict[str, Any]] = []
        seen: set[str] = set()
        for schema in schemas:
            identity = str(schema.get("verb") or schema.get("name") or "")
            if identity and identity in seen:
                continue
            if identity:
                seen.add(identity)
            unique.append(schema)
        return unique

    @staticmethod
    def _policy(policy: Mapping[str, Any] | str, path: str = "budget policy") -> Mapping[str, Any]:
        """A budget policy as a mapping, whether it arrived parsed or as bytes."""
        if isinstance(policy, str):
            try:
                policy = json.loads(policy)
            except json.JSONDecodeError as exc:
                raise CompositionError(f"budget policy is not JSON: {path}: {exc}") from exc
        if not isinstance(policy, Mapping):
            raise CompositionError(f"budget policy must be an object: {path}")
        return policy

    @classmethod
    def _effect_budget(cls, policy: Mapping[str, Any] | str, path: str = "budget policy") -> int:
        """How many effects the policy budgets for one run.

        `F-12`: a policy that declines to bound its effect count gets 1, so the
        first dispatch reserves the whole ceiling and the second is denied.
        An absent bound is not a generous bound.
        """
        policy = cls._policy(policy, path)
        if "effects" not in policy:
            return 1
        try:
            return max(int(policy["effects"]), 1)
        except (TypeError, ValueError) as exc:
            raise CompositionError("budget policy effects is not an integer") from exc

    @classmethod
    def _budget(cls, policy: Mapping[str, Any] | str,
                path: str = "budget policy") -> Mapping[str, int]:
        """Budget ceilings, as `Reservation` dimensions (`CT-06`: int strings).

        Additive keys feed the governor. Structural keys (`turns`, `depth`)
        are copied onto the harness so the ledger can name the declared
        catalog without summing them as reservations.
        """
        policy = cls._policy(policy, path)
        ceilings: dict[str, int] = {"usd_micros": 1_000_000}
        for key, dimension in {**BUDGET_DIMENSION, **STRUCTURAL_BUDGET_DIMENSION}.items():
            if key in policy:
                try:
                    ceilings[dimension] = int(policy[key])
                except (TypeError, ValueError) as exc:
                    raise CompositionError(
                        f"budget policy {key} is not an integer") from exc
        return ceilings
