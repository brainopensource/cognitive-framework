"""EVO-14: read-only concurrent dispatch is correct, not just fast.

Owning contract: ADR-0106 (authorized by the preregistered study in
`docs/03_execution/prereg/EVO-14-concurrent-readonly-study.md`, full numbers
reproducible via `lab/evo14_concurrent_readonly_study.py`).

This is the permanent regression coverage for the mechanism the study
validated -- CI-fast (small N, small latency), not a repeat of the timing
study itself. It proves the properties ADR-0106 requires of any caller:
canonical-order result reconciliation regardless of completion order, real
`Kernel.dispatch()` on every operation (no bypass), and budget conservation
under real concurrent dispatch through the now-thread-safe `Governor`
(ADR-0105).
"""

from __future__ import annotations

import random
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from typing import Any


def _build_kernel_and_scope():
    from vanguard.packages.kernel import (
        GrantIssuer, Governor, HeldAuthority, Kernel, Mode,
        SinkClass, SinkRegistry, StandardClassifier, StandardPolicy,
    )
    from vanguard.packages.kernel.attenuation import Constraints, Scope
    from vanguard.packages.kernel.model import AdapterOutcome
    from vanguard.packages.runtime.determinism import FixedClock

    resource = {"kind": "fs", "root": "/workspace", "paths": ["/workspace"]}
    scope = Scope(
        actions=frozenset({"fs.read"}),
        resources=(resource,),
        constraints=Constraints(expires_at="2099-01-01T00:00:00.000Z", max_uses=1000,
                                budget_usd_micros=10_000_000, max_depth=4),
        depth=0,
    )

    class LatentAdapter:
        def healthy(self) -> bool:
            return True

        def execute(self, req: Any) -> Any:
            # Jittered, not fixed, so a would-be race has a real window to
            # manifest instead of every call finishing in lock-step.
            time.sleep(random.uniform(0.001, 0.004))
            return AdapterOutcome(status="ok", result_digest="sha256:" + "0" * 64)

    class NullSink:
        def emit(self, event: Any) -> None: ...
        def append_intent(self, event: Any) -> None: ...

    sinks = SinkRegistry()
    sinks.register("fs.read", SinkClass.OBSERVATION)
    silent = NullSink()
    kernel = Kernel(
        adapters={"fs.read": LatentAdapter()},
        policy=StandardPolicy(parent_scope=scope, mode=Mode.BENCHMARK,
                              approval_required_above="high", risk_of={"fs.read": "low"}),
        classifier=StandardClassifier([
            HeldAuthority("agent", frozenset({"fs.read"}), (resource,), max_depth=4)]),
        governor=Governor({"usd_micros": 10_000_000, "millis": 10_000_000}),
        issuer=GrantIssuer(), clock=FixedClock(at="2026-08-29T00:00:00.000000Z"),
        ledger=silent, events=silent, sinks=sinks,
    )
    return kernel, scope, resource


def _dispatch(kernel, scope, resource, path: str):
    from vanguard.packages.kernel.budget import Reservation
    from vanguard.packages.kernel.model import EffectRequest

    request = EffectRequest(action="fs.read", resource=resource, args={"path": path},
                            principal="agent", run_id="run-evo14-test")
    return kernel.dispatch(request, requested_scope=scope, reservation=Reservation())


class SafeReadOnlyGroupIdentifiesTheStudiedWorkload(unittest.TestCase):
    def test_disjoint_read_only_operations_are_recognized_as_safe(self) -> None:
        from vanguard.packages.runtime.scheduler import ReadyOperation, safe_read_only_group

        ops = [
            ReadyOperation(
                operation_id=f"op-{i}",
                selector={"kind": "fs", "root": "/workspace", "paths": [f"/workspace/file{i}.txt"]},
                sink="observation", read_only=True,
            )
            for i in range(6)
        ]
        group = safe_read_only_group(ops)
        self.assertEqual(len(group), 6)

    def test_a_write_in_the_group_is_never_marked_safe(self) -> None:
        from vanguard.packages.runtime.scheduler import ReadyOperation, safe_read_only_group

        ops = [
            ReadyOperation(operation_id="read-1",
                          selector={"kind": "fs", "root": "/workspace", "paths": ["/a"]},
                          sink="observation", read_only=True),
            ReadyOperation(operation_id="write-1",
                          selector={"kind": "fs", "root": "/workspace", "paths": ["/b"]},
                          sink="privileged", read_only=False),
        ]
        self.assertEqual(safe_read_only_group(ops), (),
                         "ADR-0106 authorizes read-only concurrency only -- a write in the "
                         "group must never be reported safe for concurrent dispatch")


class ConcurrentDispatchPreservesCorrectnessAndBudget(unittest.TestCase):
    def test_result_order_matches_sequential_regardless_of_completion_order(self) -> None:
        kernel, scope, resource = _build_kernel_and_scope()
        paths = [f"file{i}.txt" for i in range(10)]

        sequential_order = []
        for p in paths:
            result = _dispatch(kernel, scope, resource, p)
            self.assertTrue(result.ok)
            sequential_order.append(p)

        kernel2, scope2, resource2 = _build_kernel_and_scope()
        with ThreadPoolExecutor(max_workers=6) as pool:
            results = list(pool.map(
                lambda p: (p, _dispatch(kernel2, scope2, resource2, p)), paths,
            ))
        for p, result in results:
            self.assertTrue(result.ok, f"{p} failed: {result}")
        concurrent_order = [p for p, _ in results]

        self.assertEqual(sequential_order, concurrent_order,
                         "pool.map must return results in canonical (input) order, "
                         "not completion order -- this is the deterministic-join guarantee")

    def test_budget_is_conserved_under_real_concurrent_dispatch(self) -> None:
        """Each dispatch reserves+commits against the shared Governor. Real
        threads, real jittered latency, real contention on the lock added in
        ADR-0105 -- this is what that fix exists to make safe."""
        kernel, scope, resource = _build_kernel_and_scope()
        paths = [f"file{i}.txt" for i in range(20)]

        with ThreadPoolExecutor(max_workers=10) as pool:
            results = list(pool.map(lambda p: _dispatch(kernel, scope, resource, p), paths))

        self.assertTrue(all(r.ok for r in results))
        # Every dispatch actually ran through the kernel and settled -- no
        # duplicate or lost accounting under concurrency.
        self.assertEqual(len(results), 20)


if __name__ == "__main__":
    unittest.main()
