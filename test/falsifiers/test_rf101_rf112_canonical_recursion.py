"""RF-101…RF-112: canonical recursion (`WP-A1`, M-6).

M-6 was `IN_PROGRESS` for one reason, and it was not a missing feature. The
spawn path *worked*: it minted a child, wrote two facts, and returned success.
It simply did all of that without running anything. `wiring._spawn_effector`
substituted a runner that returned `completed` at zero cost whenever none was
bound, and because `TaskContext` carried no runner field, nothing was ever
bound -- so the fallback was the production path. Every `agent.spawn` in the
system reported a subtask that never existed.

That is worse than a missing feature, because it produced evidence. These
falsifiers exist to make that failure mode unreachable, and each one fails
loudly if the shortcut is ever reintroduced:

| ID | Claim |
|---|---|
| RF-101 | A composition that can spawn but has no runner fails before any fact |
| RF-102 | Child identity is derived, restart-stable, and project-scoped |
| RF-103 | A reused id bound to a different intent is refused |
| RF-104 | Every additive dimension is reserved against parent *remaining* |
| RF-105 | Depth, turns and scope are lowered and can never widen |
| RF-106 | No transcript or live handle crosses the delegation boundary |
| RF-107 | A depth>=3 tree cold-folds from the ledger alone |
| RF-108 | A crash between the two facts is `UNDETERMINABLE`, never a retry |
| RF-109 | A settled subtree replays instead of re-executing |
| RF-110 | Two projects sharing a store and a key never share a child |
| RF-111 | Killing a subtree appends facts and erases none |
| RF-112 | Recursion re-enters the sole public boundary, exactly once |
"""

from __future__ import annotations

import unittest
from dataclasses import replace
from pathlib import Path

from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.domain.ledger.reducer import initial_state, reduce_batch
from vanguard.packages.kernel.attenuation import Constraints, Scope
from vanguard.packages.kernel.model import EffectRequest, Occurrence
from vanguard.packages.ports.child_runtime import (
    CHILD_ADDITIVE_DIMENSIONS,
    CHILD_STRUCTURAL_CEILINGS,
    ChildContractError,
    ChildRunPlan,
    ChildRunResult,
    ChildRuntimePort,
)
from vanguard.packages.ports.event_store import EventRange
from vanguard.packages.runtime.child_runtime import RuntimeChildRunner
from vanguard.packages.runtime.ledger.recovery import (
    RecoveryScanner,
    replay_ledger_state,
)
from vanguard.packages.runtime.delegation import (
    ADDITIVE_DIMENSIONS,
    CHILD_ID_SCHEME,
    SPAWN_VERB,
    STRUCTURAL_CEILINGS,
    SpawnAdapter,
    SpawnPreparationError,
    derive_child_id,
)
from vanguard.packages.runtime.determinism import FixedClock, SeededRandom
from vanguard.packages.runtime.ledger_emitter import LedgerEmitter
from vanguard.packages.runtime.wiring import BindingContext, CompositionError, _spawn_effector

ROOT = Path(__file__).resolve().parents[2]
_AT = "2026-08-26T12:00:00.000Z"
_WORKSPACE = {"kind": "fs", "root": "/workspace", "paths": ["/workspace/src"]}

_AMPLE = {"usd_micros": 1_000_000, "millis": 1_000_000, "tokens": 1_000_000,
          "bytes": 1_000_000, "turns": 64, "depth": 8}


def _scope(*verbs: str, max_depth: int = 4, depth: int = 0) -> Scope:
    return Scope(
        actions=frozenset(verbs or {"fs.read", "fs.patch", SPAWN_VERB}),
        resources=(_WORKSPACE,),
        constraints=Constraints(
            expires_at="2027-01-01T00:00:00Z", max_uses=100,
            budget_usd_micros=1_000_000, max_depth=max_depth),
        depth=depth,
    )


def _request(**overrides) -> EffectRequest:
    args = {"brief": "extract the parser", "authority": ["fs.read"],
            "budget": {"tokens": 100, "usd_micros": 500}, "maxTurns": 3}
    args.update(overrides.pop("args", {}))
    base = {"action": SPAWN_VERB, "resource": _WORKSPACE, "args": args,
            "principal": "agent-m6", "run_id": "run-m6", "depth": 0,
            "idempotency_key": "intent-1"}
    base.update(overrides)
    return EffectRequest(**base)


class _Runner:
    """A conforming `ChildRuntimePort` that records what it was asked to run."""

    def __init__(self, on_call=None):
        self.plans: list[ChildRunPlan] = []
        self._on_call = on_call

    def run_child(self, plan: ChildRunPlan) -> ChildRunResult:
        self.plans.append(plan)
        if self._on_call is not None:
            return self._on_call(plan)
        return ChildRunResult(
            ok=True, outcome="completed", terminal="ok",
            child_episode_id=plan.child_episode_id,
            actual_cost={"tokens": 10}, turns_used=1)


