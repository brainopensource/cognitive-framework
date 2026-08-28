"""The real child runtime: recursion through the one public boundary.

This module is the answer to the question M-6 was actually asking. A spawn
adapter can mint identities, attenuate scope and reserve budget perfectly and
still prove nothing, because none of that executes a child. Something has to
*run* the subtree -- and the only defensible something is the same
`Runtime.run_composed` the parent went through.

That constraint is doing real work. Running a child through a second, simpler
path would make the subtree's evidence incomparable with the parent's: a
different activation, a different `RunPlan`, a different set of facts. Instead
the child re-enters the identical boundary with **rebound ports** and a
**lowered task**, so a depth-3 tree is three ordinary runs that happen to be
causally nested, and the cold reader folds all three with one reducer.

What recursion must *not* do is acquire authority on the way down. Every
widening vector is closed here by construction rather than by check:

* the plan is frozen before this module sees it, and nothing here edits it;
* the child gets the parent's *attenuated* grant, never the parent's `Scope`;
* the child shares the parent's store, so its spend lands in one ledger;
* `interactive` is forced off -- a child may not prompt a human the parent
  never offered it access to;
* the meta-controller is dropped unless explicitly rebound, so a child cannot
  inherit a strategy authority it was not granted (`WP-A2` territory).
"""

from __future__ import annotations

from dataclasses import replace
from typing import Any, Callable, Mapping

from ..kernel.attenuation import Constraints, Scope
from ..ports.child_runtime import ChildRunPlan, ChildRunResult
from ..ports.event_store import EventRange
from .compose import Harness, RunResult, TaskContext

__all__ = ["RuntimeChildRunner", "TERMINAL_OUTCOMES"]

#: How a terminal state becomes a delegation outcome. `undeterminable` is not
#: in this map on purpose: it is produced only by a genuine unknown (a raised
#: runner, an open subtree across a restart), never by a terminal the child
#: actually reached and reported.
TERMINAL_OUTCOMES: Mapping[str, str] = {
    "completed": "completed",
    "abstained": "abandoned",
    "abandoned": "abandoned",
    "escalated": "abandoned",
    "cancelled": "abandoned",
    "budget_exhausted": "abandoned",
    # An instrument or runtime error is *not* a failed child. The child may
    # have completed an irreversible effect before the instrument broke, so
    # the honest answer is that occurrence is unknown (`F-22`).
    "instrument_error": "undeterminable",
    "runtime_error": "undeterminable",
}


