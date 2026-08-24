"""Lightweight HTTP server for AETHER / Vanguard Meta-Harness Studio.

Serves the visual frontend UI and provides local read-only status.
"""

from __future__ import annotations

import json
import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Any

UI_DIR = Path(__file__).resolve().parent / "ui"


class StudioRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(UI_DIR), **kwargs)

    def do_GET(self) -> None:
        if self.path == "/api/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            payload = {
                "system": "AETHER / Vanguard",
                "tcb_loc": 1366,
                "tcb_budget": 1438,
                "active_wave": "W-3D",
                "profiles": ["local", "sandboxed", "hermetic"]
            }
            self.wfile.write(json.dumps(payload).encode("utf-8"))
            return
        super().do_GET()


def run_studio_server(port: int = 8080) -> None:
    server_address = ("", port)
    httpd = HTTPServer(server_address, StudioRequestHandler)
    print(f"============================================================")
    print(f"  VANGUARD / AETHER — Meta-Harness Studio")
    print(f"  Visual Studio active at: http://localhost:{port}")
    print(f"============================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down studio server.")
        httpd.server_close()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_studio_server(port)
