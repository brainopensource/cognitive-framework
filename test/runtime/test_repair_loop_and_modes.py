"""W11-A: multi-turn repair, the two modes, the ledger-only session log.

A single episode is one pass. A repair task is not: observe, propose, patch,
run the suite, read the failure, go again. Emitting a `completed` receipt after
one pass reports a task finished that was merely attempted.

Termination is proved by name here — a run that ran out of budget must never be
readable as a run that failed to fix the bug.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from test.agency.doubles import ScriptedModel, finish
from test.runtime.test_harness_session import FakeEnvironment
from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.kernel import Mode
from vanguard.packages.runtime.determinism import FixedClock, SeededRandom
from vanguard.packages.runtime.repair import (
    RepairOutcome,
    StopReason,
    drive_until_green,
)
from vanguard.packages.runtime.root import (
    HarnessSession,
    Runtime,
    SessionPorts,
    TaskContext,
)
from vanguard.packages.runtime.session_log import session_log
from vanguard.packages.runtime.telemetry import RunTelemetry


class _Result:
    """A RunResult-shaped stand-in for driver tests."""

    def __init__(self, *, green: bool = False, tokens: int | None = 10,
                 instrument_error: str | None = None, signal: str = "x") -> None:
        self.green = green
        self.signal = signal
        self.instrument_error = instrument_error
        self.telemetry = RunTelemetry(turns=1, prompt_tokens=tokens,
                                      completion_tokens=tokens)


class TheLoopRunsUntilGreenOrBudget(unittest.TestCase):
    def test_it_keeps_going_after_a_red_oracle(self) -> None:
        attempts = []

        def run(attempt: int) -> _Result:
            attempts.append(attempt)
            return _Result(green=attempt == 3, signal=f"s{attempt}")

        outcome = drive_until_green(run, oracle=lambda r: r.green, max_attempts=5)
        self.assertEqual(attempts, [1, 2, 3])
        self.assertEqual(outcome.stop_reason, StopReason.ORACLE_GREEN)
        self.assertTrue(outcome.succeeded)

    def test_one_pass_is_not_reported_as_completed(self) -> None:
        """The degenerate row: attempted is not finished."""

        outcome = drive_until_green(
            lambda attempt: _Result(green=False, signal=f"s{attempt}"),
            oracle=lambda r: r.green, max_attempts=3)
        self.assertFalse(outcome.succeeded)
        self.assertNotEqual(outcome.stop_reason, StopReason.ORACLE_GREEN)

    def test_running_out_of_attempts_is_named_not_silent(self) -> None:
        outcome = drive_until_green(
            lambda attempt: _Result(signal=f"s{attempt}"),
            oracle=lambda r: False, max_attempts=2)
        self.assertEqual(outcome.attempts, 2)
        self.assertIn("without a green oracle", outcome.detail)

    def test_a_token_budget_stops_the_loop_and_says_so(self) -> None:
        outcome = drive_until_green(
            lambda attempt: _Result(tokens=100, signal=f"s{attempt}"),
            oracle=lambda r: False, max_attempts=10, max_tokens=150)
        self.assertEqual(outcome.stop_reason, StopReason.BUDGET_EXHAUSTED)
        self.assertLess(outcome.attempts, 10)

    def test_budget_exhaustion_is_distinguishable_from_failure_to_fix(self) -> None:
        spent = drive_until_green(
            lambda a: _Result(tokens=100, signal=f"s{a}"),
            oracle=lambda r: False, max_attempts=10, max_tokens=150)
        tried = drive_until_green(
            lambda a: _Result(tokens=1, signal=f"s{a}"),
            oracle=lambda r: False, max_attempts=2, max_tokens=10_000)
        self.assertNotEqual(spent.stop_reason, tried.stop_reason)

    def test_repeating_itself_stops_rather_than_burning_the_budget(self) -> None:
        outcome = drive_until_green(
            lambda attempt: _Result(signal="identical"),
            oracle=lambda r: False, max_attempts=10,
            progress_of=lambda r: r.signal)
        self.assertEqual(outcome.stop_reason, StopReason.NO_PROGRESS)
        self.assertEqual(outcome.attempts, 2)

    def test_an_instrument_error_stops_and_is_not_a_failed_repair(self) -> None:
        outcome = drive_until_green(
            lambda attempt: _Result(instrument_error="model_not_invoked"),
            oracle=lambda r: False, max_attempts=5)
        self.assertEqual(outcome.stop_reason, StopReason.INSTRUMENT_ERROR)
        self.assertFalse(outcome.succeeded)

    def test_tokens_accumulate_across_attempts_as_integers(self) -> None:
        outcome = drive_until_green(
            lambda attempt: _Result(tokens=7, signal=f"s{attempt}"),
            oracle=lambda r: False, max_attempts=3)
        self.assertEqual(outcome.telemetry.prompt_tokens, 21)
        self.assertIsInstance(outcome.telemetry.total_tokens, int)

    def test_absent_token_reports_stay_absent_across_attempts(self) -> None:
        outcome = drive_until_green(
            lambda attempt: _Result(tokens=None, signal=f"s{attempt}"),
            oracle=lambda r: False, max_attempts=2)
        self.assertIsNone(outcome.telemetry.prompt_tokens)

    def test_the_oracle_is_supplied_from_outside_the_loop(self) -> None:
        """`A-05`: a loop that grades its own work is the inversion."""

        import inspect

        source = inspect.getsource(drive_until_green)
        for forbidden in ("pytest", "subprocess", "evaluate(", "verdict"):
            self.assertNotIn(forbidden, source)


class TheTwoModesAlreadyExist(unittest.TestCase):
    """W11-A item 2: prove what `root.py` already does. No TUI."""

    def _session(self, *, interactive: bool) -> HarnessSession:
        ports = SessionPorts(
            model=ScriptedModel([finish()]),
            environment=FakeEnvironment(),
            clock=FixedClock(at="2026-08-17T00:00:00.000Z", step_ms=1),
            random=SeededRandom(seed=11),
            store=SqliteEventStore(":memory:"),
            interactive=interactive,
        )
        task = TaskContext(brief="modes", repo_path=Path("/workspace"),
                           run_id="run-modes", episode_id="ep-modes", max_turns=2)
        return HarnessSession(
            Runtime.compose("vg-code-default", episode_id="ep-modes"), ports, task)

    def test_interactive_composes_the_interactive_mode(self) -> None:
        self.assertIs(self._session(interactive=True).policy.base._mode, Mode.INTERACTIVE)

    def test_non_interactive_composes_benchmark_mode(self) -> None:
        self.assertIs(self._session(interactive=False).policy.base._mode, Mode.BENCHMARK)

    def _ask_about_everything(self, session: HarnessSession):
        """The same session, forced to ask about every declared capability.

        `K-17` is about what benchmark mode does *with* an ask, so proving it
        needs a policy that asks. Since T-70 the product default no longer
        asks about the verbs it declares -- that is the point of T-70 -- so the
        threshold is lowered here explicitly rather than smuggled in from a
        hardcoded composition value.
        """
        from vanguard.packages.kernel import StandardPolicy

        return StandardPolicy(
            parent_scope=session.scope, mode=session.policy.base._mode,
            approval_required_above="low", risk_of=session.harness.risk_of)

    def test_benchmark_mode_denies_rather_than_suspending(self) -> None:
        """`K-17`: a benchmark that blocks for a human has unbounded wall clock
        *and* a human contributing to the measured outcome."""

        from vanguard.packages.kernel import FailurePath, Outcome

        session = self._session(interactive=False)
        decision = self._ask_about_everything(session).authorize(
            _patch_request(), widens_capability=False,
            requested_scope=session.scope)
        self.assertIs(decision.outcome, Outcome.REJECT)
        self.assertIs(decision.failure, FailurePath.DENIED_ASK_FAIL_CLOSED)

    def test_interactive_mode_requires_approval_for_a_privileged_patch(self) -> None:
        """`F-08`. The declared `mode: assisted` keeps a human on the run."""

        from vanguard.packages.kernel import Outcome

        session = self._session(interactive=True)
        decision = session.policy.authorize(
            _patch_request(), widens_capability=False,
            requested_scope=session.scope)
        self.assertIs(decision.outcome, Outcome.REQUIRE_APPROVAL)

    def test_a_benchmark_dispatches_the_verb_the_manifest_declared(self) -> None:
        """T-70. Successor to the assertion that a benchmark denied it.

        `vg-code-default` declares `threshold: standard`, so its own
        `patch.apply` is not an ask at all and never becomes `F-07`'s denial.
        A coding preset that cannot patch under benchmark measures nothing.
        """
        from vanguard.packages.kernel import FailurePath, Outcome

        session = self._session(interactive=False)
        decision = session.policy.authorize(
            _patch_request(), widens_capability=False,
            requested_scope=session.scope)
        self.assertIs(decision.outcome, Outcome.ALLOW)
        self.assertIsNot(decision.failure, FailurePath.DENIED_ASK_FAIL_CLOSED)

    def test_benchmark_mode_never_hangs_waiting_for_a_human(self) -> None:
        """The refusal is synchronous: no suspension token is issued."""

        from vanguard.packages.kernel import Outcome

        session = self._session(interactive=False)
        decision = self._ask_about_everything(session).authorize(
            _patch_request(), widens_capability=False,
            requested_scope=session.scope)
        self.assertIsNot(decision.outcome, Outcome.REQUIRE_APPROVAL)
        self.assertIsNone(getattr(decision, "granted_scope", None))


def _patch_request():
    from vanguard.packages.kernel import EffectRequest

    return EffectRequest(
        action="patch.apply",
        resource={"kind": "fs", "root": "/workspace", "paths": ["/workspace"]},
        args={"diff": "--- a\n+++ b\n"}, principal="agent-1", run_id="run-modes")


class _Event:
    def __init__(self, kind: str, **payload) -> None:
        self.payload = {"kind": kind, **payload}


class TheSessionLogIsALedgerProjection(unittest.TestCase):
    """W11-A item 3. No second DB — this reduces events that already exist."""

    def test_a_turn_and_its_receipt_become_one_entry(self) -> None:
        log = session_log([
            _Event("ProposalProduced", toolCalls=[{"action": "fs.read"}],
                   promptTokens=120, completionTokens=8),
            _Event("EffectCompleted"),
        ])
        entry = log.entries[0]
        self.assertEqual((entry.turn, entry.verb, entry.receipt),
                         (1, "fs.read", "EffectCompleted"))
        self.assertEqual(entry.prompt_tokens, 120)

    def test_turns_are_numbered_in_ledger_order(self) -> None:
        log = session_log([
            _Event("ProposalProduced", toolCalls=[{"action": "fs.read"}]),
            _Event("EffectCompleted"),
            _Event("ProposalProduced", toolCalls=[{"action": "patch.apply"}]),
            _Event("EffectCompleted"),
        ])
        self.assertEqual([e.turn for e in log.entries], [1, 2])
        self.assertEqual([e.verb for e in log.entries], ["fs.read", "patch.apply"])

    def test_a_refused_effect_is_a_dead_end(self) -> None:
        log = session_log([
            _Event("ProposalProduced", toolCalls=[{"action": "proc.exec"}]),
            _Event("AuthorizationDenied", reason="not granted"),
        ])
        self.assertEqual(log.dead_ends, (1,))
        self.assertEqual(log.entries[0].detail, "not granted")

    def test_compaction_and_cache_miss_are_carried(self) -> None:
        log = session_log([
            _Event("ProposalProduced", toolCalls=[{"action": "fs.read"}],
                   compacted=True, cacheMiss=True),
            _Event("EffectCompleted"),
        ])
        self.assertTrue(log.entries[0].compacted)
        self.assertEqual(log.cache_misses, (1,))

    def test_an_unreported_cache_state_is_none_not_false(self) -> None:
        """Absent is absent. `False` would claim the cache hit."""

        log = session_log([_Event("ProposalProduced", toolCalls=[{"action": "fs.read"}])])
        self.assertIsNone(log.entries[0].cache_miss)

    def test_it_opens_no_store_of_its_own(self) -> None:
        import inspect

        import vanguard.packages.runtime.session_log as module

        source = inspect.getsource(module)
        for forbidden in ("sqlite3", "open(", "Path(", "connect"):
            self.assertNotIn(forbidden, source)

    def test_an_empty_ledger_is_an_empty_log(self) -> None:
        self.assertEqual(session_log([]).entries, ())


class TheIndexIsBoundOnlyWhenDeclared(unittest.TestCase):
    """W11-A item 4. BETA adds the JSON; this is the bind."""

    def test_a_pack_declaring_no_index_binds_none(self) -> None:
        harness = Runtime.compose("vg-shell-only", episode_id="ep-idx")
        self.assertIsNone(harness.index_component)

    def test_supplying_an_index_to_a_pack_that_declares_none_is_refused(self) -> None:
        """An unasked-for component is a capability nobody authorised."""

        from vanguard.packages.adapters.stores.repo_index import InMemoryRepoIndex
        from vanguard.packages.runtime.root import CompositionError

        ports = SessionPorts(
            model=ScriptedModel([finish()]), environment=FakeEnvironment(),
            clock=FixedClock(at="2026-08-17T00:00:00.000Z"),
            random=SeededRandom(seed=1), store=SqliteEventStore(":memory:"),
            index=InMemoryRepoIndex(), interactive=False)
        task = TaskContext(brief="idx", repo_path=Path("/workspace"),
                           run_id="r", episode_id="ep-idx")
        with self.assertRaises(CompositionError):
            HarnessSession(Runtime.compose("vg-shell-only", episode_id="ep-idx"),
                           ports, task)


if __name__ == "__main__":
    unittest.main()
