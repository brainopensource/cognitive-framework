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

from dataclasses import dataclass, field, replace
from typing import Any, Callable, Mapping, Sequence

from ..domain.canonicalisation.digest import digest_of
from ..kernel.attenuation import Scope, attenuate
from ..kernel.model import AdapterOutcome, Occurrence
from ..ports.child_runtime import ChildRunPlan, ChildRunResult, ChildRuntimePort
from ..ports.event_store import EventRange

__all__ = [
    "ADDITIVE_DIMENSIONS",
    "CHILD_ID_SCHEME",
    "M6_SPAWN_ACTIVE",
    "SPAWN_VERB",
    "STRUCTURAL_CEILINGS",
    "ChildLineage",
    "DelegationContractError",
    "DelegationResult",
    "SpawnAdapter",
    "SpawnIntent",
    "SpawnPreparationError",
    "SpawnRequest",
    "derive_child_id",
    "prepare_spawn",
]

#: Versioned because the identity is durable: a child minted under this scheme
#: must still be recognisable after a restart, and changing the preimage
#: silently would orphan every open subtree in an existing ledger.
CHILD_ID_SCHEME = "aether.child_id/1"

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


def derive_child_id(
    parent_episode_id: str, idempotency_key: str, project_id: str,
) -> str:
    """`child_id = H(project_id, parent_episode_id, idempotency_key)`.

    Three properties, each of which was a falsifier before it was a line:

    * **Restart-stable.** The old counter (`parent.c1`, `parent.c2`) lived in
      adapter memory, so a process restart minted `c1` a second time and the
      cold path could not tell the retry from a new sibling.
    * **Project-isolated.** `project_id` is inside the *preimage*, not merely
      the query filter, so two projects sharing a store cannot collide on a
      shared idempotency key even if a reader forgets to scope its read.
    * **Content-addressed.** Nothing about wall time, ordering, or adapter
      instance enters, so the same intent always names the same child.
    """
    if not parent_episode_id:
        raise DelegationContractError("child identity requires a parent episode")
    if not idempotency_key:
        # ID uncertainty denies (`WP-A1` failure contract). There is no
        # fallback: a generated key would make the child un-recognisable to
        # its own retry, which is exactly the defect this replaced.
        raise DelegationContractError(
            "child identity requires an idempotency key; refusing to invent one")
    if not project_id:
        raise DelegationContractError("child identity requires a project")
    digest = digest_of({
        "scheme": CHILD_ID_SCHEME,
        "projectId": project_id,
        "parentEpisodeId": parent_episode_id,
        "idempotencyKey": idempotency_key,
    })
    return "ep-" + digest.split(":", 1)[-1][:32]


