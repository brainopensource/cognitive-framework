import unittest
from deadlock import WaitForGraph

class TestDeadlock(unittest.TestCase):
    def test_cycle_detection(self):
        wfg = WaitForGraph()
        wfg.add_wait("T1", "T2")
        wfg.add_wait("T2", "T3")
        wfg.add_wait("T3", "T1")
        cycle = wfg.detect_deadlock()
        self.assertTrue(len(cycle) >= 3)
        self.assertEqual(cycle[0], cycle[-1])

if __name__ == "__main__":
    unittest.main()
