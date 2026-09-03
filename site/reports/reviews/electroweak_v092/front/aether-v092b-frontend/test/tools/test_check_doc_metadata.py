from __future__ import annotations

import unittest
from pathlib import Path

from tools.linters.check_doc_metadata import check, parse_frontmatter


class DocMetadataLinterTests(unittest.TestCase):
    def test_parse_frontmatter_valid(self) -> None:
        sample = """---
id: test-doc
class: law
authority: normative
canonical_for:
  - test-topic
status: living
owner: architect
version: "0.6.1"
last_verified: 2026-08-21
---

# Title
Body text.
"""
        fm = parse_frontmatter(sample)
        self.assertIsNotNone(fm)
        assert fm is not None
        self.assertEqual(fm["id"], "test-doc")
        self.assertEqual(fm["class"], "law")
        self.assertEqual(fm["authority"], "normative")
        self.assertEqual(fm["canonical_for"], ["test-topic"])
        self.assertEqual(fm["status"], "living")

    def test_parse_frontmatter_missing(self) -> None:
        sample = "# Title\nBody text without frontmatter."
        self.assertIsNone(parse_frontmatter(sample))

    def test_repository_living_docs_metadata_passes(self) -> None:
        errors = check()
        self.assertEqual(errors, [], msg=f"Doc metadata check errors:\n{errors}")


if __name__ == "__main__":
    unittest.main()
