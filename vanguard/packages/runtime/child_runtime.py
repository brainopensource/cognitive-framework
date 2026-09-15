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

from dataclasses import dataclass, replace
from typing import Any, Callable, Mapping

from ..kernel.attenuation import Constraints, Scope
from ..ports.child_runtime import ChildRunPlan, ChildRunResult
from ..ports.evaluator import EvaluationProtocol, RunRef, Verdict
from ..ports.event_store import EventRange
from .compose import Harness, RunResult, TaskContext
from .evaluator_gateway import settlement_payload
from .workspace import (
    CombinedTree,
    PublicationAuthority,
    PublicationRefused,
    PublicationVerdict,
    WorkspaceFenceError,
)

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
        workspaces: Any = None,
        child_environment: Callable[[str, Any], Any] | None = None,
        tree_verifier: Callable[[str, Any, str], Any] | None = None,
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
        #: T-141. When bound, each child runs in its own isolated writable
        #: view instead of the parent's tree. Optional because the seam is
        #: additive: an unsupervised composition keeps its existing behaviour
        #: rather than acquiring containment it was never given.
        self._workspaces = workspaces
        #: T-141/`DIR-C5`. Builds a child-*local* effect adapter rooted at the
        #: child's own view. Supplied by the composition root, which is the
        #: only layer that knows which concrete adapter this profile runs, so
        #: the runner stays free of adapter types. Required whenever
        #: `workspaces` is bound: a contained view whose effects still land
        #: through the parent's adapter is not containment, it is a directory.
        self._child_environment = child_environment
        #: T-141/`DIR-C7`. Builds an exterior evaluator bound to one staged
        #: combined tree and the digest it must verify. Required whenever
        #: `workspaces` is bound: without it nothing outside the episode has
        #: seen the tree, and publication has nothing to revalidate.
        self._tree_verifier = tree_verifier

    def is_contained(self) -> bool:
        """Whether this runner can run a child without touching the parent.

        All three or none. A supervisor with no child-local adapter gives the
        child a directory it does not actually write to; a supervisor with no
        exterior verifier gives it work nothing outside the episode has seen.
        Either alone would let `run_composed` activate delegation that `DIR-C5`
        and `DIR-C7` do not admit, so the composition root asks this one
        question and refuses on a `False`.
        """
        return (self._workspaces is not None
                and self._child_environment is not None
                and self._tree_verifier is not None)

    # -- the port ---------------------------------------------------------

    def run_child(self, plan: ChildRunPlan) -> ChildRunResult:
        """Execute one child episode and project a typed result.

        The unauthorized entry point. It is legal only for a composition with
        no workspace supervisor -- the historical shared-tree behaviour. A
        supervised composition reaches the shared tree through publication, and
        publication needs a live authority, so it must come through
        `run_child_authorized` instead of acquiring one here.
        """
        return self.run_child_authorized(plan, None)

    def run_child_authorized(
        self, plan: ChildRunPlan, authority: PublicationAuthority | None,
    ) -> ChildRunResult:
        """Execute one child episode under the authority that dispatched it."""
        child_ports = self._rebind(plan)
        child_task = self._lower(plan)

        try:
            result = self._run_composed(
                self._harness,
                child_ports,
                child_task,
                release=self._release,
                profile=self._profile,
            )
        finally:
            self._dispose_child_environment(child_ports)
        return self._publish_workspace(
            plan, self._project(plan, result), authority)

    # -- internals --------------------------------------------------------

    def _publish_workspace(
        self,
        plan: ChildRunPlan,
        projected: ChildRunResult,
        authority: PublicationAuthority | None,
    ) -> ChildRunResult:
        """Retain the child's work, then publish it only if it earns it.

        The order is the whole crash contract (`T-141`). Retention happens
        first and unconditionally, so an accepted child's work cannot be lost
        to a crash during publication and an abandoned child's work stays
        recoverable instead of being discarded on the way out.

        Publication is second, and it is not a consequence of completion. A
        completed child has produced a *candidate*; four separate things must
        still hold before the parent's tree changes, and each is rechecked
        here rather than inherited from the moment of dispatch:

        * the **fence**, taken exclusively for the whole staging/publish pair;
        * the **base**, still the tree the candidate was computed against;
        * the **authority** -- grant unexpired, actions still carried, spend
          within what the parent has left (`PublicationAuthority.recheck`);
        * an **exterior verdict** naming the exact combined tree, obtained from
          outside the episode and never reconstructed from the child's terminal
          state (`DIR-C7`, `ADR-0076 §5`).

        Any refusal downgrades the result to `undeterminable` rather than
        raising past the adapter or reporting an ordinary success. The child
        did complete in its own view and nothing of its work is lost, but
        whether the shared tree received it is exactly the unknown
        `TERMINAL_OUTCOMES` reserves that outcome for -- and calling it `ok`
        would claim a publication that did not happen.
        """
        if self._workspaces is None:
            return projected

        child_id = plan.child_episode_id
        digest = self._workspaces.retain_candidate(child_id)
        if not projected.ok:
            return projected

        try:
            self._publish(plan, projected, authority, candidate_digest=digest)
        except (PublicationRefused, WorkspaceFenceError) as refusal:
            return replace(
                projected,
                ok=False,
                outcome="undeterminable",
                terminal="UNDETERMINABLE",
                detail=(f"{projected.detail} | not published: {refusal}"
                        if projected.detail else f"not published: {refusal}"),
            )
        return projected

    def _publish(
        self,
        plan: ChildRunPlan,
        projected: ChildRunResult,
        authority: PublicationAuthority | None,
        *,
        candidate_digest: str,
    ) -> None:
        """Stage, verify and publish one candidate. Raises to refuse."""
        if authority is None:
            raise PublicationRefused(
                "no live grant/budget authority accompanied this child; a "
                "supervised child may not publish on completion alone")
        if self._tree_verifier is None:
            raise PublicationRefused(
                "no exterior verifier is bound for the combined tree")

        child_id = plan.child_episode_id
        ticket = self._workspaces.acquire(child_id)
        try:
            combined = self._workspaces.stage(
                ticket, candidate_digest=candidate_digest)
            lapsed = authority.recheck(plan, projected.actual_cost)
            if lapsed:
                raise PublicationRefused(f"authority lapsed: {lapsed}")
            verdict = self._verify_tree(plan, combined)
            self._workspaces.publish(ticket, combined, verdict=verdict)
        finally:
            self._workspaces.release(ticket)

    def _verify_tree(
        self, plan: ChildRunPlan, combined: CombinedTree,
    ) -> PublicationVerdict:
        """What an exterior evaluator says about the exact staged tree.

        The verdict is projected through `evaluator_gateway.settlement_payload`,
        the same function that decides what may be ledgered, so publication and
        the ledger cannot disagree about whether a pass was bound. An unsigned,
        unbound or unreachable evaluator yields nothing to publish on -- there
        is no branch here that repairs missingness into a pass.
        """
        evaluator = self._tree_verifier(
            plan.child_episode_id, combined.root, combined.digest)
        if evaluator is None:
            raise PublicationRefused("no exterior evaluator was reachable")
        evaluation = evaluator.evaluate(
            RunRef(run_id=plan.run_id, episode_id=plan.child_episode_id),
            EvaluationProtocol(
                name=self._harness.evaluators[0]
                if self._harness.evaluators else "unnamed"),
        )
        verdict = evaluation.value if evaluation.ok else None
        if not isinstance(verdict, Verdict):
            raise PublicationRefused("exterior evaluation produced no verdict")

        # Candidate substitution is caught here, on the daemon's *own* bound
        # subject, before `settlement_payload` is told what runtime believes
        # the subject to be. Passing the combined digest in and then reading it
        # back out would make this check compare the tree to itself, and a
        # genuine pass about some other tree would publish this one.
        binding = verdict.binding if isinstance(verdict.binding, Mapping) else {}
        signed_subject = str(binding.get("subject_digest")
                             or binding.get("subjectDigest") or "")
        if signed_subject != combined.digest:
            raise PublicationRefused(
                f"exterior verdict is bound to {signed_subject or '<nothing>'}, "
                f"not the tree to publish {combined.digest}")

        payload = settlement_payload(
            verdict,
            task_id=plan.child_episode_id,
            terminal_status="completed",
            executed_test_count=_executed_test_count(verdict),
            verification_subject_digest=combined.digest,
        )
        if payload is None:
            raise PublicationRefused(
                "exterior verdict carries no bound signature to publish on")
        return PublicationVerdict(
            subject_digest=str(payload.get("verificationSubjectDigest")
                               or payload.get("verification_subject_digest") or ""),
            disposition=str(payload.get("disposition") or ""),
            envelope_digest=str(payload.get("envelopeDigest")
                                or payload.get("envelope_digest") or ""),
        )

    def _dispose_child_environment(self, child_ports: Any) -> None:
        """Retire the child's own adapter. The parent's is never touched."""
        if self._child_environment is None:
            return
        environment = getattr(child_ports, "environment", None)
        dispose = getattr(environment, "dispose", None)
        if callable(dispose):
            try:
                dispose()
            except Exception:  # noqa: BLE001 -- cleanup never decides an outcome
                pass

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
            # The parent owns its adapter and must keep it alive for the next
            # causally-ready sibling. When the child gets its own adapter it
            # owns that one, and `run_child_authorized` retires it.
            environment=self._environment_for(plan),
            environment_owner=self._child_environment is not None,
        )

    def _environment_for(self, plan: ChildRunPlan) -> Any:
        """The child's effect adapter (`DIR-C5`).

        Sharing the parent's adapter was the defect that kept T-141 refused at
        composition: pointing `repo_path` at an isolated view changes where the
        child *thinks* it is writing, while every `fs.write`, `patch.apply` and
        `proc.exec` still executes against the root the parent's adapter was
        constructed with. Containment has to be in the adapter or it is not
        containment. A supervised composition with no factory is refused rather
        than quietly falling back to the parent's adapter.
        """
        if self._workspaces is None:
            return self._parent_ports.environment
        if self._child_environment is None:
            raise PublicationRefused(
                "T-141: a supervised child needs a child-local effect adapter; "
                "refusing to run it against the parent's environment")
        view = self._workspaces.workspace_for(plan.child_episode_id, seed=True)
        return self._child_environment(plan.child_episode_id, view.root)

    def _lower(self, plan: ChildRunPlan) -> TaskContext:
        """The child's task: lowered ceilings, inherited nothing else.

        `brief` is empty because the plan carries `goal_digest`, not prose
        (`C-06`). A child that needs the brief dereferences `goal_artifact`
        through the ordinary mediated path, under its own attenuated grant.
        """
        return TaskContext(
            brief=plan.brief,
            repo_path=self._child_repo_path(plan),
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

    def _child_repo_path(self, plan: ChildRunPlan) -> Any:
        """Where this child may write (`T-141`, `DIR-C5`).

        Sharing the parent's tree was never containment: two causally-ready
        siblings interleaved their edits and a child could overwrite the
        parent's working state. The view is keyed by `child_episode_id`, which
        `delegation.derive_child_id` content-addresses, so a retried spawn
        lands on the same view and finds its own retained work.
        """
        if self._workspaces is None:
            return self._parent_task.repo_path
        return self._workspaces.workspace_for(
            plan.child_episode_id, seed=True).root

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
            # NT-B04. Success is read off the constrained delegation outcome,
            # and only `completed` is success. `abstained` maps to `abandoned`
            # above, so a refusal can never arrive at the parent as `ok`. The
            # child's exact termination is carried separately in `terminal`,
            # so nothing about the refusal is lost on the way up.
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
            consumed = self._actual_cost_from_settlements(envelopes)
        else:
            read = store.read(EventRange(episode_id=plan.child_episode_id))
            if not read.ok or read.value is None:
                raise RuntimeError("child ledger is unreadable; cost is unknown")
            consumed = self._actual_cost_from_settlements(tuple(read.value))
        return {
            dimension: int(consumed.get(dimension, 0) or 0)
            for dimension in CHILD_ADDITIVE_DIMENSIONS
            if consumed.get(dimension)
        }

    @staticmethod
    def _actual_cost_from_settlements(events: tuple[Any, ...]) -> Mapping[str, int]:
        """Project spend from the kernel's settlement facts.

        A committed lease records the amount returned to the parent budget;
        the child's actual spend is therefore ``reserved - settlement``.
        Feeding settlement directly into the general AgentView reducer would
        interpret a refund as negative consumption and make child projection
        fail closed for an otherwise successful run.
        """
        reserved_by_lease: dict[str, Mapping[str, int]] = {}
        total: dict[str, int] = {}
        for envelope in events:
            event_type = getattr(envelope, "event_type", None)
            payload = getattr(envelope, "payload", None)
            if not isinstance(payload, Mapping):
                continue
            if event_type == "BudgetReserved":
                lease_id = payload.get("lease_id")
                dimensions = payload.get("reserved", {})
                if isinstance(lease_id, str) and isinstance(dimensions, Mapping):
                    reserved_by_lease[lease_id] = {
                        str(key): int(value) for key, value in dimensions.items()
                    }
                continue
            if event_type != "BudgetCommitted":
                continue
            settlement = payload.get("settlement", {})
            lease_id = payload.get("lease_id")
            if not isinstance(settlement, Mapping):
                continue
            reserved = reserved_by_lease.get(lease_id, {})
            for key, value in settlement.items():
                dimension = str(key)
                amount = int(value)
                spent = int(reserved.get(dimension, 0)) - amount
                total[dimension] = total.get(dimension, 0) + spent
        return total


def _executed_test_count(verdict: Verdict) -> int:
    """How many tests the exterior evaluator says it actually executed.

    Read off the daemon's own bound claims, never inferred. Zero is the
    fail-closed answer, and `settlement_payload` turns a signed pass with zero
    executed tests into `UNDETERMINABLE` rather than a publication licence.
    """
    binding = verdict.binding if isinstance(verdict.binding, Mapping) else {}
    for key in ("executed_test_count", "executedTestCount"):
        if key in binding:
            try:
                return max(0, int(binding[key]))
            except (TypeError, ValueError):
                return 0
    return 0
