---
id: adr-0107-dir3-seam-types
adr: "0107"
class: decision
authority: binding-decision
canonical_for:
  - decision-0107-dir3-seam-types
status: living
owner: engineering-director
version: "1.0"
last_verified: 2026-09-13
decision_status: accepted
---

# ADR-0107 — D-1: three typed integration seams

The three seams use frozen, slotted value dataclasses and the existing `Result[T]`/`PortFailure`, with immutable tuples, existing canonical digests, `Symbol`, `WorkspaceEpoch` and `SemanticTaskState`; they add no event kind, serializer, store or model-callable authority surface.
C owns `IndexSelection` at the index port, A owns `TaskRevision` with task-state domain values, and B owns `CallerAdmissionEvidence` in the pure agency completeness policy; this is explicit authorization for these value types, not a new public service port.
The field inventory below is the cross-lane contract, while private helpers and module splits remain senior decisions.

| Type | Fields and field types |
|---|---|
| `IndexSelection` | `backend: Literal["lda", "file"]`; `source_identity: WorkspaceEpoch`; `health_verdict: Literal["healthy_current", "optional_absent", "present_invalid", "required_unbound", "subject_changed"]`; `degradation_reason: str | None`; `unresolved_coverage: bool` |
| `TaskRevision` | `revision_id: str` (canonical request digest); `target_binding: tuple[str, str, str, str]` in order run ID, episode ID, task digest, composition digest; `expected_revision: int`; `expected_state_digest: str`; `mutated_fields: tuple[TaskMutableField, ...]`; `proposed_state: SemanticTaskState`; `authority_proof: str` (reference to authenticated dispatch/grant evidence) |
| `CallerAdmissionEvidence` | `changed_public_symbols: tuple[Symbol, ...]`; `inspected_callers: tuple[Symbol, ...]`; `updated_callers: tuple[Symbol, ...]`; `inspection_receipts: tuple[tuple[Symbol, str], ...]`; `update_receipts: tuple[tuple[Symbol, str], ...]`; `omissions: tuple[str, ...]`; `candidate_identity: tuple[str, str, str]` in order task digest, composition digest, whole submitted tree digest; `source_identity: WorkspaceEpoch`; `unresolved_coverage: bool` |

The five DIR-I5 states are selection branches, not five failures: healthy current succeeds, optional absence succeeds only with a current File selection, present invalid succeeds only with a current permitted File fallback and a recorded cause, required unbound returns `Result.fail("INDEX_REQUIRED_UNBOUND", ...)`, and a changed subject returns `Result.fail("INDEX_SUBJECT_CHANGED", ...)` until refreshed; unavailable optional fallbacks return `INDEX_ABSENT` or `INDEX_INVALID`, and all four failure kinds map to existing product `INDEX_UNBOUND` missingness without retry burn.
A successful selection always has a real selected-backend epoch, records the rejected LDA cause when degraded, and sets unresolved coverage whenever caller completeness is unproven; failed selection diagnostics record the branch and cause outside the value rather than fabricating an epoch or an index handle.
`TaskMutableField` is the closed literal set `plan`, `strategy_steps`, `hypotheses`, `verification_plan`, `next_action`, `active_step_id`, `backlog`, with the corresponding existing state field types; the fold assigns the next revision, all other state fields stay unchanged, and the runtime resolves the authority reference against the current authenticated dispatch rather than trusting model-supplied proof.
Revision failure kinds are `TASK_REVISION_MALFORMED`, `TASK_REVISION_STALE`, `TASK_REVISION_CONFLICTING` and `TASK_REVISION_WIDENING`, with conflict covering reuse of one revision identity for different content and idempotent replay returning the original receipt.
Caller evidence is observational input, never a verdict: the existing admission boundary also requires relevant exterior verification of the same candidate, treats omissions/unresolved coverage as non-admissible, and invalidates affected receipts when their bound subject changes.
