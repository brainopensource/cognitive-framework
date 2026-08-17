"""W12-A: budgeted skill index, brief exemption, dead ends, sealed spawn.

Three things that all fail the same way if left to good intentions — a prefix
that quietly grows, a brief that quietly gets summarised, and a child that
quietly gets its parent's authority back.
"""

from __future__ import annotations

import unittest

from vanguard.packages.agency.context.compiler import ContextCompiler
from vanguard.packages.agency.context.layers import Fragment
from vanguard.packages.kernel import (
    Constraints,
    EffectRequest,
    FailurePath,
    Mode,
    Outcome,
    Scope,
    StandardPolicy,
)
from vanguard.packages.kernel.attenuation import attenuate
from vanguard.packages.runtime.session_log import session_log
from vanguard.packages.runtime.skill_index import (
    DEFAULT_BUDGET_CHARS,
    build_skill_index,
)

RESOURCE = {"kind": "fs", "root": "/workspace", "paths": ["/workspace"]}


def _skills(count: int, *, description: str = "does a thing") -> list[dict]:
    return [{"name": f"skill-{i:03d}", "description": description,
             "path": f"skills/skill-{i:03d}.md"} for i in range(count)]


class TheSkillIndexFitsThePrefix(unittest.TestCase):
    """Names and descriptions in the frozen prefix; bodies via `fs.read`."""

    def test_a_small_library_fits_entirely(self) -> None:
        index = build_skill_index(_skills(5))
        self.assertEqual(len(index.entries), 5)
        self.assertEqual(index.dropped, ())

    def test_the_budget_is_enforced_not_documented(self) -> None:
        index = build_skill_index(_skills(500))
        self.assertLessEqual(index.size_chars, DEFAULT_BUDGET_CHARS)

    def test_what_did_not_fit_is_named(self) -> None:
        """A pack author must see the ceiling bite, not wonder why a skill
        is never chosen."""

        index = build_skill_index(_skills(500))
        self.assertTrue(index.dropped)
        self.assertEqual(len(index.entries) + len(index.dropped), 500)

    def test_truncation_is_by_whole_entries(self) -> None:
        """Half a description is worse than an absent one: the agent cannot
        tell it is reading a fragment."""

        index = build_skill_index(_skills(500))
        for entry in index.entries:
            self.assertIn(entry.name, entry.render())
            self.assertTrue(entry.render().endswith(entry.description))

    def test_bodies_are_never_in_the_prefix(self) -> None:
        body = "SECRET-BODY-TEXT " * 100
        index = build_skill_index([
            {"name": "s", "description": "one line", "path": "skills/s.md",
             "body": body}])
        self.assertNotIn("SECRET-BODY-TEXT", index.render())

    def test_the_body_is_reachable_by_path_for_fs_read(self) -> None:
        index = build_skill_index(_skills(3))
        self.assertEqual(index.path_of("skill-001"), "skills/skill-001.md")
        self.assertIsNone(index.path_of("not-a-skill"))

    def test_order_is_the_packs_preference(self) -> None:
        index = build_skill_index(
            [{"name": "wanted", "description": "d", "path": "a.md"}] + _skills(500))
        self.assertEqual(index.entries[0].name, "wanted")

    def test_a_skill_without_a_path_is_skipped(self) -> None:
        """An entry the agent cannot fetch is an advertisement for nothing."""

        index = build_skill_index([{"name": "s", "description": "d"}])
        self.assertEqual(index.entries, ())


class TheBriefIsCompactionExempt(unittest.TestCase):
    """`VG-03 §10.5`: work is checked against the brief, never against the
    last summary of it."""

    def _compile(self, dialogue: tuple = ()):
        compiler = ContextCompiler(
            system_core="core", tool_schemas=(), environment="env",
            token_ceiling=4_096)
        return compiler.compile(brief="fix the failing suite",
                                notes=(), dialogue=dialogue)

    def test_the_brief_block_is_not_evictable(self) -> None:
        compiled = self._compile()
        briefs = [b for b in compiled.blocks if b.label == "brief"]
        self.assertEqual(len(briefs), 1)
        self.assertFalse(briefs[0].evictable)

    def test_the_brief_survives_a_dialogue_large_enough_to_compact(self) -> None:
        dialogue = tuple(
            Fragment(source="tool_result", label=f"turn-{i}",
                     text="x" * 4_000, evictable=True)
            for i in range(20))
        compiled = self._compile(dialogue)
        rendered = "\n".join(b.text for b in compiled.blocks)
        self.assertIn("fix the failing suite", rendered)


class _Event:
    def __init__(self, kind: str, **payload) -> None:
        self.payload = {"kind": kind, **payload}


