from __future__ import annotations

import tempfile
import unittest
import os
import signal
from pathlib import Path

from vanguard.packages.adapters.sandbox.rootless import RootlessSandboxRunner



class TestRunner(RootlessSandboxRunner):
    def _runtime_prefix(self):
        prefix = super()._runtime_prefix()
        # strip rlimit flags for local bwrap execution
        filtered = []
        i = 0
        while i < len(prefix):
            if prefix[i].startswith("--rlimit-"):
                i += 2
            else:
                filtered.append(prefix[i])
                i += 1
        return filtered

class SandboxIsolationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.workspace = root / "workspace"
        self.evaluator = root / "evaluator" / "bundle"
        self.workspace.mkdir()
        self.evaluator.parent.mkdir()
        self.evaluator.write_text("sealed evaluator instructions", encoding="utf-8")
        
        # Write .env
        (self.workspace / ".env").write_text("SECRET=123", encoding="utf-8")
        
        self.runner = TestRunner(
            self.workspace,
            evaluator_bundle=self.evaluator,
            timeout_seconds=2.0
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_env_file_not_accessible(self) -> None:
        # Since _validate_workspace prevents execution if .env exists, we test that it fails
        res = self.runner.execute(["cat", ".env"])
        self.assertFalse(res.ok)
        self.assertEqual(res.error.kind, "invalid_workspace")
        
    def test_home_directory_not_accessible(self) -> None:
        # Remove .env so it can run
        (self.workspace / ".env").unlink()
        res = self.runner.execute(["ls", "/home"])
        # Should fail or return empty/not-found depending on bwrap setup, but host home is not mounted
        self.assertTrue(res.ok)
        self.assertNotEqual(res.value.receipt.exit_code, 0)
        
    def test_evaluator_bundle_not_readable(self) -> None:
        (self.workspace / ".env").unlink()
        res = self.runner.execute(["cat", "/sealed-evaluator/bundle"])
        self.assertTrue(res.ok)
        self.assertNotEqual(res.value.receipt.exit_code, 0)

    def test_host_sockets_not_exposed(self) -> None:
        (self.workspace / ".env").unlink()
        res = self.runner.execute(["ls", "/var/run/docker.sock"])
        self.assertTrue(res.ok)
        self.assertNotEqual(res.value.receipt.exit_code, 0)

    def test_network_is_denied(self) -> None:
        (self.workspace / ".env").unlink()
        res = self.runner.execute(["ping", "-c", "1", "1.1.1.1"])
        self.assertTrue(res.ok)
        self.assertNotEqual(res.value.receipt.exit_code, 0)

    def test_process_group_cancellation_on_timeout(self) -> None:
        (self.workspace / ".env").unlink()
        runner = TestRunner(
            self.workspace,
            evaluator_bundle=self.evaluator,
            timeout_seconds=0.5
        )
        res = runner.execute(["sleep", "10"])
        self.assertTrue(res.ok)
        self.assertEqual(res.value.receipt.exit_code, 124) # timeout exit code in _run_isolated
        self.assertIn(b"worker process group timed out", res.value.receipt.stderr)

if __name__ == "__main__":
    unittest.main()
