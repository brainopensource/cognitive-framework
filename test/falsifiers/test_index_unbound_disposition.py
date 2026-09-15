"""Falsifier for C5 (T-135): INDEX_UNBOUND disposition and accounting.

Verifies:
1. When index is None / INDEX_UNBOUND, the completion gate refuses admission.
2. The completion policy is consulted exactly ZERO times (fail-closed before policy).
3. No recovery retry is burned: the episode terminates immediately as ABANDONED
   without cycling through model retries or burning the turn ceiling.
4. No completion is admitted.
5. In fixed-slot control accounting, the slot is retained as UNDETERMINABLE:
   binary count is lowered, and both denominators (n_scheduled, n_evaluable) are published.
"""

from __future__ import annotations

import dataclasses
import shutil
import tempfile
import unittest
from pathlib import Path
from typing import Any

from benchmarks.ladder.metrics import publish_control_report
from test.benchmarks.test_metric_veto import _bound_row
from test.benchmarks.test_preregistration import TASK_IDS, frozen_manifest
from test.agency import doubles
from test.runtime.test_harness_session import FakeClock, FakeEnvironment

from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.adapters.stores.lda_index import LdaRepoIndex
from vanguard.packages.agency import RunTermination
from vanguard.packages.agency.episode.admission_gate import AdmissionVerdict
from vanguard.packages.ports.index import DependencyEdge, RepositoryMap, Symbol, TestAssociation
from vanguard.packages.ports.event_store import Result
from vanguard.packages.runtime.root import (
    HarnessSession,
    Runtime,
    SessionPorts,
    TaskContext,
)


class RecordingPolicy:
    """A completion policy double that tracks the number of times it was evaluated."""

    def __init__(self, verdict: AdmissionVerdict | None = None) -> None:
        self.calls = 0
        self.verdict = verdict or AdmissionVerdict(True, "admissible")

    def evaluate(self, **kwargs: Any) -> AdmissionVerdict:
        self.calls += 1
        return self.verdict


class FailingRepoIndex:
    """IndexPort double whose queries and maps deterministically fail."""

    def index(self, root: str) -> Result[int]:
        return Result.fail("unavailable", "index unavailable")

    def files(self, *, prefix: str = "") -> Result[tuple[str, ...]]:
        return Result.fail("unavailable", "files unavailable")

    def symbols(self, *, name: str = "", path: str = "") -> Result[tuple[Symbol, ...]]:
        return Result.fail("unavailable", "symbols unavailable")

    def callers(self, *, symbol: str = "") -> Result[tuple[Symbol, ...]]:
        return Result.fail("unavailable", "callers unavailable")

    def get_callers(self, symbol: str) -> Result[tuple[Symbol, ...]]:
        return self.callers(symbol=symbol)

    def dependencies(self, *, path: str = "") -> Result[tuple[DependencyEdge, ...]]:
        return Result.fail("unavailable", "dependencies unavailable")

    def tests(self, *, path: str = "") -> Result[tuple[TestAssociation, ...]]:
        return Result.fail("unavailable", "tests unavailable")

    def repo_map(self, *, token_budget: int = 4000) -> Result[RepositoryMap]:
        return Result.fail("unavailable", "repo_map unavailable: index unbound")


class TestIndexUnboundDisposition(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self._tmp, True)
        self.repo = Path(self._tmp)
        (self.repo / "app.py").write_text("def main(): return 0\n", encoding="utf-8")

    def test_unbound_index_stops_immediately_with_zero_policy_calls_and_zero_retries(self) -> None:
        """T-135: policy consulted 0 times, no completion admitted, 0 retries burned."""
        tape = [doubles.finish("done")] * 8
        model = doubles.ScriptedModel(tape)
        policy = RecordingPolicy()

        # Harness with no index component declared
        harness = dataclasses.replace(
            Runtime.compose("vg-code-default", episode_id="ep-t135"),
            index_component=None,
        )
        session = HarnessSession(
            harness,
            SessionPorts(
                model=model,
                environment=FakeEnvironment(),
                clock=FakeClock(),
                store=SqliteEventStore(":memory:"),
                index=None,
                interactive=False,
                completion_policy=policy,
            ),
            TaskContext(
                brief="complete without index",
                repo_path=self.repo,
                project_id="proj-t135",
                run_id="run-t135",
                episode_id="ep-t135",
                principal="principal-test",
                max_turns=8,
            ),
        )

        result = session.run()

        # 1. Terminal is ABANDONED (not COMPLETED, not BUDGET_EXHAUSTED)
        self.assertIs(result.terminal, RunTermination.ABANDONED)
        self.assertIn("INDEX_UNBOUND", str(result.detail))

        # 2. Completion policy was consulted ZERO times
        self.assertEqual(policy.calls, 0, "Completion policy was consulted despite INDEX_UNBOUND")

        # 3. No recovery retries burned: stopped on the first turn
        self.assertEqual(session.turns_consumed(), 1)
        self.assertEqual(len(model.calls), 1)
        self.assertLess(session.turns_consumed(), 8)

    def test_failing_index_port_stops_immediately_as_index_unbound(self) -> None:
        """T-135: an index adapter that fails to map also terminates immediately without burning retries."""
        tape = [doubles.finish("done")] * 8
        model = doubles.ScriptedModel(tape)
        policy = RecordingPolicy()

        harness = Runtime.compose("vg-code-default", episode_id="ep-t135-fail")
        session = HarnessSession(
            harness,
            SessionPorts(
                model=model,
                environment=FakeEnvironment(),
                clock=FakeClock(),
                store=SqliteEventStore(":memory:"),
                index=FailingRepoIndex(),
                interactive=False,
                completion_policy=policy,
            ),
            TaskContext(
                brief="complete with failing index",
                repo_path=self.repo,
                project_id="proj-t135-fail",
                run_id="run-t135-fail",
                episode_id="ep-t135-fail",
                principal="principal-test",
                max_turns=8,
            ),
        )

        result = session.run()

        self.assertIs(result.terminal, RunTermination.ABANDONED)
        self.assertIn("INDEX_UNBOUND", str(result.detail))
        self.assertEqual(policy.calls, 0)
        self.assertEqual(session.turns_consumed(), 1)
        self.assertEqual(len(model.calls), 1)

    def test_fixed_slot_accounting_retains_slot_and_publishes_both_denominators(self) -> None:
        """T-135: slot is retained, n_scheduled and n_evaluable both published."""
        manifest = frozen_manifest()
        # 18 passing rows, but one slot is an INDEX_UNBOUND infrastructure failure
        rows = [
            _bound_row(manifest, task, settlement={} if idx < 18 else {"disposition": "failed"})
            for idx, task in enumerate(manifest["suite"]["tasks"])
        ]
        # Replace slot 29 with an INDEX_UNBOUND undeterminable outcome
        rows[29] = _bound_row(
            manifest,
            TASK_IDS[29],
            settlement={
                "terminal_status": "abandoned",
                "disposition": "undeterminable",
                "undeterminable_reason": "INDEX_UNBOUND: untestable workspace cannot be verified",
            },
        )

        report = publish_control_report(record=manifest, rows=rows)

        # Retained slot: total scheduled slots remain 30
        self.assertEqual(report["n_scheduled"], 30)
        # Missing/undeterminable slot does not count toward binary successes
        self.assertEqual(report["n_evaluable"], 29)
        self.assertEqual(report["n_missing"], 1)
        # Disposition must be UNDETERMINABLE because a scheduled slot could not be determined
        self.assertEqual(report["disposition"], "UNDETERMINABLE")


if __name__ == "__main__":
    unittest.main()
