"""T-140: one production task-conditioned skill selector, proved on the product path.

The unit that used to live here (`retrieve_skills_for_task`) was a second,
unused ranking helper over loose dicts; nothing in production called it. It is
superseded by `select_skills_for_task`, which operates on the composed
`SkillCard` values the product actually carries and is invoked by
`HarnessSession` itself.

What this module proves, through a **composed product session**
(`Runtime.compose("vg-code-default")` → `HarnessSession`):

1. Two distinct briefs select distinct, relevant skills from the same pack.
2. Stable cards stay in the frozen `L3` prefix; the task-conditioned selection
   lands in `L5` only and never leaks into `L1–L3`.
3. Admitting the selection leaves the prefix digest byte-identical across turns.
4. The `W12-A` ceiling (≤ 4096 characters) is enforced by whole-card omission,
   and the omission is itself reported rather than silently applied.
5. Removing the production selector makes the product oracle fail (the
   bypass falsifier at the end).
"""

from __future__ import annotations

import unittest
from dataclasses import replace

from test.agency.doubles import ScriptedModel, finish
from test.runtime.test_harness_session import FakeEnvironment, _ports, _task
from vanguard.packages.agency.context.layers import Layer, PREFIX_LAYERS
from vanguard.packages.domain.artifacts.skill_index import SkillCard
from vanguard.packages.runtime.root import HarnessSession, Runtime
from vanguard.packages.runtime.skill_index import (
    DEFAULT_BUDGET_CHARS,
    DYNAMIC_SELECTION_POLICY,
    SkillSelection,
    select_skills_for_task,
)

#: The three cards `vg-code-default` actually composes, by id.
PYTEST_SKILL = "pytest-green"
SCAFFOLD_SKILL = "scaffold-python-api-static-html"
RECEIPT_SKILL = "read-receipt-before-repatch"

PYTEST_BRIEF = "get the pytest suite green again"
SCAFFOLD_BRIEF = "scaffold a python http api with static html frontend assets"
FOREIGN_BRIEF = "translate the libretto into middle high german"


def _session(brief: str) -> HarnessSession:
    """One composed product session on the real `vg-code-default` pack."""
    harness = Runtime.compose("vg-code-default", episode_id="ep-session-1")
    return HarnessSession(
        harness,
        _ports(ScriptedModel([finish()]), FakeEnvironment()),
        replace(_task(), brief=brief),
    )


def _layer_text(compiled, layer) -> str:
    return "\n".join(block.text for block in compiled.layer_blocks(layer))


class ProductionSelectorIsTaskConditioned(unittest.TestCase):
    """The selector distinguishes briefs; it does not merely sort the pack."""

    def test_two_distinct_briefs_select_distinct_skills(self) -> None:
        pytest_ids = [c.skill_id for c in _session(PYTEST_BRIEF).skill_selection.selected]
        scaffold_ids = [c.skill_id for c in _session(SCAFFOLD_BRIEF).skill_selection.selected]
        self.assertIn(PYTEST_SKILL, pytest_ids)
        self.assertIn(SCAFFOLD_SKILL, scaffold_ids)
        self.assertNotEqual(pytest_ids, scaffold_ids)

    def test_a_brief_implicating_nothing_selects_nothing(self) -> None:
        session = _session(FOREIGN_BRIEF)
        self.assertIsNone(session.skill_selection)

    def test_selection_is_deterministic_for_one_brief(self) -> None:
        first = _session(PYTEST_BRIEF).skill_selection
        second = _session(PYTEST_BRIEF).skill_selection
        self.assertEqual(first.digest(), second.digest())
        self.assertEqual(first.policy_identity, DYNAMIC_SELECTION_POLICY)

    def test_the_selection_binds_a_provenance_receipt(self) -> None:
        selection = _session(PYTEST_BRIEF).skill_selection
        self.assertTrue(selection.query_digest.startswith("sha256:"))
        self.assertTrue(selection.digest().startswith("sha256:"))
        # A different brief must not reuse another brief's receipt.
        self.assertNotEqual(
            selection.digest(), _session(SCAFFOLD_BRIEF).skill_selection.digest())


class DynamicSelectionLandsInL5Only(unittest.TestCase):
    """`L3` holds the stable index; `L5` holds this task's selection."""

    def setUp(self) -> None:
        self.session = _session(PYTEST_BRIEF)
        _, self.compiled = self.session.operator._assembler.assemble(view={}, turn=0)

    def test_the_stable_index_of_every_card_rides_the_l3_prefix(self) -> None:
        environment = _layer_text(self.compiled, Layer.ENVIRONMENT)
        for skill_id in (PYTEST_SKILL, SCAFFOLD_SKILL, RECEIPT_SKILL):
            self.assertIn(skill_id, environment)

    def test_the_task_conditioned_selection_is_in_l5(self) -> None:
        dialogue = _layer_text(self.compiled, Layer.DIALOGUE)
        self.assertIn("Task-relevant skills", dialogue)
        self.assertIn(PYTEST_SKILL, dialogue)

    def test_the_selection_never_appears_in_the_frozen_prefix(self) -> None:
        for layer in PREFIX_LAYERS:
            self.assertNotIn("Task-relevant skills", _layer_text(self.compiled, layer))

    def test_no_skill_body_is_read_to_build_the_selection(self) -> None:
        """Selecting a skill costs a line, not a document.

        The rendered block carries the same name+description shape the frozen
        `L3` index uses, and the header points at `fs.read` for the body. No
        effect reached the environment to produce it.
        """
        rendered = self.session.skill_selection.render()
        self.assertIn("fs.read", rendered)
        for card in self.session.skill_selection.selected:
            self.assertIn(card.index_line(), rendered)
        self.assertEqual(self.session.calls, [])


