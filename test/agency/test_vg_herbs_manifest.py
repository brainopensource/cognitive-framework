"""Unit and contract tests for vg-herbs manifest pack and runtime resolution."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from vanguard.packages.agency.manifests.loader import ManifestLoader
from vanguard.packages.agency.manifests.validator import validate_manifest_pack
from vanguard.packages.agency.forge.facade import ForgeConfig, ForgeFacade, HERBS_PRESET_NAME, GoalContract
from vanguard.packages.runtime.root import HERBS_PRESET_NAME as ROOT_HERBS_NAME


class TestVgHerbsManifest(unittest.TestCase):
    """Test vg-herbs manifest loading, schema compliance, and end-to-end mock episode execution."""

    def test_facade_constants_aligned(self) -> None:
        self.assertEqual(HERBS_PRESET_NAME, "vg-herbs")
        self.assertEqual(ROOT_HERBS_NAME, "vg-herbs")

    def test_load_manifest_pack(self) -> None:
        loader = ManifestLoader()
        pack = loader.load_pack("vg-herbs")

        self.assertEqual(pack.name, "vg-herbs")
        self.assertIsNotNone(pack.manifest)
        self.assertIn("system_prompt", pack.components_data)
        self.assertIn("tools", pack.components_data)

        # Validate capabilities
        verbs = {c.verb for c in pack.manifest.capabilities}
        self.assertEqual(
            verbs,
            {"fs.read", "fs.search", "patch.apply", "proc.exec", "web.distill"},
        )

        # Validate aliases
        self.assertEqual(pack.to_canonical("surgical_patch"), "patch.apply")
        self.assertEqual(pack.to_canonical("read"), "fs.read")
        self.assertEqual(pack.to_canonical("search"), "fs.search")
        self.assertEqual(pack.to_canonical("test"), "proc.exec")
        self.assertEqual(pack.to_canonical("web_distill"), "web.distill")

    def test_validate_manifest_pack_logical_rules(self) -> None:
        loader = ManifestLoader()
        pack = loader.load_pack("vg-herbs")
        # Should not raise ManifestValidationError
        validate_manifest_pack(pack)

    def test_hermetic_mock_episode_execution(self) -> None:
        class FakeModelPort:
            def __init__(self) -> None:
                self.turn = 0

            def propose(self, context: any, tools: any, sampling: any = None) -> dict:
                self.turn += 1
                if self.turn == 1:
                    return {
                        "message": {
                            "content": "Reading file to locate bug.",
                            "tool_calls": [
                                {
                                    "id": "call_1",
                                    "function": {
                                        "name": "view_file",
                                        "arguments": {"path": "src/math_util.py"},
                                    },
                                }
                            ],
                        },
                        "usage": {"prompt_tokens": 50, "completion_tokens": 20, "cost": 0.0},
                    }
                elif self.turn == 2:
                    return {
                        "message": {
                            "content": "Applying surgical patch.",
                            "tool_calls": [
                                {
                                    "id": "call_2",
                                    "function": {
                                        "name": "surgical_patch",
                                        "arguments": {
                                            "path": "src/math_util.py",
                                            "target": "return x - y",
                                            "replacement": "return x + y",
                                        },
                                    },
                                }
                            ],
                        },
                        "usage": {"prompt_tokens": 80, "completion_tokens": 25, "cost": 0.0},
                    }
                elif self.turn == 3:
                    return {
                        "message": {
                            "content": "Running test suite to verify resolution.",
                            "tool_calls": [
                                {
                                    "id": "call_3",
                                    "function": {
                                        "name": "run_command",
                                        "arguments": {"command": "python3 -m unittest test_math.py"},
                                    },
                                }
                            ],
                        },
                        "usage": {"prompt_tokens": 100, "completion_tokens": 20, "cost": 0.0},
                    }
                else:
                    return {
                        "message": {
                            "content": "Verified green.",
                            "tool_calls": [
                                {
                                    "id": "call_4",
                                    "function": {
                                        "name": "finish_task",
                                        "arguments": {"summary": "All tests green."},
                                    },
                                }
                            ],
                        },
                        "usage": {"prompt_tokens": 120, "completion_tokens": 15, "cost": 0.0},
                    }

        with tempfile.TemporaryDirectory() as tmp_dir:
            ws = Path(tmp_dir)
            (ws / "src").mkdir(parents=True, exist_ok=True)
            (ws / "src" / "math_util.py").write_text(
                "def add(x, y):\n    return x - y\n", encoding="utf-8"
            )

            def mock_command_runner(cmd: str, cwd: Path) -> tuple[int, str]:
                # Simulate green test execution after fix
                content = (cwd / "src" / "math_util.py").read_text(encoding="utf-8")
                if "return x + y" in content:
                    return 0, "Ran 1 test in 0.001s\n\nOK"
                return 1, "FAIL: test_add\nAssertionError: -1 != 3"

            cfg = ForgeConfig(
                max_turns=6,
                require_patch_for_write=True,
                preset_name=HERBS_PRESET_NAME,
            )
            model_port = FakeModelPort()

            engine = ForgeFacade.create_engine(
                workspace_root=ws,
                model_port=model_port,
                config=cfg,
                command_runner=mock_command_runner,
            )

            outcome = engine.run_episode("Fix addition bug in src/math_util.py")
            self.assertEqual(outcome.status, "COMPLETED")
            self.assertIn("src/math_util.py", outcome.changed_files)
            self.assertIsNotNone(outcome.verification_receipt)
            self.assertTrue(outcome.verification_receipt.passed)


if __name__ == "__main__":
    unittest.main()
