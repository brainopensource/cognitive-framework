import unittest
from src.ppr import PersonalizedPageRank

class TestPPR(unittest.TestCase):
    def test_ppr_conserves_probability_with_dangling_nodes(self):
        # Node 'C' has no outgoing edges (dangling sink)
        adj = {
            "A": ["B", "C"],
            "B": ["A"],
            "C": []
        }
        scores = PersonalizedPageRank.compute(adj, seed_node="A", alpha=0.85, max_iter=30)
        total_mass = sum(scores.values())

        # Falsifier Assertion: Total probability mass MUST sum to 1.0 (+- 0.001)
        self.assertAlmostEqual(
            total_mass,
            1.0,
            places=3,
            msg=f"Probability mass lost: sum is {total_mass}, expected 1.0"
        )

if __name__ == "__main__":
    unittest.main()
