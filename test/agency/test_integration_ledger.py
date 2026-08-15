"""`S3-INT-001` / `REQ-EXEC-001` + `REQ-EXEC-002` — one ledger, two readers.

An episode turn and a process resume are unrelated mechanisms: one is an
open-ended loop driven by a cassette, the other a finite reducer that runs
without any model at all. They share exactly one thing, and it has to be the
durable record — two stores would give a run two irreconcilable accounts of
itself, and reconciliation of an interrupted effect would have no ground truth
to reconcile against (`K-47`).

So the assertions below are about the *record*, not about either mechanism
talking to the other. The process engine must reconstitute its state without
observing the episode, and the episode must reach its effect without the
process engine, while both appear in one ordered ledger.
"""

from __future__ import annotations

import unittest

from vanguard.packages.domain.canonicalisation.digest import digest_of
from vanguard.packages.kernel import FailurePath
from vanguard.packages.runtime.governance import ProcessDefinition, ProcessEngine

from test.agency import doubles
from test.agency.test_episode import build, run
from test.support.composition import SharedLedger


def definition() -> ProcessDefinition:
    content = {
        "states": ["draft", "awaiting_approval", "published"],
        "initialState": "draft",
        "transitions": [
            {"from": "draft", "eventKind": "ApprovalRequested", "to": "awaiting_approval"},
            {"from": "awaiting_approval", "eventKind": "ApprovalResolved", "to": "published"},
        ],
        "approvalPoints": ["awaiting_approval"],
        "boundEffectVerbs": ["git.publish"],
    }
    return ProcessDefinition.from_wire({"definitionDigest": digest_of(content), **content})


class SharedLedgerIntegration(unittest.TestCase):
    def setUp(self) -> None:
        self.ledger = SharedLedger()
        self.harness, self.engine = build(
            [doubles.effect(), doubles.finish()],
            ledger=self.ledger, sink=self.ledger)

    def test_one_episode_turn_and_one_process_resume_share_the_ledger(self) -> None:
        outcome = run(self.engine, self.harness)
        self.assertIs(outcome.dispatches[0].failure, FailurePath.OK)

        engine = ProcessEngine(definition())
        self.ledger.append_governance("ApprovalRequested",
                                      process_id="process-release",
                                      approvalId="approval-1")
        self.ledger.append_governance("ApprovalResolved",
                                      process_id="process-release",
                                      approvalId="approval-1", resolution="approved")
        instance = engine.resume("process-release", self.ledger.store)

        self.assertEqual(instance.current_state, "published")
        self.assertIn("EffectStarted", self.ledger.kinds(scope="episode"))
        self.assertEqual(self.ledger.kinds(scope="governance"),
                         ["ApprovalRequested", "ApprovalResolved"])
        # One store, one monotonic sequence across both scopes.
        seqs = [int(event.seq) for event in self.ledger.events()]
        self.assertEqual(seqs, sorted(seqs))
        self.assertEqual(len(seqs), len(set(seqs)))
        self.assertGreater(len(seqs), len(self.ledger.events(scope="governance")))

    def test_the_process_resume_reads_no_episode_event(self) -> None:
        """`REQ-EXEC-002` margin: zero governance transitions requiring a
        model — and, here, zero requiring an episode. The episode events are
        in the same ledger and must be inert to the reducer."""
        run(self.engine, self.harness)
        engine = ProcessEngine(definition())

        self.ledger.append_governance("ApprovalRequested",
                                      process_id="process-release",
                                      approvalId="approval-1")
        interrupted = engine.resume("process-release", self.ledger.store)
        self.assertEqual(interrupted.current_state, "awaiting_approval")

        # Replaying the whole ledger — episode events included — is identical
        # to replaying the governance scope alone.
        self.assertEqual(
            engine.replay("process-release", self.ledger.events()).to_wire(),
            interrupted.to_wire())

    def test_an_intent_that_cannot_be_durably_written_stops_the_effect(self) -> None:
        """`F-21a`. A shared ledger must not soften the one failure the split
        emission exists to make visible."""
        failing = SharedLedger(fails=True)
        harness, engine = build([doubles.effect(), doubles.finish()],
                                ledger=failing, sink=SharedLedger())
        outcome = run(engine, harness)

        self.assertIs(outcome.dispatches[0].failure, FailurePath.INTENT_APPEND_FAILED)
        self.assertEqual(len(harness.adapter.calls), 0)


if __name__ == "__main__":
    unittest.main()
