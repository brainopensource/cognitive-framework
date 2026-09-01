#!/usr/bin/env python3
import sys, unittest
from pathlib import Path
class TestEventBus(unittest.TestCase):
    def test_bus(self):
        sys.path.insert(0, str(Path(sys.argv[-1] if len(sys.argv) > 1 and sys.argv[-2] == '--workspace' else '.').resolve() / 'src'))
        from event_bus import EventBus
        bus = EventBus()
        received = []
        sub_id = bus.subscribe('user.created', lambda p: received.append(p))
        bus.publish('user.created', {'user_id': 42})
        self.assertEqual(len(received), 1)
if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestEventBus)
    res = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if res.wasSuccessful() else 1)
