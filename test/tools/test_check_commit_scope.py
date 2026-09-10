from __future__ import annotations

import unittest

from tools.linters.check_commit_scope import (
    has_banned_vocabulary,
    is_mislabelled,
    references_task_or_stream,
)


class TestCommitScope(unittest.TestCase):
    def test_docs_label_cannot_hide_production_or_schema_change(self) -> None:
        self.assertTrue(is_mislabelled("docs(runtime): wire child", ["vanguard/packages/runtime/root.py"]))
        self.assertTrue(is_mislabelled("chore: regenerate", ["schemas/mhf/event.schema.json"]))

    def test_valid_scopes_remain_valid(self) -> None:
        self.assertFalse(is_mislabelled("fix(runtime): wire child", ["vanguard/packages/runtime/root.py"]))
        self.assertFalse(is_mislabelled("docs: update law", ["docs/SPEC.md"]))

    def test_banned_vocabulary_detected(self) -> None:
        self.assertTrue(has_banned_vocabulary("feat(W2): Wave 2 - Phase 0 Iteration 2/2"))
        self.assertTrue(has_banned_vocabulary("chore: finish Sprint 3 tasks"))
        self.assertTrue(has_banned_vocabulary("fix(Wave1): update kernel"))
        self.assertFalse(has_banned_vocabulary("Stream A: T-99 -> MS-BASELINE: fix terminal projection"))
        self.assertFalse(has_banned_vocabulary("feat(stream-a): T-99 lossless terminal projection"))
        self.assertFalse(has_banned_vocabulary("fix(domain): validate task state schema"))

    def test_references_task_or_stream(self) -> None:
        self.assertTrue(references_task_or_stream("Stream A: T-99 -> MS-BASELINE: update"))
        self.assertTrue(references_task_or_stream("docs(execution): T-100 state schemas"))
        self.assertTrue(references_task_or_stream("docs(execution): NT-1 baseline alignment"))
        self.assertFalse(references_task_or_stream("docs(execution): unlinked planning changes"))
