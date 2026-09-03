"""CoordinationPlan: the declared shape of a multi-agent run.

A topology is *data*, not code. Adding "planner -> implementer -> verifier" must
not mean adding a second scheduler; it means declaring three roles and two
dependencies. This module holds the value types and their validation. The
runtime scheduler (runtime/coordination.py) executes them via `agent.spawn`,
under attenuated budgets, exchanging only events and content-addressed
artifacts.

Deliberately absent: any notion of an unrestricted swarm. A plan is a DAG with
declared quotas, and it is rejected if it is not.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Sequence

from ..canonicalisation.digest import digest_of

__all__ = [
    "MergePolicy",
    "Role",
    "CoordinationPlan",
    "CoordinationError",
    "planner_implementer_verifier",
    "parallel_investigators",
    "implementer_with_reviewer",
    "TOPOLOGIES",
]


class CoordinationError(ValueError):
    """The declared plan is not executable. Raised at construction, not at run."""


class MergePolicy(str, Enum):
    """How a role's several inputs become one input."""

    #: Every dependency's artifact is passed through, ordered by role name.
    CONCAT = "concat"
    #: A single role's output wins; used when investigators are redundant.
    FIRST_COMPLETE = "first_complete"
    #: Inputs are handed to a synthesiser role which produces the merged view.
    SYNTHESISE = "synthesise"
    #: All dependencies must agree on a verdict or the step fails.
    UNANIMOUS = "unanimous"


@dataclass(frozen=True, slots=True)
class Role:
    """One participant. A role is a projection, not a process.

    ``budget_share`` is a per-mille slice of the parent's budget. Shares are
    checked to sum to at most 1000 across the plan, which is what makes budget
    conservation structural rather than aspirational.
    """

    name: str
    #: Manifest/preset the child episode is composed from.
    composition: str
    #: Role names this one waits for.
    depends_on: tuple[str, ...] = ()
    #: Per-mille of the parent budget. 250 == 25%.
    budget_share: int = 0
    #: Maximum turns for this child. A hard ceiling, not a suggestion.
    max_turns: int = 20
    merge: MergePolicy = MergePolicy.CONCAT
    #: Artifact kinds this role is allowed to publish to its mailbox.
    publishes: tuple[str, ...] = ()
    #: Model role label, matched against ModelBehaviorProfile.eligible_roles.
    model_role: str = "implementer"
    #: When true a failure of this role fails the whole plan; otherwise the
    #: plan proceeds with the remaining outputs.
    required: bool = True

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise CoordinationError("role name must be non-empty")
        if not self.composition.strip():
            raise CoordinationError(f"role {self.name!r} needs a composition")
        if not 0 <= self.budget_share <= 1000:
            raise CoordinationError(
                f"role {self.name!r} budget_share must be per-mille in [0, 1000]")
        if self.max_turns <= 0:
            raise CoordinationError(f"role {self.name!r} max_turns must be positive")
        if self.name in self.depends_on:
            raise CoordinationError(f"role {self.name!r} depends on itself")
        if len(set(self.depends_on)) != len(self.depends_on):
            raise CoordinationError(f"role {self.name!r} has duplicate dependencies")

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "composition": self.composition,
            "depends_on": list(self.depends_on),
            "budget_share": self.budget_share,
            "max_turns": self.max_turns,
            "merge": self.merge.value,
            "publishes": list(self.publishes),
            "model_role": self.model_role,
            "required": self.required,
        }


