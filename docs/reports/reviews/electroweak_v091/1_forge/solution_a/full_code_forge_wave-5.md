---
id: report.electroweak.solution-a.full-code-forge-wave-5
class: report
authority: non-canonical
canonical_for: []
status: proposal
owner: repository-governance
version: 0.9.2a2
last_verified: 2026-08-31
---

# AETHER FORGE — Full Code Completion Manifest — Wave 5

## Completion admission, reflex state, controller guards, and runtime wiring

- Exact branch subject: `f242ced297216109736975376802f1e3dc4e29ce`.
- Backend FORGE only; frontend is excluded.
- This complement closes production integration omitted by waves 1–4.
- Code blocks contain complete affected modules or complete affected classes/functions so call sites can be changed without guessing signatures.
- Existing kernel invariants, authority, budgets, events, artifacts, and recovery remain authoritative.

## Required production delta

Implement `GoalContract`, `GoalRequirement`, and `GoalEvidence` as frozen domain
values; compose `ForgeAdmissionGate` over the existing `AdmissionGate`; never
replace the base verification semantics.  Add a runtime-owned state builder
that folds ledger events into `ForgeReflexState`, inject the resulting
`ForgeMetaController` through the already-existing `SessionPorts` seam, and
lower every directive to an ordinary proposal.  Extend composition only at the
root/session layer.  `EpisodeEngine` must continue to own the retry that returns
admission rejection to the model.  The final closure must bind the verification
receipt, task digest, workspace digest, changed-file set, and required goal IDs
at the instant FINISH is proposed.  A stale receipt, absent patch, unsatisfied
requirement, nondeterministic directive, budget expansion, or authority-bearing
directive must fail closed.

## Exact edit map

1. Add `vanguard/packages/domain/execution/goal_contract.py` with immutable goal
   and evidence contracts plus canonical serialization.
2. Modify `agency/episode/admission_gate.py`: retain `AdmissionGate`; add task
   digest binding to strict receipts and a composable FORGE wrapper.
3. Add `agency/forge/reflex.py`: independent deterministic rules only.
4. Add `runtime/forge/state_builder.py`: fold event/projection inputs; no store
   ownership and no effects.
5. Modify `runtime/meta_controller.py`: allow `fork` directives to carry only
   mode/hypothesis IDs and attenuated budget requests; preserve all guards.
6. Modify `runtime/session.py` and `runtime/root.py`: instantiate the closure and
   controller from the manifest/preset without constructing a second engine.
7. Add focused contract, runtime, recovery, and falsifier tests.

## Completion invariant

```text
FINISH accepted iff
goal required IDs are evidenced
and patch requirement is satisfied
and verification exit code is zero
and executed test count is positive
and task digest equals current task digest
and receipt workspace digest equals current workspace digest
and changed files respect the goal scope
```

## Complete affected code owners

### File: `vanguard/packages/agency/episode/admission_gate.py`

**Repository path:** `vanguard/packages/agency/episode/admission_gate.py`

