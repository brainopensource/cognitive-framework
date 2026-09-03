from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from vanguard.packages.runtime.state_contract import (
    StateDirectoryError,
    StateDirectoryUnwritableError,
    ensure_state_directory,
    inspect_state_directory,
    resolve_state_directory,
)
from vanguard.packages.runtime.bootstrap import RuntimeBootstrap
from vanguard.packages.adapters.models.fake import FakeModel


class TestStateContract(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.workspace = Path(self.tmp_dir.name).resolve()

    def tearDown(self) -> None:
        self.tmp_dir.cleanup()

    def test_resolve_default_state_directory(self) -> None:
        state_dir = resolve_state_directory(self.workspace)
        self.assertEqual(state_dir, self.workspace / ".vanguard")

    def test_resolve_explicit_absolute_state_directory(self) -> None:
        custom = Path("/tmp/custom_vanguard_state")
        resolved = resolve_state_directory(self.workspace, state_dir=custom)
        self.assertEqual(resolved, custom.resolve())

    def test_resolve_explicit_relative_state_directory(self) -> None:
        resolved = resolve_state_directory(self.workspace, state_dir="my_state")
        self.assertEqual(resolved, (self.workspace / "my_state").resolve())

    def test_ensure_creates_missing_state_and_blobs(self) -> None:
        target = self.workspace / "sub" / ".vanguard"
        self.assertFalse(target.exists())
        ensured = ensure_state_directory(target)
        self.assertTrue(ensured.is_dir())
        self.assertTrue((ensured / "blobs").is_dir())

    def test_inspect_reports_correct_state(self) -> None:
        target = self.workspace / ".vanguard"
        report1 = inspect_state_directory(target)
        self.assertFalse(report1.exists)
        self.assertTrue(report1.writable)

        ensure_state_directory(target)
        report2 = inspect_state_directory(target)
        self.assertTrue(report2.exists)
        self.assertTrue(report2.is_directory)
        self.assertTrue(report2.writable)
        self.assertTrue(report2.blobs_exists)

    def test_unwritable_directory_fails_closed_in_bootstrap(self) -> None:
        unwritable_parent = self.workspace / "readonly_zone"
        unwritable_parent.mkdir(mode=0o555)
        unwritable_state = unwritable_parent / ".vanguard"

        try:
            with self.assertRaises(StateDirectoryUnwritableError):
                RuntimeBootstrap.build(
                    profile_id="product",
                    repo_path=self.workspace,
                    model=FakeModel([]),
                    state_dir=unwritable_state,
                )
        finally:
            unwritable_parent.chmod(0o755)
