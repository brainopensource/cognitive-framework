"""S22 / `C-01`: a refused proposal must reach the ledger.

`REQ-TRUST-001`, `A-07`. `engine.py` terminated on a provider failure or a
malformed proposal *before* `_emit_proposal`, so three different endings —
provider raised, provider returned no proposal, translator refused the shape —
left **no event at all**. The ledger showed an episode that never happened, and
a model whose batch of tool calls was refused was indistinguishable from a
model that was never asked.

Both directions are asserted here: a refused batch is recorded, and a single
tool call still dispatches normally.
"""

from __future__ import annotations

import unittest
from pathlib import Path
from typing import Any

from test.agency.doubles import ScriptedModel, effect, finish
from test.runtime.test_harness_session import FakeClock, FakeEnvironment
from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.agency.episode.engine import EpisodeEngine
from vanguard.packages.domain.ledger.reducer import reconstruct_state
from vanguard.packages.ports.event_store import EventRange, Result
from vanguard.packages.runtime.determinism import FixedClock, SeededRandom
from vanguard.packages.runtime.lab_driver import run_lab_task
from vanguard.packages.runtime.repair import StopReason
from vanguard.packages.runtime.root import (
    HarnessSession,
    Runtime,
    SessionPorts,
    TaskContext,
)
from vanguard.packages.runtime.scoring import score_arm
from vanguard.packages.runtime.session_log import session_log

ROOT = Path(__file__).resolve().parents[2]
DOGFOOD_01 = ROOT / "lab" / "tasks" / "dogfood-01-multi-turn-file-rollback"


class _Sink:
    def __init__(self) -> None:
        self.events: list[Any] = []

    def emit(self, event: Any) -> None:
        self.events.append(event)

    def append_intent(self, event: Any) -> None:
        self.events.append(event)


class _RefusingModel:
    """A provider whose answer the translator cannot use."""

    def __init__(self, message: str) -> None:
        self.message = message
        self.calls = 0

    def propose(self, context: Any, tools: Any, sampling: Any) -> Any:
        self.calls += 1
        return Result.fail("instrument_error", self.message)


def _engine(model: Any, sink: _Sink) -> EpisodeEngine:
    from vanguard.packages.kernel import Constraints, Scope

    scope = Scope(
        actions=frozenset({"fs.read"}),
        resources=({"kind": "fs", "root": "/workspace", "paths": ["/workspace"]},),
        constraints=Constraints(expires_at="2099-01-01T00:00:00.000Z", max_uses=10,
                                budget_usd_micros=1_000, max_depth=2),
        depth=0)
    return EpisodeEngine(kernel=object(), model=model, clock=FakeClock(),
                         events=sink, scope=scope, max_turns=3)


class ARefusedProposalIsRecorded(unittest.TestCase):
    """Direction one: the batch refusal leaves a trace."""

    MESSAGE = "multiple actions in one proposal are unsupported"

    def _run(self) -> _Sink:
        sink = _Sink()
        _engine(_RefusingModel(self.MESSAGE), sink).run(
            episode_id="ep-refused", run_id="run-refused",
            principal="agent-1", brief="do the task")
        return sink

    def test_the_episode_emits_a_terminal_event(self) -> None:
        kinds = [event.kind for event in self._run().events]
        self.assertIn("EpisodeCompleted", kinds)

    def test_the_terminal_event_carries_the_refusal_reason(self) -> None:
        event = next(e for e in self._run().events if e.kind == "EpisodeCompleted")
        self.assertEqual(event.payload["outcome"], "instrument_error")
        self.assertEqual(event.payload["detail"], self.MESSAGE)

    def test_the_ledger_is_no_longer_silent(self) -> None:
        """The defect: zero events for an episode that really ran."""

        self.assertGreater(len(self._run().events), 0)

    def test_no_proposal_is_claimed(self) -> None:
        """A refused answer is not a turn, and must not be recorded as one."""

        kinds = [event.kind for event in self._run().events]
        self.assertNotIn("ProposalProduced", kinds)

    def test_the_session_log_surfaces_the_refusal(self) -> None:
        log = session_log(self._run().events)
        self.assertEqual(log.entries, ())
        self.assertIsNotNone(log.terminal_refusal)
        self.assertEqual(log.terminal_refusal["detail"], self.MESSAGE)

    def test_a_provider_exception_is_recorded_too(self) -> None:
        class Raising:
            def propose(self, context: Any, tools: Any, sampling: Any) -> Any:
                raise RuntimeError("socket closed")

        sink = _Sink()
        _engine(Raising(), sink).run(episode_id="e", run_id="r",
                                     principal="p", brief="b")
        event = next(e for e in sink.events if e.kind == "EpisodeCompleted")
        self.assertIn("socket closed", event.payload["detail"])


