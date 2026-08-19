"""`TSK-EPIC-060-001` / `G-060-01`: the coding cell is a *client* of the
runtime, not its ontology (VG-02 §1.2) -- `runtime/` owns zero coding-named
application modules, and `apps/coding/` is where they live instead.
"""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUNTIME = ROOT / "vanguard" / "packages" / "runtime"
APPS_CODING = ROOT / "vanguard" / "packages" / "apps" / "coding"

MOVED_MODULES = (
    "coding_budget.py",
    "coding_coordinator.py",
    "coding_entrypoint.py",
    "coding_plan.py",
    "coding_progress.py",
    "coding_verification.py",
    "coding_session.py",
)


class CodingCellLocation(unittest.TestCase):
    def test_runtime_owns_none_of_the_moved_modules(self) -> None:
        for name in MOVED_MODULES:
            self.assertFalse((RUNTIME / name).exists(),
                             f"{name} must not remain under runtime/")

    def test_apps_coding_owns_every_moved_module(self) -> None:
        for name in MOVED_MODULES:
            self.assertTrue((APPS_CODING / name).is_file(),
                            f"{name} missing from apps/coding/")

    def test_domain_ledger_no_longer_exports_project_coding_session(self) -> None:
        """`M11`: domain stays coding-agnostic; the projection is an app
        concern now, not a domain export."""
        from vanguard.packages.domain import ledger

        self.assertFalse(hasattr(ledger, "project_coding_session"))

    def test_the_moved_modules_import_cleanly_from_their_new_home(self) -> None:
        import importlib

        for name in MOVED_MODULES:
            module_name = "vanguard.packages.apps.coding." + name[:-3]
            importlib.import_module(module_name)  # raises on failure


if __name__ == "__main__":
    unittest.main()
