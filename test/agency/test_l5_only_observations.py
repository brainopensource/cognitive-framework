"""Falsifier for C2 (T-76 / S10-A-03 / VG-03 §10.2).

Proves:
1. `repo.search_symbols`, `repo.get_callers`, `repo.get_dependencies`, and `repo.get_tests`
   execute as bounded observations.
2. All observation outcomes land in Layer.DIALOGUE (L5) only.
3. The L1–L3 prefix digest and serialized prefix messages remain bit-for-bit identical
   across 10 turns of observations.
4. An adversarial perturbation to L1–L3 breaks prefix equality, proving the falsifier is sensitive.
"""

from __future__ import annotations

import json
from pathlib import Path
import unittest

from vanguard.packages.adapters.bindings.code import CodeBindingProvider
from vanguard.packages.adapters.stores.repo_index import InMemoryRepoIndex
from vanguard.packages.agency.context.compiler import ContextCompiler
from vanguard.packages.agency.context.layers import Layer, PREFIX_LAYERS
from vanguard.packages.domain.canonicalisation.digest import digest_of
from vanguard.packages.ports.environment import ObservationRequest
from vanguard.packages.runtime.compose import TaskContext
from vanguard.packages.runtime.prompt_assembler import PromptAssembler
from vanguard.packages.runtime.session import _LayeredOperator, _admit_turn_result


class DummyClock:
    def now(self) -> str:
        return "2026-09-13T12:00:00Z"


class DummyModel:
    def __init__(self) -> None:
        self.invocations: list[dict] = []

    def invoke(self, messages, **kwargs):
        self.invocations.append({"messages": messages, "kwargs": kwargs})
        return {"content": "ok"}


