"""The runtime composition root (`REQ-DOG-001`, `ADR-0057`, `ADR-0058`).

The one place in the tree that is allowed to know a concrete implementation
(`01 §2`). Everything below it depends on ports; this module picks which
adapter satisfies each one, and it picks by reading a `HarnessManifest` rather
than by branching.

**Why composition is data and not code.** `ADR-0060` / `M11`: adding a
research, legal or robotics domain must require zero lines changed in
`kernel/` or `agency/episode/`. That invariant is only testable if the thing
that differs between domains is a file. So the manifest supplies the system
prompt, the tool schemas, the capability verbs, each verb's sink class and
risk, the budget ceilings and the evaluator names; `root.py` supplies a
**binding table** from verb to adapter factory and nothing else. A verb the
table cannot satisfy fails at composition, not three turns into a run
(`M9`) — an unwireable harness discovered against a real repository has
already cost the thing composition was supposed to make cheap.

**Where the seams actually are.** Three protocols meet here and none of them
knows about the others:

* `kernel.EffectAdapter` — `name` / `healthy()` / `execute(EffectRequest)`.
* `ports.environment.EnvironmentAdapter` — `observe` / `preview` / `apply`.
* `ports.event_store.EventStorePort` — envelopes, not kernel events.

`_EnvironmentEffect` bridges the first two and `LedgerBridge` the second and
third. Both are adapters between ports, which is composition; neither decides
policy, and neither is a second path to an effect (`AT-01`).

**Approval and resumption.** `K-13`/`K-14`: no lease is held across a
suspension and re-entry is at S1, never at S6. The episode engine is depth-1
and *terminates* on suspension — it has no resume, deliberately, because a
loop that could resume itself past an approval would be a loop that could
decide it had been approved. So resumption lives here: the root takes the
human decision, binds it to the exact descriptor through
`DescriptorBoundApprovalPolicy`, re-dispatches that one request at S1, and
runs the next episode segment. The model is never asked to re-propose what a
human already approved.

**What this module does not do.** It does not grade the episode from inside
the loop. `ICD §3` / `M5`: the verdict comes from the evaluator named by the
manifest (or an injected override), after the episode is terminal, and
`agency` cannot reach it at all. When the instrument cannot self-certify,
the outcome is `inconclusive` — never a substituted fake pass.
"""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from ..adapters.environment.sandboxed import SandboxedEnvironmentAdapter
from ..adapters.evaluators.client import EvaluatorClient
from ..adapters.evaluators.unavailable import UnavailableEvaluator
from ..adapters.sandbox.rootless import RootlessSandboxRunner
from ..adapters.sandbox.worker import WorkerProtocol
from ..adapters.stores.event_store import SqliteEventStore
from ..agency import EpisodeEngine, RunTermination
from ..agency.context import (
    CompetencePriorRecorder,
    CompiledContext,
    ContextCompiler,
    Fragment,
)
from ..agency.manifests.discovery import WorkspaceDiscovery
from ..agency.manifests.loader import ManifestLoader, ManifestLoadError
from .coordination import EpisodeCoordinator
from ..domain.artifacts.graph import ArtifactFile, LogicalEdit, Workspace
from ..domain.artifacts.manifest import (
    FrozenHarness,
    ManifestError,
    compose,
    parse_manifest,
)
from ..domain.ledger.events import EventEnvelope
from ..domain.primitives.primitives import uuidv7
from ..kernel import (
    Constraints,
    EffectRequest,
    Event,
    FailurePath,
    GrantIssuer,
    Governor,
    HeldAuthority,
    Kernel,
    Mode,
    Reservation,
    Scope,
    SinkClass,
    SinkMismatch,
    SinkRegistry,
    StandardClassifier,
    StandardPolicy,
    Trust,
    Span,
)
from ..ports.environment import EffectRequest as EnvironmentRequest
from ..ports.environment import ObservationRequest
from ..ports.evaluator import EvaluationProtocol, RunRef, Verdict
from ..ports.event_store import EventStorePort
from .governance.approvals import (
    ApprovalAuthority,
    ApprovalDecision,
    ApprovalFlow,
    ApprovalFormatError,
    DescriptorBoundApprovalPolicy,
)