```python
"""Closed-Loop Admission Gate for Episode Completion.

Prevents models from terminating coding episodes with conversational summaries unless required
source patches and verification assertions have been generated and satisfied.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence


@dataclass(frozen=True, slots=True)
class AdmissionVerdict:
    """Verdict returned by the Admission Gate."""

    admissible: bool
    reason: str
    rejection_feedback: str | None = None


@dataclass(frozen=True, slots=True)
class VerificationReceipt:
    """Minimal local-verification identity bound to the current workspace."""

    exit_code: int
    executed_test_count: int
    workspace_digest: str
    task_digest: str = ""
    receipt_digest: str = ""

    @property
    def passed(self) -> bool:
        return self.exit_code == 0 and self.executed_test_count > 0


class AdmissionGate:
    """Validates whether an episode termination proposal meets work completion criteria."""

    def __init__(self, require_patch_for_write_presets: bool = True) -> None:
        self.require_patch_for_write_presets = require_patch_for_write_presets

    def evaluate(
        self,
        preset_name: str,
        changed_files: Sequence[str],
        proposal: Mapping[str, Any],
        *,
        verification_passed: bool | None = None,
        verification: VerificationReceipt | Mapping[str, Any] | None = None,
        current_workspace_digest: str | None = None,
        task_requirements_satisfied: bool = True,
        model_requested_finish: bool = True,
    ) -> AdmissionVerdict:
        is_write_preset = any(prefix in preset_name for prefix in ("code", "bugfix", "write"))
        is_read_only = any(prefix in preset_name for prefix in ("tutor", "research", "read"))

        if not model_requested_finish:
            return AdmissionVerdict(False, "MODEL_DID_NOT_REQUEST_FINISH")

        # Read-only policy is explicit: no source patch is required, but task
        # requirements still must be satisfied. This keeps Tutor/Research
        # separate from coding/bugfix completion semantics.
        if is_read_only or not self.require_patch_for_write_presets:
            if not task_requirements_satisfied:
                return AdmissionVerdict(False, "TASK_REQUIREMENTS_UNSATISFIED")
            return AdmissionVerdict(admissible=True, reason="read_only_preset_admissible")

        # Write-capable presets MUST produce at least one changed file
        if is_write_preset and not changed_files:
            return AdmissionVerdict(
                admissible=False,
                reason="MISSING_SOURCE_PATCH",
                rejection_feedback=(
                    "ADMISSION GATE REJECTION: Episode completion was rejected because no source code "
                    "changes were detected. You MUST use `patch.apply` or `fs.write` to modify the source "
                    "files before issuing completion."
                ),
            )

        if not task_requirements_satisfied:
            return AdmissionVerdict(False, "TASK_REQUIREMENTS_UNSATISFIED")

        receipt = verification
        if isinstance(receipt, Mapping):
            receipt = VerificationReceipt(
                exit_code=int(receipt.get("exit_code", receipt.get("exitCode", -1))),
                executed_test_count=int(receipt.get("executed_test_count", receipt.get("executedTestCount", 0))),
                workspace_digest=str(receipt.get("workspace_digest", receipt.get("workspaceDigest", ""))),
                task_digest=str(receipt.get("task_digest", receipt.get("taskDigest", ""))),
                receipt_digest=str(receipt.get("receipt_digest", receipt.get("receiptDigest", ""))),
            )
        elif receipt is None and verification_passed is not None:
            # Legacy callers may provide only a boolean; it is deliberately
            # insufficient for strict admission because subject freshness is
            # not observable.
            if verification_passed is False:
                return AdmissionVerdict(False, "VERIFICATION_FAILED")
            receipt = None
        if receipt is None:
            return AdmissionVerdict(False, "VERIFICATION_REQUIRED")
        if not receipt.passed:
            return AdmissionVerdict(False, "VERIFICATION_FAILED")
        if current_workspace_digest is None or receipt.workspace_digest != current_workspace_digest:
            return AdmissionVerdict(False, "VERIFICATION_STALE")

        return AdmissionVerdict(admissible=True, reason="completion_admissible")
```

### File: `vanguard/packages/ports/meta_controller.py`

**Repository path:** `vanguard/packages/ports/meta_controller.py`

```python
"""Exterior M-6.5 meta-control contract.

The controller is a pure policy plugin. It cannot emit, access stores, call a
model, or bypass ordinary proposal and kernel authorization paths.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, Sequence

from ..domain.ledger.agent_view import AgentView
from ..domain.ledger.progress import ConfidenceRecord, ProgressView

__all__ = ["DIRECTIVE_KINDS", "MetaController", "StrategyDirective"]

DIRECTIVE_KINDS = frozenset({
    "revise_plan", "request_context", "abandon_hypothesis",
    "change_verification", "delegate", "conclude",
    "accept", "reject", "retry", "redirect", "fork", "stop",
})


@dataclass(frozen=True, slots=True)
class StrategyDirective:
    kind: str
    controller_id: str
    reason: str
    brief: str | None = None
    scope_slice: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if self.kind not in DIRECTIVE_KINDS:
            raise ValueError("unsupported strategy directive")
        if not self.controller_id or not self.reason:
            raise ValueError("controller_id and reason are required")
        if self.kind == "delegate" and not self.brief:
            raise ValueError("delegate directive requires a brief")


class MetaController(Protocol):
    """Pure between-turn consultation; no authority or side effects."""

    controller_id: str

    def assess(
        self,
        view: AgentView,
        progress: ProgressView,
        confidence: Sequence[ConfidenceRecord],
    ) -> StrategyDirective | None: ...
```

### File: `vanguard/packages/runtime/meta_controller.py`

**Repository path:** `vanguard/packages/runtime/meta_controller.py`

