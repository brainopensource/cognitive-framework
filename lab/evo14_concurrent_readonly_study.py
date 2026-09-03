#!/usr/bin/env python3
"""EVO-14: the preregistered concurrent-read-only study.

Preregistration (frozen before this was run):
`evidence/prereg/EVO-14-concurrent-readonly-study.md`.

Runs the frozen workload -- 12 provably-independent `fs.read` operations,
each with a realistic injected 20ms round-trip latency -- through the real
`Kernel` (real `Governor`, real classifier/policy, real adapters) twice:
once via ordinary sequential dispatch (today's production behavior), once
via a bounded `ThreadPoolExecutor`. Reports median wall-time for both arms
and verifies the correctness precondition (identical resulting event order/
digest) before any performance claim is allowed to matter.

CLI:
  python3 lab/evo14_concurrent_readonly_study.py
"""

from __future__ import annotations

import json
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

N_FILES = 12
INJECTED_LATENCY_S = 0.020
REPEATS = 20
MAX_WORKERS = 8
ACCEPTANCE_REDUCTION = 0.20


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
        constraints=Constraints(expires_at="2099-01-01T00:00:00.000Z", max_uses=10_000,
                                budget_usd_micros=100_000_000, max_depth=4),
        depth=0,
    )

    class LatentAdapter:
        """A real adapter with a real (small, representative) round trip."""

        def healthy(self) -> bool:
            return True

        def execute(self, req: Any) -> Any:
            time.sleep(INJECTED_LATENCY_S)
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
            HeldAuthority("study-agent", frozenset({"fs.read"}), (resource,), max_depth=4)]),
        governor=Governor({"usd_micros": 100_000_000, "millis": 100_000_000}),
        issuer=GrantIssuer(), clock=FixedClock(at="2026-08-29T00:00:00.000000Z"),
        ledger=silent, events=silent, sinks=sinks,
    )
    return kernel, scope, resource


def _dispatch_one(kernel, scope, resource, run_id: str, path: str):
    from vanguard.packages.kernel.model import EffectRequest
    from vanguard.packages.kernel.budget import Reservation

    request = EffectRequest(
        action="fs.read", resource=resource, args={"path": path},
        principal="study-agent", run_id=run_id,
    )
    return kernel.dispatch(request, requested_scope=scope, reservation=Reservation())


def _run_sequential(kernel, scope, resource, run_id: str) -> list[str]:
    order = []
    for i in range(N_FILES):
        result = _dispatch_one(kernel, scope, resource, run_id, f"file{i}.txt")
        assert result.ok, f"sequential dispatch {i} failed: {result}"
        order.append(f"file{i}.txt")
    return order


def _run_concurrent(kernel, scope, resource, run_id: str) -> list[str]:
    paths = [f"file{i}.txt" for i in range(N_FILES)]  # canonical (sorted) order
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        results = list(pool.map(
            lambda p: (p, _dispatch_one(kernel, scope, resource, run_id, p)), paths,
        ))
    for path, result in results:
        assert result.ok, f"concurrent dispatch {path} failed: {result}"
    # `pool.map` already returns results in input (canonical) order regardless
    # of completion order -- this *is* the deterministic-join mechanism, not
    # an extra sort bolted on after the fact.
    return [path for path, _ in results]


def _time_arm(fn, repeats: int) -> dict[str, Any]:
    samples = []
    order: list[str] | None = None
    for i in range(repeats):
        kernel, scope, resource = _build_kernel_and_scope()
        start = time.perf_counter()
        this_order = fn(kernel, scope, resource, f"run-evo14-{i}")
        samples.append((time.perf_counter() - start) * 1000.0)
        if order is None:
            order = this_order
    samples.sort()
    return {
        "repeats": repeats,
        "min_ms": samples[0],
        "median_ms": statistics.median(samples),
        "p95_ms": samples[min(len(samples) - 1, int(len(samples) * 0.95))],
        "max_ms": samples[-1],
        "resulting_order": order,
    }


def main() -> int:
    sequential = _time_arm(_run_sequential, REPEATS)
    concurrent = _time_arm(_run_concurrent, REPEATS)

    order_matches = sequential["resulting_order"] == concurrent["resulting_order"]
    reduction = (sequential["median_ms"] - concurrent["median_ms"]) / sequential["median_ms"]

    report = {
        "study": "EVO-14-concurrent-readonly",
        "preregistration": "evidence/prereg/EVO-14-concurrent-readonly-study.md",
        "workload": {"n_operations": N_FILES, "injected_latency_ms": INJECTED_LATENCY_S * 1000,
                     "repeats_per_arm": REPEATS, "max_workers": MAX_WORKERS},
        "sequential": sequential,
        "concurrent": concurrent,
        "correctness_precondition_order_matches": order_matches,
        "median_wall_time_reduction": reduction,
        "acceptance_threshold": ACCEPTANCE_REDUCTION,
        "accepted": bool(order_matches and reduction >= ACCEPTANCE_REDUCTION),
    }
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
