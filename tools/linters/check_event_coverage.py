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

_TOOLS = Path(__file__).resolve().parent.parent
_COMMON = _TOOLS / "common"
for _p in (_COMMON, _TOOLS):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from repo_paths import repo_root

ROOT = repo_root()
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


def _module_string_dicts(tree: ast.Module) -> dict[str, list[str]]:
    """Module-level `name = {...}` whose values are string literals.

    `registry/lifecycle.py` holds every `Plugin*` kind in an `_EVENTS`
    state->kind table and emits `emit_kind(_EVENTS[state], ...)`. Without
    this, all seven look unproduced and the producer axis silently
    under-reports the very kinds a plugin fault depends on.
    """
    tables: dict[str, list[str]] = {}
    for stmt in tree.body:
        if not (isinstance(stmt, ast.Assign) and len(stmt.targets) == 1
                and isinstance(stmt.targets[0], ast.Name)
                and isinstance(stmt.value, ast.Dict)):
            continue
        values = [v.value for v in stmt.value.values
                  if isinstance(v, ast.Constant) and isinstance(v.value, str)]
        if values:
            tables[stmt.targets[0].id] = values
    return tables


def _string_values_of(node: ast.AST | None, local_assigns: dict[str, list[str]],
                      module_dicts: dict[str, list[str]] | None = None) -> list[str]:
    """Resolve a kind-argument AST node to its possible literal string(s)."""
    module_dicts = module_dicts or {}
    if node is None:
        return []
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return [node.value]
    if isinstance(node, ast.Name):
        return list(local_assigns.get(node.id, []))
    if isinstance(node, ast.IfExp):
        return (_string_values_of(node.body, local_assigns, module_dicts)
                + _string_values_of(node.orelse, local_assigns, module_dicts))
    # `_EVENTS[state]` -- a lookup into a module-level kind table. The
    # subscript is not statically resolvable, so every value in the table is
    # a possible kind; over-reporting here is caught by the staleness check
    # in `check()`, whereas under-reporting hides a missing producer.
    if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name):
        return list(module_dicts.get(node.value.id, []))
    return []


