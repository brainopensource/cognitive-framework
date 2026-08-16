"""Worker protocol mediating environment operations through sandbox containment.

Owning contract: S6B-MD-005, VG-05 §6.2, REQ-PORT-005.
Every product effect and observation crosses this protocol. Direct host
Git/subprocess execution is unreachable.
"""

from __future__ import annotations

import pathlib
import hashlib
import json
import uuid
from dataclasses import dataclass
from typing import Any, Mapping

from ...ports.event_store import Result
from ...ports.sandbox import SandboxRunner
from .rootless import WorkerSandboxReceipt

__all__ = [
    "WorkerOperation",
    "WorkerProtocol",
    "WorkerResult",
    "decode_worker_request",
    "encode_worker_request",
]

_SAFE_WRITE = (
    "import os,sys;"
    "root=os.path.realpath('/workspace');"
    "rel=sys.argv[1];"
    "parts=[p for p in rel.split('/') if p not in ('','.')] ;"
    "cur='/workspace';"
    "bad=any(os.path.islink(cur := os.path.join(cur,p)) for p in parts);"
    "target=os.path.realpath(os.path.join('/workspace',rel));"
    "ok=target == root or target.startswith(root + os.sep);"
    "(not bad and ok) or (_ for _ in ()).throw(RuntimeError('unsafe workspace path'));"
    "fd=os.open(target,os.O_WRONLY|os.O_CREAT|os.O_TRUNC|os.O_NOFOLLOW,0o644);"
    "os.write(fd,sys.argv[2].encode('utf-8'));os.close(fd)"
)


@dataclass(frozen=True, slots=True)
class WorkerOperation:
    operation: str
    args: Mapping[str, Any]
    working_directory: str = "."
    timeout_seconds: float = 30.0
    max_output_bytes: int = 1048576
    request_id: str = ""


@dataclass(frozen=True, slots=True)
class WorkerResult:
    exit_code: int
    stdout: str
    stderr: str
    stdout_digest: str
    truncated: bool
    duration_millis: int


