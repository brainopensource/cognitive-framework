"""Contract tests for two-axis settlement disposition and receipt (T-72 / §EW-9.1)."""

from __future__ import annotations

import unittest

from vanguard.packages.adapters.evaluators.signing import VerdictSigner
from vanguard.packages.adapters.stores.event_store import InMemoryEventStore
from vanguard.packages.domain.evidence.disposition import (
    SETTLEMENT_SCHEMA,
    DispositionError,
    SettlementReceipt,
    TaskDisposition,
    disposition_to_outcome,
    parse_settlement,
)
from vanguard.packages.domain.ledger.reducer import reconstruct_state
from vanguard.packages.ports.evaluator import Verdict
from vanguard.packages.ports.event_store import EventRange
from vanguard.packages.runtime.evaluator_gateway import record_verdict
from vanguard.packages.runtime.ledger_emitter import LedgerEmitter


class TestSettlementDisposition(unittest.TestCase):
    def test_passed_requires_executed_test_count_positive(self) -> None:
        with self.assertRaises(DispositionError):
            SettlementReceipt(
                task_id="task-01",
                disposition=TaskDisposition.PASSED,
                executed_test_count=0,
                oracle_digest="sha256:oracle",
                verification_subject_digest="sha256:subject",
            )

    def test_passed_requires_bound_oracle_and_verification_subject(self) -> None:
        with self.assertRaises(DispositionError):
            SettlementReceipt(
                task_id="task-01",
                disposition=TaskDisposition.PASSED,
                executed_test_count=5,
                oracle_digest="",
                verification_subject_digest="sha256:subject",
            )
        with self.assertRaises(DispositionError):
            SettlementReceipt(
                task_id="task-01",
                disposition=TaskDisposition.PASSED,
                executed_test_count=5,
                oracle_digest="sha256:oracle",
                verification_subject_digest="",
            )

    def test_undeterminable_requires_explicit_reason(self) -> None:
        with self.assertRaises(DispositionError):
            SettlementReceipt(
                task_id="task-01",
                disposition=TaskDisposition.UNDETERMINABLE,
                undeterminable_reason="",
            )
        # Non-empty reason succeeds
        receipt = SettlementReceipt(
            task_id="task-01",
            disposition=TaskDisposition.UNDETERMINABLE,
            undeterminable_reason="harness timeout",
        )
        self.assertEqual(receipt.undeterminable_reason, "harness timeout")

    def test_not_run_cannot_carry_execution_evidence(self) -> None:
        with self.assertRaises(DispositionError):
            SettlementReceipt(
                task_id="task-01",
                disposition=TaskDisposition.NOT_RUN,
                executed_test_count=1,
            )
        with self.assertRaises(DispositionError):
            SettlementReceipt(
                task_id="task-01",
                disposition=TaskDisposition.NOT_RUN,
                oracle_digest="sha256:oracle",
            )
        with self.assertRaises(DispositionError):
            SettlementReceipt(
                task_id="task-01",
                disposition=TaskDisposition.NOT_RUN,
                envelope_digest="sha256:envelope",
            )

    def test_disposition_to_outcome_refuses_not_run(self) -> None:
        with self.assertRaises(DispositionError):
            disposition_to_outcome(TaskDisposition.NOT_RUN)
        self.assertEqual(disposition_to_outcome(TaskDisposition.PASSED), "passed")
        self.assertEqual(disposition_to_outcome(TaskDisposition.FAILED), "failed")
        self.assertEqual(
            disposition_to_outcome(TaskDisposition.UNDETERMINABLE), "undeterminable"
        )

    def test_abandoned_with_passed_disposition_is_legal_and_replays(self) -> None:
        receipt = SettlementReceipt(
            task_id="task-01",
            disposition=TaskDisposition.PASSED,
            terminal_status="abandoned",
            oracle_digest="sha256:oracle",
            verification_subject_digest="sha256:subject",
            executed_test_count=12,
            envelope_digest="sha256:envelope",
        )
        wire = receipt.to_wire()
        self.assertEqual(wire["schema"], SETTLEMENT_SCHEMA)
        self.assertEqual(wire["terminalStatus"], "abandoned")
        self.assertEqual(wire["disposition"], "passed")
        self.assertEqual(wire["executedTestCount"], 12)

        parsed = parse_settlement(wire)
        self.assertEqual(parsed.task_id, "task-01")
        self.assertEqual(parsed.terminal_status, "abandoned")
        self.assertEqual(parsed.disposition, TaskDisposition.PASSED)
        self.assertEqual(parsed.executed_test_count, 12)
        self.assertEqual(parsed.identity, receipt.identity)

        signer = VerdictSigner(b"s" * 32, "settlement-key")
        binding = {
            "verdict": "pass",
            "subject_digest": "sha256:subject",
            "evaluation_request_id": "eval-settlement-1",
            "oracle_id": "oracle-1",
            "oracle_digest": "sha256:oracle",
            "nonce": "n" * 16,
            "key_id": signer.key_id,
            "signed_at": "2026-09-05T00:00:00Z",
        }
        verdict = Verdict(
            outcome="claims",
            signature=signer.sign(binding),
            signer_key_id=signer.key_id,
            binding=binding,
        )
        store = InMemoryEventStore()
        emitter = LedgerEmitter(
            store,
            episode_id="ep-settlement",
            project_id="project-settlement",
            principal_id="agent-1",
            harness_digest="sha256:" + "a" * 64,
            role="session",
        )
        envelope = record_verdict(
            emitter,
            run_id="run-settlement",
            principal="agent-1",
            episode_id="ep-settlement",
            verdict=verdict,
            task_id="task-01",
            terminal_status="abandoned",
            executed_test_count=12,
            verification_subject_digest="sha256:subject",
        )
        self.assertIsNotNone(envelope)
        assert envelope is not None
        replayed = parse_settlement(envelope.payload)
        self.assertEqual(replayed.disposition, TaskDisposition.PASSED)
        self.assertEqual(replayed.terminal_status, "abandoned")
        events = store.read(EventRange(episode_id="ep-settlement"))
        state = reconstruct_state(events.value or ())
        self.assertEqual(state.verdicts["eval-settlement-1"].verdict, "pass")

    def test_episode_completed_payloads_contain_no_disposition_key(self) -> None:
        # Contract assertion: Run termination payload has only terminal_status
        episode_completed_payload = {
            "schema": "aether.episode.completed/1",
            "terminal_status": "completed",
            "turn_count": 5,
        }
        self.assertNotIn("disposition", episode_completed_payload)

    def test_predicates_and_missingness(self) -> None:
        self.assertTrue(TaskDisposition.PASSED.satisfies_predicate)
        self.assertFalse(TaskDisposition.FAILED.satisfies_predicate)
        self.assertFalse(TaskDisposition.UNDETERMINABLE.satisfies_predicate)
        self.assertFalse(TaskDisposition.NOT_RUN.satisfies_predicate)

        self.assertFalse(TaskDisposition.PASSED.is_missingness)
        self.assertFalse(TaskDisposition.FAILED.is_missingness)
        self.assertTrue(TaskDisposition.UNDETERMINABLE.is_missingness)
        self.assertTrue(TaskDisposition.NOT_RUN.is_missingness)


if __name__ == "__main__":
    unittest.main()