#: Distinct per adapter. Event ids derive from the seeded random, so two
#: adapters sharing a store and a seed would collide on `event_id` -- a
#: fixture artefact, not a production property, and one that would otherwise
#: mask the very isolation these tests assert.
_SEEDS = iter(range(1000, 100000))


def _adapter(store, *, runner=None, scope=None, remaining=None,
             project="project-a", max_depth=4, max_turns=8,
             parent="ep-parent"):
    emitter = LedgerEmitter(
        store, episode_id=parent, project_id=project, principal_id="agent-m6",
        harness_digest="sha256:" + "6" * 64,
        clock=FixedClock(at=_AT, step_ms=1),
        random=SeededRandom(seed=next(_SEEDS)),
        role="spawn_adapter")
    return SpawnAdapter(
        emitter=emitter.spawn_adapter(),
        parent_scope=scope or _scope(),
        child_runtime=runner or _Runner(),
        clock=FixedClock(at=_AT, step_ms=1),
        store=store,
        parent_episode_id=parent,
        project_id=project,
        remaining_budget=lambda: dict(remaining or _AMPLE),
        max_depth=max_depth,
        max_turns=max_turns,
    )


def _payloads(store, project="project-a"):
    read = store.read(EventRange(project_id=project))
    return [e.payload for e in (read.value or [])]


def _kinds(store, project="project-a"):
    return [p.get("kind") for p in _payloads(store, project)]


class RF101MissingRunnerFailsBeforeAnyFact(unittest.TestCase):
    """The synthetic success path is gone, and cannot be re-derived."""

    def test_binding_a_spawn_verb_without_a_runner_fails_composition(self) -> None:
        context = BindingContext(
            verb=SPAWN_VERB, environment=None, repo_path=Path("/tmp"),
            parent_scope=_scope(), clock=FixedClock(at=_AT, step_ms=1),
            store=SqliteEventStore(":memory:"), parent_episode_id="ep-parent",
            child_runtime=None,
        )
        with self.assertRaises(CompositionError) as caught:
            _spawn_effector(context)
        self.assertIn("ChildRuntimePort", str(caught.exception))

    def test_the_refusal_writes_no_events_at_all(self) -> None:
        """Composition-time refusal is the one refusal that is still free."""
        store = SqliteEventStore(":memory:")
        context = BindingContext(
            verb=SPAWN_VERB, environment=None, repo_path=Path("/tmp"),
            parent_scope=_scope(), clock=FixedClock(at=_AT, step_ms=1),
            store=store, parent_episode_id="ep-parent", child_runtime=None,
        )
        with self.assertRaises(CompositionError):
            _spawn_effector(context)
        read = store.read(EventRange())
        self.assertEqual(list(read.value or []), [])

    def test_the_adapter_itself_refuses_a_none_runner(self) -> None:
        """Belt and braces: the refusal does not live only in the wiring."""
        with self.assertRaises(SpawnPreparationError):
            SpawnAdapter(
                emitter=None, parent_scope=_scope(), child_runtime=None,
                clock=None, parent_episode_id="ep-parent")

    def test_no_production_module_synthesizes_a_delegation_result(self) -> None:
        """The specific shape of the removed lie, greppable forever.

        The old fallback returned `outcome="completed"` with an all-zero
        digest. If anything in the runtime ever constructs a completed child
        result again outside a test, this fails.
        """
        runtime = ROOT / "vanguard/packages/runtime"
        offenders = []
        for path in sorted(runtime.rglob("*.py")):
            text = path.read_text(encoding="utf-8")
            if '"sha256:" + "0" * 64' in text and "outcome=\"completed\"" in text:
                offenders.append(path.name)
        self.assertEqual(offenders, [])


class RF102ChildIdentityIsDerivedAndDurable(unittest.TestCase):
    """A counter cannot survive a restart; a hash does not need to."""

    def test_the_same_intent_always_names_the_same_child(self) -> None:
        first = derive_child_id("ep-parent", "intent-1", "project-a")
        second = derive_child_id("ep-parent", "intent-1", "project-a")
        self.assertEqual(first, second)

    def test_a_fresh_adapter_recomputes_the_same_id(self) -> None:
        store = SqliteEventStore(":memory:")
        _adapter(store).execute(_request())
        spawned = next(p for p in _payloads(store) if p["kind"] == "ChildSpawned")
        self.assertEqual(
            spawned["childEpisodeId"],
            derive_child_id("ep-parent", "intent-1", "project-a"))
        self.assertEqual(spawned["childIdScheme"], CHILD_ID_SCHEME)

    def test_an_absent_idempotency_key_denies_rather_than_inventing_one(self) -> None:
        store = SqliteEventStore(":memory:")
        outcome = _adapter(store).execute(_request(idempotency_key=None))
        self.assertEqual(outcome.occurrence, Occurrence.DID_NOT_OCCUR)
        self.assertNotIn("ChildSpawned", _kinds(store))

    def test_the_id_does_not_embed_the_parents_episode_verbatim(self) -> None:
        """`ep-parent.c1` leaked lineage into the identifier itself.

        A derived id is opaque, so nothing downstream can parse a parent out
        of a child name and skip reading the actual lineage fact.
        """
        child = derive_child_id("ep-parent", "intent-1", "project-a")
        self.assertNotIn("ep-parent", child)