```python
"""Opt-in, between-turn M-6.5 controller seam.

The controller is deliberately a value-in/value-out policy hook.  This module
does not know about stores, models, capabilities, or event emitters.  Callers
must turn a returned directive into an ordinary proposal in their existing
runtime path.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from ..domain.canonicalisation.digest import digest_of
from ..domain.ledger.agent_view import AgentView
from ..domain.ledger.progress import ConfidenceRecord, ProgressView
from ..ports.meta_controller import MetaController, StrategyDirective

__all__ = [
    "ControllerInputError",
    "ControllerOutputError",
    "ControllerProposal",
    "consult",
    "directive_attribution",
    "guarded_consult",
    "validate_confidence",
    "validate_directive",
    "view_reference_set",
]


@dataclass(frozen=True, slots=True)
class ControllerProposal:
    """A normal, non-authoritative runtime proposal."""

    kind: str
    payload: Mapping[str, Any]
    attribution: Mapping[str, Any]


def directive_attribution(
    directive: StrategyDirective,
    view: AgentView,
    progress: ProgressView,
    confidence: Sequence[ConfidenceRecord],
) -> dict[str, Any]:
    refs = tuple(record.digest() for record in confidence)
    return {
        "controllerId": directive.controller_id,
        "directiveKind": directive.kind,
        "confidenceRefs": refs,
        "reasonDigest": digest_of({"reason": directive.reason}),
        "inputDigest": digest_of({"view": view.to_canonical_dict(), "progress": progress.to_dict()}),
    }


def consult(
    controller: MetaController | None,
    view: AgentView,
    progress: ProgressView,
    confidence: Sequence[ConfidenceRecord] = (),
) -> ControllerProposal | None:
    """Consult once between turns and map output to an ordinary proposal."""
    if controller is None:
        return None
    records = tuple(confidence)
    directive = controller.assess(view, progress, records)
    if directive is None:
        return None
    attribution = directive_attribution(directive, view, progress, records)
    payload: dict[str, Any] = {"reason": directive.reason}
    if directive.brief is not None:
        payload["brief"] = directive.brief
    if directive.scope_slice is not None:
        payload["scope"] = dict(directive.scope_slice)
    return ControllerProposal(kind=directive.kind, payload=payload, attribution=attribution)


# --------------------------------------------------------------------------
# M-6.5 fail-closed consultation guards (`B-M65`)
#
# `consult` above is the minimal seam: value in, value out.  A measured study
# needs more than that, because the five ways an adaptive-strategy result gets
# manufactured are all *input* or *output* defects rather than logic errors:
#
#   1. stale confidence     -- deciding on a signal computed before the last
#                              context change, so the "adaptation" is a reply
#                              to a situation that no longer exists;
#   2. missing references   -- a confidence record about a subject the view
#                              has never seen, which cannot be re-derived by a
#                              second reader and so is not evidence;
#   3. nondeterministic     -- a controller that answers differently to the
#      directives              same inputs makes paired runs incomparable;
#   4. budget bypass        -- a directive that quietly enlarges the budget it
#                              was supposed to be economising;
#   5. authority escalation -- a directive carrying capabilities, grants, or a
#                              principal, i.e. a policy plugin writing itself
#                              a permission slip.
#
# All five fail closed: `guarded_consult` raises rather than returning a
# proposal it cannot vouch for.  Metacognition stays policy, never privilege.
# --------------------------------------------------------------------------

#: Keys that would turn a routing hint into a grant.
_AUTHORITY_KEYS = frozenset({
    "capabilities", "capability", "grants", "grant", "authority", "principal",
    "uid", "role", "sink", "verb", "selector", "approval", "signature",
})
#: Keys that would let a strategy hint raise its own ceiling.
_BUDGET_KEYS = frozenset({
    "budget", "budgets", "usd_micros", "usdMicros", "millis", "tokens",
    "bytes", "turns", "depth", "limit", "limits", "ceiling", "maxBudget",
})


class ControllerInputError(ValueError):
    """The controller was consulted on inputs that cannot support a decision."""


class ControllerOutputError(ValueError):
    """The controller returned something a pure policy plugin may not return."""


def view_reference_set(view: AgentView) -> frozenset[str]:
    """Every subject a confidence record may legitimately be *about*.

    Derived from the projection, so a second reader folding the same events
    computes the same set. A reference outside it is unverifiable by
    construction, which is why it is refused rather than ignored.
    """
    # `goal` is always a legitimate subject: every lineage has exactly one,
    # and `C-06` keeps its *content* out of the ledger. Excluding the token
    # because the content is absent would make goal-level confidence
    # inexpressible on the canonical path -- which is what happened the first
    # time this guard met a real run.
    refs: set[str] = {view.lineage_id, "goal"}
    if view.goal:
        refs.add(view.goal)
    refs.update(str(key) for key in view.settled_effects)
    if view.strategy:
        refs.add(view.strategy)
    for group in (view.attempts, view.plan_revisions, view.children):
        for item in group:
            for key in ("id", "attemptId", "revisionId", "lineageId", "childLineageId"):
                value = item.get(key)
                if isinstance(value, str) and value:
                    refs.add(value)
    return frozenset(refs)


def validate_confidence(
    view: AgentView,
    confidence: Sequence[ConfidenceRecord],
) -> None:
    """Refuse unverifiable or out-of-date confidence before it is acted on."""
    known = view_reference_set(view)
    for record in confidence:
        if record.subject_ref not in known:
            raise ControllerInputError(
                f"confidence subject {record.subject_ref!r} is not in the view")
        calibration = dict(record.calibration or {})
        epoch = calibration.get("contextEpoch", calibration.get("context_epoch"))
        if epoch is None:
            raise ControllerInputError(
                "confidence record does not declare the context epoch it was "
                "computed at, so it cannot be shown to be current")
        if int(epoch) != int(view.context_epoch):
            raise ControllerInputError(
                f"confidence for epoch {epoch} is stale at epoch {view.context_epoch}")


def validate_directive(
    directive: StrategyDirective,
    *,
    remaining_budget: Mapping[str, int] | None = None,
) -> None:
    """Refuse a directive that reaches for authority or budget it was not given."""
    slice_ = dict(directive.scope_slice or {})
    for key in slice_:
        lowered = str(key)
        if lowered in _AUTHORITY_KEYS:
            raise ControllerOutputError(
                f"directive scope carries authority key {key!r}; a controller "
                f"proposes, it does not grant")
    for key, value in slice_.items():
        if str(key) in _BUDGET_KEYS or str(key).startswith("max"):
            if remaining_budget is None:
                raise ControllerOutputError(
                    f"directive scope names budget key {key!r} with no "
                    f"remaining-budget ceiling to check it against")
            dimension = _BUDGET_ALIASES.get(str(key), str(key))
            ceiling = remaining_budget.get(dimension)
            if ceiling is None:
                raise ControllerOutputError(
                    f"directive scope names unknown budget dimension {key!r}")
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise ControllerOutputError(
                    f"budget slice {key!r} must be a non-negative integer")
            if value > ceiling:
                raise ControllerOutputError(
                    f"directive requests {value} of {dimension} but only "
                    f"{ceiling} remains; a controller cannot enlarge a budget")
    try:
        digest_of(slice_)
    except Exception as exc:  # pragma: no cover - defensive
        raise ControllerOutputError(
            "directive scope must be a plain value, not a runtime handle") from exc


#: `maxTurns` is the spelling a delegate slice uses for the `turns` dimension.
_BUDGET_ALIASES: Mapping[str, str] = {
    "maxTurns": "turns", "max_turns": "turns",
    "maxDepth": "depth", "max_depth": "depth",
    "maxTokens": "tokens", "max_tokens": "tokens",
    "maxMillis": "millis", "max_millis": "millis",
    "maxBytes": "bytes", "max_bytes": "bytes",
    "usdMicros": "usd_micros", "maxUsdMicros": "usd_micros",
}


def guarded_consult(
    controller: MetaController | None,
    view: AgentView,
    progress: ProgressView,
    confidence: Sequence[ConfidenceRecord] = (),
    *,
    remaining_budget: Mapping[str, int] | None = None,
    determinism_samples: int = 2,
) -> ControllerProposal | None:
    """`consult` with every M-6.5 falsifier applied, fail-closed.

    This is the form a measured study and a runtime integration must use.  It
    is deliberately separate from `consult`: the seam stays minimal for the
    callers that only need the value mapping, while anything that will be
    *reported as evidence* goes through the guarded path.
    """
    if controller is None:
        return None
    records = tuple(confidence)
    validate_confidence(view, records)

    directive = controller.assess(view, progress, records)
    for _ in range(max(0, determinism_samples - 1)):
        again = controller.assess(view, progress, records)
        if again != directive:
            raise ControllerOutputError(
                "controller returned different directives for identical inputs; "
                "paired runs cannot be compared against a nondeterministic arm")
    if directive is None:
        return None
    validate_directive(directive, remaining_budget=remaining_budget)

    attribution = directive_attribution(directive, view, progress, records)
    payload: dict[str, Any] = {"reason": directive.reason}
    if directive.brief is not None:
        payload["brief"] = directive.brief
    if directive.scope_slice is not None:
        payload["scope"] = dict(directive.scope_slice)
    return ControllerProposal(kind=directive.kind, payload=payload,
                              attribution=attribution)
```

