"""BEP-05 parity vectors for first-party compositions."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFESTS = ROOT / "vanguard/packages/agency/manifests"


def _manifest(name: str) -> tuple[dict, str]:
    path = MANIFESTS / name / "manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    prompt_ref = manifest["components"]["system_prompt"][0]
    return manifest, (MANIFESTS / prompt_ref).read_text(encoding="utf-8").lower()


class UnifiedCompositionContractTests(unittest.TestCase):
    def test_coding_max_research_and_tutor_are_declared_compositions(self) -> None:
        rows = {
            "coding": _manifest("vg-code-max"),
            "research": _manifest("vg-research-v090-v2-web-corroborated"),
            "tutor": _manifest("vg-tutor-v090-v2-evidence-graph"),
        }
        for manifest, _prompt in rows.values():
            self.assertTrue(manifest["harness"])
            self.assertTrue(manifest["capabilities"])
            self.assertTrue(manifest["components"])
        coding, _ = rows["coding"]
        self.assertIn("patch.apply", {row["verb"] for row in coding["capabilities"]})
        for key in ("research", "tutor"):
            manifest, _ = rows[key]
            verbs = {row["verb"] for row in manifest["capabilities"]}
            self.assertNotIn("patch.apply", verbs)
            self.assertNotIn("proc.exec", verbs)

    def test_research_and_tutor_prompts_preserve_domain_completion_evidence(self) -> None:
        _, research_prompt = _manifest("vg-research-v090-v2-web-corroborated")
        _, tutor_prompt = _manifest("vg-tutor-v090-v2-evidence-graph")
        self.assertIn("citation", research_prompt)
        self.assertTrue("evidence" in tutor_prompt or "teach" in tutor_prompt)


if __name__ == "__main__":
    unittest.main()
