"""Unit tests for ManifestLoader and AliasTranslator (Task A.1 & Task A.3)."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from vanguard.packages.agency.manifests.loader import (
    AliasTranslator,
    ManifestLoader,
    ManifestLoadError,
)

MANIFESTS_DIR = Path(__file__).resolve().parents[2] / "vanguard" / "packages" / "agency" / "manifests"


class TestAliasTranslator(unittest.TestCase):
    def test_flat_dict_alias_translator(self) -> None:
        flat = {
            "Read": "fs.read",
            "Edit": "patch.apply",
            "Bash": "proc.exec",
        }
        translator = AliasTranslator.from_dict(flat)
        self.assertEqual(translator.to_canonical("Read"), "fs.read")
        self.assertEqual(translator.to_canonical("Edit"), "patch.apply")
        self.assertEqual(translator.to_canonical("Bash"), "proc.exec")
        self.assertEqual(translator.to_canonical("UnknownTool"), "UnknownTool")

        self.assertEqual(translator.to_wire("fs.read"), "Read")
        self.assertEqual(translator.to_wire("patch.apply"), "Edit")
        self.assertEqual(translator.to_wire("proc.exec"), "Bash")
        self.assertEqual(translator.to_wire("fs.search"), "fs.search")

    def test_nested_alias_translator(self) -> None:
        nested = {
            "to_canonical": {"read_file": "fs.read", "edit_file": "patch.apply"},
            "to_wire": {"fs.read": "read_file", "patch.apply": "edit_file"},
        }
        translator = AliasTranslator.from_dict(nested)
        self.assertEqual(translator.to_canonical("read_file"), "fs.read")
        self.assertEqual(translator.to_wire("fs.read"), "read_file")


class TestManifestLoader(unittest.TestCase):
    def setUp(self) -> None:
        self.loader = ManifestLoader(MANIFESTS_DIR)

    def test_list_available_packs(self) -> None:
        packs = self.loader.list_available_packs()
        self.assertIn("vg-shell-only", packs)
        self.assertIn("vg-code-default", packs)
        self.assertIn("vg-code-claude-shaped", packs)
        self.assertIn("vg-code-opencode-shaped", packs)
        self.assertIn("vg-code-swe-mini", packs)

    def test_load_vg_code_default(self) -> None:
        pack = self.loader.load_pack("vg-code-default")
        self.assertEqual(pack.name, "vg-code-default")
        self.assertEqual(len(pack.manifest.capabilities), 4)

    def test_load_vg_code_claude_shaped(self) -> None:
        pack = self.loader.load_pack("vg-code-claude-shaped")
        self.assertEqual(pack.name, "vg-code-claude-shaped")
        self.assertEqual(pack.to_canonical("Read"), "fs.read")
        self.assertEqual(pack.to_canonical("Edit"), "patch.apply")
        self.assertEqual(pack.to_canonical("Bash"), "proc.exec")
        self.assertEqual(pack.to_wire("fs.read"), "Read")

    def test_load_vg_code_opencode_shaped(self) -> None:
        pack = self.loader.load_pack("vg-code-opencode-shaped")
        self.assertEqual(pack.name, "vg-code-opencode-shaped")
        self.assertEqual(pack.to_canonical("view_file"), "fs.read")
        self.assertEqual(pack.to_canonical("edit_file"), "patch.apply")
        self.assertEqual(pack.to_canonical("run_command"), "proc.exec")
        self.assertEqual(pack.to_wire("fs.read"), "view_file")

    def test_load_vg_code_swe_mini(self) -> None:
        pack = self.loader.load_pack("vg-code-swe-mini")
        self.assertEqual(pack.name, "vg-code-swe-mini")
        self.assertEqual(pack.to_canonical("read_file"), "fs.read")
        self.assertEqual(pack.to_canonical("edit_file"), "patch.apply")
        self.assertEqual(pack.to_canonical("bash"), "proc.exec")
        self.assertEqual(pack.to_wire("fs.read"), "read_file")

    def test_load_vg_shell_only(self) -> None:
        pack = self.loader.load_pack("vg-shell-only")
        self.assertEqual(pack.name, "vg-shell-only")
        self.assertEqual(pack.to_canonical("shell"), "proc.exec")
        self.assertEqual(pack.to_canonical("bash"), "proc.exec")
        self.assertEqual(pack.to_canonical("run_command"), "proc.exec")
        self.assertEqual(pack.to_wire("proc.exec"), "shell")

    def test_missing_pack_raises_error(self) -> None:
        with self.assertRaises(ManifestLoadError):
            self.loader.load_pack("nonexistent-pack")

    def test_invalid_json_raises_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            bad_dir = Path(tmpdir) / "bad-pack"
            bad_dir.mkdir()
            (bad_dir / "manifest.json").write_text("invalid json")
            with self.assertRaises(ManifestLoadError):
                self.loader.load_pack(bad_dir)


if __name__ == "__main__":
    unittest.main()
