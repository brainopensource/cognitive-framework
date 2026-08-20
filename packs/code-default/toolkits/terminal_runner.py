"""Streaming proc.exec toolkit with first-failure classification (mhf.toolkit.terminal)."""

from __future__ import annotations

import os
import re
import subprocess
import time
from pathlib import Path
from typing import ClassVar, Mapping

from vanguard.packages.domain.wire.result import Err, Ok, Result
from vanguard.packages.domain.wire.types_gen import EffectContext, EffectRequest, Health, Receipt, ToolSchema

__all__ = ["TerminalToolkit"]

_FAIL = re.compile(r"(FAILED|FAIL:|E\s+\w+|Error:)")


class TerminalToolkit:
    spi_version: ClassVar[str] = "1.0"

    def __init__(self, workspace: str | Path, timeout_seconds: float = 30.0) -> None:
        self._root = Path(workspace)
        self._timeout = timeout_seconds
        self.last_first_failure_ms: float | None = None
        self.last_events: list[dict[str, object]] = []

    def verbs(self) -> Mapping[str, ToolSchema]:
        return {
            "proc.exec": ToolSchema(
                verb="proc.exec",
                schema={"type": "object", "properties": {"argv": {"type": "array"}}, "required": ["argv"]},
            )
        }

    def execute(self, request: EffectRequest, ctx: EffectContext) -> Result[Receipt]:
        _ = ctx
        if request.verb != "proc.exec":
            return Err("unknown_verb", request.verb)
        argv = request.args.get("argv") or request.args.get("command")
        if not isinstance(argv, (list, tuple)) or not all(isinstance(item, str) for item in argv):
            return Err("invalid_request", "argv must be a string list")
        started = time.monotonic()
        self.last_first_failure_ms = None
        self.last_events = []
        try:
            proc = subprocess.Popen(
                list(argv),
                cwd=str(self._root),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                env={**os.environ, "PYTHONUNBUFFERED": "1"},
                bufsize=1,
            )
        except OSError as exc:
            return Err("instrument_error", str(exc), instrument_error=True)
        assert proc.stdout is not None
        chunks: list[str] = []
        deadline = started + self._timeout
        try:
            while True:
                if time.monotonic() > deadline:
                    proc.kill()
                    return Err("timeout", "proc.exec exceeded lease")
                line = proc.stdout.readline()
                if not line:
                    break
                chunks.append(line)
                if self.last_first_failure_ms is None and _FAIL.search(line):
                    self.last_first_failure_ms = (time.monotonic() - started) * 1000.0
                    self.last_events.append({"kind": "first_failure", "line": line.rstrip(), "ms": self.last_first_failure_ms})
            code = proc.wait()
        finally:
            if proc.stdout is not None:
                proc.stdout.close()
        outcome = "completed" if code == 0 else "failed"
        return Ok(Receipt(request_digest="sha256:" + "b" * 64, outcome=outcome, cost=request.reservation))

    def compensate(self, receipt: Receipt) -> Result[Receipt]:
        return Ok(receipt)

    def health(self) -> Health:
        return Health(ok=True)
