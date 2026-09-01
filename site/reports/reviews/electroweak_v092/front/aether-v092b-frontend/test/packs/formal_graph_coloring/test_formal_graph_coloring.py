"""M-5b OD-3 Graph Coloring deterministic witness and pack contracts."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

from vanguard.packages.adapters.evaluators.suites.formal_graph_coloring import (
    GraphColoringEvaluator,
    parse_graph,
    parse_witness,
    verify_coloring,
)
from vanguard.packages.ports.evaluator import EvaluationProtocol, RunRef

ROOT = Path(__file__).resolve().parents[3]
PACK = ROOT / "packs" / "formal-graph-coloring"


class FormalGraphColoringOracleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.graph = (PACK / "tasks" / "gc-001.graph.json").read_text(encoding="utf-8")
        self.good = json.loads((PACK / "tasks" / "gc-001.witness.json").read_text())
        self.bad_edge = json.loads(
            (PACK / "tasks" / "gc-001.invalid-edge-conflict.json").read_text()
        )
        self.bad_incomplete = json.loads(
            (PACK / "tasks" / "gc-001.invalid-incomplete.json").read_text()
        )
        self.bad_range = json.loads(
            (PACK / "tasks" / "gc-001.invalid-range.json").read_text()
        )

    def test_canonical_graph_and_complete_witness_are_deterministic(self) -> None:
        parsed = parse_graph(self.graph)
        self.assertEqual(parsed.k, 3)
        self.assertEqual(len(parsed.vertices), 10)
        self.assertEqual(len(parsed.edges), 15)

        first = verify_coloring(self.graph, self.good)
        second = verify_coloring(self.graph, self.good)
        self.assertTrue(first.accepted)
        self.assertEqual(first, second)

    def test_invalid_negative_vectors_are_rejected(self) -> None:
        edge_fail = verify_coloring(self.graph, self.bad_edge)
        self.assertFalse(edge_fail.accepted)
        self.assertEqual(edge_fail.reason, "edge_not_satisfied")
        self.assertEqual(edge_fail.failed_edge, (0, 1))

        incomplete_fail = verify_coloring(self.graph, self.bad_incomplete)
        self.assertFalse(incomplete_fail.accepted)
        self.assertEqual(incomplete_fail.reason, "assignment_is_not_complete")
        self.assertEqual(incomplete_fail.failed_vertex, 9)

        range_fail = verify_coloring(self.graph, self.bad_range)
        self.assertFalse(range_fail.accepted)
        self.assertEqual(range_fail.reason, "color_out_of_range")
        self.assertEqual(range_fail.failed_vertex, 9)

    def test_malformed_graph_fails_closed(self) -> None:
        disordered = (PACK / "tasks" / "gc-001.invalid-disordered-graph.json").read_text()
        with self.assertRaises(ValueError):
            parse_graph(disordered)

    def test_exterior_evaluator_passes_and_fails_candidates(self) -> None:
        evaluator = GraphColoringEvaluator(PACK)
        good = evaluator.evaluate(
            RunRef("run-good", "ep-good"),
            EvaluationProtocol(
                "formal-graph-coloring-v1",
                {"graph": "tasks/gc-001.graph.json", "witness": "tasks/gc-001.witness.json"},
            ),
        )
        bad = evaluator.evaluate(
            RunRef("run-bad", "ep-bad"),
            EvaluationProtocol(
                "formal-graph-coloring-v1",
                {
                    "graph": "tasks/gc-001.graph.json",
                    "witness": "tasks/gc-001.invalid-edge-conflict.json",
                },
            ),
        )
        self.assertEqual(good.value.claims[0]["status"], "passed")
        self.assertEqual(bad.value.claims[0]["status"], "failed")

    def test_exterior_evaluator_rejects_workspace_escape(self) -> None:
        result = GraphColoringEvaluator(PACK).evaluate(
            RunRef("run-escape", "ep-escape"),
            EvaluationProtocol(
                "formal-graph-coloring-v1",
                {
                    "graph": "../outside.graph.json",
                    "witness": "tasks/gc-001.witness.json",
                },
            ),
        )
        self.assertEqual(result.value.outcome, "inconclusive")


class FormalGraphColoringPackTests(unittest.TestCase):
    def test_pack_compiles_without_substrate_special_cases(self) -> None:
        spec = importlib.util.spec_from_file_location(
            "formal_gc_load", PACK / "load.py"
        )
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        frozen = module.compile_pack()
        self.assertEqual(frozen.id, "formal-graph-coloring")
        self.assertIn("mhf.eval.formal-graph-coloring-exterior", frozen.resolved_refs.values())

    def test_task_registry_is_fixed_and_has_accept_reject_vectors(self) -> None:
        registry = json.loads((PACK / "tasks" / "registry.json").read_text())
        self.assertEqual(registry["status"], "fixed-not-run")
        self.assertEqual(
            registry["oracle"],
            "vanguard.packages.adapters.evaluators.suites.formal_graph_coloring",
        )
        oracle = (
            ROOT / "vanguard/packages/adapters/evaluators/suites/formal_graph_coloring.py"
        )
        self.assertEqual(
            registry["oracleDigest"],
            "sha256:" + hashlib.sha256(oracle.read_bytes()).hexdigest(),
        )
        for task in registry["tasks"]:
            self.assertTrue((PACK / task["formula"]).is_file())
            self.assertTrue((PACK / task["positiveWitness"]).is_file())
            self.assertTrue((PACK / task["negativeVector"]).is_file())
            self.assertEqual(
                task["formulaDigest"],
                "sha256:" + hashlib.sha256((PACK / task["formula"]).read_bytes()).hexdigest(),
            )
            self.assertEqual(
                task["positiveWitnessDigest"],
                "sha256:"
                + hashlib.sha256(
                    (PACK / task["positiveWitness"]).read_bytes()
                ).hexdigest(),
            )


if __name__ == "__main__":
    unittest.main()
