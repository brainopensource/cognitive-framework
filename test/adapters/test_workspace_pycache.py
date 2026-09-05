"""Acceptance falsifier for workspace .pyc hygiene (T-74).

Falsifies:
- Executing python tests or commands via SandboxedEnvironmentAdapter leaves NO *.pyc beneath the workspace.
- The pre-run workspace digest matches the post-run workspace digest byte-for-byte.
- PYTHONPYCACHEPREFIX routes bytecode compilation to sandbox tmpfs (/tmp/pycache).
"""

from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from vanguard.packages.adapters.environment.sandboxed import SandboxedEnvironmentAdapter, WorkerRequest
from vanguard.packages.adapters.sandbox.rootless import RootlessSandboxRunner
from vanguard.packages.adapters.sandbox.worker import WorkerProtocol
from vanguard.packages.ports.environment import EffectRequest


class TestWorkspacePycacheHygiene(unittest.TestCase):
    """Guards T-74: bytecode hygiene and workspace digest preservation."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.workspace = self.root / "workspace"
        self.workspace.mkdir()

        # Set up a sample Python project inside the workspace
        src_dir = self.workspace / "src"
        src_dir.mkdir()
        (src_dir / "__init__.py").write_text("", encoding="utf-8")
        (src_dir / "calculator.py").write_text(
            "def add(a: int, b: int) -> int:\n    return a + b\n",
            encoding="utf-8",
        )

        test_dir = self.workspace / "tests"
        test_dir.mkdir()
        (test_dir / "__init__.py").write_text("", encoding="utf-8")
        (test_dir / "test_calculator.py").write_text(
            "import unittest\n"
            "from src.calculator import add\n\n"
            "class TestCalc(unittest.TestCase):\n"
            "    def test_add(self):\n"
            "        self.assertEqual(add(2, 3), 5)\n\n"
            "if __name__ == '__main__':\n"
            "    unittest.main()\n",
            encoding="utf-8",
        )

        self.bundle = self.root / "sealed-bundle"
        self.bundle.write_text("sealed", encoding="utf-8")
        self.runner = RootlessSandboxRunner(self.workspace, evaluator_bundle=self.bundle)
        self.worker = WorkerProtocol(self.runner)
        self.adapter = SandboxedEnvironmentAdapter(self.worker, self.workspace, "env-hygiene-test")

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_proc_exec_python_leaves_no_pyc_and_preserves_workspace_digest(self) -> None:
        """Executing python tests leaves no *.pyc in workspace and reports identical before/after digests."""
        before_snap = self.adapter.snapshot()
        self.assertTrue(before_snap.ok, before_snap.error)
        before_digest = before_snap.value.digest

        # Run unit tests via proc.exec
        req = EffectRequest(
            verb="proc.exec",
            action="exec",
            command=["python3", "-m", "unittest", "discover", "-s", "tests"],
        )
        res = self.adapter.apply(req)
        self.assertTrue(res.ok, res.error)
        self.assertEqual(res.value.exit_code, 0)

        # After execution: verify snapshot digest is identical
        after_snap = self.adapter.snapshot()
        self.assertTrue(after_snap.ok, after_snap.error)
        after_digest = after_snap.value.digest

        self.assertEqual(
            before_digest,
            after_digest,
            f"Pre-run digest ({before_digest}) differs from post-run digest ({after_digest})",
        )

        # Verify no .pyc files or __pycache__ directories were created anywhere in workspace
        pyc_files = list(self.workspace.rglob("*.pyc"))
        self.assertEqual(
            pyc_files,
            [],
            f"Found unexpected *.pyc files in workspace: {pyc_files}",
        )

        pycache_dirs = [p for p in self.workspace.rglob("__pycache__") if p.is_dir()]
        self.assertEqual(
            pycache_dirs,
            [],
            f"Found unexpected __pycache__ directories in workspace: {pycache_dirs}",
        )

    def test_direct_python_module_import_routes_bytecode_to_tmp(self) -> None:
        """Direct module import via python -c routes bytecode away from workspace."""
        before_snap = self.adapter.snapshot()
        self.assertTrue(before_snap.ok)
        before_digest = before_snap.value.digest

        req = EffectRequest(
            verb="proc.exec",
            action="exec",
            command=["python3", "-c", "import src.calculator; print(src.calculator.add(10, 20))"],
        )
        res = self.adapter.apply(req)
        self.assertTrue(res.ok)
        self.assertEqual(res.value.exit_code, 0)

        after_snap = self.adapter.snapshot()
        self.assertTrue(after_snap.ok)
        after_digest = after_snap.value.digest

        self.assertEqual(before_digest, after_digest)
        self.assertEqual(list(self.workspace.rglob("*.pyc")), [])

    def test_pycache_prefix_not_duplicated_when_already_provided(self) -> None:
        """If caller already specified pycache_prefix, do not duplicate the argument."""
        captured_requests: list[WorkerRequest] = []

        class InterceptWorker:
            def execute(self, req: WorkerRequest):
                captured_requests.append(req)
                from vanguard.packages.ports.event_store import Result
                from vanguard.packages.adapters.environment.sandboxed import WorkerReply
                return Result.success(WorkerReply(exit_code=0, stdout="ok", stdout_digest="sha256:00"))

        intercept_adapter = SandboxedEnvironmentAdapter(InterceptWorker(), self.workspace, "test-intercept")
        req = EffectRequest(
            verb="proc.exec",
            action="exec",
            command=["python3", "-X", "pycache_prefix=/custom/cache", "-c", "print(1)"],
        )
        res = intercept_adapter.apply(req)
        self.assertTrue(res.ok)

        argv = captured_requests[0].args["argv"]
        # Verify pycache_prefix appears only once
        count = sum(1 for arg in argv if "pycache_prefix" in str(arg))
        self.assertEqual(count, 1)


if __name__ == "__main__":
    unittest.main()
