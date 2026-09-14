"""T-78: exact unique replacement is transaction-backed and fail-closed."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from vanguard.packages.adapters.environment.git import GitEnvironment
from vanguard.packages.ports.environment import EffectRequest


class TestStrReplaceExact(unittest.TestCase):
    def _environment(self, root: Path) -> GitEnvironment:
        return GitEnvironment(repo_path=root)

    def test_unique_preimage_replaces_only_the_observed_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "module.py"
            path.write_text("answer = 40 + 2\n", encoding="utf-8")
            result = self._environment(root).apply(EffectRequest(
                verb="patch.apply", action="str_replace",
                args={"path": "module.py", "old": "40 + 2", "new": "42"},
            ))
            self.assertTrue(result.ok, result.error and result.error.message)
            self.assertEqual(path.read_text(encoding="utf-8"), "answer = 42\n")

    def test_absent_or_nonunique_preimage_has_typed_refusal_and_no_write(self) -> None:
        for old in ("missing", "token"):
            with self.subTest(old=old), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                path = root / "module.py"
                before = "token = 1\ntoken = 2\n"
                path.write_text(before, encoding="utf-8")
                result = self._environment(root).apply(EffectRequest(
                    verb="patch.apply", action="str_replace",
                    args={"path": "module.py", "old": old, "new": "changed"},
                ))
                self.assertFalse(result.ok)
                self.assertEqual(result.error.kind if result.error else None, "PATCH_PREIMAGE_MISMATCH")
                self.assertEqual(path.read_text(encoding="utf-8"), before)

    def test_syntax_failure_leaves_all_owned_preimages_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "module.py"
            before = "def working():\n    return 1\n"
            path.write_text(before, encoding="utf-8")
            result = self._environment(root).apply(EffectRequest(
                verb="patch.apply", action="str_replace",
                args={"path": "module.py", "old": "return 1", "new": "return ("},
            ))
            self.assertFalse(result.ok)
            self.assertIn("SyntaxError", result.error.message if result.error else "")
            self.assertEqual(path.read_bytes(), before.encode("utf-8"))

    def test_all_code_presets_declare_the_shared_exact_edit_surface(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        tool = json.loads((repo_root / "vanguard/packages/agency/manifests/vg-code-default/patch-tool.json").read_text())
        self.assertIn("old", tool["schema"]["properties"])
        self.assertIn("new", tool["schema"]["properties"])
        for preset in ("vg-code-default", "vg-code-fast", "vg-code-balanced", "vg-code-max"):
            manifest = json.loads((repo_root / f"vanguard/packages/agency/manifests/{preset}/manifest.json").read_text())
            self.assertIn("vg-code-default/patch-tool.json", manifest["components"]["tools"])


if __name__ == "__main__":
    unittest.main()
