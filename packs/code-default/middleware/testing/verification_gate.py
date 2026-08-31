"""Deterministic verification gate evaluating test evidence before completion."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .test_output_parser import ParsedTestOutput, parse_test_output


@dataclass(frozen=True, slots=True)
class GateDecision:
    admitted: bool
    reason: str
    diagnostics: tuple[str, ...] = ()


def evaluate_verification_gate(
    parsed: ParsedTestOutput,
    *,
    require_zero_exit: bool = True,
    require_executed_tests: bool = True,
) -> GateDecision:
    """Deterministically decide if test execution output allows completion."""
    if require_zero_exit and parsed.exit_code != 0:
        return GateDecision(
            admitted=False,
            reason=f"Test process exited with non-zero code {parsed.exit_code}",
            diagnostics=parsed.short_diagnostics,
        )

    if parsed.failed_tests:
        return GateDecision(
            admitted=False,
            reason=f"{len(parsed.failed_tests)} tests failed",
            diagnostics=parsed.short_diagnostics,
        )

    if not parsed.passed:
        return GateDecision(
            admitted=False,
            reason="Test run was not successful",
            diagnostics=parsed.short_diagnostics,
        )

    if require_executed_tests and parsed.total_tests == 0:
        return GateDecision(
            admitted=False,
            reason="No tests were executed",
            diagnostics=parsed.short_diagnostics,
        )

    return GateDecision(
        admitted=True,
        reason="All tests passed successfully",
        diagnostics=(),
    )
