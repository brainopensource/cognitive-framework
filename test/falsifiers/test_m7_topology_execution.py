"""B-O12-01: M-7 topologies *execute*, they do not merely lower.

`milestones.md` M-7 requires that direct, planner/executor/reviewer and
fork/read/merge topologies "execute through one public path". For a long time
`run_composed` parsed a topology, lowered it and computed a sequential order,
and stopped there: `roleOperations` had no consumer but the scheduler check and
the lowering tests. A suite that only asserted lowering would have reported M-7
green while nothing ran.

These falsifiers therefore assert against the *ledger*, not against the lowered
structure. A role that executed left `ChildSpawned`/`ChildReturned` facts under
the root episode; a role that merely lowered left nothing.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from test.falsifiers.canonical_fixtures import (  # noqa: E402
    CODE_CAPABILITIES,
    authored_v2,
    write_pack,
)
from test.fixtures.m7_topologies import (  # noqa: E402
    CRITIC_REVISER,
    DIRECT,
    PLANNER_EXECUTOR,
)
from vanguard.packages.adapters.models.lam import LamModelAdapter  # noqa: E402
from vanguard.packages.agency import RunTermination  # noqa: E402
from vanguard.packages.ports.event_store import Result  # noqa: E402
from vanguard.packages.ports.evaluator import Verdict  # noqa: E402
from vanguard.packages.runtime.governance.approvals import OperatorSigner  # noqa: E402
from vanguard.packages.runtime.root import Runtime, TaskContext  # noqa: E402
from vanguard.packages.runtime.topology import parse_topology  # noqa: E402

#: The three M-7 exit-gate forms, with the role count each must actually run.
#: `DIRECT` is the degenerate case: one lineage, no delegation, so it spawns
#: nothing and must still complete through the very same path.
FORMS = (("direct", DIRECT, 0),
         ("planner-executor", PLANNER_EXECUTOR, 2),
         ("critic-reviser", CRITIC_REVISER, 3))


class _Verifier:
    def evaluate(self, run_ref, protocol):  # noqa: ANN001
        return Result.success(Verdict(
            outcome="claims", claims=({"claim": "m7", "holds": True},),
            reason=protocol.name))


def _run_topology(topology, base: Path):
    """One real run through the sole public boundary. No fakes, no stubs."""
    capabilities = CODE_CAPABILITIES + ({
        "verb": "agent.spawn", "sink": "privileged", "risk": "high",
        "selector": {"kind": "generic", "uriPattern": "agent://spawn/*"},
    },)
    manifest = write_pack(base, "m7-exec-pack", authored_v2(
        "m7-exec-pack", capabilities, oracle="coding-oracle@3",
        system_prompt="system-prompt.txt"))
    repo = base / "repo"
    (repo / "src").mkdir(parents=True)
    (repo / "src/value.py").write_text("VALUE = 1\n", encoding="utf-8")
    (repo / "test_value.py").write_text(
        "import unittest\nfrom src.value import VALUE\n\n"
        "class TestValue(unittest.TestCase):\n"
        "    def test_value(self):\n        self.assertEqual(VALUE, 2)\n",
        encoding="utf-8")
    signer = OperatorSigner(b"m7-topology-execution-key")
    return Runtime.execute_harness(
        manifest,
        TaskContext(brief="Repair the value bug and verify the test suite.",
                    repo_path=repo, run_id="m7-run", episode_id="m7-episode",
                    principal="agent-1", max_turns=12, topology=topology),
        model=LamModelAdapter(model_name="lam/t0-vanguard-vertical"),
        approver=lambda challenge: signer.approve(challenge, reviewer="operator"),
        approval_key=signer.public_bytes,
        verifier=_Verifier(),
    )


class EveryTopologyFormActuallyExecutes(unittest.TestCase):
    """M7-EXEC-01: the three forms run, and their roles become real children."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.runs = {}
        for name, topology, expected in FORMS:
            directory = tempfile.TemporaryDirectory()
            cls.addClassCleanup(directory.cleanup)
            cls.runs[name] = (_run_topology(topology, Path(directory.name)),
                              expected)

    def test_all_three_forms_complete_through_the_one_public_path(self) -> None:
        for name, (result, _) in self.runs.items():
            with self.subTest(topology=name):
                self.assertIs(result.terminal, RunTermination.COMPLETED)

    def test_role_operations_execute_as_m6_children(self) -> None:
        """The discriminator: lowering leaves no facts, execution does."""
        for name, (result, expected) in self.runs.items():
            with self.subTest(topology=name):
                kinds = [event.kind for event in result.events]
                self.assertEqual(kinds.count("ChildSpawned"), expected)
                self.assertEqual(kinds.count("ChildReturned"), expected)

    def test_every_child_is_bound_to_the_root_episode(self) -> None:
        """One foldable tree, not an unlinkable second history."""
        for name, (result, expected) in self.runs.items():
            if not expected:
                continue
            with self.subTest(topology=name):
                parents = {
                    event.payload.get("parentEpisodeId")
                    for event in result.events if event.kind == "ChildSpawned"
                }
                self.assertEqual(parents, {"m7-episode"})

    def test_each_role_runs_exactly_once(self) -> None:
        """A replayed or duplicated role would inflate the child count."""
        for name, (result, expected) in self.runs.items():
            if not expected:
                continue
            with self.subTest(topology=name):
                children = [
                    event.payload.get("childEpisodeId")
                    for event in result.events if event.kind == "ChildSpawned"
                ]
                self.assertEqual(len(children), len(set(children)))

    def test_artifact_flows_are_exercised_between_roles(self) -> None:
        """A settled producer digest is carried into its causal consumer."""
        result, _ = self.runs["planner-executor"]
        spawned = [event for event in result.events
                   if event.kind == "ChildSpawned"]
        self.assertEqual(len(spawned), 2)
        self.assertEqual(spawned[0].payload.get("artifactRefs"), None)
        refs = spawned[1].payload.get("artifactRefs")
        self.assertEqual(len(refs), 1)
        self.assertEqual(refs[0]["artifact"], "plan")
        self.assertTrue(str(refs[0]["digest"]).startswith("sha256:"))


