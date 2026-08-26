import unittest
from cluster import ConsistentHashRing

class TestConsistentHash(unittest.TestCase):
    def test_key_distribution_and_stability(self):
        ring = ConsistentHashRing(replicas=5)
        ring.add_node("node-1")
        ring.add_node("node-2")
        ring.add_node("node-3")

        node_a = ring.get_node("user:1001")
        node_b = ring.get_node("user:1001")
        self.assertEqual(node_a, node_b)
        self.assertIn(node_a, ["node-1", "node-2", "node-3"])

if __name__ == "__main__":
    unittest.main()
