"""BETA-14: the backend baseline benchmarks stay executable.

Owning contract: VANGUARD_090_BACKEND_AUDIT_AND_EVOLUTION_PLAN.md BETA-14.

Not a timing assertion -- wall-clock numbers are environment-dependent and
do not belong in a pass/fail gate. This only proves every benchmark function
still runs to completion and returns the shape `benchmarks/backend_baselines.py`
promises, so a refactor that quietly breaks the harness is caught here
instead of during the next manual benchmark run.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "benchmarks") not in sys.path:
    sys.path.insert(0, str(ROOT / "benchmarks"))

import backend_baselines as bb  # noqa: E402


class BackendBaselinesSmoke(unittest.TestCase):
    def test_every_registered_benchmark_runs_and_returns_timing_fields(self) -> None:
        for name in bb.BENCHMARKS:
            with self.subTest(benchmark=name):
                # A fast variant (1 repeat, small N) of the same call the
                # real benchmark makes -- this is a smoke test for "does it
                # run and return the right shape," not a timing run.
                result = _run_fast(name)
                self.assertIsInstance(result, dict)

    def test_main_writes_a_report_with_every_benchmark(self) -> None:
        import json
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "report.json"
            code = bb.main(["--out", str(out), "--only", "fold_1000_events,storage_amplification_1000_events"])
            self.assertEqual(code, 0)
            report = json.loads(out.read_text("utf-8"))
            self.assertEqual(report["schema"], "aether.backend-baselines/1")
            self.assertIn("fold_1000_events", report["results"])
            self.assertIn("storage_amplification_1000_events", report["results"])

    def test_an_unknown_benchmark_name_is_refused(self) -> None:
        code = bb.main(["--only", "not_a_real_benchmark"])
        self.assertEqual(code, 2)


def _run_fast(name: str):
    """Run one benchmark at minimal repeat count so the smoke test is quick."""
    if name == "no_op_turn":
        return bb.bench_no_op_turn(repeats=1)
    if name == "durable_turn":
        return bb.bench_durable_turn(repeats=1)
    if name == "single_effect_turn_durable_minus_no_op_is_kernel_dispatch_overhead":
        return bb.bench_single_effect_turn_durable(repeats=1)
    if name == "event_append_batch_100":
        return bb.bench_event_append(n_events=10, repeats=1)
    if name == "fold_1000_events":
        return bb.bench_fold(n_events=20, repeats=1)
    if name == "checkpoint_reconstruction_500_events":
        return bb.bench_checkpoint_reconstruction(n_events=10, repeats=1)
    if name == "artifact_capture_batch_50":
        return bb.bench_artifact_capture(n_artifacts=3, artifact_bytes=64, repeats=1)
    if name == "single_agent_execution":
        return bb.bench_single_agent_execution(repeats=1)
    if name == "nested_agent_execution":
        return bb.bench_nested_agent_execution(repeats=1)
    if name == "storage_amplification_1000_events":
        return bb.bench_storage_amplification(n_events=20)
    if name == "multi_agent_token_overhead":
        return bb.bench_multi_agent_token_overhead(repeats=1)
    if name == "recovery_latency":
        return bb.bench_recovery_latency(repeats=1)
    raise AssertionError(f"smoke test does not know benchmark {name!r} -- add a fast variant above")


if __name__ == "__main__":
    unittest.main()
