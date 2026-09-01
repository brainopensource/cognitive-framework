"""ADR-0090 — the child fold must be reachable, and must fail closed.

The fold landed by `M6_CLOSE_ADR0090.patch` read its payload in snake_case
(`child_episode_id`), while every other branch of this reducer -- and every
emitter in the tree -- is camelCase (`grantId`, `descriptorDigest`,
`parentGrantId`). On a repo-convention `ChildSpawned` the branch read `None`,
took the `if cid:` false arm, and folded nothing *without raising*. Because the
patch also removed both kinds from `UNFOLDED_ALLOWLIST`, the coverage contract
then asserted they were folded when in practice they were not, and the orphan /
double-return / intent-mismatch guards had no record to fire against.

Nothing caught it because `agent.spawn` is still inert
(`runtime/delegation.py: M6_SPAWN_ACTIVE = False`), so no test emits these
kinds. These tests emit them directly, which is the only way the defect is
visible before `SpawnAdapter` exists.
"""

from __future__ import annotations

import unittest
from dataclasses import replace

from vanguard.packages.domain.ledger.events import EventEnvelope
from vanguard.packages.domain.ledger.reducer import ReducerError, reduce_event
from vanguard.packages.domain.ledger.state import LedgerState

PARENT = "ep-parent"
CHILD = "ep-child"


def _envelope(seq: int, payload: dict) -> EventEnvelope:
    return EventEnvelope(
        schema_version="mhf.event/1", event_id=f"evt-{seq}", scope="episode", seq=seq,
        occurred_at="2026-08-24T00:00:00Z", recorded_at="2026-08-24T00:00:00Z",
        principal="spawn_adapter", principal_role="runtime", tenant_id="tenant",
        owner_id="owner-platform", confidentiality="internal",
        retention_class="extended", trainability="prohibited",
        redaction_status="none", payload=payload,
    )


def _spawned_camel(**overrides) -> dict:
    payload = {"kind": "ChildSpawned", "parentEpisodeId": PARENT,
               "childEpisodeId": CHILD, "authority": ["fs.read"], "depth": 1,
               "lineage": [PARENT], "settledIntentKey": "intent-1"}
    payload.update(overrides)
    return payload


def _spawned_snake(**overrides) -> dict:
    payload = {"kind": "ChildSpawned", "parent_episode_id": PARENT,
               "child_episode_id": CHILD, "authority": ["fs.read"], "depth": 1,
               "lineage": [PARENT], "settled_intent_key": "intent-1"}
    payload.update(overrides)
    return payload


def _returned_camel(**overrides) -> dict:
    payload = {"kind": "ChildReturned", "childEpisodeId": CHILD,
               "outcome": "completed", "terminal": "ok",
               "cost": {"usd_micros": 5}, "settledIntentKey": "intent-1"}
    payload.update(overrides)
    return payload


def _empty() -> LedgerState:
    return LedgerState(run_id="run-1", episode_id=PARENT)


class TheFoldIsReachableUnderEitherSpelling(unittest.TestCase):
    """The regression itself: camelCase must fold, not vanish."""

    def test_a_repo_convention_child_spawned_opens_a_record(self) -> None:
        state = reduce_event(_empty(), _envelope(1, _spawned_camel()))
        self.assertIn(CHILD, state.children)
        record = state.children[CHILD]
        self.assertEqual(record.parent_episode_id, PARENT)
        self.assertEqual(record.settled_intent_key, "intent-1")
        self.assertEqual(record.authority, ("fs.read",))
        self.assertEqual(record.depth, 1)

    def test_the_bundle_schema_spelling_still_folds(self) -> None:
        state = reduce_event(_empty(), _envelope(1, _spawned_snake()))
        self.assertIn(CHILD, state.children)
        self.assertEqual(state.children[CHILD].settled_intent_key, "intent-1")

    def test_an_open_child_is_never_folded_to_complete(self) -> None:
        """The property M6_CLOSURE_RECORD leans on for cold reconciliation."""
        state = reduce_event(_empty(), _envelope(1, _spawned_camel()))
        self.assertEqual(state.children[CHILD].status, "open")
        self.assertTrue(state.children[CHILD].reconcilable)

    def test_child_returned_closes_the_record(self) -> None:
        state = reduce_event(_empty(), _envelope(1, _spawned_camel()))
        state = reduce_event(state, _envelope(2, _returned_camel()))
        record = state.children[CHILD]
        self.assertEqual(record.status, "closed")
        self.assertFalse(record.reconcilable)
        self.assertEqual(record.outcome, "completed")
        self.assertEqual(record.cost, {"usd_micros": 5})


