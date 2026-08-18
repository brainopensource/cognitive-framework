"""Hard budget controller and integer-microdollar accounting (REQ-TRUST-001, S32).

Enforces strict financial bounding on paid model calls. Uses integer microdollars
(1 USD = 1,000,000 microdollars) and worst-case pre-call reservation to provably
prevent spend overshoots. Never represents unknown pricing or missing usage as zero.
"""

from __future__ import annotations

import math
import uuid
from dataclasses import dataclass, field
from typing import Any, Mapping

__all__ = [
    "BudgetController",
    "BudgetExhaustedError",
    "PricingUnknownError",
    "Reservation",
    "ReservationResult",
]


class BudgetExhaustedError(RuntimeError):
    """Raised or returned when a call exceeds the microdollar or paid-call ceiling."""
    pass


class PricingUnknownError(RuntimeError):
    """Raised or returned when a model has no verified microdollar pricing."""
    pass


@dataclass(frozen=True, slots=True)
class Reservation:
    """An active worst-case token & cost reservation."""

    reservation_id: str
    requested_model: str
    resolved_model: str
    reserved_micros: int
    prompt_micros_per_1m: int
    completion_micros_per_1m: int
    cached_micros_per_1m: int
    max_prompt_tokens: int
    max_completion_tokens: int


@dataclass(frozen=True, slots=True)
class ReservationResult:
    """The result of attempting to reserve budget before a paid call."""

    ok: bool
    reservation: Reservation | None = None
    reason: str = ""
    error_kind: str | None = None


