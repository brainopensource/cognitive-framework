#!/usr/bin/env python3
"""
Hermetic Python Test Suite for LED AST Evaluator & Surrogate ML Auto-Tuner.
"""

from pathlib import Path
import sys
import unittest

# Add workspace to path
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WORKSPACE_ROOT / "matrix_execution"))

from ast_evaluator import evaluate_python_code
from train_surrogate import train_surrogate_model


class TestAstEvaluator(unittest.TestCase):

    def test_perfect_code_score_100(self):
        code = '''def get_nth_fibonacci(n: int) -> int:
    """Calculates nth Fibonacci number."""
    if n < 0:
        raise ValueError("n must be non-negative")
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b
'''
        res = evaluate_python_code(code)
        self.assertEqual(res["total_score"], 100)
        self.assertEqual(res["syntax_score"], 30)
        self.assertEqual(res["signature_score"], 25)
        self.assertEqual(res["types_score"], 15)
        self.assertEqual(res["error_score"], 15)
        self.assertEqual(res["purity_score"], 15)
        self.assertTrue(res["is_valid"])

    def test_syntax_error_score_0(self):
        bad_code = "def get_nth_fibonacci(n:\n    invalid syntax !!"
        res = evaluate_python_code(bad_code)
        self.assertEqual(res["total_score"], 0)
        self.assertEqual(res["syntax_score"], 0)
        self.assertFalse(res["is_valid"])
        self.assertIn("Syntax: Error", res["feedback"])

    def test_partial_score_missing_types_and_errors(self):
        code = '''def get_nth_fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a
'''
        res = evaluate_python_code(code)
        self.assertEqual(res["syntax_score"], 30)
        self.assertEqual(res["signature_score"], 25)
        self.assertEqual(res["types_score"], 0)
        self.assertEqual(res["error_score"], 0)
        self.assertEqual(res["purity_score"], 15)
        self.assertEqual(res["total_score"], 70)


class TestSurrogateModel(unittest.TestCase):

    def test_surrogate_training_on_doe16(self):
        csv_path = WORKSPACE_ROOT / "bench_finetune/qwen_25C_14B/benchmark_results_16.csv"
        self.assertTrue(csv_path.exists(), f"Missing DoE dataset: {csv_path}")

        res = train_surrogate_model(csv_path, "qwen2.5-coder:14b")
        self.assertEqual(res["status"], "calibrated")
        self.assertEqual(res["target_model"], "qwen2.5-coder:14b")
        self.assertGreater(res["predicted_latency_sec"], 0.0)
        self.assertGreater(res["predicted_tps"], 0.0)
        self.assertGreaterEqual(len(res["feature_importances"]), 5)

        # Check that preset JSON and Modelfile were written
        preset_file = Path(res["preset_path"])
        modelfile = Path(res["modelfile_path"])
        self.assertTrue(preset_file.exists())
        self.assertTrue(modelfile.exists())


if __name__ == "__main__":
    unittest.main()
