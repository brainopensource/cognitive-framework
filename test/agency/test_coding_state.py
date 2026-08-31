import unittest

from vanguard.packages.runtime.task_state import CodingTaskState, DeadEnd, Discovery, RouteDecision, TodoItem


class TestCodingTaskState(unittest.TestCase):
    def test_round_trip_and_digest_are_stable(self) -> None:
        state = CodingTaskState(
            objective="repair parser", strategy_steps=("inspect", "patch"),
            modified_files=("src/parser.py",),
            remaining_budgets={"tokens": 100},
        )
        restored = CodingTaskState.from_mapping(state.to_canonical_dict())
        self.assertEqual(restored, state)
        self.assertEqual(restored.digest(), state.digest())

    def test_empty_objective_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            CodingTaskState("")

    def test_resume_state_keeps_provenance_dead_ends_and_route_failures(self) -> None:
        state = CodingTaskState(
            objective="repair parser", task_class="bugfix",
            completion_requirements=("patch", "verification"),
            discoveries=(Discovery("parser is hand-written", "src/parser.py:12", .9),),
            dead_ends=(DeadEnd("regex-only repair", "missed escaped input", "test/parser.py"),),
            implicated_files=("src/parser.py",), change_surface=("src/parser.py", "test/parser.py"),
            todo_items=(TodoItem("edit", "apply parser fix"),),
            route_decisions=(RouteDecision("openrouter/free", "discovery", "provider_unavailable"),),
        )
        restored = CodingTaskState.from_mapping(state.to_canonical_dict())
        self.assertEqual(restored, state)

    def test_todo_completion_is_evidence_gated(self) -> None:
        state = CodingTaskState(
            objective="repair parser", completion_requirements=("verification",),
            todo_items=(TodoItem("verify", "run targeted tests"),),
        )
        with self.assertRaises(ValueError):
            state.transition_todo("verify", "complete", receipt_digest="sha256:patch")
        completed = state.transition_todo("verify", "complete", receipt_digest="sha256:test", verification_fresh=True)
        self.assertEqual(completed.todo_items[0].status, "complete")
