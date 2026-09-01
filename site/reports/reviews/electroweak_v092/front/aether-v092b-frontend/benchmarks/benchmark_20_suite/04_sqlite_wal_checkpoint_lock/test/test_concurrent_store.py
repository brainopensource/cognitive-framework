import unittest
import tempfile
import threading
from pathlib import Path
from src.event_store import SqliteEventStore

class TestConcurrentEventStore(unittest.TestCase):
    def test_concurrent_append_and_checkpoint(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "events.db"
            store1 = SqliteEventStore(db_path)
            store2 = SqliteEventStore(db_path)

            errors = []

            def worker_write():
                try:
                    for i in range(50):
                        store2.append_event("run-1", "Step", {"i": i})
                except Exception as e:
                    errors.append(e)

            def worker_checkpoint():
                try:
                    for _ in range(10):
                        store1.checkpoint()
                except Exception as e:
                    errors.append(e)

            t1 = threading.Thread(target=worker_write)
            t2 = threading.Thread(target=worker_checkpoint)
            t1.start()
            t2.start()
            t1.join()
            t2.join()

            store1.close()
            store2.close()

            self.assertEqual(len(errors), 0, f"Concurrency failure occurred: {errors}")

if __name__ == "__main__":
    unittest.main()