class EveryGuardFires(unittest.TestCase):
    """Each of these was unreachable while the fold read the wrong spelling."""

    def test_a_child_event_with_no_id_is_a_reducer_error_not_a_no_op(self) -> None:
        for kind in ("ChildSpawned", "ChildReturned"):
            with self.subTest(kind=kind):
                with self.assertRaises(ReducerError):
                    reduce_event(_empty(), _envelope(1, {"kind": kind, "depth": 1}))

    def test_duplicate_child_spawned_denies(self) -> None:
        state = reduce_event(_empty(), _envelope(1, _spawned_camel()))
        with self.assertRaises(ReducerError):
            reduce_event(state, _envelope(2, _spawned_camel()))

    def test_child_returned_without_child_spawned_denies(self) -> None:
        with self.assertRaises(ReducerError):
            reduce_event(_empty(), _envelope(1, _returned_camel()))

    def test_a_child_never_returns_twice(self) -> None:
        state = reduce_event(_empty(), _envelope(1, _spawned_camel()))
        state = reduce_event(state, _envelope(2, _returned_camel()))
        with self.assertRaises(ReducerError):
            reduce_event(state, _envelope(3, _returned_camel()))

    def test_a_settled_intent_key_mismatch_denies(self) -> None:
        state = reduce_event(_empty(), _envelope(1, _spawned_camel()))
        with self.assertRaises(ReducerError):
            reduce_event(state, _envelope(2, _returned_camel(settledIntentKey="other")))

    def test_a_mixed_spelling_lineage_still_matches_on_the_intent_key(self) -> None:
        """A snake_case spawn and a camelCase return name the same child."""
        state = reduce_event(_empty(), _envelope(1, _spawned_snake()))
        state = reduce_event(state, _envelope(2, _returned_camel()))
        self.assertEqual(state.children[CHILD].status, "closed")


class TheStateDigestCommitsToChildren(unittest.TestCase):
    """ADR-0091 closes the child-state collision without historical churn."""

    def test_children_are_present_in_the_canonical_dict(self) -> None:
        state = reduce_event(_empty(), _envelope(1, _spawned_camel()))
        self.assertIn(CHILD, state.children)
        child = state.to_canonical_dict()["children"][CHILD]
        self.assertEqual(child["childEpisodeId"], CHILD)
        self.assertEqual(child["status"], "open")

    def test_a_spawned_child_moves_the_state_digest(self) -> None:
        spawned = reduce_event(_empty(), _envelope(1, _spawned_camel()))
        without = replace(spawned, children={})
        self.assertNotEqual(dict(spawned.children), dict(without.children))
        self.assertNotEqual(spawned.digest(), without.digest())

    def test_empty_children_preserve_the_legacy_canonical_shape(self) -> None:
        self.assertNotIn("children", _empty().to_canonical_dict())

    def test_child_order_does_not_change_the_digest(self) -> None:
        first = reduce_event(_empty(), _envelope(1, _spawned_camel()))
        second_payload = _spawned_camel()
        second_payload["childEpisodeId"] = "ep-child-2"
        second_payload["settledIntentKey"] = "intent-2"
        ordered = reduce_event(first, _envelope(2, second_payload))
        reversed_children = replace(
            ordered, children=dict(reversed(tuple(ordered.children.items())))
        )
        self.assertEqual(ordered.digest(), reversed_children.digest())

if __name__ == "__main__":
    unittest.main()
