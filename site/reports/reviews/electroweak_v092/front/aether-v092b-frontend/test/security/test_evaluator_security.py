"""S6B-MD-007 / S6B-MD-008: Exterior evaluator security boundary tests."""

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from vanguard.packages.adapters.evaluators.isolated import IsolatedEvaluator
from vanguard.packages.ports.evaluator import EvaluationProtocol, RunRef


class EvaluatorSecurityBoundary(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.workspace = Path(self.tmp.name)
        subprocess.run(["git", "init", "-q"], cwd=self.workspace, check=True)
        
        self.oracle = self.workspace / "oracle.py"
        self.oracle.write_text("assert True\n")
        subprocess.run(["git", "add", "oracle.py"], cwd=self.workspace, check=True)
        
        import hashlib
        digest = "sha256:" + hashlib.sha256(self.oracle.read_bytes()).hexdigest()
        self.protocol = EvaluationProtocol("test")
        
        self.evaluator = IsolatedEvaluator(
            workspace=self.workspace,
            oracle_digests={"oracle.py": digest},
            command=("python3", "-c", "print('ok')"),
            expected_uid=os.getuid(),
            image_digest="sha256:" + "a" * 64,
            timeout_seconds=5.0
        )

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_runtime_cannot_import_evaluator_implementation(self) -> None:
        """Boundary test: runtime must not import evaluator implementation."""
        # Simple static analysis via grep
        import subprocess
        result = subprocess.run(
            ["grep", "-r", "vanguard.packages.adapters.evaluators.isolated", "vanguard/packages/runtime"],
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 1, "Runtime must not import isolated evaluator implementation")

    def test_wrong_peer_identity_inconclusive(self) -> None:
        self.evaluator._expected_uid = 9999
        result = self.evaluator.evaluate(RunRef("run", episode_id="ep1"), self.protocol)
        self.assertEqual(result.value.outcome, "inconclusive")
        self.assertEqual(result.value.reason, "evaluator_identity_unverified")

    def test_wrong_image_digest_inconclusive(self) -> None:
        self.evaluator._image_digest = "sha256:invalid"
        result = self.evaluator.evaluate(RunRef("run", episode_id="ep1"), self.protocol)
        self.assertEqual(result.value.outcome, "inconclusive")
        self.assertEqual(result.value.reason, "evaluator_image_unverified")

    def test_oracle_modification_fails_closed(self) -> None:
        self.oracle.write_text("assert False\n")
        result = self.evaluator.evaluate(RunRef("run", episode_id="ep1"), self.protocol)
        self.assertEqual(result.value.outcome, "claims")
        self.assertEqual(result.value.claims[0]["status"], "failed")
        self.assertFalse(result.value.claims[0]["probes"]["immutability"])

    def test_import_pollution_fails_closed(self) -> None:
        (self.workspace / "sitecustomize.py").write_text("print('polluted')\n")
        result = self.evaluator.evaluate(RunRef("run", episode_id="ep1"), self.protocol)
        self.assertEqual(result.value.outcome, "claims")
        self.assertEqual(result.value.claims[0]["status"], "failed")
        self.assertFalse(result.value.claims[0]["probes"]["nonPollution"])

    def test_hooks_modification_fails_closed(self) -> None:
        hooks = self.workspace / ".git" / "hooks"
        hooks.mkdir(parents=True, exist_ok=True)
        (hooks / "pre-commit").write_text("exit 0")
        result = self.evaluator.evaluate(RunRef("run", episode_id="ep1"), self.protocol)
        self.assertEqual(result.value.outcome, "claims")
        self.assertEqual(result.value.claims[0]["status"], "failed")
        self.assertFalse(result.value.claims[0]["probes"]["nonPollution"])

if __name__ == "__main__":
    unittest.main()
