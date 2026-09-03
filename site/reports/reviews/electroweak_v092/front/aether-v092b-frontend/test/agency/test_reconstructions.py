"""Tests for Pack Reconstructions and Multi-Dimensional DNA Differentiation (S9-B-01)."""

from __future__ import annotations

import unittest
from pathlib import Path

from vanguard.packages.agency.manifests.loader import ManifestLoader

MANIFESTS_DIR = Path(__file__).resolve().parents[2] / "vanguard" / "packages" / "agency" / "manifests"


class TestPackReconstructions(unittest.TestCase):
    def setUp(self) -> None:
        self.loader = ManifestLoader(MANIFESTS_DIR)

    def test_all_packs_compose_successfully(self) -> None:
        """S9-B-01: Each pack composes with ManifestLoader with zero agency/episode/ edits."""
        pack_names = [
            "vg-code-default",
            "vg-code-claude-shaped",
            "vg-code-swe-mini",
            "vg-code-opencode-shaped",
            "vg-shell-only",
        ]
        for name in pack_names:
            pack = self.loader.load_pack(name)
            self.assertIsNotNone(pack)
            self.assertEqual(pack.name, name)
            self.assertTrue(len(pack.manifest.capabilities) > 0)

            # Assert REFERENCE.md exists
            ref_path = MANIFESTS_DIR / name / "REFERENCE.md"
            self.assertTrue(ref_path.exists(), f"REFERENCE.md missing for pack {name}")
            ref_content = ref_path.read_text(encoding="utf-8")
            self.assertIn("Public Sources", ref_content)
            self.assertIn("What Was NOT Copied", ref_content)
            self.assertIn("Honesty Label", ref_content)

    def test_packs_differ_on_at_least_three_dna_dimensions(self) -> None:
        """S9-B-01: Each pack differs from default on >= 3 DNA dimensions."""
        default_pack = self.loader.load_pack("vg-code-default")
        claude_pack = self.loader.load_pack("vg-code-claude-shaped")
        swe_pack = self.loader.load_pack("vg-code-swe-mini")
        opencode_pack = self.loader.load_pack("vg-code-opencode-shaped")

        def count_differences(p1, p2) -> int:
            diffs = 0
            # Dim 1: Compaction policy
            if p1.components_data.get("context_policy") != p2.components_data.get("context_policy"):
                diffs += 1
            # Dim 2: Routing policy
            if p1.components_data.get("routing_policy") != p2.components_data.get("routing_policy"):
                diffs += 1
            # Dim 3: Approval policy
            if p1.components_data.get("approval_policy") != p2.components_data.get("approval_policy"):
                diffs += 1
            # Dim 4: Budget policy / turns
            if p1.raw_manifest.get("budgetPolicy") != p2.raw_manifest.get("budgetPolicy"):
                diffs += 1
            # Dim 5: Aliases / tool surface
            if p1.translator.to_canonical_map != p2.translator.to_canonical_map:
                diffs += 1
            # Dim 6: System prompt
            if p1.components_data.get("system_prompt") != p2.components_data.get("system_prompt"):
                diffs += 1
            return diffs

        # Assert each pack differs from default on at least 3 dimensions
        diff_claude = count_differences(default_pack, claude_pack)
        diff_swe = count_differences(default_pack, swe_pack)
        diff_opencode = count_differences(default_pack, opencode_pack)

        self.assertGreaterEqual(diff_claude, 3, f"Claude-shaped differences {diff_claude} < 3")
        self.assertGreaterEqual(diff_swe, 3, f"SWE-mini differences {diff_swe} < 3")
        self.assertGreaterEqual(diff_opencode, 3, f"OpenCode-shaped differences {diff_opencode} < 3")

    def test_product_pack_declares_index_and_skills(self) -> None:
        """W11-B / W12-B: vg-code-default declares IndexPort retrieval and skill artifacts."""
        default_pack = self.loader.load_pack("vg-code-default")
        self.assertIn("retrieval_policy", default_pack.components_data)
        retrieval = default_pack.components_data["retrieval_policy"]
        retrieval_obj = retrieval[0] if isinstance(retrieval, list) else retrieval
        self.assertEqual(retrieval_obj.get("provider"), "IndexPort")

        # Verify skills loaded
        skills = default_pack.components_data.get("skill") or default_pack.components_data.get("skills")
        self.assertIsNotNone(skills)
        self.assertIsInstance(skills, list)
        self.assertGreaterEqual(len(skills), 3)
        skill_ids = [s.get("id") for s in skills]
        self.assertIn("pytest-green", skill_ids)
        self.assertIn("read-receipt-before-repatch", skill_ids)
        self.assertIn("scaffold-python-api-static-html", skill_ids)

    def test_skills_are_load_bearing_not_decorative(self) -> None:
        """S18-B-01: Skills declare bodyPath pointing to separate reachable markdown files."""
        pack = self.loader.load_pack("vg-code-default")
        skills = pack.components_data.get("skill") or pack.components_data.get("skills") or []
        self.assertGreaterEqual(len(skills), 3)

        # Verify bodies are external markdown files reachable via fs.read, not inlined in prefix
        for s in skills:
            self.assertIn("bodyPath", s)
            self.assertIn("id", s)
            self.assertIn("name", s)
            self.assertIn("description", s)
            body_file = MANIFESTS_DIR / "vg-code-default" / s["bodyPath"]
            self.assertTrue(body_file.exists(), f"Skill body markdown file missing: {body_file}")


if __name__ == "__main__":
    unittest.main()
