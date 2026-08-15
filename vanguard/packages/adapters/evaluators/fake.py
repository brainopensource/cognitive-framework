"""Deterministic EvaluatorPort fake. No ambient I/O and no OS identity."""

from __future__ import annotations

from typing import Mapping, Sequence

from ...ports.evaluator import EvaluationProtocol, RunRef, Verdict
from ...ports.event_store import Result

__all__ = ["FakeEvaluator"]


class FakeEvaluator:
    """Scripted verdicts. Instrument errors fail closed as `inconclusive`."""

    def __init__(
        self,
        verdicts: Mapping[str, Verdict] | None = None,
        instrument_errors: Sequence[str] = (),
    ) -> None:
        self._verdicts = dict(verdicts or {})
        self._instrument_errors = frozenset(instrument_errors)

    def evaluate(self, run_ref: RunRef, protocol: EvaluationProtocol) -> Result[Verdict]:
        del protocol
        if run_ref.run_id in self._instrument_errors:
            return Result.success(
                Verdict(outcome="inconclusive", reason="instrument_error")
            )
        verdict = self._verdicts.get(run_ref.run_id)
        if verdict is None:
            return Result.success(
                Verdict(outcome="inconclusive", reason="no scripted verdict")
            )
        return Result.success(verdict)