### File: `vanguard/packages/domain/ledger/progress.py`

**Repository path:** `vanguard/packages/domain/ledger/progress.py`

```python
"""Pure M-6.5 progress and confidence projections.

These types derive observations from ledger events. They do not emit events,
invoke models, grant authority, or make scheduling decisions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

from ..canonicalisation.digest import digest_of

__all__ = [
    "ConfidenceRecord",
    "ProgressProjection",
    "ProgressView",
    "SemanticCheckpointRef",
    "fold_progress",
    "fold_progress_projection",
]


@dataclass(frozen=True, slots=True)
class SemanticCheckpointRef:
    """`ADR-0103`: semantic reference binding (run_id, episode_id, epoch, attempt)."""

    run_id: str
    episode_id: str
    epoch: int = 0
    attempt: int = 0

    def __post_init__(self) -> None:
        if not self.run_id or not self.episode_id:
            raise ValueError("run_id and episode_id are required")
        if self.epoch < 0 or self.attempt < 0:
            raise ValueError("epoch and attempt must be non-negative integers")

    def to_dict(self) -> dict[str, Any]:
        return {
            "runId": self.run_id,
            "episodeId": self.episode_id,
            "epoch": self.epoch,
            "attempt": self.attempt,
        }

    def digest(self) -> str:
        return digest_of(self.to_dict())


@dataclass(frozen=True, slots=True)
class ProgressProjection:
    """`ProgressProjection/2` (`ADR-0103`): derived projection from the ledger."""

    verified_delta: float = 0.0
    failed_unknown_rate: float = 0.0
    repeat_entropy: float = 0.0
    novelty: float = 0.0
    normalized_burn: float = 0.0
    revision_effectiveness: float = 0.0
    calibrated_uncertainty: float = 0.0
    schema: str = "ProgressProjection/2"

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "verifiedDelta": round(self.verified_delta, 6),
            "failedUnknownRate": round(self.failed_unknown_rate, 6),
            "repeatEntropy": round(self.repeat_entropy, 6),
            "novelty": round(self.novelty, 6),
            "normalizedBurn": round(self.normalized_burn, 6),
            "revisionEffectiveness": round(self.revision_effectiveness, 6),
            "calibratedUncertainty": round(self.calibrated_uncertainty, 6),
        }

    def digest(self) -> str:
        return digest_of(self.to_dict())



@dataclass(frozen=True, slots=True)
class ConfidenceRecord:
    signal: str
    value: float
    subject_ref: str
    basis: tuple[str, ...] = ()
    calibration: Mapping[str, Any] | None = None

    def __post_init__(self) -> None:
        if self.signal not in {"self_report", "logprob", "behavioral", "external_verifier", "ensemble_disagreement"}:
            raise ValueError("unsupported confidence signal")
        if not 0.0 <= self.value <= 1.0:
            raise ValueError("confidence value must be between 0 and 1")
        if not self.subject_ref:
            raise ValueError("confidence subject_ref is required")
        if not self.basis or any(not isinstance(item, str) or not item for item in self.basis):
            raise ValueError("confidence evidence basis is required")
        if self.calibration is None or not isinstance(self.calibration, Mapping):
            raise ValueError("confidence calibration metadata is required")
        # Freeze the externally supplied mapping at the value boundary.  A
        # mutable calibration dict must not change a record's digest later.
        object.__setattr__(self, "calibration", dict(self.calibration))

    @property
    def subject(self) -> str:
        return self.subject_ref

    @property
    def context_epoch(self) -> int | None:
        if not self.calibration:
            return None
        epoch = self.calibration.get("contextEpoch", self.calibration.get("context_epoch"))
        return int(epoch) if epoch is not None else None

    def digest(self) -> str:
        return digest_of({"signal": self.signal, "value": self.value,
                          "subjectRef": self.subject_ref, "basis": self.basis,
                          "calibration": dict(self.calibration)})


@dataclass(frozen=True, slots=True)
class ProgressView:
    assessment: str | None = None
    stall_count: int = 0
    repeat_signatures: tuple[str, ...] = ()
    budget_burn_rate: float = 0.0
    last_change: str | None = None
    confidence_digests: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {"assessment": self.assessment, "stallCount": self.stall_count,
                "repeatSignatures": self.repeat_signatures,
                "budgetBurnRate": self.budget_burn_rate,
                "lastChange": self.last_change}


def _payload(event: Mapping[str, Any]) -> Mapping[str, Any]:
    payload = event.get("payload", event)
    return payload if isinstance(payload, Mapping) else {}


def fold_progress(events: Iterable[Mapping[str, Any]]) -> ProgressView:
    """Derive progress signals deterministically from event payloads."""
    assessment: str | None = None
    stalls = 0
    repeats: list[str] = []
    last_change: str | None = None
    budgets: list[float] = []
    for event in events:
        payload = _payload(event)
        kind = str(payload.get("kind", event.get("kind", "")))
        if kind == "ProgressAssessed":
            value = payload.get("assessment")
            if isinstance(value, str):
                assessment = value
                stalls = stalls + 1 if value in {"stalled", "regressing"} else 0
            signals = payload.get("signals")
            if isinstance(signals, Mapping):
                consumed = signals.get("budgetConsumed")
                if isinstance(consumed, (int, float)) and not isinstance(consumed, bool):
                    budgets.append(float(consumed))
        elif kind == "EffectFailed":
            stalls += 1
        elif kind == "StrategyChanged":
            value = payload.get("to", payload.get("toStrategy"))
            if isinstance(value, str):
                last_change = value
        signature = payload.get("repeatSignature", payload.get("repeat_signature"))
        if isinstance(signature, str) and signature not in repeats:
            repeats.append(signature)
    rate = (budgets[-1] - budgets[0]) / (len(budgets) - 1) if len(budgets) > 1 else 0.0
    return ProgressView(assessment=assessment, stall_count=stalls,
                        repeat_signatures=tuple(repeats), budget_burn_rate=rate,
                        last_change=last_change)


def fold_progress_projection(
    events: Iterable[Mapping[str, Any]],
    confidence: Sequence[ConfidenceRecord] = (),
) -> ProgressProjection:
    """Derive `ProgressProjection/2` deterministically from events and confidence."""
    total_effects = 0
    failed_effects = 0
    descriptors: list[str] = []
    revisions = 0
    revision_successes = 0
    recent_revision = False
    budgets: list[float] = []

    for event in events:
        payload = _payload(event)
        kind = str(payload.get("kind", event.get("kind", "")))
        if kind in {"EffectCompleted", "EffectFailed", "EffectReconciled", "EffectRejected", "AuthorizationDenied"}:
            total_effects += 1
            if kind in {"EffectFailed", "EffectRejected", "AuthorizationDenied"}:
                failed_effects += 1
                recent_revision = False
            else:
                if recent_revision:
                    revision_successes += 1
                    recent_revision = False
            descriptor = payload.get("descriptorDigest", payload.get("repeatSignature"))
            if isinstance(descriptor, str):
                descriptors.append(descriptor)
        elif kind == "StrategyChanged":
            revisions += 1
            recent_revision = True
        elif kind == "ProgressAssessed":
            signals = payload.get("signals")
            if isinstance(signals, Mapping):
                consumed = signals.get("budgetConsumed")
                if isinstance(consumed, (int, float)) and not isinstance(consumed, bool):
                    budgets.append(float(consumed))

    failed_unknown_rate = (failed_effects / total_effects) if total_effects > 0 else 0.0
    unique_desc = set(descriptors)
    novelty = (len(unique_desc) / len(descriptors)) if descriptors else 1.0

    repeat_count = len(descriptors) - len(unique_desc)
    repeat_entropy = (repeat_count / len(descriptors)) if descriptors else 0.0

    normalized_burn = (budgets[-1] - budgets[0]) / (len(budgets) - 1) if len(budgets) > 1 else 0.0
    revision_eff = (revision_successes / revisions) if revisions > 0 else 1.0

    uncertainties = [1.0 - c.value for c in confidence]
    calibrated_unc = (sum(uncertainties) / len(uncertainties)) if uncertainties else 0.0

    return ProgressProjection(
        verified_delta=0.0,
        failed_unknown_rate=failed_unknown_rate,
        repeat_entropy=repeat_entropy,
        novelty=novelty,
        normalized_burn=normalized_burn,
        revision_effectiveness=revision_eff,
        calibrated_uncertainty=calibrated_unc,
    )

```

