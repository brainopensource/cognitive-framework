"""M3: coding cell lives in packs/code-default/, not apps/coding or runtime shims."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUNTIME = ROOT / "vanguard" / "packages" / "runtime"
APPS_CODING = ROOT / "vanguard" / "packages" / "apps" / "coding"
APPS_CODING_MAX = ROOT / "vanguard" / "packages" / "apps" / "coding_max"
PACK = ROOT / "packs" / "code-default"


class CodingCellLocation(unittest.TestCase):
    def test_apps_coding_is_retired(self) -> None:
        self.assertFalse(APPS_CODING.exists())

    def test_thin_coding_max_facade_is_the_allowed_app_slot(self) -> None:
        self.assertTrue((APPS_CODING_MAX / "facade.py").is_file())

    def test_pack_frame_exists(self) -> None:
        self.assertTrue((PACK / "harness.yaml").is_file())
        self.assertTrue((PACK / "plugin.yaml").is_file())

    def test_runtime_has_no_coding_named_modules(self) -> None:
        leftovers = [path.name for path in RUNTIME.glob("*coding*")]
        self.assertEqual(leftovers, [])

    def test_session_projection_is_domain_tagged(self) -> None:
        from vanguard.packages.domain.ledger.session_projection import project_session

        self.assertTrue(callable(project_session))


if __name__ == "__main__":
    unittest.main()