class BudgetController:
    """Manages pre-call cost reservation and post-call reconciliation."""

    def __init__(
        self,
        max_micros: int = 500_000,  # $0.50 default ceiling
        max_paid_calls: int = 20,
    ) -> None:
        if max_micros < 0:
            raise ValueError("max_micros cannot be negative")
        if max_paid_calls < 0:
            raise ValueError("max_paid_calls cannot be negative")

        self.max_micros = max_micros
        self.max_paid_calls = max_paid_calls

        self._spent_micros: int = 0
        self._active_reservations: dict[str, Reservation] = {}
        self._paid_calls_count: int = 0
        self._unattributed_usage_count: int = 0

    @property
    def spent_micros(self) -> int:
        return self._spent_micros

    @property
    def reserved_micros(self) -> int:
        return sum(r.reserved_micros for r in self._active_reservations.values())

    @property
    def committed_micros(self) -> int:
        return self._spent_micros + self.reserved_micros

    @property
    def remaining_micros(self) -> int:
        return max(0, self.max_micros - self.committed_micros)

    @property
    def paid_calls_count(self) -> int:
        return self._paid_calls_count

    @property
    def unattributed_usage_count(self) -> int:
        return self._unattributed_usage_count

    def reserve(
        self,
        *,
        requested_model: str,
        resolved_model: str,
        pricing: tuple[int, int, int] | None,  # (prompt_per_1m, completion_per_1m, cached_per_1m)
        max_prompt_tokens: int = 8192,
        max_completion_tokens: int = 4096,
    ) -> ReservationResult:
        """Reserve worst-case cost before dispatching a model request."""
        if not requested_model or not resolved_model:
            return ReservationResult(
                ok=False,
                reason="model_identity_missing",
                error_kind="instrument_error:model_identity_missing",
            )

        # Free tier models require 0 reservation and don't count toward paid calls
        is_free = (
            resolved_model == "openrouter/free"
            or resolved_model.endswith(":free")
            or resolved_model.startswith("mock")
        )
        if is_free:
            res = Reservation(
                reservation_id=f"free-{uuid.uuid4().hex[:8]}",
                requested_model=requested_model,
                resolved_model=resolved_model,
                reserved_micros=0,
                prompt_micros_per_1m=0,
                completion_micros_per_1m=0,
                cached_micros_per_1m=0,
                max_prompt_tokens=max_prompt_tokens,
                max_completion_tokens=max_completion_tokens,
            )
            self._active_reservations[res.reservation_id] = res
            return ReservationResult(ok=True, reservation=res)

        # Paid model: pricing must be explicitly known
        if pricing is None:
            return ReservationResult(
                ok=False,
                reason=f"unknown_pricing_for_{resolved_model}",
                error_kind="instrument_error:price_unknown",
            )

        prompt_rate, completion_rate, cached_rate = pricing

        # Check paid calls limit
        if self._paid_calls_count >= self.max_paid_calls:
            return ReservationResult(
                ok=False,
                reason=f"paid_calls_ceiling_reached_{self.max_paid_calls}",
                error_kind="budget_exhausted",
            )

        # Worst-case microdollar calculation
        worst_prompt_micros = math.ceil((max_prompt_tokens * prompt_rate) / 1_000_000)
        worst_completion_micros = math.ceil((max_completion_tokens * completion_rate) / 1_000_000)
        worst_case_total = worst_prompt_micros + worst_completion_micros

        if self.committed_micros + worst_case_total > self.max_micros:
            return ReservationResult(
                ok=False,
                reason=f"reservation_{worst_case_total}_exceeds_remaining_{self.remaining_micros}",
                error_kind="budget_exhausted",
            )

        res = Reservation(
            reservation_id=f"res-{uuid.uuid4().hex[:8]}",
            requested_model=requested_model,
            resolved_model=resolved_model,
            reserved_micros=worst_case_total,
            prompt_micros_per_1m=prompt_rate,
            completion_micros_per_1m=completion_rate,
            cached_micros_per_1m=cached_rate,
            max_prompt_tokens=max_prompt_tokens,
            max_completion_tokens=max_completion_tokens,
        )
        self._active_reservations[res.reservation_id] = res
        return ReservationResult(ok=True, reservation=res)

    def reconcile(
        self,
        reservation_id: str,
        *,
        actual_prompt_tokens: int | None,
        actual_completion_tokens: int | None,
        cached_tokens: int = 0,
    ) -> int:
        """Reconcile actual usage after a call, returning actual microdollars charged."""
        if reservation_id not in self._active_reservations:
            raise KeyError(f"Unknown reservation ID: {reservation_id}")

        res = self._active_reservations.pop(reservation_id)

        # Free tier
        if res.reserved_micros == 0:
            return 0

        self._paid_calls_count += 1

        # Missing token usage telemetry
        if actual_prompt_tokens is None or actual_completion_tokens is None:
            self._unattributed_usage_count += 1
            # Retain the full reserved worst-case cost as safe conservative charge
            actual_charge = res.reserved_micros
            self._spent_micros += actual_charge
            return actual_charge

        # Integer calculation of actual cost
        prompt_cost = math.ceil(
            (max(0, actual_prompt_tokens - cached_tokens) * res.prompt_micros_per_1m) / 1_000_000
        )
        cached_cost = math.ceil(
            (cached_tokens * res.cached_micros_per_1m) / 1_000_000
        )
        completion_cost = math.ceil(
            (actual_completion_tokens * res.completion_micros_per_1m) / 1_000_000
        )

        actual_charge = prompt_cost + cached_cost + completion_cost
        self._spent_micros += actual_charge
        return actual_charge

    def release(self, reservation_id: str) -> None:
        """Release an active reservation without charging if call was aborted."""
        self._active_reservations.pop(reservation_id, None)

    def to_dict(self) -> dict[str, Any]:
        return {
            "maxMicros": self.max_micros,
            "spentMicros": self._spent_micros,
            "reservedMicros": self.reserved_micros,
            "committedMicros": self.committed_micros,
            "remainingMicros": self.remaining_micros,
            "paidCallsCount": self._paid_calls_count,
            "maxPaidCalls": self.max_paid_calls,
            "unattributedUsageCount": self._unattributed_usage_count,
        }