class DeadEndsAndCacheMissAttribution(unittest.TestCase):
    """W12-A item 6. Both derived from the log, so neither can disagree
    with the turns they explain."""

    def test_a_dead_end_carries_its_verb_and_reason(self) -> None:
        log = session_log([
            _Event("ProposalProduced", toolCalls=[{"action": "proc.exec"}]),
            _Event("AuthorizationDenied", reason="not granted in scope"),
        ])
        self.assertEqual(log.dead_end_details, (
            {"turn": 1, "verb": "proc.exec", "reason": "not granted in scope"},))

    def test_a_completed_turn_is_not_a_dead_end(self) -> None:
        log = session_log([
            _Event("ProposalProduced", toolCalls=[{"action": "fs.read"}]),
            _Event("EffectCompleted"),
        ])
        self.assertEqual(log.dead_end_details, ())

    def test_a_compaction_miss_is_attributed_to_the_compaction(self) -> None:
        log = session_log([
            _Event("ProposalProduced", toolCalls=[{"action": "fs.read"}]),
            _Event("EffectCompleted"),
            _Event("ProposalProduced", toolCalls=[{"action": "fs.read"}],
                   cacheMiss=True, compacted=True),
            _Event("EffectCompleted"),
        ])
        self.assertEqual(log.cache_miss_attribution(), (
            {"turn": 2, "cause": "compaction_rewrote_the_prefix", "verb": "fs.read"},))

    def test_a_miss_after_a_refusal_is_attributed_to_the_refusal(self) -> None:
        log = session_log([
            _Event("ProposalProduced", toolCalls=[{"action": "proc.exec"}]),
            _Event("AuthorizationDenied", reason="denied"),
            _Event("ProposalProduced", toolCalls=[{"action": "fs.read"}],
                   cacheMiss=True),
            _Event("EffectCompleted"),
        ])
        self.assertEqual(log.cache_miss_attribution()[0]["cause"], "prior_turn_refused")

    def test_a_first_turn_miss_is_a_cold_prefix_not_a_defect(self) -> None:
        log = session_log([
            _Event("ProposalProduced", toolCalls=[{"action": "fs.read"}],
                   cacheMiss=True),
            _Event("EffectCompleted"),
        ])
        self.assertEqual(log.cache_miss_attribution()[0]["cause"], "cold_prefix")

    def test_an_unexplained_miss_says_unattributed_rather_than_guessing(self) -> None:
        log = session_log([
            _Event("ProposalProduced", toolCalls=[{"action": "fs.read"}]),
            _Event("EffectCompleted"),
            _Event("ProposalProduced", toolCalls=[{"action": "fs.read"}],
                   cacheMiss=True),
            _Event("EffectCompleted"),
        ])
        self.assertEqual(log.cache_miss_attribution()[0]["cause"], "unattributed")

    def test_turns_that_hit_produce_no_attribution(self) -> None:
        log = session_log([
            _Event("ProposalProduced", toolCalls=[{"action": "fs.read"}],
                   cacheMiss=False),
            _Event("EffectCompleted"),
        ])
        self.assertEqual(log.cache_miss_attribution(), ())


def _constraints() -> Constraints:
    return Constraints(expires_at="2099-01-01T00:00:00.000Z", max_uses=100,
                       budget_usd_micros=1_000_000, max_depth=4)


def _scope(actions, depth: int = 0) -> Scope:
    return Scope(actions=frozenset(actions), resources=(RESOURCE,),
                 constraints=_constraints(), depth=depth)


class SpawnForExploreIsSealed(unittest.TestCase):
    """W12-A item 7, against the real `StandardPolicy` — no mock enforcement.

    An explore child is the case that most wants to widen: it is looking for
    something and does not yet know where. `ADR-0067` is what makes "read-only
    helper" mean read-only rather than describe an intention.
    """

    PARENT = _scope({"fs.read", "fs.search", "patch.apply"})

    def _policy(self, **overrides) -> StandardPolicy:
        base = dict(parent_scope=self.PARENT, mode=Mode.BENCHMARK,
                    approval_required_above="high",
                    risk_of={"fs.read": "low", "fs.search": "low",
                             "patch.apply": "medium"})
        base.update(overrides)
        return StandardPolicy(**base)

    def _request(self, action: str) -> EffectRequest:
        return EffectRequest(action=action, resource=RESOURCE,
                             args={"path": "a.py"}, principal="agent-1",
                             run_id="run-explore")

    def test_attenuating_to_an_explore_scope_seals_it(self) -> None:
        granted = attenuate(self.PARENT, _scope({"fs.read", "fs.search"}, depth=1))
        self.assertTrue(granted.ok)
        self.assertTrue(granted.granted.sealed)

    def test_a_sealed_explore_child_cannot_patch(self) -> None:
        child = attenuate(self.PARENT, _scope({"fs.read", "fs.search"}, depth=1)).granted
        decision = self._policy().authorize(
            self._request("patch.apply"), widens_capability=False,
            requested_scope=child)
        self.assertIs(decision.outcome, Outcome.REJECT)
        self.assertIs(decision.failure, FailurePath.DENIED_SCOPE_ESCALATION)

    def test_the_sealed_child_still_does_its_job(self) -> None:
        child = attenuate(self.PARENT, _scope({"fs.read", "fs.search"}, depth=1)).granted
        for action in ("fs.read", "fs.search"):
            with self.subTest(action=action):
                decision = self._policy().authorize(
                    self._request(action), widens_capability=False,
                    requested_scope=child)
                self.assertIs(decision.outcome, Outcome.ALLOW)

    def test_an_unsealed_parent_scope_is_unaffected(self) -> None:
        """`test_widening_alone_is_not_a_violation` must keep holding."""

        self.assertFalse(self.PARENT.sealed)

    def test_the_seal_survives_a_second_attenuation(self) -> None:
        """A grandchild of an explore child is no less sealed."""

        child = attenuate(self.PARENT, _scope({"fs.read", "fs.search"}, depth=1)).granted
        grandchild = attenuate(child, _scope({"fs.read"}, depth=2))
        self.assertTrue(grandchild.ok)
        self.assertTrue(grandchild.granted.sealed)


if __name__ == "__main__":
    unittest.main()
