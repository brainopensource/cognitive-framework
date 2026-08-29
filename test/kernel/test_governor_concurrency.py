"""EVO-07/EVO-14: `Governor` must conserve budget under concurrent access.

Owning contract: VANGUARD_090_BACKEND_AUDIT_AND_EVOLUTION_PLAN.md EVO-14
("budget conservation" under concurrent lineage execution).

`reserve()` was check-then-act on `_held` with no lock: two threads could
both pass the ceiling check against a stale `remaining()` read and both
commit, oversubscribing the ceiling. This is exactly what "concurrency
changes scheduling only... must never bypass kernel authorization" rules
out -- an unenforced ceiling is a bypassed one. `Governor` now serializes
`reserve`/`commit`/`release` internally so callers dispatching from multiple
threads (a future concurrent scheduler) get the same conservation guarantee
a sequential caller already has.
"""

from __future__ import annotations

import threading
import time
import unittest
from unittest.mock import patch

from vanguard.packages.kernel.budget import BudgetDenied, Governor, Reservation


class GovernorConservesBudgetUnderConcurrentReservation(unittest.TestCase):
    def test_the_check_then_act_window_is_provably_closed_by_the_lock(self) -> None:
        """CPython's GIL makes the natural race window too narrow to hit
        reliably by chance -- a passing unlocked run would prove nothing. This
        widens the window deliberately (a delay between the ceiling check and
        the `_held` mutation, exactly where `reserve` used to be unguarded)
        and shows the lock -- which serializes the *entire* `reserve` call,
        not just the mutation -- prevents two threads from ever being inside
        that window together."""
        governor = Governor({"usd_micros": 10})
        real_remaining = Governor.remaining

        def _slow_remaining(self, dimension):
            value = real_remaining(self, dimension)
            time.sleep(0.02)  # hold the window open long enough to guarantee overlap
            return value

        results: list[bool] = []
        lock = threading.Lock()
        barrier = threading.Barrier(2)

        def _try_reserve() -> None:
            barrier.wait()
            try:
                governor.reserve("run-race", Reservation(usd_micros=10))
            except BudgetDenied:
                with lock:
                    results.append(False)
            else:
                with lock:
                    results.append(True)

        with patch.object(Governor, "remaining", _slow_remaining):
            t1 = threading.Thread(target=_try_reserve)
            t2 = threading.Thread(target=_try_reserve)
            t1.start()
            t2.start()
            t1.join(timeout=5)
            t2.join(timeout=5)

        self.assertEqual(
            results, [True, False] if results[0] else [False, True],
            "with the ceiling fully consumed by whichever reservation goes first, "
            "the second must be denied -- if the lock did not serialize the whole "
            "check-then-act sequence, both would have read the pre-reservation "
            "remaining() and both would have succeeded",
        )
        self.assertEqual(governor.remaining("usd_micros"), 0)

    def test_concurrent_reservations_never_oversubscribe_the_ceiling(self) -> None:
        """100 threads each try to reserve 1 unit against a ceiling of 50.
        Exactly 50 must succeed -- concurrency must not let more through
        than a sequential caller could have gotten."""
        governor = Governor({"usd_micros": 50})
        granted: list[object] = []
        denied: list[BudgetDenied] = []
        lock = threading.Lock()
        barrier = threading.Barrier(100)

        def _try_reserve(i: int) -> None:
            barrier.wait()  # maximize actual concurrent overlap
            try:
                lease = governor.reserve(f"run-{i}", Reservation(usd_micros=1))
            except BudgetDenied as exc:
                with lock:
                    denied.append(exc)
            else:
                with lock:
                    granted.append(lease)

        threads = [threading.Thread(target=_try_reserve, args=(i,)) for i in range(100)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=10)

        self.assertEqual(len(granted), 50, "exactly the ceiling's worth of reservations must succeed")
        self.assertEqual(len(denied), 50)
        self.assertEqual(governor.remaining("usd_micros"), 0)

    def test_concurrent_commit_and_release_leave_spent_plus_remaining_at_ceiling(self) -> None:
        """K-07 conservation: for every dimension, spent + held + remaining
        equals the ceiling at all times -- proven here after a concurrent
        mix of commits (with overrun) and releases, not just a sequential one."""
        ceiling = 1000
        governor = Governor({"usd_micros": ceiling})
        leases = [governor.reserve(f"run-{i}", Reservation(usd_micros=10)) for i in range(50)]
        barrier = threading.Barrier(len(leases))

        def _settle(i: int, lease) -> None:
            barrier.wait()
            if i % 2 == 0:
                governor.commit(lease, {"usd_micros": 12})  # overrun on purpose
            else:
                governor.release(lease)

        threads = [threading.Thread(target=_settle, args=(i, lease)) for i, lease in enumerate(leases)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=10)

        spent = governor.spent("usd_micros")
        remaining = governor.remaining("usd_micros")
        # 25 commits at 12 each = 300 spent; 25 releases return their 10 held each.
        self.assertEqual(spent, 25 * 12)
        self.assertEqual(spent + remaining, ceiling)


if __name__ == "__main__":
    unittest.main()
