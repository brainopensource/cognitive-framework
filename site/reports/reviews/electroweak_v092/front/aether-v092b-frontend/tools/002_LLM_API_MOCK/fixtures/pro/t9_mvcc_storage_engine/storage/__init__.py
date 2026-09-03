from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class Version:
    tx_id: int
    val: str
    deleted: bool = False

class MVCCStore:
    def __init__(self):
        self.records: Dict[str, List[Version]] = {}
        self.active_txs: Set[int] = set()

    def write(self, tx_id: int, key: str, val: str) -> None:
        self.records.setdefault(key, []).append(Version(tx_id=tx_id, val=val))

    def read(self, read_tx_id: int, key: str) -> Optional[str]:
        versions = self.records.get(key, [])
        for v in reversed(versions):
            if v.tx_id <= read_tx_id and not v.deleted:
                return v.val
        return None
