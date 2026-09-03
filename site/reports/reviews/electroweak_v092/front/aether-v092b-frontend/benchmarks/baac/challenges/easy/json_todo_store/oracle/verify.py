#!/usr/bin/env python3
"""External Oracle for json_todo_store challenge.

NEVER leaked to the agent.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile
import unittest


class TestTodoStoreOracle(unittest.TestCase):
    ws_path: Path

    def setUp(self) -> None:
        sys.path.insert(0, str(self.ws_path))
        sys.path.insert(0, str(self.ws_path / "src"))

    def test_lifecycle_and_persistence(self) -> None:
        from todo import TodoStore  # type: ignore

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            fpath = Path(tf.name)

        try:
            # 1. Instance 1: Add items
            store = TodoStore(fpath)
            id1 = store.add("Buy groceries", tags=["home", "errands"])
            id2 = store.add("Write unit tests", tags=["work"])
            id3 = store.add("Review pull request", tags=["work"])

            self.assertEqual(id1, 1)
            self.assertEqual(id2, 2)
            self.assertEqual(id3, 3)

            # Check invalid title
            with self.assertRaises(ValueError):
                store.add("   ")

            # Check get
            item1 = store.get(1)
            self.assertIsNotNone(item1)
            self.assertEqual(item1["title"], "Buy groceries")
            self.assertFalse(item1["completed"])
            self.assertEqual(item1["tags"], ["home", "errands"])

            # Check complete
            ok = store.complete(2)
            self.assertTrue(ok)
            self.assertFalse(store.complete(999))

            # Check list_pending
            pending = store.list_pending()
            self.assertEqual(len(pending), 2)
            self.assertEqual([p["id"] for p in pending], [1, 3])

            # Check list_by_tag
            work_items = store.list_by_tag("work")
            self.assertEqual(len(work_items), 2)

            # 2. Instance 2: Reload from disk and verify persistence
            store2 = TodoStore(fpath)
            item2 = store2.get(2)
            self.assertIsNotNone(item2)
            self.assertTrue(item2["completed"])

            id4 = store2.add("Deploy release", tags=["work"])
            self.assertEqual(id4, 4)

        finally:
            if fpath.exists():
                fpath.unlink()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".", help="Target workspace path")
    args = parser.parse_args()

    ws = Path(args.workspace).resolve()
    TestTodoStoreOracle.ws_path = ws

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestTodoStoreOracle)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
