"""EVO-05: one logical domain event model, not a business-object duplicate.

Owning contract: VANGUARD_090_BACKEND_AUDIT_AND_EVOLUTION_PLAN.md EVO-05.

`domain/ledger/events.py::EventEnvelope` is the one event representation
every reducer, store, session, and kernel emission path constructs and
consumes. `domain/wire/types_gen.py` is auto-generated from
`schemas/mhf/event_envelope*.schema.json` (`tools/codegen/generate_types.py`)
and happens to also define an `EventEnvelope`/`EventEnvelopeV2` pair --
those schemas are the load-bearing wire contract (referenced by evidence
bundles and cross-language readers) and stay, but the generated Python
dataclasses they produce are not meant to be an alternative business
object. As of this test, nothing in the tree imports them; this is the
guard that keeps it that way; a future import of either name is exactly
the "duplicated business semantics" EVO-05 exists to prevent, and should
be resolved by using `domain.ledger.events.EventEnvelope` instead, or by
justifying and documenting the exception here.
"""

from __future__ import annotations

import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCAN_ROOTS = (ROOT / "vanguard", ROOT / "test", ROOT / "tools", ROOT / "lab", ROOT / "benchmarks")
_SKIP_DIRS = {".git", "__pycache__", ".venv", "node_modules"}
_BANNED_NAMES = frozenset({"EventEnvelope", "EventEnvelopeV2"})
_GENERATED_MODULE_SUFFIX = "wire.types_gen"

#: The generated module itself declares these names -- that is not an
#: import of them, and is exempt by construction.
_EXEMPT_FILE = ROOT / "vanguard/packages/domain/wire/types_gen.py"


def _imports_banned_wire_envelope(path: Path) -> list[str]:
    if path == _EXEMPT_FILE:
        return []
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError:
        return []
    hits: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module.endswith(_GENERATED_MODULE_SUFFIX) or module.endswith("wire.types_gen"):
                for alias in node.names:
                    if alias.name in _BANNED_NAMES:
                        hits.append(f"from {module} import {alias.name}")
        elif isinstance(node, ast.Attribute) and node.attr in _BANNED_NAMES:
            # `types_gen.EventEnvelope` accessed via attribute rather than
            # a `from`-import -- catches the same drift by a different route.
            value = node.value
            if isinstance(value, ast.Name) and "types_gen" in value.id:
                hits.append(f"{value.id}.{node.attr}")
    return hits


class OnlyOneEventEnvelopeRepresentationIsUsed(unittest.TestCase):
    def test_no_module_imports_the_generated_event_envelope_twins(self) -> None:
        offenders: dict[str, list[str]] = {}
        for scan_root in SCAN_ROOTS:
            if not scan_root.is_dir():
                continue
            for path in sorted(scan_root.rglob("*.py")):
                if any(part in _SKIP_DIRS for part in path.parts):
                    continue
                hits = _imports_banned_wire_envelope(path)
                if hits:
                    offenders[str(path.relative_to(ROOT))] = hits
        self.assertEqual(
            offenders, {},
            "found a live import of the generated (unused-by-design) "
            "EventEnvelope/EventEnvelopeV2 twins -- either switch to "
            "domain.ledger.events.EventEnvelope, or update this test's "
            "docstring and exemption list with the justification",
        )

    def test_the_generated_twins_still_exist_in_types_gen(self) -> None:
        """If codegen ever drops these, this guard becomes vacuous -- catch
        that so the test doesn't silently stop meaning anything."""
        text = _EXEMPT_FILE.read_text(encoding="utf-8")
        self.assertIn("class EventEnvelope:", text)
        self.assertIn("class EventEnvelopeV2:", text)


if __name__ == "__main__":
    unittest.main()
