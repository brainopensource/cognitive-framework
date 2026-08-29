"""Scientific-integrity tests for the v0.9 benchmark runner."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from benchmarks.frontier_v090.runner import (
    ExecutionTelemetry,
    SUBSET,
    digest_bytes,
    run_row,
    validate_subset,
)


class FrontierV090RunnerTests(unittest.TestCase):
    def test_subset_is_fixed_and_spans_easy_medium_hard(self) -> None:
        report = validate_subset()
        self.assertTrue(report["non_empirical"])
        self.assertEqual(len(report["rows"]), 3)
        self.assertEqual({row["difficulty"] for row in report["rows"]}, {"Easy", "Medium", "Hard"})
        self.assertTrue(all(row["terminal"] == "NO_PATCH" for row in report["rows"]))
        self.assertEqual(report["report_digest"], validate_subset()["report_digest"])

    def test_executor_cannot_observe_hidden_oracle(self) -> None:
        observed: list[str] = []

        def inspect(workspace: Path, challenge: object) -> ExecutionTelemetry:
            del challenge
            observed.extend(path.relative_to(workspace).as_posix() for path in workspace.rglob("*"))
            return ExecutionTelemetry("completed", "inspection")

        row = run_row(SUBSET[0], "test", inspect)
        self.assertEqual(row["terminal"], "NO_PATCH")
        self.assertFalse(any("oracle" in path.lower() for path in observed))

    def test_easy_known_good_patch_passes_exterior_oracle(self) -> None:
        def repair(workspace: Path, challenge: object) -> ExecutionTelemetry:
            del challenge
            target = workspace / "lru" / "entry.py"
            source = target.read_text(encoding="utf-8")
            target.write_text(source.replace(
                "        if self.ttl_seconds is None:\n            return False\n        return False\n",
                "        if self.ttl_seconds is None:\n            return False\n        return current_time >= self.created_at + self.ttl_seconds\n",
                1,
            ), encoding="utf-8")
            return ExecutionTelemetry("completed", "calibration_patch")

        row = run_row(SUBSET[0], "test", repair)
        self.assertEqual(row["terminal"], "COMPLETED")
        self.assertEqual(row["changed_files"], ["lru/entry.py"])
        self.assertIsNone(row["usage"]["cost_usd"])
        self.assertEqual(row["usage"]["cost_provenance"], "unknown")

    def test_dataset_preflight_rejects_passing_untouched_fixture(self) -> None:
        row = run_row("tier2_event_bus", "test", lambda *_: ExecutionTelemetry("completed", "unused"))
        self.assertEqual(row["terminal"], "DATASET_INVALID")
        self.assertEqual(row["terminal_reason"], "baseline_already_passes")

    def test_oracle_identity_is_not_a_public_file_digest(self) -> None:
        seen: dict[str, str] = {}

        def inspect(workspace: Path, challenge: object) -> ExecutionTelemetry:
            seen.update({p.relative_to(workspace).as_posix(): digest_bytes(p.read_bytes())
                         for p in workspace.rglob("*") if p.is_file()})
            return ExecutionTelemetry("completed", "inspection")

        row = run_row(SUBSET[0], "test", inspect)
        self.assertNotIn(row["oracle"]["oracle_digest"], seen.values())


if __name__ == "__main__":
    unittest.main()