def encode_worker_request(operation: WorkerOperation) -> bytes:
    request_id = operation.request_id or str(uuid.uuid4())
    payload = {
        "version": "vg.4",
        "requestId": request_id,
        "verb": operation.operation,
        "args": dict(operation.args),
        "workingDirectory": operation.working_directory,
        "timeoutMillis": max(1, int(operation.timeout_seconds * 1000)),
        "maxOutputBytes": operation.max_output_bytes,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    envelope = {**payload, "requestDigest": "sha256:" + hashlib.sha256(canonical).hexdigest()}
    return json.dumps(envelope, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8") + b"\n"


def decode_worker_request(frame: bytes, *, max_bytes: int = 65_536) -> Result[WorkerOperation]:
    if not isinstance(frame, bytes) or len(frame) > max_bytes:
        return Result.fail("invalid_request", "worker frame exceeds size limit")
    try:
        data = json.loads(frame.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError):
        return Result.fail("invalid_request", "worker frame is not strict UTF-8 JSON")
    if not isinstance(data, Mapping):
        return Result.fail("invalid_request", "worker frame must be an object")
    required = {"version", "requestId", "verb", "args", "requestDigest"}
    if not required.issubset(data) or data.get("version") != "vg.4":
        return Result.fail("invalid_request", "worker frame version or fields are invalid")
    if set(data) - required - {"workingDirectory", "timeoutMillis", "maxOutputBytes"}:
        return Result.fail("invalid_request", "worker frame contains unknown fields")
    unsigned = {key: value for key, value in data.items() if key != "requestDigest"}
    canonical = json.dumps(unsigned, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    expected = "sha256:" + hashlib.sha256(canonical).hexdigest()
    if data.get("requestDigest") != expected:
        return Result.fail("invalid_request", "worker request digest mismatch")
    if not isinstance(data.get("requestId"), str) or not data["requestId"]:
        return Result.fail("invalid_request", "worker request id is required")
    if not isinstance(data.get("verb"), str) or not isinstance(data.get("args"), Mapping):
        return Result.fail("invalid_request", "worker verb or args is invalid")
    timeout = data.get("timeoutMillis", 30_000)
    output = data.get("maxOutputBytes", 1_048_576)
    if type(timeout) is not int or timeout < 1 or type(output) is not int or output < 1:
        return Result.fail("invalid_request", "worker limits must be positive integers")
    return Result.success(WorkerOperation(
        operation=data["verb"],
        args=dict(data["args"]),
        working_directory=str(data.get("workingDirectory", ".")),
        timeout_seconds=timeout / 1000,
        max_output_bytes=output,
        request_id=data["requestId"],
    ))


class WorkerProtocol:
    """Unified protocol routing all verbs through the sandbox runner."""

    SUPPORTED_OPERATIONS = {
        "fs.read",
        "fs.search",
        "fs.write",
        "patch.apply",
        "fs.patch",
        "proc.exec",
        "proc.test",
    }

    def __init__(self, runner: SandboxRunner,
                 allowed_executables: tuple[str, ...] = ("git", "pytest", "ruff", "python3")) -> None:
        self.runner = runner
        self.allowed_executables = frozenset(allowed_executables)

    def execute(self, operation: WorkerOperation) -> Result[WorkerResult]:
        if operation.operation not in self.SUPPORTED_OPERATIONS:
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
            argv = ["cat", "--", path_str]

        elif operation.operation == "fs.search":
            pattern = operation.args.get("pattern")
            path_str = operation.args.get("path", ".")
            if not isinstance(pattern, str) or not isinstance(path_str, str):
                return Result.fail("invalid_request", "Missing pattern or path for fs.search")
            path = pathlib.Path(path_str)
            if path.is_absolute() or ".." in path.parts:
                return Result.fail("invalid_path", "Path must be relative and not traverse")
            argv = ["grep", "-rn", "--", pattern, path_str]

        elif operation.operation == "fs.write":
            path_str = operation.args.get("path")
            content = operation.args.get("content", "")
            if not isinstance(path_str, str) or not isinstance(content, str):
                return Result.fail("invalid_request", "Missing path or content for fs.write")
            path = pathlib.Path(path_str)
            if path.is_absolute() or ".." in path.parts:
                return Result.fail("invalid_path", "Path must be relative and not traverse")
            # For ``python -c``, argv[0] is already ``-c``; inserting a
            # conventional ``--`` would shift the path and write a file named
            # ``--`` instead of the requested workspace target.
            argv = ["/usr/bin/python3", "-c", _SAFE_WRITE, path_str, content]

        elif operation.operation in ("patch.apply", "fs.patch"):
            content = operation.args.get("patch") or operation.args.get("diff")
            if not isinstance(content, str):
                return Result.fail("invalid_request", "Missing patch/diff content")
            flag = " --dry-run" if operation.args.get("dry_run") is True else ""
            argv = ["/bin/sh", "-c", f'printf "%s" "$1" | patch -p1{flag}', "--", content]

        elif operation.operation in ("proc.exec", "proc.test"):
            cmd_argv = operation.args.get("argv")
            if isinstance(cmd_argv, list) and all(isinstance(a, str) for a in cmd_argv):
                argv = cmd_argv
            else:
                return Result.fail(
                    "invalid_request", "proc execution requires argv array"
                )
            executable = pathlib.PurePosixPath(argv[0]).name
            if executable not in self.allowed_executables:
                return Result.fail("denied", f"process executable is not manifest-allowed: {executable}")

        final_argv = argv
        if str(wd) != ".":
            final_argv = ["/bin/sh", "-c", 'cd "$1" && shift && exec "$@"', "--", str(wd)] + argv

        res = self.runner.execute(tuple(final_argv))
        if not res.ok:
            return Result.fail(res.error.kind, res.error.message)

        receipt = res.value.receipt
        containment = res.value.containment

        if not getattr(containment, "verified", getattr(containment, "rootless", True)):
            return Result.fail("containment_unverified", "worker containment probes are unverified")

        stdout_bytes = receipt.stdout or b""
        stderr_bytes = receipt.stderr or b""
        truncated = bool(receipt.truncated)
        stdout_str = (receipt.stdout or b"").decode("utf-8", "replace")
        stderr_str = (receipt.stderr or b"").decode("utf-8", "replace")
        truncated = receipt.truncated

        if len(stdout_str) > operation.max_output_bytes:
            stdout_str = stdout_str[: operation.max_output_bytes]
            truncated = True

        if len(stderr_str) > operation.max_output_bytes:
            stderr_str = stderr_str[: operation.max_output_bytes]
            truncated = True

        return Result.success(
            WorkerResult(
                exit_code=receipt.exit_code,
                stdout=stdout_str,
                stderr=stderr_str,
                stdout_digest=receipt.stdout_digest or ("sha256:" + "0" * 64),
                truncated=truncated,
                duration_millis=receipt.duration_millis,
            )
        )
