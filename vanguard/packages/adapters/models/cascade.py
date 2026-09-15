"""Cascading ModelPort adapter with fallback and escalation semantics.

Invariants:
- Implements ports.model.ModelPort.
- Strictly hexagonal: zero imports of kernel or agency.
- Tries primary model (e.g. fast local llama.cpp) first.
- Fails over cleanly to fallback/frontier model upon primary error, timeout, or exhaustion.
- Preserves typed Result[Proposal] semantics.
- Prices itself at the most expensive leg it may escalate to, so the runtime's
  USD ceiling bounds the *fallback* and not merely the primary.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from ...ports.event_store import PortFailure, Result
from ...ports.model import ContextBundle, ModelPort, Proposal, Sampling, ToolSchemas

__all__ = ["CascadingModel"]


class CascadingModel(ModelPort):
    """Cascading ModelPort that prioritizes primary model with failover to fallback."""

    def __init__(
        self,
        primary: ModelPort,
        fallback: ModelPort,
        *,
        max_primary_failures: int = 1,
        label: str = "cascade",
    ) -> None:
        self.primary = primary
        self.fallback = fallback
        self.max_primary_failures = max(1, max_primary_failures)
        self.label = label
        self._consecutive_primary_failures = 0
        self._total_primary_attempts = 0
        self._total_fallback_attempts = 0

    @property
    def consecutive_failures(self) -> int:
        return self._consecutive_primary_failures

    @property
    def total_primary_attempts(self) -> int:
        return self._total_primary_attempts

    @property
    def total_fallback_attempts(self) -> int:
        return self._total_fallback_attempts

    @property
    def pricing(self) -> tuple[int, int] | None:
        """Worst-case `(prompt, completion)` micro-USD per million tokens.

        The runtime reads this attribute to decide what a turn on this route
        may cost before the call (`runtime/session.py::_model_pricing`), and
        `InferenceMeter` reserves against it. A cascade exists precisely so a
        cheap primary can escalate to an expensive one, so pricing it at the
        primary would let the fallback overrun the declared `usd_micros`
        ceiling by the difference between the legs. The bound that holds for
        every outcome is the maximum across the legs; a reservation is a
        ceiling, not a forecast, and the unused remainder is refunded on
        commit.

        `None` means *unknown*, and never free (`RUN-12`): one unpriceable leg
        makes the whole route unpriceable, because the escalation that reaches
        it cannot be bounded in advance. Reading that leg as `0` would report a
        route that cannot be priced as one that can.
        """
        worst: tuple[int, int] | None = None
        for leg in (self.primary, self.fallback):
            leg_pricing = getattr(leg, "pricing", None)
            if not isinstance(leg_pricing, (tuple, list)) or len(leg_pricing) < 2:
                return None
            try:
                prompt, completion = int(leg_pricing[0]), int(leg_pricing[1])
            except (TypeError, ValueError):
                return None
            if prompt < 0 or completion < 0:
                return None
            worst = (prompt, completion) if worst is None else (
                max(worst[0], prompt), max(worst[1], completion))
        return worst

    def reset_failures(self) -> None:
        """Reset consecutive failure counter (e.g. between independent episodes)."""
        self._consecutive_primary_failures = 0

    def propose(
        self,
        context: ContextBundle,
        tools: ToolSchemas,
        sampling: Sampling,
    ) -> Result[Proposal]:
        """Propose an action using primary model, escalating to fallback if primary fails."""
        # If primary has exceeded consecutive failure threshold, bypass directly to fallback
        if self._consecutive_primary_failures >= self.max_primary_failures:
            self._total_fallback_attempts += 1
            return self.fallback.propose(context, tools, sampling)

        self._total_primary_attempts += 1
        res = self.primary.propose(context, tools, sampling)
        if res.ok and res.value is not None:
            self._consecutive_primary_failures = 0
            return res

        # Primary failed; record failure and attempt escalation
        self._consecutive_primary_failures += 1
        self._total_fallback_attempts += 1
        fallback_res = self.fallback.propose(context, tools, sampling)
        if fallback_res.ok and fallback_res.value is not None:
            # The fallback payload can report only its own usage.  The failed
            # primary may already have consumed resources, so presenting that
            # payload as complete would erase an attempt from the aggregate
            # episode budget.  The runtime meter treats this private marker as
            # unsettled and conservatively retains its reservation.
            proposal = dict(fallback_res.value)
            proposal["usage_complete"] = False
            return Result.success(proposal)

        # Both failed: return typed instrument error combining both failure details
        prim_err = res.error.message if res.error else "primary failure"
        fall_err = fallback_res.error.message if fallback_res.error else "fallback failure"
        return Result.fail(
            kind="instrument_error",
            message=f"Cascade exhausted: primary failed ({prim_err}); fallback failed ({fall_err})",
            retryable=False,
        )
