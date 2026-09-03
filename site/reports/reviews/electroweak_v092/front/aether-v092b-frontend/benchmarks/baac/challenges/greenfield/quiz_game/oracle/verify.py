#!/usr/bin/env python3
"""External Oracle for greenfield quiz_game challenge.

NEVER leaked to the agent.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile
import unittest


class TestQuizEngineOracle(unittest.TestCase):
    ws_path: Path

    def setUp(self) -> None:
        sys.path.insert(0, str(self.ws_path))
        sys.path.insert(0, str(self.ws_path / "src"))

    def test_quiz_engine_lifecycle(self) -> None:
        from quiz_engine import Question, QuizEngine  # type: ignore

        questions_data = [
            {
                "id": "q1",
                "prompt": "What is the capital of France?",
                "options": ["A. London", "B. Paris", "C. Berlin", "D. Rome"],
                "correct_choice": "B",
                "points": 10,
            },
            {
                "id": "q2",
                "prompt": "Which planet is known as the Red Planet?",
                "options": ["A. Venus", "B. Mars", "C. Jupiter", "D. Saturn"],
                "correct_choice": "b",
                "points": 20,
            },
            {
                "id": "q3",
                "prompt": "What is 2 + 2?",
                "options": ["A. 3", "B. 4", "C. 5"],
                "correct_choice": "B",
                "points": 10,
            },
        ]

        engine = QuizEngine(questions_data)
        self.assertFalse(engine.is_finished())
        self.assertEqual(engine.current_question().id, "q1")

        # Answer Q1 correctly
        res1 = engine.submit_answer("b")
        self.assertTrue(res1["correct"])
        self.assertEqual(res1["earned_points"], 10)
        self.assertEqual(engine.current_question().id, "q2")

        # Answer Q2 incorrectly
        res2 = engine.submit_answer("A")
        self.assertFalse(res2["correct"])
        self.assertEqual(res2["earned_points"], 0)
        self.assertEqual(engine.current_question().id, "q3")

        # Answer Q3 correctly
        res3 = engine.submit_answer("B ")
        self.assertTrue(res3["correct"])
        self.assertEqual(res3["earned_points"], 10)

        # Finished state
        self.assertTrue(engine.is_finished())
        self.assertIsNone(engine.current_question())

        score = engine.get_score()
        self.assertEqual(score["total_points"], 40)
        self.assertEqual(score["earned_points"], 20)
        self.assertEqual(score["score_pct"], 50.0)
        self.assertEqual(score["answered"], 3)
        self.assertEqual(score["total_questions"], 3)

        # Call submit_answer when finished should raise RuntimeError
        with self.assertRaises(RuntimeError):
            engine.submit_answer("A")

        # Test Reset
        engine.reset()
        self.assertFalse(engine.is_finished())
        self.assertEqual(engine.current_question().id, "q1")
        score_reset = engine.get_score()
        self.assertEqual(score_reset["earned_points"], 0)

    def test_json_loading(self) -> None:
        from quiz_engine import QuizEngine  # type: ignore

        data = [
            {"id": "t1", "prompt": "Test?", "options": ["A", "B"], "correct_choice": "A", "points": 5}
        ]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tf:
            json.dump(data, tf)
            fpath = Path(tf.name)

        try:
            engine = QuizEngine.load_from_json(fpath)
            self.assertEqual(engine.current_question().id, "t1")
            r = engine.submit_answer("A")
            self.assertTrue(r["correct"])
            self.assertTrue(engine.is_finished())
        finally:
            if fpath.exists():
                fpath.unlink()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".", help="Target workspace path")
    args = parser.parse_args()

    ws = Path(args.workspace).resolve()
    TestQuizEngineOracle.ws_path = ws

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestQuizEngineOracle)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
