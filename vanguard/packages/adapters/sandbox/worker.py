"""Worker protocol mediating environment operations through sandbox containment.

Owning contract: S6B-MD-005, VG-05 §6.2, REQ-PORT-005.
Every product effect and observation crosses this protocol. Direct host
Git/subprocess execution is unreachable.
"""

from __future__ import annotations

import pathlib
from dataclasses import dataclass
from typing import Any, Mapping

from ...ports.event_store import Result
from ...ports.sandbox import SandboxRunner
from .rootless import WorkerSandboxReceipt

__all__ = ["WorkerOperation", "WorkerResult", "WorkerProtocol"]


@dataclass(frozen=True, slots=True)
class WorkerOperation:
    operation: str
    args: Mapping[str, Any]
    working_directory: str
    timeout_seconds: float
    max_output_bytes: int


@dataclass(frozen=True, slots=True)
class WorkerResult:
    exit_code: int
    stdout: str
    stderr: str
    stdout_digest: str
    truncated: bool
    duration_millis: int


class WorkerProtocol:
    def __init__(self, runner: SandboxRunner) -> None:
        self.runner = runner

    def execute(self, operation: WorkerOperation) -> Result[WorkerResult]:
        if operation.operation not in ("fs.read", "fs.search", "patch.apply", "proc.test"):
            return Result.fail("invalid_operation", f"Unknown operation: {operation.operation}")

        try:
            wd = pathlib.Path(operation.working_directory)
        except TypeError:
            return Result.fail("invalid_request", "working_directory must be a string")

        if wd.is_absolute():
            return Result.fail("invalid_path", "working_directory must be relative")
        if ".." in wd.parts:
            return Result.fail("invalid_path", "working_directory must not contain traversal")

        argv: list[str] = []
        if operation.operation == "fs.read":
            path_str = operation.args.get("path")
            if not isinstance(path_str, str):
                return Result.fail("invalid_request", "Missing path for fs.read")
            path = pathlib.Path(path_str)
            if path.is_absolute() or ".." in path.parts:
                return Result.fail("invalid_path", "Path must be relative and not traverse")
            argv = ["cat", path_str]
            
        elif operation.operation == "fs.search":
            pattern = operation.args.get("pattern")
            path_str = operation.args.get("path")
            if not isinstance(pattern, str) or not isinstance(path_str, str):
                return Result.fail("invalid_request", "Missing pattern or path for fs.search")
            path = pathlib.Path(path_str)
            if path.is_absolute() or ".." in path.parts:
                return Result.fail("invalid_path", "Path must be relative and not traverse")
            argv = ["grep", "-rn", pattern, path_str]
            
        elif operation.operation == "patch.apply":
            content = operation.args.get("patch")
            if not isinstance(content, str):
                return Result.fail("invalid_request", "Missing patch content")
            # Write patch via sh so it can be passed to patch -p1
            argv = ["/bin/sh", "-c", 'printf "%s" "$1" | patch -p1', "--", content]
            
        elif operation.operation == "proc.test":
            cmd_argv = operation.args.get("argv")
            if not isinstance(cmd_argv, list) or not all(isinstance(a, str) for a in cmd_argv):
                return Result.fail("invalid_request", "proc.test argv must be list of strings")
            argv = cmd_argv

        # Wrap with chdir if needed
        final_argv = argv
        if str(wd) != ".":
            final_argv = ["/bin/sh", "-c", 'cd "$1" && shift && exec "$@"', "--", str(wd)] + argv

        # Pass timeout to runner if it supports it, else we rely on runner's default
        # Runner configuration is external to WorkerProtocol per instruction, but we bound output if we can
        
        # In case runner expects max_output_bytes we could pass it, but Runner interface doesn't have it.
        # We rely on RootlessSandboxRunner having it, or we do our own truncation if the receipt has unbounded stdout.
        
        result = self.runner.execute(tuple(final_argv))
        if not result.ok:
            return Result.fail(result.error.kind, result.error.message)

        receipt = result.value.receipt
        
        # Extract stdout/stderr if available (WorkerSandboxReceipt from rootless runner)
        if hasattr(receipt, "stdout") and isinstance(receipt.stdout, bytes):
            stdout_bytes = receipt.stdout
            stderr_bytes = getattr(receipt, "stderr", b"")
            truncated = getattr(receipt, "truncated", False)
            duration_millis = getattr(receipt, "duration_millis", 0)
        else:
            # Fallback for FakeSandboxRunner which doesn't have them
            stdout_bytes = b""
            stderr_bytes = b""
            truncated = False
            duration_millis = 0

        # Apply output bounding just in case runner didn't do it
        if len(stdout_bytes) > operation.max_output_bytes:
            stdout_bytes = stdout_bytes[:operation.max_output_bytes]
            truncated = True
        if len(stderr_bytes) > operation.max_output_bytes:
            stderr_bytes = stderr_bytes[:operation.max_output_bytes]
            truncated = True

        return Result.success(
            WorkerResult(
                exit_code=receipt.exit_code,
                stdout=stdout_bytes.decode(errors="replace"),
                stderr=stderr_bytes.decode(errors="replace"),
                stdout_digest=receipt.stdout_digest,
                truncated=truncated,
                duration_millis=duration_millis,
            )
        )
