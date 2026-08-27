"""RF-97: the trusted-core gate measures the transitive executable closure."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class TcbBudgetV2(unittest.TestCase):
    def test_closure_is_transitive_and_domain_blind(self) -> None:
        result = subprocess.run(
            [sys.executable, "tools/linters/check_tcb_budget.py", "--v2"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        receipt = json.loads(result.stdout.splitlines()[0])
        self.assertEqual(receipt["rf"], "RF-97")
        self.assertEqual(receipt["version"], 2)
        self.assertIn("vanguard/packages/domain/canonicalisation/jcs.py", receipt["closure"])
        self.assertIn("vanguard/packages/domain/selectors/resource_selector.py", receipt["closure"])
        self.assertEqual(receipt["domain_concepts"], [])
        self.assertEqual(receipt["extension_knowledge"], [])
        self.assertGreater(receipt["public_contracts"], 0)
        self.assertGreater(receipt["privileged_ops"], 0)


if __name__ == "__main__":
    unittest.main()
