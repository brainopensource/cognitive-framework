"""S6B-GOV-001: path registry, foreign-cwd resolution, stale-path rejection."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_TOOLS = str(ROOT / "tools")
if _TOOLS not in sys.path:
    sys.path.insert(0, _TOOLS)

import repo_paths  # noqa: E402


class RepoPathsTests(unittest.TestCase):
    def test_repo_root_from_this_file(self) -> None:
        root = repo_paths.repo_root()
        self.assertTrue((root / "docs" / "main_v4").is_dir())
        self.assertFalse((root / "docs" / "v4").exists())
        self.assertEqual(repo_paths.active_mvp_contract(), root / "docs/agile/sprint0/active-mvp-contract.json")

    def test_rewrite_legacy_paths(self) -> None:
        self.assertEqual(repo_paths.rewrite_legacy_doc_path("docs/v4/00_vanguard_registry_v040.md"), "docs/main_v4/00_vanguard_registry_v040.md")
        self.assertEqual(repo_paths.rewrite_legacy_doc_path("docs/sprint0/active-mvp-contract.json"), "docs/agile/sprint0/active-mvp-contract.json")
        self.assertEqual(repo_paths.rewrite_legacy_doc_path("docs/review/todo/phases_review.md"), "docs/reviews/todo/phases_review.md")
        self.assertEqual(repo_paths.rewrite_legacy_doc_path("docs/development/cli_tui_architecture.md"), "docs/development_guides/cli_tui_architecture.md")
        self.assertEqual(repo_paths.rewrite_legacy_doc_path("docs/development_guides/cli_tui_architecture.md"), "docs/development_guides/cli_tui_architecture.md")
        self.assertEqual(repo_paths.rewrite_legacy_doc_path("docs/agile/sprint0/README.md"), "docs/agile/sprint0/README.md")

    def test_stale_tokens_ignore_live_layout(self) -> None:
        live = "See docs/main_v4/00.md and docs/agile/sprint0/x.json and docs/reviews/todo/a.md and docs/development_guides/x.md"
        self.assertEqual(repo_paths.stale_path_matches(live), [])
        stale = "hard-coded docs/v4/00.md and docs/sprint0/contract.json"
        matches = repo_paths.stale_path_matches(stale)
        self.assertTrue(any("docs/v4" in m for m in matches))
        self.assertTrue(any("docs/sprint0" in m for m in matches))


class ForeignCwdGovernanceTests(unittest.TestCase):
    def _run(self, script: str, cwd: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(ROOT / "tools" / script)],
            cwd=cwd,
            text=True,
            capture_output=True,
            check=False,
            env={**os.environ, "PYTHONPATH": str(ROOT / "tools")},
        )

    def test_audit_and_governance_from_foreign_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            foreign = Path(tmp)
            for script in (
                "audit_v4.py",
                "check_sprint0_governance.py",
                "check_stale_paths.py",
            ):
                result = self._run(script, foreign)
                self.assertEqual(
                    result.returncode,
                    0,
                    msg=f"{script} from {foreign} failed:\n{result.stdout}\n{result.stderr}",
                )

    def test_stale_path_fixture_fails(self) -> None:
        fixture = ROOT / "test/broken/fixtures/stale_paths"
        self.assertTrue(fixture.is_dir())
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "check_stale_paths.py"), "--root", str(fixture)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        combined = result.stdout + result.stderr
        self.assertIn("STALE PATH", combined)
        self.assertIn("docs/v4", combined)


if __name__ == "__main__":
    unittest.main()
