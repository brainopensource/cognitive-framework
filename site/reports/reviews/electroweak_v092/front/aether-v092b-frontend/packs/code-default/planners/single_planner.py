"""plan → patch → verify loop. Escalates Free→Cheap→Frontier on signed verdict_fail."""

from __future__ import annotations

from typing import ClassVar, Sequence

from vanguard.packages.domain.wire.result import Err, Ok, Result
from vanguard.packages.domain.wire.types_gen import (
    EffectRequest,
    EpisodeOutcome,
    EpisodeView,
    GateDecision,
    Proposal,
    Receipt,
    Reflection,
    Reservation,
    SignedVerdict,
    SinkClass,
    TrajectoryRef,
)
from vanguard.packages.kernel.budget import BudgetDenied, Governor
from vanguard.packages.kernel.budget import Reservation as _GovernorReservation

import sys
from pathlib import Path

_PACK = Path(__file__).resolve().parents[1]
if str(_PACK) not in sys.path:
    sys.path.insert(0, str(_PACK))

from reservation import is_free_model, worst_case_reservation  # noqa: E402

__all__ = ["DriveUntilGreenPlanner", "TIERS"]

TIERS = ("free", "cheap", "frontier")


class DriveUntilGreenPlanner:
    spi_version: ClassVar[str] = "1.0"

    def __init__(
        self,
        *,
        governor: Governor,
        max_repair_rounds: int = 4,
        model_routes: Sequence[str] = ("mock:free", "mock:cheap", "mock:frontier"),
    ) -> None:
        self._governor = governor
        self._max_repair_rounds = max_repair_rounds
        self._routes = tuple(model_routes) or ("mock:free",)
        self._tier = 0
        self._round = 0
        self._observed: list[Receipt] = []
        self.last_model = self._routes[0]

    def plan(self, view: EpisodeView, budget: Reservation) -> Result[Proposal]:
        if self._round >= self._max_repair_rounds:
            return Err("attempts_exhausted", "max_repair_rounds reached")
        if budget.turns <= 0:
            return Err("budget_exhausted", "no turns remaining")
        model = self._routes[min(self._tier, len(self._routes) - 1)]
        self.last_model = model
        try:
            reserved = worst_case_reservation(
                model=model if not is_free_model(model) else "mock:free",
                pricing=None if is_free_model(model) or model.startswith("mock") else (140_000, 280_000, 14_000),
                turns=1,
                depth=1,
            )
            # `Governor.reserve()` (`vanguard/packages/kernel/budget.py`)
            # refuses any dimension outside its additive set -- `turns`/
            # `depth` are structural ceilings, not conserved costs (ADR-0074
            # §2, 2.2-A), and `reserved` above is the wire `Reservation`
            # shape `EffectRequest.reservation` needs, turns/depth included.
            # The governor gets only the four it actually accounts for.
            self._governor.reserve(view.run_id, _GovernorReservation(
                usd_micros=reserved.usd_micros, millis=reserved.millis,
                tokens=reserved.tokens, bytes_=reserved.bytes))
        except BudgetDenied as exc:
            return Err("budget_exhausted", str(exc))
        self._round += 1
        thought = f"round {self._round} tier {TIERS[min(self._tier, 2)]} goal={view.goal}"
        request = EffectRequest(
            verb="patch.apply",
            args={"path": "src/app.py", "content": "# repair\n"},
            selector={"kind": "fs", "root": "/workspace", "paths": ["/workspace"]},
            sink=SinkClass.PRIVILEGED,
            reservation=reserved,
        )
        return Ok(Proposal(thought=thought, requests=(request,)))

    def observe(self, receipts: Sequence[Receipt], view: EpisodeView) -> None:
        _ = view
        self._observed.extend(receipts)

    def reflect(self, outcome: EpisodeOutcome, trajectory: TrajectoryRef) -> Result[Reflection | None]:
        _ = outcome, trajectory
        return Ok(None)

    def consume_verdicts(self, verdicts: Sequence[SignedVerdict], decision: GateDecision) -> None:
        if decision is GateDecision.RETRY or any(item.verdict.lower() == "fail" for item in verdicts):
            if self._tier < len(self._routes) - 1:
                self._tier += 1
        if decision is GateDecision.PASS:
            return
