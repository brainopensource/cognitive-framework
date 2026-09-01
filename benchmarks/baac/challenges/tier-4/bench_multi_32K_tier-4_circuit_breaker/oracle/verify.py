#!/usr/bin/env python3
import sys, unittest
from pathlib import Path
class TestCircuit(unittest.TestCase):
    def test_circuit(self):
        sys.path.insert(0, str(Path(sys.argv[-1] if len(sys.argv) > 1 and sys.argv[-2] == '--workspace' else '.').resolve() / 'src'))
        from circuit import CircuitBreaker
        cb = CircuitBreaker(threshold=2)
        def fail(): raise ValueError('err')
        for _ in range(2):
            try: cb.call(fail)
            except ValueError: pass
        self.assertEqual(cb.state, 'OPEN')
if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestCircuit)
    res = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if res.wasSuccessful() else 1)
