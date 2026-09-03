"""M-6 Hierarchical Delegation & Cold Reconstruction End-to-End Suite.

Verifies:
1. Governance restriction: No production bypass of mediated delegation.
2. Canonical composition & session wiring of SpawnAdapter for `agent.spawn`.
3. Hierarchical execution through the S0-S12 kernel effect dispatch pipeline.
4. Additive budget conservation across parent and child lineages.
5. Fresh-process cold reconstruction of the multi-agent hierarchy from SQLite WAL.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from typing import Any, Mapping

from test.agency.doubles import ScriptedModel, finish
from test.falsifiers.canonical_fixtures import (
    CODE_CAPABILITIES,
    authored_v2,
    write_pack,
)
from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.domain.canonicalisation.digest import digest_of
from vanguard.packages.domain.ledger.reducer import initial_state, reduce_batch
from vanguard.packages.kernel.attenuation import Constraints, Scope
from vanguard.packages.kernel.model import EffectRequest, Occurrence
from vanguard.packages.ports.environment import (
    EffectReceipt,
    EnvironmentProfile,
    EnvironmentSnapshot,
    Observation,
)
from vanguard.packages.ports.child_runtime import ChildRunPlan, ChildRunResult
from vanguard.packages.ports.event_store import EventRange, Result
from vanguard.packages.runtime.compose import Runtime
from vanguard.packages.runtime.delegation import (
    ADDITIVE_DIMENSIONS,
    SPAWN_VERB,
    ChildLineage,
    derive_child_id,
    DelegationResult,
    SpawnAdapter,
)
from vanguard.packages.runtime.determinism import FixedClock, SeededRandom
from vanguard.packages.runtime.root import HarnessSession, SessionPorts, TaskContext


class _StubChildRuntime:
    """Minimal conforming runner for tests that only assert wiring."""

    def run_child(self, plan: ChildRunPlan) -> ChildRunResult:
        return ChildRunResult(
            ok=True, outcome="completed", terminal="ok",
            child_episode_id=plan.child_episode_id)

ROOT = Path(__file__).resolve().parents[2]
_AT = "2026-08-26T12:00:00.000Z"


class FakeEnvironment:
    """An EnvironmentAdapter for hermetic tests."""

    def __init__(self) -> None:
        self.applied: list[Any] = []

    def profile(self) -> Result[Any]:
        return Result.success(
            EnvironmentProfile(environment_id="fake:/workspace", kind="memory", root="/workspace")
        )

    def snapshot(self) -> Result[Any]:
        return Result.success(
            EnvironmentSnapshot(
                snapshot_id="snap-1", digest="sha256:snap", created_at=_AT
            )
        )

    def observe(self, req: Any, grant: Any = None) -> Result[Any]:
        return Result.success(
            Observation(action=getattr(req, "action", "fs.read"), content="code content")
        )

    def preview(self, req: Any, grant: Any = None) -> Result[Any]:
        return Result.fail("unavailable", "preview unavailable")

    def apply(self, req: Any, grant: Any = None) -> Result[Any]:
        self.applied.append(req)
        return Result.success(
            EffectReceipt(
                descriptor_digest="sha256:descriptor",
                outcome="ok",
                observed_at=_AT,
                result_digest="sha256:applied",
            )
        )

    def reconcile(self, receipt: Any, grant: Any = None) -> Result[Any]:
        return Result.fail("unavailable", "reconcile unavailable")

    def dispose(self) -> Result[None]:
        return Result.success(None)


def _delegation_pack(pack_dir: Path, pack_id: str = "rf-delegation-pack") -> Path:
    """Create an authored /2 pack that includes the agent.spawn capability."""
    spawn_selector = {"kind": "generic", "uriPattern": "agent://spawn/*"}
    capabilities = CODE_CAPABILITIES + (
        {
            "verb": "agent.spawn",
            "sink": "privileged",
            "risk": "high",
            "selector": spawn_selector,
        },
    )
    manifest = authored_v2(
        pack_id,
        capabilities,
        oracle="coding-oracle@3",
        system_prompt="system-prompt.txt",
    )
    return write_pack(pack_dir.parent, pack_id, manifest)


class GovernanceDelegationRestrictions(unittest.TestCase):
    """M-6 governance invariants: direct engine.spawn is restricted."""

    def test_no_production_bypass_of_spawn_adapter(self) -> None:
        """Assert no production code outside agency/episode/engine.py calls engine.spawn directly."""
        offenders: list[str] = []
        packages_dir = ROOT / "vanguard" / "packages"
        for path in sorted(packages_dir.rglob("*.py")):
            if "agency/episode/engine.py" in str(path):
                continue
            text = path.read_text(encoding="utf-8")
            if ".spawn(" in text or "engine.spawn" in text:
                offenders.append(str(path.relative_to(packages_dir)))
        self.assertEqual(
            offenders,
            [],
            f"Production modules must not call engine.spawn directly: {offenders}",
        )

    def test_default_bindings_includes_agent_spawn(self) -> None:
        """Verify wiring binds agent.spawn as a standard effect."""
        from vanguard.packages.runtime.wiring import DEFAULT_BINDINGS

        self.assertIn("agent.spawn", DEFAULT_BINDINGS)
        binding = DEFAULT_BINDINGS["agent.spawn"]
        self.assertFalse(binding.carries_diff)


class HarnessSessionDelegationE2E(unittest.TestCase):
    """End-to-end integration of mediated delegation in HarnessSession."""

    def test_session_wires_spawn_adapter_for_agent_spawn_capability(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pack_path = _delegation_pack(Path(tmp) / "pack")
            harness = Runtime.compose(pack_path, episode_id="ep-parent")
            self.assertIn("agent.spawn", harness.verbs)

            store = SqliteEventStore(":memory:")
            ports = SessionPorts(
                model=ScriptedModel([finish()]),
                environment=FakeEnvironment(),
                clock=FixedClock(at=_AT, step_ms=1),
                store=store,
                random=SeededRandom(seed=42),
                interactive=False,
                child_runtime=_StubChildRuntime(),
            )
            task = TaskContext(
                brief="solve parent task with child delegation",
                repo_path=Path(tmp),
                run_id="run-parent-1",
                episode_id="ep-parent",
                principal="agent-parent",
                max_turns=6,
            )
            session = HarnessSession(harness, ports, task)

            self.assertIn("agent.spawn", session.adapters)
            self.assertIsInstance(session.adapters["agent.spawn"], SpawnAdapter)

    def test_hierarchical_execution_budget_conservation_and_cold_reconstruction(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pack_path = _delegation_pack(Path(tmp) / "pack")
            harness = Runtime.compose(pack_path, episode_id="ep-parent")

            db_path = Path(tmp) / "events.sqlite"
            store = SqliteEventStore(str(db_path))

            child_executed = False

            class _RecordingChildRuntime:
                """A real `ChildRuntimePort`, bound before composition.

                This test used to reach past the binding and assign
                `spawn_adapter._run_child` after the fact, which only worked
                because a synthetic runner was already in place to overwrite.
                With the fallback gone the runner has to be supplied the way
                production supplies one -- through `SessionPorts`.
                """

                def run_child(inner, plan: ChildRunPlan) -> ChildRunResult:
                    nonlocal child_executed
                    child_executed = True
                    self.assertEqual(plan.parent_episode_id, "ep-parent")
                    self.assertEqual(plan.depth, 1)
                    self.assertIn("fs.read", plan.authority)
                    return ChildRunResult(
                        ok=True,
                        outcome="completed",
                        terminal="ok",
                        child_episode_id=plan.child_episode_id,
                        actual_cost={"tokens": 80, "usd_micros": 250},
                        turns_used=2,
                        result_digest="sha256:" + "c" * 64,
                        detail="child extracted subtask cleanly",
                    )

            ports = SessionPorts(
                model=ScriptedModel([finish()]),
                environment=FakeEnvironment(),
                clock=FixedClock(at=_AT, step_ms=1),
                store=store,
                random=SeededRandom(seed=42),
                interactive=False,
                child_runtime=_RecordingChildRuntime(),
            )
            task = TaskContext(
                brief="parent task",
                repo_path=Path(tmp),
                run_id="run-parent-1",
                episode_id="ep-parent",
                principal="agent-parent",
                max_turns=5,
            )
            session = HarnessSession(harness, ports, task)
            spawn_adapter = session.adapters["agent.spawn"]

            # Dispatch an agent.spawn effect through the adapter
            spawn_request = EffectRequest(
                action=SPAWN_VERB,
                resource={"kind": "generic", "uriPattern": "agent://spawn/*"},
                args={
                    "brief": "child subtask: analyze dependencies",
                    "authority": ["fs.read"],
                    "budget": {"tokens": 150, "usd_micros": 500},
                    "maxTurns": 3,
                },
                principal="agent-parent",
                run_id="run-parent-1",
                depth=0,
                idempotency_key="intent-spawn-subtask-1",
            )

            outcome = spawn_adapter.execute(spawn_request)

            self.assertTrue(child_executed)
            self.assertEqual(outcome.status, "ok")
            self.assertEqual(outcome.occurrence, Occurrence.OCCURRED)
            self.assertEqual(dict(outcome.actual_cost), {"tokens": 80, "usd_micros": 250})
            self.assertEqual(outcome.result_digest, "sha256:" + "c" * 64)

            # Close store and read back all events
            store.close()

            # Fresh-process reconstruction from the durable SQLite WAL
            cold_store = SqliteEventStore(str(db_path))
            read_result = cold_store.read(EventRange(run_id=None))
            self.assertTrue(read_result.ok)
            events = list(read_result.value or [])

            kinds = [e.payload.get("kind") for e in events]
            self.assertIn("ChildSpawned", kinds)
            self.assertIn("ChildReturned", kinds)

            # Verify ledger reduction over cold events
            state = reduce_batch(initial_state(), events)

            # Verify child registered in state.children projection.
            # The id is *derived*, not counted: a cold reader recomputes it
            # from the parent episode, the intent key and the project, which
            # is what makes it survive the restart this test performs. The old
            # `ep-parent.c1` came from an in-memory counter and would have been
            # reissued to a different child after any crash.
            child_id = derive_child_id(
                "ep-parent", "intent-spawn-subtask-1", task.project_id)
            self.assertIn(child_id, state.children)
            child_view = state.children[child_id]
            self.assertEqual(child_view.status, "closed")
            self.assertEqual(child_view.outcome, "completed")
            self.assertEqual(child_view.terminal, "ok")
            self.assertEqual(child_view.parent_episode_id, "ep-parent")
            # The reducer now actually folds the cost. It previously read a
            # `cost` key that no writer emitted, so every settled child in
            # every ledger folded to `cost=None` -- the conservation record
            # existed on the wire and nowhere in state.
            self.assertEqual(dict(child_view.cost),
                             {"tokens": 80, "usd_micros": 250})

            cold_store.close()


if __name__ == "__main__":
    unittest.main()
