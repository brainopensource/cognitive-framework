"""W3a: rollback defects in the adapter two-phase commit.

Packet W3a covers the three latent defects found by inspection in
`AtomicMultiFileTransactionManager`. Two are reachable and red below; the
third (the parallel `stage_index` counter) has no reachable divergence today
and is recorded as a coupling hazard in the handoff, not asserted here.

Scope note: the durable journal, indivisible publication and fault-injection
matrix are W3b and are NOT started here -- that work is MS-CAS and is gated.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from vanguard.packages.adapters.environment.transaction import (
    AtomicMultiFileTransactionManager,
    FileMutation,
    TXN_TMP_MARKER,
)


class TestNonOSErrorIsContained(unittest.TestCase):
    """Defect 1 -- a non-OSError escapes `_commit` with no rollback."""

    def test_unencodable_content_fails_closed_without_leaking_temps(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "a.txt").write_text("PRE\n", encoding="utf-8")
            (root / "b.txt").write_text("PRE\n", encoding="utf-8")
            manager = AtomicMultiFileTransactionManager(root)

            # A lone surrogate cannot be encoded as utf-8, so `write_text`
            # raises UnicodeEncodeError. `.txt` skips the AST preflight, so the
            # raise happens inside the staging pass. `_commit` catches only
            # OSError, so it escapes `execute_transaction` entirely.
            mutations = [
                FileMutation("a.txt", "NEW\n", "modify"),
                FileMutation("b.txt", "\ud800", "modify"),
            ]

            try:
                result = manager.execute_transaction(mutations)
            except Exception as exc:  # noqa: BLE001 - the defect under test
                self.fail(
                    f"execute_transaction raised {type(exc).__name__} instead of "
                    "returning a failed Result; the port contract is Result-typed "
                    "and a non-OSError bypasses rollback entirely"
                )

            self.assertFalse(result.ok, "unencodable content must fail closed")
            leaked = sorted(p.name for p in root.iterdir() if TXN_TMP_MARKER in p.name)
            self.assertEqual(
                leaked,
                [],
                f"staged temporaries survived a failed transaction: {leaked}",
            )
            self.assertEqual(
                (root / "a.txt").read_text(encoding="utf-8"),
                "PRE\n",
                "pre-image must survive a failed transaction",
            )


class TestRestoreUsesValidatedPaths(unittest.TestCase):
    """Defect 2 -- `_restore` re-derives raw paths instead of resolved ones."""

    def test_rollback_does_not_materialise_directories_outside_the_mutation_set(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "a.txt").write_text("PRE\n", encoding="utf-8")
            # Replacing onto a directory raises OSError, forcing the rollback.
            (root / "c.txt").mkdir()
            (root / "c.txt" / "keep").write_text("x", encoding="utf-8")
            manager = AtomicMultiFileTransactionManager(root)

            # `_resolve_safe_path` normpath()s this to "a.txt", but `_restore`
            # rebuilds `root / "sub/../a.txt"` verbatim and mkdirs its parent.
            mutations = [
                FileMutation("sub/../a.txt", "NEW\n", "modify"),
                FileMutation("c.txt", "NEW\n", "modify"),
            ]

            result = manager.execute_transaction(mutations)

            self.assertFalse(result.ok, "replacing onto a directory must fail")
            self.assertEqual(
                (root / "a.txt").read_text(encoding="utf-8"),
                "PRE\n",
                "pre-image must be restored",
            )
            self.assertFalse(
                (root / "sub").exists(),
                "rollback created directory 'sub/', which was never part of the "
                "mutation set; recovery must not alter the candidate tree beyond "
                "restoring pre-images",
            )

    def test_rollback_restores_without_side_effects_for_nested_creates(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "c.txt").mkdir()
            (root / "c.txt" / "keep").write_text("x", encoding="utf-8")
            manager = AtomicMultiFileTransactionManager(root)

            before = sorted(p.name for p in root.iterdir())
            mutations = [
                FileMutation("pkg/./mod.txt", "NEW\n", "create"),
                FileMutation("c.txt", "NEW\n", "modify"),
            ]

            result = manager.execute_transaction(mutations)

            self.assertFalse(result.ok)
            self.assertFalse(
                (root / "pkg" / "mod.txt").exists(),
                "a created file must not survive a rolled-back transaction",
            )
            leaked = sorted(p.name for p in root.rglob("*") if TXN_TMP_MARKER in p.name)
            self.assertEqual(leaked, [], f"staged temporaries survived: {leaked}")
            del before


class TestStagedPublishCorrespondence(unittest.TestCase):
    """Defect 3 -- regression guard, not a falsifier.

    The stage and publish passes skip on byte-identical conditions today, so no
    divergence is reachable. This pins the correspondence so that changing one
    condition without the other is caught.
    """

    def test_mixed_batch_publishes_each_staged_file_to_its_own_destination(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "keep.txt").write_text("KEEP\n", encoding="utf-8")
            (root / "drop.txt").write_text("DROP\n", encoding="utf-8")
            (root / "edit.txt").write_text("OLD\n", encoding="utf-8")
            manager = AtomicMultiFileTransactionManager(root)

            # Interleave writes with a delete and a content-None entry so the
            # two passes must skip the same members in the same order.
            mutations = [
                FileMutation("edit.txt", "ONE\n", "modify"),
                FileMutation("drop.txt", None, "delete"),
                FileMutation("new.txt", "TWO\n", "create"),
            ]

            result = manager.execute_transaction(mutations)

            self.assertTrue(result.ok, getattr(result, "error", None))
            self.assertEqual((root / "edit.txt").read_text(encoding="utf-8"), "ONE\n")
            self.assertEqual((root / "new.txt").read_text(encoding="utf-8"), "TWO\n")
            self.assertFalse((root / "drop.txt").exists())
            self.assertEqual((root / "keep.txt").read_text(encoding="utf-8"), "KEEP\n")


if __name__ == "__main__":
    unittest.main()
