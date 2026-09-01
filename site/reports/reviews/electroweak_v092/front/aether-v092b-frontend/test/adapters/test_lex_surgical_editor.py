import unittest

from vanguard.packages.adapters.bindings.lex_surgical_editor import LexSurgicalEditor


class TestLexSurgicalEditor(unittest.TestCase):
    def test_exact_patch_has_pre_and_postimage_receipt(self) -> None:
        ok, result, receipt, reason = LexSurgicalEditor.apply_patch("a=1\n", "a=1", "a=2")
        self.assertTrue(ok)
        self.assertEqual(result, "a=2\n")
        self.assertEqual(reason, "applied")
        self.assertTrue(receipt and receipt.success)

    def test_ambiguous_preimage_is_rejected_without_mutation(self) -> None:
        ok, result, receipt, reason = LexSurgicalEditor.apply_patch("x\nx\n", "x", "y")
        self.assertFalse(ok)
        self.assertEqual(result, "x\nx\n")
        self.assertIsNone(receipt)
        self.assertEqual(reason, "preimage_not_unique")
