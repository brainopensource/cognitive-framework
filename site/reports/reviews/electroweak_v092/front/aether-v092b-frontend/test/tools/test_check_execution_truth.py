from __future__ import annotations

import unittest

from tools.linters.check_execution_truth import validate


class TestExecutionTruth(unittest.TestCase):
    def test_canonical_execution_documents_are_consistent(self) -> None:
        self.assertEqual(validate(), [])
