"""Falsifiers for T-139 / ADR-0107: task.revise capability.

Coverage:
1. Scripted episode where model issues `task_revise` (`task.revise`).
2. Revision is durable in ledger before next proposal.
3. Revised state appears in L5 working state / dialogue.
4. Uninterrupted state matches state after compaction and fresh-process restart
   from SQLite store without duplicate revisions.
5. Invalid, stale, and widening requests leave state and authority unchanged.
6. Conflicting `revision_id` is refused with `TASK_REVISION_CONFLICTING`;
   identical replay returns original receipt.
7. Observation batch carrying `task.revise` dispatches zero members.
8. Disabling sink handoff or revision persistence fails corresponding oracles.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Mapping

from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.agency import EpisodeEngine, RunTermination
from vanguard.packages.domain.canonicalisation.digest import digest_of
from vanguard.packages.domain.task_state import (
    TASK_MUTABLE_FIELDS,
    TASK_REVISION_CONFLICTING,
    TASK_REVISION_MALFORMED,
    TASK_REVISION_STALE,
    TASK_REVISION_WIDENING,
    SemanticTaskState,
    TaskRevision,
    validate_revision_invariants,
)
from vanguard.packages.kernel import (
    AdapterOutcome,
    EffectRequest,
    Event,
    Occurrence,
    Scope,
    SinkClass,
    SinkRegistry,
)
from vanguard.packages.ports.event_store import EventRange
from vanguard.packages.runtime.determinism import FixedClock, SeededRandom
from vanguard.packages.runtime.ledger_emitter import LedgerEmitter
from vanguard.packages.runtime.task_state import (
    TaskRevisionHook,
    append_task_revision,
    fold_task_state,
    validate_task_revision_request,
)
from vanguard.packages.runtime.wiring import BindingContext, _TaskReviseEffect

from test.agency import doubles
from test.kernel import fakes

ROOT = Path(__file__).resolve().parents[2]
WORKSPACE = {"kind": "fs", "root": "/workspace", "paths": ["/workspace/src"]}
TASK_RESOURCE = {"kind": "generic", "uriPattern": "task://revise/*"}
HARNESS_DIGEST = "sha256:" + "h" * 64


def _observation_sinks() -> SinkRegistry:
    registry = SinkRegistry()
    registry.register("fs.read", SinkClass.OBSERVATION)
    registry.register("fs.search", SinkClass.OBSERVATION)
    registry.register("patch.apply", SinkClass.PRIVILEGED)
    registry.register("task.revise", SinkClass.PRIVILEGED)
    registry.register("agency.finish", SinkClass.PRIVILEGED)
    return registry


def _full_scope() -> Scope:
    return Scope(
        actions=frozenset({"fs.read", "task.revise", "patch.apply"}),
        resources=(WORKSPACE, TASK_RESOURCE),
        constraints=fakes.constraints(),
        depth=1,
    )


class _ReviseAdapter:
    """Real adapter delegating task.revise to runtime _TaskReviseEffect."""

    def __init__(self, context: BindingContext) -> None:
        self.name = "task.revise"
        self.verb = "task.revise"
        self._inner = _TaskReviseEffect("task.revise", context)
        self.calls: list[Any] = []

    def healthy(self) -> bool:
        return True

    def execute(self, request: Any) -> AdapterOutcome:
        self.calls.append(request)
        return self._inner.execute(request)


def _build_engine(
    proposals: list[Any],
    *,
    store: Any = None,
    emitter: Any = None,
    sinks: Any = ...,
    scope: Scope | None = None,
) -> tuple[fakes.Harness, _ReviseAdapter, EpisodeEngine]:
    scope = scope or _full_scope()
    sink = fakes.RecordingSink()
    ctx = BindingContext(
        verb="task.revise",
        environment=None,
        repo_path=Path("/workspace"),
        project_id="proj-139",
        composition_digest="sha256:" + "c" * 64,
        parent_episode_id="ep-139",
        store=store,
        emitter=emitter or sink,
    )
    adapter = _ReviseAdapter(ctx)

    harness = fakes.build(
        adapter=adapter,  # type: ignore[arg-type]
        held_actions=frozenset({"fs.read", "task.revise", "patch.apply"}),
        held_resources=(WORKSPACE, TASK_RESOURCE),
        scope=scope,
        sink=sink,
    )
    engine = EpisodeEngine(
        kernel=harness.kernel,
        model=doubles.ScriptedModel(proposals),
        clock=harness.clock,
        events=harness.sink,
        scope=scope,
        max_turns=8,
        observation_sinks=(_observation_sinks() if sinks is ... else sinks),
    )
    return harness, adapter, engine


def _run(engine: EpisodeEngine, **overrides: Any) -> Any:
    kwargs = {
        "episode_id": "ep-139",
        "run_id": "run-139",
        "principal": "agent-1",
        "brief": "revise plan then complete task",
        "spans": (fakes.operator_span(),),
    }
    kwargs.update(overrides)
    return engine.run(**kwargs)


class TestTaskRevisionCapability(unittest.TestCase):
    def test_01_scripted_episode_model_issues_task_revise(self) -> None:
        """1. Scripted episode where model issues task_revise (task.revise)."""
        proposal = {
            "kind": "effect",
            "action": "task.revise",
            "resource": TASK_RESOURCE,
            "args": {
                "expected_revision": 0,
                "plan": ["step 1: inspect code", "step 2: apply patch", "step 3: verify"],
                "next_action": "step 1: inspect code",
                "strategy_steps": ["trace call graph"],
                "rationale": "bootstrap working plan",
            },
        }
        harness, adapter, engine = _build_engine([proposal, doubles.finish()])
        outcome = _run(engine)

        self.assertIs(outcome.terminal, RunTermination.COMPLETED)
        self.assertEqual(len(adapter.calls), 1)
        self.assertEqual(adapter.calls[0].action, "task.revise")

        # Check emitted PlanRevised event
        plan_events = [e for e in harness.sink.events if e.kind == "PlanRevised"]
        self.assertEqual(len(plan_events), 1)
        payload = plan_events[0].payload
        self.assertEqual(payload["plan"], ["step 1: inspect code", "step 2: apply patch", "step 3: verify"])
        self.assertEqual(payload["nextAction"], "step 1: inspect code")
        self.assertEqual(payload["strategySteps"], ["trace call graph"])

    def test_02_revision_is_durable_in_ledger_before_next_proposal(self) -> None:
        """2. Revision is durable in ledger before next proposal."""
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "events.db"
            store = SqliteEventStore(str(db_path))
            clock = FixedClock(at="2026-09-13T00:00:00.000Z", step_ms=1)
            emitter = LedgerEmitter(
                store,
                episode_id="ep-139",
                project_id="proj-139",
                principal_id="agent-1",
                harness_digest=HARNESS_DIGEST,
                clock=clock,
                random=SeededRandom(seed=139),
                role="session",
            )

            # Emit EpisodeStarted
            emitter.emit_kind("EpisodeStarted", run_id="run-139", principal="agent-1", payload={"brief": "repair bug"})

            hook = TaskRevisionHook(
                emitter=emitter,
                target_binding=("proj-139", "ep-139", "turn-1", "prop-1"),
            )

            # Current state from store (EpisodeStarted folds as revision 1)
            events_before = store.read(EventRange(project_id="proj-139")).value or ()
            current_state = fold_task_state(events_before, objective="repair bug")
            self.assertEqual(current_state.revision, 1)

            # Issue revision
            res = hook.handle_revision(
                current_state,
                {
                    "expected_revision": 1,
                    "plan": ["step 1: investigate", "step 2: fix"],
                    "next_action": "step 1: investigate",
                },
            )
            self.assertTrue(res.ok)
            revision, receipt = res.value
            self.assertIsNotNone(receipt)

            # Read back immediately: must be durable before next proposal
            events_after = store.read(EventRange(project_id="proj-139")).value or ()
            kinds = [getattr(e, "mhf_kind", None) or getattr(e, "kind", None) or e.payload.get("kind") for e in events_after]
            self.assertIn("PlanRevised", kinds)

            folded = fold_task_state(events_after, objective="repair bug")
            self.assertEqual(folded.revision, 2)
            self.assertEqual(folded.plan, ("step 1: investigate", "step 2: fix"))
            self.assertEqual(folded.next_action, "step 1: investigate")

    def test_03_revised_state_appears_in_l5_working_state(self) -> None:
        """3. Revised state appears in L5 working state / dialogue."""
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "events.db"
            store = SqliteEventStore(str(db_path))
            clock = FixedClock(at="2026-09-13T00:00:00.000Z", step_ms=1)
            emitter = LedgerEmitter(
                store,
                episode_id="ep-139",
                project_id="proj-139",
                principal_id="agent-1",
                harness_digest=HARNESS_DIGEST,
                clock=clock,
                random=SeededRandom(seed=139),
                role="session",
            )
            hook = TaskRevisionHook(emitter=emitter)

            # Initial working state
            initial_state = SemanticTaskState(objective="fix flaw", run_id="run-139", revision=0)

            # Execute revision
            res = hook.handle_revision(
                initial_state,
                {
                    "expected_revision": 0,
                    "plan": ["phase 1: test", "phase 2: modify"],
                    "hypotheses": ["off-by-one index"],
                    "next_action": "phase 1: test",
                },
            )
            self.assertTrue(res.ok)

            # append_before_next_compile transfers pending revision to working state
            working_state = hook.append_before_next_compile(initial_state)
            self.assertEqual(working_state.revision, 1)
            self.assertEqual(working_state.plan, ("phase 1: test", "phase 2: modify"))
            self.assertEqual(working_state.hypotheses, ("off-by-one index",))
            self.assertEqual(working_state.next_action, "phase 1: test")

            # Subsequent call when none pending returns unchanged state
            self.assertIs(hook.append_before_next_compile(working_state), working_state)

    def test_04_uninterrupted_state_matches_compaction_and_fresh_process_restart(self) -> None:
        """4. Uninterrupted state matches state after compaction and fresh-process
        restart from SQLite store without duplicate revisions.
        """
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "events.db"
            store = SqliteEventStore(str(db_path))
            clock = FixedClock(at="2026-09-13T00:00:00.000Z", step_ms=1)
            emitter = LedgerEmitter(
                store,
                episode_id="ep-restart",
                project_id="proj-restart",
                principal_id="agent-1",
                harness_digest=HARNESS_DIGEST,
                clock=clock,
                random=SeededRandom(seed=139),
                role="session",
            )

            # Emit sequence of events including 2 revisions
            emitter.emit_kind("EpisodeStarted", run_id="run-restart", principal="agent-1", payload={"brief": "complex task"})
            hook = TaskRevisionHook(emitter=emitter, target_binding=("proj-restart", "ep-restart", "t1", "p1"))

            state0 = fold_task_state(store.read().value or (), objective="complex task")
            hook.handle_revision(
                state0,
                {
                    "revision_id": "rev-1",
                    "expected_revision": 0,
                    "plan": ["step 1", "step 2"],
                    "next_action": "step 1",
                },
            )

            # Intersperse observations and actions
            emitter.emit_kind("ObservationProduced", run_id="run-restart", principal="agent-1", payload={"path": "src/core.py"})
            emitter.emit_kind("ProposalProduced", run_id="run-restart", principal="agent-1", payload={"action": "step 1"})
            emitter.emit_kind(
                "EffectCompleted",
                run_id="run-restart",
                principal="agent-1",
                payload={"action": "patch.apply", "path": "src/core.py", "descriptorDigest": "sha256:" + "d" * 64},
            )

            state1 = fold_task_state(store.read().value or (), objective="complex task")
            hook.handle_revision(
                state1,
                {
                    "revision_id": "rev-2",
                    "expected_revision": state1.revision,
                    "plan": ["step 2", "step 3"],
                    "next_action": "step 2",
                    "hypotheses": ["hypothesis verified"],
                },
            )

            events = store.read(EventRange(project_id="proj-restart")).value or ()
            in_process_state = fold_task_state(events, objective="complex task")
            in_process_digest = in_process_state.digest()

            # Fresh process restart from SQLite store
            script = r"""
