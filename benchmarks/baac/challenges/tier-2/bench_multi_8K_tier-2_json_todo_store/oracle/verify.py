#!/usr/bin/env python3
import sys, unittest, tempfile
from pathlib import Path
class TestTodo(unittest.TestCase):
    def test_todo(self):
        sys.path.insert(0, str(Path(sys.argv[-1] if len(sys.argv) > 1 and sys.argv[-2] == '--workspace' else '.').resolve() / 'src'))
        from todo import TodoStore
        with tempfile.NamedTemporaryFile(suffix='.json') as tmp:
            store = TodoStore(tmp.name)
            id1 = store.add('Buy milk', tags=['errand'])
            id2 = store.add('Write tests', tags=['work'])
            self.assertEqual(len(store.list_pending()), 2)
            store.complete(id1)
            self.assertEqual(len(store.list_pending()), 1)
if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestTodo)
    res = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if res.wasSuccessful() else 1)
