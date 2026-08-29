"""Budget reservation, commit and release (`05 §2`, `K-07`).

The governor accounts for budget and holds **no opinion about policy**
(`01 §2`): it never denies because of an effect class, only because a
dimension is exhausted or a parent lease is closed.

`K-07` is the rule with teeth: commit debits reality, **including overruns**,
and the refund is `reserved − actual` *retained when negative*. Clamping the
refund at zero means an overrun is never debited and the ceiling never moves —
a run can then exceed its budget indefinitely, one small overrun at a time.
`MF-KRN-007` fails against the clamp.

Money is integer micro-units and durations are integer milliseconds
(`CT-06`, `CT-07`); there is no float anywhere in this module.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping

__all__ = ["BudgetDenied", "Governor", "Lease", "LeaseState", "Reservation"]


class LeaseState(str, Enum):
    OPEN = "open"
    COMMITTED = "committed"
    RELEASED = "released"


class BudgetDenied(Exception):
    """`F-12` / `F-13`. Carries the dimension so the denial can be recorded."""

    def __init__(self, dimension: str, requested: int, remaining: int, reason: str) -> None:
        super().__init__(f"{reason}: {dimension} requested {requested}, remaining {remaining}")
        self.dimension = dimension
        self.requested = requested
        self.remaining = remaining
        self.reason = reason


#: The conserved dimensions, and the whole of them (ADR-0074 §2). The
#: governor holds and sums exactly these. `depth` and `turns` are structural
#: ceilings enforced by attenuation (`Constraints.max_depth`) and by the
#: episode loop (`task.max_turns`) respectively -- summing either across
#: siblings is the `F-10` defect.
ADDITIVE_DIMENSIONS = frozenset({"usd_micros", "millis", "tokens", "bytes"})


@dataclass(frozen=True, slots=True)
class Reservation:
    """What a request asks to hold. Every dimension is an integer."""

    usd_micros: int = 0
    millis: int = 0
    tokens: int = 0
    bytes_: int = 0

    def as_map(self) -> Mapping[str, int]:
        # Additive conserved dimensions only (ADR-0074 §2). Structural
        # ceilings (depth, turns) are not costs and MUST NOT appear here:
        # sibling depths are never summed into remaining().
        return {"usd_micros": self.usd_micros, "millis": self.millis,
                "tokens": self.tokens, "bytes": self.bytes_}


@dataclass(slots=True)
class Lease:
    """An open reservation against a run's ceiling."""

    lease_id: str
    run_id: str
    reserved: Mapping[str, int]
    parent_lease_id: str | None = None
    state: LeaseState = LeaseState.OPEN
    actual: Mapping[str, int] = field(default_factory=dict)
    #: `reserved − actual` per dimension, negative when the effect overran.
    settlement: Mapping[str, int] = field(default_factory=dict)


class Governor:
    """Run-scoped budget accounting.

    State is explicit and inspectable because the must-fail tests assert on
    conservation: for every dimension, `spent + remaining` equals the ceiling
    at all times, including after an overrun.
    """

    def __init__(self, ceilings: Mapping[str, int]) -> None:
        self._ceilings = dict(ceilings)
        self._spent: dict[str, int] = {key: 0 for key in ceilings}
        self._held: dict[str, int] = {key: 0 for key in ceilings}
        self._leases: dict[str, Lease] = {}
        self._counter = 0
        # EVO-07/EVO-14: a caller may dispatch through one shared Governor
        # from more than one thread. `reserve` is check-then-act on `_held`;
        # unlocked, two threads can both pass the ceiling check on stale
        # `remaining()` reads and both commit, oversubscribing the ceiling
        # -- exactly the budget-conservation violation concurrency must not
        # introduce. See ADR-0105: defensive thread safety, not a
        # concurrency authorization (ADR-0099 remains SEQUENTIAL_CONFIRMED).
        self._lock = threading.Lock()

    # -- accounting -------------------------------------------------------

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

    # -- the sequence -----------------------------------------------------

    def reserve(self, run_id: str, reservation: Reservation,
                parent_lease_id: str | None = None) -> Lease:
        """S7 RESERVE. Raises `BudgetDenied` for `F-12` and `F-13`."""
        with self._lock:
            return self._reserve_locked(run_id, reservation, parent_lease_id)

    def _reserve_locked(self, run_id: str, reservation: Reservation,
                        parent_lease_id: str | None) -> Lease:
        if parent_lease_id is not None:
            parent = self._leases.get(parent_lease_id)
            if parent is None or parent.state is not LeaseState.OPEN:
                # `F-13`: a closed parent cannot fund a child.
                raise BudgetDenied("parent_lease", 0, 0, "parent_closed")
        # `F-10`, 2.2-A: the governor names its own dimensions rather than
        # trusting whatever `as_map()` hands it. `Reservation` is duck-typed
        # here, and the generated wire `Reservation` (`domain/wire/types_gen`)
        # is structurally interchangeable with this one while carrying `depth`
        # and `turns` -- holding those would sum sibling depths into
        # `remaining()`, which is exactly the defect the layer0 governor had.
        # Silently ignoring them would deny nothing but also enforce nothing;
        # refusing is the only reading that cannot hide a lost ceiling.
        offered = reservation.as_map()
        structural = sorted(set(offered) - ADDITIVE_DIMENSIONS)
        if structural:
            raise BudgetDenied(structural[0], offered[structural[0]], 0,
                               "not_a_conserved_dimension")
        wanted = {key: value for key, value in offered.items() if value}
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
        """S10 COMMIT. Debits reality, overruns included (`K-07`).

        Returns the settlement per dimension: `reserved − actual`, **retained
        when negative**. A negative settlement is an overrun that has been
        charged, not a refund that was skipped.
        """
        with self._lock:
            return self._commit_locked(lease, actual)

    def _commit_locked(self, lease: Lease, actual: Mapping[str, int]) -> Mapping[str, int]:
        if lease.state is not LeaseState.OPEN:
            raise BudgetDenied("lease", 0, 0, "commit_on_closed_lease")
        settlement: dict[str, int] = {}
        dimensions = set(lease.reserved) | set(actual)
        for dimension in dimensions:
            reserved = lease.reserved.get(dimension, 0)
            spent = actual.get(dimension, 0)
            # NOT max(reserved - spent, 0): clamping here is `MF-KRN-007`.
            settlement[dimension] = reserved - spent
            self._held[dimension] = self._held.get(dimension, 0) - reserved
            self._spent[dimension] = self._spent.get(dimension, 0) + spent
        lease.actual = dict(actual)
        lease.settlement = settlement
        lease.state = LeaseState.COMMITTED
        return settlement

    def release(self, lease: Lease) -> None:
        """S11 RELEASE. Runs on **every** path, including the exception path,
        and before any emission (`K-06`).

        Releasing an uncommitted lease returns the whole reservation: the
        effect never ran, so nothing was spent.
        """
        with self._lock:
            if lease.state is LeaseState.RELEASED:
                return
            if lease.state is LeaseState.OPEN:
                for dimension, amount in lease.reserved.items():
                    self._held[dimension] = self._held.get(dimension, 0) - amount
            lease.state = LeaseState.RELEASED

    def is_open(self, lease_id: str) -> bool:
        with self._lock:
            lease = self._leases.get(lease_id)
            return lease is not None and lease.state is LeaseState.OPEN
