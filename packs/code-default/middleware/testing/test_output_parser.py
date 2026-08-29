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

    # total tests and passed flag
    total_tests = 0
    summary_match = _SUMMARY_PATTERN.search(output)
    if summary_match:
        total_tests = int(summary_match.group(1))

    passed = (exit_code == 0) and not failed and ("FAILED" not in output) and ("ERROR" not in output or "Ran" not in output)
    if "OK" in output and "Ran" in output and not failed:
        passed = True

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
    )
