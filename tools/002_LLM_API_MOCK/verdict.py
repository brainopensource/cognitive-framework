"""Honest pass/fail and evidence labels for LAM gym and lab runners."""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Any

_BUG_COMMENT = re.compile(r"\bBug\s+\d+\b", re.IGNORECASE)
_LEAK_NAMES = ("oracle", "preregistration.json", "prompt.txt", "datalog_solution")


_RUNNER = r"""
import os, sys, unittest
from pathlib import Path
root = Path(".").resolve()
found = 0
errors = 0
for path in sorted(root.rglob("test*.py")):
    if not path.is_file():
        continue
    ns = {"__name__": path.stem, "__file__": str(path)}
    exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"), ns)
    for name, obj in list(ns.items()):
        if name.startswith("test_") and callable(obj):
            found += 1
            try:
                obj()
            except Exception:
                errors += 1
        elif isinstance(obj, type) and issubclass(obj, unittest.TestCase) and obj is not unittest.TestCase:
            result = unittest.TextTestRunner(stream=open(os.devnull, "w")).run(
                unittest.defaultTestLoader.loadTestsFromTestCase(obj)
            )
            found += result.testsRun
            errors += len(result.failures) + len(result.errors)
sys.exit(0 if found > 0 and errors == 0 else 1)
"""


def pytest_passed(workspace: Path) -> bool:
    """Run workspace tests in an isolated interpreter (workspace PYTHONPATH only)."""
    import subprocess

    env = dict(os.environ)
    env["PYTHONPATH"] = str(workspace)
    completed = subprocess.run(
        [sys.executable, "-c", _RUNNER],
        cwd=workspace,
        capture_output=True,
        text=True,
        timeout=60,
        env=env,
    )
    return completed.returncode == 0


def evidence_label(backend: str) -> str:
    name = (backend or "").lower()
    if name.startswith("lam") or name == "cassette":
        return "lam-replay"
    if "ollama" in name:
        return "live-ollama"
    if "openrouter" in name or name == "live":
        return "live-openrouter"
    if name in {"lab", "vanguard", "execute_harness"}:
        return "lab-execute-harness"
    return "unknown"


def workspace_verdict(workspace: Path, *, backend: str, llm_calls: int) -> dict[str, Any]:
    del llm_calls  # calls > 1 is not a pass
    passed = pytest_passed(workspace)
    return {
        "passed": passed,
        "evidence_label": evidence_label(backend),
    }


def leak_paths(workspace: Path) -> list[str]:
    hits: list[str] = []
    for path in workspace.rglob("*"):
        rel = str(path.relative_to(workspace)).replace("\\", "/")
        lowered = rel.lower()
        if any(token in lowered for token in _LEAK_NAMES):
            hits.append(rel)
            continue
        if path.is_file():
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeError):
                continue
            if _BUG_COMMENT.search(text) or "FIXME" in text:
                hits.append(rel)
    return hits
