"""M-6 mediated recursive delegation (`ADR-0080`, `ADR-0090`).

Spawn does not instantiate an agent. It creates a **child lineage**: its own
identity, parent reference, goal, selected context, budget, capabilities, depth
boundary and terminal conditions, which produces its own events and whose
result the parent incorporates. Recursion is the nesting of bounded causal
regions -- not a new kernel primitive.

The whole design rests on one refusal: **the Kernel never learns what
`agent.spawn` means.** It resolves the verb to an adapter, opens a lease,
enforces attenuation and settles a receipt exactly as it does for `fs.patch`.
There is no `if verb == "agent.spawn"` anywhere in `kernel/`, and if one ever
appears, the generality claim this project is built on is false.

Three consequences follow, and each is a falsifier rather than a comment:

* **Budget conservation is structural, not computed.** The adapter reports the
  child's real cost as `AdapterOutcome.actual_cost`, so the Kernel commits it
  against the *parent's* lease through the ordinary path. A tree therefore
  cannot spend more than its root ceiling, because nobody added a second
  accountant -- there is only ever one (`C-05`: additive `usd_micros`,
  `millis`, `tokens`, `bytes`; `depth` and `turns` are structural ceilings and
  are never costs).
* **A crash between `ChildSpawned` and `ChildReturned` is `UNDETERMINABLE`.**
  Not "probably failed", not a silent retry. The child may have mutated the
  world already, so the cold path reports what it actually knows.
* **The delegation return is a typed contract**, never a conversation dump.
  A parent that receives the child's transcript has not delegated; it has
  inlined.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Sequence

from ..domain.canonicalisation.digest import digest_of
from ..kernel.attenuation import Scope, attenuate
from ..kernel.model import AdapterOutcome, Occurrence
from ..ports.event_store import EventRange

__all__ = [
    "ADDITIVE_DIMENSIONS",
    "M6_SPAWN_ACTIVE",
    "SPAWN_VERB",
    "STRUCTURAL_CEILINGS",
    "ChildLineage",
    "DelegationContractError",
    "DelegationResult",
    "SpawnAdapter",
    "SpawnPreparationError",
    "SpawnRequest",
    "prepare_spawn",
]

#: `ADR-0088` kept this false while `agent.spawn` parsed but had no live code
#: path. M-6 is the milestone that supplies the path.
M6_SPAWN_ACTIVE = True

SPAWN_VERB = "agent.spawn"

#: `C-05`. Exactly four, and the list is closed. The withdrawn fifth
#: "charged-millis" dimension is not here and never was; `depth` and `turns`
#: are ceilings, so adding either would let a structural bound be *spent* -- a
#: child could buy depth by using fewer tokens, which is not what a ceiling
#: means. `test_event_substrate_v2` greps this tree for the withdrawn name, so
#: it must not appear verbatim even in prose.
ADDITIVE_DIMENSIONS = ("usd_micros", "millis", "tokens", "bytes")

STRUCTURAL_CEILINGS = ("depth", "turns")


class SpawnPreparationError(PermissionError):
    """A spawn was refused before any child lineage or ledger fact existed."""


class DelegationContractError(ValueError):
    """A child returned something that is not a delegation result.

    Raised rather than coerced. A parent that accepts a malformed return has
    no way to tell a completed subtask from an absent one.
    """


@dataclass(frozen=True, slots=True)
class ChildLineage:
    """The bounded causal region a spawn creates.

    Everything here is decided *before* the child runs and cannot be widened
    from inside it. `lineage` is the ancestor chain, so a cold reader can
    rebuild the tree without a live parent object -- which is the whole point
    of RF-59.
    """

    child_episode_id: str
    parent_episode_id: str
    run_id: str
    principal: str
    goal_digest: str
    authority: tuple[str, ...]
    depth: int
    lineage: tuple[str, ...]
    budget: Mapping[str, int]
    max_turns: int
    settled_intent_key: str
    goal_artifact: str | None = None

    def to_spawned_payload(self) -> dict[str, Any]:
        """The `ChildSpawned` fact. camelCase, digests only.

        No goal text (`C-06`): an append-only store is the one place from
        which nothing can be withdrawn, and a brief may quote a secret.
        """
        payload: dict[str, Any] = {
            "kind": "ChildSpawned",
            "parentEpisodeId": self.parent_episode_id,
            "childEpisodeId": self.child_episode_id,
            "authority": list(self.authority),
            "depth": int(self.depth),
            "lineage": list(self.lineage),
            "settledIntentKey": self.settled_intent_key,
            "goalDigest": self.goal_digest,
            "budget": {k: int(v) for k, v in sorted(self.budget.items())},
            "maxTurns": int(self.max_turns),
        }
        if self.goal_artifact:
            payload["goalArtifact"] = self.goal_artifact
        return payload


@dataclass(frozen=True, slots=True)
class DelegationResult:
    """What a parent gets back. A contract, not a handle and not a transcript.

    `result_digest` names the child's output; the bytes live in the artifact
    store if they were captured at all. A parent that needs the content
    dereferences it deliberately, which keeps a delegated subtask from
    silently re-entering the parent's context window.
    """

    ok: bool
    outcome: str  # "completed" | "abandoned" | "denied" | "undeterminable"
    terminal: str
    child_episode_id: str
    actual_cost: Mapping[str, int] = field(default_factory=dict)
    result_digest: str | None = None
    turns_used: int = 0
    detail: str = ""

    def __post_init__(self) -> None:
        for dimension in self.actual_cost:
            if dimension in STRUCTURAL_CEILINGS:
                raise DelegationContractError(
                    f"{dimension!r} is a structural ceiling and cannot appear in "
                    "an additive cost (C-05)")
            if dimension not in ADDITIVE_DIMENSIONS:
                raise DelegationContractError(
                    f"unknown cost dimension {dimension!r}; the additive set is "
                    f"exactly {ADDITIVE_DIMENSIONS}")

    def to_returned_payload(self) -> dict[str, Any]:
        return {
            "kind": "ChildReturned",
            "childEpisodeId": self.child_episode_id,
            "outcome": self.outcome,
            "terminal": self.terminal,
            "actualCost": {k: int(v) for k, v in sorted(self.actual_cost.items())},
            "turnsUsed": int(self.turns_used),
            **({"resultDigest": self.result_digest} if self.result_digest else {}),
            **({"detail": self.detail} if self.detail else {}),
        }


class SpawnAdapter:
    """`agent.spawn` as an ordinary `EffectAdapter`.

    It coordinates nothing and decides no policy -- the Kernel already decided
    admissibility before `execute` is reached. What this owns is lineage
    semantics: minting the child identity, writing the two facts that make the
    subtree reconstructible, and reporting a cost the Kernel can settle.

    It is the **sole legal writer** of `ChildSpawned`/`ChildReturned`
    (`PRIVILEGED_KIND_OWNERS`). Plugins, workers and child episodes propose;
    they never append.
    """

    name = SPAWN_VERB

    def __init__(
        self,
        *,
        emitter: Any,
        parent_scope: Scope,
        run_child: Callable[[ChildLineage], DelegationResult],
        clock: Any,
        store: Any | None = None,
        parent_episode_id: str,
        max_depth: int = 4,
        max_turns: int = 1,
        lineage: Sequence[str] = (),
    ) -> None:
        if not M6_SPAWN_ACTIVE:  # pragma: no cover -- the flag is the gate
            raise SpawnPreparationError("agent.spawn not implemented before M-6")
        self._emitter = emitter
        self._parent_scope = parent_scope
        self._run_child = run_child
        self._clock = clock
        self._store = store
        self._parent_episode_id = parent_episode_id
        self._max_depth = int(max_depth)
        # `turns` is an episode ceiling, not a `Constraints` field -- it lives
        # on `TaskContext`. It is passed in rather than inferred so that a
        # child can never be handed a ceiling the parent did not actually hold.
        self._max_turns = int(max_turns)
        self._lineage = tuple(lineage) or (parent_episode_id,)
        self._spawned = 0

    def healthy(self) -> bool:
        return True

    # -- the effect -------------------------------------------------------

    def execute(self, request: Any) -> AdapterOutcome:
        args: Mapping[str, Any] = request.args or {}
        intent_key = request.idempotency_key or ""

        # Idempotent settlement first. A retried spawn after a crash must not
        # create a second child: the subtree already happened, and running it
        # again would double every irreversible effect inside it.
        settled = self._already_settled(intent_key)
        if settled is not None:
            return settled

        # Depth is a structural ceiling: checked, never charged.
        child_depth = int(request.depth) + 1
        if child_depth > self._max_depth:
            return self._denied(
                f"depth ceiling {self._max_depth} reached at depth {child_depth}")

        requested = self._requested_scope(args, child_depth)
        decision = attenuate(self._parent_scope, requested)
        if not decision.ok or decision.granted is None:
            dimension = decision.denial.dimension if decision.denial else "unknown"
            # No child events. A denied spawn produced no lineage, so writing
            # `ChildSpawned` here would put a child in the ledger that never
            # existed (RF-55/RF-56).
            return self._denied(f"attenuation denied on {dimension}")

        granted = decision.granted
        goal_digest = str(args.get("goalDigest") or "")
        if not goal_digest:
            brief = args.get("brief")
            if not isinstance(brief, str) or not brief:
                return self._denied("spawn requires a goalDigest or a brief")
            # `C-06`: the ledger gets the identity, never the prose.
            goal_digest = digest_of({"brief": brief})

        lineage = ChildLineage(
            child_episode_id=self._mint_child_id(),
            parent_episode_id=self._parent_episode_id,
            run_id=request.run_id,
            principal=request.principal,
            goal_digest=goal_digest,
            authority=tuple(sorted(granted.actions)),
            depth=child_depth,
            lineage=self._lineage,
            budget=self._child_budget(args),
            max_turns=self._child_turns(args, granted),
            settled_intent_key=intent_key,
            goal_artifact=args.get("goalArtifact") if isinstance(
                args.get("goalArtifact"), str) else None,
        )

        # Fact before execution. If the process dies inside `run_child`, the
        # cold path finds an open `ChildSpawned` and reports UNDETERMINABLE --
        # which is only possible because the fact was durable *first*.
        self._emit("ChildSpawned", lineage.to_spawned_payload(), request,
                   episode_id=lineage.child_episode_id)

        try:
            result = self._run_child(lineage)
        except Exception as exc:  # noqa: BLE001 -- occurrence is genuinely unknown
            # The child may have completed an irreversible effect before
            # raising. Reporting DID_NOT_OCCUR here would be a guess that
            # licenses a retry (`F-22`).
            result = DelegationResult(
                ok=False, outcome="undeterminable", terminal="UNDETERMINABLE",
                child_episode_id=lineage.child_episode_id,
                detail=f"child raised: {exc}")

        if not isinstance(result, DelegationResult):
            raise DelegationContractError(
                "run_child must return a DelegationResult; a raw handle or "
                "transcript is not a delegation contract")

        self._emit("ChildReturned", result.to_returned_payload(), request,
                   episode_id=lineage.child_episode_id)

        occurrence = (
            Occurrence.UNDETERMINABLE if result.outcome == "undeterminable"
            else Occurrence.OCCURRED)
        return AdapterOutcome(
            status="ok" if result.ok else "error",
            occurrence=occurrence,
            # The Kernel commits this against the PARENT's lease. That single
            # line is four-dimensional additive conservation across the tree.
            actual_cost=dict(result.actual_cost),
            result_digest=result.result_digest,
        )

    # -- internals --------------------------------------------------------

    def _requested_scope(self, args: Mapping[str, Any], depth: int) -> Scope:
        requested = args.get("authority") or args.get("actions") or ()
        if isinstance(requested, str):
            requested = (requested,)
        actions = frozenset(str(verb) for verb in requested)
        if not actions:
            # An unspecified child inherits nothing rather than everything.
            # The safe default for authority is the empty set; the opposite
            # default is how delegation becomes privilege escalation.
            actions = frozenset()
        resources = tuple(args.get("resources") or self._parent_scope.resources)
        return Scope(actions=actions, resources=resources,
                     constraints=self._parent_scope.constraints, depth=depth)

    def _child_budget(self, args: Mapping[str, Any]) -> Mapping[str, int]:
        raw = args.get("budget") or {}
        budget: dict[str, int] = {}
        for dimension, amount in raw.items():
            if dimension in STRUCTURAL_CEILINGS:
                raise DelegationContractError(
                    f"{dimension!r} is a structural ceiling, not a budget "
                    "dimension (C-05)")
            if dimension not in ADDITIVE_DIMENSIONS:
                raise DelegationContractError(
                    f"unknown budget dimension {dimension!r}")
            budget[dimension] = int(amount)
        return budget

    def _child_turns(self, args: Mapping[str, Any], granted: Scope) -> int:
        """A child may lower the turn ceiling and never raise it."""
        requested = args.get("maxTurns")
        if isinstance(requested, int) and requested > 0:
            return min(requested, self._max_turns)
        return self._max_turns

    def _mint_child_id(self) -> str:
        self._spawned += 1
        return f"{self._parent_episode_id}.c{self._spawned}"

    def _emit(self, kind: str, payload: Mapping[str, Any], request: Any,
              *, episode_id: str) -> None:
        self._emitter.emit_kind(
            kind,
            run_id=request.run_id,
            principal=request.principal,
            payload=dict(payload),
            episode_id=episode_id,
            idempotency_key=request.idempotency_key,
        )

    def _denied(self, detail: str) -> AdapterOutcome:
        """A refusal that costs nothing and leaves no lineage behind.

        `DID_NOT_OCCUR` is knowable here precisely because the refusal happens
        before `ChildSpawned`: nothing ran, so nothing is ambiguous. That is
        the difference between this and the `UNDETERMINABLE` path below.
        """
        return AdapterOutcome(
            status="error",
            occurrence=Occurrence.DID_NOT_OCCUR,
            actual_cost={},
            result_digest=None,
            detail=detail,
        )

    def _already_settled(self, intent_key: str) -> AdapterOutcome | None:
        """Replay a settled subtree rather than running it twice."""
        if not intent_key or self._store is None:
            return None
        read = self._store.read(EventRange(run_id=None))
        envelopes = list(read.value) if getattr(read, "ok", False) and read.value else []
        spawned_child = None
        for envelope in envelopes:
            payload = envelope.payload or {}
            if payload.get("kind") == "ChildSpawned" and payload.get(
                    "settledIntentKey") == intent_key:
                spawned_child = payload.get("childEpisodeId")
        if spawned_child is None:
            return None
        for envelope in envelopes:
            payload = envelope.payload or {}
            if payload.get("kind") == "ChildReturned" and payload.get(
                    "childEpisodeId") == spawned_child:
                return AdapterOutcome(
                    status="ok" if payload.get("outcome") == "completed" else "error",
                    occurrence=Occurrence.OCCURRED,
                    actual_cost=dict(payload.get("actualCost") or {}),
                    result_digest=payload.get("resultDigest"),
                )
        # Spawned but never returned: the subtree is open across a restart.
        # Neither success nor failure is knowable from here.
        return AdapterOutcome(
            status="error", occurrence=Occurrence.UNDETERMINABLE, actual_cost={},
            detail=f"child subtree for intent {intent_key!r} spawned but never "
                   "returned; occurrence is unknown across the restart")


# -- retained pre-M-6 seam -------------------------------------------------


@dataclass(frozen=True, slots=True)
class SpawnRequest:
    """The pre-M-6 reservation shape, kept so existing callers still parse."""

    target_harness_digest: str
    selector: Mapping[str, Any]
    turns: int
    depth: int
    budget: Mapping[str, int]


def prepare_spawn(request: SpawnRequest, *, grant: Mapping[str, Any] | None,
                  parent_ceiling: Mapping[str, Any] | None) -> None:
    """Validate a spawn reservation. Still refuses without grant and ceiling."""
    if not M6_SPAWN_ACTIVE:
        raise SpawnPreparationError("agent.spawn not implemented before M-6")
    if grant is None or parent_ceiling is None:
        raise SpawnPreparationError(
            "agent.spawn requires an explicit grant and parent ceiling")
