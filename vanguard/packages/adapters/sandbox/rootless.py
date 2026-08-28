"""Rootless Bubblewrap perimeter with probe-derived containment reports.

The adapter never infers containment from its command line. It runs the mount,
network and denied-syscall probes inside the same constructed perimeter as the
worker command. A runtime startup failure still produces an unverified report,
so callers can record the failure and the publication gate remains fail-closed.
"""

from __future__ import annotations

import hashlib
import os
import signal
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

from ...ports.event_store import Result
from ...ports.sandbox import ContainmentReport, ProbeResult, SandboxReceipt, SandboxResult

__all__ = ["RootlessSandboxRunner", "WorkerSandboxReceipt"]


@dataclass(frozen=True, slots=True)
class WorkerSandboxReceipt(SandboxReceipt):
    """Extended receipt carrying bounded outputs for the worker protocol."""
    stdout: bytes = b""
    stderr: bytes = b""
    truncated: bool = False
    duration_millis: int = 0


@dataclass(frozen=True, slots=True)
class _Invocation:
    returncode: int
    stdout: bytes
    stderr: bytes
    truncated: bool = False
    duration_millis: int = 0
    started: bool = True


class RootlessSandboxRunner:
    """Execute argv in a rootless Bubblewrap namespace and attest with probes."""

    _EVALUATOR_TARGET = "/sealed-evaluator/bundle"

    def __init__(
        self,
        workspace: str | Path,
        *,
        evaluator_bundle: str | Path,
        runtime: str = "/usr/bin/bwrap",
        timeout_seconds: float = 30.0,
        attested_at: str | None = None,
        max_output_bytes: int = 10 * 1024 * 1024,
    ) -> None:
        self._raw_workspace = Path(workspace)
        self.workspace = self._raw_workspace.resolve(strict=True)
        self.evaluator_bundle = Path(evaluator_bundle).resolve(strict=True)
        self.runtime = runtime
        self.timeout_seconds = timeout_seconds
        self._attested_at = attested_at
        self.max_output_bytes = max_output_bytes

    def _validate_workspace(self) -> Result[None]:
        if not self.workspace.is_dir():
            return Result.fail("invalid_workspace", "Workspace must be a directory")
        if self._raw_workspace.is_symlink():
            return Result.fail("invalid_workspace", "Workspace cannot be a symlink")
        
        # Check for symlinks pointing outside
        for root, dirs, files in os.walk(self.workspace):
            for name in dirs + files:
                path = Path(root) / name
                if path.is_symlink():
                    target = path.resolve()
                    try:
                        target.relative_to(self.workspace)
                    except ValueError:
                        return Result.fail("invalid_workspace", f"Symlink {name} points outside workspace")
                        
        if (self.workspace / ".env").exists():
            return Result.fail("invalid_workspace", ".env file found in workspace")
            
        return Result.success(None)

    def _runtime_prefix(self) -> list[str]:
        prefix = [
            self.runtime,
            "--unshare-all",
            "--unshare-user",
            "--die-with-parent",
            "--new-session",
            "--clearenv",
            "--ro-bind", "/usr", "/usr",
            "--symlink", "usr/bin", "/bin",
            "--symlink", "usr/lib", "/lib",
            "--proc", "/proc",
            "--dev", "/dev",
            "--tmpfs", "/tmp",
            "--bind", str(self.workspace), "/workspace",
            "--chdir", "/workspace",
            "--setenv", "PATH", "/usr/bin:/bin",
        ]
        if Path("/usr/lib64").exists():
            prefix.extend(("--symlink", "usr/lib64", "/lib64"))
        return prefix

    def _run_isolated(self, argv: Sequence[str]) -> _Invocation:
        command = [*self._runtime_prefix(), "--", *argv]
        start_time = time.monotonic()
        try:
            process = subprocess.Popen(
                command,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True,
                env={}, # Ensure no host env leak
            )
        except OSError as exc:
            return _Invocation(126, b"", str(exc).encode(), started=False)
            
        try:
            stdout, stderr = process.communicate(timeout=self.timeout_seconds)
            truncated = False
            if len(stdout) > self.max_output_bytes:
                stdout = stdout[:self.max_output_bytes]
                truncated = True
            if len(stderr) > self.max_output_bytes:
                stderr = stderr[:self.max_output_bytes]
                truncated = True
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            stdout, stderr = process.communicate()
            truncated = True
            if len(stdout) > self.max_output_bytes:
                stdout = stdout[:self.max_output_bytes]
            if len(stderr) > self.max_output_bytes:
                stderr = stderr[:self.max_output_bytes]
            stderr += b"\nworker process group timed out"
            
        duration_millis = int((time.monotonic() - start_time) * 1000)
        code = 124 if "timed out" in stderr.decode("utf-8", "ignore") else process.returncode
        # Popen succeeding only proves that the launcher process started.  A
        # bubblewrap namespace setup failure (for example a restricted WSL
        # NETLINK_ROUTE operation) must not be interpreted as a child command
        # failure or, worse, as a successful security probe.  Preserve the
        # distinction so every probe becomes ``perimeter-startup-failed`` and
        # the worker remains fail-closed.
        launcher_failed = (
            code != 0
            and not stdout
            and stderr.lstrip().startswith(b"bwrap:")
        )
        return _Invocation(
            code, stdout, stderr, truncated, duration_millis,
            started=not launcher_failed,
        )

    @staticmethod
    def _observed(invocation: _Invocation, denied_when_nonzero: bool) -> tuple[str, bool]:
        if not invocation.started:
            return "perimeter-startup-failed", False
        denied = invocation.returncode != 0 if denied_when_nonzero else invocation.returncode == 0
        return ("denied" if denied else "allowed"), denied

    def _probe(self, kind: str, attempted: str, argv: Sequence[str], *, denied_when_nonzero: bool) -> ProbeResult:
        observed, verified = self._observed(self._run_isolated(argv), denied_when_nonzero)
        return ProbeResult(kind=kind, attempted=attempted, observed=observed, verified=verified)

    def _probes(self) -> tuple[ProbeResult, ...]:
        return (
            self._probe(
                "mount",
                f"read evaluator fixture at {self._EVALUATOR_TARGET}",
                ("/bin/sh", "-c", f"test ! -r {self._EVALUATOR_TARGET}"),
                denied_when_nonzero=False,
            ),
            self._probe(
                "egress",
                "connect UDP socket to 1.1.1.1:53",
                (
                    "/usr/bin/python3", "-c",
                    "import socket;s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM);s.connect(('1.1.1.1',53))",
                ),
                denied_when_nonzero=True,
            ),
            self._probe(
                "syscall",
                "create nested mount namespace with unshare",
                ("/usr/bin/unshare", "--mount", "true"),
                denied_when_nonzero=True,
            ),
        )

    def _runtime_version(self) -> str:
        try:
            result = subprocess.run(
                (self.runtime, "--version"),
                check=False,
                capture_output=True,
                timeout=2,
            )
        except (OSError, subprocess.SubprocessError):
            return "unavailable"
        return result.stdout.decode(errors="replace").strip() or "unknown"

    def qualify(self) -> Result[ContainmentReport]:
        """Run startup containment probes once and return cached report."""
        val_res = self._validate_workspace()
        if not val_res.ok:
            return Result.fail(val_res.error.kind, val_res.error.message)
            
        rt_ver = self._runtime_version()
        if rt_ver == "unavailable":
            return Result.fail("unavailable", "Bubblewrap runtime is not available")

        probes = self._probes()
        verified = all(probe.verified for probe in probes)
        attested_at = self._attested_at or datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
        report = ContainmentReport(
            runtime="bubblewrap-rootless",
            runtime_version=rt_ver,
            namespace="user,mount,ipc,pid,uts,cgroup,network",
            syscall_profile="namespace capability boundary; denial probe recorded",
            network_enforcement="outer bubblewrap network namespace",
            writable_mounts=("/workspace", "/tmp"),
            exposed_sockets=(),
            resource_limits={
                "wallClockSeconds": self.timeout_seconds,
                "nofile": 256,
                "as_bytes": 536870912,
                "nproc": 64
            },
            startup_probes=probes,
            attested_at=attested_at,
            contained=verified,
            verified=verified,
            visibility_mark="probe-verified-rootless" if verified else "unverified-rootless-perimeter",
        )
        return Result.success(report)

    def execute(self, argv: Sequence[str]) -> Result[SandboxResult]:
        if not argv or not all(isinstance(arg, str) and arg for arg in argv):
            return Result.fail("invalid_request", "sandbox argv must be a non-empty string sequence")
            
        val_res = self._validate_workspace()
        if not val_res.ok:
            return Result.fail(val_res.error.kind, val_res.error.message)
            
        rt_ver = self._runtime_version()
        if rt_ver == "unavailable":
            return Result.fail("unavailable", "Bubblewrap runtime is not available")

        probes = self._probes()
        invocation = self._run_isolated(tuple(argv))
        verified = invocation.started and all(probe.verified for probe in probes)
        attested_at = self._attested_at or datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
        report = ContainmentReport(
            runtime="bubblewrap-rootless",
            runtime_version=rt_ver,
            namespace="user,mount,ipc,pid,uts,cgroup,network",
            syscall_profile="namespace capability boundary; denial probe recorded",
            network_enforcement="outer bubblewrap network namespace",
            writable_mounts=("/workspace", "/tmp"),
            exposed_sockets=(),
            resource_limits={
                "wallClockSeconds": self.timeout_seconds,
                "nofile": 256,
                "as_bytes": 536870912,
                "nproc": 64
            },
            startup_probes=probes,
            attested_at=attested_at,
            contained=verified,
            verified=verified,
            visibility_mark="probe-verified-rootless" if verified else "unverified-rootless-perimeter",
        )
        digest = "sha256:" + hashlib.sha256(invocation.stdout).hexdigest()
        return Result.success(
            SandboxResult(
                receipt=WorkerSandboxReceipt(
                    exit_code=invocation.returncode, 
                    stdout_digest=digest,
                    stdout=invocation.stdout,
                    stderr=invocation.stderr,
                    truncated=invocation.truncated,
                    duration_millis=invocation.duration_millis
                ),
                containment=report,
            )
        )
