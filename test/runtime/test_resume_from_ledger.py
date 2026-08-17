"""Suspend and resume from the ledger alone.

S8-A-02. `run()` looped `for _ in range(max_segments)` building a **fresh**
`Episode` each pass, so:

  - the real turn bound was `max_turns × max_segments` = 8 × 8 = **64**, not 8,
    and nothing said so;
  - no-progress detection reset every segment, making `FT-02` livelock
    undetectable across an approval;
  - resume depended on live object identity (`_LayeredOperator._dialogue`)
    rather than on the ledger, which is restart wearing the word resume.

`003` A9, `T3.6`. The reuse is deliberate: `domain/ledger/reducer.py` already
reconstructs episode state for crash recovery, and approval suspension is the
same mechanism with a different trigger.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from test.agency.doubles import ScriptedModel, effect, finish
from test.runtime.test_harness_session import FakeEnvironment, FakeClock
from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.domain.ledger.reducer import (
    compute_state_digest,
    reconstruct_state,
)
from vanguard.packages.ports.event_store import EventRange
from vanguard.packages.runtime.determinism import FixedClock, SeededRandom
from vanguard.packages.runtime.governance.approvals import OperatorSigner
from vanguard.packages.runtime.root import (
    HarnessSession,
    Runtime,
    SessionPorts,
    TaskContext,
)

ROOT_PY = Path(__file__).resolve().parents[2] / "vanguard" / "packages" / "runtime" / "root.py"

OPERATOR_SIGNER = OperatorSigner(b"test-operator-held-approval-key")
OPERATOR_KEY = OPERATOR_SIGNER.public_bytes


def approve_everything(challenge):
    """A human who always says yes.

    This is what makes the 64 case reachable: each approval used to start a
    *fresh* segment with a fresh `max_turns`, so an agreeable reviewer bought
    the run another eight turns every time.
    """
    return OPERATOR_SIGNER.approve(challenge, reviewer="agent-1")


PATCH = {"kind": "effect", "action": "patch.apply",
         "resource": {"kind": "fs", "root": "/workspace", "paths": ["/workspace"]},
         "args": {"diff": "--- a\n+++ b\n"}}


def _ports(script: list, store: SqliteEventStore, **overrides) -> SessionPorts:
    base = dict(
        model=ScriptedModel(script),
        environment=FakeEnvironment(),
        clock=FixedClock(at="2026-08-16T00:00:00.000Z", step_ms=1),
        random=SeededRandom(seed=2026),
        store=store,
        interactive=True,
    )
    base.update(overrides)
    return SessionPorts(**base)


def _task(*, max_turns: int = 8, episode_id: str = "ep-resume-1") -> TaskContext:
    return TaskContext(
        brief="fix the failing suite", repo_path=Path("/workspace"),
        run_id="run-resume-1", episode_id=episode_id,
        principal="agent-1", max_turns=max_turns)


def _digest_from_store(store: SqliteEventStore, episode_id: str) -> str:
    """Reduce the ledger for one episode. Nothing in memory contributes."""
    read = store.read(EventRange(episode_id=episode_id))
    assert read.ok and read.value is not None
    return compute_state_digest(reconstruct_state(read.value))


class TheSegmentLoopIsGone(unittest.TestCase):
    def test_max_segments_does_not_appear_in_root(self) -> None:
        """DoD: `grep -c max_segments root.py` -> 0."""

        source = ROOT_PY.read_text(encoding="utf-8")
        self.assertNotIn("max_segments", source)

    def test_no_fresh_episode_is_built_per_segment(self) -> None:
        source = ROOT_PY.read_text(encoding="utf-8")
        self.assertNotIn("for _ in range(", source)


class MaxTurnsIsHardAcrossApproval(unittest.TestCase):
    """The 64 case. `max_turns` bounds the run, not each segment of it."""

    def _run_with_turn_cap(self, max_turns: int) -> tuple[int, object]:
        store = SqliteEventStore(":memory:")
        # A model that never finishes: it proposes a privileged patch every
        # turn, so without a hard bound it would suspend and re-enter forever.
        script = [dict(PATCH) for _ in range(64)]
        session = HarnessSession(
            Runtime.compose("vg-code-default", episode_id="ep-cap-1"),
            _ports(script, store, approver=approve_everything,
                   approval_key=OPERATOR_KEY),
            _task(max_turns=max_turns, episode_id="ep-cap-1"))
        result = session.run()
        read = store.read(EventRange(episode_id="ep-cap-1"))
        state = reconstruct_state(read.value or ())
        return len(state.proposals), result

    def test_turns_never_exceed_max_turns_in_total(self) -> None:
        proposals, _ = self._run_with_turn_cap(4)
        self.assertLessEqual(
            proposals, 4,
            "turns reset across the approval boundary; this is the 8x8=64 defect")

    def test_a_smaller_cap_yields_strictly_fewer_turns(self) -> None:
        """If the bound were per-segment, both would run to the same ceiling."""

        few, _ = self._run_with_turn_cap(2)
        more, _ = self._run_with_turn_cap(6)
        self.assertLessEqual(few, 2)
        self.assertLessEqual(more, 6)
        self.assertLess(few, 8)

    def test_the_bound_is_not_the_product_of_two_numbers(self) -> None:
        proposals, _ = self._run_with_turn_cap(8)
        self.assertLessEqual(proposals, 8, "real bound was max_turns x max_segments")


class ResumeReconstructsFromTheLedgerAlone(unittest.TestCase):
    def test_a_suspended_run_leaves_a_reducible_ledger(self) -> None:
        store = SqliteEventStore(":memory:")
        session = HarnessSession(
            Runtime.compose("vg-code-default", episode_id="ep-susp-1"),
            _ports([dict(PATCH), finish()], store),
            _task(episode_id="ep-susp-1"))
        session.run()
        self.assertIsNotNone(_digest_from_store(store, "ep-susp-1"))

    def test_the_digest_is_identical_with_every_live_object_discarded(self) -> None:
        """Stop condition 2: if a live object must cross, that is restart."""

        store = SqliteEventStore(":memory:")
        session = HarnessSession(
            Runtime.compose("vg-code-default", episode_id="ep-susp-2"),
            _ports([dict(PATCH), finish()], store),
            _task(episode_id="ep-susp-2"))
        session.run()
        in_session = session.state_digest()

        # Every in-memory object is dropped. Only the store survives.
        del session
        from_ledger = _digest_from_store(store, "ep-susp-2")
        self.assertEqual(in_session, from_ledger)

    def test_a_second_reduction_of_the_same_ledger_agrees(self) -> None:
        store = SqliteEventStore(":memory:")
        HarnessSession(
            Runtime.compose("vg-code-default", episode_id="ep-susp-3"),
            _ports([dict(PATCH), finish()], store),
            _task(episode_id="ep-susp-3")).run()
        self.assertEqual(_digest_from_store(store, "ep-susp-3"),
                         _digest_from_store(store, "ep-susp-3"))

    def test_turns_consumed_are_read_from_the_ledger_not_from_the_operator(self) -> None:
        store = SqliteEventStore(":memory:")
        session = HarnessSession(
            Runtime.compose("vg-code-default", episode_id="ep-susp-4"),
            _ports([dict(PATCH), finish()], store),
            _task(episode_id="ep-susp-4"))
        session.run()
        read = store.read(EventRange(episode_id="ep-susp-4"))
        state = reconstruct_state(read.value or ())
        self.assertEqual(session.turns_consumed(), len(state.proposals))

    def test_the_session_exposes_no_dialogue_carried_across_re_entry(self) -> None:
        """Re-entry must not depend on `_LayeredOperator._dialogue` identity."""

        import inspect

        source = inspect.getsource(HarnessSession.run)
        self.assertNotIn("_dialogue", source)


if __name__ == "__main__":
    unittest.main()
