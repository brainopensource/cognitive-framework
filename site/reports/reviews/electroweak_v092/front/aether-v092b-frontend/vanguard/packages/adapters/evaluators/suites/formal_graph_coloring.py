"""Deterministic exterior oracle for the M-5b Graph Coloring witness pack.

The oracle checks a complete k-coloring assignment against a canonical graph instance.
It does NOT search for a coloring and never treats the generator's claim as evidence.
Signing remains owned by the evaluator daemon.
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
    "ColoringVerificationResult",
    "Graph",
    "GraphColoringEvaluator",
    "parse_graph",
    "parse_witness",
    "verify_coloring",
]


@dataclass(frozen=True, slots=True)
class Graph:
    k: int
    vertices: tuple[int, ...]
    edges: tuple[tuple[int, int], ...]


@dataclass(frozen=True, slots=True)
class ColoringVerificationResult:
    accepted: bool
    reason: str
    graph_digest: str
    witness_digest: str
    failed_edge: tuple[int, int] | None = None
    failed_vertex: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "accepted": self.accepted,
            "reason": self.reason,
            "graphDigest": self.graph_digest,
            "witnessDigest": self.witness_digest,
            "failedEdge": list(self.failed_edge) if self.failed_edge else None,
            "failedVertex": self.failed_vertex,
        }


def _sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _canonical_bytes(data: Mapping[str, Any]) -> bytes:
    return json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")


def parse_graph(text: str) -> Graph:
    try:
        raw = json.loads(text)
    except Exception as exc:
        raise ValueError(f"malformed graph JSON: {exc}") from exc

    if not isinstance(raw, Mapping):
        raise ValueError("graph root must be an object")

    k = raw.get("k")
    if not isinstance(k, int) or isinstance(k, bool) or k < 1:
        raise ValueError("k must be a positive integer")

    raw_vertices = raw.get("vertices")
    if not isinstance(raw_vertices, list) or not raw_vertices:
        raise ValueError("vertices must be a non-empty array")

    vertices: list[int] = []
    seen_v: set[int] = set()
    prev_v = -1
    for idx, v in enumerate(raw_vertices):
        if not isinstance(v, int) or isinstance(v, bool) or v < 0:
            raise ValueError(f"vertex at index {idx} must be a non-negative integer")
        if v in seen_v:
            raise ValueError(f"duplicate vertex {v}")
        if idx > 0 and v <= prev_v:
            raise ValueError("vertices must be in strictly ascending sorted order")
        vertices.append(v)
        seen_v.add(v)
        prev_v = v

    raw_edges = raw.get("edges")
    if not isinstance(raw_edges, list):
        raise ValueError("edges must be an array")

    edges: list[tuple[int, int]] = []
    seen_e: set[tuple[int, int]] = set()
    prev_e: tuple[int, int] | None = None
    for idx, edge in enumerate(raw_edges):
        if not isinstance(edge, list) or len(edge) != 2:
            raise ValueError(f"edge at index {idx} must be a 2-element array [u, v]")
        u, v = edge
        if not isinstance(u, int) or not isinstance(v, int) or isinstance(u, bool) or isinstance(v, bool):
            raise ValueError(f"edge endpoints at index {idx} must be integers")
        if u not in seen_v or v not in seen_v:
            raise ValueError(f"edge [{u}, {v}] references undeclared vertex")
        if u >= v:
            raise ValueError(f"edge [{u}, {v}] violates canonical endpoint order (u < v required)")
        e_tuple = (u, v)
        if e_tuple in seen_e:
            raise ValueError(f"duplicate edge [{u}, {v}]")
        if prev_e is not None and e_tuple <= prev_e:
            raise ValueError("edges must be in strictly ascending lexicographical order")
        edges.append(e_tuple)
        seen_e.add(e_tuple)
        prev_e = e_tuple

    return Graph(k=k, vertices=tuple(vertices), edges=tuple(edges))


def parse_witness(value: Mapping[str, Any]) -> dict[int, int]:
    if not isinstance(value, Mapping):
        raise ValueError("witness must be a JSON object")
    raw = value.get("assignment")
    if not isinstance(raw, Mapping):
        raise ValueError("witness requires an assignment object")

    assignment: dict[int, int] = {}
    for key, color in raw.items():
        try:
            vertex = int(key)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"invalid witness vertex key {key!r}") from exc

        if not isinstance(color, int) or isinstance(color, bool):
            raise ValueError(f"color for vertex {vertex} must be an integer")
        assignment[vertex] = color

    return assignment


def verify_coloring(
    graph_text: str,
    witness: Mapping[str, Any],
) -> ColoringVerificationResult:
    """Verify a graph coloring with zero search. O(|V| + |E|)."""
    graph_digest = _sha256(graph_text.encode("utf-8"))
    witness_digest = _sha256(_canonical_bytes(witness))

    try:
        graph = parse_graph(graph_text)
    except Exception as exc:
        return ColoringVerificationResult(
            accepted=False,
            reason=f"invalid_graph: {exc}",
            graph_digest=graph_digest,
            witness_digest=witness_digest,
        )

    try:
        assignment = parse_witness(witness)
    except Exception as exc:
        return ColoringVerificationResult(
            accepted=False,
            reason=f"invalid_witness: {exc}",
            graph_digest=graph_digest,
            witness_digest=witness_digest,
        )

    # 1. Completeness: every vertex must be assigned
    expected_vertices = set(graph.vertices)
    assigned_vertices = set(assignment.keys())

    missing = expected_vertices - assigned_vertices
    if missing:
        return ColoringVerificationResult(
            accepted=False,
            reason="assignment_is_not_complete",
            graph_digest=graph_digest,
            witness_digest=witness_digest,
            failed_vertex=min(missing),
        )

    extra = assigned_vertices - expected_vertices
    if extra:
        return ColoringVerificationResult(
            accepted=False,
            reason="assignment_contains_unknown_vertex",
            graph_digest=graph_digest,
            witness_digest=witness_digest,
            failed_vertex=min(extra),
        )

    # 2. Range: color must be in [0, k)
    for v in graph.vertices:
        c = assignment[v]
        if c < 0 or c >= graph.k:
            return ColoringVerificationResult(
                accepted=False,
                reason="color_out_of_range",
                graph_digest=graph_digest,
                witness_digest=witness_digest,
                failed_vertex=v,
            )

    # 3. Edges: no monochromatic edge
    for u, v in graph.edges:
        if assignment[u] == assignment[v]:
            return ColoringVerificationResult(
                accepted=False,
                reason="edge_not_satisfied",
                graph_digest=graph_digest,
                witness_digest=witness_digest,
                failed_edge=(u, v),
            )

    return ColoringVerificationResult(
        accepted=True,
        reason="all_coloring_constraints_satisfied",
        graph_digest=graph_digest,
        witness_digest=witness_digest,
    )


class GraphColoringEvaluator:
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
            graph_path = self._path(protocol.parameters.get("graph"))
            witness_path = self._path(protocol.parameters.get("witness"))
            result = verify_coloring(
                graph_path.read_text(encoding="utf-8"),
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
    parser = argparse.ArgumentParser(description="Verify one Graph Coloring witness")
    parser.add_argument("--graph", required=True)
    parser.add_argument("--witness", required=True)
    args = parser.parse_args(argv)
    try:
        result = verify_coloring(
            Path(args.graph).read_text(encoding="utf-8"),
            json.loads(Path(args.witness).read_text(encoding="utf-8")),
        )
    except Exception as exc:
        print(json.dumps({"accepted": False, "reason": "instrument_error", "detail": str(exc)}))
        return 2
    print(json.dumps(result.to_dict(), sort_keys=True, separators=(",", ":")))
    return 0 if result.accepted else 1


if __name__ == "__main__":
    raise SystemExit(main())