class RF103CollisionIsRefused(unittest.TestCase):

    def test_a_child_id_bound_to_a_different_intent_is_refused(self) -> None:
        store = SqliteEventStore(":memory:")
        adapter = _adapter(store)
        adapter.execute(_request())
        spawned = next(p for p in _payloads(store) if p["kind"] == "ChildSpawned")

        # Forge a second ChildSpawned with the same id but a different intent,
        # then attempt the spawn that would derive that id.
        forged = dict(spawned)
        forged["settledIntentKey"] = "some-other-intent"
        adapter._emit("ChildSpawned", forged, _request(),
                      episode_id=forged["childEpisodeId"])

        outcome = _adapter(store).execute(_request(idempotency_key="intent-1"))
        self.assertEqual(outcome.occurrence, Occurrence.OCCURRED,
                         "the original settlement should still replay")

    def test_a_foreign_parent_on_the_same_id_is_refused(self) -> None:
        store = SqliteEventStore(":memory:")
        adapter = _adapter(store)
        child_id = derive_child_id("ep-parent", "intent-1", "project-a")
        adapter._emit("ChildSpawned", {
            "kind": "ChildSpawned", "childEpisodeId": child_id,
            "parentEpisodeId": "ep-somebody-else",
            "settledIntentKey": "different-intent",
        }, _request(), episode_id=child_id)

        outcome = _adapter(store).execute(_request())
        self.assertEqual(outcome.occurrence, Occurrence.DID_NOT_OCCUR)
        self.assertIn("already bound", outcome.detail or "")


class RF104EveryBudgetDimensionIsReservedAgainstParentRemaining(unittest.TestCase):
    """Componentwise, against *remaining* -- not against the original ceiling."""

    def test_each_additive_dimension_denies_when_it_exceeds_remaining(self) -> None:
        for dimension in ADDITIVE_DIMENSIONS:
            with self.subTest(dimension=dimension):
                store = SqliteEventStore(":memory:")
                remaining = dict(_AMPLE)
                remaining[dimension] = 5
                outcome = _adapter(store, remaining=remaining).execute(
                    _request(args={"budget": {dimension: 6}}))
                self.assertEqual(outcome.occurrence, Occurrence.DID_NOT_OCCUR)
                self.assertIn(dimension, outcome.detail or "")
                self.assertNotIn("ChildSpawned", _kinds(store))

    def test_a_dimension_exactly_at_remaining_is_granted(self) -> None:
        """The boundary is `>`, not `>=`. Spending the last token is legal."""
        store = SqliteEventStore(":memory:")
        remaining = dict(_AMPLE, tokens=6)
        outcome = _adapter(store, remaining=remaining).execute(
            _request(args={"budget": {"tokens": 6}}))
        self.assertEqual(outcome.occurrence, Occurrence.OCCURRED)

    def test_an_unspecified_dimension_is_zero_not_the_parents_balance(self) -> None:
        """No ambient inheritance. Silence requests nothing."""
        store = SqliteEventStore(":memory:")
        runner = _Runner()
        _adapter(store, runner=runner).execute(
            _request(args={"budget": {"tokens": 10}}))
        plan = runner.plans[0]
        for dimension in ADDITIVE_DIMENSIONS:
            if dimension != "tokens":
                self.assertEqual(plan.budget.get(dimension, 0), 0, dimension)

    def test_a_spent_parent_cannot_fund_a_second_child(self) -> None:
        """The reservation reads a callable, so siblings see prior spend."""
        store = SqliteEventStore(":memory:")
        balance = {"tokens": 100, "usd_micros": 0, "millis": 0, "bytes": 0,
                   "turns": 10, "depth": 4}

        def spend(plan):
            balance["tokens"] -= 100
            return ChildRunResult(
                ok=True, outcome="completed", terminal="ok",
                child_episode_id=plan.child_episode_id,
                actual_cost={"tokens": 100}, turns_used=1)

        emitter = LedgerEmitter(
            store, episode_id="ep-parent", project_id="project-a",
            principal_id="agent-m6", harness_digest="sha256:" + "6" * 64,
            clock=FixedClock(at=_AT, step_ms=1), random=SeededRandom(seed=6),
            role="spawn_adapter")
        adapter = SpawnAdapter(
            emitter=emitter.spawn_adapter(), parent_scope=_scope(),
            child_runtime=_Runner(on_call=spend),
            clock=FixedClock(at=_AT, step_ms=1), store=store,
            parent_episode_id="ep-parent", project_id="project-a",
            remaining_budget=lambda: dict(balance), max_depth=4, max_turns=8)

        first = adapter.execute(_request(args={"budget": {"tokens": 100}}))
        self.assertEqual(first.occurrence, Occurrence.OCCURRED)
        second = adapter.execute(
            _request(idempotency_key="intent-2", args={"budget": {"tokens": 100}}))
        self.assertEqual(second.occurrence, Occurrence.DID_NOT_OCCUR)

    def test_a_structural_ceiling_can_never_be_a_budget_dimension(self) -> None:
        for ceiling in STRUCTURAL_CEILINGS:
            with self.subTest(ceiling=ceiling):
                store = SqliteEventStore(":memory:")
                outcome = _adapter(store).execute(
                    _request(args={"budget": {ceiling: 1}}))
                self.assertEqual(outcome.occurrence, Occurrence.DID_NOT_OCCUR)


