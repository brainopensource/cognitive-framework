"""M-6 spawn adapter. Lives in runtime/, NOT kernel/.
The kernel authorises a descriptor; only this adapter knows it means 'child'."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable, Mapping, Optional
from .attenuate import AgentContext, attenuate, AttenuationError

OCCURRED, DID_NOT_OCCUR, UNDETERMINABLE = "OCCURRED", "DID_NOT_OCCUR", "UNDETERMINABLE"

@dataclass(frozen=True, slots=True)
class Receipt:
    outcome: str
    child_id: Optional[str] = None
    cost: Mapping[str, int] | None = None
    detail: str = ""

class SpawnAdapter:
    def __init__(self, ledger, engine, probe_child: Callable[[str], str]) -> None:
        self._ledger, self._engine, self._probe = ledger, engine, probe_child

    def on_authorised_intent(self, intent) -> Receipt:
        if intent.verb != "agent.spawn":
            return Receipt("failed", detail="not_mine")

        # RECOVERY GUARD — a settled physical effect is never repeated.
        if prior := self._ledger.settled(intent.idempotency_key):
            return prior

        try:
            child = attenuate(intent.parent_ctx, intent.requested_authority,
                              intent.budget_share, intent.child_id)
        except AttenuationError as e:
            return Receipt("denied", detail=str(e))

        self._ledger.emit("ChildSpawned", parent=intent.parent_ctx.episode_id,
                          child=child.episode_id, authority=sorted(child.authority),
                          depth=child.depth)
        result = self._engine.run(child)          # SAME engine. sequential (I-11).
        self._ledger.emit("ChildReturned", child=child.episode_id,
                          outcome=result.terminal, cost=result.cost)
        r = Receipt(result.terminal, child.episode_id, result.cost)
        self._ledger.settle(intent.idempotency_key, r)
        return r

    def reconcile_cold(self, intent) -> str:
        """Crash between S8a durable intent and child creation."""
        state = self._probe(intent.child_id)
        if state == "FOUND":     return OCCURRED         # adopt existing child
        if state == "ABSENT":    return DID_NOT_OCCUR    # safe to retry
        return UNDETERMINABLE    # F-22: fail closed. never guess, never retry.