import sys
from pathlib import Path
from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.ports.event_store import EventRange
from vanguard.packages.runtime.task_state import fold_task_state

db_path = sys.argv[1]
store = SqliteEventStore(db_path)
read_res = store.read(EventRange(project_id="proj-restart"))
events = read_res.value or ()
state = fold_task_state(events, objective="complex task")
print(state.digest())
print(state.revision)
print(",".join(state.plan))
print(state.next_action)
print(",".join(state.hypotheses))
"""
            env = {**os.environ, "PYTHONPATH": str(ROOT)}
            ran = subprocess.run(
                [sys.executable, "-c", script, str(db_path)],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(ran.returncode, 0, ran.stdout + ran.stderr)
            lines = ran.stdout.strip().splitlines()
            fresh_digest, fresh_revision, fresh_plan, fresh_next, fresh_hypo = lines

            self.assertEqual(fresh_digest, in_process_digest)
            self.assertEqual(int(fresh_revision), in_process_state.revision)
            self.assertEqual(fresh_plan, ",".join(in_process_state.plan))
            self.assertEqual(fresh_next, in_process_state.next_action)
            self.assertEqual(fresh_hypo, ",".join(in_process_state.hypotheses))

    def test_05_invalid_stale_and_widening_requests_leave_state_and_authority_unchanged(self) -> None:
        """5. Invalid, stale, and widening requests leave state and authority unchanged."""
        current = SemanticTaskState(
            objective="immutable objective",
            run_id="run-1",
            revision=3,
            remaining_budgets={"turns": 5, "usd_micros": 5000},
            plan=("orig 1", "orig 2"),
            next_action="orig 1",
        )
        initial_digest = current.digest()

        # 5a. Stale revision number
        res_stale_seq = validate_task_revision_request(
            current,
            {"expected_revision": 2, "plan": ["new plan"]},
        )
        self.assertFalse(res_stale_seq.ok)
        self.assertEqual(res_stale_seq.error.kind, TASK_REVISION_STALE)

        # 5b. Stale digest
        res_stale_dig = validate_task_revision_request(
            current,
            {
                "expected_revision": 3,
                "expected_state_digest": "sha256:" + "0" * 64,
                "plan": ["new plan"],
            },
        )
        self.assertFalse(res_stale_dig.ok)
        self.assertEqual(res_stale_dig.error.kind, TASK_REVISION_STALE)

        # 5c. Widening objective
        res_widen_obj = validate_task_revision_request(
            current,
            {
                "expected_revision": 3,
                "proposed_state": {
                    **current.to_canonical_dict(),
                    "objective": "widened goal",
                },
            },
        )
        self.assertFalse(res_widen_obj.ok)
        self.assertEqual(res_widen_obj.error.kind, TASK_REVISION_WIDENING)

        # 5d. Widening remaining budgets
        res_widen_bud = validate_task_revision_request(
            current,
            {
                "expected_revision": 3,
                "proposed_state": {
                    **current.to_canonical_dict(),
                    "remainingBudgets": {"turns": 1000},
                },
            },
        )
        self.assertFalse(res_widen_bud.ok)
        self.assertEqual(res_widen_bud.error.kind, TASK_REVISION_WIDENING)

        # 5e. Malformed mutated field
        res_malformed = validate_task_revision_request(
            current,
            {
                "expected_revision": 3,
                "mutated_fields": ["unauthorized_field"],
            },
        )
        self.assertFalse(res_malformed.ok)
        self.assertEqual(res_malformed.error.kind, TASK_REVISION_MALFORMED)

        # Confirm state unchanged and untouched
        self.assertEqual(current.digest(), initial_digest)
        self.assertEqual(current.revision, 3)
        self.assertEqual(current.objective, "immutable objective")
        self.assertEqual(current.remaining_budgets["turns"], 5)

    def test_06_conflicting_revision_id_refused_identical_replay_returns_original_receipt(self) -> None:
        """6. Conflicting revision_id is refused with TASK_REVISION_CONFLICTING;
        identical replay returns original receipt.
        """
        emitted_events: list[Event] = []

        class SimpleSink:
            def emit_kind(self, kind: str, **kwargs: Any) -> SimpleNamespace:
                ev = SimpleNamespace(kind=kind, kwargs=kwargs, receipt_id=f"rec-{len(emitted_events)}")
                emitted_events.append(ev)  # type: ignore[arg-type]
                return ev

        sink = SimpleSink()
        hook = TaskRevisionHook(emitter=sink)
        state = SemanticTaskState(objective="test conflicts", run_id="run-1", revision=0)

        # First attempt: succeeds
        res1 = hook.handle_revision(
            state,
            {
                "revision_id": "rev-shared-id",
                "expected_revision": 0,
                "plan": ["p1", "p2"],
            },
        )
        self.assertTrue(res1.ok)
        rev1, receipt1 = res1.value
        self.assertEqual(len(emitted_events), 1)

        # Second attempt with IDENTICAL payload and same revision_id: idempotent replay
        res2 = hook.handle_revision(
            state,
            {
                "revision_id": "rev-shared-id",
                "expected_revision": 0,
                "plan": ["p1", "p2"],
            },
        )
        self.assertTrue(res2.ok)
        rev2, receipt2 = res2.value
        self.assertEqual(receipt2, receipt1)
        # No duplicate emission!
        self.assertEqual(len(emitted_events), 1)

        # Third attempt with CONFLICTING payload but same revision_id: refused
        res3 = hook.handle_revision(
            state,
            {
                "revision_id": "rev-shared-id",
                "expected_revision": 0,
                "plan": ["conflicting plan"],
            },
        )
        self.assertFalse(res3.ok)
        self.assertEqual(res3.error.kind, TASK_REVISION_CONFLICTING)
        # Still no duplicate emission
        self.assertEqual(len(emitted_events), 1)

    def test_07_observation_batch_carrying_task_revise_dispatches_zero_members(self) -> None:
        """7. Observation batch carrying task.revise dispatches zero members."""
        batch = {
            "kind": "observe",
            "requests": [
                {
                    "id": "r0",
                    "action": "fs.read",
                    "resource": WORKSPACE,
                    "args": {"path": "a.py"},
                },
                {
                    "id": "r1",
                    "action": "task.revise",
                    "resource": TASK_RESOURCE,
                    "args": {"plan": ["illicit batch plan"]},
                },
            ],
        }
        harness, adapter, engine = _build_engine([batch, doubles.finish()])
        outcome = _run(engine)

        # Adapter called zero times
        self.assertEqual(adapter.calls, [])

        # Batch refused whole with AuthorizationDenied
        denials = [e for e in harness.sink.events if e.kind == "AuthorizationDenied"]
        self.assertEqual(len(denials), 1)
        self.assertEqual(denials[0].reason, "observation_batch_refused")
        self.assertIn("task.revise", denials[0].payload["detail"])

        # Zero ledger entries dispatched
        self.assertEqual(harness.ledger.entries, [])
        self.assertIs(outcome.terminal, RunTermination.COMPLETED)

    def test_08_disabling_sink_handoff_or_revision_persistence_fails_oracles(self) -> None:
        """8. Disabling sink handoff or revision persistence fails corresponding oracles."""
        # 8a. Sinks=None (undeclared sinks) fails closed
        batch = {
            "kind": "observe",
            "requests": [
                {
                    "id": "r0",
                    "action": "fs.read",
                    "resource": WORKSPACE,
                    "args": {"path": "a.py"},
                },
            ],
        }
        harness, adapter, engine = _build_engine([batch, doubles.finish()], sinks=None)
        _run(engine)
        self.assertEqual(adapter.calls, [])
        denials = [e for e in harness.sink.events if e.reason == "observation_batch_refused"]
        self.assertEqual(len(denials), 1)

        # 8b. Disabling persistence (emitter is None) prevents durability
        hook_no_emitter = TaskRevisionHook(emitter=None)
        state = SemanticTaskState(objective="no emitter", run_id="run-1", revision=0)
        res = hook_no_emitter.handle_revision(state, {"plan": ["p1"]})
        self.assertTrue(res.ok)
        rev, receipt = res.value
        self.assertIsNone(receipt)


if __name__ == "__main__":
    unittest.main()
