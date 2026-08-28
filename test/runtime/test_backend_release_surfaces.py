"""Focused backend regressions for install and release qualification surfaces."""

from __future__ import annotations

import json
import tempfile
import tomllib
import unittest
from pathlib import Path

from vanguard import __version__
from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.agency.manifests.loader import ManifestLoader
from vanguard.packages.runtime.cli import default_manifest_path
from tools.release_qualification import qualify


ROOT = Path(__file__).resolve().parents[2]


class InstallableBackendSurface(unittest.TestCase):
    def test_public_version_matches_distribution_metadata(self) -> None:
        with (ROOT / "pyproject.toml").open("rb") as handle:
            declared = tomllib.load(handle)["project"]["version"]
        self.assertEqual(__version__, declared)

    def test_manifest_loader_accepts_the_installed_style_file_path(self) -> None:
        manifest = default_manifest_path()
        loaded = ManifestLoader().load_pack(manifest)
        self.assertEqual(loaded.name, "vg-code-default")


class DurableEventStoreSurface(unittest.TestCase):
    def test_integrity_and_backup_restore_are_atomic_surfaces(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            store = SqliteEventStore(root / "events.sqlite3")
            report = store.integrity_check()
            self.assertTrue(report.ok)
            self.assertTrue(report.value and report.value["ok"])
            backup = store.backup(root / "backup.sqlite3")
            store.close()
            restored = SqliteEventStore.restore_backup(backup, root / "restored.sqlite3")
            self.assertTrue(restored.integrity_check().value["ok"])
            restored.close()


class ReleaseQualificationSurface(unittest.TestCase):
    def test_missing_external_git_receipt_blocks_without_git_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            envelope = root / "release.json"
            envelope.write_text("{}", encoding="utf-8")
            receipt = root / "external.json"
            receipt.write_text(json.dumps({"source": "internal"}), encoding="utf-8")
            report = qualify(
                subject="sha256:" + "a" * 64,
                envelope=envelope,
                git_receipt=receipt,
            )
            self.assertFalse(report["passed"])
            self.assertEqual(report["gitOperations"], "none")
            self.assertTrue(report["checks"]["external_git_prerequisite"])


if __name__ == "__main__":
    unittest.main()
