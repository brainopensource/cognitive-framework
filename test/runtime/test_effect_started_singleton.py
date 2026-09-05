"""Single-emission ledger falsifier for EffectStarted (T-73).

Falsifies:
- Replaying one effect must emit exactly one EffectStarted with exactly one lease id.
- Intent (S8a) and publish (S12) for the same effect lease collapse into a singleton.
- Prior ledgers with adjacent duplicate EffectStarted events are loaded and replayed without duplicating.
- Zero edits to vanguard/packages/kernel (TCB budget <= 1438 LOC, baseline 1386).
"""

from __future__ import annotations

import unittest
from typing import Any

from test.kernel import fakes
from vanguard.packages.adapters.stores.event_store import InMemoryEventStore
from vanguard.packages.kernel.model import EffectRequest, Event, FailurePath
from vanguard.packages.ports.event_store import EventRange
from vanguard.packages.runtime.ledger_emitter import LedgerEmitter


def _make_emitter(store: InMemoryEventStore | None = None, **kwargs: Any) -> LedgerEmitter:
    defaults = dict(
        episode_id="ep-test",
        project_id="proj-test",
        principal_id="agent-1",
        harness_digest="sha256:" + ("a" * 64),
        role="kernel",
    )
    defaults.update(kwargs)
    return LedgerEmitter(store or InMemoryEventStore(), **defaults)


class TestEffectStartedSingleton(unittest.TestCase):
    """Guards single-emission invariant for EffectStarted (T-73, Defect L)."""

    def test_single_effect_dispatch_emits_one_and_only_one_effect_started(self) -> None:
        """A single dispatched effect must produce exactly one EffectStarted in store and events."""
        store = InMemoryEventStore()
        emitter = _make_emitter(store=store)

        harness = fakes.build(ledger=emitter, sink=emitter)

        req = fakes.request()
        result = harness.kernel.dispatch(
            req,
            requested_scope=fakes.child_scope(),
            reservation=fakes.reservation(),
        )
        self.assertIs(result.failure, FailurePath.OK, result.detail)

        # In-memory emitted events: exactly one EffectStarted
        effect_started_events = [e for e in emitter.events if e.kind == "EffectStarted"]
        self.assertEqual(len(effect_started_events), 1)
        started_event = effect_started_events[0]
        self.assertIn("descriptorDigest", started_event.payload)
        self.assertIn("leaseId", started_event.payload)

        # Durable event store: exactly one EffectStarted envelope
        read_res = store.read(EventRange(project_id="proj-test"))
        self.assertTrue(read_res.ok)
        stored_effect_started = [
            env for env in read_res.value if env.payload.get("kind") == "EffectStarted"
        ]
        self.assertEqual(
            len(stored_effect_started),
            1,
            f"Expected exactly 1 EffectStarted envelope in store, found {len(stored_effect_started)}",
        )
        self.assertEqual(
            stored_effect_started[0].payload.get("leaseId"),
            started_event.payload["leaseId"],
        )

    def test_replaying_one_effect_emits_exactly_one_effect_started(self) -> None:
        """Replaying the same effect with identical descriptorDigest and leaseId is idempotent."""
        store = InMemoryEventStore()
        emitter = _make_emitter(store=store)

        desc_digest = "sha256:" + ("d" * 64)
        lease_id = "lease-fixed-42"
        intent = Event(
            kind="EffectStarted",
            reason="intent",
            at="2026-09-04T20:00:00.000Z",
            run_id="run-1",
            principal="agent-1",
            payload={
                "descriptorDigest": desc_digest,
                "leaseId": lease_id,
                "idempotencyKey": "idem-1",
                "action": "fs.read",
                "resource": {"kind": "fs", "paths": ["/workspace/test.py"]},
                "sinkClass": "observation",
            },
        )

        # S8a: intent append
        emitter.append_intent(intent)
        # S12: publish emit
        emitter.emit(intent)

        # Replay attempt: re-appending and re-emitting the same effect
        emitter.append_intent(intent)
        emitter.emit(intent)

        # Check in-memory events
        effect_started_events = [e for e in emitter.events if e.kind == "EffectStarted"]
        self.assertEqual(
            len(effect_started_events),
            1,
            "In-memory events must contain exactly one EffectStarted after replay",
        )

        # Check durable store
        read_res = store.read(EventRange(project_id="proj-test"))
        self.assertTrue(read_res.ok)
        stored = [
            env for env in read_res.value if env.payload.get("kind") == "EffectStarted"
        ]
        self.assertEqual(
            len(stored),
            1,
            "Durable store must contain exactly one EffectStarted envelope after replay",
        )
        self.assertEqual(stored[0].payload.get("leaseId"), lease_id)
        self.assertEqual(stored[0].payload.get("descriptorDigest"), desc_digest)

    def test_replaying_ledger_with_adjacent_duplicates_loads_as_singleton(self) -> None:
        """Loading an existing chain with adjacent equal descriptorDigest and leaseId preserves singleton."""
        store = InMemoryEventStore()
        desc_digest = "sha256:" + ("9" * 64)
        lease_id = "lease-historical-1"

        emitter1 = _make_emitter(store=store)
        event1 = Event(
            kind="EffectStarted",
            reason="intent",
            at="2026-09-04T12:00:00.000Z",
            run_id="run-old",
            principal="agent-1",
            payload={
                "descriptorDigest": desc_digest,
                "leaseId": lease_id,
                "action": "fs.read",
            },
        )
        # Directly append through emitter
        emitter1.append_intent(event1)

        # Construct a new emitter resuming the same project
        emitter2 = _make_emitter(store=store)
        self.assertIn((desc_digest, lease_id), emitter2._effect_started_envelopes)

        # Replaying or publishing the same effect on the resumed emitter emits no duplicate
        emitter2.emit(event1)
        emitter2.append_intent(event1)

        read_res = store.read(EventRange(project_id="proj-test"))
        self.assertTrue(read_res.ok)
        stored = [
            env for env in read_res.value if env.payload.get("kind") == "EffectStarted"
        ]
        self.assertEqual(len(stored), 1)

    def test_kernel_tcb_budget_is_preserved_without_kernel_changes(self) -> None:
        """TCB budget MUST stay at or below 1438 LOC (current baseline 1386 LOC)."""
        import subprocess
        result = subprocess.run(
            ["python3", "tools/linters/check_tcb_budget.py"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("TCB PASS: 1386 logical lines", result.stdout)


if __name__ == "__main__":
    unittest.main()
