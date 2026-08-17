from __future__ import annotations

import unittest
from typing import Sequence

from vanguard.packages.adapters.sandbox.worker import (
    WorkerProtocol, WorkerOperation, WorkerResult, decode_worker_request, encode_worker_request,
)
from vanguard.packages.adapters.sandbox.rootless import WorkerSandboxReceipt
from vanguard.packages.ports.sandbox import SandboxResult, ContainmentReport, SandboxRunner
from vanguard.packages.ports.event_store import Result


class FakeSandboxRunner(SandboxRunner):
    def __init__(self, exit_code: int = 0, stdout: bytes = b"", stderr: bytes = b""):
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr
        self.commands: list[Sequence[str]] = []

    def execute(self, argv: Sequence[str]) -> Result[SandboxResult]:
        self.commands.append(argv)
        report = ContainmentReport(
            runtime="fake", runtime_version="0", namespace="none",
            syscall_profile="none", network_enforcement="none",
            writable_mounts=("/workspace",), exposed_sockets=(),
            resource_limits={}, startup_probes=(),
            attested_at="2026-08-15T00:00:00Z", contained=True,
            verified=True, visibility_mark="test-verified"
        )
        receipt = WorkerSandboxReceipt(
            exit_code=self.exit_code,
            stdout_digest="sha256:fake",
            stdout=self.stdout,
            stderr=self.stderr,
            truncated=False,
            duration_millis=10,
        )
        return Result.success(SandboxResult(receipt=receipt, containment=report))


class TestSandboxWorker(unittest.TestCase):
    def test_execute_fs_read(self) -> None:
        runner = FakeSandboxRunner(stdout=b"file content")
        worker = WorkerProtocol(runner)
        op = WorkerOperation(
            operation="fs.read",
            args={"path": "dir/file.txt"},
            working_directory=".",
            timeout_seconds=30.0,
            max_output_bytes=100,
        )
        res = worker.execute(op)
        self.assertTrue(res.ok)
        self.assertEqual(res.value.stdout, "file content")
        self.assertEqual(runner.commands[0], ("cat", "--", "dir/file.txt"))

    def test_path_traversal_rejection(self) -> None:
        worker = WorkerProtocol(FakeSandboxRunner())
        op = WorkerOperation(
            operation="fs.read",
            args={"path": "../../../etc/passwd"},
            working_directory=".",
            timeout_seconds=30.0,
            max_output_bytes=100,
        )
        res = worker.execute(op)
        self.assertFalse(res.ok)
        self.assertEqual(res.error.kind, "invalid_path")

    def test_execute_fs_search(self) -> None:
        runner = FakeSandboxRunner(stdout=b"match")
        worker = WorkerProtocol(runner)
        op = WorkerOperation(
            operation="fs.search",
            args={"pattern": "TODO", "path": "src/"},
            working_directory=".",
            timeout_seconds=30.0,
            max_output_bytes=100,
        )
        res = worker.execute(op)
        self.assertTrue(res.ok)
        self.assertEqual(runner.commands[0], ("grep", "-rn", "--", "TODO", "src/"))

    def test_execute_patch_apply(self) -> None:
        runner = FakeSandboxRunner()
        worker = WorkerProtocol(runner)
        op = WorkerOperation(
            operation="patch.apply",
            args={"patch": "--- a/file\n+++ b/file\n"},
            working_directory=".",
            timeout_seconds=30.0,
            max_output_bytes=100,
        )
        res = worker.execute(op)
        self.assertTrue(res.ok)
        cmd = runner.commands[0]
        self.assertEqual(cmd[0], "/bin/sh")
        self.assertEqual(cmd[1], "-c")
        self.assertEqual(cmd[2], 'printf "%s" "$1" | patch -p1')
        self.assertEqual(cmd[4], "--- a/file\n+++ b/file\n")

    def test_execute_proc_exec(self) -> None:
        runner = FakeSandboxRunner()
        worker = WorkerProtocol(runner)
        op = WorkerOperation(
            operation="proc.exec",
            args={"argv": ["pytest", "tests/"]},
            working_directory=".",
            timeout_seconds=30.0,
            max_output_bytes=100,
        )
        res = worker.execute(op)
        self.assertTrue(res.ok)
        self.assertEqual(runner.commands[0], ("pytest", "tests/"))

    def test_proc_exec_rejects_shell_string(self) -> None:
        worker = WorkerProtocol(FakeSandboxRunner())
        op = WorkerOperation(
            operation="proc.exec",
            args={"argv": "pytest tests/"},
            working_directory=".",
            timeout_seconds=30.0,
            max_output_bytes=100,
        )
        res = worker.execute(op)
        self.assertFalse(res.ok)
        self.assertEqual(res.error.kind, "invalid_request")

    def test_proc_exec_enforces_manifest_executable_allowlist(self) -> None:
        worker = WorkerProtocol(FakeSandboxRunner())
        res = worker.execute(WorkerOperation("proc.exec", {"argv": ["rm", "-rf", "."]}))
        self.assertFalse(res.ok)
        self.assertEqual(res.error.kind, "denied")

    def test_output_bounding(self) -> None:
        runner = FakeSandboxRunner(stdout=b"A" * 200, stderr=b"B" * 200)
        worker = WorkerProtocol(runner)
        op = WorkerOperation(
            operation="fs.read",
            args={"path": "file.txt"},
            working_directory=".",
            timeout_seconds=30.0,
            max_output_bytes=100,
        )
        res = worker.execute(op)
        self.assertTrue(res.ok)
        self.assertEqual(len(res.value.stdout), 100)
        self.assertEqual(len(res.value.stderr), 100)
        self.assertTrue(res.value.truncated)

    def test_typed_wire_round_trip_and_digest_binding(self) -> None:
        operation = WorkerOperation("fs.read", {"path": "x.py"}, request_id="req-1")
        decoded = decode_worker_request(encode_worker_request(operation))
        self.assertTrue(decoded.ok)
        self.assertEqual(decoded.value.operation, "fs.read")
        self.assertEqual(decoded.value.request_id, "req-1")

        tampered = encode_worker_request(operation).replace(b"fs.read", b"fs.write")
        self.assertFalse(decode_worker_request(tampered).ok)

    def test_wire_rejects_invalid_utf8_and_unknown_fields(self) -> None:
        self.assertFalse(decode_worker_request(b"\xff\n").ok)
        operation = WorkerOperation("fs.read", {"path": "x.py"}, request_id="req-2")
        frame = encode_worker_request(operation).rstrip(b"\n")[:-1] + b',"unknown":true}'
        self.assertFalse(decode_worker_request(frame).ok)

if __name__ == "__main__":
    unittest.main()