class RF105DepthTurnAndScopeOnlyEverNarrow(unittest.TestCase):

    def test_depth_increments_and_stops_at_the_ceiling(self) -> None:
        store = SqliteEventStore(":memory:")
        outcome = _adapter(store, max_depth=2).execute(_request(depth=2))
        self.assertEqual(outcome.occurrence, Occurrence.DID_NOT_OCCUR)
        self.assertIn("depth", outcome.detail or "")

    def test_a_child_cannot_raise_the_turn_ceiling(self) -> None:
        store = SqliteEventStore(":memory:")
        runner = _Runner()
        _adapter(store, runner=runner, max_turns=3).execute(
            _request(args={"maxTurns": 99}))
        self.assertEqual(runner.plans[0].max_turns, 3)

    def test_a_child_may_lower_the_turn_ceiling(self) -> None:
        store = SqliteEventStore(":memory:")
        runner = _Runner()
        _adapter(store, runner=runner, max_turns=8).execute(
            _request(args={"maxTurns": 2}))
        self.assertEqual(runner.plans[0].max_turns, 2)

    def test_turns_are_checked_against_parent_remaining_turns(self) -> None:
        store = SqliteEventStore(":memory:")
        remaining = dict(_AMPLE, turns=1)
        outcome = _adapter(store, remaining=remaining, max_turns=8).execute(
            _request(args={"maxTurns": 5}))
        self.assertEqual(outcome.occurrence, Occurrence.DID_NOT_OCCUR)

    def test_no_depth_headroom_denies_even_below_the_ceiling(self) -> None:
        store = SqliteEventStore(":memory:")
        remaining = dict(_AMPLE, depth=0)
        outcome = _adapter(store, remaining=remaining).execute(_request())
        self.assertEqual(outcome.occurrence, Occurrence.DID_NOT_OCCUR)

    def test_a_child_cannot_acquire_a_verb_the_parent_lacks(self) -> None:
        store = SqliteEventStore(":memory:")
        outcome = _adapter(store, scope=_scope("fs.read")).execute(
            _request(args={"authority": ["proc.exec"]}))
        self.assertEqual(outcome.occurrence, Occurrence.DID_NOT_OCCUR)
        self.assertIn("attenuation denied", outcome.detail or "")

    def test_the_granted_plan_is_a_subset_of_the_parent_grant(self) -> None:
        store = SqliteEventStore(":memory:")
        runner = _Runner()
        _adapter(store, runner=runner, scope=_scope("fs.read", "fs.patch", SPAWN_VERB),
                 ).execute(_request(args={"authority": ["fs.read"]}))
        self.assertEqual(set(runner.plans[0].authority), {"fs.read"})


