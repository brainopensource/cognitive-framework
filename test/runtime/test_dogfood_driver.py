"""W13-A: the MOCK dogfood driver and its session export.

The driver's job is to run a task set honestly. Most of what it must get right
is about the denominator: a task set that quietly drops the tasks it could not
run reports a pass rate over whatever happened to be present.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from vanguard.packages.runtime.dogfood import (
    WORKSPACE_MISSING,
    DogfoodReport,
    run_task_set,
)
from vanguard.packages.runtime.repair import StopReason
from vanguard.packages.runtime.telemetry import RunTelemetry

FIXTURES = Path(__file__).resolve().parent / "fixtures"


class _Event:
    def __init__(self, kind: str, **payload) -> None:
        self.payload = {"kind": kind, **payload}


class _Result:
    def __init__(self, *, green: bool, events: list | None = None) -> None:
        self.green = green
        self.instrument_error = None
        self.telemetry = RunTelemetry(turns=2, prompt_tokens=50, completion_tokens=10)
        self.events = events or [
            _Event("ProposalProduced", toolCalls=[{"action": "fs.read"}]),
            _Event("EffectCompleted"),
            _Event("ProposalProduced", toolCalls=[{"action": "proc.exec"}]),
            _Event("EffectCompleted"),
        ]


def _drive(tasks, *, green: bool = True, **overrides):
    return run_task_set(
        tasks,
        run_session=lambda task, attempt: _Result(green=green),
        oracle=lambda result: result.green,
        events_of=lambda result: result.events,
        **overrides,
    )


class TheDenominatorIsHonest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.workspace = Path(self._tmp.name) / "ws"
        self.workspace.mkdir()

    def test_a_missing_workspace_is_reported_not_skipped(self) -> None:
        report = _drive([
            {"id": "DOGFOOD-01", "workspace": str(self.workspace)},
            {"id": "DOGFOOD-02", "workspace": "/nowhere/at/all"},
        ])
        self.assertEqual(report.denominator, 2)
        outcomes = {t.task_id: t.outcome for t in report.tasks}
        self.assertEqual(outcomes["DOGFOOD-02"], WORKSPACE_MISSING)

    def test_a_missing_workspace_stays_in_the_denominator(self) -> None:
        """Otherwise the pass rate is over whatever happened to be present."""

        report = _drive([{"id": "gone", "workspace": "/nowhere"}])
        self.assertEqual(report.resolved, 0)
        self.assertEqual(report.denominator, 1)

    def test_missing_workspaces_are_listed_as_inconclusive(self) -> None:
        report = _drive([{"id": "gone", "workspace": "/nowhere"}])
        self.assertEqual(report.inconclusive, ("gone",))

    def test_a_green_task_is_counted_resolved(self) -> None:
        report = _drive([{"id": "ok", "workspace": str(self.workspace)}])
        self.assertEqual(report.resolved, 1)
        self.assertEqual(report.tasks[0].outcome, StopReason.ORACLE_GREEN)

    def test_a_red_task_is_not_counted_resolved(self) -> None:
        report = _drive([{"id": "red", "workspace": str(self.workspace)}],
                        green=False, max_attempts=2)
        self.assertEqual(report.resolved, 0)
        self.assertNotEqual(report.tasks[0].outcome, StopReason.ORACLE_GREEN)


class TheSessionExportComesFromTheLedger(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.workspace = Path(self._tmp.name) / "ws"
        self.workspace.mkdir()
        self.report = _drive([{"id": "t1", "workspace": str(self.workspace)}])

    def test_each_turn_appears_with_its_verb(self) -> None:
        session = self.report.tasks[0].session
        self.assertEqual([entry["verb"] for entry in session],
                         ["fs.read", "proc.exec"])

    def test_dead_ends_are_exported(self) -> None:
        report = run_task_set(
            [{"id": "t", "workspace": str(self.workspace)}],
            run_session=lambda task, attempt: _Result(green=False, events=[
                _Event("ProposalProduced", toolCalls=[{"action": "proc.exec"}]),
                _Event("AuthorizationDenied", reason="not granted"),
            ]),
            oracle=lambda r: r.green,
            events_of=lambda r: r.events,
            max_attempts=1)
        self.assertEqual(report.tasks[0].dead_ends,
                         ({"turn": 1, "verb": "proc.exec", "reason": "not granted"},))

    def test_the_json_is_written_and_reloadable(self) -> None:
        target = Path(self._tmp.name) / "out" / "session.json"
        written = self.report.write(target)
        loaded = json.loads(written.read_text())
        self.assertEqual(loaded["denominator"], 1)
        self.assertEqual(loaded["tasks"][0]["taskId"], "t1")

    def test_the_json_is_stable_across_two_writes(self) -> None:
        first = Path(self._tmp.name) / "a.json"
        second = Path(self._tmp.name) / "b.json"
        self.report.write(first)
        self.report.write(second)
        self.assertEqual(first.read_text(), second.read_text())

    def test_token_counts_are_integers_or_absent(self) -> None:
        task = self.report.tasks[0]
        for value in (task.prompt_tokens, task.completion_tokens):
            self.assertTrue(value is None or isinstance(value, int))


class TheDriverIsNotTheJudge(unittest.TestCase):
    """`A-05`: it never runs a test itself."""

    def test_the_module_runs_no_suite_of_its_own(self) -> None:
        import inspect

        import vanguard.packages.runtime.dogfood as module

        source = inspect.getsource(module)
        for forbidden in ("subprocess", "pytest", "unittest.main", "os.system"):
            self.assertNotIn(forbidden, source)


class TheGreenfieldFixtureStartsRed(unittest.TestCase):
    """`W13-A`'s greenfield task: a Python API plus a static HTML page."""

    ROOT = FIXTURES / "greenfield_api"

    def test_the_fixture_exists_with_a_suite(self) -> None:
        self.assertTrue((self.ROOT / "app.py").is_file())
        self.assertTrue((self.ROOT / "tests" / "test_app.py").is_file())

    def test_the_suite_is_red_before_any_work(self) -> None:
        """A fixture that starts green measures nothing."""

        import subprocess
        import sys

        completed = subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-t", "tests"],
            cwd=self.ROOT, capture_output=True, text=True, check=False)
        self.assertNotEqual(completed.returncode, 0)

    def test_it_needs_no_network_or_build_step(self) -> None:
        source = (self.ROOT / "app.py").read_text()
        for forbidden in ("import requests", "urllib", "npm", "svelte"):
            self.assertNotIn(forbidden, source.lower())


if __name__ == "__main__":
    unittest.main()