def _scan_file(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found: set[str] = set()
    module_dicts = _module_string_dicts(tree)

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
                # `_emit` is not one signature. The kernel's is
                # `_emit(emitted, request, kind, reason, ...)`;
                # `delegation.py`'s is `_emit(kind, payload, request, ...)`.
                # Pinning this to `args[2]` read `request` at the delegation
                # sites and lost `ChildSpawned`/`ChildReturned` entirely.
                # Read both kind positions -- and only those: the kernel's
                # `args[3]` is a reason code (`"lease_leak"`, `"issued"`),
                # so scanning every argument would report reasons as kinds.
                for index in (0, 2):
                    if len(call.args) > index:
                        found.update(
                            _string_values_of(call.args[index], local_assigns, module_dicts))

            if kind_arg is not None:
                found.update(_string_values_of(kind_arg, local_assigns, module_dicts))

    return found


def emitting_call_sites() -> set[str]:
    """Kinds some production call site actually emits. AST only.

    Deliberately *excludes* `PRIVILEGED_KIND_OWNERS`: that table records what
    a role is permitted to write, not what anything writes. Unioning it in --
    as `production_emittable_kinds()` must, to preserve the "can legally
    write" direction -- would let a kind satisfy the producer check by being
    added to an authority table, with no emitter anywhere.
    """
    found: set[str] = set()
    for scan_root in SCAN_ROOTS:
        for path in sorted(scan_root.rglob("*.py")):
            if _is_excluded(path) or "/test" in str(path):
                continue
            found |= _scan_file(path)
    return found


def production_emittable_kinds() -> set[str]:
    """Kinds actually *or legally* writable by `LedgerEmitter` today.

    Actual call sites plus the writer-authority table. This is the right set
    for the "nothing emitted is uncatalogued" direction; use
    `emitting_call_sites()` for anything asking whether a producer exists.
    """
    sys.path.insert(0, str(ROOT))
    from vanguard.packages.runtime.ledger_emitter import PRIVILEGED_KIND_OWNERS

    return emitting_call_sites() | set(PRIVILEGED_KIND_OWNERS)


#: Writable kinds with no producer, each an explicit and reviewable decision
#: rather than an accident. This is the *producer* axis; it is not the same
#: question as `test_event_coverage.UNFOLDED_ALLOWLIST`, which records kinds
#: the *reducer* deliberately does not fold. A kind may legitimately appear
#: in both, in either, or in neither.
#:
#: Removing an entry is the unit of progress: `check()` fails if a kind here
#: acquires a producer, so an entry cannot outlive the gap it documents.
UNPRODUCED_ALLOWLIST = frozenset({
    # Outer-run lifecycle owned by `runtime/service/` (ADR-0062), which
    # publishes these directly and never routes through `LedgerEmitter`.
    # This harness's durable unit is the episode (`EpisodeStarted` /
    # `EpisodeCompleted`), so a ledger-side twin would be a second,
    # contradictory run lifecycle.
    "RunStarted",
    "RunCompleted",
    "Heartbeat",               # Liveness lease; a supervisor's fact, not a session's
    "CheckpointCreated",       # Service emits `CheckpointRecorded` in its own vocabulary
    "ClaimRecorded",           # Legacy synonym; `EvidenceClaimProduced` is the live kind
    # Phase-2: reduced and projected, but no subsystem computes the signal yet.
    "ActivationChanged",
    "InvalidationChecked",
    "ProgressAssessed",
    "ConflictDetected",
    # No planner/reflection surface exists on the single-worker EpisodeEngine
    # path. Revisit under MS-SPECIALIST / MS-META, not here.
    "ProposalRejected",
    "ReflectionProduced",
    # TODO(kernel-audit): real gaps, previously masked by the
    # `PRIVILEGED_KIND_OWNERS` union. `kernel/grants.py:224` documents
    # `revoke()` as "it emits ... a revocation leaving no event is
    # indistinguishable from a grant that was never issued" -- and no caller
    # emits. Closing these is TCB work under its own LOC budget.
    "CapabilityRevoked",
    "CapabilityAttenuated",
    "BudgetExhausted",
    "AuthorizationRequested",
    "ApprovalResolved",
    # Scheduled producers -- see the plan's Waves 2-4. Each entry is deleted
    # by the wave that implements it.
    "GoalDeclared",
    "TurnStarted",
    "ContextCompacted",
    "EffectPreviewed",
    "ObservationProduced",
})


def check() -> list[str]:
    sys.path.insert(0, str(ROOT))
    from vanguard.packages.domain.ledger.events import EVENT_KINDS

    from vanguard.packages.domain.ledger.events import WRITABLE_KINDS

    emittable = production_emittable_kinds()
    errors = []

    missing = sorted(emittable - EVENT_KINDS)
    if missing:
        errors.append(
            "kinds production LedgerEmitter can write but the canonical "
            f"catalog (domain/ledger/events.EVENT_KINDS) does not carry: {missing}"
        )

    # The other direction. Without it a kind can be catalogued, reduced,
    # projected and rendered by a client while nothing ever writes it -- the
    # reader looks correct and the feature is simply invisible. Asserted
    # against `emitting_call_sites()`, never `production_emittable_kinds()`:
    # the latter unions the writer-authority table, so a kind could satisfy
    # this check by being granted an owner with no emitter anywhere.
    sites = emitting_call_sites()
    unproduced = sorted(WRITABLE_KINDS - sites - UNPRODUCED_ALLOWLIST)
    if unproduced:
        errors.append(
            "writable kinds with no producer and no UNPRODUCED_ALLOWLIST "
            f"entry: {unproduced}"
        )

    stale = sorted(UNPRODUCED_ALLOWLIST & sites)
    if stale:
        errors.append(
            "UNPRODUCED_ALLOWLIST entries that now have a producer -- delete "
            f"them so the allowlist cannot become a graveyard: {stale}"
        )

    unknown = sorted(UNPRODUCED_ALLOWLIST - WRITABLE_KINDS)
    if unknown:
        errors.append(
            "UNPRODUCED_ALLOWLIST entries that are not writable kinds "
            f"(typo, or a kind that was removed): {unknown}"
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
