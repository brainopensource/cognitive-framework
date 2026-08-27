"""Hermetic tests for the bounded LAM live-coding collector."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LAM = ROOT / "tools" / "002_LLM_API_MOCK"
if str(LAM) not in sys.path:
    sys.path.insert(0, str(LAM))

from live_coding import (  # noqa: E402
    Budget,
    CollectionLimit,
    _run_command,
    _text_diff,
    execute_tool,
    load_challenge,
)


class BudgetTests(unittest.TestCase):
    def test_call_limit_is_hard(self) -> None:
        budget = Budget(max_calls=1, max_usd=1.0)
        budget.reserve()
        with self.assertRaises(CollectionLimit):
            budget.reserve()

    def test_spend_limit_is_hard(self) -> None:
        budget = Budget(max_calls=2, max_usd=0.1)
        with self.assertRaises(CollectionLimit):
            budget.charge(0.100001)


class WorkspaceSafetyTests(unittest.TestCase):
    def test_file_tools_cannot_escape_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            workspace = Path(raw)
            self.assertIn("escapes", execute_tool(workspace, "view_file", {"path": "../outside"}))

    def test_shell_operators_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            self.assertIn("shell operators", _run_command(Path(raw), "python3 -c 'print(1)' && pwd"))

    def test_diff_reports_changed_files(self) -> None:
        diff = _text_diff({"a.py": "return 1\n"}, {"a.py": "return 2\n"})
        self.assertIn("--- a/a.py", diff)
        self.assertIn("+return 2", diff)


class ChallengeLoadingTests(unittest.TestCase):
    def test_loads_reference_challenge_without_mutating_it(self) -> None:
        challenge = load_challenge(ROOT.parent / "LEX_LLM_EXECUTION" / "lab", "semver_parser")
        self.assertIn("SemVer", challenge.problem)
        self.assertEqual(challenge.key, "semver_parser")


if __name__ == "__main__":
    unittest.main()
