import unittest
import time
from src.token_bucket import HierarchicalTokenBucket

class TestHierarchicalTokenBucket(unittest.TestCase):
    def test_parent_child_atomicity(self):
        parent = HierarchicalTokenBucket(capacity=10.0, refill_rate=5.0)
        child1 = HierarchicalTokenBucket(capacity=10.0, refill_rate=5.0, parent=parent)
        child2 = HierarchicalTokenBucket(capacity=10.0, refill_rate=5.0, parent=parent)

        # Child1 acquires 8 tokens (parent now has 2)
        self.assertTrue(child1.acquire(8.0))

        # Child2 wants 5 tokens. Child2 has 10, but parent only has 2 -> must fail
        self.assertFalse(child2.acquire(5.0))

        # Wait for refill (0.8s * 5 tokens/s = 4 tokens)
        time.sleep(0.8)
        self.assertTrue(child2.acquire(5.0))

if __name__ == "__main__":
    unittest.main()
