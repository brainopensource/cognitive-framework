"""Parallel observation as a causal partial order (`Vision Ch. 15`, `A1`).

One turn may carry **N independent read-only requests**. The unit of economy
is the turn, not the request: a brownfield task needs a dozen reads before its
first change, and at one request per turn that spends the whole episode budget
before anything is proposed.

Three things this module is careful about, because each is where the idea goes
wrong when implemented casually:

1. **Sequence number is not dependency.** `A before C` and `B before C` does
   not imply `A before B`. The order declared here is a *partial* order over
   an explicit `dependsOn` relation, and the settlement rank (`level`) is
   derived from that relation alone. Reading position in the array as
   causality is the defect this module exists to prevent.

2. **Identity is per request.** Every request keeps its own descriptor, and
   therefore its own `EffectStarted`, receipt and digest once the engine
   settles it through `Kernel.dispatch`. Nothing here collapses a batch into
   one receipt: a collapsed receipt cannot be replayed and makes the change
   surface unreconstructable.

3. **The batch descriptor is rename-stable.** No-progress detection compares
   proposal descriptors across turns (`Turn.signature`). A descriptor that
   included provider-generated request ids would differ on every turn and the
   livelock detector would never fire — the exact failure `Turn.signature`
   records for `state_digest`. So the batch descriptor digests the *positional*
   dependency relation and the request content, never the ids.

Read-only membership is **not** decided here. This module knows nothing about
which verbs exist; sink classification is kernel/manifest authority and the
engine consults it (`ICD §3`). A module that carried its own list of safe
verbs would be a second place a domain has to be registered.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from ...domain.canonicalisation.digest import digest_of

__all__ = [
    "MAX_PARALLEL_OBSERVATIONS",
    "ObservationRequest",
    "batch_descriptor",
    "parse_observation_requests",
    "settlement_levels",
]

#: Hard ceiling on requests in one batch. A bound, not a tuning knob: an
#: unbounded batch lets one malformed provider reply reserve arbitrarily much
#: against the governor in a single turn. A composition may narrow it further;
#: nothing may widen it.
MAX_PARALLEL_OBSERVATIONS = 16


@dataclass(frozen=True, slots=True)
class ObservationRequest:
    """One read-only sub-request inside a batch. Carries no authority."""

    request_id: str
    action: str
    resource: Mapping[str, Any] = field(default_factory=dict)
    args: Mapping[str, Any] = field(default_factory=dict)
    reservation: Mapping[str, int] = field(default_factory=dict)
    #: Ids of sibling requests that must settle before this one. Empty means
    #: independent — the common case, and the one that buys the turn back.
    depends_on: tuple[str, ...] = ()
    idempotency_key: str | None = None

    @property
    def descriptor(self) -> str:
        """Action-only identity, matching `Proposal.descriptor`'s contract.

        The id is excluded on purpose (see the module note): it is provider
        vocabulary, not content.
        """
        return digest_of({
            "action": self.action,
            "resource": dict(self.resource),
            "args": dict(self.args),
        })


def parse_observation_requests(value: Any) -> tuple[ObservationRequest, ...]:
    """Parse the `requests` array of an observe proposal.

    Raises `ValueError` on any shape defect. The caller converts that to
    `ProposalMalformed`, which keeps a bad provider reply an *instrument*
    problem rather than a task verdict (`CT-03`).
    """
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError("requests must be an array")
    rows = list(value)
    if not rows:
        raise ValueError("an observe proposal requires at least one request")
    if len(rows) > MAX_PARALLEL_OBSERVATIONS:
        raise ValueError(
            f"{len(rows)} requests exceeds the parallel observation ceiling "
            f"of {MAX_PARALLEL_OBSERVATIONS}")

    parsed: list[ObservationRequest] = []
    seen: set[str] = set()
    for position, row in enumerate(rows):
        if not isinstance(row, Mapping):
            raise ValueError(f"request {position} is not an object")
        action = row.get("action")
        if not isinstance(action, str) or not action:
            raise ValueError(f"request {position} requires a non-empty action")

        request_id = row.get("id")
        if request_id is None:
            request_id = row.get("requestId")
        if request_id is None:
            # Positional fallback, generated here rather than left absent so
            # every request is addressable by `dependsOn` even when the
            # provider omitted ids entirely.
            request_id = f"obs-{position}"
        if not isinstance(request_id, str) or not request_id:
            raise ValueError(f"request {position} id must be a non-empty string")
        if request_id in seen:
            raise ValueError(f"duplicate request id {request_id!r}")
        seen.add(request_id)

        members = {
            "resource": row.get("resource", {}),
            "args": row.get("args", {}),
            "reservation": row.get("reservation", {}) or {},
        }
        for name, member in members.items():
            if not isinstance(member, Mapping):
                raise ValueError(f"request {position}: {name} must be an object")
        for dimension, amount in members["reservation"].items():
            if not isinstance(amount, int) or isinstance(amount, bool) or amount < 0:
                raise ValueError(
                    f"request {position}: reservation.{dimension} must be a "
                    "non-negative integer (CT-06)")

        raw_deps = row.get("dependsOn")
        if raw_deps is None:
            raw_deps = row.get("depends_on")
        if raw_deps is None:
            raw_deps = ()
        if isinstance(raw_deps, str) or not isinstance(raw_deps, Sequence):
            raise ValueError(f"request {position}: dependsOn must be an array")
        depends_on: list[str] = []
        for dep in raw_deps:
            if not isinstance(dep, str) or not dep:
                raise ValueError(
                    f"request {position}: dependsOn entries must be non-empty strings")
            if dep == request_id:
                raise ValueError(f"request {request_id!r} depends on itself")
            if dep not in depends_on:
                depends_on.append(dep)

        key = row.get("idempotencyKey")
        if key is None:
            key = row.get("idempotency_key")
        if key is not None and (not isinstance(key, str) or not key):
            raise ValueError(
                f"request {position}: idempotencyKey must be a non-empty string")

        parsed.append(ObservationRequest(
            request_id=request_id,
            action=action,
            resource=dict(members["resource"]),
            args=dict(members["args"]),
            reservation={str(k): int(v) for k, v in members["reservation"].items()},
            depends_on=tuple(depends_on),
            idempotency_key=key,
        ))

    for request in parsed:
        for dep in request.depends_on:
            if dep not in seen:
                raise ValueError(
                    f"request {request.request_id!r} depends on unknown id {dep!r}")

    # Acyclicity is a *shape* property, so it is rejected at parse time rather
    # than discovered during settlement. `settlement_levels` may then assume a
    # DAG and still fails closed if it is ever handed one that is not.
    settlement_levels(parsed)
    return tuple(parsed)


def settlement_levels(
    requests: Sequence[ObservationRequest],
) -> tuple[tuple[int, ...], ...]:
    """Rank the batch into causal levels, as positions in declaration order.

    Level `n` contains exactly the requests whose longest dependency chain has
    length `n`. Everything within one level is mutually independent — that is
    the licence to settle it concurrently — and every level is settled before
    the next begins.

    Within a level, positions stay in declaration order. That makes settlement
    a *deterministic* linear extension of the partial order, which is what
    lets a cold replay reconstruct the identical run. Declaration order is
    used only to break ties inside a level; it never creates an edge.
    """
    index_of = {request.request_id: position
                for position, request in enumerate(requests)}
    pending = {
        position: {index_of[dep] for dep in request.depends_on if dep in index_of}
        for position, request in enumerate(requests)
    }
    levels: list[tuple[int, ...]] = []
    settled: set[int] = set()
    while pending:
        ready = tuple(position for position in sorted(pending)
                      if pending[position] <= settled)
        if not ready:
            # Fail closed. Parsing rejects cycles, so reaching here means a
            # caller built a batch by hand and skipped the parser.
            remaining = sorted(pending)
            raise ValueError(
                "observation requests form a dependency cycle: "
                f"{[requests[position].request_id for position in remaining]}")
        levels.append(ready)
        settled.update(ready)
        for position in ready:
            del pending[position]
    return tuple(levels)


def batch_descriptor(requests: Sequence[ObservationRequest]) -> str:
    """A stable digest of the batch *and* its partial order.

    Dependencies are digested as sorted declaration positions, so two batches
    that differ only in provider-generated ids share a descriptor and the
    no-progress detector can still see a repeat.
    """
    index_of = {request.request_id: position
                for position, request in enumerate(requests)}
    return digest_of({
        "kind": "observe",
        "requests": [
            {
                "action": request.action,
                "resource": dict(request.resource),
                "args": dict(request.args),
                "dependsOn": sorted(index_of[dep] for dep in request.depends_on
                                    if dep in index_of),
            }
            for request in requests
        ],
    })
