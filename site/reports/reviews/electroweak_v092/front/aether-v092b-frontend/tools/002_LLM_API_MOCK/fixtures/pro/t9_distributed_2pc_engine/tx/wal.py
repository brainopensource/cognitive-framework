import enum
from typing import List
from dataclasses import dataclass

class TxState(enum.Enum):
    INIT = "INIT"
    PREPARED = "PREPARED"
    COMMITTED = "COMMITTED"
    ABORTED = "ABORTED"

@dataclass
class WalRecord:
    tx_id: str
    state: TxState
    participants: List[str]

class TxWAL:
    def __init__(self):
        self.records: List[WalRecord] = []

    def log(self, tx_id: str, state: TxState, participants: List[str]) -> None:
        self.records.append(WalRecord(tx_id=tx_id, state=state, participants=list(participants)))

    def get_latest_state(self, tx_id: str) -> TxState:
        for r in reversed(self.records):
            if r.tx_id == tx_id:
                return r.state
        return TxState.INIT
