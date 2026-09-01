from typing import Dict, Set, List, Optional

class WaitForGraph:
    def __init__(self):
        self.adj: Dict[str, Set[str]] = {}

    def add_wait(self, tx_a: str, tx_b: str) -> None:
        # tx_a is waiting for tx_b
        self.adj.setdefault(tx_a, set()).add(tx_b)

    def remove_wait(self, tx_a: str, tx_b: str) -> None:
        if tx_a in self.adj and tx_b in self.adj[tx_a]:
            self.adj[tx_a].remove(tx_b)

    def detect_deadlock(self) -> List[str]:
        # Detect cycles using DFS
        visited = set()
        rec_stack = []

        def dfs(node: str) -> Optional[List[str]]:
            visited.add(node)
            rec_stack.append(node)
            for neighbor in self.adj.get(node, []):
                if neighbor not in visited:
                    res = dfs(neighbor)
                    if res: return res
                elif neighbor in rec_stack:
                    idx = rec_stack.index(neighbor)
                    return rec_stack[idx:] + [neighbor]
            rec_stack.pop()
            return None

        for n in list(self.adj.keys()):
            if n not in visited:
                cycle = dfs(n)
                if cycle: return cycle
        return []
