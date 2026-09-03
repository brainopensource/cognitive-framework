"""Unit tests for LatencyBenchmarkRunner against deterministic cassettes.

Owning contract: REQ-BENCH-001, VG-07 §5.6, §5.8.
Invariant: Telemetry suites run deterministically in CI against recorded golden cassettes.
"""

import sys
import unittest
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.telemetry.runner import (
    BenchmarkTask,
    LatencyBenchmarkRunner,
)
from tools.telemetry.tuple import (
    CompatibilityKey,
    InstrumentTuple,
    ObservationMetadata,
    StratificationFields,
    TreatmentDimensions,
)
from vanguard.packages.adapters.models.cassette import Cassette, CassettePlayer


class LatencyBenchmarkRunnerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.compat_key = CompatibilityKey(
            benchmark_id="deterministic_cassette_suite",
            split_hash="sha256:split_01",
            model_fingerprint="deepseek/deepseek-v4-flash-0731",
            sampling_params={"temperature": 0.0, "max_tokens": 64},
            harness_commit="v0.5.0",
        )
        self.strat = StratificationFields(difficulty="standard", language="python")

    def _build_cassette_player(self, num_records: int = 3) -> CassettePlayer:
        cassette = Cassette()
        for i in range(num_records):
            context = {"blocks": [{"label": "L5", "content": f"Task {i}"}]}
            tools = [{"name": "read", "schema": {"type": "object"}}]
            sampling = {"temperature": 0.0, "maxTokens": 64}
            proposal = {
                "text": f"Response {i}",
                "toolCalls": [],
                "usage": {
                    "prompt_tokens": 100 * (i + 1),
                    "completion_tokens": 20 * (i + 1),
                    "cached_tokens": 50 * (i + 1),
                    "total_tokens": 120 * (i + 1),
                    "cost_usd": 0.00003 * (i + 1),
                },
            }
            cassette.add_record(context, tools, sampling, proposal)
        return CassettePlayer(cassette, match_mode="tape")

    def test_deterministic_cassette_benchmark_execution(self) -> None:
        player = self._build_cassette_player(3)
        tasks = [
            BenchmarkTask(
                task_id=f"t{i}",
                context={"blocks": [{"label": "L5", "content": f"Task {i}"}]},
                tools=[{"name": "read", "schema": {"type": "object"}}],
                sampling={"temperature": 0.0, "maxTokens": 64},
            )
            for i in range(3)
        ]

        treatment = TreatmentDimensions(manifest="vg-code-default", cache_enabled=True)
        meta = ObservationMetadata(timestamp="2026-08-15T20:00:00Z", run_id="bench_01")
        inst_tuple = InstrumentTuple(self.compat_key, treatment, self.strat, meta)

        runner = LatencyBenchmarkRunner()
        result = runner.run_benchmark("code_default_arm", tasks, player, instrument_tuple=inst_tuple)

        self.assertEqual(result.task_count, 3)
        report = result.report
        self.assertEqual(report.turn_count, 3)

        # Token checks (100+200+300 = 600 prompt, 20+40+60 = 120 completion, 50+100+150 = 300 cached)
        tc = report.token_cost
        self.assertEqual(tc.prompt_tokens, 600)
        self.assertEqual(tc.completion_tokens, 120)
        self.assertEqual(tc.cached_tokens, 300)
        self.assertEqual(tc.total_tokens, 720)
        self.assertEqual(tc.total_cost_usd_micros, 180)

        # Effect overhead checks
        oh = report.effect_overhead.to_dict()
        self.assertEqual(oh["effectCount"], 3)
        self.assertGreater(oh["totalsMs"]["overheadTotal"], 0.0)

    def test_paired_arms_comparison_under_rule_m18(self) -> None:
        player_a = self._build_cassette_player(2)
        player_b = self._build_cassette_player(2)

        tasks = [
            BenchmarkTask(
                task_id=f"t{i}",
                context={"blocks": [{"label": "L5", "content": f"Task {i}"}]},
                tools=[{"name": "read", "schema": {"type": "object"}}],
                sampling={"temperature": 0.0, "maxTokens": 64},
            )
            for i in range(2)
        ]

        treatment_a = TreatmentDimensions(manifest="vg-code-default", cache_enabled=True)
        treatment_b = TreatmentDimensions(manifest="vg-shell-only", cache_enabled=False)

        tuple_a = InstrumentTuple(self.compat_key, treatment_a, self.strat, ObservationMetadata(timestamp="T1", run_id="r1"))
        tuple_b = InstrumentTuple(self.compat_key, treatment_b, self.strat, ObservationMetadata(timestamp="T2", run_id="r2"))

        runner = LatencyBenchmarkRunner()
        arm_a = runner.run_benchmark("arm_code_default", tasks, player_a, instrument_tuple=tuple_a)
        arm_b = runner.run_benchmark("arm_shell_only", tasks, player_b, instrument_tuple=tuple_b)

        comparison = runner.compare_arms(arm_a, arm_b)
        self.assertTrue(comparison.is_valid_comparison)
        self.assertEqual(comparison.arm_a_name, "arm_code_default")
        self.assertEqual(comparison.arm_b_name, "arm_shell_only")
        self.assertEqual(comparison.rejection_reason, "")


if __name__ == "__main__":
    unittest.main()
