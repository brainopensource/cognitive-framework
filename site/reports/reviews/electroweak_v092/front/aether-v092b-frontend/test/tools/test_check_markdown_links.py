from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.linters.check_markdown_links import check, heading_anchors


class MarkdownLinkTests(unittest.TestCase):
    def test_heading_anchors_follow_duplicate_suffixes(self) -> None:
        anchors = heading_anchors("# A & B\n## Repeat\n## Repeat\n")
        self.assertEqual({"a--b", "repeat", "repeat-1"}, anchors)

    def test_check_rejects_missing_fragment(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "README.md").write_text(
                "[valid](target.md#present) [invalid](target.md#absent)\n",
                encoding="utf-8",
            )
            (root / "target.md").write_text("# Present\n", encoding="utf-8")
            errors = check(root)
        self.assertEqual(1, len(errors))
        self.assertIn("#absent", errors[0])

    def test_check_validates_same_file_fragment(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "README.md").write_text("# Present\n[here](#present)\n", encoding="utf-8")
            self.assertEqual([], check(root))


if __name__ == "__main__":
    unittest.main()
