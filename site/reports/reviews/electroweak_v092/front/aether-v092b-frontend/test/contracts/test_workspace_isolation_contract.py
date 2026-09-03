"""Contract tests for workspace root enforcement and path isolation."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from vanguard.packages.domain.workspace import (
    DEFAULT_WORKSPACE_ROOT,
    ENV_WORKSPACE_ROOT,
    controlled_environment,
    get_workspace_path,
    get_workspace_root,
    validate_workspace_path,
)


class TestWorkspaceIsolationContract(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace_root = Path(self.temp_dir.name).resolve()
        self.env_patcher = patch.dict(
            os.environ,
            {
                ENV_WORKSPACE_ROOT: str(self.workspace_root),
                "TMPDIR": str(self.workspace_root / "tmp"),
                "TMP": str(self.workspace_root / "tmp"),
                "TEMP": str(self.workspace_root / "tmp"),
                "XDG_CACHE_HOME": str(self.workspace_root / "cache"),
                "XDG_STATE_HOME": str(self.workspace_root / "state"),
            },
        )
        self.env_patcher.start()

    def tearDown(self) -> None:
        self.env_patcher.stop()
        self.temp_dir.cleanup()

    def test_workspace_root_resolution_and_validation(self) -> None:
        root = get_workspace_root()
        self.assertTrue(root.is_dir())
        self.assertEqual(root, self.workspace_root)

    def test_missing_workspace_root_fails_closed(self) -> None:
        with patch.dict(os.environ, {}, clear=True), patch("vanguard.packages.domain.workspace._discover_workspace_root", return_value=None):
            with self.assertRaises(RuntimeError) as ctx:
                get_workspace_root()
            self.assertIn(f"{ENV_WORKSPACE_ROOT} is not set", str(ctx.exception))

    def test_category_paths_strictly_under_root(self) -> None:
        root = get_workspace_root()
        categories = ("tmp", "benchmarks", "evaluators", "sandboxes", "state", "cache", "logs")
        for cat in categories:
            cat_path = get_workspace_path(cat)
            self.assertTrue(cat_path.is_dir())
            self.assertTrue(cat_path.is_relative_to(root))
            self.assertEqual(cat_path, root / cat)

    def test_validate_path_accepts_valid_and_rejects_escapes(self) -> None:
        root = get_workspace_root()
        valid_bench = root / "benchmarks" / "run_01"
        self.assertEqual(validate_workspace_path(valid_bench), valid_bench.resolve())

        # Escapes must raise RuntimeError
        with self.assertRaises(RuntimeError) as ctx:
            validate_workspace_path(Path(tempfile.gettempdir()) / "escape_test")
        self.assertIn("escapes AETHER_WORKSPACE_ROOT", str(ctx.exception))

        with self.assertRaises(RuntimeError) as ctx:
            validate_workspace_path(Path("/etc/passwd").resolve() if os.name != "nt" else Path("C:\\Windows\\System32\\drivers\\etc\\hosts").resolve())
        self.assertIn("escapes AETHER_WORKSPACE_ROOT", str(ctx.exception))

    def test_controlled_environment_contains_overrides(self) -> None:
        root = get_workspace_root()
        env = controlled_environment({"PATH": "/usr/bin", "CUSTOM_VAR": "1"})
        self.assertEqual(env["AETHER_WORKSPACE_ROOT"], str(root))
        self.assertEqual(env["TMPDIR"], str(root / "tmp"))
        self.assertEqual(env["TMP"], str(root / "tmp"))
        self.assertEqual(env["TEMP"], str(root / "tmp"))
        self.assertEqual(env["XDG_CACHE_HOME"], str(root / "cache"))
        self.assertEqual(env["XDG_STATE_HOME"], str(root / "state"))
        self.assertEqual(env["PYTHONPYCACHEPREFIX"], str(root / "cache" / "python"))
        self.assertEqual(env["npm_config_cache"], str(root / "cache" / "npm"))
        self.assertEqual(env["PATH"], "/usr/bin")
        self.assertEqual(env["CUSTOM_VAR"], "1")


if __name__ == "__main__":
    unittest.main()
