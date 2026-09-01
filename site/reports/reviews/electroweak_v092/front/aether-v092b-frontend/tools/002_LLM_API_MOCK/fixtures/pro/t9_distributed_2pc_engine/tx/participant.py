from typing import Dict, Any, Optional

class LockConflictError(Exception):
    pass

class Participant:
    def __init__(self, name: str):
        self.name = name
        self.store: Dict[str, Any] = {}
        self.pending_locks: Dict[str, str] = {} # key -> tx_id
        self.prepared_mutations: Dict[str, Dict[str, Any]] = {} # tx_id -> {key: value}

    def prepare(self, tx_id: str, key: str, value: Any) -> bool:
        if key in self.pending_locks and self.pending_locks[key] != tx_id:
            return False
        self.pending_locks[key] = tx_id
        self.prepared_mutations[tx_id] = {key: value}
        return True

    def commit(self, tx_id: str) -> None:
        if tx_id in self.prepared_mutations:
            for k, v in self.prepared_mutations[tx_id].items():
                self.store[k] = v
                if k in self.pending_locks:
                    del self.pending_locks[k]
            del self.prepared_mutations[tx_id]

    def abort(self, tx_id: str) -> None:
        if tx_id in self.prepared_mutations:
            for k in self.prepared_mutations[tx_id].keys():
                if k in self.pending_locks and self.pending_locks[k] == tx_id:
                    del self.pending_locks[k]
            del self.prepared_mutations[tx_id]
