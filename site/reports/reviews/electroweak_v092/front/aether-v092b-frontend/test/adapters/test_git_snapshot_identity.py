from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
import unittest

from vanguard.packages.adapters.environment.git import GitEnvironment


class TestGitSnapshotIdentity(unittest.TestCase):
    def test_repeated_observation_does_not_change_workspace_digest(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "module.py").write_text("VALUE = 1\n", encoding="utf-8")
            for argv in (
                ["git", "init", "-q"],
                ["git", "config", "user.email", "snapshot@example.test"],
                ["git", "config", "user.name", "snapshot-test"],
                ["git", "add", "module.py"],
                ["git", "commit", "-q", "-m", "seed"],
            ):
                subprocess.run(argv, cwd=root, check=True, capture_output=True)
            environment = GitEnvironment(repo_path=root)

            first = environment.snapshot().value
            second = environment.snapshot().value

            self.assertNotEqual(first.snapshot_id, second.snapshot_id)
            self.assertEqual(first.digest, second.digest)

            (root / "module.py").write_text("VALUE = 2\n", encoding="utf-8")
            changed = environment.snapshot().value
            self.assertNotEqual(second.digest, changed.digest)


if __name__ == "__main__":
    unittest.main()
