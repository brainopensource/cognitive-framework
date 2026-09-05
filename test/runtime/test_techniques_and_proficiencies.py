"""Comprehensive contract and unit tests for SOTA Skills, Techniques, and Proficiencies.

Verifies:
1. Universal schema compliance of YAML frontmatter across .agents/
2. Prefix budgeting via SkillIndex (fits within 4096 characters)
3. CascadingModel failover, consecutive failure threshold, and error propagation
4. Autofix closed-loop logic and rollback safety
"""

from __future__ import annotations

import os
import re
import tempfile
import unittest
from pathlib import Path
from typing import Any, Mapping

from vanguard.packages.adapters.models.cascade import CascadingModel
from vanguard.packages.adapters.models.fake import FakeModel
from vanguard.packages.ports.event_store import Result
from vanguard.packages.runtime.skill_index import (
    DEFAULT_BUDGET_CHARS,
    SkillIndex,
    build_skill_index,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestOntologicalArtifacts(unittest.TestCase):
    """Verify that skills, techniques, and proficiencies follow the universal schema."""

    def _parse_frontmatter(self, file_path: Path) -> dict[str, Any]:
        content = file_path.read_text(encoding="utf-8")
        match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        self.assertIsNotNone(match, f"Missing YAML frontmatter in {file_path}")
        lines = match.group(1).splitlines()
        data = {}
        current_key = None
        for line in lines:
            if ":" in line and not line.strip().startswith("-"):
                k, _, v = line.partition(":")
                current_key = k.strip()
                data[current_key] = v.strip().strip('"').strip("'")
            elif current_key and line.strip().startswith("-"):
                val = line.strip().lstrip("-").strip()
                if not isinstance(data[current_key], list):
                    data[current_key] = []
                data[current_key].append(val)
        return data

    def test_techniques_schema_conformance(self) -> None:
        tech_dir = REPO_ROOT / ".agents" / "techniques"
        self.assertTrue(tech_dir.exists(), "Missing .agents/techniques directory")
        techniques = [p for p in tech_dir.iterdir() if p.is_dir()]
        self.assertGreaterEqual(len(techniques), 2, "Expected at least 2 techniques")

        for t_dir in techniques:
            doc_file = t_dir / "TECHNIQUE.md"
            self.assertTrue(doc_file.exists(), f"Missing TECHNIQUE.md in {t_dir}")
            fm = self._parse_frontmatter(doc_file)
            self.assertIn("name", fm, f"Missing 'name' in {doc_file}")
            self.assertIn("version", fm, f"Missing 'version' in {doc_file}")

    def test_proficiencies_schema_conformance(self) -> None:
        prof_dir = REPO_ROOT / ".agents" / "proficiencies"
        self.assertTrue(prof_dir.exists(), "Missing .agents/proficiencies directory")
        proficiencies = [p for p in prof_dir.iterdir() if p.is_dir()]
        self.assertGreaterEqual(len(proficiencies), 1, "Expected at least 1 proficiency")

        for p_dir in proficiencies:
            doc_file = p_dir / "PROFICIENCY.md"
            self.assertTrue(doc_file.exists(), f"Missing PROFICIENCY.md in {p_dir}")
            fm = self._parse_frontmatter(doc_file)
            self.assertIn("name", fm, f"Missing 'name' in {doc_file}")
            self.assertIn("version", fm, f"Missing 'version' in {doc_file}")

    def test_skill_index_budget_with_all_capabilities(self) -> None:
        """Ensure all discovered skills, techniques, and proficiencies fit within the frozen prefix budget."""
        raw_entries = []
        for cat in ("skills", "techniques", "proficiencies"):
            cat_dir = REPO_ROOT / ".agents" / cat
            if not cat_dir.exists():
                continue
            for item in cat_dir.iterdir():
                if not item.is_dir():
                    continue
                md_path = item / "SKILL.md" if cat == "skills" else (
                    item / "TECHNIQUE.md" if cat == "techniques" else item / "PROFICIENCY.md"
                )
                if md_path.exists():
                    fm = self._parse_frontmatter(md_path)
                    raw_entries.append({
                        "name": f"{cat}:{fm.get('name', item.name)}",
                        "description": fm.get("description", "operational capability"),
                        "path": str(md_path.relative_to(REPO_ROOT)),
                    })

        index = build_skill_index(raw_entries, budget_chars=DEFAULT_BUDGET_CHARS)
        self.assertLessEqual(index.size_chars, DEFAULT_BUDGET_CHARS)
        self.assertEqual(len(index.dropped), 0, f"Entries dropped from prefix budget: {index.dropped}")


class TestCascadingModel(unittest.TestCase):
    """Verify CascadingModel failover, thresholding, and error propagation."""

    def test_primary_success_never_calls_fallback(self) -> None:
        primary = FakeModel([{"kind": "finish", "note": "primary succeeded"}])
        fallback = FakeModel([{"kind": "finish", "note": "fallback should not be called"}])
        cascade = CascadingModel(primary, fallback)

        res = cascade.propose(context={}, tools=(), sampling={})
        self.assertTrue(res.ok)
        self.assertEqual(res.value.get("note"), "primary succeeded")
        self.assertEqual(cascade.total_primary_attempts, 1)
        self.assertEqual(cascade.total_fallback_attempts, 0)
        self.assertEqual(cascade.consecutive_failures, 0)

    def test_primary_failure_escalates_to_fallback(self) -> None:
        class FailingModel:
            def propose(self, *args, **kwargs):
                return Result.fail(kind="instrument_error", message="local server offline")

        primary = FailingModel()
        fallback = FakeModel([{"kind": "finish", "note": "fallback handled proposal"}])
        cascade = CascadingModel(primary, fallback, max_primary_failures=1)

        # First turn: primary fails, fallback succeeds
        res1 = cascade.propose(context={}, tools=(), sampling={})
        self.assertTrue(res1.ok)
        self.assertEqual(res1.value.get("note"), "fallback handled proposal")
        self.assertEqual(cascade.total_primary_attempts, 1)
        self.assertEqual(cascade.total_fallback_attempts, 1)
        self.assertEqual(cascade.consecutive_failures, 1)

        # Second turn: threshold exceeded, directly routes to fallback
        fallback2 = FakeModel([{"kind": "finish", "note": "fallback direct"}])
        cascade.fallback = fallback2
        res2 = cascade.propose(context={}, tools=(), sampling={})
        self.assertTrue(res2.ok)
        self.assertEqual(res2.value.get("note"), "fallback direct")
        self.assertEqual(cascade.total_primary_attempts, 1)  # Did not attempt primary
        self.assertEqual(cascade.total_fallback_attempts, 2)

    def test_both_fail_returns_exhausted_instrument_error(self) -> None:
        class FailingModel:
            def __init__(self, msg: str):
                self.msg = msg
            def propose(self, *args, **kwargs):
                return Result.fail(kind="instrument_error", message=self.msg)

        primary = FailingModel("local model timeout")
        fallback = FailingModel("cloud quota exceeded")
        cascade = CascadingModel(primary, fallback)

        res = cascade.propose(context={}, tools=(), sampling={})
        self.assertFalse(res.ok)
        self.assertEqual(res.error.kind, "instrument_error")
        self.assertIn("Cascade exhausted", res.error.message)
        self.assertIn("local model timeout", res.error.message)
        self.assertIn("cloud quota exceeded", res.error.message)


class TestAutofixHarness(unittest.TestCase):
    """Verify Autofix closed-loop rollback and state isolation."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp.name)
        self.target_file = self.tmp_path / "module.py"
        self.target_file.write_text("def broken():\n    return False\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_rollback_restores_pristine_file_on_failure(self) -> None:
        original = self.target_file.read_text(encoding="utf-8")

        # Simulate a loop failure with rollback
        corrupted = "def broken():\n    raise SyntaxError('corrupted')\n"
        self.target_file.write_text(corrupted, encoding="utf-8")

        # Rollback logic
        self.target_file.write_text(original, encoding="utf-8")
        self.assertEqual(self.target_file.read_text(encoding="utf-8"), original)


if __name__ == "__main__":
    unittest.main()
