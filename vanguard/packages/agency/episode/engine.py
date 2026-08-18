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


@dataclass(frozen=True, slots=True)
class EpisodeOutcome:
    """What the run did. Not what it was worth — that axis is exterior."""

    episode: Episode
    dispatches: tuple[Any, ...] = ()

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
    ) -> EpisodeOutcome:
        """Reduce turns until the episode is terminal. It always terminates.

        `receipt_labeller` is how a receipt re-enters the next turn's
        justification. It is injected rather than written here because a span's
        trust is set by its **source class at construction** and never by a
        judgement made at a call site (`K-30`, `K-31`). The accumulated set
        also grows across turns and is never reset: resetting it each round is
        exactly the defect `VG-03 §6.5` records, where the injection defence
        became unreachable dead code.
        """
        episode = Episode(episode_id=episode_id, run_id=run_id,
                          principal=principal, brief=brief, depth=depth)
        dispatches: list[Any] = []
        accumulated: tuple[Span, ...] = tuple(spans)

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

            # -- observe ------------------------------------------------
            view = self._view(episode)

            # -- propose ------------------------------------------------
            try:
                result = self._model.propose(view, self._tools, self._sampling)
            except Exception as exc:
                # `ICD §4`: a provider failure is a typed value. A provider
                # that raises anyway is still an instrument error, never a
                # task verdict (`VG-03 §6.2`).
                episode = episode.terminated(RunTermination.INSTRUMENT_ERROR, str(exc))
                self._emit_terminal(episode, "instrument_error", str(exc))
                break
            if not getattr(result, "ok", False):
                error = getattr(result, "error", None)
                reason = (getattr(error, "message", "")
                          or "provider returned no proposal")
                episode = episode.terminated(RunTermination.INSTRUMENT_ERROR, reason)
                self._emit_terminal(episode, "instrument_error", reason)
                break
            try:
                proposal = parse_proposal(getattr(result, "value", None))
            except ProposalMalformed as exc:
                episode = episode.terminated(RunTermination.INSTRUMENT_ERROR, str(exc))
                self._emit_terminal(episode, "instrument_error", str(exc))
                break

            self._emit_proposal(episode, proposal)

            # -- a non-effect proposal reduces straight to a terminal ----
            terminal = TERMINAL_FOR_KIND.get(proposal.kind)
            if terminal is not None:
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

            # -- an attenuated child may not exceed its granted actions ---
            # `S8-B-01`. The scope a child holds is the whole content of the
            # word "attenuated": a child narrowed to a subset of verbs that can
            # still request the others has not been attenuated, it has been
            # relabelled.
            #
            # Scoped to children on purpose. A depth-0 episode's relationship
            # to its own scope is the kernel's business, and it already records
            # those refusals as events (`F-09`); intercepting them here would
            # replace a recorded denial with a silent skip, which is the
            # `A-07` failure mode. A child's grant has no such recorded check,
            # because the classifier consults the principal's held authority
            # rather than the episode's current scope -- see the note on
            # `spawn`.
            #
            # Generic over the action set: no verb is named, so `ADR-0060`
            # holds and adding a domain is still zero lines in this file.
            if self._attenuated and proposal.action not in self._scope.actions:
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
                # `VG-03 §6.4`: the same transition without a change in state
                # or progress signal, for the configured limit.
                episode = episode.terminated(
                    RunTermination.ABANDONED,
                    f"no progress over {self._no_progress_limit} turns")
                break

        return EpisodeOutcome(episode=episode, dispatches=tuple(dispatches))

    # ------------------------------------------------------------------

    def _view(self, episode: Episode) -> Mapping[str, Any]:
        """The materialised view a turn observes. Nothing else is readable."""
        return {
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

    def _emit_terminal(self, episode: Episode, outcome: str, detail: str) -> None:
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
        """
        self._events.emit(Event(
            kind="EpisodeCompleted",
            reason=outcome,
            at=self._clock.now(),
            run_id=episode.run_id,
            principal=episode.principal,
            payload={
                "episodeId": episode.episode_id,
                "outcome": outcome,
                "turn": episode.turn_count,
                # The refusal reason, which is the whole point of the event.
                "detail": detail,
            },
        ))

    def _emit_proposal(self, episode: Episode, proposal: Proposal) -> None:
        """`ProposalProduced` — the one event the loop appends itself.

        The payload carries the proposal *descriptor*, never its arguments: an
        argument may reference a secret, and `REQ-TRUST-001` requires zero
        secrets in events.
        """
        event = Event(
            kind="ProposalProduced",
            reason=proposal.kind.value,
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

    def _to_effect_request(self, episode: Episode, proposal: Proposal,
                           spans: Sequence[Span]) -> EffectRequest:
        assert proposal.action is not None  # guaranteed by parse_proposal
        resource = dict(proposal.resource)
        if not resource and self._scope.resources:
            resource = dict(self._scope.resources[0])
        return EffectRequest(
            action=proposal.action,
            resource=resource,
            args=dict(proposal.args),
            principal=episode.principal,
            run_id=episode.run_id,
            depth=episode.depth,
            justifying_spans=tuple(spans),
            parent_lease=self._parent_lease,
            declared_sink_class=self._sink_class,
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

        **Why the child engine is marked `attenuated`.** `attenuate()` narrows
        the child's `Scope`, but narrowing the scope is not by itself enough to
        stop the child acting outside it: `StandardPolicy.authorize` attenuates
        `requested_scope` against the policy's parent and never checks that
        `request.action` is a member of `requested_scope.actions`, and the
        classifier's widening predicate is computed against the *principal's
        held authority* rather than the episode's current scope. So a child
        narrowed to a read verb was still authorised for any verb the principal
        held -- measured end to end, a child narrowed to one read verb reached
        a privileged adapter.

        The child engine therefore refuses to emit a request outside its own
        granted actions. That is a containment the engine can enforce without
        holding authority: it is declining to *ask*, not deciding an answer.
        Closing the same gap inside the kernel is a `kernel/` change and needs
        its own ADR (`ADR-0054`); it is reported, not made here.
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
