from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from vanguard.packages.adapters.models.fake import FakeModel
from vanguard.packages.runtime.compose import TaskContext
from vanguard.packages.runtime.root import Runtime


class TestNativeAgentCatalog(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.workspace = Path(self.tmp.name)
        (self.workspace / "test.py").write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _manifest_dir(self, name: str) -> Path:
        base = Path(__file__).resolve().parents[2] / "vanguard" / "packages" / "agency" / "manifests"
        return base / name / "manifest.json"

    def test_code_lex_minimal_composes_and_runs(self) -> None:
        manifest_p = self._manifest_dir("vg-code-lex")
        self.assertTrue(manifest_p.exists(), f"missing manifest: {manifest_p}")

        harness = Runtime.compose(manifest_p)
        self.assertEqual(harness.harness, "vg-code-lex")
        # Check minimal tool capabilities
        self.assertIn("fs.read", harness.verbs)
        self.assertIn("fs.search", harness.verbs)
        self.assertIn("patch.apply", harness.verbs)
        self.assertIn("proc.exec", harness.verbs)

        task = TaskContext(
            brief="Fix addition bug in test.py",
            repo_path=self.workspace,
            run_id="run-lex-1",
            episode_id="ep-lex-1",
        )
        fake_model = FakeModel([{"kind": "finish", "note": "lex minimal finished"}])
        result = Runtime.execute_profiled(
            manifest_p,
            task,
            profile_id="ci",
            model=fake_model,
        )
        self.assertEqual(
            str(getattr(result.terminal, "value", result.terminal)),
            "instrument_error",
        )
        self.assertTrue(
            any(
                event.kind == "EpisodeStateChanged"
                for event in result.events
            ),
            "a rejected mutation-free finish must enter recovery before exhaustion",
        )

    def test_code_explain_read_only_agent(self) -> None:
        manifest_p = self._manifest_dir("vg-code-explain")
        self.assertTrue(manifest_p.exists(), f"missing manifest: {manifest_p}")

        harness = Runtime.compose(manifest_p)
        self.assertEqual(harness.harness, "vg-code-explain")
        # Verify read capabilities present, write capabilities strictly absent
        self.assertIn("fs.read", harness.verbs)
        self.assertIn("fs.search", harness.verbs)
        self.assertNotIn("fs.patch", harness.verbs)
        self.assertNotIn("patch.apply", harness.verbs)
        self.assertNotIn("fs.write", harness.verbs)
        self.assertNotIn("proc.exec", harness.verbs)

        task = TaskContext(
            brief="Explain the architecture of test.py",
            repo_path=self.workspace,
            run_id="run-explain-1",
            episode_id="ep-explain-1",
        )
        fake_model = FakeModel([{"kind": "finish", "note": "codebase explained"}])
        result = Runtime.execute_profiled(
            manifest_p,
            task,
            profile_id="ci",
            model=fake_model,
        )
        self.assertEqual(str(getattr(result.terminal, "value", result.terminal)), "completed")

    def test_all_shipped_manifests_compose(self) -> None:
        manifests = [
            "vg-code-default",
            "vg-code-lex",
            "vg-code-explain",
            "vg-table-default",
            "vg-shell-only",
            "vg-code-swe-mini",
            "vg-code-claude-shaped",
            "vg-code-opencode-shaped",
        ]
        for name in manifests:
            with self.subTest(manifest=name):
                p = self._manifest_dir(name)
                harness = Runtime.compose(p)
                self.assertIsNotNone(harness.composition_digest)
                self.assertTrue(len(harness.verbs) > 0)
