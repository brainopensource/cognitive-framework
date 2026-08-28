"""ADR-0090 reducer fold for mediated delegation.

Removes ChildSpawned/ChildReturned from UNFOLDED_ALLOWLIST. They are NOT
advisory markers: they are material FSM transitions and must fold, per
001_alfa sec.3 (via 005 Epsilon) -- every material transition catalogued,
emitted, and reduced.

Reducer contract (ADR-0090 constraint 4):
  ChildSpawned            -> child record `open`
  + ChildReturned         -> child record `closed`
  ChildSpawned alone      -> stays `open`, reconciled by the cold path.
                             NEVER assumed complete.

Purity: zero I/O, zero clocks, zero randomness. Same law as reduce_event.
"""
from __future__ import annotations
from dataclasses import dataclass, replace
from typing import Any, Mapping

OPEN, CLOSED = "open", "closed"

class ChildReducerError(Exception): ...

@dataclass(frozen=True, slots=True)
class ChildRecord:
    child_episode_id: str
    parent_episode_id: str
    authority: tuple[str, ...]
    depth: int
    lineage: tuple[str, ...]
    settled_intent_key: str
    status: str = OPEN
    outcome: str | None = None
    terminal: str | None = None
    cost: Mapping[str, Any] | None = None

    @property
    def reconcilable(self) -> bool:
        """An open record is what the cold path must reconcile."""
        return self.status == OPEN

def fold_child_event(children: Mapping[str, ChildRecord],
                     payload: Mapping[str, Any]) -> dict[str, ChildRecord]:
    out = dict(children)
    kind = payload.get("kind")

    if kind == "ChildSpawned":
        cid = payload["child_episode_id"]
        if cid in out:
            raise ChildReducerError(f"duplicate ChildSpawned for {cid!r}")
        # monotonicity is recomputable: child authority must be within parent's
        out[cid] = ChildRecord(
            child_episode_id=cid,
            parent_episode_id=payload["parent_episode_id"],
            authority=tuple(payload["authority"]),
            depth=int(payload["depth"]),
            lineage=tuple(payload["lineage"]),
            settled_intent_key=payload["settled_intent_key"])
        return out

    if kind == "ChildReturned":
        cid = payload["child_episode_id"]
        rec = out.get(cid)
        if rec is None:
            raise ChildReducerError(f"ChildReturned without ChildSpawned for {cid!r}")
        if rec.status == CLOSED:
            raise ChildReducerError(f"child {cid!r} returned twice")
        if rec.settled_intent_key != payload["settled_intent_key"]:
            raise ChildReducerError(f"intent key mismatch for {cid!r}")
        out[cid] = replace(rec, status=CLOSED, outcome=payload["outcome"],
                           terminal=payload["terminal"], cost=payload["cost"])
        return out

    return out

def open_children(children: Mapping[str, ChildRecord]) -> tuple[ChildRecord, ...]:
    """Cold-path input: every child needing reconciliation."""
    return tuple(c for c in children.values() if c.reconcilable)

def parent_cost(children: Mapping[str, ChildRecord]) -> dict[str, int]:
    """Cost conservation (ADR-0090 constraint 5): child spend IS parent spend."""
    total: dict[str, int] = {}
    for c in children.values():
        for k, v in (c.cost or {}).items():
            if isinstance(v, int):
                total[k] = total.get(k, 0) + v
    return total
