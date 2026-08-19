"""I-7 and I-6 CI gates plus Governor reservation (no pack-local Budget class)."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class DomainBlindnessGateTests(unittest.TestCase):
    def test_layer0_is_clean(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "check_domain_blindness.py")],
            cwd=ROOT,
            check=False,
        )
        self.assertEqual(result.returncode, 0)

    def test_planted_leak_fails_closed(self) -> None:
        fixture = ROOT / "test" / "broken" / "fixtures" / "domain_blindness"
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "check_domain_blindness.py"),
             "--root", str(fixture), "--expect-fail"],
            cwd=ROOT,
            check=False,
        )
        self.assertEqual(result.returncode, 0)


class IsolationPolicyGateTests(unittest.TestCase):
    def test_pack_terminal_is_container(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "check_isolation_policy.py")],
            cwd=ROOT,
            check=False,
        )
        self.assertEqual(result.returncode, 0)

    def test_in_process_proc_exec_fails(self) -> None:
        fixture = ROOT / "test" / "broken" / "fixtures" / "isolation_policy"
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "check_isolation_policy.py"),
             "--root", str(fixture), "--expect-fail"],
            cwd=ROOT,
            check=False,
        )
        self.assertEqual(result.returncode, 0)


class ReservationGovernorTests(unittest.TestCase):
    def test_worst_case_goes_through_governor(self) -> None:
        sys.path.insert(0, str(ROOT / "packs" / "code-default"))
        from layer0.kernel.budget import BudgetDenied, Governor
        from reservation import worst_case_reservation

        governor = Governor({
            "usd_micros": 5000, "millis": 10**9, "tokens": 10**6,
            "bytes": 0, "turns": 10, "depth": 2,
        })
        free = worst_case_reservation(model="mock:free", pricing=None)
        lease = governor.reserve("run", free)
        self.assertEqual(lease.reserved.get("usd_micros", 0), 0)
        paid = worst_case_reservation(
            model="deepseek/deepseek-v4-flash",
            pricing=(140_000, 280_000, 14_000),
            max_prompt_tokens=10_000,
            max_completion_tokens=5_000,
        )
        self.assertEqual(paid.usd_micros, 2800)
        governor.reserve("run", paid)
        with self.assertRaises(BudgetDenied):
            worst_case_reservation(model="vendor/unpriced", pricing=None)

    def test_packs_have_no_budget_controller_class(self) -> None:
        import re

        hits: list[str] = []
        for path in (ROOT / "packs").rglob("*.py"):
            for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
                if re.search(r"class .*Budget", line):
                    hits.append(f"{path}:{lineno}:{line.strip()}")
        self.assertEqual(hits, [])


if __name__ == "__main__":
    unittest.main()
