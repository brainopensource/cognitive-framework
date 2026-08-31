# Greenfield PRD: Submodular Greedy Knapsack Packer

## Objective
Implement `SubmodularPacker` and `PackItem` in `src/packer.py`.

## Requirements
- `PackItem(id: str, cost: int, features: set[str])`
- `SubmodularPacker.pack(items: list[PackItem], budget: int) -> list[PackItem]`
- The utility function is the total count of unique features covered: $f(S) = |\bigcup_{i \in S} i.features|$.
- Algorithm: Greedy marginal gain $\Delta(e \mid S) = f(S \cup \{e\}) - f(S)$. At each step, select item maximizing $\Delta(e \mid S) / cost(e)$ that fits in the remaining budget.
- Total cost of returned items MUST not exceed `budget`.
