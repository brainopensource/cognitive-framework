"""EVO-02: `Runtime.execute_harness` stays retired from production code.

Owning contract: VANGUARD_090_BACKEND_AUDIT_AND_EVOLUTION_PLAN.md EVO-02.

`RuntimeBootstrap.build()` is the sole concrete-adapter construction
authority (`ADR-0089 §Decision 2`). `ApplicationService`, the CLI, and the
service daemon all call `Runtime.execute_profiled`, which routes through
`RuntimeBootstrap`; none of them call `Runtime.execute_harness` (the
pre-`RuntimeBootstrap` legacy entrypoint) directly. This guard keeps it that
way: a new caller of `execute_harness` under `vanguard/` is exactly the
regression EVO-02 exists to prevent.

`execute_harness` itself is not deleted -- falsifier coverage (the M7
topology suite) deliberately exercises its `sandbox_mode="host-dev"` escape
hatch, and that suite's evidence bundle pins the test file's digest, so
migrating it is a change to signed evidence, not a refactor. `test/` is
exempt from this guard for exactly that reason.
"""

from __future__ import annotations

import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCAN_ROOT = ROOT / "vanguard"
_SKIP_DIRS = {".git", "__pycache__", ".venv", "node_modules"}

#: The method's own definition and its self-referential docstring/comments
#: are not a call to it.
_EXEMPT_FILE = ROOT / "vanguard/packages/runtime/root.py"


def _calls_execute_harness(path: Path) -> bool:
    if path == _EXEMPT_FILE:
        return False
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError:
        return False
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr == "execute_harness":
            return True
    return False


class LegacyBootstrapStaysOutOfProduction(unittest.TestCase):
    def test_no_production_module_calls_execute_harness(self) -> None:
        offenders = []
        for path in sorted(SCAN_ROOT.rglob("*.py")):
            if any(part in _SKIP_DIRS for part in path.parts):
                continue
            if _calls_execute_harness(path):
                offenders.append(str(path.relative_to(ROOT)))
        self.assertEqual(
            offenders, [],
            "found a production caller of the retired Runtime.execute_harness "
            "-- use Runtime.execute_profiled (RuntimeBootstrap) instead, or "
            "justify the exception here and in root.py's docstring",
        )

    def test_execute_profiled_still_exists_as_the_replacement(self) -> None:
        from vanguard.packages.runtime.root import Runtime
        self.assertTrue(hasattr(Runtime, "execute_profiled"))
        self.assertTrue(hasattr(Runtime, "execute_harness"))


if __name__ == "__main__":
    unittest.main()
