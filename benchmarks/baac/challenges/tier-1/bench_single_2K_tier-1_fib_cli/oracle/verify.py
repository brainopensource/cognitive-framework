#!/usr/bin/env python3
import sys, unittest
from pathlib import Path
class TestFib(unittest.TestCase):
    def test_fib(self):
        sys.path.insert(0, str(Path(sys.argv[-1] if len(sys.argv) > 1 and sys.argv[-2] == '--workspace' else '.').resolve() / 'src'))
        from fib import fib
        self.assertEqual(fib(0), 0)
        self.assertEqual(fib(1), 1)
        self.assertEqual(fib(10), 55)
        with self.assertRaises(ValueError):
            fib(-1)
if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestFib)
    res = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if res.wasSuccessful() else 1)
