"""M-5b OD-3 SAT/CNF deterministic witness and pack contracts."""

from __future__ import annotations

import importlib.util
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from vanguard.packages.adapters.evaluators.suites.formal_sat import (
    SatWitnessEvaluator,
    parse_dimacs,
    verify_assignment,
)
from vanguard.packages.ports.evaluator import EvaluationProtocol, RunRef

ROOT = Path(__file__).resolve().parents[3]
PACK = ROOT / "packs" / "formal-sat"


class FormalSatOracleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.formula = (PACK / "tasks" / "sat-001.cnf").read_text(encoding="utf-8")
        self.good = json.loads((PACK / "tasks" / "sat-001.witness.json").read_text())
        self.bad = json.loads((PACK / "tasks" / "sat-001.invalid-witness.json").read_text())

    def test_dimacs_and_complete_witness_are_deterministic(self) -> None:
        parsed = parse_dimacs(self.formula)
        self.assertEqual(parsed.variables, 2)
        self.assertEqual(len(parsed.clauses), 3)
        first = verify_assignment(self.formula, self.good)
        second = verify_assignment(self.formula, self.good)
        self.assertTrue(first.accepted)
        self.assertEqual(first, second)

    def test_wrong_and_partial_witnesses_are_rejected(self) -> None:
        wrong = verify_assignment(self.formula, self.bad)
        partial = verify_assignment(self.formula, {"assignment": {"1": True}})
        self.assertFalse(wrong.accepted)
        self.assertEqual(wrong.reason, "clause_not_satisfied")
        self.assertFalse(partial.accepted)
        self.assertEqual(partial.reason, "assignment_is_not_complete")

    def test_malformed_dimacs_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            parse_dimacs("p cnf 2 1\n3 0\n")

    def test_exterior_evaluator_passes_and_fails_candidates(self) -> None:
        evaluator = SatWitnessEvaluator(PACK)
        good = evaluator.evaluate(RunRef("run-good", "ep-good"), EvaluationProtocol(
            "formal-sat-v1",
            {"formula": "tasks/sat-001.cnf", "witness": "tasks/sat-001.witness.json"},
        ))
        bad = evaluator.evaluate(RunRef("run-bad", "ep-bad"), EvaluationProtocol(
            "formal-sat-v1",
            {"formula": "tasks/sat-001.cnf", "witness": "tasks/sat-001.invalid-witness.json"},
        ))
        self.assertEqual(good.value.claims[0]["status"], "passed")
        self.assertEqual(bad.value.claims[0]["status"], "failed")

    def test_exterior_evaluator_rejects_workspace_escape(self) -> None:
        result = SatWitnessEvaluator(PACK).evaluate(
            RunRef("run-escape", "ep-escape"),
            EvaluationProtocol("formal-sat-v1", {
                "formula": "../outside.cnf", "witness": "tasks/sat-001.witness.json",
            }),
        )
        self.assertEqual(result.value.outcome, "inconclusive")


class FormalSatPackTests(unittest.TestCase):
    def test_pack_compiles_without_substrate_special_cases(self) -> None:
        spec = importlib.util.spec_from_file_location("formal_sat_load", PACK / "load.py")
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        frozen = module.compile_pack()
        self.assertEqual(frozen.id, "formal-sat")
        self.assertIn("mhf.eval.formal-sat-exterior", frozen.resolved_refs.values())

    def test_task_registry_is_fixed_and_has_accept_reject_vectors(self) -> None:
        registry = json.loads((PACK / "tasks" / "registry.json").read_text())
        self.assertEqual(registry["status"], "fixed-not-run")
        self.assertEqual(registry["oracle"],
                         "vanguard.packages.adapters.evaluators.suites.formal_sat")
        oracle = ROOT / "vanguard/packages/adapters/evaluators/suites/formal_sat.py"
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
                "sha256:" + hashlib.sha256(
                    (PACK / task["positiveWitness"]).read_bytes()
                ).hexdigest(),
            )


if __name__ == "__main__":
    unittest.main()
