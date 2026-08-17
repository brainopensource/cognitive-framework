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
suspension and re-entry is at S1, never at S6. The episode engine *terminates*
on suspension — it has no resume of its own, deliberately, because a loop that
could resume itself past an approval would be a loop that could decide it had
been approved. So resumption lives here: the root takes the human decision,
binds it to the exact descriptor through `DescriptorBoundApprovalPolicy`,
re-dispatches that one request at S1, and re-enters (`S8-A-02`) against a turn
budget read back from the ledger. The model is never asked to re-propose what a
human already approved.

The engine is no longer depth-1: `S8-B-01` gives it `spawn`, so an episode may
run an attenuated child. That is recursion *downward* under a narrowed grant,
which is a different thing from an episode resuming itself past a human.

**What this module does not do.** It does not grade the episode from inside
the loop. `ICD §3` / `M5`: the verdict comes from the evaluator named by the
manifest (or an injected override), after the episode is terminal, and
`agency` cannot reach it at all. When the instrument cannot self-certify,
the outcome is `inconclusive` — never a substituted fake pass.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, ClassVar, Mapping, Sequence

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
from ..domain.artifacts.graph import ArtifactFile, LogicalEdit, Workspace
from ..domain.artifacts.manifest import (
    FrozenHarness,
    ManifestError,
    compose,
    parse_manifest,
)
from ..domain.ledger.events import EventEnvelope
from ..domain.ledger.reducer import compute_state_digest, reconstruct_state
from ..domain.ledger.state import LedgerState
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
from ..ports.determinism import ClockPort, RandomPort
from ..ports.event_store import EventRange, EventStorePort
from .determinism import SystemClock, SystemRandom, event_id
from .telemetry import RunTelemetry
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
    "approval_policy": "approval_policy",
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
    effect_budget: int
    evaluators: tuple[str, ...]
    bindings: Mapping[str, EffectBinding]
    translator: Any = None
    gene_digests: Mapping[str, str] = field(default_factory=dict)

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

    def __init__(self, store: EventStorePort, *, episode_id: str,
                 clock: ClockPort | None = None,
                 random: RandomPort | None = None) -> None:
        # `S8-A-03`: event ids come from the injected pair, never from the
        # process-global RNG and wall clock. A recorded run replays to the
        # same bytes only if the ids do.
        self._clock = clock or SystemClock()
        self._random = random or SystemRandom()
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
            event_id=event_id(clock=self._clock, random=self._random),
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


def _bwrap_path(*, which: Callable[[str], str | None] = shutil.which) -> str:
    """Locate rootless Bubblewrap on PATH.

    `N-06` requires containment, not a particular filesystem layout. Asking for
    an absolute path made composition a claim about one distribution: a host
    with bubblewrap under /nix/store, /usr/local/bin or /opt could not compose
    at all. The refusal names the remedy, because "required" without "install
    this" is a dead end for whoever hits it.
    """

    found = which("bwrap")
    if found is None:
        raise CompositionError(
            "rootless Bubblewrap is required for product effects, and no 'bwrap' "
            "was found on PATH. Install bubblewrap (Debian/Ubuntu: "
            "'apt install bubblewrap'; Fedora: 'dnf install bubblewrap'), or put "
            "an existing bwrap on PATH."
        )
    return found


def _reservation_for(budget: Mapping[str, int], effects: int) -> Reservation:
    """One dispatch's share of the frozen budget policy.

    `K-14` re-enters an approved request at S1, and that re-entry has to hold a
    reservation. Inventing one at the call site meant the manifest's ceilings
    did not govern the single dispatch a human had explicitly authorised.

    The share is the run ceiling divided by the effect count the policy itself
    declares, so a manifest that budgets 128 effects reserves 1/128th per
    dispatch. Reserving the *whole* ceiling would be equally derived and
    equally wrong: it denies the second effect of every run.

    A dimension the policy does not name reserves nothing rather than a guess.
    """

    share = max(int(effects), 1)
    return Reservation(
        usd_micros=int(budget.get("usd_micros", 0) or 0) // share,
        millis=int(budget.get("millis", 0) or 0) // share,
    )


