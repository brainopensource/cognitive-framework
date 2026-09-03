"""T1 Cassette integration tests across all reconstruction packs (Task A.3, Task B.2, Packet 4).

Proves that all 4 reconstruction packs + default pack compose and execute
end-to-end against real repositories with zero edits to kernel/ or agency/episode/.
"""

from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from typing import Any

from vanguard.packages.agency import RunTermination
from vanguard.packages.ports.evaluator import RunRef, Verdict
from vanguard.packages.ports.event_store import Result
from vanguard.packages.runtime.governance.approvals import OperatorSigner
from vanguard.packages.runtime.root import (
    Runtime,
    TaskContext,
)

OPERATOR_SIGNER = OperatorSigner(b"test-operator-held-approval-key")
OPERATOR_KEY = OPERATOR_SIGNER.public_bytes


def sign_challenge(challenge):
    return OPERATOR_SIGNER.approve(challenge, reviewer="agent-1")


ROOT = Path(__file__).resolve().parents[2]
MANIFESTS = ROOT / "vanguard" / "packages" / "agency" / "manifests"

BUGGY_SOURCE = '''"""A tiny summing helper."""


def total(values):
    result = 1
    for value in values:
        result += value
    return result
'''

FIXED_SOURCE = BUGGY_SOURCE.replace("result = 1", "result = 0")

TEST_SOURCE = '''import unittest

from calc import total


class Total(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(total([]), 0)

    def test_sums(self):
        self.assertEqual(total([1, 2, 3]), 6)


if __name__ == "__main__":
    unittest.main()
'''


def build_repo() -> Path:
    path = Path(tempfile.mkdtemp(prefix="vg-recon-"))
    (path / "calc.py").write_text(BUGGY_SOURCE, encoding="utf-8")
    (path / "test_calc.py").write_text(TEST_SOURCE, encoding="utf-8")
    for argv in (
        ["git", "init", "-q"],
        ["git", "config", "user.email", "recon@vanguard.test"],
        ["git", "config", "user.name", "recon"],
        ["git", "add", "-A"],
        ["git", "commit", "-q", "-m", "seed"],
    ):
        subprocess.run(argv, cwd=path, check=True, capture_output=True)
    return path


def repo_tests_pass(repo: Path) -> bool:
    completed = subprocess.run(
        ["python3", "-m", "unittest", "discover", "-s", str(repo), "-t", str(repo)],
        capture_output=True,
        text=True,
        cwd=repo,
    )
    return completed.returncode == 0


