import unittest
from typing import Tuple
from tx.wal import TxState, TxWAL
from tx.participant import Participant
from tx.coordinator import TwoPhaseCoordinator, TransactionAbortedError

class TestTwoPhaseCommit(unittest.TestCase):
    def test_successful_two_phase_commit(self):
        wal = TxWAL()
        coord = TwoPhaseCoordinator(wal)
        p1 = Participant("db1")
        p2 = Participant("db2")
        parts = {"db1": p1, "db2": p2}

        coord.execute_tx("tx-1", {"db1": ("user:1", "Alice"), "db2": ("account:1", 500)}, parts)
        self.assertEqual(p1.store.get("user:1"), "Alice")
        self.assertEqual(p2.store.get("account:1"), 500)
        self.assertEqual(wal.get_latest_state("tx-1"), TxState.COMMITTED)

    def test_single_participant_veto_triggers_global_abort(self):
        wal = TxWAL()
        coord = TwoPhaseCoordinator(wal)
        p1 = Participant("db1")
        p2 = Participant("db2")
        parts = {"db1": p1, "db2": p2}

        # Lock key in p2 with concurrent tx
        p2.prepare("tx-blocker", "account:2", 100)

        with self.assertRaises(TransactionAbortedError):
            coord.execute_tx("tx-2", {"db1": ("user:2", "Bob"), "db2": ("account:2", 900)}, parts)

        # db1 must be aborted clean without committed mutations
        self.assertNotIn("user:2", p1.store)
        self.assertEqual(wal.get_latest_state("tx-2"), TxState.ABORTED)

if __name__ == "__main__":
    unittest.main()
