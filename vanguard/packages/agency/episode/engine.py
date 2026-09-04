"""The episode loop: observe -> propose -> authorise -> effect -> receipt.

`VG-03 §6.1` with the two reading notes made structural:

* **Emission is split.** The loop appends `ProposalProduced` itself because
  proposal production happens *outside* the dispatch sequence. Grants,
  denials, budget events, intent and receipts are appended by the kernel, so
  this module never emits them — and never writes a durable intent of its own.
* **No evaluator is invoked.** An episode terminates; it does not grade itself
  (`ICD §3`). `agency` cannot import an evaluator, and the run-termination axis
  here carries no evaluation verdict (`VG-03 §6.2`).

There is exactly one path from a proposal to an effect and it is
`Kernel.dispatch` (`05 §2.1`, `AT-01`). This module builds an `EffectRequest`
and hands it over; it issues no grant, opens no lease, and resolves no denial.

Recursion (`S8-B-01`): when a proposal requests `spawn`, the engine delegates
to `spawn()`, executing an attenuated child episode under budget conservation
and returning a value-only outcome (ADR-0060).

The provider is consumed structurally (`propose(context, tools, sampling)`
returning a typed result — `ICD §4`). It is annotated `Any` on purpose: the
`ModelPort` interface lives in `ports`, and declaring a second one here would
be a second port.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Mapping, Sequence

from ...domain.canonicalisation.digest import digest_of
from ...kernel import (
    Accumulation,
    Constraints,
    EffectRequest,
    Event,
    FailurePath,
    Reservation,
    Scope,
    SinkClass,
    Span,
    Trust,
    attenuate,
)
from .protocol_recovery import (
    ProtocolRecoveryState,
    RecoveryDecision,
    recover_proposal,
)
from .admission_gate import AdmissionVerdict
from .tool_policy import ToolPolicy, derive_phase, resolve_tool_policy
from .state import (
    TERMINAL_FOR_KIND,
    Episode,
    Proposal,
    ProposalKind,
    ProposalMalformed,
    RunTermination,
    SpawnResult,
    Turn,
    parse_proposal,
)

__all__ = ["EpisodeEngine", "EpisodeOutcome", "SpawnResult"]


#: Failure paths that end the run, and the termination each reduces to
#: (`VG-03 §6.2`). Everything absent from this table is an *event the loop
#: reduces over and continues from* — `VG-03 §6.1`: denial is an event, not an
#: exception. A denied call that silently ended the run would make the denial
#: indistinguishable from a crash.
_TERMINAL_FOR_FAILURE: Mapping[FailurePath, RunTermination] = {
    FailurePath.APPROVAL_SUSPENDED: RunTermination.ESCALATED,
    FailurePath.BUDGET_DENIED: RunTermination.BUDGET_EXHAUSTED,
    FailurePath.PARENT_LEASE_CLOSED: RunTermination.BUDGET_EXHAUSTED,
    FailurePath.CANCELLED: RunTermination.CANCELLED,
    FailurePath.INTENT_APPEND_FAILED: RunTermination.RUNTIME_ERROR,
    FailurePath.COMMIT_FAILED: RunTermination.RUNTIME_ERROR,
    FailurePath.CLASSIFIER_ERROR: RunTermination.RUNTIME_ERROR,
}

#: Reservation dimension names as they arrive in a proposal (`CT-06`, `CT-07`).
_RESERVATION_FIELDS = {
    "usd_micros": "usd_micros",
    "millis": "millis",
    "tokens": "tokens",
    "bytes": "bytes_",
}

#: Provider telemetry fields safe to carry into a durable event. Deliberately
#: excludes "text" and any argument payload: those may reference a secret or
#: task content, and `REQ-TRUST-001` requires zero secrets in events. Everything
#: here is either a token count, a cost figure, or a resolved identifier — the
#: instrument's own bookkeeping, never the model's answer.
_DIAGNOSTIC_FIELDS = (
    "usage",
    "resolved_model",
    "model_fingerprint",
    "cost_usd",
    "usd_micros",
    "pricing_known",
    "pricing_source",
)


def _extract_diagnostics(raw_value: Any) -> Mapping[str, Any]:
    """Pull provider/translator telemetry off a raw proposal value (`M-4 Approach A`).

    `parse_proposal` only reads `kind`/`action`/`args`/... and silently drops
    everything else, so the token usage, resolved model name, and cost the
    adapter already computed (`openrouter.py`'s `_complete`) never reached a
    durable event. This is why the canonical runtime could not answer "what
    did the provider actually say" from the ledger alone.
    """
    if not isinstance(raw_value, Mapping):
        return {}
    return {field: raw_value[field] for field in _DIAGNOSTIC_FIELDS if field in raw_value}


@dataclass(frozen=True, slots=True)
class EpisodeOutcome:
    """What the run did. Not what it was worth — that axis is exterior."""

    episode: Episode
    dispatches: tuple[Any, ...] = ()
    recovery_state: ProtocolRecoveryState = ProtocolRecoveryState()

    @property
    def terminal(self) -> RunTermination:
        assert self.episode.terminal is not None  # the loop only returns terminal states
        return self.episode.terminal


def _parse_child_scope(raw_scope: Any, parent: Scope) -> Scope | None:
    """Build child Scope from model proposal args["scope"]. Fail-closed on missing/junk."""
    if isinstance(raw_scope, Scope):
        return raw_scope
    if not isinstance(raw_scope, Mapping):
        return None

    actions_raw = raw_scope.get("actions")
    if actions_raw is None:
        return None
    if isinstance(actions_raw, (list, tuple, set, frozenset)):
        if not all(isinstance(a, str) and a for a in actions_raw):
            return None
        actions = frozenset(actions_raw)
    else:
        return None

    resources_raw = raw_scope.get("resources")
    if resources_raw is None:
        resources = parent.resources
    elif isinstance(resources_raw, (list, tuple)):
        if not all(isinstance(r, Mapping) for r in resources_raw):
            return None
        resources = tuple(dict(r) for r in resources_raw)
    else:
        return None

    constraints_raw = raw_scope.get("constraints")
    if constraints_raw is None:
        constraints = parent.constraints
    elif isinstance(constraints_raw, Constraints):
        constraints = constraints_raw
    elif isinstance(constraints_raw, Mapping):
        try:
            constraints = Constraints(
                expires_at=constraints_raw.get("expires_at") or constraints_raw.get("expiresAt") or parent.constraints.expires_at,
                max_uses=int(constraints_raw["max_uses"]) if "max_uses" in constraints_raw else (int(constraints_raw["maxUses"]) if "maxUses" in constraints_raw else parent.constraints.max_uses),
                budget_usd_micros=int(constraints_raw["budget_usd_micros"]) if "budget_usd_micros" in constraints_raw else (int(constraints_raw["budgetUsdMicros"]) if "budgetUsdMicros" in constraints_raw else parent.constraints.budget_usd_micros),
                max_depth=int(constraints_raw["max_depth"]) if "max_depth" in constraints_raw else (int(constraints_raw["maxDepth"]) if "maxDepth" in constraints_raw else parent.constraints.max_depth),
                network_policy=str(constraints_raw.get("network_policy") or constraints_raw.get("networkPolicy") or parent.constraints.network_policy),
            )
        except (ValueError, TypeError, KeyError):
            return None
    else:
        return None

    return Scope(
        actions=actions,
        resources=resources,
        constraints=constraints,
        depth=parent.depth,
    )


class EpisodeEngine:
    """Runs one episode against one kernel. Holds no authority of its own."""

    def __init__(
        self,
        *,
        kernel: Any,
        model: Any,
        clock: Any,
        events: Any,
        scope: Scope,
        tools: Sequence[Mapping[str, Any]] = (),
        sampling: Mapping[str, Any] | None = None,
        max_turns: int = 8,
        no_progress_limit: int = 3,
        sink_class: SinkClass = SinkClass.PRIVILEGED,
        parent_lease: str | None = None,
        attenuated: bool = False,
        spawn_dispatcher: Any = None,
        preset_mode: str | None = None,
        protocol_decoders: Sequence[Any] = (),
        patch_detector: Any = None,
        truncation_detector: Any = None,
        completion_admitter: Any = None,
        completion_allowed_tools: Sequence[str] | None = None,
    ) -> None:
        self._kernel = kernel
        #: True when this engine runs a spawned child under a narrowed grant.
        self._attenuated = attenuated
        self._model = model
        self._clock = clock
        self._events = events
        self._scope = scope
        self._tools = tuple(dict(tool) for tool in tools)
        self._sampling = dict(sampling or {})
        self._max_turns = max_turns
        self._no_progress_limit = no_progress_limit
        self._sink_class = sink_class
        self._parent_lease = parent_lease
        # Runtime injects this callback for the production path.  Direct
        # agency tests keep the historical in-process child seam until their
        # caller explicitly supplies the mediated dispatcher.
        self._spawn_dispatcher = spawn_dispatcher
        #: Preset intent forwarded to the tool-policy resolver (`ADR-0106 §4`).
        #: `None` keeps the engine generic (no phase gating) — the phase
        #: ladder is preset semantics and must be explicitly declared by the
        #: composition root, never assumed by the loop (`ADR-0060`).
        self._preset_mode = preset_mode
        #: Injected dialect-decoding pipeline (`ADR-0106 §3`). Agency never
        #: imports pack middleware directly; the composition root supplies
        #: the decoders, keeping the dependency direction intact.
        self._protocol_decoders = tuple(protocol_decoders)
        self._patch_detector = patch_detector
        self._truncation_detector = truncation_detector
        #: Optional composition seam. Agency records the model's finish
        #: proposal, while the harness pack supplies task-specific admission
        #: facts (patch and verification). No coding policy is imported here.
        self._completion_admitter = completion_admitter
        # Runtime may narrow the advertised tools after redundant successful
        # verification.  This is an offer-set restriction only; the kernel
        # remains the authority if a model proposes anything else.
        self._completion_allowed_tools = (
            frozenset(str(item) for item in completion_allowed_tools)
            if completion_allowed_tools is not None else None)

    # ------------------------------------------------------------------

    def run(
        self,
        *,
        episode_id: str,
        run_id: str,
        principal: str,
        brief: str = "",
        spans: Sequence[Span] = (),
        depth: int = 1,
        is_cancelled: Any = None,
        receipt_labeller: Any = None,
        prior_turns: Sequence[Turn] = (),
        prior_seen_verbs: Sequence[str] = (),
        prior_recovery_state: ProtocolRecoveryState | None = None,
    ) -> EpisodeOutcome:
        """Reduce turns until the episode is terminal. It always terminates.

        `receipt_labeller` is how a receipt re-enters the next turn's
        justification. It is injected rather than written here because a span's
        trust is set by its **source class at construction** and never by a
        judgement made at a call site (`K-30`, `K-31`). The accumulated set
        also grows across turns and is never reset: resetting it each round is
        exactly the defect `VG-03 §6.5` records, where the injection defence
        became unreachable dead code.

        `prior_turns` carries the turn history of earlier segments of the same
        episode. A run that suspends for approval re-enters through a *new*
        engine (`session.py`), and without this the episode's whole memory of
        what it had already done was discarded on every approval round-trip:
        turn indices restarted at 0, and no-progress detection could never
        accumulate the consecutive history it needs. The bound stays a bound on
        the episode, not on each segment of it -- the caller sizes `max_turns`
        to include what `prior_turns` already spent.
        """
        episode = Episode(episode_id=episode_id, run_id=run_id,
                          principal=principal, brief=brief, depth=depth,
                          turns=tuple(prior_turns))
        dispatches: list[Any] = []
        accumulated: tuple[Span, ...] = tuple(spans)
        recovery_state = prior_recovery_state or ProtocolRecoveryState()
        recovery_feedback: dict[str, Any] | None = None
        sampling_override: dict[str, Any] | None = None
        #: Repeated-action escalation (`CMX-03`). Tracked across turns because
        #: a livelock is a property of the *sequence* of proposals, not of any
        #: one of them.
        repeat_count = 0
        forced_tool_policy: ToolPolicy | None = None
        # Phase is derived from the verbs already attempted. Like the turn
        # history, this must survive the engine being rebuilt around an
        # approval suspension: without it the ladder snapped back to `inspect`
        # mid-run and un-offered the very tool the model was already using --
        # `patch.apply` suspends for approval, so the turn straight after a
        # patch lost the patch tool and failed as an undeclared-tool error.
        seen_verbs: set[str] = {str(v) for v in prior_seen_verbs if v}
        for span in accumulated:
            span_verb = getattr(span, "verb", None) or getattr(span, "action", None)
            if span_verb:
                seen_verbs.add(str(span_verb))
        declared_tool_names = {
            str(tool.get("verb") or tool.get("name"))
            for tool in self._tools
            if isinstance(tool, Mapping) and (tool.get("verb") or tool.get("name"))
        }
        allowed_tool_names = tuple(sorted(declared_tool_names))

        def _apply_retry(decision: RecoveryDecision, *,
                         base_sampling: Mapping[str, Any]) -> bool:
            """Record one bounded recovery retry turn.

            Returns False when the retry itself shows no progress; the caller
            must then break out of the loop with the terminated episode.
            """
            nonlocal episode, recovery_feedback, sampling_override
            turn = Turn(
                index=episode.turn_count,
                state_digest=episode.state_digest(),
                proposal_descriptor=digest_of({
                    "recovery_retry": decision.retry_reason,
                    "feedback": dict(decision.retry_feedback),
                }),
                receipt_digest=None,
                progress_signal=f"recovery_{decision.retry_reason}",
            )
            if episode.repeats(turn, limit=self._no_progress_limit):
                episode = episode.terminated(
                    RunTermination.ABANDONED,
                    f"no progress over {self._no_progress_limit} turns",
                )
                return False
            episode = episode.with_turn(turn)
            # The retry must be observable by the next model request, or the
            # provider repeats the identical malformed output until the
            # no-progress bound abandons the run (`ADR-0106 §3`).
            recovery_feedback = {
                **dict(decision.retry_feedback),
                "reason": decision.retry_reason,
            }
            self._emit_recovery_state(episode, recovery_state)
            if decision.continuation:
                base_tokens = int(base_sampling.get("maxTokens", 4096) or 4096)
                if 0 < base_tokens < 8192:
                    sampling_override = {**base_sampling, "maxTokens": base_tokens * 2}
            return True

        while not episode.is_terminal:
            if is_cancelled is not None and is_cancelled():
                episode = episode.terminated(RunTermination.CANCELLED,
                                             "cancelled before proposal")
                break
            if episode.turn_count >= self._max_turns:
                episode = episode.terminated(
                    RunTermination.ABANDONED,
                    f"turn bound {self._max_turns} reached")
                break

            # The turn is a fact once it is committed to, which is here --
            # after the cancellation and turn-bound guards, so a turn that
            # never ran is never recorded as started. Emitting above the
            # guards would make the ledger's turn count disagree with the
            # episode's on every cancelled or bounded run.
            self._events.emit(Event(
                kind="TurnStarted",
                reason="turn_opened",
                at=self._clock.now(),
                run_id=episode.run_id,
                principal=principal,
                payload={
                    "episodeId": episode.episode_id,
                    "turn": episode.turn_count,
                    "maxTurns": self._max_turns,
                },
            ))

            # -- observe ------------------------------------------------
            # State-dependent phase (`ADR-0106 §4`), only for presets that
            # declared one; the generic engine stays ungated (`ADR-0060`).
            if self._preset_mode is not None:
                phase = derive_phase(seen_verbs)
                policy = resolve_tool_policy(phase, preset_mode=self._preset_mode)
            else:
                phase, policy = "inspect", None
            # A tool set narrowed by the escalation ladder outranks the phase
            # ladder: the phase policy is what the model was already ignoring.
            if forced_tool_policy is not None:
                policy = forced_tool_policy
            offered_tools = self._tools
            turn_sampling = dict(sampling_override or self._sampling)
            if policy is not None and policy.mode == "required" and policy.allowed:
                filtered = tuple(
                    tool for tool in self._tools
                    if str(tool.get("verb") or tool.get("name") or "") in policy.allowed)
                if filtered:
                    offered_tools = filtered
                turn_sampling["toolChoice"] = "required"
            if self._completion_allowed_tools is not None:
                narrowed = tuple(
                    tool for tool in offered_tools
                    if str(tool.get("verb") or tool.get("name") or "")
                    in self._completion_allowed_tools)
                if narrowed:
                    offered_tools = narrowed
                turn_sampling["toolChoice"] = "required"
            view = self._view(episode, recovery_feedback=recovery_feedback)

            # -- propose ------------------------------------------------
            try:
                result = self._model.propose(view, offered_tools, turn_sampling)
            except Exception as exc:
                # `ICD §4`: a provider failure is a typed value. A provider
                # that raises anyway is still an instrument error, never a
                # task verdict (`VG-03 §6.2`).
                episode = episode.terminated(RunTermination.INSTRUMENT_ERROR, str(exc))
                self._emit_terminal(episode, "instrument_error", str(exc))
                break
            raw_value = getattr(result, "value", None)
            diagnostics = _extract_diagnostics(raw_value)
            if not getattr(result, "ok", False):
                error = getattr(result, "error", None)
                reason = (getattr(error, "message", "")
                          or "provider returned no proposal")
                episode = episode.terminated(RunTermination.INSTRUMENT_ERROR, reason)
                self._emit_terminal(episode, "instrument_error", reason, diagnostics=diagnostics)
                break
            try:
                proposal = parse_proposal(raw_value)
            except ProposalMalformed as exc:
                decision, recovery_state = recover_proposal(
                    raw_value,
                    recovery_state,
                    allowed_tools=allowed_tool_names,
                    decoders=self._protocol_decoders,
                    patch_detector=self._patch_detector,
                    truncation_detector=self._truncation_detector,
                )
                if decision.status == "accept" and decision.proposal is not None:
                    proposal = decision.proposal
                elif decision.status == "retry_model":
                    if not _apply_retry(decision, base_sampling=turn_sampling):
                        break
                    continue
                else:
                    episode = episode.terminated(RunTermination.INSTRUMENT_ERROR, str(exc))
                    self._emit_terminal(episode, "instrument_error", str(exc), diagnostics=diagnostics)
                    break

            # A recovery-fed turn was observed by this request; clear it so
            # only the turn immediately after a retry carries feedback.
            recovery_feedback = None
            sampling_override = None

            # -- repeated-action escalation (`CMX-03`) -------------------
            # A model proposing the identical effect turn after turn is
            # livelocked: the receipt it already holds is the one it would get
            # again. Interrupt *before* dispatch, so the loop stops paying for
            # the effect as well as the turn, and escalate rather than abandon
            # on the first repeat — corrective feedback first, then a tool set
            # that no longer offers the verb it cannot stop calling.
            if proposal.kind == ProposalKind.EFFECT:
                # The streak is read back off the episode's own turn history,
                # not held in a local counter, so it survives the engine being
                # rebuilt around an approval suspension -- which is exactly
                # when a livelocked run used to lose its memory and start over.
                #
                # Re-proposing an action whose last dispatch did *not* succeed
                # is legitimate retry, not livelock: the receipt it holds is a
                # failure, and the next attempt may well differ. Only an action
                # that keeps succeeding identically is stuck.
                #
                # Counted over a *window*, not as a strict consecutive run. A
                # livelocked model rarely repeats one call cleanly: nudged, it
                # varies for a turn and then falls straight back. A trailing
                # streak resets on that one different turn and the guard never
                # escalates, which is exactly what was observed live.
                window = [t for t in episode.turns
                          if not str(t.progress_signal).startswith("recovery_")]
                window = window[-(2 * self._no_progress_limit):]
                same = [t for t in window
                        if t.proposal_descriptor == proposal.descriptor]
                # Livelock is "the outcome stopped changing", not "the outcome
                # was ok". An action that keeps suspending for approval, or
                # keeps being denied identically, is just as stuck as one that
                # keeps succeeding identically -- and approval-suspended
                # repeats are what a real run actually produces, because every
                # privileged effect round-trips through approval. If the
                # outcome *did* move between attempts the signatures differ,
                # which is the legitimate-retry carve-out.
                if same and all(t.signature == same[-1].signature for t in same):
                    repeat_count = len(same) + 1
                else:
                    repeat_count = 1
                if repeat_count == 1:
                    forced_tool_policy = None
                if repeat_count >= self._no_progress_limit:
                    # Two bounds, because they catch different shapes. The
                    # window bound catches a model that keeps *dispatching* the
                    # same call; the retry bound catches one that keeps
                    # proposing it after being blocked, which adds nudge turns
                    # but no new dispatches for the window to count.
                    if (repeat_count >= 2 * self._no_progress_limit
                            or recovery_state.effect_retries
                            >= recovery_state.max_effect_retries):
                        detail = (f"repeated action {proposal.action} over "
                                  f"{repeat_count} turns")
                        episode = episode.terminated(RunTermination.ABANDONED, detail)
                        self._emit_terminal(episode, "abandoned", detail)
                        break
                    recovery_state = recovery_state.with_effect_retry()
                    # Guarded: never narrow to an empty set, which would strand
                    # the episode with nothing left to propose.
                    narrowed = tuple(sorted(declared_tool_names - {proposal.action}))
                    if narrowed:
                        forced_tool_policy = ToolPolicy(mode="required", allowed=narrowed)
                    if not _apply_retry(
                        RecoveryDecision(
                            status="retry_model",
                            retry_reason="REPEATED_ACTION",
                            retry_feedback={
                                "repeatedAction": proposal.action,
                                "repeatCount": repeat_count,
                                "lastReceiptDigest": (
                                    episode.turns[-1].receipt_digest
                                    if episode.turns else None),
                                "message": (
                                    f"You have proposed {proposal.action} with the "
                                    f"same arguments {repeat_count} times. It already "
                                    "returned a result — read that result and take "
                                    "the next distinct step."
                                ),
                            },
                        ),
                        base_sampling=turn_sampling,
                    ):
                        break
                    continue

            # -- state-dependent tool policy at the request boundary -----
            # (`ADR-0106 §4`). Only actions the harness itself declares are
            # phase-constrained; anything else remains a kernel authority
            # matter (I4/I12). Bounded: once protocol retries are exhausted
            # the proposal proceeds and the kernel fail-closes, so this gate
            # cannot deadlock the episode.
            if (policy is not None
                    and proposal.kind == ProposalKind.EFFECT
                    and policy.mode == "required" and policy.allowed
                    and proposal.action in declared_tool_names
                    and proposal.action not in policy.allowed
                    and recovery_state.protocol_retries < recovery_state.max_protocol_retries):
                recovery_state = recovery_state.with_protocol_retry()
                if not _apply_retry(
                    RecoveryDecision(
                        status="retry_model",
                        retry_reason="DISALLOWED_TOOL_PHASE",
                        retry_feedback={
                            "allowed_tools": list(policy.allowed),
                            "requested": proposal.action,
                            "phase": phase,
                        },
                    ),
                    base_sampling=turn_sampling,
                ):
                    break
                continue

            self._emit_proposal(episode, proposal, diagnostics=diagnostics)
            # -- a non-effect proposal reduces straight to a terminal ----
            terminal = TERMINAL_FOR_KIND.get(proposal.kind)
            if terminal is not None:
                if (proposal.kind == ProposalKind.FINISH
                        and self._completion_admitter is not None):
                    verdict = self._completion_admitter(episode, proposal)
                    if not isinstance(verdict, AdmissionVerdict):
                        raise TypeError("completion_admitter must return AdmissionVerdict")
                    if not verdict.admissible:
                        if not _apply_retry(
                            RecoveryDecision(
                                status="retry_model",
                                retry_reason="COMPLETION_ADMISSION_REJECTED",
                                retry_feedback={
                                    "admissionReason": verdict.reason,
                                    "feedback": verdict.rejection_feedback or verdict.reason,
                                },
                            ),
                            base_sampling=turn_sampling,
                        ):
                            break
                        continue
                episode = episode.terminated(terminal, proposal.note)
                break

            # -- spawn proposal runs an attenuated child episode (S8-B-01 / ADR-0060) --
            if proposal.kind == ProposalKind.SPAWN or proposal.action in ("agency.spawn", "spawn"):
                raw_scope = proposal.args.get("scope")
                child_scope = _parse_child_scope(raw_scope, self._scope)
                if child_scope is None:
                    # Fail-closed: missing or unparseable scope produces a typed failure, never parent's full grant
                    turn = Turn(
                        index=episode.turn_count,
                        state_digest=episode.state_digest(),
                        proposal_descriptor=proposal.descriptor,
                        receipt_digest=digest_of({
                            "spawn": False,
                            "detail": "missing or unparseable child scope (fail-closed)",
                            "payload": None,
                        }),
                        progress_signal="scope_unparseable",
                    )
                    repeats = episode.repeats(turn, limit=self._no_progress_limit)
                    episode = episode.with_turn(turn)
                    if repeats:
                        episode = episode.terminated(
                            RunTermination.ABANDONED,
                            f"no progress over {self._no_progress_limit} turns",
                        )
                        break
                    continue

                child_brief = str(proposal.args.get("brief") or proposal.note or "")
                if self._spawn_dispatcher is not None:
                    request = self._to_effect_request(episode, proposal, accumulated)
                    outcome = self._spawn_dispatcher(request)
                    dispatches.append(outcome)
                    if receipt_labeller is not None:
                        label = receipt_labeller(episode.turn_count, outcome)
                        if label is not None:
                            accumulated = accumulated + (label,)
                    spawn_res = SpawnResult(
                        ok=outcome.failure is FailurePath.OK,
                        payload=(outcome.outcome.result_digest
                                 if outcome.outcome is not None else None),
                        terminal=(RunTermination.COMPLETED
                                  if outcome.failure is FailurePath.OK
                                  else RunTermination.ABANDONED),
                        detail=outcome.detail,
                    )
                else:
                    spawn_res = self.spawn(
                        child_scope=child_scope,
                        brief=child_brief,
                        episode_id=f"{episode.episode_id}.child.{episode.turn_count}",
                        run_id=episode.run_id,
                        principal=episode.principal,
                        parent_episode_id=episode.episode_id,
                        parent_lease=self._parent_lease,
                    )
                if spawn_res.return_spans:
                    accumulated = Accumulation(accumulated).extend(spawn_res.return_spans).spans
                turn = Turn(
                    index=episode.turn_count,
                    state_digest=episode.state_digest(),
                    proposal_descriptor=proposal.descriptor,
                    receipt_digest=digest_of({
                        "spawn": spawn_res.ok,
                        "detail": spawn_res.detail,
                        "payload": spawn_res.payload,
                    }),
                    progress_signal="ok" if spawn_res.ok else "spawn_denied",
                )
                repeats = episode.repeats(turn, limit=self._no_progress_limit)
                episode = episode.with_turn(turn)
                if not spawn_res.ok and "depth ceiling" in spawn_res.detail:
                    episode = episode.terminated(RunTermination.ABANDONED, spawn_res.detail)
                    break
                if repeats:
                    episode = episode.terminated(
                        RunTermination.ABANDONED,
                        f"no progress over {self._no_progress_limit} turns",
                    )
                    break
                continue

            # -- defence in depth for an attenuated child ----------------
            # `S8-B-01`. ADR-0067 also enforces sealed action membership in
            # kernel policy. This earlier refusal keeps the child loop concise
            # and records a durable local denial; it is not the authority
            # boundary. RF-26 proves policy still denies if this pre-filter is
            # absent or bypassed.
            #
            # Scoped to children on purpose. A depth-0 episode's relationship
            # to its own scope is the kernel's business, and it already records
            # those refusals as events (`F-09`); intercepting them here would
            # replace a recorded denial with a silent skip, which is the
            # `A-07` failure mode. Kernel policy remains the final check for a
            # sealed child grant.
            #
            # Generic over the action set: no verb is named, so `ADR-0060`
            # holds and adding a domain is still zero lines in this file.
            if self._attenuated and proposal.action not in self._scope.actions:
                # `TSK-CORE-004`: this refuse has no kernel dispatch behind
                # it (`self._kernel.dispatch` is never called), so unlike the
                # F-09/F-10 denials the kernel records for its own path,
                # nothing durable existed for this one -- only the local
                # `Turn`. Append `AuthorizationDenied` so the ledger carries
                # it too, not only in-memory episode state (`A-07`).
                self._emit_scope_escalation_denied(episode, proposal)
                turn = Turn(
                    index=episode.turn_count,
                    state_digest=episode.state_digest(),
                    proposal_descriptor=proposal.descriptor,
                    receipt_digest=digest_of({
                        "denied": "scope_escalation",
                        "action": proposal.action,
                    }),
                    progress_signal="scope_escalation_denied",
                )
                repeats = episode.repeats(turn, limit=self._no_progress_limit)
                episode = episode.with_turn(turn)
                if repeats:
                    episode = episode.terminated(
                        RunTermination.ABANDONED,
                        f"no progress over {self._no_progress_limit} turns",
                    )
                    break
                continue

            # -- authorise + effect + receipt, through the one path ------
            request = self._to_effect_request(episode, proposal, accumulated)
            outcome = self._kernel.dispatch(
                request,
                requested_scope=self._scope,
                reservation=self._reservation(proposal),
            )
            dispatches.append(outcome)
            # The phase advances from an *attempted* effect (`ADR-0106 §4`):
            # a denied dispatch still proves the workflow moved past the
            # earlier phase, and verify-phase allowances (proc.exec) must be
            # reachable after a patch attempt regardless of its outcome.
            seen_verbs.add(str(proposal.action))

            if receipt_labeller is not None:
                label = receipt_labeller(episode.turn_count, outcome)
                if label is not None:
                    accumulated = accumulated + (label,)

            turn = Turn(
                index=episode.turn_count,
                state_digest=episode.state_digest(),
                proposal_descriptor=proposal.descriptor,
                receipt_digest=(outcome.outcome.result_digest
                                if outcome.outcome is not None else None),
                progress_signal=outcome.failure.name.lower(),
            )
            repeats = episode.repeats(turn, limit=self._no_progress_limit)
            episode = episode.with_turn(turn)

            terminal = _TERMINAL_FOR_FAILURE.get(outcome.failure)
            if terminal is not None:
                episode = episode.terminated(terminal, outcome.detail)
                break
            if repeats:
                if recovery_state.effect_retries < recovery_state.max_effect_retries:
                    recovery_state = recovery_state.with_effect_retry()
                    if _apply_retry(
                        RecoveryDecision(
                            status="retry_model",
                            retry_reason="NO_PROGRESS_RECOVERY",
                            retry_feedback={
                                "repeatedAction": proposal.action,
                                "message": (
                                    f"Action {proposal.action} produced no new state change. "
                                    "Inspect the workspace files or apply your bugfix patch next."
                                ),
                            },
                        ),
                        base_sampling=turn_sampling,
                    ):
                        continue
                episode = episode.terminated(
                    RunTermination.ABANDONED,
                    f"no progress over {self._no_progress_limit} turns")
                break

        return EpisodeOutcome(episode=episode, dispatches=tuple(dispatches),
                              recovery_state=recovery_state)

    # ------------------------------------------------------------------

    def _view(self, episode: Episode, *,
              recovery_feedback: Mapping[str, Any] | None = None) -> Mapping[str, Any]:
        """The materialised view a turn observes. Nothing else is readable."""
        view: dict[str, Any] = {
            "episodeId": episode.episode_id,
            "runId": episode.run_id,
            "brief": episode.brief,
            "turn": episode.turn_count,
            "stateDigest": episode.state_digest(),
            "lastReceiptDigest": (episode.turns[-1].receipt_digest
                                  if episode.turns else None),
            "lastProgressSignal": (episode.turns[-1].progress_signal
                                   if episode.turns else None),
        }
        if recovery_feedback is not None:
            view["recoveryFeedback"] = dict(recovery_feedback)
        return view

    def _emit_terminal(self, episode: Episode, outcome: str, detail: str,
                       diagnostics: Mapping[str, Any] | None = None) -> None:
        """`EpisodeCompleted` — record a termination that produced no turn (`C-01`).

        The three paths above end an episode *before* `_emit_proposal`, so a
        provider that timed out, raised, or answered with a shape the
        translator refuses left **no event at all**. The ledger showed an
        episode that never happened, and a refused batch of tool calls was
        indistinguishable from a model that was never asked (`A-07`,
        `REQ-TRUST-001`).

        This emits the terminal the episode actually reached, using the
        existing `EpisodeCompleted` kind the reducer already understands. It is
        not a turn -- no turn occurred -- and it opens no second store.

        `diagnostics`, when present, is whatever provider telemetry survived
        to this point (`_extract_diagnostics`) — e.g. usage/cost on a
        malformed-proposal instrument error, so the ledger records the
        instrument still answered even though its answer was unusable.
        """
        payload: dict[str, Any] = {
            "episodeId": episode.episode_id,
            "outcome": outcome,
            "turn": episode.turn_count,
            # The refusal reason, which is the whole point of the event.
            "detail": detail,
        }
        if diagnostics:
            payload["diagnostics"] = dict(diagnostics)
        self._events.emit(Event(
            kind="EpisodeCompleted",
            reason=outcome,
            at=self._clock.now(),
            run_id=episode.run_id,
            principal=episode.principal,
            payload=payload,
        ))

    def _emit_recovery_state(self, episode: Episode,
                             state: ProtocolRecoveryState) -> None:
        """Persist retry spend through the existing event authority.

        Recovery is execution state, not a second ledger.  Emitting the
        serialised state alongside the ordinary episode stream lets a fresh
        process restore retry decisions before it asks the provider again.
        """
        try:
            self._events.emit(Event(
                # Reuse the canonical episode-state event; recovery is state
                # belonging to this episode, not a new event authority.
                kind="EpisodeStateChanged",
                reason="protocol_recovery",
                at=self._clock.now(),
                run_id=episode.run_id,
                principal=episode.principal,
                payload={"episodeId": episode.episode_id,
                         "recoveryState": state.to_dict()},
            ))
        except Exception:
            # Recovery telemetry must not turn a handled retry into a runtime
            # failure; the append-only event stream remains best effort here.
            pass

    def _emit_scope_escalation_denied(self, episode: Episode, proposal: Proposal) -> None:
        """`AuthorizationDenied` for the engine-side sealed-scope refuse.

        Distinct writer from the kernel's own `F-09`/`F-10` denials -- this
        fires before `Kernel.dispatch` is ever called, so it is the only
        durable record a scope-escalating child proposal gets (`TSK-CORE-004`,
        `A-07`).
        """
        event = Event(
            kind="AuthorizationDenied",
            reason="scope_escalation",
            at=self._clock.now(),
            run_id=episode.run_id,
            principal=episode.principal,
            payload={
                "episodeId": episode.episode_id,
                "turn": episode.turn_count,
                "action": proposal.action,
                "proposalDescriptor": proposal.descriptor,
            },
        )
        try:
            self._events.emit(event)
        except Exception:
            # `F-25`: emission failure never fails the work it describes.
            pass

    def _emit_proposal(self, episode: Episode, proposal: Proposal,
                       diagnostics: Mapping[str, Any] | None = None) -> None:
        """`ProposalProduced` — the one event the loop appends itself.

        The payload carries the proposal *descriptor*, never its arguments: an
        argument may reference a secret, and `REQ-TRUST-001` requires zero
        secrets in events.

        `diagnostics` (`_extract_diagnostics`) adds the provider's own
        telemetry — token usage, resolved model, cost — that `parse_proposal`
        discards when it builds the `Proposal`. Without this the ledger could
        show a turn happened but never what it cost or which model actually
        answered (`M-4 Approach A`).
        """
        payload: dict[str, Any] = {
            "episodeId": episode.episode_id,
            "turn": episode.turn_count,
            "action": proposal.action,
            "proposalDescriptor": proposal.descriptor,
        }
        if proposal.note:
            payload["note"] = proposal.note[:8000]
        if diagnostics:
            payload["diagnostics"] = dict(diagnostics)
        event = Event(
            kind="ProposalProduced",
            reason=proposal.kind.value,
            at=self._clock.now(),
            run_id=episode.run_id,
            principal=episode.principal,
            payload=payload,
        )
        try:
            self._events.emit(event)
        except Exception:
            # `F-25`: emission failure never fails the work it describes.
            pass

    def _to_effect_request(self, episode: Episode, proposal: Proposal,
                           spans: Sequence[Span]) -> EffectRequest:
        assert proposal.action is not None  # guaranteed by parse_proposal
        resource = dict(proposal.resource)
        if not resource and self._scope.resources:
            resource = dict(self._scope.resources[0])
        action = proposal.action
        if action in ("spawn", "agency.spawn"):
            action = "agent.spawn"
        return EffectRequest(
            action=action,
            resource=resource,
            args=dict(proposal.args),
            principal=episode.principal,
            run_id=episode.run_id,
            depth=episode.depth,
            justifying_spans=tuple(spans),
            parent_lease=self._parent_lease,
            declared_sink_class=self._sink_class,
            idempotency_key=proposal.idempotency_key,
        )

    def _reservation(self, proposal: Proposal) -> Reservation:
        fields = {
            _RESERVATION_FIELDS[name]: amount
            for name, amount in proposal.reservation.items()
            if name in _RESERVATION_FIELDS
        }
        return Reservation(**fields)

    def spawn(
        self,
        *,
        child_scope: Scope,
        brief: str,
        episode_id: str,
        run_id: str,
        principal: str,
        parent_episode_id: str | None = None,
        parent_lease: str | None = None,
        workspace: Any = None,
        workspace_factory: Any = None,
        max_turns: int | None = None,
        model: Any = None,
        tools: Sequence[Mapping[str, Any]] | None = None,
        sampling: Mapping[str, Any] | None = None,
        is_cancelled: Any = None,
    ) -> SpawnResult:
        """Spawn a recursive child episode under attenuated scope (S8-B-01).

        Child authority strictly narrows the parent. Budget is conserved across
        the tree. The return value is a typed SpawnResult containing text or
        structured data, never a mutable handle. Workspace is destroyed in
        finally (N-16).

        **Why the child engine is marked `attenuated`.** `attenuate()` seals a
        child grant when the parent withholds verbs. ADR-0067 closed the former
        membership gap: `StandardPolicy.authorize` now rejects an action absent
        from a sealed requested scope before approval. The engine also declines
        such proposals and records a durable denial as defence in depth, but it
        is not the authority boundary. RF-26 exercises kernel policy directly,
        so disabling or bypassing the engine-side refusal cannot restore the
        historical widening path.
        """
        # Depth check: recursion ceiling
        current_depth = self._scope.depth
        max_depth = self._scope.constraints.max_depth
        if current_depth >= max_depth:
            return SpawnResult(
                ok=False,
                terminal=RunTermination.ABANDONED,
                detail=f"depth ceiling {max_depth} reached",
            )

        # Attenuation check: child grant strictly narrows parent (K-26)
        attenuation = attenuate(self._scope, child_scope)
        if not attenuation.ok or attenuation.granted is None:
            denial_dim = attenuation.denial.dimension if attenuation.denial else "unknown"
            return SpawnResult(
                ok=False,
                terminal=RunTermination.ABANDONED,
                detail=f"attenuation denied on {denial_dim}",
            )

        granted_scope = replace(attenuation.granted, depth=current_depth + 1)

        # Filter tools to those in granted actions
        child_tools = tools if tools is not None else tuple(
            t for t in self._tools if str(t.get("verb") or t.get("name")) in granted_scope.actions
        )

        # Wrap events emitter with causationId
        parent_causation = parent_episode_id or getattr(self._events, "episode_id", None)
        child_events = _CausationEventAdapter(self._events, causation_id=parent_causation)

        branch_ws = workspace
        try:
            if branch_ws is None and workspace_factory is not None:
                branch_ws = workspace_factory()

            child_engine = EpisodeEngine(
                kernel=self._kernel,
                model=model or self._model,
                clock=self._clock,
                events=child_events,
                scope=granted_scope,
                tools=child_tools,
                sampling=sampling or self._sampling,
                max_turns=max_turns if max_turns is not None else self._max_turns,
                no_progress_limit=self._no_progress_limit,
                sink_class=self._sink_class,
                parent_lease=parent_lease or self._parent_lease,
                attenuated=True,
            )

            child_outcome = child_engine.run(
                episode_id=episode_id,
                run_id=run_id,
                principal=principal,
                brief=brief,
                depth=granted_scope.depth,
                is_cancelled=is_cancelled,
            )

            is_ok = child_outcome.terminal in (RunTermination.COMPLETED, RunTermination.ABSTAINED)
            # Child return payload is value-only text / note
            payload = child_outcome.episode.detail or child_outcome.episode.brief
            # `K-33`: the child's return value re-enters the parent's
            # accumulation as untrusted-derived at minimum, whatever trust the
            # child itself believed it held (`Accumulation.child_return`).
            return_spans = Accumulation().child_return(
                (Span(f"{episode_id}.return", Trust.AGENT_DERIVED, "spawn_return"),)
            ).spans
            return SpawnResult(
                ok=is_ok,
                payload=payload,
                terminal=child_outcome.terminal,
                detail=child_outcome.episode.detail,
                turns=child_outcome.episode.turn_count,
                return_spans=return_spans,
            )
        except Exception as exc:
            return SpawnResult(
                ok=False,
                terminal=RunTermination.RUNTIME_ERROR,
                detail=str(exc),
            )
        finally:
            if branch_ws is not None:
                if hasattr(branch_ws, "destroy"):
                    branch_ws.destroy()
                elif hasattr(branch_ws, "cleanup"):
                    branch_ws.cleanup()
                elif hasattr(branch_ws, "close"):
                    branch_ws.close()


class _CausationEventAdapter:
    """Wraps an event store/emitter to tag child events with causationId (S8-B-01)."""

    def __init__(self, target: Any, causation_id: str | None) -> None:
        self._target = target
        self.causation_id = causation_id

    def emit(self, event: Any) -> None:
        if self.causation_id:
            if hasattr(event, "payload") and isinstance(event.payload, Mapping):
                new_payload = dict(event.payload)
                if "causationId" not in new_payload:
                    new_payload["causationId"] = self.causation_id
                event = replace(event, payload=new_payload)
            elif hasattr(event, "data") and isinstance(event.data, Mapping):
                new_data = dict(event.data)
                if "causationId" not in new_data:
                    new_data["causationId"] = self.causation_id
                event = replace(event, data=new_data)
            if hasattr(event, "causation_id") and getattr(event, "causation_id", None) is None:
                try:
                    event = replace(event, causation_id=self.causation_id)
                except Exception:
                    pass
        if hasattr(self._target, "emit"):
            self._target.emit(event)
        elif hasattr(self._target, "append"):
            self._target.append(event)