class RuntimeChildRunner:
    """`ChildRuntimePort` over the sole public run path.

    Constructed per parent session and handed the parent's own composition and
    ports. It holds no policy: by the time `run_child` is called, every
    authority question has already been answered by `delegation.SpawnAdapter`.
    """

    def __init__(
        self,
        *,
        run_composed: Callable[..., RunResult],
        harness: Harness,
        parent_ports: Any,
        parent_task: TaskContext,
        profile: Any = None,
        release: bool = False,
    ) -> None:
        #: The sole public activation boundary, injected rather than imported.
        #: `root` imports `session` imports `wiring` imports `delegation`, so
        #: naming `Runtime` here would close that ring -- and a lazy import
        #: would only hide the ring from readers, not from the boundary
        #: linter. Recursion is a runtime edge, so it is passed at runtime.
        #: `root.run_composed` is its only production binder, and
        #: `test_rfA1_recursive_depth` asserts that is what arrives.
        self._run_composed = run_composed
        self._harness = harness
        self._parent_ports = parent_ports
        self._parent_task = parent_task
        self._profile = profile
        self._release = release

    # -- the port ---------------------------------------------------------

    def run_child(self, plan: ChildRunPlan) -> ChildRunResult:
        """Execute one child episode and project a typed result."""
        child_ports = self._rebind(plan)
        child_task = self._lower(plan)

        result = self._run_composed(
            self._harness,
            child_ports,
            child_task,
            release=self._release,
            profile=self._profile,
        )
        return self._project(plan, result)

    # -- internals --------------------------------------------------------

    def _rebind(self, plan: ChildRunPlan) -> Any:
        """The parent's ports, narrowed. Never widened, never replaced.

        The store is deliberately shared. One ledger is what makes the tree
        foldable: the child's facts carry `parentEpisodeId`, so a cold reader
        rebuilds the whole subtree from a single chain (`RF-59`). A private
        child store would produce an unlinkable second history.
        """
        return replace(
            self._parent_ports,
            # A topology decorator owns only the root routing decision.  A
            # child is an ordinary runtime episode and must use the supplied
            # provider, not emit the root's next topology role recursively.
            model=getattr(self._parent_ports.model, "child_model",
                          self._parent_ports.model),
            # A child may not prompt a human on the parent's behalf.
            interactive=False,
            # Strategy authority is not inherited. Binding a controller for a
            # child is an explicit act, and M-6 does not perform it.
            meta_controller=None,
            controller_confidence=(),
            # The child's own children run through this same runner, which is
            # what makes depth >= 3 real rather than simulated.
            child_runtime=self,
            # The parent owns the adapter and must keep it alive for the next
            # causally-ready sibling. A child may use it, never dispose it.
            environment_owner=False,
        )

    def _lower(self, plan: ChildRunPlan) -> TaskContext:
        """The child's task: lowered ceilings, inherited nothing else.

        `brief` is empty because the plan carries `goal_digest`, not prose
        (`C-06`). A child that needs the brief dereferences `goal_artifact`
        through the ordinary mediated path, under its own attenuated grant.
        """
        return TaskContext(
            brief=plan.brief,
            repo_path=self._parent_task.repo_path,
            run_id=plan.run_id,
            episode_id=plan.child_episode_id,
            principal=plan.principal,
            max_turns=plan.max_turns,
            project_id=plan.project_id,
            parent_principal_id=self._parent_task.principal,
            parent_episode_id=plan.parent_episode_id,
            preregistration=self._parent_task.preregistration,
            lineage=tuple(plan.lineage) + (plan.child_episode_id,),
            artifact_refs=plan.artifact_refs,
            scope_override=Scope(
                actions=frozenset(plan.authority),
                resources=tuple(plan.resources),
                constraints=Constraints(
                    expires_at=str(plan.constraints.get("expires_at", "2099-01-01T00:00:00.000Z")),
                    max_uses=int(plan.constraints.get("max_uses", 0)),
                    budget_usd_micros=int(plan.constraints.get("budget_usd_micros", 0)),
                    max_bytes=(
                        int(plan.constraints["max_bytes"])
                        if plan.constraints.get("max_bytes") is not None else None
                    ),
                    max_effects=(
                        int(plan.constraints["max_effects"])
                        if plan.constraints.get("max_effects") is not None else None
                    ),
                    risk_ceiling=str(plan.constraints.get("risk_ceiling", "low")),
                    max_depth=int(plan.constraints.get("max_depth", plan.max_depth)),
                    network_policy=str(plan.constraints.get("network_policy", "deny")),
                ),
                depth=plan.depth,
                sealed=True,
            ),
        )

    def _project(self, plan: ChildRunPlan, result: RunResult) -> ChildRunResult:
        """`RunResult` -> `ChildRunResult`. A projection, never a passthrough.

        This is the transcript boundary. `RunResult` holds events, receipts, a
        live store handle and a trajectory; none of it crosses. What the parent
        receives is the terminal state, the digests, the measured cost and the
        references it may choose to dereference.
        """
        terminal = getattr(result.terminal, "value", str(result.terminal))
        outcome = TERMINAL_OUTCOMES.get(terminal, "undeterminable")

        cost = self._measured_cost(plan, result)
        evidence_refs = [
            ref for ref in (result.run_digest, result.activation_digest) if ref
        ]
        # Minimal ChildRuntimePort contract doubles may expose only the
        # historical RunResult fields.  Missing trajectory means no captured
        # artifact references, never an invented one.
        trajectory = getattr(result, "trajectory", None)
        if isinstance(trajectory, Mapping):
            for artifact in trajectory.get("artifacts", ()) or ():
                if not isinstance(artifact, Mapping):
                    continue
                digest = artifact.get("digest")
                if (artifact.get("stored") is True and isinstance(digest, str)
                        and digest.startswith("sha256:") and digest not in evidence_refs):
                    evidence_refs.append(digest)

        return ChildRunResult(
            ok=outcome == "completed",
            outcome=outcome,
            terminal=terminal.upper(),
            child_episode_id=plan.child_episode_id,
            actual_cost=cost,
            turns_used=len(result.receipts),
            result_digest=result.state_digest or None,
            evidence_refs=tuple(evidence_refs),
            detail=result.detail or "",
        )

    def _measured_cost(self, plan: ChildRunPlan,
                       result: RunResult) -> Mapping[str, int]:
        """What the child actually spent, folded from its own facts.

        Read from the ledger rather than estimated. `_ZERO_COST` is prohibited
        by the trajectory contract, and a child reporting a cost it did not
        measure is precisely the fabrication this package removed.
        """
        from ..domain.ledger.agent_view import fold_agent_view
        from ..ports.child_runtime import CHILD_ADDITIVE_DIMENSIONS

        # ``RunResult.events`` is the in-process ``Event`` projection and has
        # no durable sequence.  Cost reduction is an evidence operation, so
        # read the child's persisted envelopes from its shared store instead
        # of feeding the projection to the cold reducer.
        store = getattr(result, "store", None)
        if store is None:
            # Minimal ChildRuntimePort test doubles may return only the
            # projection.  They carry no measurable ledger and therefore
            # report no measured cost; production RunResult always has a
            # store and takes the fail-closed branch below.
            envelopes = tuple(
                event for event in getattr(result, "events", ())
                if hasattr(event, "seq")
            )
            consumed = (fold_agent_view(None, envelopes).budget_consumed
                        if envelopes else {})
        else:
            read = store.read(EventRange(episode_id=plan.child_episode_id))
            if not read.ok or read.value is None:
                raise RuntimeError("child ledger is unreadable; cost is unknown")
            consumed = fold_agent_view(None, tuple(read.value)).budget_consumed
        return {
            dimension: int(consumed.get(dimension, 0) or 0)
            for dimension in CHILD_ADDITIVE_DIMENSIONS
            if consumed.get(dimension)
        }