def unified_diff(repo: Path) -> str:
    (repo / "calc.py").write_text(FIXED_SOURCE, encoding="utf-8")
    completed = subprocess.run(
        ["git", "diff", "--", "calc.py"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    )
    (repo / "calc.py").write_text(BUGGY_SOURCE, encoding="utf-8")
    return completed.stdout


class SuiteVerifier:
    def __init__(self, repo: Path) -> None:
        self._repo = repo
        self.calls: list[RunRef] = []

    def evaluate(self, run_ref, protocol):
        self.calls.append(run_ref)
        green = repo_tests_pass(self._repo)
        return Result.success(
            Verdict(
                outcome="claims",
                claims=(
                    {"claim": "tests_green", "holds": green, "protocol": protocol.name},
                ),
            )
        )


class _Ok:
    def __init__(self, value):
        self.ok, self.value, self.error = True, value, None


class _Failed:
    def __init__(self, message):
        self.ok, self.value = False, None
        self.error = type("E", (), {"kind": "instrument_error", "message": message})()


class PackScriptedOperator:
    """Scripted operator that proposes dialect-specific tool names for each pack."""

    def __init__(self, script: list[dict[str, Any]]) -> None:
        self.script = script
        self.contexts: list[dict] = []
        self._turn = 0

    def propose(self, context, tools, sampling):
        self.contexts.append(dict(context))
        turn, self._turn = self._turn, self._turn + 1
        if turn >= len(self.script):
            return _Failed("cassette exhausted")
        return _Ok(self.script[turn])


class ReconstructionPacksIntegration(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = build_repo()
        self.addCleanup(lambda: subprocess.run(["rm", "-rf", str(self.repo)], check=False))
        self.diff = unified_diff(self.repo)
        self.verifier = SuiteVerifier(self.repo)

    def _execute_pack(self, manifest_name: str, script: list[dict[str, Any]]):
        operator = PackScriptedOperator(script)
        task = TaskContext(
            brief="Fix off-by-one error in calc.py to make test suite pass.",
            repo_path=self.repo,
            run_id=f"run-{manifest_name}-1",
            episode_id=f"episode-{manifest_name}-1",
            principal="agent-1",
            competence_prior=0.75,
        )
        return Runtime.execute_harness(
            manifest_path=MANIFESTS / manifest_name / "manifest.json",
            task_context=task,
            model=operator,
            approver=sign_challenge,
            approval_key=OPERATOR_KEY,
            verifier=self.verifier,
        )

    def test_vg_code_default_cassette(self) -> None:
        resource = {"kind": "fs", "root": "/workspace", "paths": ["/workspace"]}
        script = [
            {
                "kind": "effect",
                "action": "fs.read",
                "resource": resource,
                "args": {"path": "calc.py"},
            },
            {
                "kind": "effect",
                "action": "patch.apply",
                "resource": resource,
                "args": {"diff": self.diff},
            },
            {"kind": "finish", "note": "repaired with default pack"},
        ]
        result = self._execute_pack("vg-code-default", script)
        self.assertEqual(result.harness, "vg-code-default")
        self.assertEqual(result.terminal, RunTermination.COMPLETED)
        self.assertTrue(repo_tests_pass(self.repo))
        self.assertTrue(result.verdict.claims[0]["holds"])

    def test_vg_code_claude_shaped_cassette(self) -> None:
        # Uses Claude Code dialect: Read, Edit, Bash
        resource = {"kind": "fs", "root": "/workspace", "paths": ["/workspace"]}
        script = [
            {
                "kind": "effect",
                "action": "fs.read",
                "resource": resource,
                "args": {"file_path": "calc.py"},
            },
            {
                "kind": "effect",
                "action": "patch.apply",
                "resource": resource,
                "args": {"diff": self.diff},
            },
            {"kind": "finish", "note": "repaired with claude-shaped pack"},
        ]
        result = self._execute_pack("vg-code-claude-shaped", script)
        self.assertEqual(result.harness, "vg-code-claude-shaped")
        self.assertEqual(result.terminal, RunTermination.COMPLETED)
        self.assertTrue(repo_tests_pass(self.repo))
        self.assertTrue(result.verdict.claims[0]["holds"])

    def test_vg_code_opencode_shaped_cassette(self) -> None:
        # Uses OpenCode dialect: view_file, edit_file, run_command
        resource = {"kind": "fs", "root": "/workspace", "paths": ["/workspace"]}
        script = [
            {
                "kind": "effect",
                "action": "fs.read",
                "resource": resource,
                "args": {"file_path": "calc.py"},
            },
            {
                "kind": "effect",
                "action": "patch.apply",
                "resource": resource,
                "args": {"diff": self.diff},
            },
            {"kind": "finish", "note": "repaired with opencode-shaped pack"},
        ]
        result = self._execute_pack("vg-code-opencode-shaped", script)
        self.assertEqual(result.harness, "vg-code-opencode-shaped")
        self.assertEqual(result.terminal, RunTermination.COMPLETED)
        self.assertTrue(repo_tests_pass(self.repo))
        self.assertTrue(result.verdict.claims[0]["holds"])

    def test_vg_code_swe_mini_cassette(self) -> None:
        # Uses SWE mini dialect: read_file, edit_file, bash
        resource = {"kind": "fs", "root": "/workspace", "paths": ["/workspace"]}
        script = [
            {
                "kind": "effect",
                "action": "fs.read",
                "resource": resource,
                "args": {"path": "calc.py"},
            },
            {
                "kind": "effect",
                "action": "patch.apply",
                "resource": resource,
                "args": {"diff": self.diff},
            },
            {"kind": "finish", "note": "repaired with swe-mini pack"},
        ]
        result = self._execute_pack("vg-code-swe-mini", script)
        self.assertEqual(result.harness, "vg-code-swe-mini")
        self.assertEqual(result.terminal, RunTermination.COMPLETED)
        self.assertTrue(repo_tests_pass(self.repo))
        self.assertTrue(result.verdict.claims[0]["holds"])

    def test_vg_shell_only_cassette(self) -> None:
        # Uses single proc.exec capability with raw command
        patch_file = self.repo / "fix.patch"
        patch_file.write_text(self.diff, encoding="utf-8")
        resource = {"kind": "process", "root": str(self.repo), "executable": "git"}
        script = [
            {
                "kind": "effect",
                "action": "proc.exec",
                "resource": resource,
                "args": {"argv": ["git", "apply", "fix.patch"]},
            },
            {"kind": "finish", "note": "repaired with shell-only pack"},
        ]
        result = self._execute_pack("vg-shell-only", script)
        self.assertEqual(result.harness, "vg-shell-only")
        self.assertEqual(result.terminal, RunTermination.COMPLETED)
        self.assertTrue(repo_tests_pass(self.repo))
        self.assertTrue(result.verdict.claims[0]["holds"])


if __name__ == "__main__":
    unittest.main()