@dataclass(frozen=True, slots=True)
class SessionPorts:
    """Everything a session needs from outside itself.

    Every field is injected, which is the whole point of `S8-A-01`: a session
    built from fakes runs a turn with no live model, no bubblewrap and no
    network, so the control plane is testable without the world.
    """

    model: Any
    environment: Any
    clock: Any
    store: EventStorePort
    #: `S8-A-03`. Pinned by `Recording.seed` on a replay; live when recording.
    random: RandomPort | None = None
    verifier: Any = None
    approver: Callable[[Any], Any] | None = None
    approval_key: bytes | None = None
    interactive: bool = True


class _SwappablePolicy:
    """One policy object whose delegate the session may replace.

    `K-14` binds an approved request to its exact descriptor, which means the
    policy in force changes once a human has decided. The kernel takes its
    policy at construction, so the old code built a second `Kernel` to carry
    the second policy -- and a third for the re-dispatch. Holding the delegate
    here keeps **one kernel per run** without `kernel/` learning anything about
    approvals: it still sees a single object satisfying `authorize`.
    """

    def __init__(self, base: Any) -> None:
        self.base = base
        self._current: Any = base

    def bind(self, authorization: Any | None) -> None:
        self._current = (
            self.base if authorization is None
            else DescriptorBoundApprovalPolicy(self.base, authorization)
        )

    def authorize(self, request: EffectRequest, **kwargs: Any) -> Any:
        return self._current.authorize(request, **kwargs)