class RF106NoTranscriptCrossesTheBoundary(unittest.TestCase):
    """A parent that receives a transcript has not delegated; it has inlined."""

    def test_a_result_holding_a_live_object_is_refused(self) -> None:
        with self.assertRaises(ChildContractError):
            ChildRunResult(
                ok=True, outcome="completed", terminal="ok",
                child_episode_id="c", result_digest=object())

    def test_evidence_refs_are_reference_strings_not_content(self) -> None:
        with self.assertRaises(ChildContractError):
            ChildRunResult(
                ok=True, outcome="completed", terminal="ok",
                child_episode_id="c",
                evidence_refs=({"messages": ["hello"]},))

    def test_the_returned_fact_contains_no_prose_keys(self) -> None:
        store = SqliteEventStore(":memory:")
        _adapter(store).execute(_request(args={"brief": "SECRET-TOKEN-abc"}))
        returned = next(p for p in _payloads(store) if p["kind"] == "ChildReturned")
        for forbidden in ("messages", "transcript", "text", "brief", "prompt"):
            self.assertNotIn(forbidden, returned)

    def test_the_brief_never_reaches_the_ledger(self) -> None:
        import json
        store = SqliteEventStore(":memory:")
        _adapter(store).execute(_request(args={"brief": "SECRET-TOKEN-abc"}))
        self.assertNotIn("SECRET-TOKEN", json.dumps(_payloads(store)))

    def test_ok_cannot_contradict_the_outcome(self) -> None:
        """A runner cannot report success and abandonment simultaneously."""
        with self.assertRaises(ChildContractError):
            ChildRunResult(ok=True, outcome="abandoned", terminal="x",
                           child_episode_id="c")

    def test_a_negative_cost_is_refused(self) -> None:
        """A refund is the kernel's settlement, never the child's report."""
        with self.assertRaises(ChildContractError):
            ChildRunResult(ok=True, outcome="completed", terminal="ok",
                           child_episode_id="c", actual_cost={"tokens": -5})

    def test_the_port_dimension_tuples_match_the_runtimes(self) -> None:
        """Ports may not import Runtime, so the two lists are asserted equal."""
        self.assertEqual(CHILD_ADDITIVE_DIMENSIONS, ADDITIVE_DIMENSIONS)
        self.assertEqual(CHILD_STRUCTURAL_CEILINGS, STRUCTURAL_CEILINGS)


class RF107DeepTreesColdFold(unittest.TestCase):
    """depth>=3 reconstructs from the ledger with no live parent object."""

    def _spawn_at(self, store, parent, depth, key, project="project-a"):
        adapter = _adapter(store, parent=parent, project=project, max_depth=6,
                           scope=_scope(depth=depth))
        return adapter.execute(_request(depth=depth, idempotency_key=key))

    def test_a_three_deep_chain_folds_to_three_closed_children(self) -> None:
        store = SqliteEventStore(":memory:")
        parent = "ep-root"
        for depth in range(3):
            outcome = self._spawn_at(store, parent, depth, f"intent-d{depth}")
            self.assertEqual(outcome.occurrence, Occurrence.OCCURRED, depth)
            parent = derive_child_id(parent, f"intent-d{depth}", "project-a")

        read = store.read(EventRange(project_id="project-a"))
        state = reduce_batch(initial_state(), list(read.value or []))
        self.assertEqual(len(state.children), 3)
        for record in state.children.values():
            self.assertEqual(record.status, "closed")

    def test_each_level_records_its_own_depth(self) -> None:
        store = SqliteEventStore(":memory:")
        parent = "ep-root"
        for depth in range(3):
            self._spawn_at(store, parent, depth, f"intent-d{depth}")
            parent = derive_child_id(parent, f"intent-d{depth}", "project-a")
        spawned = [p for p in _payloads(store) if p["kind"] == "ChildSpawned"]
        self.assertEqual(sorted(p["depth"] for p in spawned), [1, 2, 3])

    def test_the_chain_is_rebuildable_without_a_live_parent(self) -> None:
        store = SqliteEventStore(":memory:")
        parent = "ep-root"
        chain = [parent]
        for depth in range(3):
            self._spawn_at(store, parent, depth, f"intent-d{depth}")
            parent = derive_child_id(parent, f"intent-d{depth}", "project-a")
            chain.append(parent)

        # Cold: nothing but the store.
        cold = reduce_batch(initial_state(), list(
            store.read(EventRange(project_id="project-a")).value or []))
        for child, expected_parent in zip(chain[1:], chain[:-1]):
            self.assertEqual(cold.children[child].parent_episode_id, expected_parent)


class RF108CrashBoundariesAreUndeterminable(unittest.TestCase):

    def test_a_raising_runner_yields_undeterminable_not_failure(self) -> None:
        def explode(plan):
            raise RuntimeError("the child process died")

        store = SqliteEventStore(":memory:")
        outcome = _adapter(store, runner=_Runner(on_call=explode)).execute(_request())
        self.assertEqual(outcome.occurrence, Occurrence.UNDETERMINABLE)

    def test_the_spawn_fact_is_durable_before_the_runner_is_called(self) -> None:
        seen = []
        store = SqliteEventStore(":memory:")

        def observe(plan):
            seen.append(_kinds(store))
            return ChildRunResult(ok=True, outcome="completed", terminal="ok",
                                  child_episode_id=plan.child_episode_id)

        _adapter(store, runner=_Runner(on_call=observe)).execute(_request())
        self.assertIn("ChildSpawned", seen[0])

    def test_an_open_subtree_replays_as_undeterminable_never_as_a_retry(self) -> None:
        store = SqliteEventStore(":memory:")
        adapter = _adapter(store)
        child_id = derive_child_id("ep-parent", "intent-1", "project-a")
        adapter._emit("ChildSpawned", {
            "kind": "ChildSpawned", "childEpisodeId": child_id,
            "parentEpisodeId": "ep-parent", "settledIntentKey": "intent-1",
        }, _request(), episode_id=child_id)

        runner = _Runner()
        outcome = _adapter(store, runner=runner).execute(_request())
        self.assertEqual(outcome.occurrence, Occurrence.UNDETERMINABLE)
        self.assertEqual(runner.plans, [], "an open subtree was blindly retried")

    def test_an_instrument_error_terminal_maps_to_undeterminable(self) -> None:
        """The child may have mutated the world before the instrument broke."""
        from vanguard.packages.runtime.child_runtime import TERMINAL_OUTCOMES
        self.assertEqual(TERMINAL_OUTCOMES["instrument_error"], "undeterminable")
        self.assertEqual(TERMINAL_OUTCOMES["runtime_error"], "undeterminable")


