# Problem Specification: Incremental Stratified Datalog Fixed-Point Engine

## Overview
Implement an in-memory incremental Datalog evaluation engine supporting:
1. **Extensional Database (EDB)**: Ingestion of ground facts `P(c_1, ..., c_k)`.
2. **Intensional Database (IDB)**: Recursive Horn clauses `Head :- Body_1, ..., Body_n`.
3. **Semi-Naive Bottom-Up Evaluation**: Computing minimal fixed-points via differential relations ($\Delta R$) without duplicate derivation loops.
4. **Stratified Negation**: Resolving negation-as-failure `not P(...)` with dependency graph stratification (topological stratum ordering) and detecting non-stratifiable negative cycles.
5. **Recursive Monotonic Aggregates**: Fixed-point computation over monotonic aggregations (`min`, `max`, `sum`, `count`) with stratification constraints.

## Interface Contract

```python
from dataclasses import dataclass
from typing import Sequence, Any, Optional

@dataclass(frozen=True)
class Fact:
    predicate: str
    args: tuple[Any, ...]

@dataclass(frozen=True)
class Literal:
    predicate: str
    args: tuple[Any, ...]
    negated: bool = False

@dataclass(frozen=True)
class AggregateLiteral:
    target_var: str
    op: str  # "min", "max", "sum", "count"
    source_var: str
    predicate: str
    args: tuple[Any, ...]

@dataclass(frozen=True)
class Clause:
    head: Literal
    body: tuple[Literal | AggregateLiteral, ...]

class StratificationError(Exception):
    """Raised when the program contains non-stratifiable negative or aggregate recursion."""
    pass

class DatalogEngine:
    def __init__(self) -> None:
        pass

    def add_fact(self, fact: Fact) -> None:
        """Add an extensional fact."""
        pass

    def add_clause(self, clause: Clause) -> None:
        """Add a deductive rule."""
        pass

    def stratify(self) -> list[set[str]]:
        """
        Compute dependency graph strata for all IDB and EDB predicates.
        Returns ordered list of strata sets [Stratum_0, Stratum_1, ...].
        Raises StratificationError on negative/aggregate cycles.
        """
        pass

    def query(self, predicate: str, pattern: Optional[tuple[Any, ...]] = None) -> set[tuple[Any, ...]]:
        """
        Evaluate the engine and query all derived tuples matching the predicate and pattern.
        Pattern variables are represented by strings starting with '?' (e.g. '?x').
        Constants are matched exactly.
        """
        pass
```

## Constraints
- **Safety**: Every variable appearing in the head or in a negated literal / aggregate must appear in at least one positive relational body literal.
- **Stratification**: If predicate $P$ depends negatively or via aggregate on $Q$, $stratum(Q) < stratum(P)$. If positively, $stratum(Q) \le stratum(P)$.
- **Fixed-point Termination**: Semi-naive evaluation must terminate deterministically and compute the unique minimal perfect model.
