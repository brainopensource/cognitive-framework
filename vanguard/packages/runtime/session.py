"""One run: session wiring and lifecycle (`2.2-C`).

`HarnessSession` is the one kernel the engine sees for a run. It does not
compose a harness and it does not write envelopes except through
`LedgerEmitter`.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from ..adapters.stores.repo_index import FileRepoIndex
from ..agency import EpisodeEngine, RunTermination
from ..agency.context import (
    CompetencePriorRecorder,
    CompiledContext,
    ContextCompiler,
    Fragment,
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
from .telemetry import RunTelemetry
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

    It wraps the provider rather than changing `EpisodeEngine`, because
    `ADR-0060` prices any edit to `agency/episode/` at the generality
    invariant. The engine keeps handing its own view to `propose`; this
    intercepts it, compiles the layered context around it, and passes the
    provider a `ContextBundle` (`ICD §4`).
    """

    def __init__(self, model: Any, compiler: ContextCompiler, *,
                 recorder: CompetencePriorRecorder | None = None,
                 task: TaskContext,
                 clock: Any,
                 artifacts: ArtifactWriter | None = None,
                 provenance: ProvenanceSink | None = None,
                 meta_controller: Callable[[], ControllerProposal | None] | None = None,
                 memory: MemoryBinding | None = None) -> None:
        self._model = model
        self._compiler = compiler
        self._recorder = recorder
        self._task = task
        self._clock = clock
        self._dialogue: list[Fragment] = []
        self.contexts: list[Mapping[str, Any]] = []
        # `None` is the legacy no-capture composition (`blobs=None`). It is a
        # first-class state, not a degraded one: a session with no artifact
        # store captures nothing and therefore claims nothing.
        self._artifacts = artifacts
        self._provenance = provenance
        self._meta_controller = meta_controller
        self._memory = memory

    def note(self, label: str, source: str, text: str, *, evictable: bool = True) -> None:
        """Admit one turn's outcome to L5. Mid-run additions go to L5, always
        (`VG-03 §10.2`) — anything else destroys the cached prefix."""
        self._dialogue.append(Fragment(source=source, label=label, text=text,
                                       evictable=evictable))

    def propose(self, view: Mapping[str, Any], tools: Sequence[Mapping[str, Any]],
                sampling: Mapping[str, Any]) -> Any:
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
        memory_fragments, memory_digest = self._memory_fragments()
        compiled: CompiledContext = self._compiler.compile(
            brief=self._task.brief,
            dialogue=tuple(self._dialogue) + memory_fragments,
        )
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
        if memory_digest:
            bundle["memoryRetrievalDigest"] = memory_digest
        digest = view.get("lastReceiptDigest")
        if digest:
            token = (
                f"justifying_receipt={digest} "
                f"progress={view.get('lastProgressSignal') or ''}"
            )
            messages = list(bundle.get("messages") or ())
            messages.append({"role": "user", "content": token})
            bundle["messages"] = tuple(messages)
            bundle["lastReceiptDigest"] = digest
        self.contexts.append(bundle)
        # 0-based, matching `turn`/`turnIndex` in the frozen cross-lane
        # fixture and in `mhf.trajectory/1`'s existing turn numbering.
        turn = len(self.contexts) - 1

        # Context/compaction provenance, then the exact provider input. All
        # of it before the call, because after the call the only honest thing
        # to say about a prompt is what it *was*.
        self._record_selection(compiled, turn)
        input_ref = self._capture(
            "prompt", bundle, turn=turn,
            labels={"promptDigest": compiled.digest,
                    "prefixDigest": compiled.prefix_digest})

        answer = self._model.propose(bundle, tools, sampling)

        # `ADR-0096 §14.1`: the raw structured response, immediately on
        # return and before anything below reinterprets it. The `usage` and
        # `resolved_model` folding further down rewrites what this run
        # *believes* about the call; capturing after it would record the
        # belief rather than the response.
        value = getattr(answer, "value", None)
        raw = value if value is not None else answer
        output_ref = self._capture("model_output", raw, turn=turn)
        # The trajectory `/2` writer reads per-turn exact-I/O references off
        # the context record (`trajectory.py`), so the refs are stamped here
        # rather than rediscovered later by matching digests back to turns.
        if input_ref is not None or output_ref is not None:
            stamped = dict(self.contexts[-1])
            if input_ref is not None and input_ref.digest:
                stamped["model_input_ref"] = input_ref.digest
            if output_ref is not None and output_ref.digest:
                stamped["model_output_ref"] = output_ref.digest
            self.contexts[-1] = stamped

        if self._provenance is not None and hasattr(self._provenance, "record_model_io"):
            policy = (self._artifacts.policy.identity()
                      if self._artifacts is not None else {})
            self._provenance.record_model_io(
                route=_route_of(self._model), input_ref=input_ref,
                output_ref=output_ref, capture_policy=policy, turn=turn)
            # Only when the provider itself reported cache participation. A
            # live call that touched no cache emits nothing (`14.1` capture is
            # about what happened, not about what the composition could do).
            self._provenance.record_cache(
                reported=cache_participation(value), turn=turn,
                source_digest=output_ref.digest if output_ref else "")

        if isinstance(value, Mapping):
            usage = value.get("usage")
            if isinstance(usage, Mapping):
                measured = dict(self.contexts[-1])
                for key in ("prompt_tokens", "completion_tokens", "usd_micros",
                            "ttft_millis"):
                    reported = usage.get(key)
                    if isinstance(reported, int) and not isinstance(reported, bool):
                        measured[key] = reported
                measured["provider_usage_reported"] = True
                resolved = value.get("resolved_model")
                if isinstance(resolved, str) and resolved:
                    measured["model"] = resolved
                fingerprint = value.get("model_fingerprint")
                if isinstance(fingerprint, str) and fingerprint:
                    measured["model_fingerprint"] = fingerprint
                self.contexts[-1] = measured
        return answer

    def _memory_fragments(self) -> tuple[tuple[Fragment, ...], str]:
        """Retrieve authorized context immediately before compiling a turn."""
        if self._memory is None:
            return (), ""
        access = self._memory.authorize("read", now=_memory_now(self._clock))
        result = self._memory.port.recall(
            self._memory.query, access, self._memory.limit)
        selected = require_retrieval_provenance(result)
        if selected and len(result.texts) != len(selected):
            raise PermissionError("memory result has no complete materialized context")
        fragments = tuple(
            Fragment(
                source=f"memory:{result.provenance.policy_identity}",
                label=f"memory:{record_id}",
                text=text,
            )
            for record_id, text in zip(selected, result.texts)
            if isinstance(text, str) and text
        )
        if len(fragments) != len(selected):
            raise PermissionError("memory result contains invalid context text")
        return fragments, result.provenance.digest() if selected else ""

    # -- capture helpers ---------------------------------------------------

    def _capture(self, role: str, payload: Any, *, turn: int,
                 labels: Mapping[str, Any] | None = None) -> Any:
        """Hand bytes to the writer, or do nothing on the legacy path.

        Nothing is caught here. `EvidenceCaptureRequiredError` and
        `EvidenceLedgerAppendError` are fatal by `ADR-0096 §14.2` and must
        reach the caller through the generic Agency protocol; swallowing them
        would leave the turn running with evidence it does not have.
        """
        if self._artifacts is None:
            return None
        return self._artifacts.capture(role, payload, turn=turn, labels=labels)

    def _record_selection(self, compiled: CompiledContext, turn: int) -> None:
        """Context-selection and compaction provenance for one turn.

        The compiler stays pure: it is *asked* for its identity here rather
        than handed a sink, so no prompt can be assembled differently on the
        run where provenance was enabled.
        """
        if self._provenance is None or not hasattr(self._provenance, "record_context_selection"):
            return
        identity = self._compiler.selection_identity()
        selected = [block.label for block in compiled.blocks]
        # Per-layer token counts, not a layer tally: `L5` growing while `L1`
        # holds still is the signal a cache-cost regression looks like, and a
        # single integer erases it.
        layer_counts: dict[str, int] = {}
        for block in compiled.blocks:
            key = block.layer.value
            layer_counts[key] = layer_counts.get(key, 0) + block.token_estimate
        self._provenance.record_context_selection(
            identity=identity,
            candidate_digest=compiled.candidate_digest,
            selected_digest=compiled.digest,
            prefix_digest=compiled.prefix_digest,
            selected=selected, dropped=compiled.dropped, elided=compiled.elided,
            tokens=compiled.total_tokens, layer_counts=layer_counts, turn=turn)
        self._provenance.record_compaction(
            identity=identity,
            input_digest=compiled.candidate_digest,
            output_digest=compiled.digest,
            dropped=compiled.dropped, elided=compiled.elided,
            tokens_before=compiled.candidate_tokens,
            tokens_after=compiled.total_tokens, turn=turn)


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
    child_runtime: Any = None
    #: `M-6`. The runtime that executes child episodes. `None` is legal for a
    #: composition that never declares `agent.spawn`; for one that does, the
    #: binding fails closed at composition rather than substituting a fake.
    child_runtime: ChildRuntimePort | None = None


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

        repo = Path(task.repo_path)
        self.repo = repo
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

        self.scope = _scope_for(harness)
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
            approval_required_above="low",
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
        if discovered_env:
            env_parts.append(discovered_env)
        if self.index is not None:
            files_res = self.index.files()
            if files_res.ok and files_res.value is not None:
                symbols_res = self.index.symbols()
                slist = list(symbols_res.value) if symbols_res.ok and symbols_res.value is not None else []
                sym_by_file: dict[str, list[str]] = {}
                for s in slist:
                    sym_by_file.setdefault(s.path, []).append(f"{s.kind} {s.name}:{s.line}")
                lines = ["=== Workspace Repository Map ==="]
                if not files_res.value:
                    lines.append("- state: empty greenfield workspace")
                for f in files_res.value:
                    syms = sym_by_file.get(f, [])
                    if syms:
                        lines.append(f"- {f} ({', '.join(syms)})")
                    else:
                        lines.append(f"- {f}")
                env_parts.append("\n".join(lines))
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
        )

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
                "harness": self.harness.harness,
                "compositionDigest": self.harness.composition_digest,
                "activationDigest": getattr(self.run_plan, "activation_digest", ""),
                "runDigest": getattr(self.run_plan, "run_digest", ""),
                "taskDigest": getattr(self.run_plan, "task_digest", ""),
                "preregistrationDigest": getattr(
                    self.run_plan, "preregistration_digest", ""),
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
        while True:
            remaining = task.max_turns - self.turns_consumed()
            if remaining <= 0:
                terminal = RunTermination.ABANDONED
                detail = f"max_turns ({task.max_turns}) exhausted across approval"
                break
            self.policy.bind(authorization)
            engine = EpisodeEngine(
                kernel=self, model=self.operator, clock=ports.clock,
                events=delayed, scope=self.scope, tools=harness.tool_schemas,
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

        Empty on the legacy path, and deliberately so: `assemble_trajectory`
        renders an absent artifact index and a null capture status rather than
        synthesising a complete one, so a run that captured nothing says that
        instead of claiming it captured everything it was asked to.
        """
        if self.artifacts is None:
            return {}
        provenance = self.provenance.trajectory_provenance()
        return {
            "artifact_index": list(self.artifacts.index_entries()),
            "context_provenance": provenance["context"],
            "compaction_provenance": provenance["compaction"],
            "cache_provenance": provenance["cache"],
            "capture_status": self.artifacts.capture_state(),
        }

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


def _admit_turn_result(operator: _LayeredOperator, turn: int, result: Any) -> Span | None:
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
