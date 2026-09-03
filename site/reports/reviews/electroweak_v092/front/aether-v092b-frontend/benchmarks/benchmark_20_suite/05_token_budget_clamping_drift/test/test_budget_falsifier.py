import unittest
from src.budget import BudgetGovernor

class TestBudgetGovernorDrift(unittest.TestCase):
    def test_repeated_micro_transactions_zero_drift(self):
        gov = BudgetGovernor(initial_usd=1.0)
        micro_amount = 0.00001  # 10 micro-USD

        for _ in range(1000):
            self.assertTrue(gov.reserve(micro_amount))
            gov.refund(micro_amount)

        # Falsifier Assertion: After 1000 equal reserves and refunds, balance must be EXACTLY initial
        self.assertEqual(
            gov.remaining_balance(),
            1.0,
            f"Float drift detected: expected 1.0, got {gov.remaining_balance()}"
        )

if __name__ == "__main__":
    unittest.main()
