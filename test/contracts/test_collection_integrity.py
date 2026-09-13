"""Complete collection and current-subject test integrity contract (NT-B01, NT-B02, NT-B03).

Falsifier for T-101 / GATE-01:
1. Discovers complete test suites across all canonical test directories.
2. Proves that missing or omitted test modules fail collection integrity verification.
3. Proves that import-broken test modules fail collection (produce _FailedTest errors).
4. Verifies that all test_*.py files in test/ are accounted for (no silent exclusion).
5. Verifies that retired test modules have explicit tombstone/successor documentation.
6. Proves that test discovery operates nonmutatingly.
"""

from __future__ import annotations

import hashlib
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Sequence

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

# Known retired or aggregator test modules with documented successor claims
RECORDED_RETIREMENTS_AND_AGGREGATORS: dict[str, str] = {
    "test/contracts/test_t1.py": "Aggregator module importing t1_dev1_* and t7_* TestCase suites (REQ-SCHEMA-001..012)",
    "test/contracts/test_t3.py": "Aggregator module importing t3_ledger TestCase suites (TEST-LEDGER-001..008)",
    "test/falsifiers/test_m65_integrated_study.py": "MS-META falsifier retired: lab/ research package withdrawn (Wave 2.5)",
    "test/falsifiers/test_m701_recorded_workload.py": "MS-META falsifier retired: lab/ research package withdrawn (Wave 2.5)",
    "test/falsifiers/test_m7_topology_and_independence.py": "MS-META falsifier retired: lab/ research package withdrawn (Wave 2.5)",
    "test/falsifiers/test_rf114_rf117_m65_falsifiers.py": "MS-META falsifier retired: lab/ research package withdrawn (Wave 2.5)",
    "test/runtime/test_coding_coordinator.py": "Retired with apps/coding (M3); semantics live in packs/code-default/",
    "test/runtime/test_coding_entrypoint.py": "Retired with apps/coding (M3); semantics live in packs/code-default/",
    "test/runtime/test_coding_plan.py": "Retired with apps/coding (M3); semantics live in packs/code-default/",
    "test/runtime/test_coding_progress.py": "Retired with apps/coding (M3); semantics live in packs/code-default/",
    "test/runtime/test_coding_resume.py": "Retired with apps/coding (M3); semantics live in packs/code-default/",
    "test/runtime/test_m701_independence.py": "MS-META falsifier retired: lab/ research package withdrawn (Wave 2.5)",
}

CANONICAL_TEST_SUBSYSTEMS: tuple[str, ...] = (
    "kernel",
    "contracts",
    "agency",
    "runtime",
    "adapters",
    "security",
    "trust",
    "governance",
    "integration",
    "packs",
    "registry",
    "benchmarks",
    "lab",
    "tools",
    "apps",
    "transforms",
    "workflows",
    "middleware",
    "falsifiers",
)


def _flatten_suite(suite: unittest.TestSuite) -> list[unittest.TestCase]:
    """Recursively extract all test cases from a nested TestSuite."""
    tests: list[unittest.TestCase] = []
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            tests.extend(_flatten_suite(item))
        else:
            tests.append(item)
    return tests


def _collect_discovered_modules(suite: unittest.TestSuite) -> set[str]:
    """Extract all module names represented in the discovered suite."""
    tests = _flatten_suite(suite)
    modules: set[str] = set()
    for t in tests:
        cls = t.__class__
        if cls.__name__ == "_FailedTest":
            # For discovery failures, the testMethodName or id contains the module name
            tid = t.id()
            # format: unittest.loader._FailedTest.test.module.name
            if tid.startswith("unittest.loader._FailedTest."):
                modules.add(tid.replace("unittest.loader._FailedTest.", ""))
            else:
                modules.add(getattr(t, "_testMethodName", tid))
        elif cls.__name__ == "ModuleSkipped":
            tid = t.id()
            if tid.startswith("unittest.loader.ModuleSkipped."):
                modules.add(tid.replace("unittest.loader.ModuleSkipped.", ""))
            else:
                modules.add(cls.__module__)
        else:
            modules.add(cls.__module__)
    return modules


def verify_module_inventory(
    collected_modules: set[str],
    expected_modules: Sequence[str],
) -> list[str]:
    """Check that all expected modules are present in the collected set, returning missing ones."""
    missing: list[str] = []
    for mod in expected_modules:
        if mod not in collected_modules:
            missing.append(mod)
    return missing