__all__ = [
    "DEFAULT_BINDINGS",
    "EVALUATOR_BINDINGS",
    "CompositionError",
    "EffectBinding",
    "Harness",
    "LedgerBridge",
    "Receipt",
    "RunResult",
    "Runtime",
    "TaskContext",
]

#: Manifest component role → artifact kind. The manifest names roles; the
#: artifact graph types them. Declared here because it is the one mapping the
#: two vocabularies do not share, and it is a table rather than a function so
#: that a new role is a row.
ROLE_KIND: Mapping[str, str] = {
    "system_prompt": "system_prompt",
    "tools": "tool_schema",
    "context_policy": "context_policy",
    "routing_policy": "routing_policy",
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

#: Classification for a Phase 0 single-tenant run (`VG-04 §12.1`). Explicit
#: rather than absent: an unlabelled event is not a cheaper event, it is one no
#: retention or trainability rule can be applied to.
CLASSIFICATION: Mapping[str, str] = {
    "schema_version": "vg.4",
    "tenant_id": "tenant-default",
    "owner_id": "owner-platform",
    "confidentiality": "internal",
    "retention_class": "extended",
    "trainability": "prohibited",
    "redaction_status": "none",
}

_FAR_FUTURE = "2099-01-01T00:00:00.000Z"


class CompositionError(RuntimeError):
    """A harness that cannot be wired. Raised while composing, never later."""


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


@dataclass(frozen=True, slots=True)
class Receipt:
    """One effect that actually happened, as the root observed it."""

    verb: str
    descriptor_digest: str
    outcome: str
    detail: str = ""


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


@dataclass(frozen=True, slots=True)
class EffectBinding:
    """Verb → adapter factory. The whole of what `root.py` knows about verbs."""

    factory: Callable[["BindingContext"], Any]
    #: This verb's privileged effects carry a unified diff, so a suspension on
    #: it resolves through the descriptor-bound approval flow (`REQ-APP-001`).
    carries_diff: bool = False


@dataclass(frozen=True, slots=True)
class BindingContext:
    """Everything a factory may see. Deliberately small."""

    verb: str
    environment: Any
    repo_path: Path


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
    evaluators: tuple[str, ...]
    bindings: Mapping[str, EffectBinding]
    translator: Any = None

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


# ---------------------------------------------------------------------------
# Port bridges
# ---------------------------------------------------------------------------


class _EnvironmentEffect:
    """`kernel.EffectAdapter` over an `EnvironmentAdapter` (`ICD §4`).

    One verb, one environment call, no coordination — which is exactly what
    `ports/kernel.py` says an effect adapter is. The `Result` → `AdapterOutcome`
    translation preserves the one distinction the kernel cannot recover later:
    a failure whose occurrence is *undeterminable* stays undeterminable
    (`F-22`), because resolving it either way manufactures evidence.
    """

    def __init__(self, name: str, environment: Any, call: str) -> None:
        self.name = name
        self._environment = environment
        self._call = call

    def healthy(self) -> bool:
        profile = self._environment.profile()
        return bool(profile.ok)

    def execute(self, request: Any) -> Any:
        from ..kernel import AdapterOutcome, Occurrence

        if self._call == "observe":
            result = self._environment.observe(_observation_of(request))
            occurred = Occurrence.OCCURRED
        else:
            result = self._environment.apply(_effect_of(request))
            occurred = Occurrence.OCCURRED if result.ok else Occurrence.UNDETERMINABLE
        if not result.ok:
            error = result.error
            kind = error.kind if error is not None else "instrument_error"
            return AdapterOutcome(
                "denied" if kind == "denied" else "error",
                Occurrence.NOT_OCCURRED if kind in {"denied", "invalid_request", "not_found"}
                else occurred,
                {"usd_micros": 0},
                detail=error.message if error is not None else "",
            )
        value = result.value
        digest = getattr(value, "result_digest", None) or getattr(
            value, "metadata", {}).get("digest") or "sha256:" + "0" * 64
        detail = ""
        if hasattr(value, "content") and value.content is not None:
            detail = str(value.content)
        elif hasattr(value, "matches") and value.matches:
            detail = json.dumps(value.matches)
        elif hasattr(value, "files") and value.files:
            detail = json.dumps(value.files)
        elif hasattr(value, "output") and value.output is not None:
            detail = str(value.output)
        return AdapterOutcome("ok", Occurrence.OCCURRED, {"usd_micros": 1},
                              result_digest=digest, detail=detail)


def _observation_of(request: Any) -> ObservationRequest:
    """A kernel request read as an observation. `fs.read` → `read`."""
    action = request.action.split(".")[-1]
    return ObservationRequest(
        action=action,
        path=request.args.get("path"),
        pattern=request.args.get("pattern"),
        args=dict(request.args),
    )


def _effect_of(request: Any) -> EnvironmentRequest:
    """A kernel request read as an environment effect."""
    diff = request.args.get("diff") or request.args.get("patch")
    argv = request.args.get("argv") or request.args.get("command")
    return EnvironmentRequest(
        verb=request.action,
        action="patch" if diff else ("exec" if argv else "write"),
        args=dict(request.args),
        patch=diff,
        command=tuple(argv) if argv else None,
        idempotency_key=getattr(request, "idempotency_key", None),
    )


class LedgerBridge:
    """`Ledger` + `EventSink` for the kernel, one `EventStorePort` underneath.

    Two roles, one store. A second store is how a trajectory ends up with two
    irreconcilable accounts of the same run. The failure contracts of both
    roles are preserved because the kernel's exits are built on them:
    `append_intent` durably persists or raises (`F-21a` depends on the
    difference), and `emit` never raises (`F-25` is log-not-fail, and the lease
    is already released by the time anything is emitted — `K-06`).
    """

    def __init__(self, store: EventStorePort, *, episode_id: str) -> None:
        self.store = store
        self.events: list[Event] = []
        self._episode_id = episode_id
        self._seq = 0

    def append_intent(self, event: Event) -> None:
        self._remember(event)
        self._write(event, role="intent")

    def emit(self, event: Event) -> None:
        self._remember(event)
        try:
            self._write(event, role="emitted")
        except Exception:
            pass

    def _remember(self, event: Event) -> None:
        """`K-47` writes the intent durably and `S12` publishes the *same*
        object afterwards. Both reach the store — durability and publication
        are different records — but the in-process trace counts the event
        once, or every caller has to know that one kind is doubled.
        """
        if self.events and self.events[-1] is event:
            return
        self.events.append(event)

    def _write(self, event: Event, *, role: str) -> None:
        self._seq += 1
        envelope = EventEnvelope(
            event_id=uuidv7(),
            scope="episode",
            seq=str(self._seq),
            occurred_at=event.at,
            recorded_at=event.at,
            principal=event.principal,
            principal_role="episode",
            run_id=event.run_id,
            episode_id=self._episode_id,
            # `VG-04 §12.1` requires correlation identifiers on read. A run
            # whose events cannot be correlated is a log, not a ledger.
            trace_id=event.run_id or self._episode_id,
            span_id=f"{role}-{self._seq}",
            payload={"kind": event.kind, "reason": event.reason,
                     "alertable": bool(event.alertable), **dict(event.payload)},
            **CLASSIFICATION,
        )
        result = self.store.append([envelope])
        if not result.ok:
            raise OSError(result.error.message if result.error else "append rejected")


class _SystemClock:
    """`CT-08` timestamps. Injected, never read from inside `domain`."""

    def now(self) -> str:
        from datetime import datetime, timezone

        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.") \
            + f"{datetime.now(timezone.utc).microsecond // 1000:03d}Z"


class _WitnessKernel:
    """A pass-through that remembers the request behind each dispatch.

    The suspension path returns a token but not the request it suspended, and
    the approval flow needs the request to bind the descriptor. Recording it
    here keeps `DispatchResult` from growing a field that only one caller
    reads, and adds no path: every call still lands on `Kernel.dispatch`.
    """

    def __init__(self, kernel: Kernel) -> None:
        self.kernel = kernel
        self.calls: list[tuple[EffectRequest, Any]] = []

    def dispatch(self, request: EffectRequest, **kwargs: Any) -> Any:
        result = self.kernel.dispatch(request, **kwargs)
        self.calls.append((request, result))
        return result


class _LayeredOperator:
    """Compiles L1–L5 for each turn and hands the bundle to the real model.

    It wraps the provider rather than changing `EpisodeEngine`, because
    `ADR-0060` prices any edit to `agency/episode/` at the generality
    invariant. The engine keeps handing its own view to `propose`; this
    intercepts it, compiles the layered context around it, and passes the
    provider a `ContextBundle` (`ICD §4`).
    """

    def __init__(self, model: Any, compiler: ContextCompiler, *,
                 recorder: CompetencePriorRecorder | None = None,
                 task: TaskContext) -> None:
        self._model = model
        self._compiler = compiler
        self._recorder = recorder
        self._task = task
        self._dialogue: list[Fragment] = []
        self.contexts: list[Mapping[str, Any]] = []

    def note(self, label: str, source: str, text: str, *, evictable: bool = True) -> None:
        """Admit one turn's outcome to L5. Mid-run additions go to L5, always
        (`VG-03 §10.2`) — anything else destroys the cached prefix."""
        self._dialogue.append(Fragment(source=source, label=label, text=text,
                                       evictable=evictable))

    def propose(self, view: Mapping[str, Any], tools: Sequence[Mapping[str, Any]],
                sampling: Mapping[str, Any]) -> Any:
        compiled: CompiledContext = self._compiler.compile(
            brief=self._task.brief, dialogue=tuple(self._dialogue))
        if self._recorder is not None and self._task.competence_prior is not None:
            # Before turn 1 reaches the provider (`S5-SA-002`). The recorder
            # refuses a second prior for the same episode, so a later segment
            # cannot overwrite a pre-action estimate with a post-evidence one.
            self._recorder.record(
                episode_id=self._task.episode_id, run_id=self._task.run_id,
                principal=self._task.principal, prior=self._task.competence_prior,
                context=compiled)
        # The provider contract is `messages` / digests / layers. The engine's
        # flat view is compiled into L5; it is not a second wire dialect.
        bundle = dict(compiled.bundle())
        self.contexts.append(bundle)
        return self._model.propose(bundle, tools, sampling)


# ---------------------------------------------------------------------------
# The binding table
# ---------------------------------------------------------------------------


def _environment_observer(context: BindingContext) -> Any:
    return _EnvironmentEffect(context.verb, context.environment, "observe")


def _environment_effector(context: BindingContext) -> Any:
    return _EnvironmentEffect(context.verb, context.environment, "apply")


def _sandbox_effector(context: BindingContext) -> Any:
    """Compatibility binding for process verbs on the unified worker.

    The name is retained for manifest/test compatibility; the returned adapter
    is the same environment bridge used by filesystem effects, whose concrete
    worker is rootless Bubblewrap-bound at composition time.
    """
    return _environment_effector(context)


#: Verb → adapter. Adding a capability is a row here plus a manifest line
#: (`01 §2`, open/closed); the dispatcher and the loop never change to
#: accommodate one.
DEFAULT_BINDINGS: Mapping[str, EffectBinding] = {
    "fs.read": EffectBinding(_environment_observer),
    "fs.search": EffectBinding(_environment_observer),
    "fs.write": EffectBinding(_environment_effector),
    "patch.apply": EffectBinding(_environment_effector, carries_diff=True),
    "fs.patch": EffectBinding(_environment_effector, carries_diff=True),
    "proc.exec": EffectBinding(_sandbox_effector),
}

#: Manifest evaluator name → constructor. Unknown names bind nothing.
#: There is no FakeEvaluator row: absence is inconclusive, not a pass (`M5`).
EVALUATOR_BINDINGS: Mapping[str, type] = {
    "coding-oracle@3": EvaluatorClient,
}


# ---------------------------------------------------------------------------
# The root
# ---------------------------------------------------------------------------


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
        try:
            frozen = compose(manifest, workspace.graph, episode_id)
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

        components = dict(manifest.components)
        system_core = "\n".join(contents[p] for p in components.get("system_prompt", ()))
        schemas = []
        for tool_path in components.get("tools", ()):
            try:
                schemas.append(json.loads(contents[tool_path]))
            except json.JSONDecodeError as exc:
                raise CompositionError(f"tool schema is not JSON: {tool_path}: {exc}") from exc

        return Harness(
            harness=manifest.harness,
            frozen=frozen,
            verbs=verbs,
            sinks=sinks,
            risk_of={c.verb: c.risk for c in manifest.capabilities},
            system_core=system_core,
            tool_schemas=tuple(schemas),
            budget=cls._budget(contents[manifest.budget_policy], manifest.budget_policy),
            evaluators=manifest.evaluators,
            bindings={verb: table[verb] for verb in verbs},
            translator=translator,
        )

    # -- the entrypoint --------------------------------------------------

    @classmethod
    def execute_harness(
        cls,
        manifest_path: str | Path,
        task_context: TaskContext,
        interactive: bool = True,
        *,
        model: Any = None,
        approver: Callable[[Any], Any] | None = None,
        verifier: Any = None,
        store: EventStorePort | None = None,
        clock: Any = None,
        bindings: Mapping[str, EffectBinding] | None = None,
        approval_key: bytes | None = None,
        max_segments: int = 8,
    ) -> RunResult:
        """Compose, run one episode, resolve approvals, and evaluate exterior.

        `interactive=False` is `Mode.BENCHMARK` and is **not** "approve
        everything": `K-17` fails approval closed there, because a run that
        blocks for a human has unbounded wall-clock *and* a human contributing
        to the measured outcome.
        """
        harness = cls.compose(manifest_path, episode_id=task_context.episode_id,
                              bindings=bindings)
        repo = Path(task_context.repo_path).resolve()
        if not Path("/usr/bin/bwrap").exists():
            raise CompositionError("rootless Bubblewrap is required for product effects")
        sealed_dir = Path(tempfile.mkdtemp(prefix="vg-sealed-worker-"))
        sealed_bundle = sealed_dir / "bundle"
        sealed_bundle.write_bytes(b"sealed evaluator mount is intentionally unavailable to worker\n")
        worker = WorkerProtocol(RootlessSandboxRunner(repo, evaluator_bundle=sealed_bundle))
        environment = SandboxedEnvironmentAdapter(
            worker, repo, environment_id=f"workspace:{repo}")
        clock = clock or _SystemClock()
        store = store or SqliteEventStore(":memory:")
        ledger = LedgerBridge(store, episode_id=task_context.episode_id)

        if model is None:
            from ..adapters.models.openrouter import OpenRouterModel

            model = OpenRouterModel()

        adapters = {
            verb: harness.bindings[verb].factory(
                BindingContext(verb=verb, environment=environment, repo_path=repo))
            for verb in harness.verbs
        }
        scope = _scope_for(harness, repo)
        classifier = StandardClassifier([
            HeldAuthority(task_context.principal, frozenset(harness.verbs),
                          (_resource_for(repo),), max_depth=4)])
        governor = Governor(harness.budget)
        issuer = GrantIssuer()
        base_policy = StandardPolicy(
            parent_scope=scope,
            mode=Mode.INTERACTIVE if interactive else Mode.BENCHMARK,
            # Every non-`low` capability the manifest declares is descriptor-
            # bound to a human. The threshold is one number and the manifest
            # supplies the risks it applies to.
            approval_required_above="low",
            risk_of=harness.risk_of,
        )

        discovery = WorkspaceDiscovery(repo)
        discovered_env = discovery.render_environment_text()
        base_env = _environment_map(environment, harness)
        env_text = f"{base_env}\n\n{discovered_env}" if discovered_env else base_env

        compiler = ContextCompiler(
            system_core=harness.system_core,
            tool_schemas=harness.tool_schemas,
            environment=env_text,
            token_ceiling=max(harness.budget.get("tokens", 0) or 64_000, 4_096),
        )
        operator = _LayeredOperator(
            model, compiler, task=task_context,
            recorder=CompetencePriorRecorder(clock=clock, events=ledger))

        lam_db = os.environ.get("VANGUARD_LAM_DB", "tools/002_LLM_API_MOCK/lam.sqlite")
        coordinator = None
        budget_tokens = int(harness.budget.get("tokens", 64_000) or 64_000)
        try:
            coordinator = EpisodeCoordinator(lam_db)
            coordinator.open_episode(
                task_id=task_context.brief,
                budget_tokens=budget_tokens,
                episode_id=task_context.episode_id,
            )
        except Exception:
            coordinator = None

        receipts: list[Receipt] = []
        authorization = None
        terminal = RunTermination.ABANDONED
        detail = ""
        # Ed25519 verify keys are injected by the operator. The root never mints
        # a signing authority in-process (`GOV-01`, `ADR-0062`): a missing key can
        # still *issue* a challenge, but it cannot accept or verify a decision.
        can_verify = approval_key is not None
        authority = ApprovalAuthority(approval_key if approval_key is not None else None)
        # The harness names its own patch verb; `VG-05` writes `fs.patch` and
        # `vg-code-default` writes `patch.apply`. The manifest wins.
        flow = ApprovalFlow(authority, patch_verb=harness.diff_verb() or "fs.patch")

        for _ in range(max_segments):
            policy: Any = base_policy
            if authorization is not None:
                policy = DescriptorBoundApprovalPolicy(base_policy, authorization)
            witness = _WitnessKernel(Kernel(
                adapters=adapters, policy=policy, classifier=classifier,
                governor=governor, issuer=issuer, clock=clock, ledger=ledger,
                events=ledger, sinks=harness.sinks))
            engine = EpisodeEngine(
                kernel=witness, model=operator, clock=clock, events=ledger,
                scope=scope, tools=harness.tool_schemas,
                max_turns=task_context.max_turns)
            outcome = engine.run(
                episode_id=task_context.episode_id, run_id=task_context.run_id,
                principal=task_context.principal, brief=task_context.brief,
                spans=(_operator_span(),),
                receipt_labeller=lambda turn, dispatch: _admit_turn_result(
                    operator, turn, dispatch))
            terminal, detail = outcome.terminal, outcome.episode.detail
            suspended = _suspension(witness)
            _record(receipts, operator, witness)
            if suspended is None:
                break
            request, result = suspended
            authorization = _resolve(
                flow, request, result, harness, approver,
                clock=clock, task=task_context, can_verify=can_verify)
            if authorization is None or not authorization.approved:
                break
            # `K-14`: the approved request re-enters at S1, not at S6, and the
            # model is not asked to re-propose what a human already approved.
            approved = _WitnessKernel(Kernel(
                adapters=adapters,
                policy=DescriptorBoundApprovalPolicy(base_policy, authorization),
                classifier=classifier, governor=governor, issuer=issuer,
                clock=clock, ledger=ledger, events=ledger, sinks=harness.sinks))
            approved.dispatch(request, requested_scope=scope,
                              reservation=Reservation(usd_micros=100, millis=1000))
            _record(receipts, operator, approved, admit_context=True)
            authorization = None

        verdict = None
        bound_verifier = verifier if verifier is not None else _evaluator_from_manifest(
            harness, repo)
        if bound_verifier is not None:
            evaluation = bound_verifier.evaluate(
                RunRef(run_id=task_context.run_id, episode_id=task_context.episode_id),
                EvaluationProtocol(name=harness.evaluators[0] if harness.evaluators
                                   else "unnamed"))
            verdict = evaluation.value if evaluation.ok else None

        if coordinator is not None:
            try:
                tokens_used = sum(
                    int(ctx.get("total_tokens", 0)) if isinstance(ctx, dict) else 0
                    for ctx in operator.contexts
                ) or 100
                coordinator.consume(task_context.episode_id, min(tokens_used, budget_tokens))
            except Exception:
                pass

        environment.dispose()
        return RunResult(
            harness=harness.harness,
            composition_digest=harness.composition_digest,
            terminal=terminal,
            receipts=tuple(receipts),
            events=tuple(ledger.events),
            store=store,
            verdict=verdict,
            detail=detail,
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


# ---------------------------------------------------------------------------
# Helpers — each one a translation between two declared vocabularies
# ---------------------------------------------------------------------------


def _resource_for(repo: Path) -> Mapping[str, Any]:
    return {"kind": "fs", "root": str(repo), "paths": [str(repo)]}


def _scope_for(harness: Harness, repo: Path) -> Scope:
    """The authority surface, entirely from the manifest and the repo root."""
    risks = tuple(harness.risk_of.values())
    ceiling = "critical" if "critical" in risks else ("high" if "high" in risks else "medium")
    return Scope(
        actions=frozenset(harness.verbs),
        resources=(_resource_for(repo),),
        constraints=Constraints(
            expires_at=_FAR_FUTURE,
            max_uses=64,
            budget_usd_micros=harness.budget.get("usd_micros", 1_000_000),
            max_bytes=harness.budget.get("bytes", 8_388_608),
            risk_ceiling=ceiling,
            max_depth=4,
            network_policy="deny",
        ),
        depth=0,
    )


def _operator_span() -> Span:
    """The brief is operator-authored, so it may justify capability widening
    (`M4`, `F-09`). Trust is set by source class at construction (`K-30`)."""
    return Span("brief-1", Trust.OPERATOR, "operator_brief")


def _environment_map(environment: Any, harness: Harness) -> str:
    """L3. Stable within a task, so it is read once and never re-read mid-run."""
    profile = environment.profile()
    if not profile.ok or profile.value is None:
        return f"harness={harness.harness}"
    value = profile.value
    return (f"harness={harness.harness} environment={value.environment_id} "
            f"kind={value.kind} root={value.root} "
            f"capabilities={','.join(sorted(harness.verbs))}")


def _admit_turn_result(operator: _LayeredOperator, turn: int, result: Any) -> None:
    """Admit the just-produced tool result before the next model turn.

    EpisodeEngine invokes this callback immediately after every dispatch. The
    result is therefore available to the next proposal in the same episode,
    rather than waiting until an approval suspension or terminal boundary.
    """
    outcome = getattr(result, "outcome", None)
    if outcome is None:
        # Approval suspension is not an observation of an executed effect.
        # Do not let a control-plane challenge advance a workload scenario.
        return None
    detail = getattr(result, "detail", "") or getattr(outcome, "detail", "")
    digest = getattr(outcome, "result_digest", None) or ""
    text = f"tool result turn={turn} digest={digest}"
    if detail:
        text += f"\n{detail}"
    operator.note(label=f"tool-result-{turn}", source="tool_result", text=text)
    return None


def _record(receipts: list[Receipt], operator: _LayeredOperator,
            witness: _WitnessKernel, *, admit_context: bool = False) -> None:
    """Turn dispatch outcomes into root receipts.

    Context admission normally happens at the engine callback so the next
    turn sees the observation. ``admit_context`` remains available for the
    approved dispatch performed between episode segments.
    """
    for request, result in witness.calls:
        if result.failure is not FailurePath.OK or result.outcome is None:
            continue
        outcome_detail = result.detail or getattr(result.outcome, "detail", "")
        receipts.append(Receipt(
            verb=request.action,
            descriptor_digest=result.descriptor_digest or "",
            outcome=result.outcome.status,
            detail=outcome_detail,
        ))
        text = f"{request.action} -> {result.outcome.status} ({result.outcome.result_digest})"
        if outcome_detail:
            text += f"\n{outcome_detail}"
        if admit_context:
            operator.note(
                label=f"{request.action}-{len(receipts)}",
                source=request.action,
                text=text,
            )
    witness.calls.clear()


def _suspension(witness: _WitnessKernel) -> tuple[EffectRequest, Any] | None:
    for request, result in witness.calls:
        if result.failure is FailurePath.APPROVAL_SUSPENDED and result.suspension:
            return request, result
    return None


def _evaluator_from_manifest(harness: Harness, repo: Path) -> Any | None:
    """Bind the manifest's evaluator. Unknown names bind nothing — never a fake."""
    if not harness.evaluators:
        return None
    constructor = EVALUATOR_BINDINGS.get(harness.evaluators[0])
    if constructor is None:
        return None
    if constructor is not EvaluatorClient:
        return UnavailableEvaluator("unsupported_evaluator_binding")
    import base64

    socket_path = os.environ.get("VANGUARD_EVALUATOR_SOCKET")
    image_digest = os.environ.get("VANGUARD_EVALUATOR_IMAGE_DIGEST")
    key_id = os.environ.get("VANGUARD_EVALUATOR_VERDICT_KEY_ID")
    public_key_encoded = os.environ.get("VANGUARD_EVALUATOR_VERDICT_PUBLIC_KEY")
    if not socket_path or not image_digest or not key_id or not public_key_encoded:
        return UnavailableEvaluator("evaluator_peer_unavailable")
    try:
        public_key = base64.b64decode(public_key_encoded, validate=True)
    except Exception:
        return UnavailableEvaluator("evaluator_key_unavailable")
    return constructor(
        socket_path=socket_path,
        expected_uid=10002,
        expected_image_digest=image_digest,
        timeout_seconds=60.0,
        expected_verdict_key_id=key_id,
        expected_verdict_public_key=public_key,
    )


def _resolve(flow: ApprovalFlow,
             request: EffectRequest, result: Any, harness: Harness,
             approver: Callable[[Any], Any] | None, *,
             clock: Any, task: TaskContext, can_verify: bool) -> Any:
    """Put the exact descriptor in front of a human and bind their answer.

    `ADR-0057`: the human approves *this* descriptor. A `None` approver is a
    refusal, not a default-allow — an unattended run that silently approved its
    own privileged effects would make the whole flow decorative.

    The signature is produced *outside* this process (`GOV-01`) and re-verified
    against the request *as it stands at resumption* (`K-15`). A boolean
    callback is not cryptographic authority.
    """
    if approver is None:
        return None
    try:
        challenge = flow.request(request, result.suspension,
                                 process_id=task.episode_id, expires_at=_FAR_FUTURE)
    except ApprovalFormatError:
        return None
    answer = approver(challenge)
    if answer is None or answer is False:
        return None
    if not isinstance(answer, ApprovalDecision) or not can_verify:
        return None
    return flow.verify(challenge, answer, request, now=clock.now())
