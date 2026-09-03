#!/usr/bin/env python3
import sys, unittest
from pathlib import Path
class TestMVCC(unittest.TestCase):
    def test_mvcc(self):
        sys.path.insert(0, str(Path(sys.argv[-1] if len(sys.argv) > 1 and sys.argv[-2] == '--workspace' else '.').resolve() / 'src'))
        from mvcc import MVCCStore
        db = MVCCStore()
        db.put('k1', 'v1', tx_id=10)
        db.put('k1', 'v2', tx_id=20)
        self.assertEqual(db.get('k1', tx_id=15), 'v1')
        self.assertEqual(db.get('k1', tx_id=25), 'v2')
if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestMVCC)
    res = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if res.wasSuccessful() else 1)
