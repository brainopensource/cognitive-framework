#!/usr/bin/env python3
import sys, unittest
from pathlib import Path
class TestCalc(unittest.TestCase):
    def test_calc(self):
        sys.path.insert(0, str(Path(sys.argv[-1] if len(sys.argv) > 1 and sys.argv[-2] == '--workspace' else '.').resolve() / 'src'))
        from calculator import calculate_value
        self.assertEqual(calculate_value(2, 3), 15)
        self.assertEqual(calculate_value(0, 4), 16)
        self.assertEqual(calculate_value(1, 1), 2)
if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestCalc)
    res = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if res.wasSuccessful() else 1)
