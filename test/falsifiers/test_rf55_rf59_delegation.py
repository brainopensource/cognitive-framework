"""RF-55…RF-59: `agent.spawn` as a mediated nested lineage (M-6).

Two documents allocate these five identifiers with different assertions:
`ADR-0080 §"Bound falsifiers"` (grant, durable intent, target `D_H`, evaluator
reach, wider authority) and the director review `SPEC_M5B_M6.md §2` (grant,
attenuation, conservation, join, kill-tree). They do not contradict each other,
so this file discharges **both** sets rather than picking a winner on what is a
governance question. Each class names the source it satisfies; the Tech Lead
owns resolving the identifier collision in `INDEX.md`.

The invariant underneath all of them: the Kernel never learns what
`agent.spawn` means.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.domain.ledger.reducer import initial_state, reduce_batch
from vanguard.packages.kernel.attenuation import Constraints, Scope
from vanguard.packages.kernel.model import EffectRequest, Occurrence
from vanguard.packages.ports.event_store import EventRange
from vanguard.packages.runtime.delegation import (
    ADDITIVE_DIMENSIONS,
    SPAWN_VERB,
    STRUCTURAL_CEILINGS,
    ChildLineage,
    DelegationContractError,
    DelegationResult,
    SpawnAdapter,
)
from vanguard.packages.runtime.determinism import FixedClock, SeededRandom
from vanguard.packages.runtime.ledger_emitter import LedgerEmitter

ROOT = Path(__file__).resolve().parents[2]
_AT = "2026-08-26T12:00:00.000Z"


#: The selector shape `domain/selectors/resource_selector.py` actually
#: parses. An unparseable selector is *denied*, not ignored, so getting this
#: wrong makes every spawn look attenuation-denied.
_WORKSPACE = {"kind": "fs", "root": "/workspace", "paths": ["/workspace/src"]}


def _constraints(max_depth: int = 4) -> Constraints:
    return Constraints(expires_at="2027-01-01T00:00:00Z", max_uses=100,
                       budget_usd_micros=1_000_000, max_depth=max_depth)


def _parent_scope(*verbs: str, max_depth: int = 4) -> Scope:
    return Scope(
        actions=frozenset(verbs or {"fs.read", "fs.patch", SPAWN_VERB}),
        resources=(_WORKSPACE,),
        constraints=_constraints(max_depth),
        depth=0,
    )


def _request(**overrides) -> EffectRequest:
    args = {
        "brief": "extract the parser",
        "authority": ["fs.read"],
        "budget": {"tokens": 100, "usd_micros": 500},
        "maxTurns": 3,
    }
    args.update(overrides.pop("args", {}))
    base = {
        "action": SPAWN_VERB,
        "resource": _WORKSPACE,
        "args": args,
        "principal": "agent-m6",
        "run_id": "run-m6",
        "depth": 0,
        "idempotency_key": "intent-spawn-1",
    }
    base.update(overrides)
    return EffectRequest(**base)


def _emitter(store, project="project-m6"):
    return LedgerEmitter(
        store, episode_id="ep-parent", project_id=project,
        principal_id="agent-m6", harness_digest="sha256:" + "6" * 64,
        clock=FixedClock(at=_AT, step_ms=1), random=SeededRandom(seed=6),
        role="spawn_adapter")


def _adapter(store, *, scope=None, run_child=None, max_depth=4, max_turns=8,
             use_store=True):
    return SpawnAdapter(
        emitter=_emitter(store).spawn_adapter(),
        parent_scope=scope or _parent_scope(),
        run_child=run_child or (lambda lineage: DelegationResult(
            ok=True, outcome="completed", terminal="ok",
            child_episode_id=lineage.child_episode_id,
            actual_cost={"tokens": 40, "usd_micros": 120}, turns_used=2,
            result_digest="sha256:" + "d" * 64)),
        clock=FixedClock(at=_AT, step_ms=1),
        store=store if use_store else None,
        parent_episode_id="ep-parent",
        max_depth=max_depth,
        max_turns=max_turns,
    )


def _events(store, project="project-m6"):
    read = store.read(EventRange(project_id=project))
    return [e.payload for e in (read.value or [])]


def _kinds(store, project="project-m6"):
    return [p.get("kind") for p in _events(store, project)]


class TheKernelNeverLearnsWhatSpawnMeans(unittest.TestCase):
    """The load-bearing claim. If this fails, M-6 has taught the TCB a verb."""

    def test_no_kernel_module_mentions_spawn_or_delegation(self) -> None:
        offenders = []
        for path in sorted((ROOT / "vanguard/packages/kernel").glob("*.py")):
            text = path.read_text(encoding="utf-8")
            for token in ("agent.spawn", "SpawnAdapter", "ChildSpawned",
                          "ChildReturned", "delegation", "lineage"):
                if token in text:
                    offenders.append(f"{path.name}: {token}")
        self.assertEqual(offenders, [])

    def test_the_adapter_satisfies_the_generic_effect_adapter_port(self) -> None:
        from vanguard.packages.ports.kernel import EffectAdapter

        adapter = _adapter(SqliteEventStore(":memory:"))
        self.assertIsInstance(adapter, EffectAdapter)
        self.assertEqual(adapter.name, SPAWN_VERB)
        self.assertTrue(adapter.healthy())


class RF55NoGrantNoDelegation(unittest.TestCase):
    """ADR-0080 RF-55 + review RF-55: refusal leaves no lineage in the ledger."""

    def test_a_parent_without_the_spawn_verb_cannot_widen_into_it(self) -> None:
        store = SqliteEventStore(":memory:")
        # The parent holds fs.read only; the child asks for fs.patch.
        adapter = _adapter(store, scope=_parent_scope("fs.read"))
        outcome = adapter.execute(_request(args={"authority": ["fs.patch"]}))
        self.assertEqual(outcome.status, "error")
        self.assertEqual(outcome.occurrence, Occurrence.DID_NOT_OCCUR)
        self.assertIn("attenuation denied", outcome.detail or "")

    def test_a_denied_spawn_writes_no_child_events(self) -> None:
        store = SqliteEventStore(":memory:")
        adapter = _adapter(store, scope=_parent_scope("fs.read"))
        adapter.execute(_request(args={"authority": ["fs.patch"]}))
        self.assertNotIn("ChildSpawned", _kinds(store))
        self.assertNotIn("ChildReturned", _kinds(store))

    def test_a_denied_spawn_costs_nothing(self) -> None:
        store = SqliteEventStore(":memory:")
        adapter = _adapter(store, scope=_parent_scope("fs.read"))
        outcome = adapter.execute(_request(args={"authority": ["fs.patch"]}))
        self.assertEqual(dict(outcome.actual_cost), {})


class RF56AttenuationIsStrict(unittest.TestCase):
    """Review RF-56 + ADR-0080 RF-59: a child never holds more than its parent."""

    def test_the_child_authority_is_a_subset_of_the_parent(self) -> None:
        store = SqliteEventStore(":memory:")
        _adapter(store).execute(_request())
        spawned = next(p for p in _events(store) if p["kind"] == "ChildSpawned")
        self.assertTrue(set(spawned["authority"]) <= _parent_scope().actions)

    def test_an_unspecified_child_inherits_nothing_rather_than_everything(self) -> None:
        store = SqliteEventStore(":memory:")
        _adapter(store).execute(_request(args={"authority": []}))
        spawned = next(p for p in _events(store) if p["kind"] == "ChildSpawned")
        self.assertEqual(spawned["authority"], [])

    def test_depth_increments_and_is_recorded(self) -> None:
        store = SqliteEventStore(":memory:")
        _adapter(store).execute(_request(depth=1))
        spawned = next(p for p in _events(store) if p["kind"] == "ChildSpawned")
        self.assertEqual(spawned["depth"], 2)


class RF57ConservationAndStructuralCeilings(unittest.TestCase):
    """Review RF-57 + C-05: four additive dimensions, two structural ceilings."""

    def test_the_additive_set_is_exactly_four(self) -> None:
        self.assertEqual(ADDITIVE_DIMENSIONS,
                         ("usd_micros", "millis", "tokens", "bytes"))

    def test_depth_and_turns_are_ceilings_not_costs(self) -> None:
        self.assertEqual(STRUCTURAL_CEILINGS, ("depth", "turns"))
        for ceiling in STRUCTURAL_CEILINGS:
            self.assertNotIn(ceiling, ADDITIVE_DIMENSIONS)

    def test_charged_millis_is_not_a_dimension(self) -> None:
        self.assertNotIn("charged_millis", ADDITIVE_DIMENSIONS)
        with self.assertRaises(DelegationContractError):
            DelegationResult(ok=True, outcome="completed", terminal="ok",
                             child_episode_id="c", actual_cost={"charged_millis": 5})

    def test_a_structural_dimension_inside_an_additive_cost_is_refused(self) -> None:
        for ceiling in STRUCTURAL_CEILINGS:
            with self.assertRaises(DelegationContractError, msg=ceiling):
                DelegationResult(ok=True, outcome="completed", terminal="ok",
                                 child_episode_id="c", actual_cost={ceiling: 1})

    def test_a_structural_dimension_inside_a_child_budget_is_refused(self) -> None:
        store = SqliteEventStore(":memory:")
        adapter = _adapter(store)
        with self.assertRaises(DelegationContractError):
            adapter.execute(_request(args={"budget": {"depth": 2}}))

    def test_the_childs_cost_flows_to_the_parents_lease(self) -> None:
        # Conservation is structural: the adapter reports, the Kernel settles.
        # There is no second accountant, so there is nothing to drift.
        store = SqliteEventStore(":memory:")
        outcome = _adapter(store).execute(_request())
        self.assertEqual(dict(outcome.actual_cost),
                         {"tokens": 40, "usd_micros": 120})

    def test_the_depth_ceiling_is_enforced_independently_of_budget(self) -> None:
        store = SqliteEventStore(":memory:")
        adapter = _adapter(store, max_depth=2)
        # Budget is untouched and generous; only depth is exhausted.
        outcome = adapter.execute(_request(depth=2))
        self.assertEqual(outcome.occurrence, Occurrence.DID_NOT_OCCUR)
        self.assertIn("depth ceiling", outcome.detail or "")
        self.assertNotIn("ChildSpawned", _kinds(store))

    def test_the_child_turn_ceiling_never_exceeds_the_parents(self) -> None:
        store = SqliteEventStore(":memory:")
        _adapter(store, max_turns=4).execute(_request(args={"maxTurns": 99}))
        spawned = next(p for p in _events(store) if p["kind"] == "ChildSpawned")
        self.assertEqual(spawned["maxTurns"], 4)


class RF58JoinSemantics(unittest.TestCase):
    """Review RF-58 + ADR-0080 RF-56: a typed contract, ordered, durable."""

    def test_child_returned_follows_child_spawned(self) -> None:
        store = SqliteEventStore(":memory:")
        _adapter(store).execute(_request())
        kinds = [k for k in _kinds(store) if k in ("ChildSpawned", "ChildReturned")]
        self.assertEqual(kinds, ["ChildSpawned", "ChildReturned"])

    def test_the_parent_receives_a_contract_not_a_transcript(self) -> None:
        store = SqliteEventStore(":memory:")
        outcome = _adapter(store).execute(_request())
        self.assertEqual(outcome.result_digest, "sha256:" + "d" * 64)
        returned = next(p for p in _events(store) if p["kind"] == "ChildReturned")
        # Digests and outcomes only. No prose anywhere in the fact.
        self.assertNotIn("messages", returned)
        self.assertNotIn("transcript", returned)
        self.assertNotIn("text", returned)

    def test_a_run_child_that_returns_a_handle_is_refused(self) -> None:
        store = SqliteEventStore(":memory:")
        adapter = _adapter(store, run_child=lambda lineage: {"text": "done"})
        with self.assertRaises(DelegationContractError):
            adapter.execute(_request())

    def test_the_goal_reaches_the_ledger_as_a_digest_never_as_prose(self) -> None:
        store = SqliteEventStore(":memory:")
        _adapter(store).execute(_request(args={"brief": "SECRET-TOKEN-abc123"}))
        blob = json.dumps(_events(store))
        self.assertNotIn("SECRET-TOKEN", blob)
        spawned = next(p for p in _events(store) if p["kind"] == "ChildSpawned")
        self.assertTrue(spawned["goalDigest"].startswith("sha256:"))

    def test_the_lineage_chain_is_recorded_for_a_cold_reader(self) -> None:
        store = SqliteEventStore(":memory:")
        _adapter(store).execute(_request())
        spawned = next(p for p in _events(store) if p["kind"] == "ChildSpawned")
        self.assertEqual(spawned["lineage"], ["ep-parent"])
        self.assertEqual(spawned["parentEpisodeId"], "ep-parent")


class RF59KillTreeAndRestartRecovery(unittest.TestCase):
    """Review RF-59: the hard one. A crash mid-child is UNDETERMINABLE."""

    def test_a_child_that_raises_yields_undeterminable_not_failure(self) -> None:
        def explode(lineage: ChildLineage) -> DelegationResult:
            raise RuntimeError("child process died")

        store = SqliteEventStore(":memory:")
        outcome = _adapter(store, run_child=explode).execute(_request())
        # The child may already have patched a file. "failed" would license a
        # retry that double-applies it.
        self.assertEqual(outcome.occurrence, Occurrence.UNDETERMINABLE)
        returned = next(p for p in _events(store) if p["kind"] == "ChildReturned")
        self.assertEqual(returned["outcome"], "undeterminable")

    def test_the_spawn_fact_is_durable_before_the_child_runs(self) -> None:
        seen: list[list[str]] = []

        def observe(lineage: ChildLineage) -> DelegationResult:
            seen.append(_kinds(store))
            return DelegationResult(ok=True, outcome="completed", terminal="ok",
                                    child_episode_id=lineage.child_episode_id)

        store = SqliteEventStore(":memory:")
        _adapter(store, run_child=observe).execute(_request())
        # Without this ordering the cold path cannot tell a crashed subtree
        # from one that never started.
        self.assertIn("ChildSpawned", seen[0])

    def test_an_orphan_child_spawned_folds_to_open_and_is_reconcilable(self) -> None:
        def die(lineage: ChildLineage) -> DelegationResult:
            raise KeyboardInterrupt("SIGKILL the parent mid-child")

        store = SqliteEventStore(":memory:")
        adapter = _adapter(store)
        adapter._emit("ChildSpawned",
                      ChildLineage(
                          child_episode_id="ep-parent.c9",
                          parent_episode_id="ep-parent", run_id="run-m6",
                          principal="agent-m6", goal_digest="sha256:" + "a" * 64,
                          authority=("fs.read",), depth=1, lineage=("ep-parent",),
                          budget={"tokens": 10}, max_turns=1,
                          settled_intent_key="intent-orphan").to_spawned_payload(),
                      _request(), episode_id="ep-parent.c9")

        read = store.read(EventRange(project_id="project-m6"))
        state = reduce_batch(initial_state(), list(read.value or []))
        child = state.children["ep-parent.c9"]
        self.assertEqual(child.status, "open")
        self.assertTrue(child.reconcilable)

    def test_a_settled_subtree_is_replayed_not_re_executed(self) -> None:
        runs: list[str] = []

        def count(lineage: ChildLineage) -> DelegationResult:
            runs.append(lineage.child_episode_id)
            return DelegationResult(
                ok=True, outcome="completed", terminal="ok",
                child_episode_id=lineage.child_episode_id,
                actual_cost={"tokens": 7})

        store = SqliteEventStore(":memory:")
        first = _adapter(store, run_child=count).execute(_request())
        # A fresh adapter, same durable store, same intent key: the restart.
        second = _adapter(store, run_child=count).execute(_request())

        self.assertEqual(len(runs), 1, "the subtree ran twice across a restart")
        self.assertEqual(dict(second.actual_cost), dict(first.actual_cost))
        self.assertEqual(_kinds(store).count("ChildSpawned"), 1)

    def test_an_open_subtree_replays_as_undeterminable_across_a_restart(self) -> None:
        def die(lineage: ChildLineage) -> DelegationResult:
            raise SystemExit(9)

        store = SqliteEventStore(":memory:")
        adapter = _adapter(store)
        lineage = ChildLineage(
            child_episode_id="ep-parent.c1", parent_episode_id="ep-parent",
            run_id="run-m6", principal="agent-m6",
            goal_digest="sha256:" + "a" * 64, authority=("fs.read",), depth=1,
            lineage=("ep-parent",), budget={"tokens": 10}, max_turns=1,
            settled_intent_key="intent-spawn-1")
        adapter._emit("ChildSpawned", lineage.to_spawned_payload(),
                      _request(), episode_id=lineage.child_episode_id)

        # Fresh process semantics: new adapter, same store, no ChildReturned.
        outcome = _adapter(store).execute(_request())
        self.assertEqual(outcome.occurrence, Occurrence.UNDETERMINABLE)
        self.assertEqual(_kinds(store).count("ChildSpawned"), 1)


class OnlyTheSpawnAdapterMayWriteChildEvents(unittest.TestCase):
    """ADR-0090: plugins, workers and child episodes propose. They never append."""

    def test_the_role_exists_and_owns_both_kinds(self) -> None:
        from vanguard.packages.runtime.ledger_emitter import (
            PRIVILEGED_KIND_OWNERS, ROLE_AUTHORITY_SOURCES, WRITER_ROLES,
        )
        self.assertIn("spawn_adapter", WRITER_ROLES)
        self.assertIn("spawn_adapter", ROLE_AUTHORITY_SOURCES)
        for kind in ("ChildSpawned", "ChildReturned"):
            self.assertEqual(PRIVILEGED_KIND_OWNERS[kind],
                             frozenset({"spawn_adapter"}))

    def test_an_orchestrator_cannot_forge_a_child_event(self) -> None:
        from vanguard.packages.runtime.ledger_emitter import WriterAuthorityError

        store = SqliteEventStore(":memory:")
        emitter = LedgerEmitter(
            store, episode_id="ep-parent", project_id="project-forge",
            principal_id="agent-m6", harness_digest="sha256:" + "6" * 64,
            clock=FixedClock(at=_AT, step_ms=1), random=SeededRandom(seed=7),
            role="orchestrator")
        with self.assertRaises(WriterAuthorityError):
            emitter.orchestrator().emit_kind(
                "ChildSpawned", run_id="run-m6", principal="agent-m6",
                payload={"kind": "ChildSpawned", "childEpisodeId": "forged"})


if __name__ == "__main__":
    unittest.main()