class ASingleToolCallStillDispatches(unittest.TestCase):
    """Direction two: the hook must not disturb the working path."""

    def _run(self, script: list) -> dict:
        ports = SessionPorts(
            model=ScriptedModel(script), environment=FakeEnvironment(),
            clock=FixedClock(at="2026-08-17T00:00:00.000Z", step_ms=1),
            random=SeededRandom(seed=22), store=SqliteEventStore(":memory:"),
            interactive=False)
        task = TaskContext(brief="b", repo_path=Path("/workspace"),
                           run_id="run-ok", episode_id="ep-ok", max_turns=4)
        harness = Runtime.compose("vg-code-default", episode_id="ep-ok")
        result = HarnessSession(harness, ports, task).run()
        log = session_log(result.events)
        return {"log": log, "result": result}

    def test_a_single_effect_still_produces_a_turn(self) -> None:
        out = self._run([effect(action="fs.read", path="/workspace/a.py"), finish()])
        verbs = [entry.verb for entry in out["log"].entries if entry.verb]
        self.assertIn("fs.read", verbs)

    def test_a_normal_run_reports_no_terminal_refusal(self) -> None:
        out = self._run([effect(action="fs.read", path="/workspace/a.py"), finish()])
        self.assertIsNone(out["log"].terminal_refusal)

    def test_the_mock_driver_run_is_unchanged(self) -> None:
        result = run_lab_task("vg-code-default", DOGFOOD_01, max_attempts=1)
        self.assertEqual(result["outcome"], StopReason.ATTEMPTS_EXHAUSTED)
        self.assertGreater(result["turns"], 0)
        self.assertIsNone(result["terminalRefusal"])

    def test_the_ledger_still_reduces(self) -> None:
        """`EpisodeCompleted` is a kind the reducer already understands."""

        ports = SessionPorts(
            model=ScriptedModel([finish()]), environment=FakeEnvironment(),
            clock=FixedClock(at="2026-08-17T00:00:00.000Z", step_ms=1),
            random=SeededRandom(seed=1), store=SqliteEventStore(":memory:"),
            interactive=False)
        task = TaskContext(brief="b", repo_path=Path("/workspace"),
                           run_id="r", episode_id="e", max_turns=2)
        session = HarnessSession(
            Runtime.compose("vg-code-default", episode_id="e"), ports, task)
        session.run()
        read = ports.store.read(EventRange(episode_id="e"))
        self.assertIsNotNone(reconstruct_state(read.value or ()))


class MultiActionStaysInconclusive(unittest.TestCase):
    """S22-A-02. Never `oracle_green`, always counted."""

    ROWS = (
        {"taskId": "gf", "outcome": "instrument_error:multi_action_proposal"},
        {"taskId": "ok", "outcome": StopReason.ORACLE_GREEN},
    )

    def test_it_is_inconclusive(self) -> None:
        self.assertIn("gf", score_arm("live", self.ROWS).inconclusive)

    def test_it_stays_in_the_denominator(self) -> None:
        self.assertEqual(score_arm("live", self.ROWS).denominator, 2)

    def test_it_is_never_counted_resolved(self) -> None:
        self.assertEqual(score_arm("live", self.ROWS).resolved, 1)

    def test_the_rate_text_names_the_inconclusive_count(self) -> None:
        text = score_arm("live", self.ROWS).rate_text()
        self.assertIn("1/2", text)
        self.assertIn("inconclusive", text)


if __name__ == "__main__":
    unittest.main()
