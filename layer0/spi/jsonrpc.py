"""Line-delimited JSON-RPC 2.0 codec for plugin-cell UDS (SPEC §2.1)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Mapping

__all__ = ["JsonRpcError", "dumps_error", "dumps_request", "dumps_result", "loads"]


class JsonRpcError(ValueError):
    def __init__(self, code: str | int, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def dumps_request(rpc_id: int | str, method: str, params: Mapping[str, Any] | None = None) -> bytes:
    payload: dict[str, Any] = {"jsonrpc": "2.0", "id": rpc_id, "method": method}
    if params is not None:
        payload["params"] = dict(params)
    return _line(payload)


def dumps_result(rpc_id: int | str, result: Any) -> bytes:
    return _line({"jsonrpc": "2.0", "id": rpc_id, "result": result})


def dumps_error(rpc_id: int | str | None, code: str | int, message: str) -> bytes:
    return _line(
        {
            "jsonrpc": "2.0",
            "id": rpc_id,
            "error": {"code": code, "message": message},
        }
    )


def loads(line: str | bytes) -> dict[str, Any]:
    if isinstance(line, bytes):
        text = line.decode("utf-8")
    else:
        text = line
    text = text.strip()
    if not text:
        raise JsonRpcError("parse_error", "empty frame")
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise JsonRpcError("parse_error", str(exc)) from exc
    if not isinstance(value, dict) or value.get("jsonrpc") != "2.0":
        raise JsonRpcError("invalid_request", "not JSON-RPC 2.0")
    return value


def _line(payload: Mapping[str, Any]) -> bytes:
    return json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8") + b"\n"