class AdmittingTheSelectionPreservesThePrefix(unittest.TestCase):
    """`L1–L3` must be byte-identical across turns once the note is admitted."""

    def test_prefix_digest_is_stable_across_turns(self) -> None:
        session = _session(PYTEST_BRIEF)
        digests = []
        for turn in range(3):
            _, compiled = session.operator._assembler.assemble(view={}, turn=turn)
            digests.append(compiled.prefix_digest)
            session.operator.note(
                label=f"tool-result-{turn}", source="tool_result", text="a turn-local fact")
        self.assertEqual(len(set(digests)), 1, digests)

    def test_a_session_without_a_selection_has_the_same_prefix_as_one_with(self) -> None:
        """The note is `L5`; its presence or absence cannot move the prefix."""
        with_selection = _session(PYTEST_BRIEF)
        without = _session(PYTEST_BRIEF)
        without.operator._assembler._dialogue.clear()
        _, a = with_selection.operator._assembler.assemble(view={}, turn=0)
        _, b = without.operator._assembler.assemble(view={}, turn=0)
        self.assertEqual(a.prefix_digest, b.prefix_digest)
        self.assertNotEqual(
            _layer_text(a, Layer.DIALOGUE), _layer_text(b, Layer.DIALOGUE))


class W12ACeilingIsEnforced(unittest.TestCase):
    """≤ 4096 characters, by whole-card omission, with the omission reported."""

    @staticmethod
    def _cards(count: int, *, description: str = "pytest suite green coverage") -> tuple[SkillCard, ...]:
        return tuple(
            SkillCard(
                skill_id=f"skill-{index:03d}",
                name=f"Skill {index} pytest",
                description=description,
                body_path=f"skills/skill-{index:03d}.md",
            )
            for index in range(count)
        )

    def test_the_default_ceiling_is_the_w12a_bound(self) -> None:
        self.assertEqual(DEFAULT_BUDGET_CHARS, 4096)

    def test_a_large_library_is_truncated_to_the_ceiling(self) -> None:
        selection = select_skills_for_task(self._cards(400), "pytest suite green")
        self.assertLessEqual(selection.size_chars, DEFAULT_BUDGET_CHARS)
        self.assertTrue(selection.omitted)

    def test_truncation_omits_whole_cards_never_fragments(self) -> None:
        selection = select_skills_for_task(self._cards(400), "pytest suite green")
        rendered = selection.render()
        for card in selection.selected:
            self.assertIn(card.index_line(), rendered)
        for skill_id in selection.omitted:
            self.assertNotIn(f"{skill_id}: ", rendered)
        self.assertIn(f"{len(selection.omitted)} skill card(s)", rendered)

    def test_every_card_is_either_selected_or_reported_omitted(self) -> None:
        cards = self._cards(400)
        selection = select_skills_for_task(cards, "pytest suite green")
        accounted = {c.skill_id for c in selection.selected} | set(selection.omitted)
        self.assertEqual(accounted, {c.skill_id for c in cards})

    def test_a_narrower_ceiling_selects_strictly_fewer(self) -> None:
        cards = self._cards(400)
        wide = select_skills_for_task(cards, "pytest suite green")
        narrow = select_skills_for_task(cards, "pytest suite green", budget_chars=500)
        self.assertLessEqual(narrow.size_chars, 500)
        self.assertLess(len(narrow.selected), len(wide.selected))

    def test_the_ceiling_biting_is_itself_reported_to_the_agent(self) -> None:
        selection = select_skills_for_task(self._cards(400), "pytest suite green")
        self.assertIn("omitted for W12-A ceiling", selection.render())

    def test_a_nonpositive_ceiling_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            select_skills_for_task(self._cards(2), "pytest", budget_chars=0)

    def test_the_product_session_selection_respects_the_ceiling(self) -> None:
        selection = _session(PYTEST_BRIEF).skill_selection
        self.assertLessEqual(selection.size_chars, DEFAULT_BUDGET_CHARS)
        self.assertEqual(selection.budget_chars, DEFAULT_BUDGET_CHARS)


class RemovingTheProductionSelectorFailsTheOracle(unittest.TestCase):
    """The bypass falsifier: a session that skips selection must not look green."""

    def test_a_session_that_never_selects_has_no_l5_skill_observation(self) -> None:
        session = _session(PYTEST_BRIEF)
        bypassed = _session(PYTEST_BRIEF)
        # Simulate the helper being unused again: drop the admitted note.
        bypassed.skill_selection = None
        bypassed.operator._assembler._dialogue.clear()

        _, admitted = session.operator._assembler.assemble(view={}, turn=0)
        _, skipped = bypassed.operator._assembler.assemble(view={}, turn=0)

        self.assertIn("Task-relevant skills", _layer_text(admitted, Layer.DIALOGUE))
        self.assertNotIn("Task-relevant skills", _layer_text(skipped, Layer.DIALOGUE))

    def test_the_superseded_duplicate_helper_is_gone(self) -> None:
        import vanguard.packages.runtime.skill_index as skill_index

        self.assertFalse(hasattr(skill_index, "retrieve_skills_for_task"))
        self.assertNotIn("retrieve_skills_for_task", skill_index.__all__)

    def test_there_is_exactly_one_production_selector_entry_point(self) -> None:
        import vanguard.packages.runtime.skill_index as skill_index

        selectors = [
            name for name in skill_index.__all__
            if "select" in name or "retrieve" in name
        ]
        self.assertEqual(selectors, ["select_skills_for_task"])

    def test_an_empty_selection_renders_nothing_rather_than_a_bare_header(self) -> None:
        empty = SkillSelection()
        self.assertEqual(empty.render(), "")
        self.assertEqual(empty.size_chars, 0)


if __name__ == "__main__":
    unittest.main()