@dataclass(frozen=True, slots=True)
class SpawnIntent:
    """The parsed, validated request -- before any ledger fact exists.

    Separating intent from lineage is what lets a denial be honest: everything
    here can be refused with `DID_NOT_OCCUR`, because nothing has happened yet.
    Once a `ChildSpawned` fact is durable, that answer is no longer available.
    """

    parent_episode_id: str
    project_id: str
    run_id: str
    principal: str
    idempotency_key: str
    requested_actions: frozenset[str]
    requested_resources: tuple[str, ...]
    requested_budget: Mapping[str, int]
    requested_turns: int | None
    child_depth: int
    goal_digest: str
    goal_artifact: str | None = None
    brief: str = ""

    @classmethod
    def parse(
        cls, request: Any, *, project_id: str, parent_episode_id: str,
        parent_resources: Sequence[str],
    ) -> "SpawnIntent":
        """Read the effect request into a validated intent, or refuse.

        Raises `DelegationContractError` for a malformed request. The caller
        turns that into a `DID_NOT_OCCUR` denial rather than letting it escape,
        because a rejected proposal is not an adapter crash.
        """
        args: Mapping[str, Any] = request.args or {}

        requested = args.get("authority") or args.get("actions") or ()
        if isinstance(requested, str):
            requested = (requested,)
        # An unspecified child inherits nothing rather than everything. The
        # opposite default is how delegation becomes privilege escalation.
        actions = frozenset(str(verb) for verb in requested)

        raw_resources = args.get("resources")
        resources = (tuple(str(r) for r in raw_resources)
                     if raw_resources else tuple(parent_resources))

        budget: dict[str, int] = {}
        for dimension, amount in (args.get("budget") or {}).items():
            if dimension in STRUCTURAL_CEILINGS:
                raise DelegationContractError(
                    f"{dimension!r} is a structural ceiling, not a budget "
                    "dimension (C-05)")
            if dimension not in ADDITIVE_DIMENSIONS:
                raise DelegationContractError(
                    f"unknown budget dimension {dimension!r}")
            budget[dimension] = int(amount)

        brief = args.get("brief", "")
        if not isinstance(brief, str):
            raise DelegationContractError("spawn brief must be a string")
        goal_digest = str(args.get("goalDigest") or "")
        if not goal_digest:
            if not brief:
                raise DelegationContractError(
                    "spawn requires a goalDigest or a brief")
            # `C-06`: the ledger gets the identity, never the prose.
            goal_digest = digest_of({"brief": brief})

        requested_turns = args.get("maxTurns")
        if not isinstance(requested_turns, int) or requested_turns <= 0:
            requested_turns = None

        goal_artifact = args.get("goalArtifact")

        return cls(
            parent_episode_id=parent_episode_id,
            project_id=project_id,
            run_id=request.run_id,
            principal=request.principal,
            idempotency_key=request.idempotency_key or "",
            requested_actions=actions,
            requested_resources=resources,
            requested_budget=budget,
            requested_turns=requested_turns,
            child_depth=int(request.depth) + 1,
            goal_digest=goal_digest,
            goal_artifact=goal_artifact if isinstance(goal_artifact, str) else None,
            brief=brief,
        )

    def child_id(self) -> str:
        return derive_child_id(
            self.parent_episode_id, self.idempotency_key, self.project_id)


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
    project_id: str = ""

    @classmethod
    def from_plan(cls, plan: ChildRunPlan) -> "ChildLineage":
        """The ledger fact derived from the frozen plan.

        One direction only. The plan is decided first and the fact records it;
        a lineage that could be edited after the plan would let the ledger and
        the executed child disagree about what was authorized.
        """
        return cls(
            child_episode_id=plan.child_episode_id,
            parent_episode_id=plan.parent_episode_id,
            run_id=plan.run_id,
            principal=plan.principal,
            goal_digest=plan.goal_digest,
            authority=plan.authority,
            depth=plan.depth,
            lineage=plan.lineage,
            budget=plan.budget,
            max_turns=plan.max_turns,
            settled_intent_key=plan.idempotency_key,
            goal_artifact=plan.goal_artifact,
            project_id=plan.project_id,
        )

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
            # The identity scheme is persisted with the fact so a cold reader
            # can verify the child id rather than trust it.
            "childIdScheme": CHILD_ID_SCHEME,
        }
        if self.project_id:
            payload["projectId"] = self.project_id
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
    #: Binds the fact to the intent that caused it. The reducer already checks
    #: this against `ChildSpawned`; the check was dead because nothing wrote it.
    settled_intent_key: str = ""

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

    @classmethod
    def from_child_result(cls, result: ChildRunResult) -> "DelegationResult":
        """Adapt the port's result into the historical lineage shape."""
        return cls(
            ok=result.ok,
            outcome=result.outcome,
            terminal=result.terminal,
            child_episode_id=result.child_episode_id,
            actual_cost=dict(result.actual_cost),
            result_digest=result.result_digest,
            turns_used=result.turns_used,
            detail=result.detail,
        )

    def to_returned_payload(self) -> dict[str, Any]:
        """The `ChildReturned` fact.

        The cost key is `cost`, which is what `domain/ledger/reducer.py` folds
        into `ChildRecord.cost`. It previously wrote `actualCost`, so the fold
        silently produced `None` for every child that ever returned -- the
        conservation record existed on the wire and nowhere in state.
        """
        return {
            "kind": "ChildReturned",
            "childEpisodeId": self.child_episode_id,
            "outcome": self.outcome,
            "terminal": self.terminal,
            "cost": {k: int(v) for k, v in sorted(self.actual_cost.items())},
            "turnsUsed": int(self.turns_used),
            **({"settledIntentKey": self.settled_intent_key}
               if self.settled_intent_key else {}),
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
        child_runtime: ChildRuntimePort,
        clock: Any,
        store: Any | None = None,
        parent_episode_id: str,
        project_id: str = "project-default",
        composition_digest: str = "",
        remaining_budget: Callable[[], Mapping[str, int]] | None = None,
        max_depth: int = 4,
        max_turns: int = 1,
        lineage: Sequence[str] = (),
    ) -> None:
        if not M6_SPAWN_ACTIVE:  # pragma: no cover -- the flag is the gate
            raise SpawnPreparationError("agent.spawn not implemented before M-6")
        if child_runtime is None:
            # Composition-time refusal. This is the whole point of `WP-A1`:
            # the previous binding substituted a lambda that reported success
            # at zero cost, so an unwired product path *manufactured* the very
            # evidence M-6 was supposed to produce.
            raise SpawnPreparationError(
                "agent.spawn requires a ChildRuntimePort; refusing to "
                "synthesize a delegation result")
        self._emitter = emitter
        self._parent_scope = parent_scope
        self._child_runtime = child_runtime
        self._clock = clock
        self._store = store
        self._parent_episode_id = parent_episode_id
        self._project_id = project_id
        self._composition_digest = composition_digest
        # A callable, not a snapshot. Siblings spawned in later turns must see
        # what earlier siblings actually spent, or the second child is granted
        # a balance the first one already consumed.
        self._remaining_budget = remaining_budget or (lambda: {})
        self._max_depth = int(max_depth)
        # `turns` is an episode ceiling, not a `Constraints` field -- it lives
        # on `TaskContext`. It is passed in rather than inferred so that a
        # child can never be handed a ceiling the parent did not actually hold.
        self._max_turns = int(max_turns)
        self._lineage = tuple(lineage) or (parent_episode_id,)

    def healthy(self) -> bool:
        return True

    # -- the effect -------------------------------------------------------

    def execute(self, request: Any) -> AdapterOutcome:
        intent_key = request.idempotency_key or ""

        # Idempotent settlement first. A retried spawn after a crash must not
        # create a second child: the subtree already happened, and running it
        # again would double every irreversible effect inside it.
        settled = self._already_settled(intent_key)
        if settled is not None:
            return settled

        try:
            intent = SpawnIntent.parse(
                request,
                project_id=self._project_id,
                parent_episode_id=self._parent_episode_id,
                parent_resources=self._parent_scope.resources,
            )
        except DelegationContractError as exc:
            # A malformed proposal is a refusal, not an adapter crash. Nothing
            # ran, so `DID_NOT_OCCUR` is knowable.
            return self._denied(str(exc))

        # Depth is a structural ceiling: checked, never charged.
        if intent.child_depth > self._max_depth:
            return self._denied(
                f"depth ceiling {self._max_depth} reached at depth "
                f"{intent.child_depth}")

        requested = Scope(
            actions=intent.requested_actions,
            resources=intent.requested_resources,
            constraints=self._parent_scope.constraints,
            depth=intent.child_depth,
        )
        decision = attenuate(self._parent_scope, requested)
        if not decision.ok or decision.granted is None:
            dimension = decision.denial.dimension if decision.denial else "unknown"
            # No child events. A denied spawn produced no lineage, so writing
            # `ChildSpawned` here would put a child in the ledger that never
            # existed (RF-55/RF-56).
            return self._denied(f"attenuation denied on {dimension}")
        granted = decision.granted

        # Componentwise reservation against the parent's *remaining* balance,
        # not its original ceiling. This is the conservation the milestone
        # asked for: a child cannot be granted what the parent already spent.
        remaining = dict(self._remaining_budget())
        for dimension in ADDITIVE_DIMENSIONS:
            wanted = int(intent.requested_budget.get(dimension, 0))
            available = int(remaining.get(dimension, 0))
            if wanted > available:
                return self._denied(
                    f"budget dimension {dimension!r} requests {wanted} but the "
                    f"parent has {available} remaining")

        # Structural ceilings are compared the same way and spent by nobody.
        child_turns = self._child_turns(intent)
        if "turns" in remaining and child_turns > int(remaining["turns"]):
            return self._denied(
                f"turn ceiling {child_turns} exceeds parent remaining "
                f"{remaining['turns']}")
        if "depth" in remaining and int(remaining["depth"]) <= 0:
            return self._denied("no depth headroom remains for a child")

        try:
            plan = ChildRunPlan(
                child_episode_id=intent.child_id(),
                parent_episode_id=intent.parent_episode_id,
                run_id=intent.run_id,
                project_id=intent.project_id,
                principal=intent.principal,
                composition_digest=self._composition_digest,
                goal_digest=intent.goal_digest,
                authority=tuple(sorted(granted.actions)),
                resources=tuple(granted.resources),
                depth=intent.child_depth,
                max_depth=self._max_depth,
                max_turns=child_turns,
                budget={d: int(intent.requested_budget.get(d, 0))
                        for d in ADDITIVE_DIMENSIONS
                        if intent.requested_budget.get(d)},
                lineage=self._lineage,
                idempotency_key=intent.idempotency_key,
                goal_artifact=intent.goal_artifact,
                constraints={
                    "expires_at": granted.constraints.expires_at,
                    "max_uses": granted.constraints.max_uses,
                    "budget_usd_micros": granted.constraints.budget_usd_micros,
                    "max_bytes": granted.constraints.max_bytes,
                    "max_effects": granted.constraints.max_effects,
                    "risk_ceiling": granted.constraints.risk_ceiling,
                    "max_depth": granted.constraints.max_depth,
                    "network_policy": granted.constraints.network_policy,
                },
                brief=intent.brief,
            )
        except Exception as exc:  # noqa: BLE001 -- plan validation is a refusal
            return self._denied(f"invalid child plan: {exc}")

        collision = self._collides(plan)
        if collision is not None:
            return self._denied(collision)

        lineage = ChildLineage.from_plan(plan)

        # Fact before execution. If the process dies inside the runner, the
        # cold path finds an open `ChildSpawned` and reports UNDETERMINABLE --
        # which is only possible because the fact was durable *first*.
        self._emit("ChildSpawned", lineage.to_spawned_payload(), request,
                   episode_id=plan.child_episode_id)

        try:
            child_result = self._child_runtime.run_child(plan)
        except Exception as exc:  # noqa: BLE001 -- occurrence is genuinely unknown
            # The child may have completed an irreversible effect before
            # raising. Reporting DID_NOT_OCCUR here would be a guess that
            # licenses a retry (`F-22`).
            child_result = ChildRunResult(
                ok=False, outcome="undeterminable", terminal="UNDETERMINABLE",
                child_episode_id=plan.child_episode_id,
                detail=f"child raised: {exc}")

        if not isinstance(child_result, ChildRunResult):
            raise DelegationContractError(
                "a ChildRuntimePort must return a ChildRunResult; a raw handle "
                "or transcript is not a delegation contract")

        refresh_chain = getattr(self._emitter, "refresh_chain", None)
        if callable(refresh_chain):
            refresh_chain()

        result = DelegationResult.from_child_result(child_result)
        result = replace(result, settled_intent_key=plan.idempotency_key)
        self._emit("ChildReturned", result.to_returned_payload(), request,
                   episode_id=plan.child_episode_id)

        occurrence = (
            Occurrence.UNDETERMINABLE if result.outcome == "undeterminable"
            else Occurrence.OCCURRED)
        return AdapterOutcome(
            status="ok" if result.ok else "error",
            occurrence=occurrence,
            # The Kernel commits this against the PARENT's lease and releases
            # the unspent remainder. That single line is four-dimensional
            # additive conservation across the tree -- there is exactly one
            # accountant, and it is not this adapter.
            actual_cost=dict(result.actual_cost),
            result_digest=result.result_digest,
        )

    # -- internals --------------------------------------------------------

    def _child_turns(self, intent: SpawnIntent) -> int:
        """A child may lower the turn ceiling and never raise it."""
        if intent.requested_turns is not None:
            return min(intent.requested_turns, self._max_turns)
        return self._max_turns

    def _collides(self, plan: ChildRunPlan) -> str | None:
        """Refuse a child id already bound to a different intent.

        The derivation is a hash, so a collision means either a genuine digest
        collision or -- far more likely -- that two different intents were
        handed the same key. Either way the correct answer is refusal: reusing
        the id would silently merge two distinct subtrees in the ledger.
        """
        for payload in self._child_payloads():
            if payload.get("kind") != "ChildSpawned":
                continue
            if payload.get("childEpisodeId") != plan.child_episode_id:
                continue
            same_intent = payload.get("settledIntentKey") == plan.idempotency_key
            same_parent = payload.get("parentEpisodeId") == plan.parent_episode_id
            if same_intent and same_parent:
                # Not a collision: this is the retry path, already handled by
                # `_already_settled` above.
                return None
            return (f"child id {plan.child_episode_id!r} already bound to a "
                    "different intent")
        return None

    def _child_payloads(self) -> list[Mapping[str, Any]]:
        """Every event payload in *this project*.

        Scoped by `project_id`. An unscoped read let one project's settled
        subtree answer another project's spawn -- cross-project idempotency,
        which the failure contract forbids outright.
        """
        if self._store is None:
            return []
        read = self._store.read(EventRange(project_id=self._project_id))
        envelopes = list(read.value) if getattr(read, "ok", False) and read.value else []
        return [envelope.payload or {} for envelope in envelopes]

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
        payloads = self._child_payloads()
        spawned_child = None
        for payload in payloads:
            if payload.get("kind") == "ChildSpawned" and payload.get(
                    "settledIntentKey") == intent_key:
                spawned_child = payload.get("childEpisodeId")
        if spawned_child is None:
            return None
        for payload in payloads:
            if payload.get("kind") == "ChildReturned" and payload.get(
                    "childEpisodeId") == spawned_child:
                outcome = payload.get("outcome")
                if outcome == "undeterminable":
                    return AdapterOutcome(
                        status="error", occurrence=Occurrence.UNDETERMINABLE,
                        actual_cost=dict(payload.get("cost") or {}),
                        detail="settled subtree was undeterminable; not retried")
                return AdapterOutcome(
                    status="ok" if outcome == "completed" else "error",
                    occurrence=Occurrence.OCCURRED,
                    actual_cost=dict(payload.get("cost") or {}),
                    result_digest=payload.get("resultDigest"),
                )
        # Recovery may already have adjudicated this open subtree. If it did,
        # replay its verdict rather than re-running: the child may have
        # mutated the world, so a blind retry would double an irreversible
        # effect (`F-22`).
        for payload in payloads:
            if payload.get("kind") != "EffectReconciled":
                continue
            if payload.get("idempotencyKey") != intent_key:
                continue
            return AdapterOutcome(
                status="error", occurrence=Occurrence.UNDETERMINABLE,
                actual_cost={},
                detail="subtree reconciled as undeterminable by recovery; "
                       "not retried")
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
