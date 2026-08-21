#!/usr/bin/env python3
"""E-COV: every event kind the production `LedgerEmitter` can legally write
is present in the canonical event catalog (SPEC §1.2, ADR-0076 §6).

"Production-emittable" is the union of:

1. Every kind literal that is actually the argument of an `Event(kind=...)`
   construction, a `.emit_kind(...)` call, or the kernel's `_emit(...)`
   helper, anywhere under `kernel/`, `agency/`, `runtime/` -- a static AST
   walk, not a hand-maintained site registry, so it cannot silently rot the
   way the deleted `layer0.events.taxonomy.EMITTER_SITES` did.
2. Every kind in `PRIVILEGED_KIND_OWNERS` (`runtime/ledger_emitter.py`) --
   the writer-authority table that says a role is *permitted* to emit a
   kind, independent of whether a call site already exists for it yet
   ("can legally write", the Tech Lead's own words for the M-2 blocker).

`runtime/service/` is deliberately out of scope: it is the CLI "vg.4"
streaming wire protocol (ADR-0062), a distinct bounded context from the
ledger. Its event-shaped dicts (e.g. `"RunFailed"`) are never routed through
`LedgerEmitter` and must NOT be catalogued as ledger event kinds -- see
`test/kernel/test_event_kinds_writer.py::test_unknown_kind_is_not_in_the_writer_catalog`.
It is excluded structurally (no `Event(...)`/`.emit_kind(...)`/`._emit(...)`
call sites live there) rather than by an ad hoc path skip.

This does not assert equality with `EVENT_KINDS`: the catalog also carries
VG-04-normative kinds nothing emits yet (`domain/ledger/events.py`
`_V4_ONLY_KINDS`), and that is intentional -- nothing here authorises
deleting a locked kind. It asserts the one direction that matters:
everything production can actually or legally write today is representable,
so `LedgerEmitter` can never write an event the reducer would silently
misfile into `unknown_events`.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKAGES = ROOT / "vanguard" / "packages"

SCAN_ROOTS = (
    PACKAGES / "kernel",
    PACKAGES / "agency",
    PACKAGES / "runtime",
)

# CLI streaming wire protocol (ADR-0062) -- a distinct bounded context from
# the ledger, never routed through `LedgerEmitter`.
EXCLUDE_DIRS = (PACKAGES / "runtime" / "service",)


def _is_excluded(path: Path) -> bool:
    return any(excluded == path or excluded in path.parents for excluded in EXCLUDE_DIRS)


def _string_values_of(node: ast.AST | None, local_assigns: dict[str, list[str]]) -> list[str]:
    """Resolve a kind-argument AST node to its possible literal string(s)."""
    if node is None:
        return []
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return [node.value]
    if isinstance(node, ast.Name):
        return list(local_assigns.get(node.id, []))
    if isinstance(node, ast.IfExp):
        return _string_values_of(node.body, local_assigns) + _string_values_of(node.orelse, local_assigns)
    return []


def _scan_file(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found: set[str] = set()

    for scope in ast.walk(tree):
        if not isinstance(scope, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Module)):
            continue
        # Local string-literal assignments within this scope only, so a kind
        # threaded through a variable (e.g. `terminal_event_kind = "X" if
        # ... else "Y"`) still resolves without cross-function guessing.
        local_assigns: dict[str, list[str]] = {}
        for stmt in ast.walk(scope):
            if (isinstance(stmt, ast.Assign) and len(stmt.targets) == 1
                    and isinstance(stmt.targets[0], ast.Name)):
                values = _string_values_of(stmt.value, {})
                if values:
                    local_assigns.setdefault(stmt.targets[0].id, []).extend(values)

        for call in ast.walk(scope):
            if not isinstance(call, ast.Call):
                continue
            callee = call.func
            kind_arg: ast.AST | None = None

            if isinstance(callee, ast.Name) and callee.id == "Event":
                for kw in call.keywords:
                    if kw.arg == "kind":
                        kind_arg = kw.value
            elif isinstance(callee, ast.Attribute) and callee.attr == "emit_kind":
                if call.args:
                    kind_arg = call.args[0]
            elif isinstance(callee, ast.Attribute) and callee.attr == "_emit":
                if len(call.args) >= 3:
                    kind_arg = call.args[2]

            if kind_arg is not None:
                found.update(_string_values_of(kind_arg, local_assigns))

    return found


def production_emittable_kinds() -> set[str]:
    """Kinds actually or legally writable by `LedgerEmitter` today."""
    sys.path.insert(0, str(ROOT))
    from vanguard.packages.runtime.ledger_emitter import PRIVILEGED_KIND_OWNERS

    found: set[str] = set(PRIVILEGED_KIND_OWNERS)
    for scan_root in SCAN_ROOTS:
        for path in sorted(scan_root.rglob("*.py")):
            if _is_excluded(path) or "/test" in str(path):
                continue
            found |= _scan_file(path)
    return found


def check() -> list[str]:
    sys.path.insert(0, str(ROOT))
    from vanguard.packages.domain.ledger.events import EVENT_KINDS

    emittable = production_emittable_kinds()
    missing = sorted(emittable - EVENT_KINDS)
    errors = []
    if missing:
        errors.append(
            "kinds production LedgerEmitter can write but the canonical "
            f"catalog (domain/ledger/events.EVENT_KINDS) does not carry: {missing}"
        )
    return errors


def main() -> int:
    errors = check()
    if errors:
        print("E-COV FAIL:")
        for err in errors:
            print(f"  - {err}")
        return 1
    print("E-COV PASS: every production-emittable event kind is in the canonical catalog")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
