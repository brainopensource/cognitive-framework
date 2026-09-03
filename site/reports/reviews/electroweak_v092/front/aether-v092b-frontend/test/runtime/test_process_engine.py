from __future__ import annotations

import unittest

from vanguard.packages.adapters.stores.event_store import InMemoryEventStore
from vanguard.packages.domain.canonicalisation.digest import digest_of
from vanguard.packages.domain.ledger.events import EventEnvelope
from vanguard.packages.runtime.governance import ProcessDefinition, ProcessEngine


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


def event(seq: int, kind: str, **payload: str) -> EventEnvelope:
    return EventEnvelope(
        schema_version="vg.4",
        event_id=f"018f3a2b-7c4d-7e1f-9a2b-{seq:012x}",
        scope="governance",
        seq=str(seq),
        occurred_at="2026-08-15T10:00:00.000Z",
        recorded_at="2026-08-15T10:00:00.000Z",
        principal="approval-process",
        principal_role="process",
        tenant_id="tenant-default",
        owner_id="owner-platform",
        confidentiality="internal",
        retention_class="extended",
        trainability="prohibited",
        redaction_status="none",
        payload={"kind": kind, "processId": "process-release", **payload},
    )


class ProcessEngineTest(unittest.TestCase):
    def test_pending_approval_blocks_other_declared_events(self) -> None:
        engine = ProcessEngine(definition())
        waiting = engine.apply(
            engine.initial_instance("process-release"),
            event(1, "ApprovalRequested", approvalId="approval-1"),
        )
        self.assertEqual(waiting.current_state, "awaiting_approval")
        self.assertEqual(waiting.pending_approvals, ("approval-1",))
        self.assertIs(
            engine.apply(waiting, event(2, "ApprovalResolved", approvalId="other", resolution="approved")),
            waiting,
        )

    def test_interrupted_instance_resumes_identically_from_ledger(self) -> None:
        engine = ProcessEngine(definition())
        events = [
            event(1, "ApprovalRequested", approvalId="approval-1"),
            event(2, "ApprovalResolved", approvalId="approval-1", resolution="approved"),
        ]
        before_restart = engine.replay("process-release", events)
        store = InMemoryEventStore()
        self.assertTrue(store.append(events).ok)

        after_restart = ProcessEngine(definition()).resume("process-release", store)

        self.assertEqual(after_restart, before_restart)
        self.assertEqual(after_restart.current_state, "published")
        self.assertEqual(after_restart.pending_approvals, ())
        self.assertEqual(len(after_restart.history), 2)

    def test_events_for_episode_or_another_process_do_not_advance(self) -> None:
        engine = ProcessEngine(definition())
        initial = engine.initial_instance("process-release")
        unrelated = event(1, "ApprovalRequested", approvalId="approval-1")
        unrelated = EventEnvelope(**{
            field: getattr(unrelated, field)
            for field in unrelated.__dataclass_fields__
            if field != "payload"
        }, payload={**unrelated.payload, "processId": "another-process"})
        self.assertIs(engine.apply(initial, unrelated), initial)


if __name__ == "__main__":
    unittest.main()
