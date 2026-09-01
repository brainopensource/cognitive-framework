import sys
import unittest
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.telemetry.collector import TelemetryCollector
from tools.telemetry.tuple import InstrumentTuple, CompatibilityKey, TreatmentDimensions, StratificationFields, ObservationMetadata
from tools.telemetry.runner import LatencyBenchmarkRunner, BenchmarkTask
from vanguard.packages.ports.model import ModelPort
from typing import Any, Mapping, Sequence, Optional
class MockResult:
    def __init__(self, ok, value):
        self.ok = ok
        self.value = value

class FakeModelPort(ModelPort):
    def propose(self, context: Mapping[str, Any], tools: Sequence[Mapping[str, Any]], sampling: Mapping[str, Any]):
        return MockResult(True, {"usage": {"prompt_tokens": 10, "completion_tokens": 5, "usd_micros": 150}})

class TestTelemetryProvenance(unittest.TestCase):
    def test_data_source_must_be_valid(self):
        with self.assertRaises(ValueError):
            TelemetryCollector(data_source="invalid_source")

    def test_collector_relabeling_prevented(self):
        collector = TelemetryCollector(data_source="synthetic")
        with self.assertRaises(AttributeError):
            collector.data_source = "live"

    def test_integer_types_enforced(self):
        collector = TelemetryCollector(data_source="synthetic")
        with self.assertRaises(TypeError):
            collector.record_turn_latency(ttft_ms=10.5)
        with self.assertRaises(TypeError):
            collector.record_token_usage(prompt_tokens=10, completion_tokens=10, usd_micros=0.05)
        with self.assertRaises(TypeError):
            collector.record_effect_timing(mount_ms=1.5)

    def test_sandbox_timing_tagged_synthetic(self):
        runner = LatencyBenchmarkRunner()
        task = BenchmarkTask(task_id="t1", context={}, tools=[], sampling={})
        model = FakeModelPort()
        
        result = runner.run_benchmark("test", [task], model, simulate_sandbox=True)
        self.assertEqual(result.report.data_source, "synthetic")
        overhead = result.report.effect_overhead.to_dict()["totalsMs"]["overheadTotal"]
        self.assertGreater(overhead, 0)
        
        live_collector = TelemetryCollector(data_source="live")
        with self.assertRaises(ValueError):
            live_collector.record_effect_timing(mount_ms=15, is_synthetic=True)
            
    def test_observation_metadata_validate_provenance(self):
        meta = ObservationMetadata(timestamp="now", run_id="r1", data_source="invalid")
        with self.assertRaises(ValueError):
            meta.validate_provenance()
