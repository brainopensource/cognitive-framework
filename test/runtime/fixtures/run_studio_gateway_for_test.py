"""Test helper: start a real StudioGateway on an ephemeral port and print it.

Used by the TypeScript F6 live-wiring integration test
(vanguard/clients/studio/test/live-observatory.test.ts) to prove a real
HttpRuntimeClient + StudioFoldEngine can consume this gateway's live SSE
stream end-to-end, not just fixtures.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from vanguard.packages.runtime.service.studio_gateway import create_gateway


def main() -> None:
    tempdir = tempfile.TemporaryDirectory()
    workspace = Path(tempdir.name) / "workspace"
    workspace.mkdir(parents=True, exist_ok=True)
    server = create_gateway(host="127.0.0.1", port=0, workspace_root=workspace)
    print(f"PORT {server.server_port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    sys.exit(main() or 0)
