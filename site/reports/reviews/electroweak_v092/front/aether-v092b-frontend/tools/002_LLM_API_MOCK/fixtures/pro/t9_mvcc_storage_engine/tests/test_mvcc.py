import unittest
from storage import MVCCStore

class TestMVCC(unittest.TestCase):
    def test_snapshot_isolation_read(self):
        store = MVCCStore()
        store.write(tx_id=1, key="k1", val="v1")
        store.write(tx_id=3, key="k1", val="v3")

        # Tx 2 reading key should only see v1
        self.assertEqual(store.read(read_tx_id=2, key="k1"), "v1")
        # Tx 4 reading key should see v3
        self.assertEqual(store.read(read_tx_id=4, key="k1"), "v3")

if __name__ == "__main__":
    unittest.main()
