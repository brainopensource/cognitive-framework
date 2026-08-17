import json
import unittest
from pathlib import Path

from tools.telemetry.cache_replay import measure_replay


class TestCacheReplayMetric(unittest.TestCase):
    def test_fixed_replay_reports_stable_prefix_and_provider_hits(self) -> None:
        records = json.loads(
            (Path(__file__).parents[2] / "tools/telemetry/fixtures/prefix_replay.json").read_text()
        )
        metric = measure_replay(records)
        self.assertEqual(metric["dataSource"], "cassette")
        self.assertTrue(metric["prefixDigestStable"])
        self.assertEqual(metric["providerCacheHitRate"], 0.5)

    def test_missing_provider_field_labels_limitation(self) -> None:
        metric = measure_replay([
            {"context": {"system": "same", "user": "one"}, "tools": []},
            {"context": {"system": "same", "user": "two"}, "tools": []},
        ])
        self.assertTrue(metric["prefixDigestStable"])
        self.assertIsNone(metric["providerCacheHitRate"])
        self.assertIn("did not report", metric["limitation"])


if __name__ == "__main__":
    unittest.main()
