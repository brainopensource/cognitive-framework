"""T-92: L0 smoke triad through the public product path."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from benchmarks.ladder.l0_triad.runner import (
    TASKS,
    refuse_patchless_completion,
    run_task,
    task_dir,
)

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "benchmarks" / "ladder" / "l0_triad" / "runner.py"


class TestL0Triad(unittest.TestCase):
    def test_three_tasks_exist_with_oracles(self) -> None:
        self.assertEqual(TASKS, ("P0-FIB", "P0-CSV", "P0-BUG"))
        for task_id in TASKS:
            folder = task_dir(task_id)
            self.assertTrue((folder / "TASK.md").is_file(), task_id)
            self.assertTrue((folder / "test_oracle.py").is_file(), task_id)

    def test_runner_invokes_the_product_path(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")
        self.assertIn("execute_product", source)
        self.assertNotIn("execute_profiled", source)

    def test_each_task_returns_a_typed_terminal_or_failure(self) -> None:
        for task_id in TASKS:
            with tempfile.TemporaryDirectory() as tmp:
                row = run_task(task_id, Path(tmp) / task_id)
            self.assertIn(row["task_id"], TASKS)
            self.assertTrue(row["fixture_digest"].startswith("sha256:"))
            self.assertTrue(row["oracle_digest"].startswith("sha256:"))
            self.assertTrue(row["terminal_status"])
            self.assertNotEqual(row["terminal_status"], "completed")

    def test_patchless_completion_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            refuse_patchless_completion({
                "terminal_status": "completed",
                "patch_digest": None,
            })


if __name__ == "__main__":
    unittest.main()
