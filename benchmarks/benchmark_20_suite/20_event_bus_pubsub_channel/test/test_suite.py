import unittest
from src.event_bus import EventBus, DeadLetterItem

class TestEventBus(unittest.TestCase):
    def test_wildcard_dispatch_and_dlq(self):
        bus = EventBus()
        received = []

        bus.subscribe("telemetry.*", lambda topic, data: received.append((topic, data)))

        def failing_handler(topic, data):
            raise RuntimeError("handler failed")

        bus.subscribe("telemetry.errors", failing_handler)

        success_count = bus.publish("telemetry.cpu", {"usage": 80})
        self.assertEqual(success_count, 1)
        self.assertEqual(len(received), 1)

        # Publish to error topic (1 succeeds, 1 fails into DLQ)
        bus.publish("telemetry.errors", {"error": "OOM"})
        dlq = bus.get_dlq()
        self.assertEqual(len(dlq), 1)
        self.assertEqual(dlq[0].topic, "telemetry.errors")

if __name__ == "__main__":
    unittest.main()
