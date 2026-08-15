"""`REQ-EXEC-001` — what `agency/` is forbidden to name or reach.

Two separate claims, both structural rather than behavioural:

1. **No cognitive identifiers.** `plan`, `debug`, `reflect` and `architect`
   are not loop concepts. Naming a code path after a cognitive posture invites
   a second dispatch path shaped like a mood, and the prototype's dead
   injection defence is what that looks like after a year (`VG-03 §6.5`).
2. **No evaluator reach.** `ICD §3`: evaluation is exterior and `agency`
   cannot request its own. `tools/check_boundaries.py` enforces the import
   direction repository-wide; this asserts it at the package, where a defect
   would land first.

Both scan the source rather than the runtime, because an unexecuted branch is
still a path.
"""

from __future__ import annotations

import ast
import unittest
from pathlib import Path

FORBIDDEN = ("plan", "debug", "reflect", "architect")

AGENCY = Path(__file__).resolve().parents[2] / "vanguard" / "packages" / "agency"


def agency_sources() -> list[Path]:
    return sorted(p for p in AGENCY.rglob("*.py") if "__pycache__" not in p.parts)


def identifiers(tree: ast.AST) -> set[str]:
    """Every name this module defines, binds or reads — comments excluded."""
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            found.add(node.id)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            found.add(node.name)
        elif isinstance(node, ast.Attribute):
            found.add(node.attr)
        elif isinstance(node, ast.arg):
            found.add(node.arg)
        elif isinstance(node, ast.alias):
            found.add((node.asname or node.name).split(".")[-1])
    return found


class Identifiers(unittest.TestCase):
    def test_agency_has_source_to_lint(self) -> None:
        """A lint over an empty directory passes for the wrong reason."""
        self.assertTrue(agency_sources())

    def test_no_cognitive_identifiers_in_agency(self) -> None:
        offences: list[str] = []
        for source in agency_sources():
            tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
            for name in sorted(identifiers(tree)):
                lowered = name.lower()
                if any(word in lowered for word in FORBIDDEN):
                    offences.append(f"{source.name}: {name}")
        self.assertEqual(offences, [])

    def test_the_lint_would_catch_one(self) -> None:
        """`ICD §7.5`: a gate that cannot fail is not a gate."""
        tree = ast.parse("def reflect_on_turn(state):\n    return state\n")
        names = {n.lower() for n in identifiers(tree)}
        self.assertTrue(any(any(w in n for w in FORBIDDEN) for n in names))


class Reach(unittest.TestCase):
    def test_agency_imports_no_evaluator_and_no_adapter(self) -> None:
        """`ICD §3`, `ICD §7.4`. `agency` may import `domain`, `ports` and
        `kernel` — nothing else in the tree."""
        offences: list[str] = []
        for source in agency_sources():
            tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
            for node in ast.walk(tree):
                specs: list[str] = []
                if isinstance(node, ast.ImportFrom):
                    specs.append(node.module or "")
                    specs.extend(f"{node.module or ''}.{a.name}" for a in node.names)
                elif isinstance(node, ast.Import):
                    specs.extend(alias.name for alias in node.names)
                for spec in specs:
                    lowered = spec.lower().replace("_", "-")
                    if "evaluator" in lowered or "adapters" in lowered:
                        offences.append(f"{source.name}: {spec}")
                        continue
                    for part in spec.split("."):
                        if part in {"runtime", "spike", "slice", "lab"}:
                            offences.append(f"{source.name}: {spec}")
        self.assertEqual(offences, [])


if __name__ == "__main__":
    unittest.main()
