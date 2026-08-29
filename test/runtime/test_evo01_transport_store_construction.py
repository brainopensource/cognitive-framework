"""EVO-01: transport layers construct stores through the shared fail-closed
state-directory contract, never independently.

Owning contract: VANGUARD_090_BACKEND_AUDIT_AND_EVOLUTION_PLAN.md EVO-01.

`ApplicationService`/`RuntimeBootstrap` already give the CLI a fail-closed
guarantee: a durable configuration never silently drops into ephemeral
behavior, and an unwritable target refuses to start rather than succeeding
on a bare `mkdir`. The daemon (`service/server.py`) and the studio gateway
(`service/studio_gateway.py`) used to bypass that contract entirely --
`db_path.parent.mkdir(parents=True, exist_ok=True)` with no writability
check, no `blobs/` provisioning guarantee, no typed failure. This proves
both now go through `state_contract.ensure_state_directory` instead.
"""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from vanguard.packages.runtime.state_contract import StateDirectoryUnwritableError
from vanguard.packages.runtime.service.studio_gateway import create_gateway


class StudioGatewayUsesTheSharedStateContract(unittest.TestCase):
    def test_default_db_path_provisions_blobs_like_every_other_transport(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            workspace = Path(d)
            gateway = create_gateway(workspace_root=workspace, port=0)
            try:
                state_dir = workspace / ".vanguard"
                self.assertTrue(state_dir.is_dir())
                self.assertTrue((state_dir / "blobs").is_dir(),
                                "the gateway must provision blobs/ exactly as RuntimeBootstrap does")
            finally:
                gateway.service.shutdown() if hasattr(gateway.service, "shutdown") else None

    def test_an_unwritable_target_refuses_to_start_rather_than_silently_succeeding(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            readonly_parent = Path(d) / "readonly"
            readonly_parent.mkdir()
            os.chmod(readonly_parent, 0o500)  # r-x: cannot create a child directory in it
            try:
                target_db = readonly_parent / "nested" / "runtime.db"
                with self.assertRaises(StateDirectoryUnwritableError):
                    create_gateway(db_path=target_db, port=0)
            finally:
                os.chmod(readonly_parent, 0o700)  # restore so tempdir cleanup can remove it


class DaemonMainUsesTheSharedStateContract(unittest.TestCase):
    def test_server_module_imports_ensure_state_directory(self) -> None:
        """`server.py:main()` isn't easily unit-tested directly (it blocks
        serving forever), so this proves the wiring is in place rather than
        exercising the CLI end-to-end: the fail-closed helper is actually
        imported and used, not merely available."""
        import inspect

        from vanguard.packages.runtime.service import server

        source = inspect.getsource(server.main)
        self.assertIn("ensure_state_directory", source)
        self.assertNotIn("db_path.parent.mkdir", source,
                         "the bare mkdir that bypassed the writability contract must be gone")


if __name__ == "__main__":
    unittest.main()
