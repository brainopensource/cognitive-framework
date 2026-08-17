"""bug-001 oracle must not pass a comment that only contains the formula string."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ORACLE = ROOT / "vanguard/packages/adapters/evaluators/suites/bug-001-single-file/test_oracle.py"


class Bug001OracleBehaviour(unittest.TestCase):
    def _run(self, source: str) -> int:
        tmp = Path(tempfile.mkdtemp())
        src = tmp / "src"
        src.mkdir()
        (src / "calculator.py").write_text(source, encoding="utf-8")
        (tmp / "test_oracle.py").write_text(ORACLE.read_text(encoding="utf-8"), encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, "-m", "unittest", "test_oracle"],
            cwd=tmp,
            capture_output=True,
            text=True,
        )
        return proc.returncode

    def test_comment_only_formula_fails(self) -> None:
        source = 'def calculate(A, B):\n    # (A + B) * B\n    return (A + B) + B\n'
        self.assertNotEqual(self._run(source), 0)

    def test_correct_function_passes(self) -> None:
        source = "def calculate(A, B):\n    return (A + B) * B\n"
        self.assertEqual(self._run(source), 0)


if __name__ == "__main__":
    unittest.main()
