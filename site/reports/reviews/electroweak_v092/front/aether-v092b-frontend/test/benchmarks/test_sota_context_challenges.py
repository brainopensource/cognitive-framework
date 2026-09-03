from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
import unittest

from benchmarks.run_20_eval_suite import run_oracle_test, setup_workspace
from benchmarks.sota_context import CHALLENGES, TIERS


class TestSotaContextChallenges(unittest.TestCase):
    def test_five_unique_challenges_have_broken_public_and_hidden_baselines(self) -> None:
        self.assertEqual(len(CHALLENGES), 5)
        self.assertEqual(sum(len(keys) for keys in TIERS.values()), 5)
        for challenge in CHALLENGES.values():
            with self.subTest(challenge=challenge.challenge_id):
                with tempfile.TemporaryDirectory() as td:
                    workspace = Path(td)
                    setup_workspace(workspace, challenge)
                    public = subprocess.run(
                        ["python3", "-m", "unittest", "discover", "-s", "."],
                        cwd=workspace,
                        capture_output=True,
                        text=True,
                        timeout=20,
                    )
                    hidden_passed, _ = run_oracle_test(
                        workspace,
                        challenge.oracle_code,
                    )
                    self.assertNotEqual(public.returncode, 0)
                    self.assertFalse(hidden_passed)

    def test_large_context_fixture_is_materially_large(self) -> None:
        data = CHALLENGES["sota_hard_large_catalog_collision"].files[
            "catalog/data.py"
        ]
        self.assertGreater(len(data), 200_000)
        self.assertIn("(5999, 'item-42'", data)


if __name__ == "__main__":
    unittest.main()
