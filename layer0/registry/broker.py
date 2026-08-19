"""Plugin isolation broker: process FSM, UDS JSON-RPC client, crash containment."""

from __future__ import annotations

import os
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Mapping, Sequence

from layer0.events.emitter import LedgerEmitter
from layer0.registry.sandbox import SandboxLimits, apply_rlimits, open_log_sink
from layer0.spi import jsonrpc
from layer0.spi.ceiling import ceiling_allows
from layer0.spi.types_gen import EventKind

__all__ = [
    "CellState",
    "IllegalCellTransition",
    "PluginCell",
    "PluginIsolationBroker",
    "RpcResponse",
]

_ALLOWED_METHODS = frozenset({"execute", "health", "compensate", "verbs", "quiesce", "init"})
_REPO_ROOT = Path(__file__).resolve().parents[2]


class CellState(str, Enum):
    UNINSTANTIATED = "uninstantiated"
    BOUND = "bound"
    RUNNING = "running"
    TERMINATED = "terminated"


class IllegalCellTransition(ValueError):
    pass


@dataclass
class RpcResponse:
    ok: bool
    result: Any = None
    error: dict[str, Any] | None = None


@dataclass
class PluginCell:
    plugin_id: str
    state: CellState = CellState.UNINSTANTIATED
    pid: int | None = None
    socket_path: str = ""
    stdout_log: str = ""
    capabilities: tuple[Mapping[str, Any], ...] = ()
    limits: SandboxLimits = field(default_factory=SandboxLimits)
    workdir: str = ""
    _proc: subprocess.Popen[bytes] | None = field(default=None, repr=False)
    _log: Any = field(default=None, repr=False)
    _rpc_id: int = field(default=0, repr=False)


