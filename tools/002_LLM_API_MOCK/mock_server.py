#!/usr/bin/env python3
"""Standalone lightweight HTTP server simulating OpenAI and Ollama completions."""

from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any
from stub import MockLLMStub


class MockHTTPHandler(BaseHTTPRequestHandler):
    stub = MockLLMStub()

    def _set_headers(self, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

    def do_GET(self) -> None:
        if self.path in ("/health", "/api/tags"):
            self._set_headers(200)
            self.wfile.write(json.dumps({"status": "ok", "models": [{"name": "mock-model"}]}).encode("utf-8"))
        else:
            self._set_headers(200)
            self.wfile.write(json.dumps({"message": "Mock LLM API Server Online"}).encode("utf-8"))

    def do_POST(self) -> None:
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
        try:
            payload = json.loads(post_data)
        except Exception:
            payload = {}

        prompt = payload.get("prompt", "")
        if not prompt and "messages" in payload:
            prompt = " ".join(m.get("content", "") for m in payload["messages"])

        model = payload.get("model", "mock-model")

        if "/api/generate" in self.path:
            # Ollama style response
            res = {
                "model": model,
                "created_at": "2026-08-15T00:00:00Z",
                "response": self.stub.message,
                "done": True,
            }
        else:
            # OpenAI / OpenRouter style response
            res = self.stub.generate(prompt=prompt, model=model)

        self._set_headers(200)
        self.wfile.write(json.dumps(res).encode("utf-8"))

    def log_message(self, format: str, *args: Any) -> None:
        pass  # Quiet logging


def run(port: int = 11435) -> None:
    server_address = ("127.0.0.1", port)
    httpd = HTTPServer(server_address, MockHTTPHandler)
    print(f"Mock LLM Server listening on http://127.0.0.1:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Mock LLM Server.")
        httpd.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mock LLM HTTP API Server")
    parser.add_argument("--port", type=int, default=11435, help="Port to listen on (default: 11435)")
    args = parser.parse_args()
    run(args.port)