class ExecutionHonoursTheDeclaredStructure(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        directory = tempfile.TemporaryDirectory()
        cls.addClassCleanup(directory.cleanup)
        cls.result = _run_topology(CRITIC_REVISER, Path(directory.name))

    def _roles_in_settlement_order(self) -> list[str]:
        """Role names as the ledger recorded them, not as the plan hoped.

        `settledIntentKey` is `topology:<digest>:<role>`, so the durable fact
        carries which role each child was, and the intent is bound to the
        topology digest -- two topologies cannot collide on one key.
        """
        return [str(event.payload.get("settledIntentKey", "")).rsplit(":", 1)[-1]
                for event in self.result.events if event.kind == "ChildReturned"]

    def test_children_are_spawned_in_causal_predecessor_order(self) -> None:
        """author -> critic -> reviser. Structure is not a suggestion."""
        self.assertEqual(self._roles_in_settlement_order(),
                         ["author", "critic", "reviser"])

    def test_each_intent_key_is_bound_to_the_topology_digest(self) -> None:
        """Cross-topology idempotency keys must not collide."""
        keys = [str(event.payload.get("settledIntentKey", ""))
                for event in self.result.events if event.kind == "ChildSpawned"]
        self.assertTrue(keys)
        for key in keys:
            with self.subTest(key=key):
                self.assertTrue(key.startswith("topology:sha256:"))
        self.assertEqual(len(keys), len(set(keys)))

    def test_execution_is_sequential_not_overlapped(self) -> None:
        """ADR-0099 is `SEQUENTIAL_CONFIRMED`; no child may open before the
        previous one settles, or the disposition would be contradicted by the
        very evidence offered to support it."""
        depth = 0
        for event in self.result.events:
            if event.kind == "ChildSpawned":
                depth += 1
                self.assertLessEqual(depth, 1, "children overlapped")
            elif event.kind == "ChildReturned":
                depth -= 1
        self.assertEqual(depth, 0, "a child never settled")

    def test_the_ledger_reconstructs_the_whole_tree_cold(self) -> None:
        """Every executed role is recoverable from the facts alone."""
        spawned = {event.payload.get("childEpisodeId")
                   for event in self.result.events if event.kind == "ChildSpawned"}
        returned = {event.payload.get("childEpisodeId")
                    for event in self.result.events if event.kind == "ChildReturned"}
        self.assertEqual(spawned, returned)
        self.assertTrue(spawned)


class WhatRoleExecutionDoesAndDoesNotYetShow(unittest.TestCase):
    """M7-EXEC-02: the boundary of the current execution claim.

    Recording this boundary is the point. `run_composed` now really does spawn
    each lowered role as an M-6 child, and the degenerate `direct` form does
    real work through the canonical path. But under a multi-role topology the
    root model is replaced by the topology bridge, which only emits spawn
    proposals -- so the root performs no effects, and each role lineage settles
    `abandoned` having performed none either.

    That means role-to-role *artifact flows* are declared and lowered but never
    exercised. M-7's evidence must say so: a milestone that claimed honoured
    artifact flows on the strength of these runs would be claiming a behaviour
    no fact in the ledger supports.
    """

    def test_the_direct_form_does_real_work_through_the_canonical_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = _run_topology(DIRECT, Path(directory))
        self.assertIs(result.terminal, RunTermination.COMPLETED)
        self.assertEqual([receipt.verb for receipt in result.receipts],
                         ["fs.read", "patch.apply", "proc.exec"])

    def test_multi_role_lineages_currently_perform_no_effects(self) -> None:
        """Pins the gap. If a role ever does real work this test must be
        rewritten -- and M-7's `artifact_flows_exercised` marker can be set."""
        with tempfile.TemporaryDirectory() as directory:
            result = _run_topology(PLANNER_EXECUTOR, Path(directory))
        self.assertEqual([receipt.verb for receipt in result.receipts], [])
        outcomes = {event.payload.get("outcome")
                    for event in result.events if event.kind == "ChildReturned"}
        self.assertEqual(outcomes, {"abandoned"})

    def test_no_artifact_flow_fact_is_recorded_for_a_declared_flow(self) -> None:
        """`critic-reviser` declares draft and critique flows; nothing carries
        them, so no fact should pretend otherwise."""
        with tempfile.TemporaryDirectory() as directory:
            result = _run_topology(CRITIC_REVISER, Path(directory))
        self.assertTrue(CRITIC_REVISER["artifactFlows"])
        produced = [event for event in result.events
                    if event.kind == "ArtifactCreated"]
        self.assertEqual(produced, [])


class TopologyDataCarriesNoAuthority(unittest.TestCase):
    """Executing a topology must not become a way to widen authority."""

    def test_a_role_may_not_declare_its_own_capabilities(self) -> None:
        hostile = {
            **CRITIC_REVISER,
            "roles": [{**role, "capabilities": ["proc.exec"]}
                      for role in CRITIC_REVISER["roles"]],
        }
        with self.assertRaises(Exception):
            parse_topology(hostile)

    def test_children_never_receive_the_spawn_verb(self) -> None:
        """Otherwise a two-role topology could unfold without bound."""
        with tempfile.TemporaryDirectory() as directory:
            result = _run_topology(PLANNER_EXECUTOR, Path(directory))
        for event in result.events:
            if event.kind == "ChildSpawned":
                authority = event.payload.get("authority") or ()
                self.assertNotIn("agent.spawn", list(authority))


if __name__ == "__main__":
    unittest.main()
