"""Incremental Stratified Datalog Evaluation Engine.

Skeleton implementation containing intentional flaws:
- Incomplete stratification algorithm failing on negative recursion
- Naive evaluation that loops infinitely on cyclic rules
- Incorrect variable unification across mixed relational and aggregate joins
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Optional, Sequence, Set, Tuple


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
        self.edb: dict[str, set[tuple[Any, ...]]] = {}
        self.idb: list[Clause] = []

    def add_fact(self, fact: Fact) -> None:
        if fact.predicate not in self.edb:
            self.edb[fact.predicate] = set()
        self.edb[fact.predicate].add(fact.args)

    def add_clause(self, clause: Clause) -> None:
        self.idb.append(clause)

    def stratify(self) -> list[set[str]]:
        # Bug: Does not compute topological strata or detect negative cycles
        all_preds = set(self.edb.keys()) | {c.head.predicate for c in self.idb}
        return [all_preds]

    def query(self, predicate: str, pattern: Optional[tuple[Any, ...]] = None) -> set[tuple[Any, ...]]:
        # Bug: Incomplete naive evaluation that cannot handle negation or aggregates
        tables: dict[str, set[tuple[Any, ...]]] = {k: set(v) for k, v in self.edb.items()}
        for c in self.idb:
            if c.head.predicate not in tables:
                tables[c.head.predicate] = set()

        changed = True
        iterations = 0
        while changed and iterations < 10:
            changed = False
            iterations += 1
            for clause in self.idb:
                # Basic positive match only
                head_pred = clause.head.predicate
                initial_count = len(tables[head_pred])
                # Mock naive join
                if len(clause.body) == 1 and isinstance(clause.body[0], Literal) and not clause.body[0].negated:
                    body_pred = clause.body[0].predicate
                    for row in tables.get(body_pred, set()):
                        tables[head_pred].add(row)
                if len(tables[head_pred]) > initial_count:
                    changed = True

        results = tables.get(predicate, set())
        if pattern is None:
            return results

        filtered = set()
        for row in results:
            if len(row) != len(pattern):
                continue
            match = True
            for r_val, p_val in zip(row, pattern):
                if isinstance(p_val, str) and p_val.startswith("?"):
                    continue
                if r_val != p_val:
                    match = False
                    break
            if match:
                filtered.add(row)
        return filtered
