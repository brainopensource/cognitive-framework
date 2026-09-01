"""Fail-closed evaluator used when the supervised peer is not configured."""

from __future__ import annotations

from ...ports.evaluator import EvaluationProtocol, EvaluatorPort, RunRef, Verdict
from ...ports.event_store import Result


class UnavailableEvaluator(EvaluatorPort):
    def __init__(self, reason: str = "evaluator_peer_unavailable") -> None:
        self.reason = reason

    def evaluate(self, run_ref: RunRef, protocol: EvaluationProtocol) -> Result[Verdict]:
        del run_ref, protocol
        return Result.success(Verdict(outcome="inconclusive", reason=self.reason))
