"""Tests for ledger-triggered EvaluationListener (TSK-EVAL-001, D-02)."""

from __future__ import annotations

import unittest
from typing import Optional, Sequence

from vanguard.packages.domain.ledger.events import EventEnvelope
from vanguard.packages.ports.evaluator import EvaluationProtocol, EvaluatorPort, RunRef, Verdict
from vanguard.packages.ports.event_store import EventRange, EventStorePort, Result
from vanguard.packages.runtime.evaluation_listener import EvaluationListener


class InMemoryEventStore(EventStorePort):
    def __init__(self) -> None:
        self.events: list[EventEnvelope] = []

    def append(self, events: Sequence[EventEnvelope]) -> Result[None]:
        self.events.extend(events)
        return Result.success(None)

    def read(self, range_query: Optional[EventRange] = None) -> Result[Sequence[EventEnvelope]]:
        return Result.success(list(self.events))

    def digest(self, run_id: Optional[str] = None) -> Result[str]:
        return Result.success("digest-001")

    def count(self, run_id: Optional[str] = None) -> int:
        return len(self.events)


class FakeEvaluator(EvaluatorPort):
    def __init__(self, expected_verdict: str = "oracle_green") -> None:
        self.evaluated_runs: list[tuple[RunRef, EvaluationProtocol]] = []
        self.expected_verdict = expected_verdict

    def evaluate(self, run_ref: RunRef, protocol: EvaluationProtocol) -> Result[Verdict]:
        self.evaluated_runs.append((run_ref, protocol))
        verdict = Verdict(
            outcome="claims",
            claims=({"subject": "task-01", "predicate": "oracle_green", "value": True},),
            reason="all_oracles_passed",
            signature="fake-sig",
        )
        return Result.success(verdict)


class TestEvaluationListener(unittest.TestCase):
    def setUp(self) -> None:
        self.store = InMemoryEventStore()
        self.evaluator = FakeEvaluator(expected_verdict="oracle_green")
        self.verdicts: list[Verdict] = []
        self.listener = EvaluationListener(
            event_store=self.store,
            evaluator=self.evaluator,
            default_protocol="oracle_green",
            on_verdict_callback=lambda v: self.verdicts.append(v),
        )

    def test_ignores_non_episode_completed_events(self) -> None:
        env = EventEnvelope(
            schema_version="4.0.0",
            event_id="018f1111-2222-7000-8000-000000000001",
            scope="episode",
            seq="1",
            occurred_at="2026-08-18T00:00:00Z",
            recorded_at="2026-08-18T00:00:00Z",
            principal="principal:agent",
            principal_role="episode",
            tenant_id="tenant-1",
            owner_id="owner-1",
            confidentiality="internal",
            retention_class="standard",
            trainability="prohibited",
            redaction_status="none",
            run_id="run-001",
            episode_id="ep-001",
            payload={"kind": "ObservationProduced", "snapshot": "data"},
        )
        out = self.listener.process_envelope(env)
        self.assertIsNone(out)
        self.assertEqual(len(self.store.events), 0)
        self.assertEqual(len(self.evaluator.evaluated_runs), 0)

    def test_emits_evaluation_requested_on_episode_completed(self) -> None:
        env = EventEnvelope(
            schema_version="4.0.0",
            event_id="018f1111-2222-7000-8000-000000000002",
            scope="episode",
            seq="10",
            occurred_at="2026-08-18T00:01:00Z",
            recorded_at="2026-08-18T00:01:00Z",
            principal="principal:agent",
            principal_role="episode",
            tenant_id="tenant-1",
            owner_id="owner-1",
            confidentiality="internal",
            retention_class="standard",
            trainability="prohibited",
            redaction_status="none",
            run_id="run-001",
            episode_id="ep-001",
            payload={"kind": "EpisodeCompleted", "outcome": "resolved", "evaluationProtocol": "oracle_green"},
        )
        out = self.listener.process_envelope(env)
        self.assertIsNotNone(out)
        self.assertEqual(out.payload["kind"], "EvaluationRequested")
        self.assertEqual(out.payload["runId"], "run-001")
        self.assertEqual(out.payload["protocol"], "oracle_green")

        # Verified appended to ledger
        self.assertEqual(len(self.store.events), 1)
        self.assertEqual(self.store.events[0].payload["kind"], "EvaluationRequested")

        # Verified evaluator invoked
        self.assertEqual(len(self.evaluator.evaluated_runs), 1)
        self.assertEqual(len(self.verdicts), 1)
        self.assertEqual(self.verdicts[0].outcome, "claims")


if __name__ == "__main__":
    unittest.main()