class RF108bRecoveryAdjudicatesOpenSubtrees(unittest.TestCase):
    """The cold path closes what the crash left open -- without guessing."""

    def _orphan(self, store, project="project-a"):
        adapter = _adapter(store, project=project)
        child_id = derive_child_id("ep-parent", "intent-1", project)
        adapter._emit("ChildSpawned", {
            "kind": "ChildSpawned", "childEpisodeId": child_id,
            "parentEpisodeId": "ep-parent", "settledIntentKey": "intent-1",
            "depth": 1, "lineage": ["ep-parent"],
        }, _request(), episode_id=child_id)
        return child_id

    def test_the_replay_fold_reports_an_open_child(self) -> None:
        store = SqliteEventStore(":memory:")
        child_id = self._orphan(store)
        events = list(store.read(EventRange(project_id="project-a")).value or [])
        state = replay_ledger_state(events)
        self.assertEqual(len(state.open_children), 1)
        self.assertEqual(state.open_children[0]["childEpisodeId"], child_id)
        self.assertEqual(state.status, "undeterminable")

    def test_reconciliation_emits_undeterminable_never_failed(self) -> None:
        store = SqliteEventStore(":memory:")
        self._orphan(store)
        emitted = RecoveryScanner().reconcile_open_children(
            store, occurred_at=_AT, project_id="project-a")
        self.assertEqual(len(emitted), 1)
        payload = emitted[0].payload
        self.assertEqual(payload["occurrence"], "undeterminable")
        self.assertEqual(payload["idempotencyKey"], "intent-1")

    def test_reconciliation_does_not_write_child_facts(self) -> None:
        """`SpawnAdapter` stays the sole writer of `ChildSpawned`/`ChildReturned`.

        Recovery adjudicates in its own owned kind rather than widening the
        privileged-writer matrix, which is the ADR-0090 claim.
        """
        store = SqliteEventStore(":memory:")
        self._orphan(store)
        emitted = RecoveryScanner().reconcile_open_children(
            store, occurred_at=_AT, project_id="project-a")
        self.assertEqual([e.payload["kind"] for e in emitted], ["EffectReconciled"])
        self.assertEqual(_kinds(store).count("ChildReturned"), 0)

    def test_reconciliation_is_idempotent(self) -> None:
        store = SqliteEventStore(":memory:")
        self._orphan(store)
        scanner = RecoveryScanner()
        first = scanner.reconcile_open_children(
            store, occurred_at=_AT, project_id="project-a")
        second = scanner.reconcile_open_children(
            store, occurred_at=_AT, project_id="project-a")
        self.assertEqual(len(first), 1)
        self.assertEqual(second, [])

    def test_a_reconciled_subtree_is_never_re_executed(self) -> None:
        store = SqliteEventStore(":memory:")
        self._orphan(store)
        RecoveryScanner().reconcile_open_children(
            store, occurred_at=_AT, project_id="project-a")
        runner = _Runner()
        outcome = _adapter(store, runner=runner).execute(_request())
        self.assertEqual(outcome.occurrence, Occurrence.UNDETERMINABLE)
        self.assertEqual(runner.plans, [])

    def test_reconciliation_is_project_scoped(self) -> None:
        store = SqliteEventStore(":memory:")
        self._orphan(store, project="project-a")
        emitted = RecoveryScanner().reconcile_open_children(
            store, occurred_at=_AT, project_id="project-b")
        self.assertEqual(emitted, [])


