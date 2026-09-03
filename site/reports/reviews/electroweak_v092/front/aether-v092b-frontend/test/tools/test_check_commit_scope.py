from __future__ import annotations

import unittest

from tools.linters.check_commit_scope import is_mislabelled


class TestCommitScope(unittest.TestCase):
    def test_docs_label_cannot_hide_production_or_schema_change(self) -> None:
        self.assertTrue(is_mislabelled("docs(runtime): wire child", ["vanguard/packages/runtime/root.py"]))
        self.assertTrue(is_mislabelled("chore: regenerate", ["schemas/mhf/event.schema.json"]))

    def test_valid_scopes_remain_valid(self) -> None:
        self.assertFalse(is_mislabelled("fix(runtime): wire child", ["vanguard/packages/runtime/root.py"]))
        self.assertFalse(is_mislabelled("docs: update law", ["docs/SPEC.md"]))
