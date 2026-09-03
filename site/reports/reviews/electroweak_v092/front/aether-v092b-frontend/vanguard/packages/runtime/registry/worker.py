"""Plugin child: JSON-RPC 2.0 server over a filesystem Unix domain socket."""

from __future__ import annotations

import argparse
import os
import signal
import socket
import sys

from .sandbox import SandboxLimits, apply_rlimits
from vanguard.packages.domain.wire import jsonrpc

__all__ = ["main"]

_EXECUTE_COUNT = 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="mhf-plugin-worker")
    parser.add_argument("--socket", required=True)
    parser.add_argument("--cpu", type=int, default=2)
    parser.add_argument("--as-bytes", type=int, default=256 * 1024 * 1024)
    parser.add_argument("--nofile", type=int, default=64)
    parser.add_argument("--nproc", type=int, default=64)
    args = parser.parse_args(argv)
    apply_rlimits(
        SandboxLimits(
            cpu_seconds=args.cpu,
            address_space_bytes=args.as_bytes,
            max_open_files=args.nofile,
            max_processes=args.nproc,
        )
    )
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    if os.path.exists(args.socket):
        os.remove(args.socket)
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(args.socket)
    os.chmod(args.socket, 0o600)
    server.listen(8)
    try:
        while True:
            conn, _ = server.accept()
            with conn:
                _handle(conn)
    except SystemExit:
        raise
    finally:
        try:
            os.unlink(args.socket)
        except OSError:
            pass
    return 0


def _handle(conn: socket.socket) -> None:
    raw = _read_frame(conn)
    if not raw:
        return
    try:
        message = jsonrpc.loads(raw)
    except jsonrpc.JsonRpcError as exc:
        conn.sendall(jsonrpc.dumps_error(None, exc.code, exc.message))
        return
    rpc_id = message.get("id")
    method = str(message.get("method", ""))
    params = message.get("params") or {}
    if not isinstance(params, dict):
        conn.sendall(jsonrpc.dumps_error(rpc_id, "invalid_params", "params must be object"))
        return
    try:
        result = _dispatch(method, params)
    except jsonrpc.JsonRpcError as exc:
        conn.sendall(jsonrpc.dumps_error(rpc_id, exc.code, exc.message))
        return
    except Exception as exc:  # noqa: BLE001 — cell must not die on a bad call
        conn.sendall(jsonrpc.dumps_error(rpc_id, "internal_error", str(exc)))
        return
    conn.sendall(jsonrpc.dumps_result(rpc_id, result))


def _read_frame(conn: socket.socket) -> bytes:
    buf = b""
    while b"\n" not in buf:
        chunk = conn.recv(4096)
        if not chunk:
            break
        buf += chunk
        if len(buf) > 65_536:
            break
    return buf


def _dispatch(method: str, params: dict) -> object:
    global _EXECUTE_COUNT
    if method == "health":
        import resource

        def _pair(tag: int) -> tuple[int, int]:
            return resource.getrlimit(tag)

        return {
            "ok": True,
            "execute_count": _EXECUTE_COUNT,
            "rlimits": {
                "cpu": _pair(resource.RLIMIT_CPU),
                "as": _pair(resource.RLIMIT_AS),
                "nofile": _pair(resource.RLIMIT_NOFILE),
                "nproc": _pair(resource.RLIMIT_NPROC),
            },
        }
    if method == "verbs":
        return {"echo": {"type": "object"}, "fs.read": {"type": "object"}}
    if method == "execute":
        _EXECUTE_COUNT += 1
        args = params.get("args") if isinstance(params.get("args"), dict) else {}
        text = str(args.get("text", params.get("verb", "")))
        print(text, flush=True)
        verb = str(params.get("verb", "echo"))
        if verb == "fs.read":
            return {"path": args.get("path"), "echo": text}
        return {"echo": text or "ok"}
    if method == "compensate":
        return {"ok": True}
    if method in {"quiesce", "init"}:
        return {"ok": True}
    raise jsonrpc.JsonRpcError("method_not_found", method)


if __name__ == "__main__":
    sys.exit(main())