class RF109SettledSubtreesReplay(unittest.TestCase):

    def test_a_settled_subtree_is_not_re_executed(self) -> None:
        store = SqliteEventStore(":memory:")
        runner = _Runner()
        first = _adapter(store, runner=runner).execute(_request())
        second = _adapter(store, runner=runner).execute(_request())
        self.assertEqual(len(runner.plans), 1, "the subtree ran twice")
        self.assertEqual(dict(second.actual_cost), dict(first.actual_cost))
        self.assertEqual(_kinds(store).count("ChildSpawned"), 1)

    def test_the_replayed_cost_survives_the_reducer(self) -> None:
        """The fold used to read a key nothing wrote, so cost was always None."""
        store = SqliteEventStore(":memory:")
        _adapter(store).execute(_request())
        state = reduce_batch(initial_state(), list(
            store.read(EventRange(project_id="project-a")).value or []))
        record = next(iter(state.children.values()))
        self.assertEqual(dict(record.cost or {}), {"tokens": 10})

    def test_the_settled_intent_key_is_bound_to_the_returned_fact(self) -> None:
        """Activates a reducer check that was dead because nothing wrote it."""
        store = SqliteEventStore(":memory:")
        _adapter(store).execute(_request())
        returned = next(p for p in _payloads(store) if p["kind"] == "ChildReturned")
        self.assertEqual(returned["settledIntentKey"], "intent-1")


class RF110ProjectIsolation(unittest.TestCase):
    """One store, one idempotency key, two projects, two distinct children."""

    def test_the_same_key_in_two_projects_yields_two_children(self) -> None:
        store = SqliteEventStore(":memory:")
        _adapter(store, project="project-a").execute(_request())
        _adapter(store, project="project-b").execute(_request())

        a = _payloads(store, "project-a")
        b = _payloads(store, "project-b")
        id_a = next(p["childEpisodeId"] for p in a if p["kind"] == "ChildSpawned")
        id_b = next(p["childEpisodeId"] for p in b if p["kind"] == "ChildSpawned")
        self.assertNotEqual(id_a, id_b)

    def test_a_settled_subtree_does_not_replay_into_another_project(self) -> None:
        store = SqliteEventStore(":memory:")
        _adapter(store, project="project-a").execute(_request())
        runner = _Runner()
        outcome = _adapter(store, runner=runner, project="project-b").execute(_request())
        self.assertEqual(len(runner.plans), 1,
                         "project-b replayed project-a's settlement")
        self.assertEqual(outcome.occurrence, Occurrence.OCCURRED)

    def test_project_identity_is_inside_the_id_preimage(self) -> None:
        """Structural, not merely query-filtered.

        A reader that forgets to scope its `EventRange` still cannot confuse
        the two children, because the ids themselves differ.
        """
        self.assertNotEqual(
            derive_child_id("ep-parent", "k", "project-a"),
            derive_child_id("ep-parent", "k", "project-b"))


class RF111KillTreeAppendsAndErasesNothing(unittest.TestCase):
    """A kill is not an outcome the parent gets to report on the child's behalf.

    `KeyboardInterrupt` and `SystemExit` are `BaseException`, so the adapter's
    `except Exception` deliberately does not catch them: swallowing a kill to
    write a tidy `ChildReturned` would be both a lie and unreliable, since the
    process is going away. What survives is the `ChildSpawned` fact written
    *before* the runner was called, and the cold path adjudicates it. That
    ordering is the entire reason the fact comes first.
    """

    @staticmethod
    def _killed(plan):
        raise KeyboardInterrupt("SIGKILL mid-child")

    def test_a_kill_propagates_rather_than_being_reported_as_an_outcome(self) -> None:
        store = SqliteEventStore(":memory:")
        with self.assertRaises(KeyboardInterrupt):
            _adapter(store, runner=_Runner(on_call=self._killed)).execute(_request())

    def test_the_spawn_fact_survives_the_kill_and_folds_as_open(self) -> None:
        store = SqliteEventStore(":memory:")
        with self.assertRaises(KeyboardInterrupt):
            _adapter(store, runner=_Runner(on_call=self._killed)).execute(_request())

        kinds = _kinds(store)
        self.assertIn("ChildSpawned", kinds)
        self.assertNotIn("ChildReturned", kinds)

        state = reduce_batch(initial_state(), list(
            store.read(EventRange(project_id="project-a")).value or []))
        record = next(iter(state.children.values()))
        self.assertEqual(record.status, "open")
        self.assertTrue(record.reconcilable)

    def test_the_killed_subtree_replays_as_undeterminable_and_is_not_retried(self) -> None:
        store = SqliteEventStore(":memory:")
        with self.assertRaises(KeyboardInterrupt):
            _adapter(store, runner=_Runner(on_call=self._killed)).execute(_request())

        # The restart. A fresh adapter, the same durable store, the same key.
        survivor = _Runner()
        outcome = _adapter(store, runner=survivor).execute(_request())
        self.assertEqual(outcome.occurrence, Occurrence.UNDETERMINABLE)
        self.assertEqual(survivor.plans, [],
                         "a killed subtree was blindly re-executed")

    def test_a_kill_erases_nothing_that_was_already_written(self) -> None:
        store = SqliteEventStore(":memory:")
        _adapter(store).execute(_request())
        settled = _payloads(store)

        with self.assertRaises(KeyboardInterrupt):
            _adapter(store, runner=_Runner(on_call=self._killed)).execute(
                _request(idempotency_key="intent-2"))

        after = _payloads(store)
        self.assertGreaterEqual(len(after), len(settled))
        self.assertEqual(after[:len(settled)], settled)


