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

        result = evaluator.evaluate(RunRef("run-tampered", episode_id="ep1"), self.protocol)

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

        result = self._evaluator().evaluate(RunRef("run-polluted", episode_id="ep1"), self.protocol)

        self.assertTrue(result.ok)
        self.assertEqual(result.value.claims[0]["event"], "EvaluationTampered")
        self.assertFalse(result.value.claims[0]["probes"]["nonPollution"])

    def test_dropped_socket_is_inconclusive_not_passed(self) -> None:
        def dropped(*args: object, **kwargs: object) -> subprocess.CompletedProcess[bytes]:
            raise ConnectionResetError("evaluator socket dropped")

        result = self._evaluator(runner=dropped).evaluate(
            RunRef("run-dropped", episode_id="ep1"), self.protocol
        )

        self.assertTrue(result.ok)
        self.assertEqual(result.value.outcome, "inconclusive")
        self.assertEqual(result.value.reason, "instrument_error")
        self.assertEqual(result.value.claims, ())

    def test_genuine_fix_returns_passed_with_both_probes(self) -> None:
        result = self._evaluator().evaluate(RunRef("run-fixed", episode_id="ep1"), self.protocol)

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

    def test_untracked_files_under_oracle_paths_fails(self) -> None:
        (self.workspace / "untracked_oracle.py").write_text("assert True\n")
        result = self._evaluator().evaluate(RunRef("run", episode_id="ep1"), self.protocol)
        self.assertEqual(result.value.outcome, "claims")
        self.assertFalse(result.value.claims[0]["probes"]["immutability"])

    def test_oracle_directory_replaced_by_symlink(self) -> None:
        digest = _digest(self.oracle)
        self.oracle.unlink()
        (self.workspace / "test_oracle.py").symlink_to(Path("/tmp"))
        evaluator = IsolatedEvaluator(
            workspace=self.workspace,
            oracle_digests={"test_oracle.py": digest},
            command=("python3", "-c", "raise SystemExit(0)"),
            expected_uid=os.getuid(),
            image_digest="sha256:" + "a" * 64
        )
        result = evaluator.evaluate(RunRef("run", episode_id="ep1"), self.protocol)
        self.assertFalse(result.value.claims[0]["probes"]["immutability"])

    def test_executable_unexpected_location(self) -> None:
        p = self.workspace / "malicious.sh"
        p.write_text("echo 'hello'\n")
        p.chmod(0o755)
        result = self._evaluator().evaluate(RunRef("run", episode_id="ep1"), self.protocol)
        self.assertFalse(result.value.claims[0]["probes"]["nonPollution"])

    def test_path_shadowing(self) -> None:
        p = self.workspace / "python"
        p.write_text("")
        result = self._evaluator().evaluate(RunRef("run", episode_id="ep1"), self.protocol)
        self.assertFalse(result.value.claims[0]["probes"]["nonPollution"])

    def test_modified_lockfile(self) -> None:
        p = self.workspace / "requirements.txt"
        p.write_text("requests==2.0")
        result = self._evaluator().evaluate(RunRef("run", episode_id="ep1"), self.protocol)
        self.assertFalse(result.value.claims[0]["probes"]["nonPollution"])

    def test_git_hooks_modification(self) -> None:
        p = self.workspace / ".git" / "hooks" / "pre-commit"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("exit 0")
        result = self._evaluator().evaluate(RunRef("run", episode_id="ep1"), self.protocol)
        self.assertFalse(result.value.claims[0]["probes"]["nonPollution"])

    def test_symlink_outside_workspace(self) -> None:
        p = self.workspace / "link"
        p.symlink_to("/etc/passwd")
        result = self._evaluator().evaluate(RunRef("run", episode_id="ep1"), self.protocol)
        self.assertFalse(result.value.claims[0]["probes"]["nonPollution"])

    def test_unsafe_env_vars(self) -> None:
        os.environ["PYTHONPATH"] = "/tmp"
        try:
            result = self._evaluator().evaluate(RunRef("run", episode_id="ep1"), self.protocol)
            self.assertFalse(result.value.claims[0]["probes"]["nonPollution"])
        finally:
            del os.environ["PYTHONPATH"]

    @unittest.skipIf(not hasattr(os, "getuid") or os.getuid() == 10002,
                     "this host already is the evaluator uid")
    def test_default_uid_gate_is_inconclusive_off_the_daemon(self) -> None:
        evaluator = IsolatedEvaluator(
            workspace=self.workspace,
            oracle_digests={"test_oracle.py": _digest(self.oracle)},
            command=("python3", "-c", "raise SystemExit(0)"),
            image_digest="sha256:" + "a" * 64,
        )
        result = evaluator.evaluate(RunRef("run-uid", episode_id="ep1"), self.protocol)
        self.assertTrue(result.ok)
        self.assertEqual(result.value.outcome, "inconclusive")
        self.assertEqual(result.value.reason, "evaluator_identity_unverified")


if __name__ == "__main__":
    unittest.main()
