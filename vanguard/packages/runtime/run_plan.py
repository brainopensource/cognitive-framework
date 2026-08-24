"""`RunPlan` — the run identity `D_R` (`ADR-0088 §1.4`, `SPEC A-5`).

`D_H` says *what was composed*. `D_R` adds *what it was run against*: the
project under evaluation, the task, the environment, the durable store, the
model route, the exterior oracle, the root authority, the budget, and the
execution mode. The three identity subjects stay distinct and are never
collapsed — `D_X` (dataset/protocol) is added by the experiment layer above.

`run_id` and `episode_id` are correlation identifiers: they bind this plan to
its events, and they are deliberately **not** part of `D_R`. Two runs of the
same configuration must share one `D_R`, or the digest could not answer "was
this the same setup?" — which is the only question it exists to answer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from ..domain.canonicalisation.digest import digest_of
from .activation import ActivationPlan


class RunPlanError(ValueError):
    """A run identity that cannot be formed. Raised before the first turn."""


#: The execution modes the sequential reference mechanism admits. `I-11` holds
#: until M-7 measurement and an explicit Director lift, so a plan that names
#: anything else is refused here rather than discovered mid-run.
_EXECUTION_MODES = frozenset({"sequential"})


@dataclass(frozen=True, slots=True)
class RunPlan:
    """Immutably binds one frozen composition and activation to one run."""

    composition_digest: str
    activation_digest: str
    project_id: str
    run_id: str
    episode_id: str
    #: Digest of the preregistered task/brief. Preregistration is what stops a
    #: task from being edited to fit the result it got.
    task_digest: str
    #: Identity of the environment the effects land in (kind, containment).
    environment: Mapping[str, Any] = field(default_factory=dict)
    #: Identity of the durable store. `:memory:` is legible here and is exactly
    #: what disqualifies a run from certifying M-4.
    store: Mapping[str, Any] = field(default_factory=dict)
    #: Provider, model, and fingerprint. A fake or cassette route is legible.
    model_route: Mapping[str, Any] = field(default_factory=dict)
    #: The exterior evaluator identity, or `None` when evaluation is declared
    #: absent. Absent is a typed state, never a pass.
    oracle: str | None = None
    root_principal: str = ""
    budget: Mapping[str, int] = field(default_factory=dict)
    execution_mode: str = "sequential"
    run_digest: str = field(init=False)

    def __post_init__(self) -> None:
        if not self.composition_digest or not self.activation_digest:
            raise RunPlanError("a run plan binds one composition and one activation")
        if not self.project_id or not self.run_id or not self.episode_id:
            raise RunPlanError("a run plan requires project, run, and episode identity")
        if self.execution_mode not in _EXECUTION_MODES:
            raise RunPlanError(
                f"execution mode {self.execution_mode!r} is not authorized before M-7; "
                "I-11 keeps the turn loop unary and sequential")
        object.__setattr__(self, "run_digest", digest_of({
            "compositionDigest": self.composition_digest,
            "activationDigest": self.activation_digest,
            "projectId": self.project_id,
            "taskDigest": self.task_digest,
            "environment": dict(self.environment),
            "store": dict(self.store),
            "modelRoute": dict(self.model_route),
            "oracle": self.oracle,
            "rootPrincipal": self.root_principal,
            "budget": dict(self.budget),
            "executionMode": self.execution_mode,
        }))

    @property
    def durable(self) -> bool:
        """Whether the store can carry evidence past this process.

        An in-memory store is a legitimate local and test configuration. It is
        never a release configuration, and this is where that shows.
        """
        return bool(self.store.get("durable"))

    def lineage(self) -> Mapping[str, Any]:
        """The correlation identity every event and evidence row must carry."""
        return {
            "project_id": self.project_id,
            "run_id": self.run_id,
            "episode_id": self.episode_id,
            "composition_digest": self.composition_digest,
            "activation_digest": self.activation_digest,
            "run_digest": self.run_digest,
        }


def plan_run(
    activation: ActivationPlan,
    *,
    project_id: str,
    run_id: str,
    episode_id: str,
    task: str,
    environment: Mapping[str, Any] | None = None,
    store: Mapping[str, Any] | None = None,
    model_route: Mapping[str, Any] | None = None,
    oracle: str | None = None,
    root_principal: str = "",
    budget: Mapping[str, int] | None = None,
    execution_mode: str = "sequential",
) -> RunPlan:
    """Bind one activation to the run it is about to perform."""
    return RunPlan(
        composition_digest=activation.composition_digest,
        activation_digest=activation.activation_digest,
        project_id=project_id,
        run_id=run_id,
        episode_id=episode_id,
        task_digest=digest_of({"task": task}),
        environment=dict(environment or {}),
        store=dict(store or {}),
        model_route=dict(model_route or {}),
        oracle=oracle,
        root_principal=root_principal,
        budget=dict(budget or {}),
        execution_mode=execution_mode,
    )
