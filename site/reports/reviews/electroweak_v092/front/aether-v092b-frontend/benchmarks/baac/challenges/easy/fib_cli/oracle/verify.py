#!/usr/bin/env python3
"""External Oracle for fib_cli challenge.

NEVER leaked to the agent.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys
import unittest


class TestFibOracle(unittest.TestCase):
    ws_path: Path

    def setUp(self) -> None:
        sys.path.insert(0, str(self.ws_path))
        sys.path.insert(0, str(self.ws_path / "src"))

    def test_fib_values(self) -> None:
        from fib import fib  # type: ignore

        expected = [
            (0, 0),
            (1, 1),
            (2, 1),
            (3, 2),
            (4, 3),
            (5, 5),
            (10, 55),
            (20, 6765),
            (30, 832040),
        ]
        for n, val in expected:
            self.assertEqual(fib(n), val, f"fib({n}) must be {val}")

    def test_fib_exceptions(self) -> None:
        from fib import fib  # type: ignore

        with self.assertRaises(ValueError):
            fib(-1)
        with self.assertRaises(ValueError):
            fib(-10)
        with self.assertRaises(TypeError):
            fib("invalid")  # type: ignore

    def test_cli_execution(self) -> None:
        fib_script = self.ws_path / "src" / "fib.py"
        self.assertTrue(fib_script.is_file(), "src/fib.py must exist")

        # Test valid CLI run
        proc = subprocess.run(
            [sys.executable, str(fib_script), "--n", "10"],
            cwd=self.ws_path,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(proc.stdout.strip(), "55")

        # Test negative CLI run
        proc_neg = subprocess.run(
            [sys.executable, str(fib_script), "--n", "-5"],
            cwd=self.ws_path,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(proc_neg.returncode, 0)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".", help="Target workspace path")
    args = parser.parse_args()

    ws = Path(args.workspace).resolve()
    TestFibOracle.ws_path = ws

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestFibOracle)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
