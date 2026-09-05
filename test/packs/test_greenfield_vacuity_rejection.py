"""T-81: greenfield oracles must fail against empty implementation stubs."""

from __future__ import annotations

import io
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ORACLES = ROOT / "packs" / "code-default" / "oracles"
if str(ORACLES) not in sys.path:
    sys.path.insert(0, str(ORACLES))

from gate import GreenfieldControlOutcome, PackOracleGate
from vanguard.packages.domain.wire.result import Err, Ok


def _run_suite(case: type[unittest.TestCase]) -> GreenfieldControlOutcome:
    result = unittest.TextTestRunner(stream=io.StringIO()).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(case)
    )
    return GreenfieldControlOutcome(
        tests_run=result.testsRun,
        failures=len(result.failures),
        errors=len(result.errors),
    )


class TestGreenfieldVacuityRejection(unittest.TestCase):
    def test_non_integer_control_counts_are_rejected(self) -> None:
        decision = PackOracleGate().run_greenfield_control(
            lambda: GreenfieldControlOutcome(1, False)
        )

        self.assertIsInstance(decision, Err)
        self.assertEqual(decision.code, "invalid_request")

    def test_pass_stub_with_zero_control_failures_is_typed_rejection(self) -> None:
        def empty_stub() -> None:
            pass

        class VacuousOracle(unittest.TestCase):
            def test_stub(self) -> None:
                empty_stub()

        decision = PackOracleGate().run_greenfield_control(
            lambda: _run_suite(VacuousOracle)
        )

        self.assertIsInstance(decision, Err)
        self.assertEqual(decision.code, "VACUOUS_ORACLE_REJECTED")

    def test_swallowed_not_implemented_stub_is_typed_rejection(self) -> None:
        def empty_stub() -> None:
            raise NotImplementedError

        class VacuousOracle(unittest.TestCase):
            def test_stub(self) -> None:
                try:
                    empty_stub()
                except NotImplementedError:
                    pass

        decision = PackOracleGate().run_greenfield_control(
            lambda: _run_suite(VacuousOracle)
        )

        self.assertIsInstance(decision, Err)
        self.assertEqual(decision.code, "VACUOUS_ORACLE_REJECTED")

    def test_not_implemented_stub_makes_control_red(self) -> None:
        def empty_stub() -> None:
            raise NotImplementedError

        class BehavioralOracle(unittest.TestCase):
            def test_stub(self) -> None:
                empty_stub()

        decision = PackOracleGate().run_greenfield_control(
            lambda: _run_suite(BehavioralOracle)
        )

        self.assertIsInstance(decision, Ok)
        self.assertEqual(decision.value.errors, 1)


if __name__ == "__main__":
    unittest.main()
