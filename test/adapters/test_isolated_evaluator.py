"""REQ-EVAL-001: adversarial contract for the exterior evaluator."""

from __future__ import annotations

import hashlib
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from vanguard.packages.adapters.evaluators.isolated import IsolatedEvaluator
from vanguard.packages.ports.evaluator import EvaluationProtocol, RunRef


def _digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


class IsolatedEvaluatorContract(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary = tempfile.TemporaryDirectory()
        self.workspace = Path(self._temporary.name)
        self.oracle = self.workspace / "test_oracle.py"
        self.oracle.write_text("assert 1 + 1 == 2\n", encoding="utf-8")
        subprocess.run(
            ["git", "init", "-q"], cwd=self.workspace, check=True
        )
        subprocess.run(
            ["git", "add", "test_oracle.py"], cwd=self.workspace, check=True
        )
        self.protocol = EvaluationProtocol(name="coding-oracle@3")

    def tearDown(self) -> None:
        self._temporary.cleanup()

    def _evaluator(self, **overrides: object) -> IsolatedEvaluator:
        options = {
            "workspace": self.workspace,
            "oracle_digests": {"test_oracle.py": _digest(self.oracle)},
            "command": ("python3", "-c", "raise SystemExit(0)"),
            "expected_uid": os.getuid(),
            "image_digest": "sha256:" + "a" * 64,
        }
        options.update(overrides)
        return IsolatedEvaluator(**options)

    def test_modified_test_oracle_fails_closed_before_runner(self) -> None:
        called = False

        def runner(*args: object, **kwargs: object) -> subprocess.CompletedProcess[bytes]:
            nonlocal called
            called = True
            return subprocess.CompletedProcess([], 0, b"", b"")

        evaluator = self._evaluator(runner=runner)
        self.oracle.write_text("assert False\n", encoding="utf-8")

        result = evaluator.evaluate(RunRef("run-tampered"), self.protocol)

        self.assertTrue(result.ok)
        self.assertEqual(result.value.outcome, "claims")
        self.assertEqual(result.value.claims[0]["event"], "EvaluationTampered")
        self.assertEqual(result.value.claims[0]["status"], "failed")
        self.assertFalse(result.value.claims[0]["probes"]["immutability"])
        self.assertTrue(result.value.claims[0]["probes"]["nonPollution"])
        self.assertFalse(called)

    def test_untracked_monkey_patch_fails_closed(self) -> None:
        (self.workspace / "conftest.py").write_text(
            "# candidate-planted pytest hook\n", encoding="utf-8"
        )

        result = self._evaluator().evaluate(RunRef("run-polluted"), self.protocol)

        self.assertTrue(result.ok)
        self.assertEqual(result.value.claims[0]["event"], "EvaluationTampered")
        self.assertFalse(result.value.claims[0]["probes"]["nonPollution"])

    def test_dropped_socket_is_inconclusive_not_passed(self) -> None:
        def dropped(*args: object, **kwargs: object) -> subprocess.CompletedProcess[bytes]:
            raise ConnectionResetError("evaluator socket dropped")

        result = self._evaluator(runner=dropped).evaluate(
            RunRef("run-dropped"), self.protocol
        )

        self.assertTrue(result.ok)
        self.assertEqual(result.value.outcome, "inconclusive")
        self.assertEqual(result.value.reason, "instrument_error")
        self.assertEqual(result.value.claims, ())

    def test_genuine_fix_returns_passed_with_both_probes(self) -> None:
        result = self._evaluator().evaluate(RunRef("run-fixed"), self.protocol)

        self.assertTrue(result.ok)
        self.assertEqual(result.value.outcome, "claims")
        claim = result.value.claims[0]
        self.assertEqual(claim["event"], "EvaluationCompleted")
        self.assertEqual(claim["status"], "passed")
        self.assertEqual(
            claim["probes"], {"immutability": True, "nonPollution": True}
        )
        self.assertEqual(claim["evaluatorUid"], os.getuid())
        self.assertEqual(claim["imageDigest"], "sha256:" + "a" * 64)


if __name__ == "__main__":
    unittest.main()
