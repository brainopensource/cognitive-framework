import hashlib
import bisect
from typing import Dict, List, Optional

class ConsistentHashRing:
    def __init__(self, replicas: int = 3):
        self.replicas = replicas
        self.ring: List[int] = []
        self.node_map: Dict[int, str] = {}

    def _hash(self, key: str) -> int:
        return int(hashlib.md5(key.encode("utf-8")).hexdigest(), 16)

    def add_node(self, node: str) -> None:
        for r in range(self.replicas):
            v_key = f"{node}#replica-{r}"
            h = self._hash(v_key)
            bisect.insort(self.ring, h)
            self.node_map[h] = node

    def get_node(self, key: str) -> Optional[str]:
        if not self.ring:
            return None
        h = self._hash(key)
        idx = bisect.bisect_right(self.ring, h)
        if idx == len(self.ring):
            idx = 0
        return self.node_map[self.ring[idx]]
