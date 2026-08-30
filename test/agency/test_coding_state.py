import unittest

from vanguard.packages.runtime.task_state import CodingTaskState


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
