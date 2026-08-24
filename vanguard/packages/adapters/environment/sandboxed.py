"""Sandbox-backed environment adapter routing all operations through the worker.

Owning contract: S6B-MD-005, VG-03 §7.1.
This adapter ensures no direct host filesystem or subprocess access.

The worker is injected at composition time (runtime/root.py). This module
never imports from the sandbox adapter family, preserving LT-5.
"""

from __future__ import annotations

import datetime
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Optional, Protocol

from ...ports.environment import (
    EnvironmentAdapter,
    EnvironmentProfile,
    EnvironmentSnapshot,
    Observation,
    ObservationRequest,
    EffectRequest,
    EffectPreview,
    EffectReceipt,
    Reconciliation,
)
from ...ports.event_store import Result

__all__ = ["SandboxedEnvironmentAdapter", "WorkerRequest", "WorkerReply"]


@dataclass(frozen=True, slots=True)
class WorkerRequest:
    """A request to the worker, defined here so the environment adapter
    can construct it without importing the sandbox adapter family."""

    operation: str  # filesystem and process verbs routed through WorkerProtocol
    args: Mapping[str, Any]
    working_directory: str = "."
    timeout_seconds: float = 30.0
    max_output_bytes: int = 10_485_760


@dataclass(frozen=True, slots=True)
class WorkerReply:
    """A worker reply, matching the structural shape of WorkerResult."""

    exit_code: int
    stdout: str
    stderr: str = ""
    stdout_digest: str = ""
    truncated: bool = False
    duration_millis: int = 0


class WorkerPort(Protocol):
    """Structural protocol for the worker, used by the environment adapter.
    The composition root binds this to the concrete WorkerProtocol."""

    def execute(self, request: Any) -> Any:
        ...



