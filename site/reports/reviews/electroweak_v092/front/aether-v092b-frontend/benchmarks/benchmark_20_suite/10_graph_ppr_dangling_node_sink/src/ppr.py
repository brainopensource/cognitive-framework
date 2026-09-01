from typing import Dict, List, Set

class PersonalizedPageRank:
    @staticmethod
    def compute(adjacency: Dict[str, List[str]], seed_node: str, alpha: float = 0.85, max_iter: int = 50) -> Dict[str, float]:
        nodes = list(adjacency.keys())
        n = len(nodes)
        if n == 0:
            return {}

        p = {node: 1.0 / n for node in nodes}
        teleport = {node: (1.0 if node == seed_node else 0.0) for node in nodes}

        for _ in range(max_iter):
            next_p = {node: (1.0 - alpha) * teleport[node] for node in nodes}
            for u, neighbors in adjacency.items():
                if neighbors:
                    out_weight = alpha * (p[u] / len(neighbors))
                    for v in neighbors:
                        if v in next_p:
                            next_p[v] += out_weight
                # BUG: Dangling nodes (neighbors == []) absorb probability mass!
                # Their mass alpha * p[u] is not redistributed to the teleport distribution.
            p = next_p

        return p
