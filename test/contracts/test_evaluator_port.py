"""Shared substitution contract for EvaluatorPort.

Owning contract: REQ-PORT-004 / TEST-PORT-004, ICD §4, ADR-0048.
"""

from __future__ import annotations

import ast
import unittest
from pathlib import Path

from vanguard.packages.adapters.evaluators import FakeEvaluator
from vanguard.packages.ports.evaluator import (
    EvaluationProtocol,
    EvaluatorPort,
    RunRef,
    Verdict,
)


def _fake() -> EvaluatorPort:
    return FakeEvaluator(
        verdicts={
            "run-ok": Verdict(
                outcome="claims",
                claims=({"kind": "pass", "statement": "fixture"},),
            )
        },
        instrument_errors=("run-broken",),
    )


def _spec_names(node: ast.AST) -> list[str]:
    names: list[str] = []
    if isinstance(node, ast.Import):
        names.extend(alias.name for alias in node.names)
    elif isinstance(node, ast.ImportFrom):
        if node.module:
            names.append(node.module)
        names.extend(alias.name for alias in node.names)
    return names


def _agency_evaluator_imports() -> list[str]:
    root = Path("vanguard/packages/agency")
    if not root.exists():
        return []
    offenders: list[str] = []
    for path in root.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            for spec in _spec_names(node):
                if "evaluator" in spec.lower().replace("_", "-"):
                    offenders.append(f"{path.as_posix()}:{node.lineno}: {spec}")
    return offenders


class EvaluatorPortContract(unittest.TestCase):
    def test_fake_returns_fixed_claims(self) -> None:
        result = _fake().evaluate(RunRef(run_id="run-ok"), EvaluationProtocol(name="fixture"))
        self.assertTrue(result.ok)
        self.assertIsNotNone(result.value)
        self.assertEqual(result.value.outcome, "claims")
        self.assertEqual(result.value.claims[0]["kind"], "pass")

    def test_instrument_error_is_inconclusive(self) -> None:
        result = _fake().evaluate(
            RunRef(run_id="run-broken"), EvaluationProtocol(name="fixture")
        )
        self.assertTrue(result.ok)
        self.assertIsNotNone(result.value)
        self.assertEqual(result.value.outcome, "inconclusive")
        self.assertIn("instrument_error", result.value.reason)

    def test_agency_has_no_evaluator_import(self) -> None:
        self.assertEqual(_agency_evaluator_imports(), [])


if __name__ == "__main__":
    unittest.main()
