"""S17/S18: BETA's real paths, and a MOCK that actually takes coding turns.

`REQ-TRUST-001`. Two defects this closes, both of which produced *honest* but
useless output:

  - the task-set constant pointed at `benchmarkings/dogfood/DOGFOOD-0N`, so
    every task reported `workspace_missing` — the instrument working correctly
    over a wrong address;
  - the MOCK was `FakeModel([])`, so every run reported
    `turns: 0 / model_not_invoked` — a failure of the brain binding, not a
    measurement of the loop.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from vanguard.packages.runtime.lab_driver import run_lab_task
from vanguard.packages.runtime.mock_coding_tape import (
    brief_from_task_dir,
    coding_tape,
)
from vanguard.packages.runtime.repair import StopReason
from vanguard.packages.runtime.task_sets import (
    DOGFOOD_SET,
    GREENFIELD_SET,
    missing_tasks,
    resolve_task_set,
)

ROOT = Path(__file__).resolve().parents[2]
ALL_TASKS = DOGFOOD_SET + GREENFIELD_SET


class TheDeclaredSetPointsAtBetasPaths(unittest.TestCase):
    """S17-A-01. One constant, and it must resolve."""

    def test_the_protocol_ids_are_unchanged(self) -> None:
        self.assertEqual([t["id"] for t in ALL_TASKS],
                         ["DOGFOOD-01", "DOGFOOD-02", "DOGFOOD-03",
                          "GREENFIELD-API-HTML"])

    def test_nothing_is_missing_now_that_the_constant_is_right(self) -> None:
        """Fail closed: if this reports missing, the constant is still wrong."""

        resolved = resolve_task_set(ALL_TASKS, root=ROOT)
        self.assertEqual(missing_tasks(resolved), ())

    def test_the_set_is_declared_not_globbed(self) -> None:
        import inspect

        import vanguard.packages.runtime.task_sets as module

        source = inspect.getsource(module)
        for forbidden in ("glob(", "rglob(", "iterdir("):
            self.assertNotIn(forbidden, source)

    def test_the_lam_workspace_map_reads_the_same_constant(self) -> None:
        """One copy of a path; two copies is one copy that is wrong."""

        import sys

        if str(ROOT / "tools" / "telemetry") not in sys.path:
            sys.path.insert(0, str(ROOT / "tools" / "telemetry"))
        from tools.telemetry.coding_lam import default_workspace_map

        mapped = default_workspace_map(ROOT)
        self.assertEqual(sorted(mapped), sorted(t["id"] for t in ALL_TASKS))
        self.assertTrue(all(value is not None for value in mapped.values()))


class TheMockTakesRealTurns(unittest.TestCase):
    """S18-A-01. `turns: 0` is an instrument error, not a result."""

    TASK = ROOT / "lab" / "tasks" / "dogfood-01-multi-turn-file-rollback"

    def test_a_mock_run_produces_turns(self) -> None:
        result = run_lab_task("vg-code-default", self.TASK, max_attempts=1)
        self.assertGreater(result["turns"], 0)
        self.assertNotEqual(result["detail"], "model_not_invoked")

    def test_it_reads_before_it_edits(self) -> None:
        result = run_lab_task("vg-code-default", self.TASK, max_attempts=1)
        verbs = [entry["verb"] for entry in result["session"]]
        self.assertEqual(verbs[0], "fs.read")
        self.assertIn("patch.apply", verbs)

    def test_the_mock_never_reaches_a_green_oracle(self) -> None:
        """A MOCK that could fix the bug would be a gold patch in the tape."""

        result = run_lab_task("vg-code-default", self.TASK, max_attempts=1)
        self.assertNotEqual(result["outcome"], StopReason.ORACLE_GREEN)

    def test_the_tape_contains_no_working_diff(self) -> None:
        import inspect

        import vanguard.packages.runtime.mock_coding_tape as module

        source = inspect.getsource(module)
        for forbidden in ("return a / b", "except ZeroDivisionError", "def divide"):
            self.assertNotIn(forbidden, source)

    def test_the_tape_only_proposes_granted_verbs(self) -> None:
        tape = coding_tape(verbs=("fs.read",))
        actions = {item.get("action") for item in tape if "action" in item}
        self.assertEqual(actions, {"fs.read"})

    def test_the_brief_comes_from_the_task_not_the_harness(self) -> None:
        brief = brief_from_task_dir(self.TASK)
        self.assertIsNotNone(brief)
        self.assertIn("DOGFOOD-01", brief)

    def test_a_task_without_a_brief_file_returns_none(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(brief_from_task_dir(tmp))


class BothModesInARealRun(unittest.TestCase):
    """S15-A-01 / S18, end to end rather than at the policy alone."""

    TASK = ROOT / "lab" / "tasks" / "dogfood-01-multi-turn-file-rollback"

    def test_benchmark_denies_the_privileged_verbs(self) -> None:
        result = run_lab_task("vg-code-default", self.TASK, max_attempts=1,
                              interactive=False)
        receipts = {entry["verb"]: entry["receipt"] for entry in result["session"]}
        self.assertEqual(receipts.get("patch.apply"), "AuthorizationDenied")

    def test_interactive_suspends_the_same_verb(self) -> None:
        result = run_lab_task("vg-code-default", self.TASK, max_attempts=1,
                              interactive=True)
        receipts = {entry["verb"]: entry["receipt"] for entry in result["session"]}
        self.assertEqual(receipts.get("patch.apply"), "ApprovalRequested")

    def test_neither_mode_hangs(self) -> None:
        for interactive in (True, False):
            with self.subTest(interactive=interactive):
                result = run_lab_task("vg-code-default", self.TASK,
                                      max_attempts=1, interactive=interactive)
                self.assertIn("outcome", result)

    def test_a_denial_is_a_dead_end_with_a_reason(self) -> None:
        result = run_lab_task("vg-code-default", self.TASK, max_attempts=1)
        self.assertTrue(result["deadEnds"])
        self.assertTrue(all(entry["reason"] for entry in result["deadEnds"]))


class TheJsonlIsALedgerExport(unittest.TestCase):
    """S18-A-02. The exporter must accept what the driver writes."""

    TASK = ROOT / "lab" / "tasks" / "dogfood-01-multi-turn-file-rollback"

    def test_the_export_is_vg4_envelopes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "episode.jsonl"
            run_lab_task("vg-code-default", self.TASK, max_attempts=1,
                         jsonl_out=target)
            lines = [json.loads(line) for line in
                     target.read_text().splitlines() if line.strip()]
        self.assertTrue(lines)
        for envelope in lines:
            self.assertEqual(envelope["schemaVersion"], "vg.4")

    def test_the_projection_reads_it(self) -> None:
        from vanguard.packages.adapters.stores.ledger_jsonl import import_jsonl

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "episode.jsonl"
            run_lab_task("vg-code-default", self.TASK, max_attempts=1,
                         jsonl_out=target)
            with target.open(encoding="utf-8") as reader:
                envelopes = import_jsonl(reader)
        self.assertTrue(envelopes)

    def test_the_driver_opens_no_second_session_store(self) -> None:
        import inspect

        import vanguard.packages.runtime.session_log as module

        source = inspect.getsource(module)
        for forbidden in ("sqlite3", "connect("):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
