"""Visibly non-contained SandboxRunner fake. Local development only (K-46)."""

from __future__ import annotations

from typing import Sequence

from ...ports.event_store import Result
from ...ports.sandbox import (
    ContainmentReport,
    ProbeResult,
    SandboxReceipt,
    SandboxResult,
)

__all__ = ["FakeSandboxRunner", "NON_CONTAINED_MARK"]

NON_CONTAINED_MARK = "non-contained-development-fake"


class FakeSandboxRunner:
    """Executes nothing. Every report is unverified and visibly non-contained."""

    def execute(self, argv: Sequence[str]) -> Result[SandboxResult]:
        del argv
        report = ContainmentReport(
            runtime="fake",
            runtime_version="0",
            namespace="none",
            syscall_profile="none",
            network_enforcement="none",
            writable_mounts=("host",),
            exposed_sockets=(),
            resource_limits={},
            startup_probes=(
                ProbeResult(
                    kind="syscall",
                    attempted="unshare",
                    observed="not-probed",
                    verified=False,
                ),
            ),
            attested_at="2026-08-15T00:00:00.000Z",
            contained=False,
            verified=False,
            visibility_mark=NON_CONTAINED_MARK,
        )
        return Result.success(
            SandboxResult(receipt=SandboxReceipt(exit_code=0), containment=report)
        )
