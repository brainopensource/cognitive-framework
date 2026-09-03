#!/usr/bin/env python3
import sys, unittest
from pathlib import Path
class TestDedupe(unittest.TestCase):
    def test_dedupe(self):
        sys.path.insert(0, str(Path(sys.argv[-1] if len(sys.argv) > 1 and sys.argv[-2] == '--workspace' else '.').resolve() / 'src'))
        from dedupe import remove_consecutive_duplicates
        self.assertEqual(remove_consecutive_duplicates('aaabbcddd'), 'abcd')
        self.assertEqual(remove_consecutive_duplicates('hello'), 'helo')
        self.assertEqual(remove_consecutive_duplicates(''), '')
if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestDedupe)
    res = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if res.wasSuccessful() else 1)
