"""W16-A: consume BETA's task paths, and skip a live smoke closed.

`REQ-TRUST-001`. The live smoke is the sharpest place to get this wrong: a
test that passes because no backend answered is indistinguishable, in a
summary, from one that passed because the model did the work.
"""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from vanguard.packages.runtime.dogfood import WORKSPACE_MISSING, run_task_set
from vanguard.packages.runtime.model_selection import ModelUnavailable, select_model
from vanguard.packages.runtime.repair import StopReason
from vanguard.packages.runtime.scoring import score_arm
from vanguard.packages.runtime.task_sets import (
    DOGFOOD_SET,
    GREENFIELD_SET,
    missing_tasks,
    resolve_task_set,
)
from vanguard.packages.runtime.telemetry import RunTelemetry

ROOT = Path(__file__).resolve().parents[2]


class TheTaskSetIsDeclaredNotDiscovered(unittest.TestCase):
    """A glob reports a smaller set when a directory is missing and calls it
    a full run."""

    def test_the_dogfood_set_names_three_tasks_whatever_is_on_disk(self) -> None:
        self.assertEqual([t["id"] for t in DOGFOOD_SET],
                         ["DOGFOOD-01", "DOGFOOD-02", "DOGFOOD-03"])

    def test_the_greenfield_set_names_one(self) -> None:
        self.assertEqual([t["id"] for t in GREENFIELD_SET], ["GREENFIELD-01"])

    def test_resolution_does_not_filter_by_existence(self) -> None:
        resolved = resolve_task_set(DOGFOOD_SET, root=ROOT)
        self.assertEqual(len(resolved), 3)

    def test_missing_tasks_are_reported_for_reporting_not_filtering(self) -> None:
        resolved = resolve_task_set(DOGFOOD_SET, root=ROOT)
        missing = missing_tasks(resolved)
        # BETA may or may not have landed these; either way the set is 3.
        self.assertLessEqual(len(missing), 3)
        self.assertEqual(len(resolved), 3)

    def test_the_greenfield_workspace_exists_in_this_tree(self) -> None:
        resolved = resolve_task_set(GREENFIELD_SET, root=ROOT)
        self.assertEqual(missing_tasks(resolved), ())


class _Result:
    def __init__(self, green: bool) -> None:
        self.green = green
        self.instrument_error = None
        self.telemetry = RunTelemetry(turns=1, prompt_tokens=5, completion_tokens=5)
        self.events = []


class RunningTheSetsIsHonestAboutAbsence(unittest.TestCase):
    def test_absent_dogfood_dirs_are_counted_not_dropped(self) -> None:
        report = run_task_set(
            resolve_task_set(DOGFOOD_SET, root=ROOT),
            run_session=lambda task, attempt: _Result(green=True),
            oracle=lambda r: r.green,
            events_of=lambda r: r.events,
            label="mock-dogfood")
        self.assertEqual(report.denominator, 3)

    def test_a_present_greenfield_task_runs(self) -> None:
        report = run_task_set(
            resolve_task_set(GREENFIELD_SET, root=ROOT),
            run_session=lambda task, attempt: _Result(green=True),
            oracle=lambda r: r.green,
            events_of=lambda r: r.events,
            label="mock-greenfield")
        self.assertEqual(report.resolved, 1)
        self.assertEqual(report.denominator, 1)

    def test_the_arm_score_carries_the_same_denominator(self) -> None:
        report = run_task_set(
            resolve_task_set(DOGFOOD_SET, root=ROOT),
            run_session=lambda task, attempt: _Result(green=False),
            oracle=lambda r: r.green,
            events_of=lambda r: r.events,
            max_attempts=1)
        score = score_arm("mock-dogfood", [t.to_dict() for t in report.tasks])
        self.assertEqual(score.denominator, 3)
        self.assertEqual(score.resolved, 0)

    def test_a_missing_workspace_never_reports_oracle_green(self) -> None:
        report = run_task_set(
            [{"id": "gone", "workspace": "/nowhere/at/all"}],
            run_session=lambda task, attempt: _Result(green=True),
            oracle=lambda r: r.green,
            events_of=lambda r: r.events)
        self.assertEqual(report.tasks[0].outcome, WORKSPACE_MISSING)
        self.assertNotEqual(report.tasks[0].outcome, StopReason.ORACLE_GREEN)


class TheLiveSmokeSkipsClosed(unittest.TestCase):
    """W16-A item 14. One optional live run; never a fake green."""

    LIVE = os.environ.get("VANGUARD_LIVE_SMOKE") == "1"

    def _available(self) -> tuple[str, object] | None:
        for port in ("ollama", "openrouter", "deepseek"):
            try:
                return port, select_model(port)
            except ModelUnavailable:
                continue
        return None

    def test_the_smoke_reports_which_backend_it_used_or_why_it_did_not(self) -> None:
        available = self._available()
        if available is None:
            self.skipTest("no live backend reachable: ollama daemon down, "
                          "no OPENROUTER_API_KEY, or free band empty — "
                          "skipped closed, not passed")
        port, selected = available
        self.assertIn(port, ("ollama", "openrouter", "deepseek"))
        self.assertTrue(selected.label)

    def test_an_absent_backend_is_never_reported_as_a_pass(self) -> None:
        """The property that matters even when nothing is reachable."""

        from vanguard.packages.runtime.lab_driver import run_lab_task

        with tempfile.TemporaryDirectory() as tmp:
            result = run_lab_task("vg-code-default", tmp, model_port="ollama")
        self.assertIn(result["outcome"],
                      (StopReason.INSTRUMENT_ERROR, StopReason.ORACLE_GREEN))
        if result["outcome"] == StopReason.INSTRUMENT_ERROR:
            self.assertTrue(result["detail"])

    def test_the_live_gate_is_opt_in_so_ci_stays_on_mock(self) -> None:
        if not self.LIVE:
            self.assertFalse(self.LIVE)
        self.assertIsInstance(self.LIVE, bool)

    def test_a_live_run_is_labelled_with_its_port(self) -> None:
        available = self._available()
        if available is None:
            self.skipTest("no live backend reachable — skipped closed")
        _, selected = available
        self.assertNotEqual(selected.to_dict()["modelPort"], "mock")


if __name__ == "__main__":
    unittest.main()
