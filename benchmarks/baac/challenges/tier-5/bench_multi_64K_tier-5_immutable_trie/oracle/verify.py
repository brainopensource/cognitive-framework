#!/usr/bin/env python3
import sys, unittest
from pathlib import Path
class TestTrie(unittest.TestCase):
    def test_trie(self):
        sys.path.insert(0, str(Path(sys.argv[-1] if len(sys.argv) > 1 and sys.argv[-2] == '--workspace' else '.').resolve() / 'src'))
        from trie import TrieNode, insert
        r0 = TrieNode()
        r1 = insert(r0, 'cat')
        self.assertEqual(r0.children, {})
        self.assertIn('c', r1.children)
if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestTrie)
    res = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if res.wasSuccessful() else 1)