class SandboxedEnvironmentAdapter:
    def __init__(
        self, worker: Any, workspace: Path, environment_id: str,
        *, direct_filesystem: bool = False,
    ) -> None:
        self.worker = worker
        self.workspace = workspace
        self.environment_id = environment_id
        self.containment_report: Any = None
        self._direct_filesystem = direct_filesystem
        from .git import GitEnvironmentAdapter
        self._filesystem = GitEnvironmentAdapter(
            workspace, environment_id=f"{environment_id}:filesystem")

    def qualify(self) -> Result[Any]:
        """Run the worker perimeter probes before release execution starts."""
        runner = getattr(self.worker, "runner", None)
        if runner is not None and hasattr(runner, "qualify"):
            result = runner.qualify()
            if not result.ok:
                return Result.fail(result.error.kind, result.error.message)
            report = result.value
        else:
            result = self.worker.runner.execute(("/usr/bin/true",))
            if not result.ok:
                return Result.fail(result.error.kind, result.error.message)
            report = result.value.containment
        if not report.verified or not report.contained:
            return Result.fail("containment_unverified", "rootless containment probes failed")
        self.containment_report = report
        return Result.success(report)

    def profile(self) -> Result[EnvironmentProfile]:
        return Result.success(
            EnvironmentProfile(
                environment_id=self.environment_id,
                kind="sandboxed",
                root=str(self.workspace),
                capabilities=("sandbox", "read", "search", "patch", "test"),
            )
        )

    def snapshot(self) -> Result[EnvironmentSnapshot]:
        digest = hashlib.sha256()
        for path in sorted(self.workspace.rglob("*")):
            if path.is_symlink() or not path.is_file():
                continue
            digest.update(str(path.relative_to(self.workspace)).encode("utf-8"))
            digest.update(path.read_bytes())
        return Result.success(
            EnvironmentSnapshot(
                snapshot_id="sandbox-" + digest.hexdigest()[:16],
                digest="sha256:" + digest.hexdigest(),
                created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            )
        )

    def observe(self, req: ObservationRequest, grant: Optional[Any] = None) -> Result[Observation]:
        if self._direct_filesystem and req.action in {"read", "search", "list", "glob", "stat"}:
            return self._filesystem.observe(req, grant)
        if req.action == "read":
            if not req.path:
                return Result.fail("invalid_request", "path is required for read")
            op = WorkerRequest(
                operation="fs.read",
                args={"path": req.path},
                working_directory=".",
                timeout_seconds=30.0,
                max_output_bytes=10*1024*1024,
            )
            res = self.worker.execute(op)
            if not res.ok:
                return Result.fail(res.error.kind, res.error.message)
            return Result.success(Observation(
                action="read", content=res.value.stdout,
                metadata={"digest": res.value.stdout_digest,
                          "truncated": res.value.truncated},
            ))
            
        elif req.action == "search":
            if not req.pattern:
                return Result.fail("invalid_request", "pattern is required for search")
            op = WorkerRequest(
                operation="fs.search",
                args={"pattern": req.pattern, "path": req.path or "."},
                working_directory=".",
                timeout_seconds=30.0,
                max_output_bytes=10*1024*1024,
            )
            res = self.worker.execute(op)
            if not res.ok:
                return Result.fail(res.error.kind, res.error.message)
            return Result.success(Observation(
                action="search", output=res.value.stdout,
                metadata={"digest": res.value.stdout_digest,
                          "truncated": res.value.truncated},
            ))
            
        return Result.fail("unsupported_action", f"Action {req.action} not supported")

    def preview(self, req: EffectRequest, grant: Optional[Any] = None) -> Result[EffectPreview]:
        if self._direct_filesystem and (req.verb in {"patch.apply", "fs.patch", "fs.write"} or req.action in {"patch", "write"}):
            return self._filesystem.preview(req, grant)
        if req.verb == "patch.apply" or req.action == "patch":
            patch = req.patch or req.args.get("patch")
            if not patch:
                return Result.fail("invalid_request", "patch content is required")
            op = WorkerRequest(
                operation="patch.apply",
                args={"patch": patch, "dry_run": True},
                working_directory=req.working_directory or ".",
                timeout_seconds=30.0,
                max_output_bytes=10*1024*1024,
            )
            res = self.worker.execute(op)
            if not res.ok:
                return Result.fail(res.error.kind, res.error.message)
            
            return Result.success(EffectPreview(diff=res.value.stdout, stat={"exit_code": res.value.exit_code}))
            
        return Result.fail("unsupported_verb", f"Verb {req.verb} not supported for preview")

    def apply(self, req: EffectRequest, grant: Optional[Any] = None) -> Result[EffectReceipt]:
        if self._direct_filesystem and (req.verb in {"patch.apply", "fs.patch", "fs.write"} or req.action in {"patch", "write"}):
            return self._filesystem.apply(req, grant)
        if req.verb == "patch.apply" or req.action == "patch":
            patch = req.patch or req.args.get("patch")
            if not patch:
                return Result.fail("invalid_request", "patch content is required")
            
            op = WorkerRequest(
                operation="patch.apply",
                args={"patch": patch},
                working_directory=req.working_directory or ".",
                timeout_seconds=30.0,
                max_output_bytes=10*1024*1024,
            )
            res = self.worker.execute(op)
            if not res.ok:
                return Result.fail(res.error.kind, res.error.message)
                
            return Result.success(
                EffectReceipt(
                    descriptor_digest=_descriptor_digest(req),
                    outcome="ok" if res.value.exit_code == 0 else "failed",
                    observed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    result_digest=res.value.stdout_digest,
                    exit_code=res.value.exit_code,
                    output=res.value.stdout + res.value.stderr,
                )
            )
            
        elif req.verb == "proc.exec" or req.action in {"test", "exec"}:
            cmd = req.command or req.args.get("argv")
            if not cmd:
                return Result.fail("invalid_request", "command argv is required")
                
            op = WorkerRequest(
                # `S10-A-02`. This said `proc.test` for every process call,
                # including ones the manifest declared as `proc.exec` -- so the
                # worker allowlist and the ledger saw an operation name the
                # harness never granted.
                operation="proc.exec",
                args={"argv": list(cmd)},
                working_directory=req.working_directory or ".",
                timeout_seconds=30.0,
                max_output_bytes=10*1024*1024,
            )
            res = self.worker.execute(op)
            if not res.ok:
                return Result.fail(res.error.kind, res.error.message)
                
            return Result.success(
                EffectReceipt(
                    descriptor_digest=_descriptor_digest(req),
                    outcome="ok" if res.value.exit_code == 0 else "failed",
                    observed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    result_digest=res.value.stdout_digest,
                    exit_code=res.value.exit_code,
                    output=res.value.stdout + res.value.stderr,
                )
            )

        elif req.verb == "fs.write" or req.action == "write":
            path = req.args.get("path")
            content = req.args.get("content")
            if not isinstance(path, str) or not isinstance(content, str):
                return Result.fail("invalid_request", "fs.write requires path and content")
            op = WorkerRequest(
                operation="fs.write",
                args={"path": path, "content": content},
                working_directory=req.working_directory or ".",
                timeout_seconds=30.0,
                max_output_bytes=10 * 1024 * 1024,
            )
            res = self.worker.execute(op)
            if not res.ok:
                return Result.fail(res.error.kind, res.error.message)
            return Result.success(EffectReceipt(
                descriptor_digest=_descriptor_digest(req),
                outcome="ok" if res.value.exit_code == 0 else "failed",
                observed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                result_digest=res.value.stdout_digest,
                exit_code=res.value.exit_code,
                output=res.value.stdout + res.value.stderr,
            ))

        return Result.fail("unsupported_verb", f"Verb {req.verb} not supported for apply")

    def reconcile(self, receipt: EffectReceipt, grant: Optional[Any] = None) -> Result[Reconciliation]:
        return Result.fail("unsupported_action", "reconcile not supported in sandboxed environment")

    def compensate(self, receipt: EffectReceipt, grant: Optional[Any] = None) -> Result[EffectReceipt]:
        return Result.fail("unsupported_action", "compensate not supported in sandboxed environment")

    def dispose(self) -> Result[None]:
        return Result.success(None)


def _descriptor_digest(request: EffectRequest) -> str:
    payload = {
        "verb": request.verb,
        "action": request.action,
        "args": dict(request.args),
        "patch": request.patch,
        "command": list(request.command) if request.command else None,
        "working_directory": request.working_directory,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "sha256:" + hashlib.sha256(encoded.encode("utf-8")).hexdigest()
