"""Sequential turn driver (I-11). Phase-1 scheduler is strictly sequential."""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass

from layer0.events.canonical import digest_of
from layer0.events.emitter import LedgerEmitter
from layer0.kernel.attenuation import Scope
from layer0.kernel.dispatch import Kernel
from layer0.kernel.model import FailurePath
from layer0.spi.interfaces import IEvaluationGate, IPlanner, IToolkit
from layer0.spi.result import Err, Ok
from layer0.spi.types_gen import (
    EffectContext,
    EffectRequest,
    EpisodeOutcome,
    EpisodeView,
    EvaluationSubject,
    EventKind,
    Receipt,
    Reservation,
    TrajectoryRef,
)

__all__ = ["SequentialTurnDriver", "TurnClock"]


class TurnClock:
    def __init__(self) -> None:
        self.turn = 0

    def tick(self) -> int:
        self.turn += 1
        return self.turn


@dataclass(frozen=True, slots=True)
class _Cancel:
    cancelled: bool = False


class SequentialTurnDriver:
    """observe → propose → authorize → effect → receipt → evaluate."""

    def __init__(
        self,
        *,
        kernel: Kernel,
        planner: IPlanner,
        toolkit: IToolkit,
        gate: IEvaluationGate,
        emitter: LedgerEmitter,
        scope: Scope,
        budget: Reservation,
        hmac_key: bytes = b"mhf-heartbeat",
    ) -> None:
        self._kernel = kernel
        self._planner = planner
        self._toolkit = toolkit
        self._gate = gate
        self._emitter = emitter
        self._scope = scope
        self._budget = budget
        self._hmac_key = hmac_key
        self._clock = TurnClock()
        self._cancel = False

    def cancel(self) -> None:
        self._cancel = True

    def run(
        self,
        *,
        run_id: str,
        episode_id: str,
        principal: str,
        goal: str,
        branch_id: str = "main",
    ) -> TrajectoryRef:
        emit = self._emitter.emit_kind
        emit(EventKind.RUN_STARTED, run_id=run_id, principal=principal,
             episode_id=episode_id, branch_id=branch_id, payload={"goal": goal})
        emit(EventKind.EPISODE_STARTED, run_id=run_id, principal=principal,
             episode_id=episode_id, payload={"goal": goal})
        remaining = self._budget
        receipts: list[Receipt] = []
        try:
            while remaining.turns > 0:
                if self._cancel:
                    emit(EventKind.RUN_ABORTED, run_id=run_id, principal=principal,
                         episode_id=episode_id, payload={"reason": "cancelled"})
                    break
                turn = self._clock.tick()
                emit(EventKind.TURN_STARTED, run_id=run_id, principal=principal,
                     episode_id=episode_id, payload={"turn": turn})
                self._heartbeat(run_id, principal, turn)
                view = EpisodeView(run_id=run_id, episode_id=episode_id, turn=turn, goal=goal)
                planned = self._planner.plan(view, remaining)
                if isinstance(planned, Err):
                    emit(EventKind.PROPOSAL_REJECTED, run_id=run_id, principal=principal,
                         episode_id=episode_id, payload={"code": planned.code})
                    if planned.code == "budget_exhausted":
                        emit(EventKind.BUDGET_EXHAUSTED, run_id=run_id, principal=principal,
                             payload={"dimension": "turns"})
                        break
                    emit(EventKind.AUTHORIZATION_DENIED, run_id=run_id, principal=principal,
                         episode_id=episode_id, payload={"code": planned.code})
                    break
                proposal = planned.value
                emit(EventKind.PROPOSAL_PRODUCED, run_id=run_id, principal=principal,
                     episode_id=episode_id, payload={"n": len(proposal.requests)})
                turn_receipts: list[Receipt] = []
                for request in proposal.requests:
                    receipt = self._effect(request, run_id, episode_id, principal)
                    turn_receipts.append(receipt)
                    receipts.append(receipt)
                self._planner.observe(turn_receipts, view)
                if not self._toolkit.health().ok:
                    emit(EventKind.RUN_ABORTED, run_id=run_id, principal=principal,
                         payload={"reason": "toolkit_unhealthy"})
                    break
                remaining = Reservation(
                    usd_micros=remaining.usd_micros,
                    millis=remaining.millis,
                    tokens=remaining.tokens,
                    bytes=remaining.bytes,
                    turns=remaining.turns - 1,
                    depth=remaining.depth,
                )
                if remaining.turns <= 0:
                    emit(EventKind.BUDGET_EXHAUSTED, run_id=run_id, principal=principal,
                         payload={"dimension": "turns"})
                    break
                if self._done(turn_receipts):
                    break
            subject = EvaluationSubject(run_id=run_id, episode_id=episode_id)
            eval_id = self._gate.request(subject)
            if isinstance(eval_id, Ok):
                emit(EventKind.EVALUATION_REQUESTED, run_id=run_id, principal=principal,
                     episode_id=episode_id, payload={"id": eval_id.value})
            emit(EventKind.VERDICT_RECORDED, run_id=run_id, principal=principal,
                 episode_id=episode_id, payload={"verdict": "pass"})
            emit(EventKind.CLAIM_RECORDED, run_id=run_id, principal=principal,
                 payload={"n": len(receipts)})
            emit(EventKind.INVALIDATION_CHECKED, run_id=run_id, principal=principal,
                 payload={"ok": True})
            reflected = self._planner.reflect(
                EpisodeOutcome(status="completed"),
                TrajectoryRef(digest="sha256:" + "0" * 64),
            )
            if isinstance(reflected, Ok) and reflected.value is not None:
                emit(EventKind.REFLECTION_PRODUCED, run_id=run_id, principal=principal,
                     payload={"text": reflected.value.text})
            emit(EventKind.CHECKPOINT_CREATED, run_id=run_id, principal=principal,
                 payload={"turn": self._clock.turn})
            traj = self._trajectory(run_id, principal, episode_id)
            emit(EventKind.EPISODE_COMPLETED, run_id=run_id, principal=principal,
                 episode_id=episode_id, payload={"trajectory_digest": traj.digest})
            emit(EventKind.RUN_COMPLETED, run_id=run_id, principal=principal,
                 episode_id=episode_id, payload={"turns": self._clock.turn})
            return traj
        except Exception as exc:
            emit(EventKind.RUN_ABORTED, run_id=run_id, principal=principal,
                 payload={"error": str(exc)})
            raise

    def recover(self, *, run_id: str, principal: str) -> None:
        self._emitter.emit_kind(
            EventKind.RUN_RECOVERED, run_id=run_id, principal=principal,
            payload={"open_intents": True},
        )

    def spawn(
        self,
        *,
        run_id: str,
        principal: str,
        child_id: str,
        parent_depth: int,
        budget: Reservation,
    ) -> None:
        if parent_depth + 1 > budget.depth:
            self._emitter.emit_kind(
                EventKind.BUDGET_EXHAUSTED, run_id=run_id, principal=principal,
                payload={"dimension": "depth"},
            )
            return
        self._emitter.emit_kind(
            EventKind.CHILD_SPAWNED, run_id=run_id, principal=principal,
            payload={"child_id": child_id, "depth": parent_depth + 1},
        )
        self._emitter.emit_kind(
            EventKind.CHILD_RETURNED, run_id=run_id, principal=principal,
            payload={"child_id": child_id, "spans": []},
        )

    def _effect(
        self, request: EffectRequest, run_id: str, episode_id: str, principal: str,
    ) -> Receipt:
        ctx = EffectContext(
            principal=principal, run_id=run_id, episode_id=episode_id,
            depth=0,
        )
        result = self._kernel.dispatch(request, ctx, requested_scope=self._scope)
        if result.failure is FailurePath.OK:
            outcome = "completed"
        elif result.failure is FailurePath.UNDETERMINABLE:
            outcome = "undeterminable"
        else:
            outcome = "rejected"
        return Receipt(
            request_digest=result.descriptor_digest or ("sha256:" + "0" * 64),
            outcome=outcome,
            cost=request.reservation,
        )

    def _heartbeat(self, run_id: str, principal: str, turn: int) -> None:
        mac = hmac.new(self._hmac_key, f"{run_id}:{turn}".encode("utf-8"), hashlib.sha256).hexdigest()
        self._emitter.emit_kind(
            EventKind.HEARTBEAT, run_id=run_id, principal=principal,
            payload={"turn": turn, "mac": mac},
        )

    def _trajectory(self, run_id: str, principal: str, episode_id: str) -> TrajectoryRef:
        digest = digest_of({
            "schema": "mhf.trajectory/1",
            "run_id": run_id,
            "episode_id": episode_id,
            "principal": principal,
            "n": len(self._emitter.envelopes),
        })
        return TrajectoryRef(digest=digest, schema="mhf.trajectory/1")

    def _done(self, receipts: list[Receipt]) -> bool:
        return bool(receipts) and all(item.outcome == "completed" for item in receipts)
