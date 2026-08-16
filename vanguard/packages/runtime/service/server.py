"""Unix Domain Socket NDJSON Server for RuntimeService.

Owning contract: REQ-CLI-002, S6B-SA-001, DEC-6B-010, DEC-6B-011.
"""

from __future__ import annotations

import json
import os
import socket
import threading
from pathlib import Path
from typing import Any, Mapping

from ...domain.primitives.primitives import uuidv7
from .service import RuntimeService

MAX_FRAME_BYTES = 1024 * 1024  # 1 MiB


class RuntimeServer:
    """Unix domain socket server serving RuntimeService NDJSON frames."""

    def __init__(
        self,
        service: RuntimeService,
        socket_path: str | Path,
    ) -> None:
        self.service = service
        self.socket_path = Path(socket_path).resolve()
        self._server_sock: socket.socket | None = None
        self._running = False
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()

    def start(self) -> None:
        """Bind socket, set permissions to 0600, and start accept loop."""
        with self._lock:
            if self._running:
                return
            self._running = True

            # Ensure parent dir exists
            self.socket_path.parent.mkdir(parents=True, exist_ok=True)
            if self.socket_path.exists():
                try:
                    self.socket_path.unlink()
                except OSError:
                    pass

            self._server_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self._server_sock.bind(str(self.socket_path))
            # Set mode 0600
            os.chmod(str(self.socket_path), 0o600)
            self._server_sock.listen(128)
            self._server_sock.settimeout(0.5)

            self._thread = threading.Thread(target=self._accept_loop, daemon=True)
            self._thread.start()

    def stop(self) -> None:
        """Stop server and clean up socket file."""
        with self._lock:
            if not self._running:
                return
            self._running = False

            if self._server_sock is not None:
                try:
                    self._server_sock.close()
                except OSError:
                    pass
                self._server_sock = None

            if self.socket_path.exists():
                try:
                    self.socket_path.unlink()
                except OSError:
                    pass

        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=2.0)

    def _accept_loop(self) -> None:
        while self._running:
            try:
                if self._server_sock is None:
                    break
                conn, _ = self._server_sock.accept()
            except (socket.timeout, OSError):
                continue

            t = threading.Thread(target=self._handle_client, args=(conn,), daemon=True)
            t.start()

    def _handle_client(self, conn: socket.socket) -> None:
        with conn:
            buffer = b""
            while self._running:
                try:
                    chunk = conn.recv(8192)
                except OSError:
                    break
                if not chunk:
                    break
                buffer += chunk

                if len(buffer) > MAX_FRAME_BYTES:
                    err = {
                        "version": "vg.4",
                        "frameType": "error",
                        "frameId": uuidv7(),
                        "error": {
                            "code": "frame_too_large",
                            "message": f"frame exceeds {MAX_FRAME_BYTES} bytes limit",
                        },
                    }
                    self._send_frame(conn, err)
                    break

                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)
                    line_str = line.strip().decode("utf-8", "replace")
                    if not line_str:
                        continue

                    try:
                        frame = json.loads(line_str)
                    except json.JSONDecodeError as exc:
                        err = {
                            "version": "vg.4",
                            "frameType": "error",
                            "frameId": uuidv7(),
                            "error": {
                                "code": "invalid_json",
                                "message": f"failed to parse NDJSON frame: {exc}",
                            },
                        }
                        self._send_frame(conn, err)
                        continue

                    self._process_client_frame(conn, frame)

    def _process_client_frame(self, conn: socket.socket, frame: Mapping[str, Any]) -> None:
        cmd = frame.get("command")
        if isinstance(cmd, Mapping) and cmd.get("name") == "StreamEvents":
            run_id = str(cmd.get("runId", ""))
            payload = cmd.get("payload", {})
            after_seq = int(payload.get("afterSeq", 0)) if isinstance(payload, Mapping) else 0

            # Stream events until terminal or disconnected
            try:
                for evt_frame in self.service.stream_events(run_id, after_seq=after_seq):
                    if not self._send_frame(conn, evt_frame):
                        break
            except Exception as exc:
                err = {
                    "version": "vg.4",
                    "frameType": "error",
                    "frameId": uuidv7(),
                    "error": {"code": "streaming_error", "message": str(exc)},
                }
                self._send_frame(conn, err)
            return

        # Regular command-response frame
        resp_frame = self.service.execute_command(frame)
        self._send_frame(conn, resp_frame)

    @staticmethod
    def _send_frame(conn: socket.socket, frame: Mapping[str, Any]) -> bool:
        try:
            line = json.dumps(frame, separators=(",", ":")).encode("utf-8") + b"\n"
            conn.sendall(line)
            return True
        except OSError:
            return False
