import unittest
from paxos import LeaseCoordinator

class TestPaxosLease(unittest.TestCase):
    def test_quorum_lease_acquisition_and_renewal(self):
        coord = LeaseCoordinator("n1", lease_duration=10.0)
        # 3 out of 5 nodes vote yes
        acquired = coord.acquire_or_renew(node="n1", current_time=100.0, quorum_votes=3, total_nodes=5)
        self.assertTrue(acquired)
        self.assertEqual(coord.current_leader, "n1")
        self.assertEqual(coord.lease_expiry, 110.0)

if __name__ == "__main__":
    unittest.main()
