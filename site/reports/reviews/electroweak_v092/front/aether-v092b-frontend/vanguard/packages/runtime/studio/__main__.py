"""Main CLI entrypoint for running the Vanguard Meta-Harness Studio."""

from __future__ import annotations

import sys
from .server import run_studio_server

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_studio_server(port)
