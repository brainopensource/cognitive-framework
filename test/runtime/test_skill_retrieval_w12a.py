"""Contract tests and falsifiers for C4: Retrieval-driven, task-conditioned skill selection.

Verifies:
1. `retrieve_skills_for_task` ranks candidate skills by task relevance.
2. The W12-A ceiling (<= 4096 characters) is strictly enforced with whole-entry truncation and dropped reporting.
3. Skills in composition epoch remain in the frozen L3 prefix.
4. Dynamic per-turn skills land in L5 only, preserving byte-identical L1-L3 prefix digests.
"""

from __future__ import annotations

from pathlib import Path
import unittest

from vanguard.packages.agency.context.compiler import ContextCompiler
from vanguard.packages.agency.context.layers import Layer, PREFIX_LAYERS
from vanguard.packages.domain.artifacts.skill_index import SkillCard
from vanguard.packages.runtime.compose import TaskContext
from vanguard.packages.runtime.prompt_assembler import PromptAssembler
from vanguard.packages.runtime.skill_index import (
    DEFAULT_BUDGET_CHARS,
    SkillIndex,
    retrieve_skills_for_task,
)


class FakeClock:
    def now(self) -> str:
        return "2026-09-13T12:00:00Z"


class TestSkillRetrievalW12A(unittest.TestCase):
    def setUp(self) -> None:
        self.skills_pool = [
            {
                "name": "lda-navigator",
                "description": "Universal repository intelligence, symbol lookups, and graph navigation.",
                "path": ".agents/skills/lda-navigator/SKILL.md",
            },
            {
                "name": "test-runner",
                "description": "Atomic test runner for executing isolated, hermetic unit and contract suites.",
                "path": ".agents/skills/test-runner/SKILL.md",
            },
            {
                "name": "tdd-falsifier",
                "description": "TDD falsifier combining lda-navigator and test-runner to locate and run falsifiers.",
                "path": ".agents/techniques/tdd-falsifier/TECHNIQUE.md",
            },
            {
                "name": "lam-engine",
                "description": "LLM API mock engine for zero-cost cassette recording and replay.",
                "path": ".agents/skills/lam-engine/SKILL.md",
            },
            {
                "name": "llama-cpp",
                "description": "Local model inference using native llama.cpp server for zero-cost generation.",
                "path": ".agents/skills/llama-cpp/SKILL.md",
            },
        ]

    def test_task_conditioned_ranking_prioritizes_relevant_skills(self) -> None:
        # Query about test execution and falsification
        idx = retrieve_skills_for_task(self.skills_pool, "run falsifiers and test suites")
        names = [entry.name for entry in idx.entries]
        # test-runner or tdd-falsifier should be ranked at the very top
        self.assertIn(names[0], ("test-runner", "tdd-falsifier"))
        self.assertIn(names[1], ("test-runner", "tdd-falsifier"))

        # Query about local inference
        idx_llm = retrieve_skills_for_task(self.skills_pool, "llama local model generation")
        names_llm = [entry.name for entry in idx_llm.entries]
        self.assertEqual(names_llm[0], "llama-cpp")

    def test_w12a_character_ceiling_enforcement(self) -> None:
        # Create many large skills that exceed a small budget
        large_skills = [
            {
                "name": f"skill-{i:02d}",
                "description": f"Detailed description for skill number {i} with a large amount of padding text to consume budget " * 3,
                "path": f".agents/skills/skill-{i}/SKILL.md",
            }
            for i in range(50)
        ]

        # Budget of 500 characters
        idx = retrieve_skills_for_task(large_skills, "skill", budget_chars=500)
        self.assertLessEqual(idx.size_chars, 500)
        self.assertGreater(len(idx.entries), 0)
        self.assertGreater(len(idx.dropped), 0)
        # Verify whole-entry truncation: no entry has broken syntax
        for entry in idx.entries:
            self.assertTrue(entry.render().startswith(f"{entry.name}: "))

        # Default W12-A ceiling (4096 characters)
        idx_default = retrieve_skills_for_task(large_skills, "skill")
        self.assertLessEqual(idx_default.size_chars, DEFAULT_BUDGET_CHARS)
        self.assertLessEqual(len(idx_default.render()), 4096)

    def test_dynamic_skills_in_l5_preserve_prefix_stability(self) -> None:
        """Proves composition skills stay in L3 prefix, and dynamic per-turn skills land in L5 without perturbing prefix."""
        card = SkillCard(
            skill_id="static-skill",
            name="static-skill",
            description="Composition epoch frozen skill card",
            body_path=".agents/skills/static-skill/SKILL.md",
        )
        compiler = ContextCompiler(
            system_core="System core instructions.",
            skill_cards=(card,),
            token_ceiling=8000,
        )
        task = TaskContext(
            brief="investigate skills",
            repo_path=Path("/workspace"),
            project_id="proj-skill",
            run_id="run-skill",
            episode_id="ep-skill",
            principal="principal-test",
        )
        assembler = PromptAssembler(
            compiler=compiler,
            task=task,
            clock=FakeClock(),
        )

        # Turn 0: baseline compile
        _, compiled0 = assembler.assemble(view={}, turn=0)
        prefix0 = compiled0.prefix_digest

        # Verify static skill is in Layer.ENVIRONMENT (L3 prefix)
        env_blocks = compiled0.layer_blocks(Layer.ENVIRONMENT)
        self.assertTrue(any("static-skill" in b.text for b in env_blocks))

        # Turn 1: dynamic skill retrieved for this turn only -> goes into L5 via note
        dynamic_idx = retrieve_skills_for_task(self.skills_pool, "mock completions cassette")
        assembler.note(
            label="dynamic-skills-turn-1",
            source="skill_retrieval",
            text=f"Task-conditioned skills:\n{dynamic_idx.render()}",
        )

        _, compiled1 = assembler.assemble(view={}, turn=1)
        prefix1 = compiled1.prefix_digest

        # Dynamic skill is in L5 (Layer.DIALOGUE)
        l5_blocks = compiled1.layer_blocks(Layer.DIALOGUE)
        self.assertTrue(any("lam-engine" in b.text for b in l5_blocks))

        # Dynamic skill is NOT in L1-L3 prefix
        for layer in PREFIX_LAYERS:
            for b in compiled1.layer_blocks(layer):
                self.assertNotIn("lam-engine", b.text)

        # Prefix digest is bit-for-bit identical across turns
        self.assertEqual(
            prefix0,
            prefix1,
            "Admitting dynamic skills to L5 must not alter the frozen L1-L3 prefix digest",
        )


if __name__ == "__main__":
    unittest.main()