### File: `vanguard/packages/domain/ledger/agent_view.py`

**Repository path:** `vanguard/packages/domain/ledger/agent_view.py`

```python
"""Deterministic event-derived AgentView projection for M-5a.

AgentView is a projection, never a second source of truth. It can be rebuilt
from a file-backed event sequence in a fresh process and therefore contains no
runtime handles, clocks, caches, or authority decisions.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Iterable, Mapping

from ..canonicalisation.digest import digest_of
from .events import EventEnvelope, READABLE_KINDS
from .reducer import ReducerError

__all__ = [
    "AGENT_VIEW_REDUCER_VERSION",
    "AgentView",
    "AgentViewCheckpoint",
    "fold_agent_view",
]

AGENT_VIEW_REDUCER_VERSION = "m5a.agent_view/1"
_TERMINAL_KINDS = frozenset({"EpisodeCompleted", "RunCompleted", "RunAborted", "RunRecovered"})
_EFFECT_KINDS = frozenset({"EffectCompleted", "EffectFailed", "EffectRejected", "EffectReconciled"})
_BUDGET_KINDS = frozenset({"BudgetCommitted", "BudgetExhausted"})


@dataclass(frozen=True, slots=True)
class AgentView:
    lineage_id: str
    goal: str | None = None
    plan_revisions: tuple[Mapping[str, Any], ...] = field(default_factory=tuple)
    attempts: tuple[Mapping[str, Any], ...] = field(default_factory=tuple)
    settled_effects: Mapping[str, str] = field(default_factory=dict)
    budget_consumed: Mapping[str, int] = field(default_factory=dict)
    strategy: str | None = None
    progress_log: tuple[Mapping[str, Any], ...] = field(default_factory=tuple)
    context_epoch: int = 0
    children: tuple[Mapping[str, Any], ...] = field(default_factory=tuple)
    terminal: str | None = None
    covered_through: str = ""
    reducer_version: str = AGENT_VIEW_REDUCER_VERSION

    def to_canonical_dict(self) -> dict[str, Any]:
        """Return the stable JSON-shaped projection used by RF-96."""

        return {
            "lineageId": self.lineage_id,
            "goal": self.goal,
            "planRevisions": [dict(item) for item in self.plan_revisions],
            "attempts": [dict(item) for item in self.attempts],
            "settledEffects": dict(sorted(self.settled_effects.items())),
            "budgetConsumed": dict(sorted(self.budget_consumed.items())),
            "strategy": self.strategy,
            "progressLog": [dict(item) for item in self.progress_log],
            "contextEpoch": self.context_epoch,
            "children": [dict(item) for item in self.children],
            "terminal": self.terminal,
            "coveredThrough": self.covered_through,
            "reducerVersion": self.reducer_version,
        }

    def digest(self) -> str:
        return digest_of(self.to_canonical_dict())

    @classmethod
    def empty(cls, lineage_id: str = "") -> "AgentView":
        """Construct an initial empty AgentView."""
        return cls(lineage_id=lineage_id)

    @staticmethod
    def fold(
        events: Iterable[EventEnvelope],
        checkpoint: AgentViewCheckpoint | None = None,
    ) -> "AgentView":
        """Deterministic fold of events into an AgentView."""
        return fold_agent_view(checkpoint, events)


@dataclass(frozen=True, slots=True)
class AgentViewCheckpoint:
    """Runtime-neutral checkpoint value consumed by a future CheckpointManager."""

    view: AgentView
    state_digest: str
    covered_through_event_id: str
    covered_through_seq: str
    reducer_version: str = AGENT_VIEW_REDUCER_VERSION


def _kind(event: EventEnvelope) -> str:
    return str(event.payload.get("kind") or event.mhf_kind or "")


def _lineage(event: EventEnvelope) -> str:
    return str(event.principal_id or event.payload.get("lineageId") or event.principal)


def _effect_key(payload: Mapping[str, Any]) -> str | None:
    return payload.get("idempotencyKey") or payload.get("idempotency_key") or payload.get("descriptorDigest")


def _copy_payload(payload: Mapping[str, Any], *, event: EventEnvelope) -> dict[str, Any]:
    """Copy only JSON values and bind the event identity without raw context."""

    return {
        "eventId": event.event_id,
        "seq": event.seq,
        **{str(key): value for key, value in payload.items() if key != "kind"},
    }


def fold_agent_view(
    checkpoint: AgentViewCheckpoint | None,
    events: Iterable[EventEnvelope],
) -> AgentView:
    """Fold one lineage deterministically, optionally from a trusted checkpoint.

    A checkpoint is only a starting projection. Events at or before its covered
    sequence are ignored; all later events are validated and folded. A caller
    must verify blob bytes and reducer pins before constructing the checkpoint.
    """

    if checkpoint is not None:
        if checkpoint.reducer_version != AGENT_VIEW_REDUCER_VERSION:
            raise ReducerError("AgentView checkpoint reducer version is not current")
        view = checkpoint.view
        covered_seq = int(checkpoint.covered_through_seq)
        last_seq = covered_seq
    else:
        view = AgentView(lineage_id="")
        last_seq = -1

    plans = list(view.plan_revisions)
    attempts = [dict(item) for item in view.attempts]
    settled = dict(view.settled_effects)
    budget = {key: int(value) for key, value in view.budget_consumed.items()}
    progress = list(view.progress_log)
    children = [dict(item) for item in view.children]
    goal = view.goal
    strategy = view.strategy
    context_epoch = view.context_epoch
    terminal = view.terminal
    covered_through = view.covered_through
    lineage_id = view.lineage_id

    for event in events:
        seq = int(event.seq)
        if seq <= last_seq:
            continue
        if lineage_id and _lineage(event) != lineage_id:
            raise ReducerError(
                f"event {event.event_id} belongs to lineage {_lineage(event)!r}, "
                f"expected {lineage_id!r}"
            )
        if not lineage_id:
            lineage_id = _lineage(event)
        kind = _kind(event)
        if kind not in READABLE_KINDS:
            raise ReducerError(f"event kind is not readable: {kind!r}")
        payload = event.payload

        if kind == "GoalDeclared":
            goal = payload.get("goalDigest") or payload.get("goalArtifact")
        elif kind == "PlanRevised":
            plans.append(_copy_payload(payload, event=event))
        elif kind == "StrategyChanged":
            strategy = payload.get("to") or payload.get("toStrategy")
        elif kind == "ProgressAssessed":
            progress.append(_copy_payload(payload, event=event))
        elif kind == "ContextCompacted":
            context_epoch += 1
        elif kind == "ProposalProduced":
            attempts.append({
                "eventId": event.event_id,
                "operationId": payload.get("operationId") or event.event_id,
                # Production `/2` events use `action`; older readable history
                # used `verb` or `operatorId`.
                "verb": payload.get("action") or payload.get("verb") or payload.get("operatorId") or "unknown",
                "status": "proposed",
            })
        elif kind == "EffectStarted":
            attempts.append({
                "eventId": event.event_id,
                "operationId": payload.get("operationId") or payload.get("descriptorDigest") or event.event_id,
                "verb": payload.get("action") or payload.get("verb") or "effect",
                "status": "dispatched",
            })
        elif kind in _EFFECT_KINDS:
            key = _effect_key(payload)
            status = str(payload.get("status") or payload.get("outcome") or {
                "EffectCompleted": "settled",
                "EffectFailed": "failed",
                "EffectRejected": "rejected",
                "EffectReconciled": "reconciled",
            }[kind])
            if key:
                settled[key] = status
            operation_id = payload.get("operationId") or key
            if operation_id:
                attempts.append({
                    "eventId": event.event_id,
                    "operationId": operation_id,
                    "verb": payload.get("action") or payload.get("verb") or "effect",
                    "status": status,
                })
        elif kind in _BUDGET_KINDS:
            for key, value in (payload.get("debits") or payload.get("settlement") or payload.get("dimensions") or {}).items():
                if key in {"usd_micros", "millis", "tokens", "bytes"}:
                    budget[key] = budget.get(key, 0) + int(value)
        elif kind == "ChildSpawned":
            child_id = payload.get("childEpisodeId") or payload.get("childLineageId") or payload.get("childId")
            if child_id:
                children.append({"childId": child_id, "status": "open", **_copy_payload(payload, event=event)})
        elif kind == "ChildReturned":
            child_id = payload.get("childEpisodeId") or payload.get("childLineageId") or payload.get("childId")
            for index, child in enumerate(children):
                if child.get("childId") == child_id:
                    children[index] = {**child, "status": payload.get("status") or payload.get("outcome") or "returned", **_copy_payload(payload, event=event)}
        elif kind in _TERMINAL_KINDS:
            terminal = str(payload.get("outcome") or payload.get("status") or kind)

        last_seq = seq
        covered_through = event.event_id

    if not lineage_id:
        raise ReducerError("cannot construct AgentView from an empty event sequence")
    return replace(
        view,
        lineage_id=lineage_id,
        goal=goal,
        plan_revisions=tuple(plans),
        attempts=tuple(attempts),
        settled_effects=dict(sorted(settled.items())),
        budget_consumed=dict(sorted(budget.items())),
        strategy=strategy,
        progress_log=tuple(progress),
        context_epoch=context_epoch,
        children=tuple(children),
        terminal=terminal,
        covered_through=covered_through,
        reducer_version=AGENT_VIEW_REDUCER_VERSION,
    )
```

## Required focused tests

- completion without a patch is rejected for FORGE write presets;
- completion with a Boolean-only legacy verification flag is rejected;
- receipt for an earlier workspace digest is rejected;
- receipt for a different task digest is rejected;
- missing required goal IDs are returned in model-visible feedback;
- repeated FINISH consumes retry budget and cannot loop without bound;
- identical controller inputs produce identical directives;
- stale confidence fails before controller invocation;
- controller cannot add capabilities, principals, grants, approvals, or budgets;
- recovered execution reconstructs the same admission state from ledger events;
- controller absence preserves the current Vanguard behavior exactly.

## Minimal validation commands

```bash
python3 -m unittest test.agency.test_episode -v
python3 -m unittest test.falsifiers.test_m65_controller_falsifiers -v
python3 -m unittest test.runtime.test_m65_m7_m8_seams -v
python3 tools/linters/check_boundaries.py
python3 tools/linters/check_domain_blindness.py
python3 tools/linters/check_tcb_budget.py
```
