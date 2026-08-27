"""Unit tests for TelemetryCollector.

Owning contract: REQ-BENCH-001, VG-07 §5.6, §5.8.
"""

import sys
import unittest
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import io
import json

from tools.telemetry.collector import TelemetryCollector
from tools.telemetry.tuple import (
    CompatibilityKey,
    InstrumentTuple,
    ObservationMetadata,
    StratificationFields,
    TreatmentDimensions,
)


class TelemetryCollectorTest(unittest.TestCase):
    def test_direct_measurement_accumulation(self) -> None:
        collector = TelemetryCollector(run_id="test_run_01", task_id="task_123")

        # Record 3 turns with varying TTFT
        collector.record_turn_latency(ttft_ms=120, ttlt_ms=450, turn_duration_ms=450)
        collector.record_turn_latency(ttft_ms=80, ttlt_ms=300, turn_duration_ms=300)
        collector.record_turn_latency(ttft_ms=250, ttlt_ms=800, turn_duration_ms=800)

        # Record 2 effects
        collector.record_effect_timing(mount_ms=12, probe_ms=4, exec_ms=20, teardown_ms=6)
        collector.record_effect_timing(mount_ms=10, probe_ms=5, exec_ms=15, teardown_ms=5)

        # Record tokens and cost
        collector.record_token_usage(prompt_tokens=500, completion_tokens=100, cached_tokens=200, usd_micros=120, model="deepseek/deepseek-v4-flash-0731")
        collector.record_token_usage(prompt_tokens=600, completion_tokens=150, cached_tokens=300, usd_micros=150, model="deepseek/deepseek-v4-flash-0731")

        report = collector.build_report()
        self.assertEqual(report.run_id, "test_run_01")
        self.assertEqual(report.turn_count, 3)

        # Latency checks
        lat_dict = report.latency.to_dict()
        self.assertEqual(lat_dict["sampleCount"], 3)
        self.assertEqual(lat_dict["ttft"]["p50"], 120.0)
        self.assertEqual(lat_dict["ttft"]["min"], 80.0)
        self.assertEqual(lat_dict["ttft"]["max"], 250.0)

        # Overhead checks
        oh_dict = report.effect_overhead.to_dict()
        self.assertEqual(oh_dict["effectCount"], 2)
        self.assertEqual(oh_dict["totalsMs"]["mount"], 22.0)
        self.assertEqual(oh_dict["totalsMs"]["overheadTotal"], 42.0)  # mount(22) + probe(9) + teardown(11)

        # Token checks
        tc_dict = report.token_cost.to_dict()
        self.assertEqual(tc_dict["promptTokens"], 1100)
        self.assertEqual(tc_dict["completionTokens"], 250)
        self.assertEqual(tc_dict["cachedTokens"], 500)
        self.assertEqual(tc_dict["totalTokens"], 1350)
        self.assertEqual(tc_dict["totalCostUsdMicros"], 270)

    def test_jsonl_formatting_and_export(self) -> None:
        collector = TelemetryCollector(run_id="run_jsonl", task_id="task_jsonl")
        collector.record_turn_latency(ttft_ms=100, ttlt_ms=200)
        collector.record_token_usage(prompt_tokens=200, completion_tokens=50, usd_micros=50)

        stream = io.StringIO()
        collector.export_jsonl(stream)
        raw_output = stream.getvalue()

        self.assertTrue(raw_output.endswith("\n"))
        parsed = json.loads(raw_output.strip())
        self.assertEqual(parsed["runId"], "run_jsonl")
        self.assertIn("latency", parsed)
        self.assertIn("tokenCost", parsed)
        self.assertEqual(parsed["tokenCost"]["totalTokens"], 250)

    def test_event_ingestion_non_invasive(self) -> None:
        collector = TelemetryCollector(run_id="run_events")

        collector.ingest_event({
            "payload": {"kind": "EpisodeStarted", "occurredAt": "2026-08-15T20:00:00Z"}
        })
        collector.ingest_event({
            "payload": {
                "kind": "ProposalProduced",
                "occurredAt": "2026-08-15T20:00:01Z",
                "proposal": {
                    "usage": {
                        "prompt_tokens": 800,
                        "completion_tokens": 120,
                        "cached_tokens": 400,
                        "cost_usd": 0.00018,
                    },
                },
                "timing": {"ttftMs": 150, "durationMs": 400},
            }
        })
        collector.ingest_event({
            "payload": {
                "kind": "EffectCompleted",
                "occurredAt": "2026-08-15T20:00:02Z",
                "timing": {"mountMs": 14, "probeMs": 3, "execMs": 25, "teardownMs": 5},
            }
        })
        collector.ingest_event({
            "payload": {"kind": "EpisodeCompleted", "occurredAt": "2026-08-15T20:00:03Z"}
        })

        report = collector.build_report()
        self.assertEqual(report.status, "completed")
        self.assertEqual(report.turn_count, 1)
        self.assertEqual(report.token_cost.prompt_tokens, 800)
        self.assertEqual(report.token_cost.cached_tokens, 400)
        self.assertEqual(report.latency.ttft_samples_ms, [150])
        self.assertEqual(report.effect_overhead.effect_count, 1)

    def test_data_source_labeling_and_integer_micros(self) -> None:
        collector = TelemetryCollector(run_id="run_cassette", data_source="cassette")
        collector.record_token_usage(prompt_tokens=100, completion_tokens=50, usd_micros=30)
        report = collector.build_report()
        self.assertEqual(report.data_source, "cassette")
        report_dict = report.to_dict()
        self.assertEqual(report_dict["dataSource"], "cassette")
        self.assertEqual(report_dict["tokenCost"]["totalCostUsdMicros"], 30)

    def test_live_collector_rejects_synthetic_timing(self) -> None:
        collector = TelemetryCollector(run_id="run_live", data_source="live")
        with self.assertRaises(ValueError) as ctx:
            collector.record_turn_latency(ttft_ms=10, is_synthetic=True)
        self.assertIn("synthetic timing forbidden in live", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx:
            collector.ingest_event({
                "payload": {
                    "kind": "ProposalProduced",
                    "synthetic": True,
                    "timing": {"ttftMs": 5.0},
                }
            })
        self.assertIn("synthetic timing forbidden in live", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
