"""ADR-0090 constraint 1: SpawnAdapter is the SOLE legal writer.

Merge into runtime/ledger_emitter.PRIVILEGED_KIND_OWNERS. Plugins, workers and
child episodes may PROPOSE delegation; they never append these envelopes.
Note 'orchestrator' is deliberately absent -- it owns no privileged kind.
"""
from __future__ import annotations
from typing import Mapping

ADR_0090_KIND_OWNERS: Mapping[str, frozenset[str]] = {
    "ChildSpawned":  frozenset({"spawn_adapter"}),
    "ChildReturned": frozenset({"spawn_adapter"}),
}

def assert_writer(kind: str, writer: str,
                  owners: Mapping[str, frozenset[str]]) -> None:
    allowed = owners.get(kind)
    if allowed is None:
        raise PermissionError(f"kind {kind!r} has no registered owner")
    if writer not in allowed:
        raise PermissionError(
            f"writer {writer!r} may not append {kind!r}; owners={sorted(allowed)}")
