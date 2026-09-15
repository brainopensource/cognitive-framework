"""T-78: exact unique replacement is transaction-backed and fail-closed."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from vanguard.packages.adapters.environment.fake import FakeEnvironment
from vanguard.packages.adapters.environment.git import GitEnvironment
from vanguard.packages.adapters.environment.transaction import TXN_TMP_MARKER
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

    # --- T-78 acceptance: the primitive is routed through the *multi-file*
    # transaction manager, so the five-file set is the subject of the proof.
    # A single-file exercise cannot falsify all-or-nothing behaviour.

    _FIXTURE = ("file_one.py", "file_two.py", "file_three.py", "file_four.py", "file_five.py")

    def _five_file_workspace(self, root: Path) -> dict[str, bytes]:
        preimages: dict[str, bytes] = {}
        for index, name in enumerate(self._FIXTURE, start=1):
            body = f"VALUE_{index} = {index}\n"
            (root / name).write_text(body, encoding="utf-8")
            preimages[name] = body.encode("utf-8")
        return preimages

    def _batch(self, root: Path, edits: list[dict[str, str]]):
        return self._environment(root).apply(EffectRequest(
            verb="patch.apply", action="str_replace", args={"edits": edits},
        ))

    def test_five_file_batch_commits_every_edit_in_one_transaction(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._five_file_workspace(root)
            result = self._batch(root, [
                {"path": name, "old": f"= {index}", "new": f"= {index * 10}"}
                for index, name in enumerate(self._FIXTURE, start=1)
            ])
            self.assertTrue(result.ok, result.error and result.error.message)
            self.assertEqual(
                tuple(item.resource for item in result.value.affected_resources),
                self._FIXTURE,
            )
            for index, name in enumerate(self._FIXTURE, start=1):
                self.assertEqual(
                    (root / name).read_text(encoding="utf-8"),
                    f"VALUE_{index} = {index * 10}\n",
                )

    def test_syntax_failure_in_file_four_preserves_all_five_preimages(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            preimages = self._five_file_workspace(root)
            edits = [
                {"path": name, "old": f"= {index}", "new": f"= {index * 10}"}
                for index, name in enumerate(self._FIXTURE, start=1)
            ]
            edits[3] = {"path": "file_four.py", "old": "VALUE_4 = 4", "new": "VALUE_4 = ("}
            result = self._batch(root, edits)
            self.assertFalse(result.ok)
            self.assertIn("SyntaxError", result.error.message if result.error else "")
            for name, before in preimages.items():
                self.assertEqual((root / name).read_bytes(), before, name)

    def test_absent_or_nonunique_preimage_in_a_batch_writes_nothing(self) -> None:
        cases = {
            "absent": {"path": "file_four.py", "old": "NOT_PRESENT", "new": "x = 1"},
            "duplicate": {"path": "file_four.py", "old": "dup", "new": "x = 1"},
        }
        for label, failing in cases.items():
            with self.subTest(case=label), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                preimages = self._five_file_workspace(root)
                if label == "duplicate":
                    body = "dup = 1\ndup = 2\n"
                    (root / "file_four.py").write_text(body, encoding="utf-8")
                    preimages["file_four.py"] = body.encode("utf-8")
                edits = [
                    {"path": name, "old": f"= {index}", "new": f"= {index * 10}"}
                    for index, name in enumerate(self._FIXTURE, start=1)
                    if name != "file_four.py"
                ]
                edits.insert(3, failing)
                result = self._batch(root, edits)
                self.assertFalse(result.ok)
                self.assertEqual(
                    result.error.kind if result.error else None, "PATCH_PREIMAGE_MISMATCH")
                for name, before in preimages.items():
                    self.assertEqual((root / name).read_bytes(), before, name)

    def test_no_temporary_staging_file_survives_a_refused_batch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._five_file_workspace(root)
            self._batch(root, [
                {"path": "file_one.py", "old": "= 1", "new": "= 10"},
                {"path": "file_four.py", "old": "VALUE_4 = 4", "new": "VALUE_4 = ("},
            ])
            leftovers = [
                item.name for item in root.rglob("*")
                if item.is_file() and TXN_TMP_MARKER in item.name
            ]
            self.assertEqual(leftovers, [])

    def test_fake_matches_git_batch_atomicity_and_python_preflight(self) -> None:
        """Hermetic episodes cannot accept an edit production would refuse."""
        initial = {
            name: f"VALUE_{index} = {index}\n"
            for index, name in enumerate(self._FIXTURE, start=1)
        }
        fake = FakeEnvironment(initial)
        result = fake.apply(EffectRequest(
            verb="patch.apply", action="str_replace", args={"edits": [
                {"path": name, "old": f"= {index}", "new": f"= {index * 10}"}
                for index, name in enumerate(self._FIXTURE, start=1)
            ][0:3] + [{
                "path": "file_four.py", "old": "VALUE_4 = 4", "new": "VALUE_4 = (",
            }] + [{"path": "file_five.py", "old": "= 5", "new": "= 50"}]},
        ))
        self.assertFalse(result.ok)
        self.assertIn("SyntaxError", result.error.message if result.error else "")
        self.assertEqual(fake._files, initial)

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
