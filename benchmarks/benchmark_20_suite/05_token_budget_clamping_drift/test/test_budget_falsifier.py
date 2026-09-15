import unittest
from src.budget import BudgetGovernor

class TestBudgetGovernorDrift(unittest.TestCase):
    def test_repeated_micro_transactions_zero_drift(self):
        gov = BudgetGovernor(initial_usd=1.0)
        micro_amount = 0.0001  # 100 micro-USD

        for _ in range(10000):
            self.assertTrue(gov.reserve(micro_amount))

        # Falsifier Assertion: After 10,000 reserves of 0.0001 from 1.0, balance must be EXACTLY 0.0
        self.assertEqual(
            gov.remaining_balance(),
            0.0,
            f"Float drift detected: expected 0.0, got {gov.remaining_balance()}"
        )

if __name__ == "__main__":
    unittest.main()
