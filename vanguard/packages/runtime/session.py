"""One run: session wiring and lifecycle (`2.2-C`).

`HarnessSession` is the one kernel the engine sees for a run. It does not
compose a harness and it does not write envelopes except through
`LedgerEmitter`.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from ..adapters.stores.repo_index import FileRepoIndex
from ..agency import EpisodeEngine, RunTermination
from ..agency.episode import ProtocolRecoveryState
from ..agency.episode.admission_gate import AdmissionGate, AdmissionVerdict, VerificationReceipt
from ..agency.context import (
    CompetencePriorRecorder,
    CompiledContext,
    ContextCompiler,
    Fragment,
    build_context_packet,
)
from ..agency.manifests.discovery import WorkspaceDiscovery
from ..agency.provenance import NullProvenanceSink, ProvenanceSink
from ..domain.canonicalisation.digest import digest_of
from ..domain.ledger.agent_view import AgentView, fold_agent_view
from ..domain.ledger.progress import ConfidenceRecord, ProgressView, fold_progress
from ..domain.ledger.reducer import compute_state_digest, reconstruct_state
from ..domain.ledger.state import LedgerState
from ..kernel import (
    EffectRequest,
    AdapterOutcome,
    DispatchResult,
    Event,
    FailurePath,
    GrantIssuer,
    Governor,
    HeldAuthority,
    Kernel,
    Mode,
    Occurrence,
    StandardClassifier,
    StandardPolicy,
    Span,
)
from ..ports.blob_store import BlobStorePort
from ..ports.child_runtime import ChildRuntimePort
from ..ports.determinism import RandomPort
from ..ports.evaluator import EvaluationProtocol, RunRef, Verdict
from ..ports.event_store import EventRange, EventStorePort, Result
from ..ports.index import IndexPort
from ..ports.meta_controller import MetaController
from ..ports.memory import MemoryBinding, require_retrieval_provenance
from ..ports.spi import ICompletionPolicy
from .compose import (
    Harness,
    Receipt,
    RunResult,
    TaskContext,
)
from .artifacts import ArtifactWriter, CapturePolicy, resolve_capture_policy
from .budget_view import ADDITIVE_DIMENSIONS, remaining_budget
from .checkpoints import Checkpoint, CheckpointManager, Reconstruction
from .evaluator_gateway import record_verdict
from .ledger.recovery import RecoveryScanner
from .ledger_emitter import LedgerEmitter
from .meta_controller import ControllerProposal, guarded_consult
from .provenance import RuntimeProvenanceSink, cache_participation
from .evidence_capture import capture_evidence as _capture_evidence_pure
from .prompt_assembler import PromptAssembler
from .protocol_pipeline import default_protocol_pipeline
from .response_handler import ResponseHandler
from .telemetry import RunTelemetry, compute_run_telemetry, instrument_error as _telemetry_instrument_error
from .trajectory import DelayedTerminalEmitter, assemble_trajectory
from .governance.approvals import (
    ApprovalAuthority,
    ApprovalDecision,
    ApprovalFlow,
    ApprovalFormatError,
    DescriptorBoundApprovalPolicy,
)
from .wiring import (
    BindingContext,
    CompositionError,
    _FAR_FUTURE,
    _ceiling_resources,
    _environment_map,
    _evaluator_from_manifest,
    _operator_span,
    _reservation_for,
    _scope_for,
    _span_for,
)


#: Harnesses whose terminal ``finish`` must pass the pack completion policy
#: (W-092-2: completion admitted only by fresh applicable verification).
#: ``vg-code-default`` is deliberately NOT gated: closed M-2 acceptance
#: falsifiers (e.g. RF-25 cold continuation) compose bare finishes through it,
#: and gating it would reopen frozen milestone evidence.  Widening or shrinking
#: this set is a governance decision to be recorded in
#: ``docs/execution/active.md`` -- it is pinned by
#: ``test/falsifiers/test_completion_gate_scope.py``, never changed silently.
ADMISSION_GATED_HARNESSES = frozenset(
    {"vg-code-fast", "vg-code-balanced", "vg-code-max", "vg-code-max-v2",
     "vg-code-max-v2b", "vg-code-max-v3", "vg-herbs", "vg-chimera-v1", "vg-code-chimera"})

#: Presets deliberately exempt from capability-derived gating. Only shrinks.
ADMISSION_GATE_EXEMPT = frozenset({"vg-code-default"})


def admission_required(harness: Any) -> bool:
    """Gate completion by declared capability, not by preset name.

    A name allowlist meant every new preset shipped ungated until someone
    remembered to edit the set, so a bare `finish` with zero effects scored as
    a completed run. Any harness granted `patch.apply` has a completion claim
    that must be admitted against real evidence.
    """
    name = getattr(harness, "harness", "")
    if name in ADMISSION_GATE_EXEMPT:
        return False
    return "patch.apply" in set(getattr(harness, "verbs", ()) or ())

_CONTROLLER_BUDGET_KEYS: Mapping[str, str] = {
    "usd_micros": "usd_micros",
    "usdMicros": "usd_micros",
    "millis": "millis",
    "tokens": "tokens",
    "bytes": "bytes",
}


def _memory_now(clock: Any) -> datetime:
    value = clock.now() if hasattr(clock, "now") else clock
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc)
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
        except ValueError as exc:
            raise PermissionError("memory authorization clock is invalid") from exc
    raise PermissionError("memory authorization clock is unavailable")


def _lower_controller_directive(
    proposal: ControllerProposal,
) -> Mapping[str, Any] | None:
    """Map direct strategy decisions onto existing episode proposals.

    Advisory directives return ``None`` and enter L5 before the provider is
    called. ``conclude`` follows the ordinary terminal proposal path, while
    ``delegate`` becomes the already-mediated M-6 effect. This function grants
    no authority and does not inspect capabilities; the Kernel still decides.
    """
    if proposal.kind == "conclude":
        return {"kind": "finish", "note": str(proposal.payload["reason"])}
    if proposal.kind != "delegate":
        return None

    scope = dict(proposal.payload.get("scope") or {})
    resource = scope.pop(
        "resource", {"kind": "generic", "uriPattern": "agent://spawn/*"})
    budget: dict[str, int] = {}
    for source, target in _CONTROLLER_BUDGET_KEYS.items():
        amount = scope.pop(source, None)
        if isinstance(amount, int) and not isinstance(amount, bool) and amount >= 0:
            budget[target] = amount
    args: dict[str, Any] = {
        "brief": str(proposal.payload["brief"]),
        **scope,
    }
    if budget:
        args["budget"] = budget
    return {
        "kind": "effect",
        "action": "agent.spawn",
        "resource": dict(resource) if isinstance(resource, Mapping) else {},
        "args": args,
        "reservation": budget,
        "note": str(proposal.payload["reason"]),
    }


def _controller_trigger(proposal: ControllerProposal) -> str:
    """Bind the closed StrategyChanged payload to confidence by digest."""
    refs = ",".join(str(item) for item in proposal.attribution["confidenceRefs"])
    return (
        f"directive={proposal.kind};"
        f"reason={proposal.attribution['reasonDigest']};"
        f"input={proposal.attribution['inputDigest']};"
        f"confidence={refs}"
    )


class _LayeredOperator:
    """Compiles L1–L5 for each turn and hands the bundle to the real model.

    Delegates prompt construction to PromptAssembler (EVO-05) and response
    parsing/telemetry normalization to ResponseHandler (EVO-06).
    """

    def __init__(
        self,
        model: Any,
        compiler: ContextCompiler,
        *,
        recorder: CompetencePriorRecorder | None = None,
        task: TaskContext,
        clock: Any,
        artifacts: ArtifactWriter | None = None,
        provenance: ProvenanceSink | None = None,
        meta_controller: Callable[[], ControllerProposal | None] | None = None,
        memory: MemoryBinding | None = None,
        capabilities: Sequence[Mapping[str, Any]] = (),
    ) -> None:
        self._model = model
        configure_capabilities = getattr(model, "configure_capabilities", None)
        if callable(configure_capabilities):
            configure_capabilities(tuple(
                dict(item) for item in capabilities if isinstance(item, Mapping)))
        self._assembler = PromptAssembler(
            compiler=compiler,
            task=task,
            clock=clock,
            recorder=recorder,
            provenance=provenance,
            memory=memory,
        )
        self._handler = ResponseHandler(
            model=model,
            provenance=provenance,
            artifacts=artifacts,
        )
        self.contexts: list[Mapping[str, Any]] = []
        self._artifacts = artifacts
        self._meta_controller = meta_controller

    @property
    def _compiler(self) -> ContextCompiler:
        return self._assembler.compiler

    def note(self, label: str, source: str, text: str, *, evictable: bool = True) -> None:
        """Admit one turn's outcome to L5. Mid-run additions go to L5, always
        (`VG-03 §10.2`) — anything else destroys the cached prefix."""
        self._assembler.note(label=label, source=source, text=text, evictable=evictable)

    def propose(
        self,
        view: Mapping[str, Any],
        tools: Sequence[Mapping[str, Any]],
        sampling: Mapping[str, Any],
    ) -> Any:
        directive = self._meta_controller() if self._meta_controller is not None else None
        if directive is not None:
            lowered = _lower_controller_directive(directive)
            if lowered is not None:
                # Keep turns aligned without claiming the policy decision was
                # a provider invocation. Trajectory assembly recognises this
                # marker and reports an empty invocation list and zero cost.
                self.contexts.append({
                    "proposal_source": "meta_controller",
                    "controller_id": directive.attribution["controllerId"],
                    "directive_kind": directive.kind,
                    "controller_input_digest": directive.attribution["inputDigest"],
                    "confidence_refs": tuple(directive.attribution["confidenceRefs"]),
                })
                return Result.success(dict(lowered))
            self.note(
                label=f"strategy-{directive.kind}-{len(self.contexts)}",
                source=f"meta-controller:{directive.attribution['controllerId']}",
                text=(f"Strategy directive: {directive.kind}. "
                      f"Reason: {directive.payload['reason']}"),
            )

        turn = len(self.contexts)
        bundle, compiled = self._assembler.assemble(view, turn)
        self.contexts.append(bundle)

        input_ref = self._capture(
            "prompt",
            bundle,
            turn=turn,
            labels={"promptDigest": compiled.digest, "prefixDigest": compiled.prefix_digest},
        )

        answer = self._model.propose(bundle, tools, sampling)
        value = getattr(answer, "value", None)
        raw = value if value is not None else answer
        if isinstance(value, Mapping) and value.get("kind") == "effect":
            action = value.get("action")
            args = value.get("args")
            if isinstance(action, str) and isinstance(args, Mapping):
                # Provider APIs require the declared function name in replayed
                # assistant messages, while the canonical proposal carries
                # the manifest verb. Resolve that from the same schemas
                # supplied to the model for this turn.
                tool_name = next(
                    (str(tool.get("name")) for tool in tools
                     if tool.get("verb") == action and tool.get("name")),
                    action,
                )
                self._assembler.tool_call(
                    turn=turn,
                    name=tool_name,
                    args=args,
                    thought=str(value.get("text") or value.get("note") or ""),
                )
        output_ref = self._capture("model_output", raw, turn=turn)

        self.contexts[-1] = self._handler.handle(
            answer,
            turn,
            self.contexts[-1],
            input_ref=input_ref,
            output_ref=output_ref,
        )
        return answer

    def _capture(
        self,
        role: str,
        payload: Any,
        *,
        turn: int,
        labels: Mapping[str, Any] | None = None,
    ) -> Any:
        """Hand bytes to the writer, or do nothing on the legacy path."""
        if self._artifacts is None:
            return None
        return self._artifacts.capture(role, payload, turn=turn, labels=labels)


def _route_of(model: Any) -> Mapping[str, Any]:
    """Which provider/model this call actually went to.

    Small and identity-only: a route that carried credentials or headers
    would put them in an append-only store.
    """
    return {
        "adapter": type(model).__name__,
        "provider": str(getattr(model, "provider", "")),
        "model": str(getattr(model, "model", getattr(model, "model_name", ""))),
        "mode": str(getattr(model, "mode", getattr(model, "_mode", ""))),
    }


def _observed_test_count(detail: str) -> int:
    """Extract a conservative test count from mediated verifier output.

    Exit status alone is not evidence that a test was collected or executed.
    Unknown/unparseable output intentionally returns zero so completion remains
    fail-closed.  The parser accepts the stable summaries emitted by unittest
    and pytest without coupling the runtime to either framework.
    """
    for pattern in (r"Ran\s+(\d+)\s+tests?\b", r"collected\s+(\d+)\s+items?\b"):
        match = re.search(pattern, detail, flags=re.IGNORECASE)
        if match:
            return max(0, int(match.group(1)))
    return 0


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
    #: `W11-A`. Bound only when the pack declares an index component. `None`
    #: means the harness declared none -- not that indexing failed.
    index: IndexPort | None = None
    verifier: Any = None
    approver: Callable[[Any], Any] | None = None
    approval_key: bytes | None = None
    interactive: bool = True
    #: `ADR-0096 §14`. `None` is the legacy no-capture composition and stays
    #: legal indefinitely: a session with no artifact store emits no
    #: artifact facts and makes no evidence claim it cannot support. Binding
    #: one turns capture on for this session and nothing else about it.
    blobs: BlobStorePort | None = None
    #: The resolved capture/redaction/sensitivity/retention policy. `None`
    #: resolves from `profile` at composition, or to the conservative default
    #: (`standard` retention, optional capture, redaction on).
    capture_policy: CapturePolicy | None = None
    #: `A-M65`. Disabled by default. The controller receives projections and
    #: confidence values only; the runtime retains every authority-bearing
    #: collaborator.
    meta_controller: MetaController | None = None
    #: Immutable evidence admitted by B-M65. An acting controller must bind at
    #: least one current record into its durable attribution.
    controller_confidence: tuple[ConfidenceRecord, ...] = ()
    #: Optional point-of-use authorized retrieval for L5 context.
    memory: MemoryBinding | None = None
    #: Optional point-of-use authorized experience sink on successful runs.
    experience: MemoryBinding | None = None
    #: Pack-composed terminal admission policy. ``None`` retains the strict
    #: built-in gate for legacy harnesses; production coding packs bind their
    #: repository/greenfield policy here.
    completion_policy: ICompletionPolicy | None = None
    #: `M-6`. The runtime that executes child episodes. `None` is legal for a
    #: composition that never declares `agent.spawn`; for one that does, the
    #: binding fails closed at composition rather than substituting a fake.
    child_runtime: ChildRuntimePort | None = None
    #: Child episodes share the parent's environment lifetime. Only the root
    #: composition owns and disposes the concrete environment adapter.
    environment_owner: bool = True


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
        *,
        on_terminal: Callable[["HarnessSession"], Any] | None = None,
        run_plan: Any = None,
    ) -> None:
        self.harness = harness
        self.ports = ports
        self.task = task
        self.calls: list[tuple[EffectRequest, Any]] = []
        # `S060-B-04` / `TSK-EVAL-001` handoff: the compose-time seam BETA's
        # `EvaluationListener` (or any future `EvaluationScheduler`) binds
        # through, without ever editing this file. `None` preserves today's
        # in-process `_evaluate()` RPC; a caller that supplies a callback
        # replaces the evaluation *authority* wholesale, not just its result.
        self._on_terminal = on_terminal
        self.run_plan = run_plan
        self._episode_begun_here = False
        self._completion_gate = AdmissionGate()
        self._completion_changed_files: set[str] = set()
        self._completion_inspected_files: set[str] = set()
        self._completion_verification: VerificationReceipt | None = None
        self._completion_verification_command: str | None = None
        self._completion_redundant_verifications = 0
        self._completion_allowed_tools: frozenset[str] | None = None

        repo = Path(task.repo_path)
        self.repo = repo
        self._completion_scaffold_baseline = self._empty_workspace_baseline()
        self.ledger = LedgerEmitter(
            ports.store,
            episode_id=task.episode_id,
            project_id=task.project_id,
            principal_id=task.principal,
            harness_digest=harness.composition_digest,
            parent_principal_id=task.parent_principal_id,
            parent_episode_id=task.parent_episode_id,
            clock=ports.clock,
            random=ports.random,
            role="session",
        )

        self.scope = task.scope_override or _scope_for(harness)
        self.adapters = {
            verb: harness.bindings[verb].factory(
                BindingContext(
                    verb=verb,
                    environment=ports.environment,
                    repo_path=repo,
                    emitter=self.ledger.spawn_adapter() if verb == "agent.spawn" else None,
                    parent_scope=self.scope,
                    clock=ports.clock,
                    store=ports.store,
                    parent_episode_id=task.episode_id,
                    max_depth=self.scope.constraints.max_depth,
                    max_turns=getattr(task, "max_turns", 10),
                    child_runtime=ports.child_runtime,
                    remaining_budget=self._spawn_remaining_budget,
                    project_id=task.project_id,
                    composition_digest=harness.frozen.composition_digest,
                    lineage=task.lineage or (task.episode_id,),
                    ledger=self.ledger,
                )
            )
            for verb in harness.verbs
        }
        # `W11-A`. The index is bound only when the pack declares it. A
        # harness that did not ask for one must not silently acquire it: an
        # unread component is a composition error (`S7-B-02`), and an unasked-
        # for one is a capability nobody authorised.
        self.index: IndexPort | None = None
        if harness.index_component is not None:
            self.index = ports.index or FileRepoIndex()
            self.index.index(str(repo))
        elif ports.index is not None:
            raise CompositionError(
                "an IndexPort was supplied but the manifest declares no index "
                "component; bind it in the pack or do not pass it")

        classifier = StandardClassifier([
            HeldAuthority(task.principal, frozenset(harness.verbs),
                          _ceiling_resources(harness), max_depth=4)])
        self.policy = _SwappablePolicy(StandardPolicy(
            parent_scope=self.scope,
            mode=Mode.INTERACTIVE if ports.interactive else Mode.BENCHMARK,
            # Every non-`low` capability the manifest declares is descriptor-
            # bound to a human. The threshold is one number and the manifest
            # supplies the risks it applies to.
            # TODO(S8-B-04): this literal is the last composition value the
            # manifest does not own. It is replaced by the approval-threshold
            # manifest component; Lane B lands that, not this sprint.
            # A sealed child scope is the already-approved delegation grant:
            # the parent approval covers the complete attenuated request, and
            # the child cannot widen that sealed membership. Requiring a
            # second interactive approval here would make every delegated
            # high-risk role fail in benchmark mode, despite the parent having
            # explicitly authorized the bounded child plan. Unsealed runs
            # retain the normal benchmark/interactive approval rule.
            approval_required_above=(None if self.scope.sealed else "low"),
            risk_of=harness.risk_of,
        ))

        # One kernel per run (`S8-A-01` DoD). Everything that used to vary
        # between the three constructions now varies behind `_SwappablePolicy`.
        governor = Governor(harness.budget)
        for dim, amt in self.ledger_state().cumulative_budget_debits.items():
            governor._spent[dim] = amt

        self.kernel = Kernel(
            adapters=self.adapters, policy=self.policy, classifier=classifier,
            governor=governor, issuer=GrantIssuer(),
            clock=ports.clock, ledger=self.ledger, events=self.ledger,
            sinks=harness.sinks)

        discovery = WorkspaceDiscovery(repo)
        discovered_env = discovery.render_environment_text()
        base_env = _environment_map(ports.environment, harness)
        env_parts = [base_env]
        if task.artifact_refs:
            env_parts.append(
                "=== Topology Artifact References ===\n" + "\n".join(
                    f"- {ref['artifact']}: {ref['digest']}"
                    for ref in task.artifact_refs))
        if discovered_env:
            env_parts.append(discovered_env)
        if task.resume_state:
            env_parts.append(
                "=== Durable Coding Task State ===\n"
                + json.dumps(dict(task.resume_state), sort_keys=True, default=str))
        if self.index is not None:
            # Repository intelligence is dynamic, bounded context. Never put a
            # complete flat index into the immutable environment prefix: large
            # workspaces would consume the compaction budget before the first
            # edit. The packet retains explicit omissions and provenance while
            # the compiler receives only a compact orientation summary.
            mapped = self.index.repo_map(token_budget=4000)
            if mapped.ok and mapped.value is not None:
                repo_map = mapped.value
                selected: list[Mapping[str, Any]] = [
                    {"kind": "file", "path": path, "estimated_tokens": 4}
                    for path in repo_map.files
                ]
                selected.extend(
                    {"kind": "symbol", "identity": f"{item.path}:{item.line}:{item.name}",
                     "path": item.path, "name": item.name, "line": item.line,
                     "symbolKind": item.kind,
                     "estimated_tokens": 8}
                    for item in repo_map.symbols
                )
                selected.extend(
                    {"kind": "dependency", "identity": f"{item.source}->{item.target}",
                     "source": item.source, "target": item.target,
                     "estimated_tokens": 6}
                    for item in repo_map.dependencies
                )
                selected.extend(
                    {"kind": "test", "path": item.test_path,
                     "source": item.source_path, "estimated_tokens": 5}
                    for item in repo_map.tests
                )
                packet = build_context_packet(
                    task_digest=digest_of({"runId": task.run_id, "brief": task.brief}),
                    repository_snapshot=repo_map.source_revision,
                    provider=repo_map.adapter_id,
                    provider_version="1",
                    query_digest=digest_of({"brief": task.brief}),
                    budget_tokens=4000,
                    selected=selected,
                    index_snapshot_digest=repo_map.source_revision,
                    reserve_tokens=1000,
                )
                orientation = {
                    "packetDigest": packet.digest(),
                    "repositorySnapshot": packet.repository_snapshot,
                    "files": list(packet.files)[:80],
                    "symbols": [dict(item) for item in packet.symbols[:80]],
                    "symbolSummary": [
                        f"{item.get('symbolKind', item.get('kind', 'symbol'))} {item.get('name', '')}:{item.get('line', '')}"
                        for item in packet.symbols[:80]
                    ],
                    "dependencies": [dict(item) for item in packet.dependencies[:80]],
                    "tests": list(packet.tests)[:80],
                    "omissions": list(packet.omissions),
                    "truncated": bool(repo_map.truncated or packet.omissions),
                }
                env_parts.append(
                    "=== Workspace Repository Map ===\n"
                    "=== Bounded Repository Context Packet ===\n"
                    + json.dumps(orientation, sort_keys=True, default=str))
        env_text = "\n\n".join(part for part in env_parts if part)
        compiler = ContextCompiler(
            system_core=harness.system_core,
            tool_schemas=harness.tool_schemas,
            environment=env_text,
            skill_cards=harness.skill_cards,
            token_ceiling=max(harness.budget.get("tokens", 0) or 64_000, 4_096),
        )
        # `ADR-0096 §14`. One optional seam, resolved once: either this
        # session captures evidence or it does not. There is no second
        # composition root and no per-call switch -- a capture path that could
        # be enabled halfway through a run would produce a trajectory whose
        # gaps mean nothing.
        self.artifacts: ArtifactWriter | None = None
        self.provenance: ProvenanceSink = NullProvenanceSink()
        if ports.blobs is not None:
            self.capture_policy = ports.capture_policy or resolve_capture_policy(
                getattr(run_plan, "profile", None))
            self.artifacts = ArtifactWriter(
                ports.blobs, self.ledger,
                policy=self.capture_policy,
                run_id=task.run_id, principal=task.principal,
                episode_id=task.episode_id)
            self.provenance = RuntimeProvenanceSink(
                self.ledger, run_id=task.run_id, principal=task.principal,
                episode_id=task.episode_id)
            # `ADR-0098 Decision 6`. The checkpoint rides the same optional
            # seam as capture, because it is written through the same writer:
            # a session with nowhere to put bytes has nowhere to put a
            # checkpoint either, and cold folding is the correct behaviour
            # there rather than a degraded one.
            self.checkpoints = CheckpointManager(
                ports.blobs, artifacts=self.artifacts)
        else:
            self.capture_policy = ports.capture_policy
            self.checkpoints: CheckpointManager | None = None
        self.last_checkpoint: Checkpoint | None = None

        self.operator = _LayeredOperator(
            ports.model, compiler, task=task,
            clock=ports.clock,
            recorder=CompetencePriorRecorder(clock=ports.clock, events=self.ledger),
            artifacts=self.artifacts,
            provenance=self.provenance if self.artifacts is not None else None,
            meta_controller=(
                self._consult_meta_controller
                if ports.meta_controller is not None else None
            ),
            memory=ports.memory,
            capabilities=tuple(
                {"verb": capability.verb,
                 "selector": capability.selector}
                for capability in harness.frozen.capabilities
            ),
        )
        # Read-only callback context for completion facts; it is populated
        # exclusively by this session's mediated dispatch path.
        self.operator._completion_calls = self.calls

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

    def _empty_workspace_baseline(self) -> bool:
        """Record whether the target was empty before product generation."""
        ignored = {
            ".git", ".vanguard", ".pytest_cache", "__pycache__", ".gitignore",
            ".editorconfig", "README.md", "TASK.md", "pyproject.toml",
            "package.json", "package-lock.json", "uv.lock",
        }
        try:
            return not any(item.name not in ignored for item in self.repo.iterdir())
        except OSError:
            return False

    def _controller_remaining_budget(self, view: AgentView) -> Mapping[str, int]:
        return remaining_budget(
            harness_budget=self.harness.budget,
            budget_consumed=view.budget_consumed,
            max_turns=self.task.max_turns,
            turns_consumed=self.turns_consumed(),
            max_depth=self.scope.constraints.max_depth,
            depth=self.scope.depth,
        )

    def _spawn_remaining_budget(self) -> Mapping[str, int]:
        """The same balance, folded from the live ledger at call time.

        Deliberately not a snapshot taken at composition. Siblings spawned in
        later turns must see what earlier siblings actually spent, or the
        second child is handed a budget the first one already consumed.
        """
        read = self.ports.store.read(EventRange(episode_id=self.task.episode_id))
        if not read.ok:
            # Fail closed. A store we cannot read is not a store that says
            # "nothing spent"; reporting the full ceiling here would let an
            # outage fund a child (`unknown is never a pass value`).
            return {dimension: 0 for dimension in
                    (*ADDITIVE_DIMENSIONS, "turns", "depth")}
        envelopes = read.value or ()
        # An empty episode has genuinely consumed nothing -- distinct from the
        # unreadable case above, and `fold_agent_view` refuses to fold zero
        # events rather than inventing a view.
        consumed = fold_agent_view(None, envelopes).budget_consumed if envelopes else {}
        return remaining_budget(
            harness_budget=self.harness.budget,
            budget_consumed=consumed,
            max_turns=self.task.max_turns,
            turns_consumed=self.turns_consumed(),
            max_depth=self.scope.constraints.max_depth,
            depth=self.scope.depth,
        )

    def _consult_meta_controller(self) -> ControllerProposal | None:
        """Consult the optional policy plugin from durable between-turn state.

        The first provider turn has no prior proposal and is intentionally not
        a consultation point. Thereafter the controller sees only pure M-5a
        projections and B-M65 confidence records. It never receives this
        session, its ports, the model, the store, the emitter, or the Kernel.
        """
        read = self.ports.store.read(EventRange(episode_id=self.task.episode_id))
        envelopes = tuple(read.value) if read.ok and read.value is not None else ()
        if not any(
            (event.payload.get("kind") or event.mhf_kind) == "ProposalProduced"
            for event in envelopes
        ):
            return None
        view: AgentView = fold_agent_view(None, envelopes)
        progress: ProgressView = fold_progress(
            {"payload": dict(event.payload)} for event in envelopes)
        proposal = guarded_consult(
            self.ports.meta_controller,
            view,
            progress,
            self.ports.controller_confidence,
            remaining_budget=self._controller_remaining_budget(view),
        )
        if proposal is None:
            return None
        if not self.ports.controller_confidence:
            raise ValueError("an acting meta-controller requires confidence evidence")
        if proposal.attribution["controllerId"] != self.ports.meta_controller.controller_id:
            raise ValueError("controller directive identity does not match its binding")

        self.ledger.emit_kind(
            "StrategyChanged",
            run_id=self.task.run_id,
            principal=self.task.principal,
            payload={
                "from": view.strategy,
                "to": proposal.kind,
                "trigger": _controller_trigger(proposal),
                "controllerId": proposal.attribution["controllerId"],
            },
            episode_id=self.task.episode_id,
        )
        if proposal.kind == "revise_plan":
            previous = (
                view.plan_revisions[-1].get("planDigest")
                if view.plan_revisions else None
            )
            plan_digest = digest_of({
                "controllerId": proposal.attribution["controllerId"],
                "directive": proposal.kind,
                "brief": proposal.payload.get("brief"),
                "reasonDigest": proposal.attribution["reasonDigest"],
                "previousPlanDigest": previous,
            })
            payload: dict[str, Any] = {
                "revision": len(view.plan_revisions) + 1,
                "planDigest": plan_digest,
                "rationaleDigest": proposal.attribution["reasonDigest"],
            }
            if isinstance(previous, str) and previous:
                payload["previousPlanDigest"] = previous
            self.ledger.orchestrator().emit_kind(
                "PlanRevised",
                run_id=self.task.run_id,
                principal=self.task.principal,
                payload=payload,
                episode_id=self.task.episode_id,
            )
        return proposal

    def checkpoint(self, *, turn: int | None = None) -> Checkpoint | None:
        """Memoise the current fold, if this session can store one.

        Returns `None` rather than raising when there is no store, no
        authorisation, or no retention for it. A checkpoint is a cache: the
        events remain the truth and the cold fold remains available, so an
        unwritten checkpoint costs time and never correctness.
        """
        if self.checkpoints is None:
            return None
        self.last_checkpoint = self.checkpoints.capture(
            self.ledger_state(), turn=turn)
        return self.last_checkpoint

    def reconstruct(self, *, verify: bool = False) -> Reconstruction:
        """Rebuild episode state, using a checkpoint only once it has proven itself.

        Every validation failure falls back to the full cold fold and records
        why (`runtime/checkpoints.py`). `verification="verified"` is reachable
        only with `verify=True`, which executes the parity comparison -- `C-04`
        separates capability from proof and this is where that separation is
        actually enforced on the runtime path.
        """
        read = self.ports.store.read(EventRange(episode_id=self.task.episode_id))
        envelopes = list(read.value) if read.ok and read.value is not None else []
        if self.checkpoints is None:
            if not envelopes:
                return Reconstruction(state=None, capability="none")
            return Reconstruction(
                state=reconstruct_state(envelopes),
                capability="full_cold",
                events_replayed=len(envelopes),
            )
        return self.checkpoints.reconstruct(
            envelopes, checkpoint=self.last_checkpoint, verify=verify)

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
        request = _with_diff_headers(request)
        if request.idempotency_key:
            settled = RecoveryScanner.settled_effect(
                self.ports.store, request.idempotency_key,
                project_id=self.task.project_id,
            )
            if settled is not None:
                occurrence = str(settled.payload.get("occurrence") or "")
                status = str(settled.payload.get("status") or "")
                if occurrence == "undeterminable" or status == "undeterminable":
                    result = DispatchResult(
                        FailurePath.UNDETERMINABLE,
                        str(settled.payload.get("descriptorDigest") or ""),
                        AdapterOutcome(
                            status="error", occurrence=Occurrence.UNDETERMINABLE,
                            detail="recovered durable intent remains undeterminable; "
                                   "physical execution denied pending exterior reconciliation",
                        ),
                        detail="recovered durable intent remains undeterminable; "
                               "physical execution denied pending exterior reconciliation",
                    )
                    self.calls.append((request, result))
                    return result
                result = DispatchResult(
                    FailurePath.OK,
                    str(settled.payload.get("descriptorDigest") or ""),
                    AdapterOutcome(
                        status="ok", occurrence=Occurrence.OCCURRED,
                        result_digest=settled.payload.get("resultDigest"),
                        detail="reused durable settled effect; physical execution skipped",
                    ),
                    detail="reused durable settled effect; physical execution skipped",
                )
                self.calls.append((request, result))
                return result
        result = self.kernel.dispatch(request, **kwargs)
        self.calls.append((request, result))
        return result

    # -- the lifecycle ----------------------------------------------------

    def begin_episode(self) -> None:
        """Durably open a new episode before registry activation begins."""
        if self.ledger_state().episode.status != "pending":
            return
        self.ledger.emit(Event(
            kind="EpisodeStarted",
            reason="composed",
            at=self.ports.clock.now(),
            run_id=self.task.run_id,
            principal=self.task.principal,
            payload={
                "episodeId": self.task.episode_id,
                "objective": self.task.brief,
                "budgetCeiling": dict(self.harness.budget),
                "scaffoldBaselineRecorded": self._completion_scaffold_baseline,
                "harness": self.harness.harness,
                "compositionDigest": self.harness.composition_digest,
                "activationDigest": getattr(self.run_plan, "activation_digest", ""),
                "runDigest": getattr(self.run_plan, "run_digest", ""),
                "taskDigest": getattr(self.run_plan, "task_digest", ""),
                "preregistrationDigest": getattr(
                    self.run_plan, "preregistration_digest", ""),
                "maxTurns": int(self.task.max_turns),
                "interactive": bool(self.ports.interactive),
            },
        ))
        self._episode_begun_here = True

    def run(self) -> RunResult:
        """Run the episode, resolve approvals, evaluate from outside."""
        harness, task, ports = self.harness, self.task, self.ports
        receipts: list[Receipt] = []
        authorization = None
        terminal = RunTermination.ABANDONED
        detail = ""

        # `TSK-LED-002` / `G-050-03`: the ledger's first durable event is
        # written from packages, not a CLI fixture. Guarded on ledger status
        # rather than a local flag: a process-restart resume constructs a
        # fresh `HarnessSession` (fresh `LedgerBridge`) for the same
        # `episode_id`, and the guard must survive that reconstruction too,
        # or resume would double-append the beginning of the run.
        prior_state = self.ledger_state()
        if self._episode_begun_here:
            pass
        elif prior_state.episode.status == "pending":
            self.begin_episode()
        else:
            scanner = RecoveryScanner(controller_principal=task.principal)
            # Checkpoints accelerate the fold but never replace the event
            # stream. A cold continuation proves the checkpoint/state parity
            # before the planner sees the restored task context.
            self.reconstruct(verify=True)
            scanner.reconcile_open_intents(
                ports.store, occurred_at=ports.clock.now(),
                project_id=task.project_id,
            )
            # Open subtrees are adjudicated before the run is declared
            # recovered, so a resumed parent never re-runs a child whose
            # occurrence nobody actually knows (`WP-A1`).
            scanner.reconcile_open_children(
                ports.store, occurred_at=ports.clock.now(),
                project_id=task.project_id,
            )
            self.ledger._seq, self.ledger._prev = self.ledger._load_chain(task.project_id)
            read_events = ports.store.read(EventRange(episode_id=task.episode_id))
            ev_list = list(read_events.value) if read_events.ok and read_events.value else []
            kinds = [(e.payload.get("kind") if hasattr(e, "payload") and isinstance(e.payload, Mapping) else None) or getattr(e, "mhf_kind", "") for e in ev_list]
            if "RunRecovered" not in kinds:
                self.ledger.emit_kind(
                    "RunRecovered",
                    run_id=task.run_id,
                    principal=task.principal,
                    payload={
                        "kind": "RunRecovered",
                        "runId": task.run_id,
                        "recoveryReason": "cold restart from durable ledger",
                        "recoveredBy": task.principal,
                        "priorState": prior_state.episode.status,
                    },
                    episode_id=task.episode_id,
                )

        # `S8-A-02`. This used to be a bounded segment loop building a fresh
        # `Episode` each pass with a fresh `max_turns` -- so the real bound was
        # the product of the two limits (8x8=64), nothing stated it, and an
        # agreeable reviewer bought the run another eight turns per approval.
        # Re-entry is now driven by the ledger: `max_turns` bounds the episode,
        # not each segment of it, and an exhausted budget is terminal.
        delayed = DelayedTerminalEmitter(self.ledger)
        # The episode's turn history spans approval re-entries. Rebuilding the
        # engine with an empty `Episode` discarded it every round-trip, so turn
        # indices restarted at 0 and no-progress detection could never see two
        # consecutive turns of the same run (`CMX-03`).
        prior_turns: tuple[Any, ...] = ()
        prior_recovery_state = ProtocolRecoveryState.from_dict(
            task.resume_state.get("recoveryState", {})
            if isinstance(task.resume_state, Mapping) else {})
        # `_record` clears `self.calls`, so the attempted-verb set has to be
        # accumulated here or the phase ladder resets to `inspect` on every
        # approval re-entry -- which un-offers `patch` on the turn right after
        # a patch, the exact shape of the observed instrument error.
        seen_verbs_acc: set[str] = set()
        while True:
            remaining = task.max_turns - self.turns_consumed()
            if remaining <= 0:
                terminal = RunTermination.ABANDONED
                detail = f"max_turns ({task.max_turns}) exhausted across approval"
                break
            self.policy.bind(authorization)
            decoders, patch_detector, truncation_detector = default_protocol_pipeline()
            engine = EpisodeEngine(
                kernel=self, model=self.operator, clock=ports.clock,
                events=delayed, scope=self.scope, tools=harness.tool_schemas,
                max_turns=len(prior_turns) + remaining,
                spawn_dispatcher=self.dispatch,
                preset_mode=getattr(harness, "tool_policy_preset", None),
                protocol_decoders=decoders,
                patch_detector=patch_detector,
                truncation_detector=truncation_detector,
                completion_admitter=(self._admit_completion
                                     if admission_required(harness)
                                     else None),
                completion_allowed_tools=self._completion_allowed_tools)
            outcome = engine.run(
                episode_id=task.episode_id, run_id=task.run_id,
                principal=task.principal, brief=task.brief,
                spans=(_operator_span(),),
                receipt_labeller=lambda turn, dispatch: _admit_turn_result(
                    self.operator, turn, dispatch,
                    on_dispatch=self._observe_completion_dispatch),
                prior_turns=prior_turns,
                prior_seen_verbs=tuple(sorted(seen_verbs_acc)),
                prior_recovery_state=prior_recovery_state)
            seen_verbs_acc.update(
                str(getattr(req, "action", "")) for req, _ in self.calls)
            prior_turns = outcome.episode.turns
            prior_recovery_state = outcome.recovery_state
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
            seen_verbs_acc.add(str(getattr(request, "action", "")))
            approved_dispatch = self.dispatch(
                request, requested_scope=self.scope,
                reservation=_reservation_for(harness.budget,
                                             harness.effect_budget))
            # The approved effect is the one that actually lands. It does not
            # pass through the engine's turn callback, so without this the
            # completion gate never saw the patch it had just applied and
            # rejected every finish with MISSING_SOURCE_PATCH.
            self._observe_completion_dispatch(request, approved_dispatch)
            observer = getattr(self.operator._model, "observe_dispatch", None)
            if callable(observer):
                observer(approved_dispatch)
            _record(receipts, self.operator, self.calls, admit_context=True)
            authorization = None

        if terminal is RunTermination.COMPLETED and ports.experience is not None:
            try:
                self._emit_experience_fact(receipts)
            except Exception as exc:
                # A successful episode cannot silently become an unrecorded
                # learning input. Preserve the failure as the run outcome.
                terminal = RunTermination.INSTRUMENT_ERROR
                detail = f"experience emission failed: {exc}"

        verdict = self._on_terminal(self) if self._on_terminal is not None else self._evaluate()
        read_all = ports.store.read(EventRange(episode_id=task.episode_id))
        durable_events = list(read_all.value) if read_all.ok and read_all.value else list(self.ledger.events)
        if delayed.pending is None:
            terminal_name = str(getattr(terminal, "value", terminal))
            delayed.pending = Event(
                kind="EpisodeCompleted",
                reason=terminal_name,
                at=ports.clock.now(),
                run_id=task.run_id,
                principal=task.principal,
                payload={
                    "episodeId": task.episode_id,
                    "outcome": ("resolved"
                               if terminal in (RunTermination.COMPLETED, RunTermination.ABSTAINED)
                               else terminal_name),
                },
            )

        # The digest of the state this trajectory *describes*: the fold of
        # exactly the events named by `event_range`, which stops before the
        # terminal event that carries the trajectory.
        #
        # It cannot include the terminal event. That event's payload contains
        # this trajectory, which contains this digest, so a digest computed
        # over a state containing it is self-referential and no fresh process
        # can ever reproduce it. The previous value folded the pending
        # `EpisodeCompleted` in and was then overwritten a few lines later by a
        # third value, so the recorded digest matched no fold of the durable
        # log at all -- reconstruction had nothing honest to verify against
        # (`C-04`: a claim no receipt can confirm).
        final_state_digest = compute_state_digest(self.ledger_state())

        trajectory = assemble_trajectory(
            task=task,
            harness_digest=harness.composition_digest,
            terminal=str(getattr(terminal, "value", terminal)),
            receipts=receipts,
            contexts=list(self.operator.contexts),
            events=tuple(durable_events),
            verdict=verdict,
            state_digest=final_state_digest,
            model=self.ports.model,
            environment=self.ports.environment,
            run_plan=self.run_plan,
            **self._capture_evidence(),
        )
        delayed.flush(trajectory)
        if ports.environment_owner:
            ports.environment.dispose()
        result = RunResult(
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
            # The same value the trajectory binds (`RF-23`), and the one a
            # fresh process can reproduce by folding the declared
            # `event_range`. Re-reading the ledger here would fold the terminal
            # event back in and reintroduce the self-reference D9 removed.
            state_digest=final_state_digest,
            trajectory=trajectory,
            run_digest=getattr(self.run_plan, "run_digest", ""),
            activation_digest=getattr(self.run_plan, "activation_digest", ""),
        )
        if self.run_plan is not None:
            from .foundation_evidence import derive_foundation_bundle
            result = replace(result, foundation_evidence=derive_foundation_bundle(
                run_plan=self.run_plan, result=result, store=ports.store,
            ))
        return result

    # -- what the instrument reads ----------------------------------------

    def _emit_experience_fact(self, receipts: Sequence[Receipt]) -> str:
        """Persist a minimal causal success fact through the injected port."""
        binding = self.ports.experience
        if binding is None:  # pragma: no cover - guarded by the caller
            raise PermissionError("experience memory binding is unavailable")
        access = binding.authorize("write", now=_memory_now(self.ports.clock))
        value = {
            "category": "experience",
            "kind": "episode_outcome",
            "text": f"Episode {self.task.episode_id} completed successfully.",
            "causal": {
                "runId": self.task.run_id,
                "episodeId": self.task.episode_id,
                "compositionDigest": self.harness.composition_digest,
                "receiptDigests": tuple(receipt.descriptor_digest for receipt in receipts),
            },
        }
        record_id = binding.port.write(value, access)
        if not isinstance(record_id, str) or not record_id:
            raise PermissionError("experience memory did not return a record identity")
        return record_id

    def _capture_evidence(self) -> dict[str, Any]:
        """What this run actually captured, for the `mhf.trajectory/2` writer.

        Delegates to `evidence_capture.capture_evidence` (EVO-06).
        """
        return _capture_evidence_pure(self.artifacts, self.provenance)

    def _telemetry(self) -> RunTelemetry:
        """Integer telemetry, with absence preserved (`S9-A-02`).

        Delegates to `telemetry.compute_run_telemetry` (EVO-06) -- summing
        reported token usage is a pure function of the operator's contexts
        and the turn count, with no other session state involved.
        """
        return compute_run_telemetry(self.operator.contexts, self.turns_consumed())

    def _instrument_error(self) -> str | None:
        """Why this arm produced no usable measurement, or `None`.

        Delegates to `telemetry.instrument_error` (EVO-06). `S7-C-02` calls
        the zero-turns case `model_not_invoked`: an instrument failure, not
        a cheap run.
        """
        return _telemetry_instrument_error(self.turns_consumed())

    def _evaluate(self) -> Any:
        """`ICD 3` / `M5`: the verdict comes from outside the episode.

        `ADR-0076 §5`: a verdict the daemon actually signed and bound is also
        ledgered here as `VerdictRecorded{SignedVerdict}`, through the one
        role-scoped facade that may originate that kind (`evaluator_gateway`,
        1.1-D). An unsigned or unbound result -- no evaluator reachable, a
        legacy response -- has nothing to ledger, by construction: there is no
        code path here that fabricates the missing fields.
        """
        bound = self.ports.verifier
        if bound is None:
            bound = _evaluator_from_manifest(self.harness, self.repo)
        if bound is None:
            return None
        evaluation = bound.evaluate(
            RunRef(run_id=self.task.run_id, episode_id=self.task.episode_id),
            EvaluationProtocol(
                name=self.harness.evaluators[0] if self.harness.evaluators else "unnamed"))
        verdict = evaluation.value if evaluation.ok else None
        if isinstance(verdict, Verdict):
            record_verdict(
                self.ledger, run_id=self.task.run_id, principal=self.task.principal,
                episode_id=self.task.episode_id, verdict=verdict)
        return verdict

    def _workspace_digest(self) -> str:
        snapshot = self.ports.environment.snapshot()
        if snapshot.ok and snapshot.value is not None:
            return snapshot.value.digest
        return ""

    def _observe_completion_dispatch(self, request: EffectRequest, result: Any) -> None:
        """Capture patch and verification facts at the mediated boundary."""
        if result.failure is not FailurePath.OK or result.outcome is None:
            return
        outcome = result.outcome
        if request.action in {"read", "search"} or request.action == "fs.read":
            path = request.args.get("path")
            if isinstance(path, str) and path and not path.startswith(("/", "\\")):
                self._completion_inspected_files.add(path.replace("\\", "/"))
        if request.action in {"patch", "patch.apply", "fs.patch", "write", "fs.write", "delete"}:
            path = request.args.get("path")
            if isinstance(path, str) and path and not path.startswith(("/", "\\")):
                self._completion_changed_files.add(path.replace("\\", "/"))
            if (self.artifacts is not None
                    and "reused durable settled effect" not in str(outcome.detail or "")):
                self.artifacts.capture(
                    "patch",
                    {"action": request.action, "args": dict(request.args),
                     "resultDigest": outcome.result_digest},
                    turn=self.turns_consumed(),
                )
        if request.action not in {"test", "exec", "proc.exec"}:
            return
        argv = request.args.get("argv", request.args.get("command", ()))
        verification_command = (
            argv if isinstance(argv, str) else " ".join(str(item) for item in argv)
        )
        executable = str(argv[0]) if isinstance(argv, Sequence) and not isinstance(argv, str) and argv else ""
        is_test = executable.rsplit("/", 1)[-1] in {"pytest", "unittest"} or any(
            "test" in str(item).lower() for item in (argv if isinstance(argv, Sequence) else (verification_command,)))
        if not is_test:
            return
        detail = str(outcome.detail or "")
        match = re.search(r"\[exit (-?\d+)\]", detail)
        exit_code = int(match.group(1)) if match else (0 if outcome.status == "ok" else 1)
        previous_verification = self._completion_verification
        self._completion_verification = VerificationReceipt(
            exit_code=exit_code,
            executed_test_count=_observed_test_count(detail),
            workspace_digest=self._workspace_digest(),
            task_digest=(self.run_plan.task_digest if self.run_plan is not None
                         else digest_of({"task": self.task.brief})),
            composition_digest=self.run_plan.composition_digest if self.run_plan is not None else self.harness.composition_digest,
            receipt_digest=outcome.result_digest or "",
            verification_command=verification_command,
            verification_subject_digest=digest_of({"command": verification_command}),
        )
        if (self.artifacts is not None
                and "reused durable settled effect" not in str(outcome.detail or "")):
            self.artifacts.capture(
                "verification_report",
                {"command": list(argv) if isinstance(argv, Sequence) else [],
                 "exitCode": exit_code,
                 "executedTestCount": self._completion_verification.executed_test_count,
                 "workspaceDigest": self._completion_verification.workspace_digest,
                 "receiptDigest": self._completion_verification.receipt_digest},
                turn=self.turns_consumed(),
            )
        self._completion_verification_command = verification_command
        if previous_verification is not None and self._completion_verification.passed:
            self._completion_redundant_verifications += 1
            if self._completion_redundant_verifications == 1:
                note = getattr(self.operator, "note", None)
                if callable(note):
                    note(
                        label="completion-recovery-1",
                        source="completion_policy",
                        text=(
                            "Completion evidence is already admissible and this "
                            "verification succeeded redundantly. Request "
                            "agency.finish now; do not rerun the same verification."
                        ),
                        evictable=False,
                    )
            elif self._completion_redundant_verifications >= 2:
                self._completion_allowed_tools = frozenset(
                    {"agency.finish", "fs.read", "fs.search"})
                note = getattr(self.operator, "note", None)
                if callable(note):
                    note(
                        label="completion-recovery-2",
                        source="completion_policy",
                        text=(
                            "Repeated successful verification is settled. Only "
                            "agency.finish, fs.read, and fs.search remain available; "
                            "choose agency.finish or inspect the result."
                        ),
                        evictable=False,
                    )

    def _admit_completion(self, _episode: Any, _proposal: Any) -> AdmissionVerdict:
        """Apply the coding completion contract before reducing ``finish``."""
        policy = self.ports.completion_policy or self._completion_gate
        verdict = policy.evaluate(
            preset_name=self.harness.harness,
            changed_files=tuple(sorted(self._completion_changed_files)),
            proposal={"kind": "finish"},
            verification=self._completion_verification,
            current_workspace_digest=self._workspace_digest(),
            current_task_digest=(self.run_plan.task_digest if self.run_plan is not None else digest_of({"runId": self.task.run_id, "brief": self.task.brief})),
            current_composition_digest=(self.run_plan.composition_digest if self.run_plan is not None else self.harness.composition_digest),
            current_verification_command=self._completion_verification_command,
            current_verification_subject_digest=(
                digest_of({"command": self._completion_verification_command})
                if self._completion_verification_command else None
            ),
            inspected_files=tuple(sorted(self._completion_inspected_files)),
            task_text=self.task.brief,
            greenfield_evidence={
                "baseline_recorded": self._completion_scaffold_baseline,
                "structural_passed": bool(self._completion_verification and self._completion_verification.passed),
                "smoke_test_created": any("test" in path.lower() for path in self._completion_changed_files),
                "behavioral_passed": bool(self._completion_verification and self._completion_verification.passed),
            },
        )
        if isinstance(verdict, AdmissionVerdict):
            return verdict
        if isinstance(verdict, Mapping):
            return AdmissionVerdict(
                bool(verdict.get("admissible", verdict.get("admitted", False))),
                str(verdict.get("reason", "COMPLETION_POLICY_REJECTED")),
                verdict.get("rejection_feedback"),
            )
        return AdmissionVerdict(False, "COMPLETION_POLICY_INVALID_VERDICT")


def _admit_turn_result(operator: _LayeredOperator, turn: int, result: Any,
                       *, on_dispatch: Callable[[EffectRequest, Any], None] | None = None) -> Span | None:
    """Admit the just-produced tool result before the next model turn.

    EpisodeEngine invokes this callback immediately after every dispatch. The
    result is therefore available to the next proposal in the same episode,
    rather than waiting until an approval suspension or terminal boundary.

    The returned `Span` (`K-33`) enters the episode's accumulated justifying
    spans at `Trust.UNTRUSTED_EXTERNAL`: a tool result is content that may
    inform the next proposal, but per `K-30`/`K-31` it may never itself
    justify capability widening -- only an operator-authored span can.
    """
    outcome = getattr(result, "outcome", None)
    if on_dispatch is not None:
        # The session's dispatch ledger is ordered; the latest call is the
        # effect represented by this callback. Keeping this hook here means
        # admission observes only mediated effects, never model output.
        calls = getattr(operator, "_completion_calls", ())
        if calls:
            on_dispatch(calls[-1][0], result)
    # The callback is also used by small operator doubles in the composition
    # contract tests.  Access the wrapped model itself first; looking up
    # ``operator._model`` as an attribute of the model is an accidental
    # second dereference and breaks operators that are not layered wrappers.
    model = getattr(operator, "_model", operator)
    observer = getattr(model, "observe_dispatch", None)
    if callable(observer):
        observer(result)
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
    return _span_for(f"tool-result-{turn}", "tool_result")


def _payload_field(result: Any, key: str) -> str | None:
    for event in getattr(result, "events", ()) or ():
        payload = getattr(event, "payload", None) or {}
        value = payload.get(key)
        if isinstance(value, str) and value:
            return value
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
            # An approved effect executes between engine segments. Its failed
            # dispatch therefore has no engine callback to carry the failure
            # into the next prompt. Dropping it here leaves the model blind and
            # guarantees identical retries (observed live with proc.exec).
            if admit_context:
                failure = str(getattr(result.failure, "value", result.failure))
                detail = str(result.detail or "dispatch produced no outcome")
                operator.note(
                    label=f"{request.action}-failure-{len(receipts)}",
                    source="tool_result",
                    text=f"{request.action} -> {failure}\n{detail}",
                )
            continue
        outcome_detail = result.detail or getattr(result.outcome, "detail", "")
        receipts.append(Receipt(
            verb=request.action,
            descriptor_digest=result.descriptor_digest or "",
            outcome=result.outcome.status,
            detail=outcome_detail,
            lease_id=_payload_field(result, "leaseId"),
            grant_digest=_payload_field(result, "grantDigest"),
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


def _with_diff_headers(request: EffectRequest) -> EffectRequest:
    """Name the file a headerless hunk is already addressed to, once, at the seam.

    A model routinely emits a bare `@@` hunk and carries the target in `path`.
    That diff is unambiguous in context but not on its own, and two layers
    downstream rejected it for opposite-looking reasons: the approval flow
    refused to build a challenge at all (`normalise_unified_diff` -- a
    signature over a diff with no filename is a signature over an ambiguity),
    so the episode escalated before any effect started; and the applier could
    not tell which file to open.

    This is the runtime seam, which is where it belongs. Unified diffs are
    coding-domain knowledge, so `agency` must not carry it (`ADR-0060`: the
    generic engine names no domain verb) and the kernel must not either. Doing
    it *here*, before `Kernel.dispatch`, is also what keeps the layers honest
    about each other: the descriptor digest, the bytes the approver signs and
    the bytes the environment writes are then all computed over the same text.
    Patching it further downstream would leave the human approving one thing
    and the environment applying another -- precisely the binding `K-15`
    re-verifies at resumption.
    """
    args = getattr(request, "args", None)
    if not isinstance(args, Mapping):
        return request
    diff = args.get("diff") or args.get("patch")
    path = args.get("path")
    if not isinstance(diff, str) or not isinstance(path, str) or not path:
        return request
    if not diff.lstrip().startswith("@@"):
        return request
    for line in diff.splitlines():
        if line.startswith("--- ") or line.startswith("diff --" + "git "):
            return request
    headed = f"--- a/{path}\n+++ b/{path}\n{diff}"
    updated = dict(args)
    for key in ("diff", "patch"):
        if key in updated:
            updated[key] = headed
    try:
        return replace(request, args=updated)
    except TypeError:
        # Not a dataclass: a caller passed a request-shaped double. Leaving it
        # untouched is correct -- normalisation is a convenience for real
        # proposals, never a precondition of dispatch.
        return request
