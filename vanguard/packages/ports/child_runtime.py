"""Child runtime port -- the M-6 recursion seam (`ADR-0090`, `WP-A1`).

A spawn does not create an agent object. It creates a **bounded causal region**
that some runtime must actually execute. This port is the boundary between the
two: `delegation.py` decides *what a child is allowed to be*, and a
`ChildRuntimePort` decides *how it runs*. Neither knows the other's internals.

Three refusals are encoded structurally rather than documented:

* **A plan is decided before the child exists.** Every field of `ChildRunPlan`
  is already attenuated, already lowered, already reserved. There is no
  negotiation from inside the child, because the plan is frozen and the child
  never receives the parent's scope object to widen.
* **A result is a contract, not a conversation.** `ChildRunResult` admits
  scalars, digests and reference strings only. `__post_init__` rejects anything
  else, so a runner cannot hand back a live session, an open port, or a
  transcript -- a parent that receives a transcript has not delegated, it has
  inlined (`C-06`).
* **Absence is not a value.** A runner that cannot determine what happened
  returns `outcome="undeterminable"`, never a cheerful default. The synthetic
  success this port replaced is precisely what made M-6 unacceptable.

This module imports nothing from `runtime/` or `kernel/` -- Ports stays a leaf.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol, runtime_checkable

__all__ = [
    "CHILD_ADDITIVE_DIMENSIONS",
    "CHILD_OUTCOMES",
    "CHILD_STRUCTURAL_CEILINGS",
    "ChildContractError",
    "ChildRunPlan",
    "ChildRunResult",
    "ChildRuntimePort",
]

#: `C-05`. Mirrored from `runtime.delegation` deliberately: Ports may not
#: import Runtime, and a port that trusted the caller to police its own
#: dimensions would not be a contract. `test_rfA1_child_result_contract`
#: asserts the two tuples stay equal.
CHILD_ADDITIVE_DIMENSIONS = ("usd_micros", "millis", "tokens", "bytes")

#: Compared, never spent. A ceiling that could be charged is not a ceiling.
CHILD_STRUCTURAL_CEILINGS = ("depth", "turns")

CHILD_OUTCOMES = ("completed", "abandoned", "denied", "undeterminable")

#: What a result field may hold. Anything outside this set is a live object or
#: a payload, and both are leaks.
_SCALARS = (str, int, bool, type(None))


class ChildContractError(ValueError):
    """A plan or result is not a delegation contract.

    Raised rather than coerced. A parent that repairs a malformed child result
    has manufactured the very evidence the result was supposed to supply.
    """


@dataclass(frozen=True, slots=True)
class ChildRunPlan:
    """Everything decided before the child runs, and nothing decided after.

    `authority` and `resources` are the **already-attenuated** grant, not a
    request: by the time a plan exists, `kernel.attenuation.attenuate` has
    already refused anything the parent could not delegate. A runner therefore
    never performs an authority decision -- it executes one.
    """

    child_episode_id: str
    parent_episode_id: str
    run_id: str
    project_id: str
    principal: str
    #: The parent's `D_H`. The child runs the *same* frozen composition; it
    #: does not recompose, because a second composition authority would make
    #: the subtree's identity unverifiable against the parent's (`RF-78`).
    composition_digest: str
    goal_digest: str
    authority: tuple[str, ...]
    resources: tuple[str, ...]
    depth: int
    max_depth: int
    max_turns: int
    #: Exactly `CHILD_ADDITIVE_DIMENSIONS`, each already checked against the
    #: parent's *remaining* balance -- not the parent's original ceiling.
    budget: Mapping[str, int]
    lineage: tuple[str, ...]
    idempotency_key: str
    goal_artifact: str | None = None

    def __post_init__(self) -> None:
        if not self.child_episode_id or not self.parent_episode_id:
            raise ChildContractError("a child plan requires both episode identities")
        if not self.idempotency_key:
            # ID uncertainty denies. Without a key the child identity is not
            # derivable, so a restart could not recognise this same subtree.
            raise ChildContractError("a child plan requires an idempotency key")
        if not self.project_id:
            raise ChildContractError("a child plan requires a project identity")
        if self.depth > self.max_depth:
            raise ChildContractError(
                f"child depth {self.depth} exceeds ceiling {self.max_depth}")
        if self.max_turns <= 0:
            raise ChildContractError("a child plan requires a positive turn ceiling")
        for dimension in self.budget:
            if dimension in CHILD_STRUCTURAL_CEILINGS:
                raise ChildContractError(
                    f"{dimension!r} is a structural ceiling, not a budget "
                    "dimension (C-05)")
            if dimension not in CHILD_ADDITIVE_DIMENSIONS:
                raise ChildContractError(
                    f"unknown budget dimension {dimension!r}; the additive set "
                    f"is exactly {CHILD_ADDITIVE_DIMENSIONS}")

    def to_wire(self) -> dict[str, Any]:
        """Canonical camelCase form. Digests and identities only, never prose.

        `goalDigest` names the brief; the brief itself is not here, because an
        append-only store is the one place from which nothing can be withdrawn
        and a brief may quote a secret (`C-06`).
        """
        payload: dict[str, Any] = {
            "schema": "aether.child_plan/1",
            "childEpisodeId": self.child_episode_id,
            "parentEpisodeId": self.parent_episode_id,
            "runId": self.run_id,
            "projectId": self.project_id,
            "principal": self.principal,
            "compositionDigest": self.composition_digest,
            "goalDigest": self.goal_digest,
            "authority": list(self.authority),
            "resources": list(self.resources),
            "depth": int(self.depth),
            "maxDepth": int(self.max_depth),
            "maxTurns": int(self.max_turns),
            "budget": {k: int(v) for k, v in sorted(self.budget.items())},
            "lineage": list(self.lineage),
            "idempotencyKey": self.idempotency_key,
        }
        if self.goal_artifact:
            payload["goalArtifact"] = self.goal_artifact
        return payload


@dataclass(frozen=True, slots=True)
class ChildRunResult:
    """What the parent gets back: a typed contract, never a handle.

    `result_digest` names the child's output and `evidence_refs` name durable
    artifacts or events. Both are strings the parent may *deliberately*
    dereference. That deliberateness is the point -- it keeps a delegated
    subtask from silently re-entering the parent's context window.
    """

    ok: bool
    outcome: str
    terminal: str
    child_episode_id: str
    actual_cost: Mapping[str, int] = field(default_factory=dict)
    turns_used: int = 0
    result_digest: str | None = None
    #: Artifact or event identifiers only. Never inline content.
    evidence_refs: tuple[str, ...] = ()
    detail: str = ""

    def __post_init__(self) -> None:
        if self.outcome not in CHILD_OUTCOMES:
            raise ChildContractError(
                f"unknown child outcome {self.outcome!r}; the set is exactly "
                f"{CHILD_OUTCOMES}")
        if self.ok and self.outcome != "completed":
            raise ChildContractError(
                f"ok=True contradicts outcome {self.outcome!r}")
        for dimension, amount in self.actual_cost.items():
            if dimension in CHILD_STRUCTURAL_CEILINGS:
                raise ChildContractError(
                    f"{dimension!r} is a structural ceiling and cannot appear "
                    "in an additive cost (C-05)")
            if dimension not in CHILD_ADDITIVE_DIMENSIONS:
                raise ChildContractError(
                    f"unknown cost dimension {dimension!r}; the additive set is "
                    f"exactly {CHILD_ADDITIVE_DIMENSIONS}")
            if not isinstance(amount, int) or isinstance(amount, bool):
                raise ChildContractError(
                    f"cost dimension {dimension!r} must be an integer")
            if amount < 0:
                raise ChildContractError(
                    f"cost dimension {dimension!r} cannot be negative; a refund "
                    "is the kernel's settlement, not the child's report")
        if self.turns_used < 0:
            raise ChildContractError("turns_used cannot be negative")
        # The leak check. A runner that returns a session, a port, a socket or
        # a message list fails here rather than three layers up where the
        # object would already have been read.
        for name in ("result_digest", "detail", "terminal", "child_episode_id"):
            value = getattr(self, name)
            if not isinstance(value, _SCALARS):
                raise ChildContractError(
                    f"{name!r} must be a scalar; a live handle or transcript is "
                    "not a delegation result")
        for ref in self.evidence_refs:
            if not isinstance(ref, str):
                raise ChildContractError(
                    "evidence_refs holds reference strings, never inline content")

    def to_returned_payload(self) -> dict[str, Any]:
        """The `ChildReturned` fact.

        `settledIntentKey` is supplied by the adapter, which owns the intent;
        this shape carries the child's own report only.
        """
        payload: dict[str, Any] = {
            "kind": "ChildReturned",
            "childEpisodeId": self.child_episode_id,
            "outcome": self.outcome,
            "terminal": self.terminal,
            # `cost` is the key the reducer folds (`domain/ledger/reducer.py`).
            "cost": {k: int(v) for k, v in sorted(self.actual_cost.items())},
            "turnsUsed": int(self.turns_used),
        }
        if self.result_digest:
            payload["resultDigest"] = self.result_digest
        if self.evidence_refs:
            payload["evidenceRefs"] = list(self.evidence_refs)
        if self.detail:
            payload["detail"] = self.detail
        return payload


@runtime_checkable
class ChildRuntimePort(Protocol):
    """Executes one child episode and reports a typed result.

    A conforming runner MUST NOT widen the plan, MUST NOT return a live
    handle, and MUST report `outcome="undeterminable"` when the child's
    occurrence is genuinely unknown -- the child may already have completed an
    irreversible effect, so reporting failure would license a retry (`F-22`).
    """

    def run_child(self, plan: ChildRunPlan) -> ChildRunResult:
        """Run `plan` to termination. Raising is permitted; lying is not."""
        ...
