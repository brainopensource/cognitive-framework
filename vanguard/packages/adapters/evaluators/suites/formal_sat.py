"""Deterministic exterior oracle for the M-5b SAT witness pack.

The oracle checks a complete Boolean assignment against a DIMACS CNF instance.
It does not search for an assignment and never treats the generator's claim as
evidence.  Signing remains owned by the evaluator daemon.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from ....ports.evaluator import EvaluationProtocol, RunRef, Verdict
from ....ports.event_store import Result

__all__ = [
    "CnfFormula",
    "SatWitnessEvaluator",
    "VerificationResult",
    "parse_dimacs",
    "parse_witness",
    "verify_assignment",
]


@dataclass(frozen=True, slots=True)
class CnfFormula:
    variables: int
    clauses: tuple[tuple[int, ...], ...]


@dataclass(frozen=True, slots=True)
class VerificationResult:
    accepted: bool
    reason: str
    formula_digest: str
    witness_digest: str
    failed_clause: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "accepted": self.accepted,
            "reason": self.reason,
            "formulaDigest": self.formula_digest,
            "witnessDigest": self.witness_digest,
            "failedClause": self.failed_clause,
        }


def _sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def parse_dimacs(text: str) -> CnfFormula:
    header: tuple[int, int] | None = None
    literals: list[int] = []
    clauses: list[tuple[int, ...]] = []
    for line_number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("c"):
            continue
        if line.startswith("p"):
            parts = line.split()
            if header is not None or len(parts) != 4 or parts[:2] != ["p", "cnf"]:
                raise ValueError(f"invalid DIMACS header at line {line_number}")
            variables, count = int(parts[2]), int(parts[3])
            if variables < 1 or count < 1:
                raise ValueError("DIMACS counts must be positive")
            header = variables, count
            continue
        if header is None:
            raise ValueError("DIMACS clauses precede the header")
        for token in line.split():
            literal = int(token)
            if literal == 0:
                if not literals:
                    raise ValueError("empty clauses are not supported by this witness pack")
                clauses.append(tuple(literals))
                literals = []
            else:
                if abs(literal) > header[0]:
                    raise ValueError(f"literal {literal} exceeds declared variable count")
                literals.append(literal)
    if header is None:
        raise ValueError("DIMACS header is missing")
    if literals:
        raise ValueError("final DIMACS clause is not terminated by zero")
    if len(clauses) != header[1]:
        raise ValueError(
            f"declared {header[1]} clauses but parsed {len(clauses)}"
        )
    return CnfFormula(variables=header[0], clauses=tuple(clauses))


def parse_witness(value: Mapping[str, Any]) -> dict[int, bool]:
    raw = value.get("assignment")
    if not isinstance(raw, Mapping):
        raise ValueError("witness requires an assignment object")
    assignment: dict[int, bool] = {}
    for key, truth in raw.items():
        try:
            variable = int(key)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"invalid witness variable {key!r}") from exc
        if variable < 1 or isinstance(truth, int) and not isinstance(truth, bool):
            raise ValueError("witness variables must be positive and values must be booleans")
        if not isinstance(truth, bool):
            raise ValueError("witness values must be booleans")
        assignment[variable] = truth
    return assignment


def verify_assignment(
    formula_text: str,
    witness: Mapping[str, Any],
) -> VerificationResult:
    formula = parse_dimacs(formula_text)
    assignment = parse_witness(witness)
    expected = set(range(1, formula.variables + 1))
    if set(assignment) != expected:
        return VerificationResult(
            accepted=False,
            reason="assignment_is_not_complete",
            formula_digest=_sha256(formula_text.encode("utf-8")),
            witness_digest=_sha256(_canonical_witness(witness)),
        )
    for index, clause in enumerate(formula.clauses):
        if not any(assignment[abs(literal)] == (literal > 0) for literal in clause):
            return VerificationResult(
                accepted=False,
                reason="clause_not_satisfied",
                formula_digest=_sha256(formula_text.encode("utf-8")),
                witness_digest=_sha256(_canonical_witness(witness)),
                failed_clause=index,
            )
    return VerificationResult(
        accepted=True,
        reason="all_clauses_satisfied",
        formula_digest=_sha256(formula_text.encode("utf-8")),
        witness_digest=_sha256(_canonical_witness(witness)),
    )


def _canonical_witness(witness: Mapping[str, Any]) -> bytes:
    return json.dumps(witness, sort_keys=True, separators=(",", ":")).encode("utf-8")


class SatWitnessEvaluator:
    """EvaluatorPort implementation intended to run in the exterior daemon."""

    def __init__(self, workspace: Path | str) -> None:
        self._workspace = Path(workspace).resolve()

    def _path(self, relative: object) -> Path:
        if not isinstance(relative, str) or not relative:
            raise ValueError("oracle paths must be non-empty strings")
        candidate = (self._workspace / relative).resolve()
        try:
            candidate.relative_to(self._workspace)
        except ValueError as exc:
            raise ValueError("oracle path escapes the evaluated workspace") from exc
        return candidate

    def evaluate(self, run_ref: RunRef, protocol: EvaluationProtocol) -> Result[Verdict]:
        try:
            formula_path = self._path(protocol.parameters.get("formula"))
            witness_path = self._path(protocol.parameters.get("witness"))
            result = verify_assignment(
                formula_path.read_text(encoding="utf-8"),
                json.loads(witness_path.read_text(encoding="utf-8")),
            )
        except Exception:
            return Result.success(Verdict(outcome="inconclusive", reason="instrument_error"))
        return Result.success(Verdict(
            outcome="claims",
            claims=({
                "event": "EvaluationCompleted",
                "status": "passed" if result.accepted else "failed",
                "runId": run_ref.run_id,
                "protocol": protocol.name,
                **result.to_dict(),
            },),
        ))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify one DIMACS SAT witness")
    parser.add_argument("--formula", required=True)
    parser.add_argument("--witness", required=True)
    args = parser.parse_args(argv)
    try:
        result = verify_assignment(
            Path(args.formula).read_text(encoding="utf-8"),
            json.loads(Path(args.witness).read_text(encoding="utf-8")),
        )
    except Exception as exc:
        print(json.dumps({"accepted": False, "reason": "instrument_error", "detail": str(exc)}))
        return 2
    print(json.dumps(result.to_dict(), sort_keys=True, separators=(",", ":")))
    return 0 if result.accepted else 1


if __name__ == "__main__":
    raise SystemExit(main())
