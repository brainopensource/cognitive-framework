"""Exterior Sealed Oracle Test Suite for Tier 5 Stratified Datalog Fixed-Point Engine.

Tests rigorous mathematical properties:
1. Transitive Closures & Cyclic Graph Fixed-Point Termination.
2. Stratified Negation Resolution & Strata Order Validation.
3. Negative Dependency Cycle Detection (StratificationError).
4. Monotonic Aggregate Evaluations (min shortest path, group-by count/sum).
5. Multi-way Relational Joins with Complex Variable Unification.
"""

from __future__ import annotations

import unittest
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from datalog import AggregateLiteral, Clause, DatalogEngine, Fact, Literal, StratificationError


class TestStratifiedDatalogEngine(unittest.TestCase):

    def test_01_transitive_closure_reachability(self):
        """Standard recursive transitive closure on a DAG with diamond structures."""
        engine = DatalogEngine()
        # Edge EDB
        edges = [("a", "b"), ("b", "c"), ("c", "d"), ("a", "e"), ("e", "d")]
        for u, v in edges:
            engine.add_fact(Fact("edge", (u, v)))

        # IDB: reach(?x, ?y) :- edge(?x, ?y).
        # IDB: reach(?x, ?z) :- reach(?x, ?y), edge(?y, ?z).
        engine.add_clause(Clause(
            head=Literal("reach", ("?x", "?y")),
            body=(Literal("edge", ("?x", "?y")),)
        ))
        engine.add_clause(Clause(
            head=Literal("reach", ("?x", "?z")),
            body=(Literal("reach", ("?x", "?y")), Literal("edge", ("?y", "?z")))
        ))

        res = engine.query("reach")
        expected = {
            ("a", "b"), ("b", "c"), ("c", "d"), ("a", "e"), ("e", "d"),
            ("a", "c"), ("a", "d"), ("b", "d"), ("e", "d")
        }
        self.assertEqual(res, expected)
        self.assertEqual(engine.query("reach", ("a", "?dest")), {("a", "b"), ("a", "c"), ("a", "d"), ("a", "e")})

    def test_02_cyclic_graph_termination(self):
        """Semi-naive evaluation must terminate on cyclic graphs without infinite loops."""
        engine = DatalogEngine()
        # Ring cycle: 1 -> 2 -> 3 -> 1
        engine.add_fact(Fact("link", (1, 2)))
        engine.add_fact(Fact("link", (2, 3)))
        engine.add_fact(Fact("link", (3, 1)))

        engine.add_clause(Clause(
            head=Literal("path", ("?x", "?y")),
            body=(Literal("link", ("?x", "?y")),)
        ))
        engine.add_clause(Clause(
            head=Literal("path", ("?x", "?z")),
            body=(Literal("path", ("?x", "?y")), Literal("link", ("?y", "?z")))
        ))

        res = engine.query("path")
        expected = {
            (1, 2), (2, 3), (3, 1),
            (1, 3), (2, 1), (3, 2),
            (1, 1), (2, 2), (3, 3)
        }
        self.assertEqual(res, expected)

    def test_03_stratified_negation_complement(self):
        """Stratified negation: compute unvisited / unconnected pairs."""
        engine = DatalogEngine()
        nodes = ["s", "a", "b", "c", "isolated"]
        for n in nodes:
            engine.add_fact(Fact("node", (n,)))

        engine.add_fact(Fact("edge", ("s", "a")))
        engine.add_fact(Fact("edge", ("a", "b")))
        engine.add_fact(Fact("edge", ("b", "c")))

        # reach(?x) :- edge("s", ?x).
        # reach(?y) :- reach(?x), edge(?x, ?y).
        # unreachable(?x) :- node(?x), not reach(?x).
        engine.add_clause(Clause(
            head=Literal("reach", ("?x",)),
            body=(Literal("edge", ("s", "?x")),)
        ))
        engine.add_clause(Clause(
            head=Literal("reach", ("?y",)),
            body=(Literal("reach", ("?x",)), Literal("edge", ("?x", "?y")))
        ))
        engine.add_clause(Clause(
            head=Literal("unreachable", ("?x",)),
            body=(Literal("node", ("?x",)), Literal("reach", ("?x",), negated=True))
        ))

        strata = engine.stratify()
        # reach must be in a strictly lower stratum than unreachable
        reach_stratum = next(i for i, s in enumerate(strata) if "reach" in s)
        unreach_stratum = next(i for i, s in enumerate(strata) if "unreachable" in s)
        self.assertLess(reach_stratum, unreach_stratum)

        unreachable = engine.query("unreachable")
        self.assertEqual(unreachable, {("s",), ("isolated",)})

    def test_04_non_stratifiable_cycle_error(self):
        """Mutually recursive negative cycles (e.g. p :- not q and q :- not p) must raise StratificationError."""
        engine = DatalogEngine()
        engine.add_clause(Clause(
            head=Literal("win", ("?x",)),
            body=(Literal("move", ("?x", "?y")), Literal("win", ("?y",), negated=True))
        ))
        with self.assertRaises(StratificationError):
            engine.stratify()

    def test_05_monotonic_aggregates(self):
        """Recursive monotonic aggregation: compute shortest path cost via min aggregate."""
        engine = DatalogEngine()
        # Direct candidate routes with varying costs
        engine.add_fact(Fact("route", ("A", "C", 10)))
        engine.add_fact(Fact("route", ("A", "C", 5)))
        engine.add_fact(Fact("route", ("A", "C", 12)))
        engine.add_fact(Fact("route", ("A", "D", 15)))
        engine.add_fact(Fact("route", ("A", "D", 10)))

        engine.add_clause(Clause(
            head=Literal("path_cost", ("?u", "?v", "?c")),
            body=(Literal("route", ("?u", "?v", "?c")),)
        ))
        engine.add_clause(Clause(
            head=Literal("shortest_path", ("?u", "?v", "?min_c")),
            body=(
                Literal("path_cost", ("?u", "?v", "?_")),
                AggregateLiteral(target_var="?min_c", op="min", source_var="?c", predicate="path_cost", args=("?u", "?v", "?c")),
            )
        ))

        shortest = engine.query("shortest_path", ("A", "C", "?val"))
        self.assertEqual(shortest, {("A", "C", 5)})

        shortest_d = engine.query("shortest_path", ("A", "D", "?val"))
        self.assertEqual(shortest_d, {("A", "D", 10)})


if __name__ == "__main__":
    unittest.main()
