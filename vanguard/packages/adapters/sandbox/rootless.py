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
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

from ...ports.event_store import Result
from ...ports.sandbox import ContainmentReport, ProbeResult, SandboxReceipt, SandboxResult

__all__ = ["RootlessSandboxRunner"]


@dataclass(frozen=True, slots=True)
class _Invocation:
    returncode: int
    stdout: bytes
    stderr: bytes
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
    ) -> None:
        self.workspace = Path(workspace).resolve(strict=True)
        self.evaluator_bundle = Path(evaluator_bundle).resolve(strict=True)
        self.runtime = runtime
        self.timeout_seconds = timeout_seconds
        self._attested_at = attested_at

    def _runtime_prefix(self) -> list[str]:
        prefix = [
            self.runtime,
            "--unshare-all",
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
        try:
            process = subprocess.Popen(
                command,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True,
            )
        except OSError as exc:
            return _Invocation(126, b"", str(exc).encode(), started=False)
        try:
            stdout, stderr = process.communicate(timeout=self.timeout_seconds)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            stdout, stderr = process.communicate()
            return _Invocation(124, stdout, stderr + b"\nworker process group timed out")
        return _Invocation(process.returncode, stdout, stderr)

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

    def execute(self, argv: Sequence[str]) -> Result[SandboxResult]:
        if not argv or not all(isinstance(arg, str) and arg for arg in argv):
            return Result.fail("invalid_request", "sandbox argv must be a non-empty string sequence")

        probes = self._probes()
        invocation = self._run_isolated(tuple(argv))
        verified = invocation.started and all(probe.verified for probe in probes)
        attested_at = self._attested_at or datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
        report = ContainmentReport(
            runtime="bubblewrap-rootless",
            runtime_version=self._runtime_version(),
            namespace="user,mount,ipc,pid,uts,cgroup,network",
            syscall_profile="namespace capability boundary; denial probe recorded",
            network_enforcement="outer bubblewrap network namespace",
            writable_mounts=("/workspace", "/tmp"),
            exposed_sockets=(),
            resource_limits={"wallClockSeconds": self.timeout_seconds},
            startup_probes=probes,
            attested_at=attested_at,
            contained=verified,
            verified=verified,
            visibility_mark="probe-verified-rootless" if verified else "unverified-rootless-perimeter",
        )
        digest = "sha256:" + hashlib.sha256(invocation.stdout).hexdigest()
        return Result.success(
            SandboxResult(
                receipt=SandboxReceipt(exit_code=invocation.returncode, stdout_digest=digest),
                containment=report,
            )
        )
