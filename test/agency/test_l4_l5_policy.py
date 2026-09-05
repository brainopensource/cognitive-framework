"""T-15: FEATURE_SPEC 4-tier is L4/L5 policy on the existing ContextCompiler."""

from __future__ import annotations

import inspect
import unittest

from vanguard.packages.agency.context import (
    ContextBudgetExceeded,
    ContextCompiler,
    Fragment,
    Layer,
    estimate_tokens,
)
from vanguard.packages.agency.context import compiler as compiler_mod
from vanguard.packages.agency.context import compaction as compaction_mod

from test.agency.test_context_compiler import SYSTEM_CORE, TOOLS, ENVIRONMENT, build, dialogue


class ProgressivePolicyOnExistingCompiler(unittest.TestCase):
    def test_no_second_compiler_class(self) -> None:
        compiler_classes = [
            name for name, obj in inspect.getmembers(compiler_mod, inspect.isclass)
            if name.endswith("Compiler")
        ]
        self.assertEqual(compiler_classes, ["ContextCompiler"])
        self.assertFalse(hasattr(compiler_mod, "ProgressiveContextCompiler"))
        self.assertFalse(hasattr(compaction_mod, "ProgressiveContextCompiler"))

    def test_settled_invariants_and_dead_ends_survive_compaction(self) -> None:
        floor = build().compile(brief="implement the store").total_tokens
        notes = (
            Fragment(
                source="settled-invariant",
                label="inv-checksum",
                text="checksum must stay monotonic",
                evictable=False,
            ),
            Fragment(
                source="dead-end",
                label="dead-regex",
                text="regex parser rejected by the oracle",
                evictable=False,
            ),
            Fragment(
                source="falsified-hypothesis",
                label="hyp-sort",
                text="sorting dict keys is not JCS",
                evictable=False,
            ),
            Fragment(source="operator", label="scratch", text="scratch " * 40),
        )
        pinned_cost = sum(
            estimate_tokens(item.text) for item in notes if item.source != "operator"
        )
        ceiling = floor + pinned_cost + 8
        compiled = build(token_ceiling=ceiling).compile(
            brief="implement the store",
            notes=notes,
            dialogue=dialogue(40, size=400),
        )
        labels = [block.label for block in compiled.layer_blocks(Layer.TASK)]
        self.assertIn("inv-checksum", labels)
        self.assertIn("dead-regex", labels)
        self.assertIn("hyp-sort", labels)
        self.assertLessEqual(compiled.total_tokens, ceiling)
        dropped_task = [
            label for label in compiled.dropped
            if label in {"inv-checksum", "dead-regex", "hyp-sort"}
        ]
        self.assertEqual(dropped_task, [])

    def test_budget_caps_on_l5_only(self) -> None:
        floor = build().compile(brief="implement the store").total_tokens
        invariant = Fragment(
            source="settled-invariant",
            label="inv-checksum",
            text="checksum must stay monotonic",
            evictable=False,
        )
        ceiling = floor + estimate_tokens(invariant.text) + 12
        compiled = build(token_ceiling=ceiling).compile(
            brief="implement the store",
            notes=(invariant,),
            dialogue=dialogue(20, size=400),
        )
        self.assertEqual(compiled.layer_blocks(Layer.DIALOGUE)[-1].source, "goal-echo")
        self.assertEqual(
            [block.source for block in compiled.layer_blocks(Layer.DIALOGUE) if block.source != "goal-echo"],
            [],
        )
        self.assertIn("inv-checksum", [block.label for block in compiled.layer_blocks(Layer.TASK)])
        self.assertTrue(compiled.dropped)
        self.assertNotIn("inv-checksum", compiled.dropped)

    def test_invariants_sit_at_l4_head_after_the_brief(self) -> None:
        compiled = build().compile(
            brief="implement the store",
            notes=(
                Fragment(source="operator", label="later-note", text="working scratch"),
                Fragment(
                    source="settled-invariant",
                    label="inv-checksum",
                    text="checksum must stay monotonic",
                    evictable=False,
                ),
                Fragment(
                    source="dead-end",
                    label="dead-regex",
                    text="regex parser rejected",
                    evictable=False,
                ),
            ),
        )
        task_labels = [block.label for block in compiled.layer_blocks(Layer.TASK)]
        self.assertEqual(task_labels[:3], ["brief", "inv-checksum", "dead-regex"])

    def test_pinned_l4_that_cannot_fit_fails_closed(self) -> None:
        invariant = Fragment(
            source="settled-invariant",
            label="inv-huge",
            text="pin " * 4000,
            evictable=False,
        )
        floor = build().compile(brief="implement the store").total_tokens
        with self.assertRaises(ContextBudgetExceeded):
            build(token_ceiling=floor + 4).compile(
                brief="implement the store",
                notes=(invariant,),
            )


if __name__ == "__main__":
    unittest.main()
