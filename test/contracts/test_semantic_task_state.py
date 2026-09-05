"""T-09: domain SemanticTaskState is stdlib + JCS, merged with CodingTaskState."""

from __future__ import annotations

import importlib
import unittest

from vanguard.packages.domain.canonicalisation.jcs import canonicalise
from vanguard.packages.domain.task_state import (
    CodingTaskState,
    SemanticTaskState,
    StepState,
    TaskStep,
)


class TestSemanticTaskState(unittest.TestCase):
    def test_module_is_stdlib_plus_jcs(self) -> None:
        module = importlib.import_module("vanguard.packages.domain.task_state")
        forbidden = {
            name
            for name, value in vars(module).items()
            if getattr(value, "__module__", "").startswith(
                ("vanguard.packages.runtime", "vanguard.packages.adapters",
                 "vanguard.packages.agency", "vanguard.packages.kernel")
            )
        }
        self.assertEqual(forbidden, set())

    def test_coding_task_state_is_the_same_schema(self) -> None:
        self.assertIs(CodingTaskState, SemanticTaskState)

    def test_jcs_round_trip_and_digest_are_stable(self) -> None:
        state = SemanticTaskState(
            objective="repair parser",
            run_id="run-1",
            revision=2,
            backlog=(TaskStep("step-001", "inspect parser", ("src/parser.py",)),),
            falsified_hypotheses=("regex-only repair",),
            settled_invariants=("parser is hand-written",),
            changed_files_tree_hash="sha256:" + "a" * 64,
            task_class="bugfix",
        )
        restored = SemanticTaskState.from_mapping(state.to_canonical_dict())
        self.assertEqual(restored, state)
        self.assertEqual(canonicalise(state.to_canonical_dict()),
                         canonicalise(restored.to_canonical_dict()))
        self.assertEqual(state.digest(), restored.digest())
        self.assertEqual(state.overarching_goal, "repair parser")

    def test_task_step_and_step_state_are_immutable_values(self) -> None:
        step = TaskStep("step-001", "inspect", ("a.py",), state=StepState.READY)
        self.assertEqual(step.state, StepState.READY)
        with self.assertRaises(AttributeError):
            step.title = "mutated"  # type: ignore[misc]

    def test_empty_objective_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            SemanticTaskState("")


if __name__ == "__main__":
    unittest.main()