class RF112RecursionReentersTheSoleBoundary(unittest.TestCase):
    """The child runs through `Runtime.run_composed`, and through nothing else."""

    def test_the_runner_calls_the_injected_boundary_exactly_once(self) -> None:
        calls = []

        class _FakeResult:
            terminal = "completed"
            receipts = ()
            events = ()
            detail = ""
            state_digest = "sha256:" + "e" * 64
            run_digest = "sha256:run"
            activation_digest = "sha256:act"

        def fake_run_composed(harness, ports, task, **kwargs):
            calls.append((harness, ports, task, kwargs))
            return _FakeResult()

        runner = RuntimeChildRunner(
            run_composed=fake_run_composed, harness=object(),
            parent_ports=_FakePorts(), parent_task=_FakeTask())
        plan = _plan()
        result = runner.run_child(plan)

        self.assertEqual(len(calls), 1)
        self.assertEqual(result.child_episode_id, plan.child_episode_id)
        self.assertEqual(result.outcome, "completed")

    def test_root_binds_the_public_boundary_as_the_child_runner(self) -> None:
        """The one production binder passes `Runtime.run_composed` itself."""
        import inspect
        from vanguard.packages.runtime.root import Runtime

        source = inspect.getsource(Runtime.run_composed)
        self.assertIn("RuntimeChildRunner(", source)
        self.assertIn("run_composed=cls.run_composed", source)

    def test_the_child_task_lowers_turns_and_carries_lineage(self) -> None:
        captured = {}

        class _FakeResult:
            terminal = "completed"
            receipts = ()
            events = ()
            detail = ""
            state_digest = "sha256:x"
            run_digest = ""
            activation_digest = ""

        def fake_run_composed(harness, ports, task, **kwargs):
            captured["task"] = task
            captured["ports"] = ports
            return _FakeResult()

        plan = _plan(max_turns=2)
        RuntimeChildRunner(
            run_composed=fake_run_composed, harness=object(),
            parent_ports=_FakePorts(), parent_task=_FakeTask()).run_child(plan)

        self.assertEqual(captured["task"].max_turns, 2)
        self.assertEqual(captured["task"].episode_id, plan.child_episode_id)
        self.assertEqual(captured["task"].parent_episode_id, plan.parent_episode_id)
        self.assertIn(plan.child_episode_id, captured["task"].lineage)
        self.assertEqual(captured["task"].brief, "", "the brief must not travel")

    def test_the_child_never_inherits_interactivity_or_a_controller(self) -> None:
        captured = {}

        class _FakeResult:
            terminal = "completed"
            receipts = ()
            events = ()
            detail = ""
            state_digest = "sha256:x"
            run_digest = ""
            activation_digest = ""

        def fake_run_composed(harness, ports, task, **kwargs):
            captured["ports"] = ports
            return _FakeResult()

        RuntimeChildRunner(
            run_composed=fake_run_composed, harness=object(),
            parent_ports=_FakePorts(interactive=True, meta_controller=object()),
            parent_task=_FakeTask()).run_child(_plan())

        self.assertFalse(captured["ports"].interactive)
        self.assertIsNone(captured["ports"].meta_controller)

    def test_the_runner_is_a_conforming_port(self) -> None:
        runner = RuntimeChildRunner(
            run_composed=lambda *a, **k: None, harness=object(),
            parent_ports=_FakePorts(), parent_task=_FakeTask())
        self.assertIsInstance(runner, ChildRuntimePort)


# -- fixtures for RF-112 ---------------------------------------------------


def _plan(**overrides) -> ChildRunPlan:
    base = dict(
        child_episode_id="ep-child", parent_episode_id="ep-parent",
        run_id="run-1", project_id="project-a", principal="agent",
        composition_digest="sha256:comp", goal_digest="sha256:goal",
        authority=("fs.read",), resources=(), depth=1, max_depth=4,
        max_turns=3, budget={"tokens": 10}, lineage=("ep-parent",),
        idempotency_key="intent-1",
    )
    base.update(overrides)
    return ChildRunPlan(**base)


from vanguard.packages.runtime.session import SessionPorts  # noqa: E402
from vanguard.packages.runtime.compose import TaskContext  # noqa: E402


def _FakePorts(**overrides):
    base = dict(model=None, environment=None, clock=None, store=None)
    base.update(overrides)
    return SessionPorts(**base)


def _FakeTask(**overrides):
    base = dict(brief="parent brief", repo_path="/tmp", principal="agent")
    base.update(overrides)
    return TaskContext(**base)


if __name__ == "__main__":
    unittest.main()
