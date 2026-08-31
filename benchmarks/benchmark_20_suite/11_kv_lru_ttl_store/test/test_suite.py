import unittest
import time
from src.store import LRUTTLStore

class TestLRUTTLStore(unittest.TestCase):
    def test_lru_eviction(self):
        store = LRUTTLStore(capacity=2)
        store.put("a", 1)
        store.put("b", 2)
        self.assertEqual(store.get("a"), 1)
        store.put("c", 3)  # Evicts "b"
        self.assertIsNone(store.get("b"))
        self.assertEqual(store.get("a"), 1)
        self.assertEqual(store.get("c"), 3)

    def test_ttl_expiration(self):
        store = LRUTTLStore(capacity=5, default_ttl=0.1)
        store.put("temp", "val")
        self.assertEqual(store.get("temp"), "val")
        time.sleep(0.15)
        self.assertIsNone(store.get("temp"))

    def test_delete_and_size(self):
        store = LRUTTLStore(capacity=3)
        store.put("x", 10)
        store.put("y", 20)
        self.assertEqual(store.size(), 2)
        self.assertTrue(store.delete("x"))
        self.assertFalse(store.delete("nonexistent"))
        self.assertEqual(store.size(), 1)

if __name__ == "__main__":
    unittest.main()
