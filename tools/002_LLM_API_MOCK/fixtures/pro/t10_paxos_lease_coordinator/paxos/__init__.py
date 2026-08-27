from typing import Dict, Optional

class LeaseCoordinator:
    def __init__(self, node_id: str, lease_duration: float = 5.0):
        self.node_id = node_id
        self.lease_duration = lease_duration
        self.current_leader: Optional[str] = None
        self.lease_expiry: float = 0.0

    def acquire_or_renew(self, node: str, current_time: float, quorum_votes: int, total_nodes: int) -> bool:
        if quorum_votes > total_nodes // 2:
            if current_time >= self.lease_expiry or self.current_leader == node:
                self.current_leader = node
                self.lease_expiry = current_time + self.lease_duration
                return True
        return False
