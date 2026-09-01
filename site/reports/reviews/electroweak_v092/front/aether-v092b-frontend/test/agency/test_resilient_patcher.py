"""Unit and contract tests for the 9-Strategy Resilient Patcher."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from vanguard.packages.agency.forge.patcher import ForgeAtomicPatcher
from vanguard.packages.agency.forge.resilient_patcher import (
    PatchOutcome,
    ResilientPatcher,
    collapse_whitespace,
    normalize_unicode,
)


class TestResilientPatcherStrategies(unittest.TestCase):
    """Test each of the 9 fuzzy matching strategies independently and robustly."""

    def test_strategy_1_exact_match(self) -> None:
        original = (
            "def calculate(a, b):\n"
            "    # Simple addition\n"
            "    return a + b\n"
        )
        target = "    # Simple addition\n    return a + b"
        replacement = "    # Fast addition\n    return int(a) + int(b)"

        outcome = ResilientPatcher.apply_patch(original, target, replacement, file_path="calc.py")
        self.assertTrue(outcome.success)
        self.assertEqual(outcome.strategy_used, "exact_match")
        self.assertIn("int(a) + int(b)", outcome.modified_content)

    def test_strategy_2_line_trimmed(self) -> None:
        original = (
            "def process(items):\n"
            "    results = []    \n"
            "    for item in items:   \n"
            "        results.append(item * 2)\n"
            "    return results\n"
        )
        # Target with different trailing whitespaces but matching base indentation
        target = (
            "    results = []\n"
            "    for item in items:\n"
            "        results.append(item * 2)"
        )
        replacement = (
            "    results = [item * 2 for item in items]"
        )

        outcome = ResilientPatcher.apply_patch(original, target, replacement, file_path="proc.py")
        self.assertTrue(outcome.success)
        self.assertEqual(outcome.strategy_used, "line_trimmed")
        self.assertIn("[item * 2 for item in items]", outcome.modified_content)

    def test_strategy_3_whitespace_normalized(self) -> None:
        original = (
            "def execute(query,    params):\n"
            "    cursor   =   db.cursor()\n"
            "    return cursor.execute(query, params)\n"
        )
        # Target with collapsed single spaces
        target = (
            "def execute(query, params):\n"
            "    cursor = db.cursor()\n"
            "    return cursor.execute(query, params)"
        )
        replacement = (
            "def execute(query, params):\n"
            "    with db.cursor() as cursor:\n"
            "        return cursor.execute(query, params)"
        )

        outcome = ResilientPatcher.apply_patch(original, target, replacement, file_path="db.py")
        self.assertTrue(outcome.success)
        self.assertEqual(outcome.strategy_used, "whitespace_normalized")
        self.assertIn("with db.cursor() as cursor:", outcome.modified_content)

    def test_strategy_4_indent_flexible(self) -> None:
        original = (
            "class Worker:\n"
            "    def run(self):\n"
            "        # nested at 8 spaces\n"
            "        if True:\n"
            "            value = compute()\n"
            "            return value\n"
        )
        # Target formatted at 2-space base indent
        target = (
            "if True:\n"
            "  value = compute()\n"
            "  return value"
        )
        # Replacement with 2-space relative indent
        replacement = (
            "if True:\n"
            "  value = fast_compute()\n"
            "  return value"
        )

        outcome = ResilientPatcher.apply_patch(original, target, replacement, file_path="worker.py")
        self.assertTrue(outcome.success)
        self.assertEqual(outcome.strategy_used, "indent_flexible")
        self.assertIn("fast_compute()", outcome.modified_content)

    def test_strategy_5_unicode_normalized(self) -> None:
        original = (
            'MSG = "Hello World"\n'
            'SEP = "--"\n'
        )
        # Target with smart quotes and em-dash
        target = (
            'MSG = “Hello World”\n'
            'SEP = "—"\n'
        )
        replacement = (
            'MSG = "Hello Vanguard"\n'
            'SEP = "---"\n'
        )

        outcome = ResilientPatcher.apply_patch(original, target, replacement, file_path="config.py")
        self.assertTrue(outcome.success)
        self.assertEqual(outcome.strategy_used, "unicode_normalized")
        self.assertIn('"Hello Vanguard"', outcome.modified_content)

    def test_strategy_6_boundary_trimmed(self) -> None:
        original = (
            "def setup():\n"
            "    init_db()\n"
            "    # comment\n"
            "    init_cache()\n"
            "    init_routes()\n"
        )
        # Target matching first & last boundary lines
        target = (
            "def setup():\n"
            "    init_db()\n"
            "    init_routes()"
        )
        replacement = (
            "def setup():\n"
            "    init_all()"
        )

        outcome = ResilientPatcher.apply_patch(original, target, replacement, file_path="setup.py")
        self.assertTrue(outcome.success)
        self.assertEqual(outcome.strategy_used, "boundary_trimmed")
        self.assertIn("init_all()", outcome.modified_content)

    def test_strategy_7_block_anchors(self) -> None:
        original = (
            "def authenticate(user, password):\n"
            "    # Step 1: verify salt\n"
            "    salt = get_user_salt(user.id)\n"
            "    h = hash_pw(password, salt)\n"
            "    # Step 2: verify digest\n"
            "    return h == user.password_hash\n"
        )
        # Target has matching first & last lines, but interior is slightly different (>= 0.75 similarity)
        target = (
            "    # Step 1: verify salt\n"
            "    salt = get_salt(user.id)\n"
            "    h = hash_pw(password, salt)\n"
            "    # Step 2: verify digest"
        )
        replacement = (
            "    # Step 1: constant-time verify\n"
            "    return secure_verify(user, password)"
        )

        outcome = ResilientPatcher.apply_patch(original, target, replacement, file_path="auth.py")
        self.assertTrue(outcome.success)
        self.assertEqual(outcome.strategy_used, "block_anchors")
        self.assertIn("secure_verify(user, password)", outcome.modified_content)

    def test_strategy_8_ast_node(self) -> None:
        original = (
            "import os\n\n"
            "def helper_old(x):\n"
            "    return x + 1\n\n"
            "def transform(data):\n"
            "    # complex legacy logic\n"
            "    temp = []\n"
            "    for d in data:\n"
            "        temp.append(d.lower())\n"
            "    return temp\n\n"
            "def helper_other(y):\n"
            "    return y * 2\n"
        )
        # Target does not match the lines directly, but replacement defines transform(data)
        target = (
            "def transform(data):\n"
            "    pass"
        )
        replacement = (
            "def transform(data):\n"
            "    return [item.strip().lower() for item in data]"
        )

        outcome = ResilientPatcher.apply_patch(original, target, replacement, file_path="pipeline.py")
        self.assertTrue(outcome.success)
        self.assertEqual(outcome.strategy_used, "ast_node")
        self.assertIn("item.strip().lower()", outcome.modified_content)
        self.assertIn("helper_old", outcome.modified_content)
        self.assertIn("helper_other", outcome.modified_content)

    def test_strategy_9_context_aware(self) -> None:
        original = (
            "# Header\n"
            "ALPHA = 10\n"
            "BETA = 20\n"
            "GAMMA = 30\n"
            "DELTA = 40\n"
            "# Footer\n"
        )
        # Target has approximate sequence similarity (>= 50%) but first/last line mismatch
        target = (
            "ALPHA_OLD = 10\n"
            "BETA = 20\n"
            "GAMMA = 30\n"
            "DELTA_OLD = 40"
        )
        replacement = (
            "ALPHA = 100\n"
            "BETA = 200\n"
            "GAMMA = 300\n"
            "DELTA = 400"
        )

        outcome = ResilientPatcher.apply_patch(original, target, replacement, file_path="constants.py")
        self.assertTrue(outcome.success)
        self.assertEqual(outcome.strategy_used, "context_aware")
        self.assertIn("ALPHA = 100", outcome.modified_content)

    def test_syntax_error_rollback(self) -> None:
        original = (
            "def valid_func(x):\n"
            "    return x + 1\n"
        )
        target = "return x + 1"
        # Invalid syntax in replacement: unclosed parenthesis
        replacement = "return (x + 1"

        outcome = ResilientPatcher.apply_patch(original, target, replacement, file_path="func.py")
        self.assertFalse(outcome.success)
        self.assertEqual(outcome.modified_content, original)
        self.assertEqual(outcome.strategy_used, "failed_all_strategies")
        self.assertIsNotNone(outcome.error_message)
        self.assertIn("Syntax", outcome.error_message)

    def test_empty_target_chunk(self) -> None:
        original = "print('hello')\n"
        outcome = ResilientPatcher.apply_patch(original, "   ", "print('world')\n")
        self.assertFalse(outcome.success)
        self.assertEqual(outcome.strategy_used, "none")
        self.assertEqual(outcome.error_message, "Target chunk is empty.")

    def test_atomic_patcher_integration(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            ws = Path(tmp_dir)
            target_file = ws / "module.py"
            target_file.write_text("def solve():\n    return 41\n", encoding="utf-8")

            patcher = ForgeAtomicPatcher(ws)
            res = patcher.apply_resilient_patch(
                rel_path="module.py",
                target_chunk="return 41",
                replacement_chunk="return 42",
            )
            self.assertTrue(res.success)
            self.assertEqual(target_file.read_text(encoding="utf-8"), "def solve():\n    return 42\n")


if __name__ == "__main__":
    unittest.main()
