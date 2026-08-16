"""OpenAI-compatible HTTP front for LAM. POST /v1/chat/completions"""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from engine import LamEngine

_ENGINE = LamEngine.from_directory(Path(__file__).resolve().parent / "scenarios")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return

    def do_POST(self) -> None:  # noqa: N802
        if self.path.rstrip("/") != "/v1/chat/completions":
            self._send(404, {"error": {"message": "not found", "type": "invalid_request_error"}})
            return
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length)
        try:
            body = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            self._send(400, {"error": {"message": "invalid json", "type": "invalid_request_error"}})
            return
        try:
            completion = _ENGINE.complete(body)
        except KeyError as exc:
            self._send(404, {"error": {"message": f"unknown lam scenario: {exc}", "type": "invalid_request_error"}})
            return
        self._send(200, completion)

    def _send(self, status: int, payload: dict) -> None:
        blob = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(blob)))
        self.end_headers()
        self.wfile.write(blob)


def main(host: str = "127.0.0.1", port: int = 8787) -> None:
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"LAM listening on http://{host}:{port}/v1/chat/completions")
    server.serve_forever()


if __name__ == "__main__":
    main()