class TestL5OnlyObservations(unittest.TestCase):
    """Falsifier for T-76: repo.* observations land in L5 only and never perturb L1-L3."""

    def setUp(self) -> None:
        self.repo_contents = {
            "pkg/core.py": (
                "class CoreService:\n"
                "    def run(self):\n"
                "        return helper()\n"
            ),
            "pkg/util.py": (
                "def helper():\n"
                "    return 42\n"
            ),
            "tests/test_core.py": (
                "from pkg.core import CoreService\n"
                "def test_run():\n"
                "    assert CoreService().run() == 42\n"
            ),
        }
        self.index = InMemoryRepoIndex(self.repo_contents)
        self.provider = CodeBindingProvider()
        self.task = TaskContext(
            brief="investigate repository",
            repo_path=Path("/workspace"),
            project_id="p-t76",
            run_id="run-t76",
            episode_id="ep-t76",
            principal="principal-test",
        )
        self.compiler = ContextCompiler(
            system_core="You are a verified engineering agent.",
            capability_cards="[CAPABILITY: repo tools available]",
            token_ceiling=8000,
        )
        self.clock = DummyClock()
        self.model = DummyModel()
        self.operator = _LayeredOperator(
            model=self.model,
            compiler=self.compiler,
            task=self.task,
            clock=self.clock,
        )

    def test_repo_verbs_execute_and_return_outcomes(self) -> None:
        """Verify CodeBindingProvider instantiates and executes all four repo verbs."""
        for verb in (
            "repo.search_symbols",
            "repo.get_callers",
            "repo.get_dependencies",
            "repo.get_tests",
        ):
            adapter = self.provider.create_adapter(verb, environment=None, index=self.index)
            self.assertTrue(adapter.healthy())

        # 1. repo.search_symbols
        adapter = self.provider.create_adapter("repo.search_symbols", None, index=self.index)
        req = ObservationRequest(action="search_symbols", args={"name": "helper"})
        outcome = adapter.execute(req)
        self.assertEqual(outcome.status, "ok")
        self.assertIn("helper", outcome.detail)

        # 2. repo.get_callers
        adapter = self.provider.create_adapter("repo.get_callers", None, index=self.index)
        req = ObservationRequest(action="get_callers", args={"symbol": "helper"})
        outcome = adapter.execute(req)
        self.assertEqual(outcome.status, "ok")
        self.assertIn("run", outcome.detail)

        # 3. repo.get_dependencies
        adapter = self.provider.create_adapter("repo.get_dependencies", None, index=self.index)
        req = ObservationRequest(action="get_dependencies", args={"path": "pkg/core.py"})
        outcome = adapter.execute(req)
        self.assertEqual(outcome.status, "ok")

        # 4. repo.get_tests
        adapter = self.provider.create_adapter("repo.get_tests", None, index=self.index)
        req = ObservationRequest(action="get_tests", args={"path": "pkg/core.py"})
        outcome = adapter.execute(req)
        self.assertEqual(outcome.status, "ok")

    def test_ten_turns_of_observations_keep_l1_l3_prefix_bit_identical(self) -> None:
        """10 turns with all 4 observations admitted to L5 maintain a constant prefix digest."""
        queries = [
            ("repo.search_symbols", {"name": "CoreService"}),
            ("repo.search_symbols", {"name": "helper"}),
            ("repo.get_callers", {"symbol": "helper"}),
            ("repo.get_callers", {"symbol": "run"}),
            ("repo.get_dependencies", {"path": "pkg/core.py"}),
            ("repo.get_dependencies", {"path": "pkg/util.py"}),
            ("repo.get_tests", {"path": "pkg/core.py"}),
            ("repo.get_tests", {"path": "tests/test_core.py"}),
            ("repo.search_symbols", {"path": "pkg/"}),
            ("repo.get_callers", {"symbol": "CoreService"}),
        ]
        self.assertEqual(len(queries), 10)

        prefix_digests: list[str] = []
        l1_l3_contents: list[list[str]] = []

        for turn, (verb, args) in enumerate(queries):
            # 1. Execute observation through adapter
            adapter = self.provider.create_adapter(verb, None, index=self.index)
            req = ObservationRequest(action=verb.split(".")[-1], args=args)
            outcome = adapter.execute(req)
            self.assertEqual(outcome.status, "ok")

            # Double object wrapping outcome as engine/session does
            class DispatchResult:
                def __init__(self, out):
                    self.outcome = out
                    self.detail = out.detail

            # 2. Admit turn result into operator
            _admit_turn_result(self.operator, turn, DispatchResult(outcome))

            # 3. Assemble prompt vector
            bundle, compiled = self.operator._assembler.assemble(view={}, turn=turn)

            # 4. Verify all tool observations are in Layer.DIALOGUE (L5)
            dialogue_blocks = compiled.layer_blocks(Layer.DIALOGUE)
            self.assertTrue(any(f"tool-result-{turn}" in b.label for b in dialogue_blocks))

            # 5. Verify NO tool observations appear in L1-L3 (SYSTEM, TOOLS, ENVIRONMENT)
            for l in PREFIX_LAYERS:
                blocks = compiled.layer_blocks(l)
                for b in blocks:
                    self.assertNotIn("tool-result", b.label)
                    self.assertNotIn("tool result turn=", b.text)

            prefix_digests.append(compiled.prefix_digest)

            # Extract exact text of L1-L3 blocks
            prefix_texts = [
                f"{b.layer.value}:{b.label}:{b.text}"
                for b in compiled.blocks
                if b.layer in PREFIX_LAYERS
            ]
            l1_l3_contents.append(prefix_texts)

        # Invariant: Every prefix digest must be identical across all 10 turns
        self.assertEqual(len(set(prefix_digests)), 1, f"Prefix digest changed: {prefix_digests}")
        # Invariant: Every L1-L3 content block must be identical
        for i in range(1, 10):
            self.assertEqual(l1_l3_contents[i], l1_l3_contents[0])

    def test_adversarial_prefix_mutation_breaks_equality(self) -> None:
        """Negative control: proves the falsifier detects any leak of dynamic data into L1-L3."""
        bundle0, compiled0 = self.operator._assembler.assemble(view={}, turn=0)
        digest0 = compiled0.prefix_digest

        # Inject a dynamic block into compiler prefix
        from vanguard.packages.agency.context.layers import Block
        mutated_prefix = list(self.compiler._prefix) + [
            Block(layer=Layer.ENVIRONMENT, source="leak", label="leaked_obs", text="mutated")
        ]
        self.compiler._prefix = tuple(mutated_prefix)

        bundle1, compiled1 = self.operator._assembler.assemble(view={}, turn=1)
        digest1 = compiled1.prefix_digest

        self.assertNotEqual(digest0, digest1, "Mutated prefix must produce a different prefix digest")


if __name__ == "__main__":
    unittest.main()
