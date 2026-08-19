"""Budget reservation, commit and release. Six-dimension Reservation (ADR-M0-07)."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping

from layer0.spi.types_gen import Reservation

__all__ = ["BudgetDenied", "Governor", "Lease", "LeaseState", "Reservation"]


class LeaseState(str, Enum):
    OPEN = "open"
    COMMITTED = "committed"
    RELEASED = "released"


class BudgetDenied(Exception):
    def __init__(self, dimension: str, requested: int, remaining: int, reason: str) -> None:
        super().__init__(f"{reason}: {dimension} requested {requested}, remaining {remaining}")
        self.dimension = dimension
        self.requested = requested
        self.remaining = remaining
        self.reason = reason


@dataclass(slots=True)
class Lease:
    lease_id: str
    run_id: str
    reserved: Mapping[str, int]
    parent_lease_id: str | None = None
    state: LeaseState = LeaseState.OPEN
    actual: Mapping[str, int] = field(default_factory=dict)
    settlement: Mapping[str, int] = field(default_factory=dict)


class Governor:
    def __init__(self, ceilings: Mapping[str, int]) -> None:
        self._ceilings = dict(ceilings)
        self._spent: dict[str, int] = {key: 0 for key in ceilings}
        self._held: dict[str, int] = {key: 0 for key in ceilings}
        self._leases: dict[str, Lease] = {}
        self._counter = 0

    def remaining(self, dimension: str) -> int:
        return self._ceilings.get(dimension, 0) - self._spent.get(dimension, 0) \
            - self._held.get(dimension, 0)

    def spent(self, dimension: str) -> int:
        return self._spent.get(dimension, 0)

    def ledger(self) -> Mapping[str, Mapping[str, int]]:
        return {
            dimension: {
                "ceiling": ceiling,
                "spent": self._spent.get(dimension, 0),
                "held": self._held.get(dimension, 0),
                "remaining": self.remaining(dimension),
            }
            for dimension, ceiling in self._ceilings.items()
        }

    def reserve(self, run_id: str, reservation: Reservation,
                parent_lease_id: str | None = None) -> Lease:
        if parent_lease_id is not None:
            parent = self._leases.get(parent_lease_id)
            if parent is None or parent.state is not LeaseState.OPEN:
                raise BudgetDenied("parent_lease", 0, 0, "parent_closed")
        wanted = {key: value for key, value in reservation.as_map().items() if value}
        for dimension, amount in wanted.items():
            if amount > self.remaining(dimension):
                raise BudgetDenied(dimension, amount, self.remaining(dimension), "denied")
        self._counter += 1
        lease = Lease(
            lease_id=f"lease-{self._counter}",
            run_id=run_id,
            reserved=dict(wanted),
            parent_lease_id=parent_lease_id,
        )
        for dimension, amount in wanted.items():
            self._held[dimension] = self._held.get(dimension, 0) + amount
        self._leases[lease.lease_id] = lease
        return lease

    def commit(self, lease: Lease, actual: Mapping[str, int]) -> Mapping[str, int]:
        if lease.state is not LeaseState.OPEN:
            raise BudgetDenied("lease", 0, 0, "commit_on_closed_lease")
        settlement: dict[str, int] = {}
        dimensions = set(lease.reserved) | set(actual)
        for dimension in dimensions:
            reserved = lease.reserved.get(dimension, 0)
            spent = actual.get(dimension, 0)
            settlement[dimension] = reserved - spent
            self._held[dimension] = self._held.get(dimension, 0) - reserved
            self._spent[dimension] = self._spent.get(dimension, 0) + spent
        lease.actual = dict(actual)
        lease.settlement = settlement
        lease.state = LeaseState.COMMITTED
        return settlement

    def release(self, lease: Lease) -> None:
        if lease.state is LeaseState.RELEASED:
            return
        if lease.state is LeaseState.OPEN:
            for dimension, amount in lease.reserved.items():
                self._held[dimension] = self._held.get(dimension, 0) - amount
        lease.state = LeaseState.RELEASED

    def is_open(self, lease_id: str) -> bool:
        lease = self._leases.get(lease_id)
        return lease is not None and lease.state is LeaseState.OPEN
