from typing import List, Dict, Any, Tuple
from .wal import TxState, TxWAL
from .participant import Participant

class TransactionAbortedError(Exception):
    pass

class TwoPhaseCoordinator:
    def __init__(self, wal: TxWAL):
        self.wal = wal

    def execute_tx(self, tx_id: str, mutations: Dict[str, Tuple[str, Any]], participants: Dict[str, Participant]) -> bool:
        # BENCHMARK SKELETON: Stub implementation
        names = list(participants.keys())
        self.wal.log(tx_id, TxState.INIT, names)
        # Phase 1
        all_yes = True
        for part_name, (key, val) in mutations.items():
            if not participants[part_name].prepare(tx_id, key, val):
                all_yes = False
                break
        if not all_yes:
            self.wal.log(tx_id, TxState.ABORTED, names)
            for p in participants.values():
                p.abort(tx_id)
            raise TransactionAbortedError(f"tx {tx_id} aborted during prepare")

        # Phase 2
        self.wal.log(tx_id, TxState.COMMITTED, names)
        for p in participants.values():
            p.commit(tx_id)
        return True
