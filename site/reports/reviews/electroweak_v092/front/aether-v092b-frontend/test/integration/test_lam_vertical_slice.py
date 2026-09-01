"""Integration test for offline LAM (Local Agent Mock) vertical slice.

Owning contract: S6B-MD-002, LAM-VERTICAL, REQ-PORT-006.
Proves end-to-end execution of a multi-turn task (read -> patch -> test -> finish)
driven by real tool observations against a concrete repository.
"""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from vanguard.packages.adapters.models.lam import LamModelAdapter


class TestLamVerticalSlice(unittest.TestCase):
    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self.repo = Path(self._tempdir.name)

        # Create broken calculator repository
        calc_py = self.repo / "calc.py"
        calc_py.write_text(
            "def total(items):\n    acc = 1\n    for x in items:\n        acc += x\n    return acc\n",
            encoding="utf-8",
        )
        test_calc_py = self.repo / "test_calc.py"
        test_calc_py.write_text(
            "import unittest\nfrom calc import total\n\nclass TestCalc(unittest.TestCase):\n    def test_total(self):\n        self.assertEqual(total([1, 2, 3]), 6)\n\nif __name__ == '__main__':\n    unittest.main()\n",
            encoding="utf-8",
        )

        subprocess.run(["git", "init"], cwd=self.repo, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Vanguard Test"], cwd=self.repo, check=True)
        subprocess.run(
            ["git", "config", "user.email", "test@vanguard.dev"], cwd=self.repo, check=True
        )
        subprocess.run(["git", "add", "."], cwd=self.repo, check=True)
        subprocess.run(["git", "commit", "-m", "broken"], cwd=self.repo, check=True)

    def tearDown(self) -> None:
        self._tempdir.cleanup()

    def test_lam_model_adapter_propose_multi_turn(self) -> None:
        adapter = LamModelAdapter(model_name="lam/t1-calculator")

        # Turn 1: initial task -> proposes fs.read
        context_turn_1 = [{"role": "user", "content": "Fix calc.py bug"}]
        res_1 = adapter.propose(context_turn_1, tools=())
        self.assertTrue(res_1.ok)
        prop_1 = res_1.value
        self.assertEqual(prop_1["kind"], "effect")
        self.assertEqual(prop_1["action"], "fs.read")

        # Turn 2: observation provided -> proposes patch.apply
        context_turn_2 = [
            {"role": "user", "content": "Fix calc.py bug"},
            {"role": "tool", "content": "def total(items):\n    acc = 1\n..."},
        ]
        res_2 = adapter.propose(context_turn_2, tools=())
        self.assertTrue(res_2.ok)
        prop_2 = res_2.value
        self.assertEqual(prop_2["kind"], "effect")
        self.assertEqual(prop_2["action"], "patch.apply")

        # Turn 3: patch applied -> proposes test
        context_turn_3 = [
            {"role": "user", "content": "Fix calc.py bug"},
            {"role": "tool", "content": "file read"},
            {"role": "tool", "content": "patch applied successfully"},
        ]
        res_3 = adapter.propose(context_turn_3, tools=())
        self.assertTrue(res_3.ok)
        prop_3 = res_3.value
        self.assertEqual(prop_3["kind"], "effect")
        self.assertIn(prop_3["action"], ("proc.test", "proc.exec"))

        # Turn 4: test passed -> proposes finish
        context_turn_4 = [
            {"role": "user", "content": "Fix calc.py bug"},
            {"role": "tool", "content": "file read"},
            {"role": "tool", "content": "patch applied"},
            {"role": "tool", "content": "OK (ran 1 test)"},
        ]
        res_4 = adapter.propose(context_turn_4, tools=())
        self.assertTrue(res_4.ok)
        prop_4 = res_4.value
        self.assertEqual(prop_4["kind"], "finish")


if __name__ == "__main__":
    unittest.main()
