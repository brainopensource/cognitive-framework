import unittest
from src.packer import SubmodularPacker, PackItem

class TestSubmodularPacker(unittest.TestCase):
    def test_greedy_coverage_under_budget(self):
        items = [
            PackItem("item1", cost=10, features={"python", "ast", "indexer"}),
            PackItem("item2", cost=10, features={"python", "ast"}),  # redundant
            PackItem("item3", cost=10, features={"sqlite", "fts5"}),
            PackItem("item4", cost=30, features={"python", "ast", "sqlite", "fts5", "kernel"})
        ]

        # Budget 20: Should pick item1 and item3 (5 unique features for cost 20)
        selected = SubmodularPacker.pack(items, budget=20)
        ids = {i.id for i in selected}
        total_cost = sum(i.cost for i in selected)

        self.assertLessEqual(total_cost, 20)
        self.assertIn("item1", ids)
        self.assertIn("item3", ids)
        self.assertNotIn("item2", ids)

if __name__ == "__main__":
    unittest.main()
