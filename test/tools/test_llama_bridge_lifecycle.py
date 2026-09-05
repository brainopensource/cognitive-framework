"""Tests for llama.cpp bridge fail-closed lifecycle (T-87 / BRG-01)."""

from __future__ import annotations

import inspect
import json
import os
import pathlib
import signal
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from tools.llama_cpp import cli


class TestLlamaBridgeLifecycle(unittest.TestCase):
    def test_serve_uses_typed_flash_attention_flag(self) -> None:
        source = inspect.getsource(cli.serve_command)
        self.assertIn('cmd.extend(["--flash-attn", args.flash_attn])', source)
        self.assertNotIn('cmd.append("-fa")', source)

    def test_stop_issues_no_pkill_or_pgrep(self) -> None:
        """Stop must never invoke pkill or pgrep -f."""
        cli_source = inspect.getsource(cli)
        self.assertNotIn("pkill", cli_source)
        self.assertNotIn("pgrep", cli_source)

    def test_stale_pid_file_yields_typed_pid_stale(self) -> None:
        """A stale PID file yields typed PID_STALE."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pid_file = pathlib.Path(tmpdir) / "test_server.pid"
            # Choose a PID that is almost certainly not running, e.g. 999999
            pid_file.write_text("999999\n")

            with self.assertRaises(cli.PidStaleError) as ctx:
                cli.stop_server(pid_file=pid_file)
            self.assertEqual(ctx.exception.code, "PID_STALE")
            # Proves stale PID file was cleared
            self.assertFalse(pid_file.exists())

    def test_adopting_occupied_port_without_matching_props_yields_typed_model_mismatch(self) -> None:
        """Adopting an occupied port without matching /props model and alias yields typed MODEL_MISMATCH."""
        mock_foreign_props = {
            "default_generation_settings": {
                "model": "foreign-unrelated-model.gguf"
            },
            "alias": "foreign-alias",
        }
        with patch("tools.llama_cpp.cli.check_server_health") as mock_health:
            mock_health.return_value = {
                "online": True,
                "props": mock_foreign_props,
                "health": {"status": "ok"},
            }

            with self.assertRaises(cli.ModelMismatchError) as ctx:
                cli.adopt_server(
                    "http://127.0.0.1:8080",
                    expected_model="target-model.gguf",
                    expected_alias="target-alias",
                )
            self.assertEqual(ctx.exception.code, "MODEL_MISMATCH")

    def test_failed_child_remains_failed_and_never_online_while_foreign_server_holds_port(self) -> None:
        """Keeps a failed child FAILED while a foreign server holds the port."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pid_file = pathlib.Path(tmpdir) / "test_server.pid"
            log_file = pathlib.Path(tmpdir) / "test_server.log"

            # Mock foreign server running on port
            mock_foreign_props = {
                "default_generation_settings": {"model": "foreign-model.gguf"},
                "alias": "foreign-alias",
            }

            # Simulate a child process that fails immediately.
            mock_proc = MagicMock()
            mock_proc.pid = 42424
            mock_proc.poll.return_value = 1  # Exited with error!

            with patch("subprocess.Popen", return_value=mock_proc), \
                 patch("tools.llama_cpp.cli.check_server_health") as mock_health:
                mock_health.return_value = {
                    "online": True,
                    "props": mock_foreign_props,
                    "health": {"status": "ok"},
                }

                result = cli.launch_server_process(
                    ["llama-server", "-m", "target.gguf", "--flash-attn", "on"],
                    host="127.0.0.1",
                    port=8080,
                    expected_model="target.gguf",
                    expected_alias="target-alias",
                    log_file=str(log_file),
                    pid_file=pid_file,
                    max_wait_seconds=1.0,
                )

                self.assertEqual(result["status"], "FAILED")
                self.assertFalse(result["online"])
                self.assertNotEqual(result["status"], "ONLINE")


if __name__ == "__main__":
    unittest.main()
