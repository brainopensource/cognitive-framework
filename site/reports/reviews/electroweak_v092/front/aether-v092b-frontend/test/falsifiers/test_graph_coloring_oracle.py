"""M-5b integrity and adversarial falsifiers for the Graph Coloring witness pack.

Covers:
1. Pinned graph, witness, and oracle digests matching task registry.
2. Positive witness verification.
3. Negative vectors:
   - Edge color conflict
   - Incomplete vertex coverage
   - Unknown vertex in assignment
   - Color out of [0, k) range (negative or >= k)
   - Non-integer color representation
   - Disordered graph / non-canonical format
   - Disordered edge endpoints (u >= v)
4. Exterior oracle separation: pack cannot grade itself (I-5).
5. Pack declares no new event kinds.
"""

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from vanguard.packages.adapters.evaluators.suites.formal_graph_coloring import (
    parse_graph,
    verify_coloring,
)

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "packs/formal-graph-coloring"
REGISTRY = json.loads((PACK / "tasks/registry.json").read_text(encoding="utf-8"))
ORACLE = ROOT / "vanguard/packages/adapters/evaluators/suites/formal_graph_coloring.py"


def _digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _task(task_id: str = "GC-001") -> dict:
    return next(t for t in REGISTRY["tasks"] if t["id"] == task_id)


def _graph_text() -> str:
    return (PACK / _task()["formula"]).read_text(encoding="utf-8")


def _witness() -> dict:
    return json.loads((PACK / _task()["positiveWitness"]).read_text(encoding="utf-8"))


class GraphColoringRegistryPinned(unittest.TestCase):
    """Digest drift: verify that the graph coloring task set is immutable and strictly pinned."""

    def test_the_graph_matches_its_recorded_digest(self) -> None:
        self.assertEqual(_digest(PACK / _task()["formula"]), _task()["formulaDigest"])

    def test_the_positive_witness_matches_its_recorded_digest(self) -> None:
        self.assertEqual(
            _digest(PACK / _task()["positiveWitness"]),
            _task()["positiveWitnessDigest"],
        )

    def test_the_oracle_matches_its_recorded_digest(self) -> None:
        self.assertEqual(_digest(ORACLE), REGISTRY["oracleDigest"])

    def test_tasks_carry_both_accepting_and_rejecting_vectors(self) -> None:
        for task in REGISTRY["tasks"]:
            self.assertTrue((PACK / task["positiveWitness"]).is_file(), task["id"])
            self.assertTrue((PACK / task["negativeVector"]).is_file(), task["id"])
            for role, path in task.get("negativeVectors", {}).items():
                self.assertTrue((PACK / path).is_file(), f"{task['id']}: {role}")


class GraphColoringAdversarialFalsifiers(unittest.TestCase):
    """Adversarial attempts to fool the exterior oracle fail closed."""

    def test_the_pinned_witness_satisfies_the_canonical_graph(self) -> None:
        result = verify_coloring(_graph_text(), _witness())
        self.assertTrue(result.accepted, result.reason)
        self.assertEqual(result.reason, "all_coloring_constraints_satisfied")

    def test_edge_conflict_is_detected(self) -> None:
        bad = json.loads(
            (PACK / "tasks/gc-001.invalid-edge-conflict.json").read_text(encoding="utf-8")
        )
        result = verify_coloring(_graph_text(), bad)
        self.assertFalse(result.accepted)
        self.assertEqual(result.reason, "edge_not_satisfied")
        self.assertEqual(result.failed_edge, (0, 1))

    def test_incomplete_assignment_is_detected(self) -> None:
        bad = json.loads(
            (PACK / "tasks/gc-001.invalid-incomplete.json").read_text(encoding="utf-8")
        )
        result = verify_coloring(_graph_text(), bad)
        self.assertFalse(result.accepted)
        self.assertEqual(result.reason, "assignment_is_not_complete")
        self.assertEqual(result.failed_vertex, 9)

    def test_unknown_extra_vertex_is_detected(self) -> None:
        extra = json.loads(json.dumps(_witness()))
        extra["assignment"]["99"] = 0
        result = verify_coloring(_graph_text(), extra)
        self.assertFalse(result.accepted)
        self.assertEqual(result.reason, "assignment_contains_unknown_vertex")
        self.assertEqual(result.failed_vertex, 99)

    def test_color_out_of_range_is_detected(self) -> None:
        bad = json.loads(
            (PACK / "tasks/gc-001.invalid-range.json").read_text(encoding="utf-8")
        )
        result = verify_coloring(_graph_text(), bad)
        self.assertFalse(result.accepted)
        self.assertEqual(result.reason, "color_out_of_range")
        self.assertEqual(result.failed_vertex, 9)

    def test_negative_color_is_detected(self) -> None:
        bad = json.loads(json.dumps(_witness()))
        bad["assignment"]["0"] = -1
        result = verify_coloring(_graph_text(), bad)
        self.assertFalse(result.accepted)
        self.assertEqual(result.reason, "color_out_of_range")
        self.assertEqual(result.failed_vertex, 0)

    def test_malformed_color_type_is_detected(self) -> None:
        bad = json.loads(
            (PACK / "tasks/gc-001.invalid-malformed.json").read_text(encoding="utf-8")
        )
        result = verify_coloring(_graph_text(), bad)
        self.assertFalse(result.accepted)
        self.assertIn("invalid_witness", result.reason)

    def test_disordered_vertices_in_graph_are_rejected(self) -> None:
        bad_graph = json.loads(_graph_text())
        bad_graph["vertices"] = [1, 0, 2, 3, 4, 5, 6, 7, 8, 9]
        result = verify_coloring(json.dumps(bad_graph), _witness())
        self.assertFalse(result.accepted)
        self.assertIn("strictly ascending", result.reason)

    def test_disordered_edge_endpoints_are_rejected(self) -> None:
        bad_graph = json.loads(_graph_text())
        bad_graph["edges"][0] = [1, 0]  # u >= v violates canonical order
        result = verify_coloring(json.dumps(bad_graph), _witness())
        self.assertFalse(result.accepted)
        self.assertIn("canonical endpoint order", result.reason)

    def test_disordered_edge_sequence_is_rejected(self) -> None:
        bad_graph = json.loads(_graph_text())
        bad_graph["edges"][0], bad_graph["edges"][1] = (
            bad_graph["edges"][1],
            bad_graph["edges"][0],
        )
        result = verify_coloring(json.dumps(bad_graph), _witness())
        self.assertFalse(result.accepted)
        self.assertIn("strictly ascending lexicographical order", result.reason)


class PackSeparationAndSubstrateInvariance(unittest.TestCase):
    """I-5: the oracle is exterior and the pack cannot grade itself."""

    def test_the_oracle_lives_outside_the_pack(self) -> None:
        self.assertTrue(ORACLE.is_file())
        self.assertNotIn("packs/", str(ORACLE.relative_to(ROOT)))

    def test_the_registry_names_the_exterior_oracle_module(self) -> None:
        self.assertTrue(
            REGISTRY["oracle"].startswith("vanguard.packages.adapters.evaluators")
        )

    def test_no_pack_file_grades_or_verifies_witness(self) -> None:
        offenders = []
        for path in PACK.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            for token in ("verify_coloring", "def verify", "accepted=True"):
                if token in text:
                    offenders.append(f"{path.name}: {token}")
        self.assertEqual(offenders, [])

    def test_the_pack_declares_no_new_event_kinds(self) -> None:
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