class HarnessSession:
    """Wiring for one run. `run()` owns the lifecycle, not the wiring.

    `execute_harness` was 175 lines performing eleven responsibilities and
    building three kernels with identical collaborators, because the segment
    loop was compensating for a missing suspend/resume (`003` A7, `007` D9).
    Construction happens here, once; `run()` reads it.

    The session is also the kernel the engine sees. It forwards every dispatch
    to the one real `Kernel` and remembers the request behind each result,
    because the suspension path returns a token but not the request the
    approval flow needs to bind. That observation used to live in a separate
    pass-through wrapper class; holding it on the session removes the wrapper
    without growing `DispatchResult` a field only one caller reads.
    """

    def __init__(
        self,
        harness: Harness,
        ports: SessionPorts,
        task: TaskContext,
    ) -> None:
        self.harness = harness
        self.ports = ports
        self.task = task
        self.calls: list[tuple[EffectRequest, Any]] = []

        repo = Path(task.repo_path)
        self.repo = repo
        self.ledger = LedgerBridge(
            ports.store, episode_id=task.episode_id,
            clock=ports.clock, random=ports.random)

        self.adapters = {
            verb: harness.bindings[verb].factory(
                BindingContext(verb=verb, environment=ports.environment, repo_path=repo))
            for verb in harness.verbs
        }
        self.scope = _scope_for(harness, repo)
        classifier = StandardClassifier([
            HeldAuthority(task.principal, frozenset(harness.verbs),
                          (_resource_for(repo),), max_depth=4)])
        self.policy = _SwappablePolicy(StandardPolicy(
            parent_scope=self.scope,
            mode=Mode.INTERACTIVE if ports.interactive else Mode.BENCHMARK,
            # Every non-`low` capability the manifest declares is descriptor-
            # bound to a human. The threshold is one number and the manifest
            # supplies the risks it applies to.
            # TODO(S8-B-04): this literal is the last composition value the
            # manifest does not own. It is replaced by the approval-threshold
            # manifest component; Lane B lands that, not this sprint.
            approval_required_above="low",
            risk_of=harness.risk_of,
        ))

        # One kernel per run (`S8-A-01` DoD). Everything that used to vary
        # between the three constructions now varies behind `_SwappablePolicy`.
        self.kernel = Kernel(
            adapters=self.adapters, policy=self.policy, classifier=classifier,
            governor=Governor(harness.budget), issuer=GrantIssuer(),
            clock=ports.clock, ledger=self.ledger, events=self.ledger,
            sinks=harness.sinks)

        discovery = WorkspaceDiscovery(repo)
        discovered_env = discovery.render_environment_text()
        base_env = _environment_map(ports.environment, harness)
        env_text = f"{base_env}\n\n{discovered_env}" if discovered_env else base_env
        compiler = ContextCompiler(
            system_core=harness.system_core,
            tool_schemas=harness.tool_schemas,
            environment=env_text,
            token_ceiling=max(harness.budget.get("tokens", 0) or 64_000, 4_096),
        )
        self.operator = _LayeredOperator(
            ports.model, compiler, task=task,
            recorder=CompetencePriorRecorder(clock=ports.clock, events=self.ledger))

        # Ed25519 verify keys are injected by the operator. The root never mints
        # a signing authority in-process (`GOV-01`, `ADR-0062`): a missing key can
        # still *issue* a challenge, but it cannot accept or verify a decision.
        self.can_verify = ports.approval_key is not None
        self.flow = ApprovalFlow(
            ApprovalAuthority(ports.approval_key),
            # The harness names its own patch verb; `VG-05` writes `fs.patch`
            # and `vg-code-default` writes `patch.apply`. The manifest wins.
            patch_verb=harness.diff_verb() or "fs.patch")

    # -- the ledger is the only memory ------------------------------------

    def ledger_state(self) -> LedgerState:
        """Reduce this episode's events. Nothing in memory contributes.

        `A-07`: everything is an event and every surface is a projection of
        it. `domain/ledger/reducer.py` already reconstructs episode state for
        crash recovery -- approval suspension is the same mechanism with a
        different trigger, so this is a reuse, not new machinery.
        """
        read = self.ports.store.read(EventRange(episode_id=self.task.episode_id))
        envelopes = read.value if read.ok and read.value is not None else ()
        return reconstruct_state(envelopes)

    def turns_consumed(self) -> int:
        """Turns this episode has already spent, counted from the ledger.

        One `ProposalProduced` per turn. Reading it here rather than from
        `_LayeredOperator._dialogue` is what makes re-entry a resume: no live
        object has to survive the approval boundary for the bound to hold.
        """
        return len(self.ledger_state().proposals)

    def state_digest(self) -> str:
        """`T3.6`. The digest a resumed run must reproduce from events alone."""
        return compute_state_digest(self.ledger_state())

    # -- the kernel seam --------------------------------------------------

    def dispatch(self, request: EffectRequest, **kwargs: Any) -> Any:
        """Forward to the one kernel, remembering the request behind the result."""
        result = self.kernel.dispatch(request, **kwargs)
        self.calls.append((request, result))
        return result

    # -- the lifecycle ----------------------------------------------------

    def run(self) -> RunResult:
        """Run the episode, resolve approvals, evaluate from outside."""
        harness, task, ports = self.harness, self.task, self.ports
        receipts: list[Receipt] = []
        authorization = None
        terminal = RunTermination.ABANDONED
        detail = ""

        # `S8-A-02`. This used to be a bounded segment loop building a fresh
        # `Episode` each pass with a fresh `max_turns` -- so the real bound was
        # the product of the two limits (8x8=64), nothing stated it, and an
        # agreeable reviewer bought the run another eight turns per approval.
        # Re-entry is now driven by the ledger: `max_turns` bounds the episode,
        # not each segment of it, and an exhausted budget is terminal.
        while True:
            remaining = task.max_turns - self.turns_consumed()
            if remaining <= 0:
                terminal = RunTermination.ABANDONED
                detail = f"max_turns ({task.max_turns}) exhausted across approval"
                break
            self.policy.bind(authorization)
            engine = EpisodeEngine(
                kernel=self, model=self.operator, clock=ports.clock,
                events=self.ledger, scope=self.scope, tools=harness.tool_schemas,
                max_turns=remaining)
            outcome = engine.run(
                episode_id=task.episode_id, run_id=task.run_id,
                principal=task.principal, brief=task.brief,
                spans=(_operator_span(),),
                receipt_labeller=lambda turn, dispatch: _admit_turn_result(
                    self.operator, turn, dispatch))
            terminal, detail = outcome.terminal, outcome.episode.detail
            suspended = _suspension(self.calls)
            _record(receipts, self.operator, self.calls)
            if suspended is None:
                break
            request, result = suspended
            authorization = _resolve(
                self.flow, request, result, harness, ports.approver,
                clock=ports.clock, task=task, can_verify=self.can_verify)
            if authorization is None or not authorization.approved:
                break
            # `K-14`: the approved request re-enters at S1, not at S6, and the
            # model is not asked to re-propose what a human already approved.
            self.policy.bind(authorization)
            self.dispatch(request, requested_scope=self.scope,
                          reservation=_reservation_for(harness.budget,
                                                       harness.effect_budget))
            _record(receipts, self.operator, self.calls, admit_context=True)
            authorization = None

        verdict = self._evaluate()
        ports.environment.dispose()
        return RunResult(
            harness=harness.harness,
            composition_digest=harness.composition_digest,
            terminal=terminal,
            receipts=tuple(receipts),
            events=tuple(self.ledger.events),
            store=ports.store,
            verdict=verdict,
            detail=detail,
            gene_digests=dict(harness.gene_digests),
            telemetry=self._telemetry(),
            instrument_error=self._instrument_error(),
            state_digest=self.state_digest(),
        )

    # -- what the instrument reads ----------------------------------------

    def _telemetry(self) -> RunTelemetry:
        """Integer telemetry, with absence preserved (`S9-A-02`).

        A provider that reported no usage did not report zero usage. Summing
        `.get(key, 0)` across contexts would turn a silent provider into a free
        run, and a corpus of free runs is how a cost claim becomes fiction.
        """
        prompt: int | None = None
        completion: int | None = None
        for context in self.operator.contexts:
            if not isinstance(context, Mapping):
                continue
            for key, current in (("prompt_tokens", prompt),
                                 ("completion_tokens", completion)):
                reported = context.get(key)
                if isinstance(reported, bool) or not isinstance(reported, int):
                    continue
                if key == "prompt_tokens":
                    prompt = reported if current is None else current + reported
                else:
                    completion = reported if current is None else current + reported
        return RunTelemetry(
            turns=self.turns_consumed(),
            prompt_tokens=prompt,
            completion_tokens=completion,
        )

    def _instrument_error(self) -> str | None:
        """Why this arm produced no usable measurement, or `None`.

        `None` means the instrument worked. It does not mean the run
        succeeded -- a refused run is a result, an unmeasured one is not.
        """
        if self.turns_consumed() == 0:
            # No proposal ever reached the ledger: the provider did not answer.
            # `S7-C-02` calls this `model_not_invoked`, and it is an
            # instrument failure, not a cheap run.
            return "model_not_invoked"
        return None

    def _evaluate(self) -> Any:
        """`ICD 3` / `M5`: the verdict comes from outside the episode."""
        bound = self.ports.verifier
        if bound is None:
            bound = _evaluator_from_manifest(self.harness, self.repo)
        if bound is None:
            return None
        evaluation = bound.evaluate(
            RunRef(run_id=self.task.run_id, episode_id=self.task.episode_id),
            EvaluationProtocol(
                name=self.harness.evaluators[0] if self.harness.evaluators else "unnamed"))
        return evaluation.value if evaluation.ok else None


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
            evaluators=manifest.evaluators,
            bindings={verb: table[verb] for verb in verbs},
            translator=translator,
            gene_digests=gene_digests,
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

        # Runtime phase. Composition has already succeeded; a host without
        # bubblewrap is a failure of *this* run, not of the harness, so the
        # probe lives here and not behind `compose`.
        bwrap = _bwrap_path()
        sealed_dir = Path(tempfile.mkdtemp(prefix="vg-sealed-worker-"))
        sealed_bundle = sealed_dir / "bundle"
        sealed_bundle.write_bytes(b"sealed evaluator mount is intentionally unavailable to worker\n")
        worker = WorkerProtocol(
            RootlessSandboxRunner(repo, evaluator_bundle=sealed_bundle, runtime=bwrap))
        environment = SandboxedEnvironmentAdapter(
            worker, repo, environment_id=f"workspace:{repo}")

        if model is None:
            from ..adapters.models.openrouter import OpenRouterModel

            model = OpenRouterModel()

        ports = SessionPorts(
            model=model,
            environment=environment,
            clock=clock or SystemClock(),
            store=store or SqliteEventStore(":memory:"),
            verifier=verifier,
            approver=approver,
            approval_key=approval_key,
            interactive=interactive,
        )
        return HarnessSession(harness, ports, task_context).run()

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
            calls: list[tuple[EffectRequest, Any]], *,
            admit_context: bool = False) -> None:
    """Turn dispatch outcomes into root receipts.

    Context admission normally happens at the engine callback so the next
    turn sees the observation. ``admit_context`` remains available for the
    approved dispatch performed between episode segments.
    """
    for request, result in calls:
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
    calls.clear()


def _suspension(calls: list[tuple[EffectRequest, Any]]) -> tuple[EffectRequest, Any] | None:
    for request, result in calls:
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
