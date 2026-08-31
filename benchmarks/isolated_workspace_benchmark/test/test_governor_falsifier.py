# test_governor_falsifier.py - Rigorous Falsifier Suite
import unittest
import time
from .rate_governor import RateGovernor

class TestRateGovernorLeaseRecovery(unittest.TestCase):
    def test_expired_lease_restores_tokens_in_pool(self):
        gov = RateGovernor(capacity=100)
        
        # Step 1: Reserve 40 tokens
        self.assertTrue(gov.reserve("lease-alpha", 40, ttl_seconds=2.0))
        self.assertEqual(gov.available_tokens, 60)
        
        # Step 2: Simulate lease expiry
        future_time = time.time() + 10.0
        cleaned_count = gov.clean_expired(current_time=future_time)
        self.assertEqual(cleaned_count, 1)
        
        # Falsifier Assertion: All 100 tokens must be restored!
        self.assertEqual(
            gov.available_tokens,
            100,
            f"FALSIFIER FAILED: Expected 100 available tokens, found {gov.available_tokens}. Token leakage occurred!"
        )

if __name__ == "__main__":
    unittest.main()
