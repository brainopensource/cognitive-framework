"""Whole-file writes declared by patch.apply must reach the sandbox worker."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from vanguard.packages.adapters.environment.sandboxed import (
    SandboxedEnvironmentAdapter,
    WorkerReply,
)
from vanguard.packages.ports.environment import EffectRequest
from vanguard.packages.ports.event_store import Result


class _Worker:
    def __init__(self) -> None:
        self.requests = []

    def execute(self, request):
        self.requests.append(request)
        return Result.success(WorkerReply(
            exit_code=0, stdout="ok", stdout_digest="sha256:worker"))


class SandboxedWholeFileWriteTests(unittest.TestCase):
    def test_patch_apply_content_routes_to_fs_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            worker = _Worker()
            environment = SandboxedEnvironmentAdapter(
                worker, Path(tmp), "sandbox-test")
            request = EffectRequest(
                verb="patch.apply",
                action="write",
                args={"path": "new.py", "content": "value = 1\n"},
            )

            result = environment.apply(request)
            self.assertTrue(result.ok)
            self.assertEqual(worker.requests[0].operation, "fs.write")
            self.assertEqual(worker.requests[0].args["path"], "new.py")
            self.assertEqual(worker.requests[0].args["content"], "value = 1\n")


if __name__ == "__main__":
    unittest.main()