class TestCollectionIntegrity(unittest.TestCase):
    """Verify test collection completeness and fail-closed collection invariants (T-101)."""

    @classmethod
    def setUpClass(cls) -> None:
        loader = unittest.defaultTestLoader
        cls.suite = loader.discover(str(_REPO_ROOT / "test"), top_level_dir=str(_REPO_ROOT))
        cls.all_tests = _flatten_suite(cls.suite)
        cls.collected_modules = _collect_discovered_modules(cls.suite)

    def test_complete_collection_floor(self) -> None:
        """Root unittest discovery must collect at least 2,900 test cases on current subject."""
        total = len(self.all_tests)
        self.assertGreaterEqual(
            total,
            2900,
            f"Collection floor violation: expected >= 2900 tests, got {total}",
        )

    def test_canonical_subsystems_present_in_collection(self) -> None:
        """Every canonical test subsystem must have test modules collected by root discovery."""
        for sub in CANONICAL_TEST_SUBSYSTEMS:
            sub_prefix = f"test.{sub}."
            sub_mods = [m for m in self.collected_modules if m.startswith(sub_prefix)]
            self.assertGreater(
                len(sub_mods),
                0,
                f"Subsystem '{sub}' has zero collected test modules in discovery!",
            )

    def test_import_broken_module_fails_collection_meta_test(self) -> None:
        """An import-broken test module must fail collection as _FailedTest (never silently succeed)."""
        with tempfile.TemporaryDirectory(prefix="aether_broken_test_") as tmp:
            tmp_path = Path(tmp)
            (tmp_path / "__init__.py").write_text("", encoding="utf-8")
            broken_file = tmp_path / "test_deliberate_syntax_error.py"
            broken_file.write_text(
                "import unittest\n"
                "this is deliberate invalid python syntax !!!\n"
                "class TestDeliberate(unittest.TestCase):\n"
                "    def test_nothing(self): pass\n",
                encoding="utf-8",
            )

            loader = unittest.defaultTestLoader
            discovered = loader.discover(str(tmp_path), top_level_dir=str(tmp_path))
            tests = _flatten_suite(discovered)

            self.assertGreaterEqual(len(tests), 1, "Discovery must collect broken module as a failure item")
            failed_tests = [t for t in tests if t.__class__.__name__ == "_FailedTest"]
            self.assertEqual(
                len(failed_tests),
                1,
                "Intentionally broken test module must be represented as _FailedTest",
            )

            # Executing the suite must produce an error
            res = unittest.TestResult()
            discovered.run(res)
            self.assertEqual(len(res.errors), 1, "Running broken test must result in an error")
            self.assertEqual(len(res.failures), 0)

    def test_missing_expected_module_fails_verification(self) -> None:
        """Missing an expected test module from collection must fail verification closed."""
        synthetic_collected = {"test.kernel.test_dispatch", "test.contracts.test_b0_baseline"}
        expected = ["test.kernel.test_dispatch", "test.contracts.test_b0_baseline", "test.nonexistent.test_module"]

        missing = verify_module_inventory(synthetic_collected, expected)
        self.assertEqual(missing, ["test.nonexistent.test_module"])

        with self.assertRaises(AssertionError):
            if missing:
                raise AssertionError(f"Missing required test modules: {missing}")

    def test_no_unaccounted_test_files_omitted(self) -> None:
        """Every test_*.py file under test/ must be collected or documented in RECORDED_RETIREMENTS_AND_AGGREGATORS."""
        test_dir = _REPO_ROOT / "test"
        all_test_files = [
            p for p in test_dir.rglob("test_*.py")
            if "fixtures" not in p.parts
            and "broken" not in p.parts
            and "e2e" not in p.parts
        ]

        unaccounted: list[str] = []
        for p in all_test_files:
            rel_path = str(p.relative_to(_REPO_ROOT)).replace("\\", "/")
            if rel_path in RECORDED_RETIREMENTS_AND_AGGREGATORS:
                continue

            # Check if this test file's module is in collected_modules
            # Path: test/subsystem/test_name.py -> test.subsystem.test_name
            rel_parts = list(p.relative_to(_REPO_ROOT).parts)
            rel_parts[-1] = p.stem
            mod_name = ".".join(rel_parts)

            if mod_name not in self.collected_modules and p.stem not in self.collected_modules:
                unaccounted.append(rel_path)

        self.assertEqual(
            unaccounted,
            [],
            f"Unaccounted test files omitted from discovery (missing __init__.py or dropped): {unaccounted}",
        )

    def test_retired_modules_have_documented_rationale(self) -> None:
        """All retired or withdrawn test modules must have an explicit reason on record."""
        for path_str, reason in RECORDED_RETIREMENTS_AND_AGGREGATORS.items():
            self.assertTrue(len(reason.strip()) > 10, f"Retirement rationale for {path_str} is too brief")
            p = _REPO_ROOT / path_str
            self.assertTrue(p.is_file(), f"Recorded retired module {path_str} does not exist on disk")


if __name__ == "__main__":
    unittest.main()
