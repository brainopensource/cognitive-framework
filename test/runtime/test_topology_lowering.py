"""A-M7 topology lowering and sequential readiness mechanism."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import unittest

from vanguard.packages.runtime.scheduler import (
    ReadyOperation,
    ScheduleError,
    SequentialScheduler,
    ready_operations,
    safe_read_only_group,
)
from vanguard.packages.runtime.topology import (
    TOPOLOGY_SCHEMA,
    TopologyError,
    lower_topology,
    parse_topology,
)


def _topology() -> dict:
    return {
        "api": TOPOLOGY_SCHEMA,
        "topologyId": "planner-executor",
        "version": "1.0.0",
        "entryRole": "planner",
        "roles": [
            {"id": "executor", "policyRef": "policy/executor@1",
             "scope": {"workspace": "/workspace"},
             "budget": {"turns": 2, "tokens": 100}, "context": {}},
            {"id": "planner", "policyRef": "policy/planner@1",
             "scope": {"workspace": "/workspace"},
             "budget": {"turns": 2, "tokens": 100}, "context": {}},
        ],
        "edges": [{"from": "planner", "to": "executor",
                   "relation": "may_delegate_to"}],
        "artifactFlows": [
            {"artifact": "plan", "from": "planner", "to": "executor",
             "schemaId": "mhf.plan/1"}
        ],
    }


@dataclass(frozen=True)
class _Composition:
    verbs: tuple[str, ...] = ("agent.spawn",)
    budget: dict[str, int] | None = None
    composition_digest: str = "sha256:" + "a" * 64

    def __post_init__(self) -> None:
        if self.budget is None:
            object.__setattr__(self, "budget", {"tokens": 1000})


class TopologyValueBoundary(unittest.TestCase):
    def test_schema_exists_and_codegen_exposes_the_artifact(self) -> None:
        schema = json.loads((
            Path(__file__).resolve().parents[2]
            / "schemas/mhf/topology.schema.json"
        ).read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["api"]["const"], TOPOLOGY_SCHEMA)
        from vanguard.packages.domain.wire.types_gen import TopologyArtifact
        self.assertEqual(TopologyArtifact.__name__, "TopologyArtifact")

    def test_semantically_equal_declaration_order_has_one_digest(self) -> None:
        raw = _topology()
        reversed_roles = {**raw, "roles": list(reversed(raw["roles"]))}
        self.assertEqual(parse_topology(raw).digest(),
                         parse_topology(reversed_roles).digest())

    def test_authority_is_rejected_at_any_nesting_depth(self) -> None:
        raw = _topology()
        raw["roles"][0]["scope"] = {"nested": {"capabilityGrant": "g-1"}}
        with self.assertRaisesRegex(TopologyError, "authority"):
            parse_topology(raw)

    def test_malformed_or_unrunnable_structure_fails_before_lowering(self) -> None:
        raw = _topology()
        raw["artifactFlows"][0]["from"] = "missing-role"
        with self.assertRaisesRegex(TopologyError, "no declared producer"):
            parse_topology(raw)


class SequentialLowering(unittest.TestCase):
    def test_lowering_binds_composition_and_emits_no_concurrent_mode(self) -> None:
        lowered = lower_topology(parse_topology(_topology()), _Composition())
        self.assertEqual(lowered["compositionDigest"], "sha256:" + "a" * 64)
        self.assertEqual(lowered["executionMode"], "sequential")
        self.assertEqual(lowered["schedulerPolicy"], "sequential-reference")
        self.assertEqual(lowered["activation"], "ordinary-agent-spawn-sequential")
        self.assertEqual(
            [item["role"] for item in lowered["lineageTemplates"]],
            ["planner", "executor"],
        )
        self.assertEqual(
            lowered["roleOperations"][1]["causalPredecessors"],
            ("role:planner",),
        )

    def test_multi_role_lowering_requires_mediated_spawn_in_composition(self) -> None:
        composition = _Composition(verbs=("fs.read",))
        with self.assertRaisesRegex(TopologyError, "agent.spawn"):
            lower_topology(parse_topology(_topology()), composition)

    def test_role_budget_cannot_exceed_composition_ceiling(self) -> None:
        composition = _Composition(budget={"tokens": 50})
        with self.assertRaisesRegex(TopologyError, "above composition ceiling"):
            lower_topology(parse_topology(_topology()), composition)

    def test_review_edges_order_work_but_do_not_grant_delegation(self) -> None:
        raw = _topology()
        raw["edges"][0]["relation"] = "reviews"
        lowered = lower_topology(parse_topology(raw), _Composition())
        self.assertEqual(lowered["allowedDelegations"], ())
        self.assertEqual(lowered["lineageTemplates"][0]["allowedTargets"], ())
        self.assertEqual(
            lowered["roleOperations"][1]["causalPredecessors"],
            ("role:planner",),
        )


class ReadinessMechanism(unittest.TestCase):
    def test_only_settled_predecessors_make_an_operation_ready(self) -> None:
        operations = (
            ReadyOperation("role:executor", ("role:planner",)),
            ReadyOperation("role:planner"),
        )
        self.assertEqual(
            tuple(item.operation_id for item in ready_operations(operations)),
            ("role:planner",),
        )
        decisions = SequentialScheduler().decide(
            operations, settled=frozenset({"role:planner"}))
        self.assertEqual(tuple(item.operation_id for item in decisions),
                         ("role:executor",))
        self.assertFalse(any(item.parallel for item in decisions))

    def test_unknown_dependencies_and_duplicate_ids_fail_closed(self) -> None:
        with self.assertRaises(ScheduleError):
            ready_operations((ReadyOperation("a", ("missing",)),))
        with self.assertRaises(ScheduleError):
            ready_operations((ReadyOperation("a"), ReadyOperation("a")))

    def test_safe_read_group_is_proof_only_and_rejects_writes(self) -> None:
        reads = (
            ReadyOperation("a", selector={"kind": "fs", "root": "/w",
                                           "paths": ["/w/a"]},
                           sink="observation", read_only=True),
            ReadyOperation("b", selector={"kind": "fs", "root": "/w",
                                           "paths": ["/w/b"]},
                           sink="observation", read_only=True),
        )
        self.assertEqual(safe_read_only_group(reads), ("a", "b"))
        write = ReadyOperation(
            "w", selector={"kind": "fs", "root": "/w", "paths": ["/w/c"]},
            sink="privileged", read_only=False)
        self.assertEqual(safe_read_only_group(reads + (write,)), ())


if __name__ == "__main__":
    unittest.main()
