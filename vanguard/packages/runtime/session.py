"""One run: session wiring and lifecycle (`2.2-C`).

`HarnessSession` is the one kernel the engine sees for a run. It does not
compose a harness and it does not write envelopes except through
`LedgerEmitter`.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
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
from ..domain.ledger.reducer import compute_state_digest, reconstruct_state
from ..domain.ledger.state import LedgerState
from ..kernel import (
    EffectRequest,
    Event,
    FailurePath,
    GrantIssuer,
    Governor,
    HeldAuthority,
    Kernel,
    Mode,
    StandardClassifier,
    StandardPolicy,
    Span,
)
from ..ports.determinism import RandomPort
from ..ports.evaluator import EvaluationProtocol, RunRef, Verdict
from ..ports.event_store import EventRange, EventStorePort
from ..ports.index import IndexPort
from .compose import (
    Harness,
    Receipt,
    RunResult,
    TaskContext,
)
from .evaluator_gateway import record_verdict
from .ledger.recovery import RecoveryScanner
from .ledger_emitter import LedgerEmitter
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
        return self._model.propose(bundle, tools, sampling)



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

        self.adapters = {
            verb: harness.bindings[verb].factory(
                BindingContext(verb=verb, environment=ports.environment, repo_path=repo))
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

        self.scope = _scope_for(harness)
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
            scanner.reconcile_open_intents(ports.store, occurred_at=ports.clock.now())
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

        from ..domain.ledger.events import EventEnvelope
        from ..domain.ledger.reducer import reduce_event
        pending_env = EventEnvelope(
            schema_version="mhf.event/1",
            event_id="pending-terminal",
            scope="episode",
            seq=str(self.ledger._seq),
            occurred_at=delayed.pending.at,
            recorded_at=delayed.pending.at,
            principal=task.principal,
            principal_role="episode",
            tenant_id="tenant-default",
            owner_id="owner-platform",
            confidentiality="internal",
            retention_class="extended",
            trainability="prohibited",
            redaction_status="none",
            payload=delayed.pending.payload,
            run_id=task.run_id,
            episode_id=task.episode_id,
        )
        final_state_digest = compute_state_digest(reduce_event(self.ledger_state(), pending_env))

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
        )
        delayed.flush(trajectory)
        if isinstance(trajectory, dict):
            trajectory["state_digest"] = self.state_digest()
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
            state_digest=self.state_digest(),
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
