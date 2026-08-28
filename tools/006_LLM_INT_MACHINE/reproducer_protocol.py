"""Gated Dual-Loop Reproducer Protocol for 006_LLM_INT_MACHINE."""

from __future__ import annotations
from enum import Enum
from dataclasses import dataclass
from pathlib import Path

try:
    from .tools import ToolWorkspace
except ImportError:
    from tools import ToolWorkspace


class ReproducerPhase(str, Enum):
    LOCALIZE = "1_LOCALIZE"
    REPRODUCE_FAILS = "2_REPRODUCE_FAILS"
    PATCH_AND_PASS = "3_PATCH_AND_PASS"
    FULL_REGRESSION = "4_FULL_REGRESSION"
    COMPLETE = "5_COMPLETE"


@dataclass
class ReproducerState:
    phase: ReproducerPhase = ReproducerPhase.LOCALIZE
    repro_file_created: bool = False
    repro_confirmed_failing: bool = False
    repro_confirmed_passing: bool = False
    full_tests_passed: bool = False
    repro_path: str = "test_reproduce_bug.py"


class ReproducerManager:
    def __init__(self, workspace: ToolWorkspace, enabled: bool = True) -> None:
        self.workspace = workspace
        self.enabled = enabled
        self.state = ReproducerState()

    def check_repro_file(self) -> bool:
        target = self.workspace.root / self.state.repro_path
        exists = target.is_file()
        self.state.repro_file_created = exists
        return exists

    def run_reproducer(self) -> tuple[bool, str]:
        if not self.check_repro_file():
            return False, f"Reproducer file '{self.state.repro_path}' not found."
        
        cmd = f"python3 {self.state.repro_path}"
        res = self.workspace.proc_exec(cmd)
        passed = (res.ok)
        
        if self.state.phase == ReproducerPhase.REPRODUCE_FAILS:
            if not passed:
                self.state.repro_confirmed_failing = True
                self.state.phase = ReproducerPhase.PATCH_AND_PASS
                return True, f"VALID REPRODUCER: '{self.state.repro_path}' failed as expected on unpatched code.\nYou may now patch the codebase."
            else:
                return False, f"INVALID REPRODUCER: '{self.state.repro_path}' passed on unpatched code! It must reproduce the failure before you patch."

        elif self.state.phase == ReproducerPhase.PATCH_AND_PASS:
            if passed:
                self.state.repro_confirmed_passing = True
                self.state.phase = ReproducerPhase.FULL_REGRESSION
                return True, f"SUCCESS: '{self.state.repro_path}' now PASSES! Now run the full test suite to check for regressions."
            else:
                return False, f"STILL FAILING: '{self.state.repro_path}' still fails after patch.\n{res.output}"

        return passed, res.output

    def get_phase_instructions(self) -> str:
        if not self.enabled:
            return ""
        
        if self.state.phase == ReproducerPhase.LOCALIZE:
            return "Current Goal: Locate bug and write a minimal 'test_reproduce_bug.py' reproducing the issue."
        elif self.state.phase == ReproducerPhase.REPRODUCE_FAILS:
            return "Current Goal: Run 'python3 test_reproduce_bug.py' to confirm it FAILS on the current broken code."
        elif self.state.phase == ReproducerPhase.PATCH_AND_PASS:
            return "Current Goal: Apply surgical patch to fix the bug, then run 'python3 test_reproduce_bug.py' until it PASSES."
        elif self.state.phase == ReproducerPhase.FULL_REGRESSION:
            return "Current Goal: Run the full test suite to verify no regressions exist, then finalize."
        return "Complete."
