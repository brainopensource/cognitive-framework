"""RF-95: the product coding path is durable without assurance infrastructure."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from vanguard.packages.adapters.models.fake import FakeModel
from vanguard.packages.runtime.bootstrap import RuntimeBootstrap
from vanguard.packages.runtime.profiles import resolve_profile


class RF95ProductExecutionProfileFalsifier(unittest.TestCase):
    def test_product_profile_preserves_layers_without_requiring_isolation(self) -> None:
        profile = resolve_profile("product", host_qualifies=False)

        self.assertEqual(profile.requested.process_backend, "host")
        self.assertEqual(profile.requested.persistence_mode, "sqlite-wal")
        self.assertTrue(profile.requested.persistence_durable)
        self.assertEqual(profile.requested.evaluation_mode, "none")
        self.assertFalse(profile.requested.promotion_eligible)

    def test_product_bootstrap_uses_file_backed_wal_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            deps = RuntimeBootstrap.build(
                profile_id="product",
                repo_path=repo,
                model=FakeModel([]),
                host_qualifies=False,
            )
            try:
                self.assertTrue(deps.store.durable)
                self.assertEqual(deps.store.journal_mode, "wal")
                self.assertEqual(
                    Path(deps.store.db_path), repo / ".vanguard" / "events.sqlite3")
            finally:
                deps.cleanup()


if __name__ == "__main__":
    unittest.main()
