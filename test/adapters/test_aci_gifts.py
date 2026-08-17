"""Tests for SWE-agent ACI adapter gifts (S8-B-06..S8-B-10, 010 §2)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from vanguard.packages.adapters.environment.git import GitEnvironment
from vanguard.packages.ports.environment import EffectRequest, ObservationRequest


class TestACIGifts(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.repo_dir = Path(self.tmp.name)
        # Initialize a git repo for GitEnvironment
        import subprocess
        subprocess.run(["git", "init"], cwd=self.repo_dir, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "ci@aether.org"], cwd=self.repo_dir, check=True)
        subprocess.run(["git", "config", "user.name", "CI Bot"], cwd=self.repo_dir, check=True)
        self.env = GitEnvironment(repo_path=self.repo_dir)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_s8_b_06_paginated_fs_read(self) -> None:
        """S8-B-06: 5000-line file returns paginated 100 lines + continuation hint."""
        large_file = self.repo_dir / "large.py"
        lines = [f"# Line {i}\n" for i in range(1, 501)]
        large_file.write_text("".join(lines), encoding="utf-8")

        # Read default: first 100 lines + hint
        req_default = ObservationRequest(action="read", path="large.py")
        res_default = self.env.observe(req_default)
        self.assertTrue(res_default.ok)
        obs = res_default.value
        self.assertEqual(obs.metadata["total_lines"], 500)
        self.assertEqual(obs.metadata["limit"], 100)
        self.assertEqual(obs.metadata["offset"], 0)
        self.assertTrue(obs.metadata["has_more"])
        self.assertIn("Line 1", obs.content)
        self.assertIn("Line 100", obs.content)
        self.assertNotIn("Line 101", obs.content)
        self.assertIn("remaining lines. Use offset=100 to continue", obs.content)

        # Read page 2 with offset=100, limit=50
        req_p2 = ObservationRequest(action="read", path="large.py", args={"offset": 100, "limit": 50})
        res_p2 = self.env.observe(req_p2)
        self.assertTrue(res_p2.ok)
        obs_p2 = res_p2.value
        self.assertEqual(obs_p2.metadata["offset"], 100)
        self.assertEqual(obs_p2.metadata["limit"], 50)
        self.assertIn("Line 101", obs_p2.content)
        self.assertIn("Line 150", obs_p2.content)
        self.assertNotIn("Line 151", obs_p2.content)

    def test_s8_b_07_succinct_fs_search(self) -> None:
        """S8-B-07: Search returns ranked file list and capped snippets."""
        f1 = self.repo_dir / "a.py"
        f1.write_text("def target_func():\n    pass\n# target_func comment\n", encoding="utf-8")
        import subprocess
        subprocess.run(["git", "add", "."], cwd=self.repo_dir, check=True)

        req = ObservationRequest(action="search", pattern="target_func")
        res = self.env.observe(req)
        self.assertTrue(res.ok)
        obs = res.value
        self.assertIn("a.py", obs.files)
        self.assertTrue(len(obs.matches) <= 3)

    def test_s8_b_08_empty_output_acknowledgement(self) -> None:
        """S8-B-08: Silent command returns explicit text, not empty string."""
        req = EffectRequest(
            action="exec",
            verb="proc.exec",
            command=["python3", "-c", "pass"],
        )
        res = self.env.apply(req)
        self.assertTrue(res.ok)
        receipt = res.value
        self.assertEqual(receipt.exit_code, 0)
        self.assertEqual(receipt.output, "Command executed successfully with no output.")

    def test_s8_b_09_lint_on_patch_as_observation_receipt(self) -> None:
        """S8-B-09: Syntax issue on patch is returned as observation receipt, never a verdict (A-05)."""
        bad_syntax_patch = (
            "diff --git a/syntax_err.py b/syntax_err.py\n"
            "new file mode 100644\n"
            "--- /dev/null\n"
            "+++ b/syntax_err.py\n"
            "@@ -0,0 +1,2 @@\n"
            "+def broken_syntax(\n"
            "+    return 42\n"
        )
        req = EffectRequest(
            action="patch",
            verb="patch.apply",
            patch=bad_syntax_patch,
        )
        res = self.env.apply(req)
        # Patch succeeds as an effect, and records syntax warning in receipt output (observation)
        self.assertTrue(res.ok)
        receipt = res.value
        self.assertEqual(receipt.outcome, "ok")
        self.assertIsNotNone(receipt.output)
        self.assertIn("syntax_observation", receipt.output)


if __name__ == "__main__":
    unittest.main()
