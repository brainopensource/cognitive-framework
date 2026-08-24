"""RF-92 (ADR-0089): durable events are the sole source for replay and live fan-out."""

from __future__ import annotations

import queue
import unittest

from vanguard.packages.runtime.service.inbox import ServiceInboxStore
from vanguard.packages.runtime.service.service import ActiveRunContext, RuntimeService


class RF92DurableEventStreamFalsifier(unittest.TestCase):
    def test_publish_persists_before_fanout_with_one_sequence(self) -> None:
        service = RuntimeService(ServiceInboxStore(":memory:"))
        run_id = "rf92-run"
        subscriber: queue.Queue = queue.Queue()
        context = ActiveRunContext(run_id, "manifest", ".", "stream")
        context.event_subscribers.append(subscriber)
        with service._lock:
            service._active_runs[run_id] = context

        envelope = {"payload": {"kind": "TurnStarted", "runId": run_id}}
        seq = service.publish_event(run_id, envelope)
        live = subscriber.get_nowait()
        replay = service.store.get_events(run_id)

        self.assertEqual(live["seq"], str(seq))
        self.assertEqual(str(replay[0]["seq"]), live["seq"])
        self.assertEqual(live["payload"], replay[0]["payload"])


if __name__ == "__main__":
    unittest.main()
