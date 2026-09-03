"""Multi-Stage Adaptive Verification Cortex for CHIMERA.

Scales verification depth according to patch risk and uncertainty:
V0: Syntax & AST validation
V1: Targeted test execution
V2: Full test suite verification
V3: Static checks & Rubric verification
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re
import time
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Tuple

from .blackboard import VerificationRecord
from .symbolic import SymbolicCortex


class VerificationLevel(str, Enum):
    V0_SYNTAX = "V0_SYNTAX"
    V1_TARGETED = "V1_TARGETED"
    V2_FULL_SUITE = "V2_FULL_SUITE"
    V3_STATIC = "V3_STATIC"
    V4_RUBRIC = "V4_RUBRIC"


@dataclass(frozen=True, slots=True)
class PatchRiskAssessment:
    risk_level: str  # "LOW" | "MEDIUM" | "HIGH"
    risk_score: float  # [0.0, 1.0]
    required_level: VerificationLevel
    reasons: tuple[str, ...]


class VerificationCortex:
    """Adaptive Verification Planner and Output Parser."""

    @classmethod
    def assess_patch_risk(
        cls,
        changed_files: Sequence[str],
        total_loc_changed: int,
        is_greenfield: bool = False,
    ) -> PatchRiskAssessment:
        """Compute patch risk score and determine minimum required verification level."""
        reasons: list[str] = []
        score = 0.1

        if is_greenfield:
            score += 0.3
            reasons.append("Greenfield project creation")

        if len(changed_files) > 2:
            score += 0.3
            reasons.append(f"Multi-file modification ({len(changed_files)} files)")

        if total_loc_changed > 100:
            score += 0.3
            reasons.append(f"Large diff size ({total_loc_changed} LOC)")
        elif total_loc_changed > 30:
            score += 0.15
            reasons.append(f"Moderate diff size ({total_loc_changed} LOC)")

        score = min(1.0, score)
        if score >= 0.6:
            risk_level = "HIGH"
            req_lvl = VerificationLevel.V2_FULL_SUITE
        elif score >= 0.3:
            risk_level = "MEDIUM"
            req_lvl = VerificationLevel.V1_TARGETED
        else:
            risk_level = "LOW"
            req_lvl = VerificationLevel.V0_SYNTAX

        return PatchRiskAssessment(
            risk_level=risk_level,
            risk_score=round(score, 3),
            required_level=req_lvl,
            reasons=tuple(reasons),
        )

    @classmethod
    def parse_test_output(
        cls,
        output: str,
        exit_code: int,
        level: VerificationLevel = VerificationLevel.V2_FULL_SUITE,
    ) -> VerificationRecord:
        """Parse raw terminal test output across pytest, unittest, cargo test, and npm test."""
        executed = 0
        passed = 0
        failed: list[str] = []

        # 1. Unittest pattern: "Ran X tests in Ys\n\nOK" or "FAILED (failures=X, errors=Y)"
        unittest_m = re.search(r"Ran\s+(\d+)\s+tests?", output)
        if unittest_m:
            executed = int(unittest_m.group(1))
            if exit_code == 0 and "OK" in output:
                passed = executed
            else:
                fail_m = re.search(r"failures=(\d+)", output)
                err_m = re.search(r"errors=(\d+)", output)
                f_cnt = int(fail_m.group(1)) if fail_m else 0
                e_cnt = int(err_m.group(1)) if err_m else 0
                f_total = max(1, f_cnt + e_cnt)
                passed = max(0, executed - f_total)
                # Find test failure names
                for f_line in re.findall(r"(?:FAIL|ERROR):\s+([A-Za-z0-9_\.]+)", output):
                    failed.append(f_line)

        # 2. Pytest pattern: "X passed, Y failed" or "X passed in Ys"
        if executed == 0:
            pytest_pass = re.search(r"(\d+)\s+passed", output)
            pytest_fail = re.search(r"(\d+)\s+failed", output)
            if pytest_pass:
                p_cnt = int(pytest_pass.group(1))
                f_cnt = int(pytest_fail.group(1)) if pytest_fail else 0
                executed = p_cnt + f_cnt
                passed = p_cnt
                for f_line in re.findall(r"FAILED\s+([A-Za-z0-9_\.\:\/]+)", output):
                    failed.append(f_line)

        # 3. Cargo test pattern: "test result: ok. X passed; Y failed"
        if executed == 0:
            cargo_m = re.search(r"test result:\s+(\w+)\.\s+(\d+)\s+passed;\s+(\d+)\s+failed", output)
            if cargo_m:
                p_cnt = int(cargo_m.group(2))
                f_cnt = int(cargo_m.group(3))
                executed = p_cnt + f_cnt
                passed = p_cnt

        # Bare exit 0 is not evidence a test ran. Unknown counts stay 0 (T-06).
        # Non-zero exit without a parsed runner summary still records a failed command.
        if executed == 0 and exit_code != 0:
            executed = 1
            passed = 0
            failed.append("CommandFailed")

        return VerificationRecord(
            verification_id=f"ver_{int(time.time()*1000)}",
            level=level.value,
            exit_code=exit_code,
            executed_tests=executed,
            passed_tests=passed,
            failed_tests=tuple(failed),
            output_summary=output[:500],
        )

    @classmethod
    def get_test_command_for_workspace(
        cls,
        workspace_files: Sequence[str],
    ) -> str:
        """Infer best automated test command based on workspace files."""
        for f in workspace_files:
            if "Cargo.toml" in f:
                return "cargo test"
            if "package.json" in f:
                return "npm test"

        # Check Python test suites
        has_tests_dir = any("test/" in f or "tests/" in f for f in workspace_files)
        if has_tests_dir:
            return "python3 -m unittest discover -s test -t ."

        # Standalone test files
        test_py_files = [f for f in workspace_files if f.endswith(".py") and ("test" in f or "oracle" in f)]
        if test_py_files:
            return f"python3 {test_py_files[0]}"

        return "python3 -m unittest discover -s . -p '*test*.py'"
