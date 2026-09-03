"""Integration test for RuntimeService stream reconnection and event deduplication.

Owning contract: W2-05, REQ-PORT-001, ADR-0062.
Proves that client disconnection and reconnection with after_seq receives remaining
events without dropped frames or duplicate delivery.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from vanguard.packages.domain.primitives.primitives import uuidv7
from vanguard.packages.runtime.service.inbox import ServiceInboxStore
from vanguard.packages.runtime.service.service import RuntimeService


class TestStreamReconnect(unittest.TestCase):
    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self._tempdir.name) / "test_inbox.db"
        self.store = ServiceInboxStore(self.db_path)
        self.service = RuntimeService(self.store)

    def tearDown(self) -> None:
        self.store.close()
        self._tempdir.cleanup()

    def test_reconnect_cursor_deduplication(self) -> None:
        run_id = "run-reconnect-001"
        self.store.record_command(
            command_id="cmd-start-1",
            idempotency_key="idemp-1",
            name="StartRun",
            run_id=run_id,
            payload={"run_id": run_id, "prompt": "test"},
        )

        # Record 5 events through the canonical writer. Seeding the inbox
        # outbox directly exercised the second event history WP-C1 removed;
        # streams now replay from the one durable store, which is what this
        # test's own contract ("no dropped frames or duplicate delivery")
        # is about.
        for i in range(1, 6):
            self.service.publish_event(
                run_id,
                {
                    "eventId": uuidv7(),
                    "runId": run_id,
                    "principal": "operator",
                    "payload": {"kind": "Log", "msg": f"Event {i}", "step": i},
                },
            )

        # First connection: reads all events
        all_frames = list(self.service.stream_events(run_id=run_id, after_seq=0))
        self.assertEqual(len(all_frames), 5)
        all_events = [f["event"] for f in all_frames]
        self.assertEqual([int(e.get("seq", 0)) for e in all_events], [1, 2, 3, 4, 5])

        # Disconnection & Reconnection with cursor after_seq=2
        resumed_frames = list(self.service.stream_events(run_id=run_id, after_seq=2))
        self.assertEqual(len(resumed_frames), 3)
        resumed_events = [f["event"] for f in resumed_frames]
        self.assertEqual([int(e.get("seq", 0)) for e in resumed_events], [3, 4, 5])

        # Append more events mid-run
        self.service.publish_event(
            run_id,
            {
                "eventId": uuidv7(),
                "runId": run_id,
                "principal": "operator",
                "payload": {"kind": "Outcome", "status": "completed"},
            },
        )

        # Incremental polling with after_seq=5
        final_frames = list(self.service.stream_events(run_id=run_id, after_seq=5))
        self.assertEqual(len(final_frames), 1)
        final_event = final_frames[0]["event"]
        self.assertEqual(int(final_event.get("seq", 0)), 6)
        self.assertEqual(final_event["payload"]["kind"], "Outcome")


if __name__ == "__main__":
    unittest.main()
