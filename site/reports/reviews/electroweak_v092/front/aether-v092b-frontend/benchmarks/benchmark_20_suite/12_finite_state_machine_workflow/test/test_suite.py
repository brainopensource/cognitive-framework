import unittest
from src.fsm import StateMachine, InvalidTransitionError

class TestStateMachine(unittest.TestCase):
    def test_valid_transitions(self):
        fsm = StateMachine(initial_state="draft")
        fsm.add_transition("draft", "submit", "in_review")
        fsm.add_transition("in_review", "approve", "published")

        self.assertEqual(fsm.trigger("submit"), "in_review")
        self.assertEqual(fsm.trigger("approve"), "published")
        self.assertEqual(fsm.current_state, "published")
        self.assertEqual(len(fsm.history), 2)

    def test_guard_condition(self):
        fsm = StateMachine(initial_state="draft")
        fsm.add_transition("draft", "submit", "in_review", guard=lambda user: user == "admin")

        with self.assertRaises(InvalidTransitionError):
            fsm.trigger("submit", user="guest")

        self.assertEqual(fsm.trigger("submit", user="admin"), "in_review")

    def test_invalid_event_raises(self):
        fsm = StateMachine(initial_state="draft")
        with self.assertRaises(InvalidTransitionError):
            fsm.trigger("unknown_event")

if __name__ == "__main__":
    unittest.main()
