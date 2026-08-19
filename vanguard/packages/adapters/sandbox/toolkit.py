"""IToolkit client over the plugin-cell UDS JSON-RPC boundary."""

from __future__ import annotations

import socket
from typing import Any, ClassVar, Mapping, Sequence

from layer0.spi import jsonrpc
from layer0.spi.ceiling import ceiling_allows
from layer0.spi.result import Err, Ok, Result
from layer0.spi.types_gen import (
    EffectContext,
    EffectRequest,
    Health,
    Receipt,
    Reservation,
    ToolSchema,
)

__all__ = ["SubprocessToolkitAdapter"]


class SubprocessToolkitAdapter:
    spi_version: ClassVar[str] = "1.0"

    def __init__(
        self,
        socket_path: str,
        *,
        capabilities: Sequence[Mapping[str, Any]] = (),
        timeout: float = 2.0,
        reservation: Reservation | None = None,
    ) -> None:
        self._socket_path = socket_path
        self._capabilities = tuple(dict(item) for item in capabilities)
        self._timeout = timeout
        self._reservation = reservation or Reservation(0, 0, 0, 0, 0, 0)
        self._rpc_id = 0

    def verbs(self) -> Mapping[str, ToolSchema]:
        response = self._call("verbs", {})
        if not isinstance(response, dict):
            return {}
        return {
            str(name): ToolSchema(verb=str(name), schema=schema if isinstance(schema, Mapping) else {})
            for name, schema in response.items()
        }

    def execute(self, request: EffectRequest, ctx: EffectContext) -> Result[Receipt]:
        _ = ctx
        params = {
            "verb": request.verb,
            "args": dict(request.args),
            "selector": dict(request.selector),
            "sink": request.sink.value,
        }
        if not ceiling_allows("execute", params, self._capabilities):
            return Err("attenuation_denied", f"{request.verb} exceeds plugin ceiling")
        result = self._call("execute", params)
        if isinstance(result, Err):
            return result
        return Ok(
            Receipt(
                request_digest="sha256:" + "a" * 64,
                outcome="completed",
                cost=request.reservation,
            )
        )

    def compensate(self, receipt: Receipt) -> Result[Receipt]:
        result = self._call("compensate", {"request_digest": receipt.request_digest})
        if isinstance(result, Err):
            return result
        return Ok(receipt)

    def health(self) -> Health:
        result = self._call("health", {})
        if isinstance(result, Err):
            return Health(ok=False, detail=result.message)
        ok = True
        if isinstance(result, Mapping):
            ok = bool(result.get("ok", True))
        return Health(ok=ok)

    def _call(self, method: str, params: Mapping[str, Any]) -> Any:
        self._rpc_id += 1
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
                sock.settimeout(self._timeout)
                sock.connect(self._socket_path)
                sock.sendall(jsonrpc.dumps_request(self._rpc_id, method, params))
                raw = _read_frame(sock)
            message = jsonrpc.loads(raw)
        except OSError as exc:
            return Err("plugin_failed", str(exc), instrument_error=True)
        if "error" in message:
            error = message["error"]
            code = str(error.get("code") if isinstance(error, Mapping) else "rpc_error")
            text = str(error.get("message") if isinstance(error, Mapping) else error)
            return Err(code, text)
        return message.get("result")


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
