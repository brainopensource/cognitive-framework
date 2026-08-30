import unittest
from pathlib import Path

class TestGenericityGuard(unittest.TestCase):
    def test_core_has_no_aether_layout_literals(self):
        root = Path(__file__).parents[1] / "core"
        forbidden = ("AETHER", "Vanguard", "vanguard/", "docs/SPEC.md", "docs/backend/", "constitutional", "test/kernel/", "test/agency/")
        for path in root.glob("*.py"):
            text = path.read_text()
            for literal in forbidden:
                self.assertNotIn(literal, text, f"{literal} leaked into generic core: {path}")
