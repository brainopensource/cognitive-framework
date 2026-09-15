"""Behavioral contract tests for the local-only autofix model cascade."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch


ROOT = Path(__file__).resolve().parents[2]
HARNESS_PATH = ROOT / ".agents/proficiencies/autofix-swe-loop/scripts/autofix_harness.py"


def load_harness():
    spec = importlib.util.spec_from_file_location("autofix_harness_under_test", HARNESS_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class TestAutofixModelCascade(unittest.TestCase):
    def setUp(self) -> None:
        self.harness = load_harness()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.target = Path(self.temp_dir.name) / "subject.py"
        self.target.write_text("original = True\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_uses_each_local_tier_after_a_failed_turn(self) -> None:
        diagnostics = iter(
            [
                {"status": "FAIL", "failure_summary": "baseline", "failures": []},
                {"status": "FAIL", "failure_summary": "first candidate", "failures": []},
                {"status": "PASS", "failure_summary": "", "failures": []},
            ]
        )
        generated = iter(
            [
                {"generated_code": "first = True\n", "completion_tokens": 3},
                {"generated_code": "second = True\n", "completion_tokens": 5},
            ]
        )
        servers = [Mock(), Mock()]

        with patch.object(self.harness, "run_falsifier", side_effect=lambda **_: next(diagnostics)), patch.object(
            self.harness, "generate_patch", side_effect=lambda **_: next(generated)
        ) as generate_patch, patch.object(
            self.harness, "ensure_server", side_effect=servers
        ) as ensure_server, patch.object(self.harness, "run_lda_delta", return_value=0.0):
            result = self.harness.execute_autofix_loop(
                task="repair",
                target_file=str(self.target),
                max_turns=2,
                model_cascade=[
                    {"provider": "local", "model_path": "/models/small.gguf", "port": 9100},
                    {"provider": "local", "model_path": "/models/large.gguf", "port": 9101},
                ],
            )

        self.assertEqual("RESOLVED", result["status"])
        self.assertEqual(8, result["total_tokens"])
        self.assertEqual(["/models/small.gguf", "/models/large.gguf"], [
            call.kwargs["model_path"] for call in generate_patch.call_args_list
        ])
        self.assertEqual([9100, 9101], [call.kwargs["port"] for call in generate_patch.call_args_list])
        self.assertEqual(2, ensure_server.call_count)
        self.assertEqual("local", result["history"][0]["model"]["provider"])
        self.assertEqual("/models/large.gguf", result["history"][1]["model"]["model_path"])
        for server in servers:
            server.kill.assert_called_once_with()
            server.wait.assert_called_once_with(timeout=2.0)

    def test_final_tier_remains_active_for_later_retries(self) -> None:
        diagnostics = iter(
            [
                {"status": "FAIL", "failure_summary": "baseline", "failures": []},
                {"status": "FAIL", "failure_summary": "first candidate", "failures": []},
                {"status": "FAIL", "failure_summary": "second candidate", "failures": []},
                {"status": "PASS", "failure_summary": "", "failures": []},
            ]
        )
        generated = iter(
            [
                {"generated_code": "first = True\n", "completion_tokens": 1},
                {"generated_code": "second = True\n", "completion_tokens": 1},
                {"generated_code": "third = True\n", "completion_tokens": 1},
            ]
        )
        with patch.object(self.harness, "run_falsifier", side_effect=lambda **_: next(diagnostics)), patch.object(
            self.harness, "generate_patch", side_effect=lambda **_: next(generated)
        ) as generate_patch, patch.object(self.harness, "ensure_server", return_value=Mock()), patch.object(
            self.harness, "run_lda_delta", return_value=0.0
        ):
            result = self.harness.execute_autofix_loop(
                task="repair",
                target_file=str(self.target),
                max_turns=3,
                model_path="/models/legacy-primary.gguf",
                model_cascade=[
                    {"provider": "local", "model_path": "/models/small.gguf", "port": 9100},
                    {"provider": "local", "model_path": "/models/large.gguf", "port": 9101},
                ],
            )

        self.assertEqual("RESOLVED", result["status"])
        self.assertEqual(["/models/small.gguf", "/models/large.gguf", "/models/large.gguf"], [
            call.kwargs["model_path"] for call in generate_patch.call_args_list
        ])

    def test_rejects_remote_cascade_before_dispatch(self) -> None:
        with patch.object(self.harness, "run_falsifier") as falsifier, patch.object(
            self.harness, "ensure_server"
        ) as ensure_server, patch.object(self.harness, "generate_patch") as generate_patch:
            result = self.harness.execute_autofix_loop(
                task="repair",
                target_file=str(self.target),
                model_cascade=[{"provider": "openrouter", "model": "remote/model"}],
            )

        self.assertEqual("CONFIGURATION_ERROR", result["status"])
        self.assertIn("local", result["message"])
        falsifier.assert_not_called()
        ensure_server.assert_not_called()
        generate_patch.assert_not_called()
        self.assertEqual("original = True\n", self.target.read_text(encoding="utf-8"))

    def test_rejects_ambiguous_shared_server_port_before_dispatch(self) -> None:
        with patch.object(self.harness, "run_falsifier") as falsifier, patch.object(
            self.harness, "ensure_server"
        ) as ensure_server:
            result = self.harness.execute_autofix_loop(
                task="repair",
                target_file=str(self.target),
                model_cascade=[
                    {"provider": "local", "model_path": "/models/small.gguf", "port": 9100},
                    {"provider": "local", "model_path": "/models/large.gguf", "port": 9100},
                ],
            )

        self.assertEqual("CONFIGURATION_ERROR", result["status"])
        self.assertIn("share a cascade port", result["message"])
        falsifier.assert_not_called()
        ensure_server.assert_not_called()

    def test_passing_baseline_never_starts_a_model_server(self) -> None:
        baseline = {"status": "PASS", "test_command": "python3 -m unittest", "failures": []}
        with patch.object(self.harness, "run_falsifier", return_value=baseline), patch.object(
            self.harness, "ensure_server"
        ) as ensure_server, patch.object(self.harness, "generate_patch") as generate_patch:
            result = self.harness.execute_autofix_loop(
                task="repair",
                target_file=str(self.target),
                model_cascade=[{"provider": "local", "model_path": "/models/small.gguf", "port": 9100}],
            )

        self.assertEqual("ALREADY_PASSING", result["status"])
        ensure_server.assert_not_called()
        generate_patch.assert_not_called()

    def test_failed_tiers_restore_the_original_file(self) -> None:
        diagnostics = iter(
            [
                {"status": "FAIL", "failure_summary": "baseline", "failures": []},
                {"status": "FAIL", "failure_summary": "still broken", "failures": []},
                {"status": "FAIL", "failure_summary": "still broken", "failures": []},
            ]
        )
        with patch.object(self.harness, "run_falsifier", side_effect=lambda **_: next(diagnostics)), patch.object(
            self.harness, "generate_patch", return_value={"generated_code": "broken = True\n", "completion_tokens": 1}
        ), patch.object(self.harness, "ensure_server", return_value=Mock()), patch.object(
            self.harness, "run_lda_delta", return_value=0.0
        ):
            result = self.harness.execute_autofix_loop(
                task="repair",
                target_file=str(self.target),
                max_turns=2,
                model_cascade=[
                    {"provider": "local", "model_path": "/models/small.gguf", "port": 9100},
                    {"provider": "local", "model_path": "/models/large.gguf", "port": 9101},
                ],
            )

        self.assertEqual("FAILED_ROLLED_BACK", result["status"])
        self.assertEqual("original = True\n", self.target.read_text(encoding="utf-8"))

    def test_cli_cascade_requires_an_explicit_local_fallback(self) -> None:
        fake_result = {
            "status": "RESOLVED",
            "target_file": str(self.target),
            "total_turns": 1,
            "total_tokens": 0,
            "total_duration_seconds": 0.0,
        }
        with patch.object(self.harness, "execute_autofix_loop", return_value=fake_result) as execute, patch.object(
            sys, "argv", [
                "autofix_harness.py",
                "--task", "repair",
                "--target-file", str(self.target),
                "--model-path", "/models/small.gguf",
                "--cascade",
                "--fallback-model-path", "/models/large.gguf",
                "--fallback-port", "9101",
                "--json",
            ]
        ), self.assertRaises(SystemExit) as exited:
            self.harness.main()

        self.assertEqual(0, exited.exception.code)
        self.assertEqual(
            [
                {"provider": "local", "model_path": "/models/small.gguf", "port": 8080},
                {"provider": "local", "model_path": "/models/large.gguf", "port": 9101},
            ],
            execute.call_args.kwargs["model_cascade"],
        )

    def test_cli_refuses_an_implicit_fallback_model(self) -> None:
        with patch.object(self.harness, "execute_autofix_loop") as execute, patch.object(
            sys, "argv", [
                "autofix_harness.py",
                "--task", "repair",
                "--target-file", str(self.target),
                "--cascade",
            ]
        ), self.assertRaises(SystemExit) as exited:
            self.harness.main()

        self.assertEqual(2, exited.exception.code)
        execute.assert_not_called()
