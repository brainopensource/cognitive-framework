"""Cascading ModelPort adapter with fallback and escalation semantics.

Invariants:
- Implements ports.model.ModelPort.
- Strictly hexagonal: zero imports of kernel or agency.
- Tries primary model (e.g. fast local llama.cpp) first.
- Fails over cleanly to fallback/frontier model upon primary error, timeout, or exhaustion.
- Preserves typed Result[Proposal] semantics.
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
        if fallback_res.ok:
            return fallback_res

        # Both failed: return typed instrument error combining both failure details
        prim_err = res.error.message if res.error else "primary failure"
        fall_err = fallback_res.error.message if fallback_res.error else "fallback failure"
        return Result.fail(
            kind="instrument_error",
            message=f"Cascade exhausted: primary failed ({prim_err}); fallback failed ({fall_err})",
            retryable=False,
        )
