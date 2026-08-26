"""RF-52/53 + M-5b integrity falsifiers for the SAT witness pack.

`test/packs/formal_sat/test_formal_sat.py` proves the oracle accepts a correct
witness and rejects a wrong one. These are the attacks it does not cover: the
ways a generality result could be *manufactured* rather than earned.

The M-5b hypothesis is "a materially non-coding domain runs on the unchanged
substrate". A result is only evidence for that if the oracle cannot be talked
into agreeing -- by moving the goalposts (altering the formula), by grading
itself, or by drifting away from the registry that pinned it.
"""

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from vanguard.packages.adapters.evaluators.suites.formal_sat import (
    parse_dimacs,
    verify_assignment,
)

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "packs/formal-sat"
REGISTRY = json.loads((PACK / "tasks/registry.json").read_text(encoding="utf-8"))
ORACLE = ROOT / "vanguard/packages/adapters/evaluators/suites/formal_sat.py"


def _digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _task(task_id: str = "SAT-001") -> dict:
    return next(t for t in REGISTRY["tasks"] if t["id"] == task_id)


def _formula_text() -> str:
    return (PACK / _task()["formula"]).read_text(encoding="utf-8")


def _witness() -> dict:
    return json.loads((PACK / _task()["positiveWitness"]).read_text(encoding="utf-8"))


class TheFixedTaskSetIsActuallyPinned(unittest.TestCase):
    """Digest drift: a registry that records digests nobody checks pins nothing."""

    def test_the_formula_matches_its_recorded_digest(self) -> None:
        self.assertEqual(_digest(PACK / _task()["formula"]), _task()["formulaDigest"])

    def test_the_positive_witness_matches_its_recorded_digest(self) -> None:
        self.assertEqual(_digest(PACK / _task()["positiveWitness"]),
                         _task()["positiveWitnessDigest"])

    def test_the_oracle_matches_its_recorded_digest(self) -> None:
        # If the oracle can be edited without the registry noticing, the task
        # set is not fixed -- the grader moved while the exam stayed still.
        self.assertEqual(_digest(ORACLE), REGISTRY["oracleDigest"])

    def test_every_task_carries_both_an_accepting_and_a_rejecting_vector(self) -> None:
        for task in REGISTRY["tasks"]:
            self.assertTrue((PACK / task["positiveWitness"]).is_file(), task["id"])
            self.assertTrue((PACK / task["negativeVector"]).is_file(), task["id"])

    def test_the_negative_vector_is_actually_rejected(self) -> None:
        bad = json.loads((PACK / _task()["negativeVector"]).read_text(encoding="utf-8"))
        self.assertFalse(verify_assignment(_formula_text(), bad).accepted)


class AlteredFormulasAreNotSatisfied(unittest.TestCase):
    """The cheapest forgery: keep the witness, weaken the problem."""

    def test_the_pinned_witness_satisfies_only_the_pinned_formula(self) -> None:
        self.assertTrue(verify_assignment(_formula_text(), _witness()).accepted)

    def test_dropping_a_clause_is_refused_outright_not_evaluated(self) -> None:
        # Deleting a clause without touching the `p cnf` header leaves the
        # formula internally inconsistent. The oracle refuses to grade it at
        # all rather than silently scoring the weakened problem -- which is a
        # stronger guarantee than merely noticing the digest moved.
        lines = [l for l in _formula_text().splitlines() if l.strip()]
        clauses = [l for l in lines if not l.startswith(("c", "p"))]
        weakened = "\n".join(l for l in lines if l != clauses[-1]) + "\n"
        with self.assertRaises(ValueError) as ctx:
            verify_assignment(weakened, _witness())
        self.assertIn("clauses", str(ctx.exception))

    def test_a_consistently_weakened_formula_still_has_a_different_digest(self) -> None:
        lines = [l for l in _formula_text().splitlines() if l.strip()]
        clauses = [l for l in lines if not l.startswith(("c", "p"))]
        header = next(l for l in lines if l.startswith("p "))
        count = int(header.split()[-1])
        weakened = "\n".join(
            (header.rsplit(" ", 1)[0] + f" {count - 1}") if l.startswith("p ")
            else l
            for l in lines if l != clauses[-1]) + "\n"
        self.assertNotEqual(
            verify_assignment(weakened, _witness()).formula_digest,
            verify_assignment(_formula_text(), _witness()).formula_digest)

    def test_a_negated_clause_is_detected_not_absorbed(self) -> None:
        # Flip every literal of one clause: the pinned witness must now fail.
        lines = _formula_text().splitlines()
        for index, line in enumerate(lines):
            stripped = line.strip()
            if stripped and not stripped.startswith(("c", "p")) and stripped.endswith("0"):
                literals = [int(x) for x in stripped.split() if x != "0"]
                lines[index] = " ".join(str(-l) for l in literals) + " 0"
                break
        result = verify_assignment("\n".join(lines) + "\n", _witness())
        self.assertFalse(result.accepted)
        self.assertEqual(result.reason, "clause_not_satisfied")

    def test_a_formula_with_more_variables_makes_the_witness_incomplete(self) -> None:
        formula = parse_dimacs(_formula_text())
        grown = _formula_text().replace(
            f"p cnf {formula.variables}", f"p cnf {formula.variables + 1}", 1)
        result = verify_assignment(grown, _witness())
        self.assertFalse(result.accepted)
        self.assertEqual(result.reason, "assignment_is_not_complete")


class ThePackCannotGradeItself(unittest.TestCase):
    """I-5: the witness verifier is exterior. A pack that grades itself proves nothing."""

    def test_the_oracle_lives_outside_the_pack(self) -> None:
        self.assertTrue(ORACLE.is_file())
        self.assertNotIn("packs/", str(ORACLE.relative_to(ROOT)))

    def test_the_registry_names_the_exterior_oracle_module(self) -> None:
        self.assertTrue(REGISTRY["oracle"].startswith("vanguard.packages.adapters.evaluators"))

    def test_no_pack_file_verifies_a_witness(self) -> None:
        # The pack may *write* a candidate; deciding whether it holds is the
        # evaluator daemon's job and nobody else's.
        offenders = []
        for path in PACK.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            for token in ("verify_assignment", "def verify", "accepted=True"):
                if token in text:
                    offenders.append(f"{path.name}: {token}")
        self.assertEqual(offenders, [])

    def test_the_pack_declares_no_new_event_kind(self) -> None:
        # "no new event kinds permitted (that is the test)" -- SPEC_M5B_M6 §1.
        from vanguard.packages.domain.ledger.events import READABLE_KINDS

        for path in PACK.rglob("*"):
            if not path.is_file() or path.suffix not in {".py", ".json", ".yaml"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for kind in ("ClaimRecorded", "ProposalProduced", "EffectCompleted"):
                if kind in text:
                    self.assertIn(kind, READABLE_KINDS)


if __name__ == "__main__":
    unittest.main()
