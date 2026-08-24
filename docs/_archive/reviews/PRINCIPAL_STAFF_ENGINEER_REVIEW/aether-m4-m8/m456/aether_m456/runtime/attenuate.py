"""M-6 attenuation algebra. Pure, no I/O, no kernel dependency."""
from __future__ import annotations
from dataclasses import dataclass, replace
from typing import FrozenSet, Mapping

MAX_DEPTH = 4
BUDGET_KEYS = ("usd_micros", "tokens", "bytes", "millis", "turns", "spawns")

class AttenuationError(Exception): ...

@dataclass(frozen=True, slots=True)
class AgentContext:
    episode_id: str
    authority: FrozenSet[str]
    budget: Mapping[str, int]
    depth: int = 0
    lineage: tuple[str, ...] = ()

    def spend(self, k: str, n: int) -> "AgentContext":
        return replace(self, budget={**self.budget, k: self.budget[k] - n})

def attenuate(parent: AgentContext, req_authority: FrozenSet[str],
              share: Mapping[str, int], child_id: str) -> AgentContext:
    # 1. authority: request must already be within the parent hull.
    # Silent narrowing is rejected: a caller that asks for authority the
    # parent lacks has a bug, and quietly handing back a smaller set hides it.
    req = frozenset(req_authority)
    escaped = req - parent.authority
    if escaped:
        raise AttenuationError(f"requested authority outside parent hull: {sorted(escaped)}")
    authority = req & parent.authority

    # 2. budget: subtract from parent. Never mint.
    for k in share:
        if k not in BUDGET_KEYS:
            raise AttenuationError(f"unknown budget dimension {k!r}")
        if share[k] > parent.budget.get(k, 0):
            raise AttenuationError(f"child {k} exceeds parent remaining")

    # 3. depth / cycles / storms
    if parent.depth + 1 > MAX_DEPTH:
        raise AttenuationError("max delegation depth exceeded")
    if child_id in parent.lineage or child_id == parent.episode_id:
        raise AttenuationError("delegation cycle")
    if parent.budget.get("spawns", 0) <= 0:
        raise AttenuationError("spawn quota exhausted")

    return AgentContext(
        episode_id=child_id,
        authority=authority,
        budget=dict(share),
        depth=parent.depth + 1,
        lineage=parent.lineage + (parent.episode_id,),
    )
