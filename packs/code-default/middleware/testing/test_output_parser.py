"""Parses python unittest / pytest output into structured test failure records."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence


@dataclass(frozen=True, slots=True)
class ParsedTestOutput:
    exit_code: int
    passed: bool
    total_tests: int = 0
    failed_tests: tuple[str, ...] = field(default_factory=tuple)
    passed_tests: tuple[str, ...] = field(default_factory=tuple)
    error_locations: tuple[dict[str, Any], ...] = field(default_factory=tuple)
    exception_types: tuple[str, ...] = field(default_factory=tuple)
    short_diagnostics: tuple[str, ...] = field(default_factory=tuple)
    raw_output_digest: str = ""
    runner: str = "unknown"
    tests_collected: int | None = None
    tests_executed: int | None = None
    tests_passed: int | None = None
    tests_failed: int | None = None
    tests_skipped: int | None = None


_FAIL_PATTERN = re.compile(r"(?:FAIL|ERROR):\s+([a-zA-Z0-9_\.]+(?:\s+\([^\)]+\))?)")
_PYTEST_FAIL_PATTERN = re.compile(r"FAILED\s+([^\s:]+::[^\s]+)")
_LOCATION_PATTERN = re.compile(r'File "([^"]+)", line (\d+)(?:, in (\w+))?')
_EXCEPTION_PATTERN = re.compile(r"^([a-zA-Z_][a-zA-Z0-9_]*(?:Error|Exception|AssertionError)): (.*)$", re.MULTILINE)
_SUMMARY_PATTERN = re.compile(r"Ran (\d+) tests in [0-9\.]+s\s+(OK|FAILED)")


def parse_test_output(output: str, exit_code: int = 0) -> ParsedTestOutput:
    """Extract structured test diagnostics from raw execution stdout/stderr."""
    if not isinstance(output, str):
        output = str(output or "")

    digest = f"sha256:{hashlib.sha256(output.encode('utf-8')).hexdigest()}"

    failed: list[str] = []
    # unittest FAIL / ERROR headers
    for m in _FAIL_PATTERN.finditer(output):
        failed.append(m.group(1).strip())
    # pytest FAILED lines
    for m in _PYTEST_FAIL_PATTERN.finditer(output):
        failed.append(m.group(1).strip())

    # locations
    locations: list[dict[str, Any]] = []
    for m in _LOCATION_PATTERN.finditer(output):
        locations.append({
            "file": m.group(1),
            "line": int(m.group(2)),
            "function": m.group(3) if m.group(3) else None,
        })

    # exceptions
    exceptions: list[str] = []
    for m in _EXCEPTION_PATTERN.finditer(output):
        exc_type = m.group(1)
        if exc_type not in exceptions:
            exceptions.append(exc_type)

    ran = re.search(r"Ran\s+(\d+)\s+tests?\b", output, flags=re.IGNORECASE)
    collected_m = re.search(r"collected\s+(\d+)\s+items?\b", output, flags=re.IGNORECASE)
    passed_m = re.search(r"(\d+)\s+passed\b", output, flags=re.IGNORECASE)
    failed_m = re.search(r"(\d+)\s+failed\b", output, flags=re.IGNORECASE)
    skipped_m = re.search(r"(\d+)\s+skipped\b", output, flags=re.IGNORECASE)
    runner = "unknown"
    tests_collected: int | None = None
    tests_executed: int | None = None
    tests_passed: int | None = None
    tests_failed: int | None = None
    tests_skipped: int | None = None
    if ran:
        runner = "unittest"
        tests_collected = tests_executed = int(ran.group(1))
        fail_block = re.search(r"FAILED\s*\(([^)]*)\)", output, flags=re.IGNORECASE)
        if fail_block:
            parts = fail_block.group(1)

            def _named(name: str) -> int:
                match = re.search(rf"{name}\s*=\s*(\d+)", parts, flags=re.IGNORECASE)
                return int(match.group(1)) if match else 0

            tests_failed = _named("failures") + _named("errors")
            tests_skipped = _named("skipped")
            tests_passed = max(0, tests_executed - tests_failed - tests_skipped)
        elif re.search(r"\bOK\b", output):
            tests_passed, tests_failed, tests_skipped = tests_executed, 0, 0
    elif collected_m or passed_m or failed_m or skipped_m:
        runner = "pytest"
        tests_collected = int(collected_m.group(1)) if collected_m else None
        tests_passed = int(passed_m.group(1)) if passed_m else None
        tests_failed = int(failed_m.group(1)) if failed_m else None
        tests_skipped = int(skipped_m.group(1)) if skipped_m else None
        known = [item for item in (tests_passed, tests_failed, tests_skipped) if item is not None]
        tests_executed = sum(known) if known else tests_collected
        if tests_passed == 0 and tests_failed is None and tests_skipped is None:
            tests_executed = 0

    total_tests = tests_executed if tests_executed is not None else (tests_collected or 0)
    passed = (
        runner != "unknown"
        and exit_code == 0
        and not failed
        and (tests_failed or 0) == 0
        and (tests_executed or 0) > 0
        and (tests_passed or 0) > 0
    )

    short_diag: list[str] = []
    if failed:
        short_diag.append(f"{len(failed)} tests failed: {', '.join(failed[:3])}")
    if exceptions:
        short_diag.append(f"Exceptions: {', '.join(exceptions[:3])}")

    return ParsedTestOutput(
        exit_code=exit_code,
        passed=passed,
        total_tests=total_tests,
        failed_tests=tuple(failed),
        error_locations=tuple(locations),
        exception_types=tuple(exceptions),
        short_diagnostics=tuple(short_diag),
        raw_output_digest=digest,
        runner=runner,
        tests_collected=tests_collected,
        tests_executed=tests_executed,
        tests_passed=tests_passed,
        tests_failed=tests_failed,
        tests_skipped=tests_skipped,
    )