@dataclass(frozen=True, slots=True)
class CoordinationPlan:
    """A validated DAG of roles with conserved budget.

    Validation happens once, at construction. By the time the scheduler sees a
    plan it is known acyclic, fully resolved, and within budget — so the
    scheduler contains no error handling for those cases at all.
    """

    name: str
    roles: tuple[Role, ...]
    #: Correlation id tying every child lineage back to this plan instance.
    correlation_id: str = ""
    #: Wall-clock ceiling for the whole plan.
    deadline_millis: int = 600_000
    #: Maximum children alive at once. Bounds fan-out explicitly.
    max_concurrency: int = 4

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise CoordinationError("plan name must be non-empty")
        if not self.roles:
            raise CoordinationError("a plan needs at least one role")
        if self.max_concurrency <= 0:
            raise CoordinationError("max_concurrency must be positive")
        if self.deadline_millis <= 0:
            raise CoordinationError("deadline_millis must be positive")

        names = [role.name for role in self.roles]
        if len(set(names)) != len(names):
            raise CoordinationError("duplicate role names in plan")

        known = set(names)
        for role in self.roles:
            unknown = set(role.depends_on) - known
            if unknown:
                raise CoordinationError(
                    f"role {role.name!r} depends on unknown role(s): {sorted(unknown)}")

        total = sum(role.budget_share for role in self.roles)
        if total > 1000:
            raise CoordinationError(
                f"budget shares sum to {total} per-mille; a plan may not exceed 1000")

        # Cycle detection. A cyclic plan would deadlock the scheduler, so it is
        # rejected here rather than discovered at runtime.
        self._assert_acyclic()

    def _assert_acyclic(self) -> None:
        dependencies = {role.name: set(role.depends_on) for role in self.roles}
        resolved: set[str] = set()
        # Kahn's algorithm: repeatedly retire roles with no unresolved deps.
        progress = True
        while progress:
            progress = False
            for name, deps in dependencies.items():
                if name not in resolved and deps <= resolved:
                    resolved.add(name)
                    progress = True
        if len(resolved) != len(dependencies):
            stuck = sorted(set(dependencies) - resolved)
            raise CoordinationError(f"plan contains a dependency cycle among {stuck}")

    # -- scheduling views --------------------------------------------------

    @property
    def waves(self) -> tuple[tuple[Role, ...], ...]:
        """Roles grouped into dependency waves; each wave may run in parallel.

        This is the only scheduling primitive the runtime needs: run wave 0,
        collect artifacts, run wave 1, and so on.
        """
        by_name = {role.name: role for role in self.roles}
        resolved: set[str] = set()
        waves: list[tuple[Role, ...]] = []
        remaining = set(by_name)
        while remaining:
            ready = sorted(
                name for name in remaining
                if set(by_name[name].depends_on) <= resolved
            )
            if not ready:  # unreachable: construction proved acyclicity
                raise CoordinationError("unschedulable plan")
            waves.append(tuple(by_name[name] for name in ready))
            resolved.update(ready)
            remaining -= set(ready)
        return tuple(waves)

    def role(self, name: str) -> Role:
        for candidate in self.roles:
            if candidate.name == name:
                return candidate
        raise CoordinationError(f"unknown role {name!r}")

    def attenuated_budget(self, role_name: str, parent_budget: Mapping[str, int]
                          ) -> dict[str, int]:
        """The child's budget: the parent's, scaled by the role's share.

        Always rounds *down*, so the sum of children can never exceed the
        parent. Budget conservation is arithmetic here, not policy.
        """
        share = self.role(role_name).budget_share
        return {
            dimension: (int(amount) * share) // 1000
            for dimension, amount in parent_budget.items()
            if isinstance(amount, int) and amount >= 0
        }

    @property
    def digest(self) -> str:
        return digest_of(self.to_dict())

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "roles": [role.to_dict() for role in self.roles],
            "deadline_millis": self.deadline_millis,
            "max_concurrency": self.max_concurrency,
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "CoordinationPlan":
        if not isinstance(raw, Mapping) or not raw.get("roles"):
            raise CoordinationError("plan payload requires roles")
        roles = tuple(
            Role(
                name=str(entry["name"]),
                composition=str(entry.get("composition", "")),
                depends_on=tuple(entry.get("depends_on") or ()),
                budget_share=int(entry.get("budget_share", 0)),
                max_turns=int(entry.get("max_turns", 20)),
                merge=MergePolicy(entry.get("merge", "concat")),
                publishes=tuple(entry.get("publishes") or ()),
                model_role=str(entry.get("model_role", "implementer")),
                required=bool(entry.get("required", True)),
            )
            for entry in raw["roles"]
        )
        return cls(
            name=str(raw.get("name", "plan")),
            roles=roles,
            correlation_id=str(raw.get("correlation_id", "")),
            deadline_millis=int(raw.get("deadline_millis", 600_000)),
            max_concurrency=int(raw.get("max_concurrency", 4)),
        )


# --------------------------------------------------------------------------
# The three qualified topologies. Start here; do not invent a swarm.
# --------------------------------------------------------------------------


def planner_implementer_verifier(*, composition: str = "vg-code-balanced") -> CoordinationPlan:
    """Sequential pipeline. The baseline every other topology is measured against."""
    return CoordinationPlan(
        name="planner_implementer_verifier",
        roles=(
            Role("planner", composition, budget_share=200, max_turns=8,
                 publishes=("plan",), model_role="planner"),
            Role("implementer", composition, depends_on=("planner",),
                 budget_share=550, max_turns=30, publishes=("patch",),
                 model_role="implementer"),
            Role("verifier", composition, depends_on=("implementer",),
                 budget_share=250, max_turns=10, publishes=("verification",),
                 model_role="verifier"),
        ),
        max_concurrency=1,
    )


def parallel_investigators(
    *, count: int = 3, composition: str = "vg-research",
) -> CoordinationPlan:
    """Fan-out investigation into a single synthesiser.

    Investigators are non-required: the synthesiser works from whatever came
    back, so one dead branch does not fail the plan.
    """
    if not 2 <= count <= 6:
        raise CoordinationError("parallel investigators must number between 2 and 6")
    share = 600 // count
    investigators = tuple(
        Role(f"investigator_{index}", composition, budget_share=share, max_turns=12,
             publishes=("finding",), model_role="implementer", required=False)
        for index in range(count)
    )
    synthesizer = Role(
        "synthesizer", composition,
        depends_on=tuple(role.name for role in investigators),
        budget_share=300, max_turns=12, merge=MergePolicy.SYNTHESISE,
        publishes=("report",), model_role="synthesizer",
    )
    return CoordinationPlan(
        name="parallel_investigators",
        roles=(*investigators, synthesizer),
        max_concurrency=count,
    )


def implementer_with_reviewer(*, composition: str = "vg-code-max") -> CoordinationPlan:
    """Implementer plus a bounded reviewer.

    The reviewer gets a deliberately small turn budget: review is advisory and
    must not become a second implementation loop.
    """
    return CoordinationPlan(
        name="implementer_with_reviewer",
        roles=(
            Role("implementer", composition, budget_share=650, max_turns=30,
                 publishes=("patch",), model_role="implementer"),
            Role("reviewer", composition, depends_on=("implementer",),
                 budget_share=250, max_turns=6, publishes=("review",),
                 model_role="reviewer", required=False),
        ),
        max_concurrency=1,
    )


#: Named catalog, so a manifest can request a topology by string.
TOPOLOGIES = {
    "planner_implementer_verifier": planner_implementer_verifier,
    "parallel_investigators": parallel_investigators,
    "implementer_with_reviewer": implementer_with_reviewer,
}
