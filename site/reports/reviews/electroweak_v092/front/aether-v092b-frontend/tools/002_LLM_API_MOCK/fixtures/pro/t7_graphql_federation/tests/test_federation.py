import unittest
from federation import SchemaStitcher

class TestGraphQLFederation(unittest.TestCase):
    def test_federated_query_plan_resolution(self):
        stitcher = SchemaStitcher()
        stitcher.register_subgraph("users_subgraph", {"User": ["id", "username", "email"]})
        stitcher.register_subgraph("orders_subgraph", {"User": ["order_count", "total_spend"]})

        plan = stitcher.resolve_query("User", ["username", "order_count", "email"])
        self.assertEqual(plan.get("users_subgraph"), ["username", "email"])
        self.assertEqual(plan.get("orders_subgraph"), ["order_count"])

if __name__ == "__main__":
    unittest.main()