class PluginIsolationBroker:
    """UNINSTANTIATED → BOUND → RUNNING → TERMINATED. Child death never kills Layer-0."""

    def __init__(
        self,
        emitter: LedgerEmitter,
        *,
        run_id: str,
        principal: str,
        call_timeout: float = 2.0,
    ) -> None:
        self._emitter = emitter
        self._run_id = run_id
        self._principal = principal
        self._timeout = call_timeout
        self._cells: dict[str, PluginCell] = {}

    def cell(self, plugin_id: str) -> PluginCell:
        existing = self._cells.get(plugin_id)
        if existing is not None:
            return existing
        return PluginCell(plugin_id=plugin_id)

    def bind(
        self,
        plugin_id: str,
        *,
        limits: SandboxLimits | None = None,
        capabilities: Sequence[Mapping[str, Any]] = (),
    ) -> PluginCell:
        if plugin_id in self._cells and self._cells[plugin_id].state is not CellState.TERMINATED:
            raise IllegalCellTransition(f"{plugin_id} already bound")
        workdir = tempfile.mkdtemp(prefix=f"mhf-{plugin_id.replace('.', '-')}-")
        cell = PluginCell(
            plugin_id=plugin_id,
            state=CellState.BOUND,
            socket_path=str(Path(workdir) / "cell.sock"),
            stdout_log=str(Path(workdir) / "child.log"),
            capabilities=tuple(dict(item) for item in capabilities),
            limits=limits or SandboxLimits(),
            workdir=workdir,
        )
        self._cells[plugin_id] = cell
        return cell

    def start(self, cell: PluginCell) -> None:
        if cell.state is not CellState.BOUND:
            raise IllegalCellTransition(f"{cell.state.value} → running")
        log = open_log_sink(cell.stdout_log)
        env = os.environ.copy()
        pythonpath = str(_REPO_ROOT)
        existing = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = pythonpath if not existing else pythonpath + os.pathsep + existing
        argv = [
            sys.executable,
            "-m",
            "layer0.registry.worker",
            "--socket",
            cell.socket_path,
            "--cpu",
            str(cell.limits.cpu_seconds),
            "--as-bytes",
            str(cell.limits.address_space_bytes),
            "--nofile",
            str(cell.limits.max_open_files),
            "--nproc",
            str(cell.limits.max_processes),
        ]
        try:
            proc = subprocess.Popen(
                argv,
                stdout=log,
                stderr=subprocess.STDOUT,
                cwd=cell.workdir,
                env=env,
                close_fds=True,
                preexec_fn=_child_preexec(cell.limits),
            )
        except Exception:
            log.close()
            self._fault(cell, "spawn_failed")
            raise
        cell._proc = proc
        cell._log = log
        cell.pid = proc.pid
        if not _wait_for(lambda: Path(cell.socket_path).exists(), timeout=5.0):
            self._fault(cell, "socket_timeout")
            raise TimeoutError(f"plugin {cell.plugin_id} did not bind UDS")
        cell.state = CellState.RUNNING

    def call(self, cell: PluginCell, method: str, params: Mapping[str, Any] | None = None) -> RpcResponse:
        payload = dict(params or {})
        if cell.state is not CellState.RUNNING:
            return RpcResponse(ok=False, error={"code": "plugin_failed", "message": "cell is not running"})
        if not ceiling_allows(method, payload, cell.capabilities):
            return RpcResponse(
                ok=False,
                error={"code": "attenuation_denied", "message": f"{method} exceeds plugin ceiling"},
            )
        if method not in _ALLOWED_METHODS:
            return RpcResponse(
                ok=False,
                error={"code": "attenuation_denied", "message": f"{method} is not a host method"},
            )
        cell._rpc_id += 1
        rpc_id = cell._rpc_id
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
                sock.settimeout(self._timeout)
                sock.connect(cell.socket_path)
                sock.sendall(jsonrpc.dumps_request(rpc_id, method, payload))
                raw = _read_frame(sock)
            if not raw:
                raise ConnectionError("empty RPC frame")
            message = jsonrpc.loads(raw)
        except Exception:
            self._fault(cell, "PluginFailed")
            return RpcResponse(ok=False, error={"code": "plugin_failed", "message": "cell died"})
        if "error" in message:
            error = message["error"]
            if not isinstance(error, dict):
                error = {"code": "rpc_error", "message": str(error)}
            return RpcResponse(ok=False, error=error)
        return RpcResponse(ok=True, result=message.get("result"))

    def terminate(self, cell: PluginCell) -> None:
        if cell.state is CellState.TERMINATED:
            return
        if cell.state is CellState.UNINSTANTIATED:
            raise IllegalCellTransition("uninstantiated → terminated")
        self._stop_process(cell, expected=True)
        self._cleanup(cell)
        cell.state = CellState.TERMINATED

    def reap(self, cell: PluginCell, timeout: float = 3.0) -> None:
        if cell.state is CellState.TERMINATED:
            return
        proc = cell._proc
        if proc is not None and proc.poll() is None:
            deadline = time.monotonic() + timeout
            while time.monotonic() < deadline and proc.poll() is None:
                time.sleep(0.02)
        if cell.state is CellState.RUNNING:
            self._fault(cell, "PluginFailed")

    def shutdown(self) -> None:
        for cell in list(self._cells.values()):
            if cell.state is CellState.TERMINATED:
                continue
            try:
                self.terminate(cell)
            except Exception:
                self._fault(cell, "shutdown")

    def _fault(self, cell: PluginCell, reason: str) -> None:
        if cell.state is CellState.TERMINATED:
            return
        self._stop_process(cell, expected=False)
        self._cleanup(cell)
        cell.state = CellState.TERMINATED
        self._emitter.emit_kind(
            EventKind.PLUGIN_FAULTED,
            run_id=self._run_id,
            principal=self._principal,
            payload={
                "plugin_id": cell.plugin_id,
                "reason": reason,
                "status": "PluginFailed",
            },
            alertable=True,
        )

    def _stop_process(self, cell: PluginCell, *, expected: bool) -> None:
        proc = cell._proc
        if proc is None:
            return
        if proc.poll() is None:
            try:
                proc.send_signal(signal.SIGTERM)
            except OSError:
                pass
            try:
                proc.wait(timeout=1.0)
            except subprocess.TimeoutExpired:
                try:
                    proc.kill()
                    proc.wait(timeout=1.0)
                except OSError:
                    pass
        cell._proc = None
        cell.pid = None
        log = cell._log
        if log is not None:
            try:
                log.close()
            except OSError:
                pass
            cell._log = None
        _ = expected

    def _cleanup(self, cell: PluginCell) -> None:
        if cell.socket_path:
            try:
                os.unlink(cell.socket_path)
            except OSError:
                pass
        if cell.workdir:
            shutil.rmtree(cell.workdir, ignore_errors=True)


def _child_preexec(limits: SandboxLimits):
    def _inner() -> None:
        apply_rlimits(limits)
        try:
            os.setsid()
        except OSError:
            pass

    return _inner


def _read_frame(sock: socket.socket) -> bytes:
    buf = b""
    while b"\n" not in buf:
        chunk = sock.recv(4096)
        if not chunk:
            break
        buf += chunk
        if len(buf) > 65_536:
            break
    return buf


def _wait_for(predicate, timeout: float) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(0.02)
    return False
