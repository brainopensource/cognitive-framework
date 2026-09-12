---
id: execution.feature_spec
canonical_id: execution.feature_spec
class: execution
authority: execution
status: living
owner: repository-governance
canonical_for:
  - active-feature-delta-specification
version: "2.1.0"
date: "2026-09-11"
last_verified: 2026-09-12
lock_head: "bf56eea9"
derived_from:
  - docs/reports/reviews/electroweak_v092/plans/DEVELOPMENT_FINAL_PLAN.md
  - docs/reports/reviews/electroweak_v092/plans/DEVELOPMENT_FINAL_PLAN_B.md
  - docs/reports/reviews/electroweak_v092/plans/DEVELOPMENT_FINAL_PLAN_v2.md
  - docs/reports/reviews/electroweak_v092/plans/PHASE-0_DEVELOPMENT_FINAL_PLAN.md
normative_authority:
  - docs/architecture/boundaries.md
relationships:
  - execution.milestones
  - execution.backlog
  - execution.tasks
  - execution.technical
---

# Feature & Target Specification (execution)

This document is the authoritative specification and typed delta contract for the active execution runway and TARGET release predicates.
Lock SHA `66aa7a3c` is the forensic baseline. Implementation head for closed instrument work: `63b77116`. Resume closed at `8637db55` (MS-RESUME `CLOSED`).

Companion handbook: [`technical.md`](technical.md). Task IDs: [`tasks.md`](tasks.md).

## RUN-1. Leadership execution decision (2026-09-12)

**ACCEPTED planning requirements; implementation not claimed.** Authority is the
user's delegation of technical/product/release planning in this session. Inspected
subject: `001911e3231967cf23e885ce2ea4356083d67d01`. This amendment decides the
remaining work; it does not retroactively accept the documentation commits
`faa53259`, `486fb530` or `001911e3`, execute a freeze, spend money or close a gate.
It supersedes conflicting readiness, placement and scheduling statements in the
five execution files. VISION, constitutional boundaries and independent empirical
acceptance remain binding. Earlier `lock_head` metadata identifies historical
planning subjects, not permanent authority over this amendment.

**RUN-01 — Current outcome.** The next outcome SHALL be a reproducible Coding Max
single-controller qualification through the shipped product path. Complete the
control evidence boundary before collecting the canary. Existing context, editing,
index, recovery and composition mechanisms SHALL be reused. New capability
activation remains outside this control arm. Negative or undeterminable results
SHALL preserve evidence and keep the positive gate open; they SHALL NOT trigger
unbounded repair-and-rescore loops or unlock the post-control tree.

**RUN-02 — Diagnostic versus release scoring.** Pure metric functions MAY compute
fixture/replay diagnostics without filesystem reads or a frozen production record.
A publishable control report MUST pass one explicit admission boundary that takes
the frozen manifest and reconciled evidence; a caller-supplied `frozen=True` is
insufficient. No fixture diagnostic is a control acceptance receipt. T-26a MUST
validate schema/version, exact subject, all four control-arm fields, suite/task/
oracle identities, model/provider/configuration identity, declared attempts,
resource ceilings, stop/missingness policy and the complete evidence population.
Empty mappings, missing values, duplicate task attempts, stale or mixed subjects,
unknown dispositions and mismatched denominators MUST fail closed. Preserve the
false-completion veto independently of pass rate. The production publication
caller MUST use this boundary; a new unused helper does not satisfy T-26a.

**RUN-03 — Bounded qualification.** T-51 SHALL freeze exactly 30 distinct L2 tasks,
in a deterministic order, stratified across the existing coding-task taxonomy
with explicit class counts. L0/L1 development tasks MUST NOT enter this holdout.
One measured attempt per task; failures and missing outcomes retain their slots.
Stop after the 30 scheduled attempts, a resource ceiling, or an integrity veto;
no replacement, top-up, outcome-dependent early success or best-of-retries claim.
Positive acceptance requires all 30 binary outcomes and the existing two-sided
95% Wilson lower bound >= 0.40 plus zero observed false completions. Insufficient
binary evidence is UNDETERMINABLE. This narrows the former open-ended
`n_evaluable >= 30` stopping text; T-26 MUST reconcile the frozen artifact first.
Per-task balanced ceilings remain unchanged. Total attempt, provider-call,
inference-cost, evaluation-cost and wall-time ceilings MUST be explicit and
approved for the run; no unspecified resource is unlimited. This amendment grants
no paid-call allowance. Qualification MUST reserve verification/recovery capacity
before work, retain unknown usage as unsettled, and never infer a refund from timeout.

**RUN-04 — Autonomous engineering.** A READY row authorizes implementation in a
subsequent engineering assignment within its lease and accepted contract. The
developer MAY choose private helpers, test fixtures, error wording, equivalent
algorithms and bounded fixes to task-introduced failures. They MAY prepare the
declared new falsifier before implementation; absence of a new test file alone is
not a blocker. They MUST NOT silently add public ports/schemas, change product
presets, widen scope/authority, disable verification, alter acceptance thresholds
or promote an unapproved proposal. Every session SHALL record subject, row,
remaining work, file ownership, verification disposition and remaining allowance
using the existing task handoff, without a new planning file. At session exhaustion,
preserve a resumable handoff; iterative repair obeys the existing rollback contract.

**RUN-05 — Admission depth.** Only the bounded control-hardening and corpus/metric
work in the active tasks table is ready now. FH-1 remains proposed. Its mathematics
and pseudocode describe candidate contracts, not ratified schemas or implemented
APIs. Before a branch becomes READY, T-129 SHALL resolve source-path collisions,
reuse owners, missing emitter/reducer/composition work, migrations, executable
falsifiers and the finite session envelope, then seek one package-level decision.
That decision authorizes ordinary choices within the branch; no per-leaf leadership
permission is needed thereafter. Passing T-27 alone never approves every branch.

**RUN-06 — Preserved boundaries.** Planned kernel delta remains zero, ceiling 1438;
N-06 forbids `import subprocess` in runtime. Reuse one ledger writer, governor,
episode execution path and existing ports. A memory composition registry is not a
workspace CAS implementation. Static skill discovery is not durable learned-skill
qualification. Empirical M-8 acceptance remains required before M-9/M-10; control
qualification is not a renamed beta release. Required containment/authorization
for a selected execution profile cannot be deferred by calling it post-beta.

## RUN-2. Director causal decision (2026-09-12)

**ACCEPTED decisions; no implementation, freeze, paid call or SOTA claim.**
Assignment subject `63881e68caab8a33a4da588718db33fe0fb88706`; recorded here on
`41429f91`. This amendment answers the questions reserved to leadership under
RUN-01..RUN-06 and supersedes conflicting scheduling statements. It does not
retroactively accept T-26b, reopen an accepted receipt, or authorize T-26/T-27.

**RUN-07 — Measurement trust and holdout integrity.** The control instrument is
NOT currently trustworthy. Two defects compound: two bound oracle files changed
after acceptance, and previously exercised `todo`/`quiz` development tasks are
present in the T-51 holdout despite having been used for live development
diagnostics. Corpus reconstitution is therefore broader than digest repair: the
exposure of all 30 members MUST be audited, every exposed member removed and
replaced, and cardinality and strata counts preserved. The default escalation
rule is retained unchanged — three or more toothless or nondeterministic oracles
means systemic failure and corpus rebuild; fewer permits named repair or
replacement — and applies to oracle quality independently of the exposure audit.
Corpus, accounting, publication and false-completion tests MUST become mandatory
in `just verify`; `just check` remains fast. A measurement instrument that no
gate protects will drift again, and did.

**RUN-08 — Invalidated oracle treatment.** REPAIR both invalidated members,
`04_sqlite_wal_checkpoint_lock` and `05_token_budget_clamping_drift`. Rebinding
the resulting source, oracle and suite digests is explicitly authorized, but only
after the repaired oracle is independently proven deterministically red on the
intended defect and green on a correct implementation. Digest synchronization
alone is forbidden: it would rebind the instrument to whatever the tree currently
says rather than to the defect the member exists to detect. **Ordering is
normative.** The RUN-07 exposure audit runs BEFORE this repair. A member that the
audit removes MUST NOT first be repaired and rebound; repairing then deleting a
member wastes the independent-proof step and leaves a rebound digest in history
with no member behind it.

**RUN-09 — Defects that block measurement.** The following are `BLOCK-T27`; none
may be deferred to post-control, because each can produce a published number that
does not mean what it claims: (1) valid model writes do not land; (2) multi-file
application can be partial or invisible to the oracle; (3) patchless, test-inlined
or unauthorized-extra-file completion can appear green; (4) product episodes
continue after a valid admitted completion; (5) malformed or undeclared tool
dialect is not attributed precisely; (6) evidence identity can diverge from the
submitted product candidate; (7) resume or compaction can lose task, candidate,
plan or budget identity; (8) model escalation can bypass the aggregate budget or
provider policy. After attribution in (5) is repaired, an actual malformed
response or pre-action resource exhaustion MAY be recorded as
`MEASURED-MISSINGNESS` with a typed reason, a retained slot and a non-binary
`UNDETERMINABLE` disposition. Neither is ever silently scored as an ordinary task
failure. New autofix-cascade activation is `POST-CONTROL` and excluded from the
balanced arm; existing policy and budget bypasses remain pre-control blockers.

**RUN-10 — Approved architectural boundaries.** All nine are approved: one
canonical `EpisodeEngine` with no second agent loop; atomic all-or-nothing
multi-file commit carrying a final whole-candidate tree digest; an exterior oracle
that evaluates the exact submitted candidate; token-bounded and provenance-bound
context retrieval; compaction preserving objective, constraints, unresolved
failures, plan state, changed-file identity and the resource ledger; fresh-process
resume that neither duplicates effects nor resets ceilings; finite replanning with
terminal exhaustion; escalation through the existing `ModelPort`, provider factory,
credential isolation and evidence accounting; one task/slot identity and one
aggregate resource budget across escalation. **No public port or schema change is
authorized.** Current public contracts MUST be preserved; a demonstrated
incompatibility is a named leadership-reviewed delta, not a developer's call.
Planned kernel delta remains zero.

**RUN-11 — Delivery order and permitted parallelism.** Packages and rough sizes:
P1 measurement and oracle integrity (M); P2 product-path write and change closure
(M); P3 exterior completion and false-completion resistance (M); P4 large-context,
compaction and resumable-session qualification (L); P5 budgeted model cascade plus
comparative evidence (L). P1 and P2 MAY proceed in parallel under separate,
disjoint leases. P3 falsifier authoring and P4 read-only qualification MAY proceed
alongside them. P3 integration requires a reviewed P2; final P4 qualification
requires reviewed P2 and P3. T-26b acceptance requires reaccepted P1 and T-51.

**RUN-12 — Live model authority.** `DEFER — zero calls`. Zero USD, zero provider
calls, zero tokens, zero turns and zero live wall-clock time are allocated before
freeze. No model is authorized. The aggregate `$0.10 USD / 150 provider call`
diagnostic ceiling remains unallocated, and the existence of a credential is not
authority. Historical usage of unknown cost remains unsettled and MUST NOT be
reported as zero. Diagnosis before freeze is hermetic. Any later live allocation
requires a separately pinned authorization naming the exact model ID, task class,
purpose, USD/call/token/turn/wall-clock sub-ceilings, ledger destination and stop
condition, granted only after the RUN-13 diagnostic packet is retained.

**RUN-13 — The one open causal question.** The write-landing failure does NOT yet
have a causal boundary, and this amendment does not invent one. Retained `todo`
and `quiz` failures reached the harness through `ForgeFacade`
(`benchmarks/baac/lib/runner.py:213`); their cassettes retain hashes and usage
counts rather than tool payloads, so they cannot identify the failing product
seam, and both tasks are additionally inside the RUN-07 holdout. No qualifying
retained L0 product trace exists. Forge, BaaC and the autofix proficiency are
comparative evidence only; a repair in one of those paths never closes a
product-path defect. One hermetic diagnostic set is therefore authorized under
T-130 at zero cost. Until it returns, an `entrypoint.py` root cause is unproven
and MUST NOT be assumed. The symptom is stated as: capable models consume turns
on multi-file and greenfield work while changing zero files; the governing
invariant is that a valid emitted write lands atomically in the candidate
workspace and the exterior oracle observes that identical submitted tree.

## DIR-1. Wave 1 rulings and replacement-corpus quarantine

Accepted Director decisions, 2026-09-12, inspected subject
`c3d640783e9bfb96e46551c27ebb6336b9d6e461` (successor of requested `da12be3f`).
The landed T-130/T-131 work is preserved, not independently accepted here.
This amendment authorizes only the named task leases and contracts below;
RUN-12 stays zero calls/zero USD, T-26 stays UNFROZEN, and T-27 is not authorized.

**DIR-D1 — REFRAME: durable carriers, not blanket kind activation.** At this
subject 18 of the fold's 28 recognized kinds are unwritable, not 16; none belongs
to `DEPRECATED_KINDS`. Shrinking that set cannot repair the gap. `READABLE_KINDS`
MUST remain derived from generated `EventKind`, and `WRITABLE_KINDS` MUST remain
its difference with deprecated kinds. The normative kind allocation is
`schemas/mhf/event_envelope.schema.json#/$defs/EventKind`.
`schemas/mhf/event_envelope_v2.schema.json` is the normative production `/2`
envelope and references that allocation; the two `schemas/v4/event-envelope*`
files are compatibility shapes, not a second allocation authority.

Authorize the narrow public schema addition of `VerificationRecorded` and
`ChangeSurfaceUpdated` in that shared allocation, with typed payload definitions
and `/2` payload validation, generated types, sole session-writer ownership,
real emission, fold handling, golden vectors and event-coverage proof delivered
together. No envelope-version bump, deprecated-kind revival, kernel change or
activation of the other 16 compatibility names is authorized. Existing
`PlanRevised`, `EpisodeStateChanged` and `EffectCompleted` carriers remain in use.
The new verification fact records observed verification, not an evaluator verdict
or independent authority to complete; `VerdictRecorded` ownership is unchanged.
It binds task/composition/workspace/verification-subject digests, argv, exit code,
observed test count (unknown stays null), and result artifact digest. The surface
fact binds the task and candidate digests, settled effect descriptor and complete
sorted changed-path set including deletions. Append through the single writer
before the next proposal; append failure stops progress. Replay verifies these
bindings and rejects stale evidence. Reconstruct verification and multi-file
surface from persisted production facts in a fresh process, without fixtures
injecting otherwise-unwritable events. The fold's existing generic
`lastVerification` payload support means "NEVER reconstructible" is too absolute;
the actual gap is an emitted, validated, qualified durable carrier.

**DIR-D2 — ACCEPT: INDEX_UNBOUND is infrastructure missingness.** Extend RUN-09
MEASURED-MISSINGNESS to absent required index infrastructure: retain the scheduled
slot, terminal reason `INDEX_UNBOUND`, and non-binary `UNDETERMINABLE` disposition.
Keep completion fail-closed and do not consult the pack policy to bypass the
missing index. Detect absence before inference where knowable; at admission stop
without spending semantic repair retries. Missing infrastructure is not evidence
of model reasoning failure. This moves affected observations from abandoned/
task-failure counts to infrastructure-missing counts, reduces the binary sample,
and can improve conditional pass rate without improving all-slot coverage.
Publish both denominators; fewer than 30 binary outcomes cannot qualify. Missing
index, stale packet, explicit policy rejection and provider failure stay distinct.
Use existing terminal/disposition axes and reason fields; no new terminal enum.

**DIR-D3 — ACCEPT: remove the false SHA-256 shim.** Authorize removal of the
zero-padded SHA-1 acceptance in `domain/evidence/baseline.py`. The inspected
accepted `CONVERGENCE-BASE-v1.json` pin equals SHA-256 of the ASCII Git tree object
ID and does not equal the padded value; the verifier test constructs that same
canonical hash. No legitimate padded caller/pin was found in the current tree.
Retain that established digest algorithm: changing to a hash of tree contents
would be a separate migration. Reject raw SHA-1 mislabeled `sha256:` as well.
Never rewrite or re-sign historical baseline evidence as part of this deletion;
if an external signed padded pin is discovered, quarantine it and return a named
migration decision, rather than silently converting or accepting it.

**Q-01 — Quarantine invariant (RUN-07/RUN-08).** All 30 old members are exposed
by solve-attempt-grade evidence and MUST be retired from qualification, including
the two stale-digest members. Their old bytes/digests stay historical; no repair
or rebinding of these removed members. Replacement is exactly 30 tasks with
10 brownfield / 11 greenfield / 5 multi_file / 1 multi_turn / 3 single_file.

Let `D*` be the append-only development/exposure registry, closed under task
aliases, origin/lineage and content fingerprints; let `H` be the replacement
holdout registry. Require `closure(H) intersect closure(D*) = empty` at admission
and on every use. A development exposure is irreversible: neither rename, copy,
new digest nor new suite revision restores holdout eligibility. Holdout material
MUST be held in a separate curator-controlled store absent from developer mounts,
LDA/retrieval, LAM capture, generic glob loaders and training/export paths. The
repository carries opaque IDs, strata, commitments and curator attestations only,
never replacement task/oracle/reference-solution plaintext. The existing product
path receives only the assigned task and source at an authorized measured slot;
the exterior oracle and reference solution are never mounted for the solver.
Pre-freeze red/green validation uses isolated curator fixtures, not a solver or
development model; only signed validation metadata leaves that boundary.

Every development task registration, materialization, capture and export MUST
fail closed unless its ID/origin/content is registered DEV and absent from H.
Every evaluation materialization MUST require an admitted frozen manifest and
separate run authority; default-deny missing role/registry/attestation or store.
A holdout exposed to development is irrevocably marked EXPOSED and removed before
freeze; after freeze it invalidates the subject, never triggers slot replacement.
Exposure history includes LAM prompts, benchmark results, retained patches and
`DOGFOOD_SET`; deletion of those artifacts does not erase the tombstone.

`tools/linters/check_corpus_quarantine.py` MUST check: exactly 30 unique IDs and
the exact strata; canonical source/oracle commitments; immutable origin and
exposure ancestry; DEV/HOLDOUT role separation; forbidden aliases, normalized
paths, symlink escapes and matching task/source/oracle fingerprints; absence of
holdout plaintext in tracked files and configured caches/indexes/exports; and
registered guarded entrypoints for every loader/capture/export. Renamed copies
and missing registries/attestations MUST fail. Fingerprint matching does not prove
semantic novelty: an independent curator attests lineage and checks near-duplicate
candidates; unresolved similarity is excluded, not declared clean by the linter.
The linter runs metadata/entrypoint checks in `just check`, full admission checks
in `just verify` and both CI workflows, and at every materialization boundary.
Offline CI validates immutable curator receipts; freeze admission additionally
revalidates the sealed store under the curator role. Neither absence of private
material nor inability to inspect it may be reported as corpus acceptance.

**DIR-P — Approval probe, not an approval repair.** T-130's valid instrument
returned NOT_REPRODUCED for all three write fixtures; it did not qualify successful
completion. The absent-approver/suspension path remains cold. Probe the real
entrypoint with a hermetic approval-requiring composition, missing approver,
explicit denial, valid descriptor-bound approval and invalid/stale approval.
Missing approver MUST NOT become default-allow. A valid signed positive control
may enter at the existing session approval boundary but MUST be labeled as such,
not misrepresented as public-entrypoint wiring. No production approval injection
or threshold change is authorized before attribution and independent review.

## NT-1. Near-term baseline, context, cache and recovery delta

**Authority and scope (2026-09-07).** This executive amendment authorizes T-98–T-111 and the revised T-77 before control qualification. It supersedes earlier EW-9 exclusions only for deterministic context/cache/recovery hardening and baseline remediation. Existing T-09–T-16 mechanisms are extended, not re-created. T-80 remains the later workspace-policy treatment; deterministic semantic stall detection belongs to T-106. Model escalation, consultation, specialists, CAS workspace promotion, memory learning, new index backends and T-96 remain outside this iteration. Historical milestone receipts retain their original subjects. No new milestone is accepted by this amendment.

### NT-1.1 Baseline and execution safety

- **NT-B01:** Baseline receipts MUST bind source SHA, dirty-state digest, environment/runner identity, exact commands, collected/executed/skipped counts, failures/errors, import failures and output artifact digests. The historical 66/2,855 audit result MUST NOT be presented as a current measurement. An unexecuted command has status `not_run`, never `passed`. Current-subject baseline discovery (T-101) established exact counts on commit `771850c1c28f9509f4d976690e1055346c826e00`: 2,924 collected, 2,918 executed, 2,861 passed, 10 failed, 7 errored, 42 skipped (0 missing or unaccounted modules; floor >= 2,900 pinned by `test/contracts/test_collection_integrity.py`).
- **NT-B02:** Broad discovery and context-refresh workflows that execute tests MUST run in an isolated repository with independent Git metadata, redirected writable corpora, provider credentials removed and network denied until nonmutation is proven. Compare source/index/corpus bytes before and after; a linked worktree alone does not isolate Git metadata. Every required module MUST be collected or have a recorded retirement and successor claim. Silent deletion or skipping of failing/security tests is forbidden.
- **NT-B03:** The near-term canonical Python runner is unittest. Essential safety setup MUST NOT depend on pytest hooks. Required additional runners remain explicit. Acceptance requires the complete `just check`/`just verify` recipe bodies, full `python3 -m unittest discover -s test -t .` in the qualified runner, and the declared TypeScript gates. Missing executables/dependencies block acceptance; invoking only available subsets does not satisfy the gate.
- **NT-B04:** Product surfaces MUST preserve terminal status and task disposition as separate axes under EW-9.1. `abstained` MUST NOT become `completed`; a refusal cannot be relabeled as success by a facade, child adapter, CLI exit mapper, or benchmark writer. Successful completion requires fresh applicable evidence under TC-E-058. Help MUST perform no model/effect invocation. Existing budget-only presets MUST NOT be advertised as behaviorally distinct harness arms. Preset and evidence configuration integrity (T-103) binds catalog ceilings (`fast`: $0.05/8t/16k, `balanced`: $0.15/20t/40k, `max`: $0.40/40t/96k); caller attenuation via `effective_limit` is strictly monotonic and cannot elevate declared limits; normalized behavioral identity includes selected plugins (`planner`, `context`); budget-only differences or identical behavior cannot be relabeled as distinct comparative treatment arms.

### NT-1.2 Typed value contracts

These are additive payload/value schemas, not new independent stores or unrestricted event kinds. All objects reject unknown required schema versions, invalid digests, duplicate stable identifiers, negative counters and booleans used as integer counts. Maps are serialized with existing RFC 8785 JCS; bytes are snapshotted before hashing. `Digest` means `sha256:` followed by 64 lowercase hex characters. Nullable observations represent explicit missingness; zero is an observed count. Runtime binds the values into registered `mhf.event/2` envelopes through the single emitter, including schema/event-coverage updates in T-107.

| Value / version | Required typed fields | Validation and ownership |
|---|---|---|
| `aether.memory-view/1` | `schema: str`, `task: SemanticTaskState`, `cursor: int >= 0`, `lineage_id: str`, `reducer_version: str`, `evidence: Evidence[]` | Pure domain snapshot. Full existing task value retained; encode/decode canonical round trip. Runtime verifies cursor/lineage/reducer before use; digest alone grants no authority. |
| `Evidence` | `key: str`, `subject: Digest`, `artifact: Digest`, `finding: str`, `body: str` | Nonempty identities/finding; body may be empty after eviction. Unique key per view. Historical evidence cannot masquerade as current-subject evidence. |
| `Interaction` | `key: str`, `action: str`, `result: str`, `artifact: Digest` | One complete action/result unit; tool-call correlation preserved. Large result bodies become receipts before compilation. |
| `aether.context-policy/2` | `schema: str`, `window/output/safety/recovery: int >= 0`, `high_percent: int`, `low_percent: int`, `max_items: int > 0`, `max_body_bytes: int > 0`, `serializer_id: str`, `counter_id: str` | `0 < low < high <= 100`; usable input positive. Initial high/low = 80/60, configurable and composition-pinned. Output + safety + recovery reserved before input selection. |
| `aether.prompt-selection/1` | `schema: str`, `prefix_digest/state_digest/policy_digest/request_digest: Digest`, `subject: Digest`, `cursor: int >= 0`, `tokens: int >= 0`, `omissions: {key: str, reason: str}[]` | Reasons: `stale`, `body_elided`, `evidence_dropped`, `interaction_dropped`. Metadata records selection; prompt text remains an authorized artifact. |
| `aether.recovery-state/1` | `schema: str`, `policy_digest: Digest`, `history: Attempt[]`, `errors: map[FailureClass,int >= 0]`, `interventions/decisions: int >= 0`, `pending_operation: str or null`, `deadline: str or null` | At most 12 attempts. Counters and decision budget survive resume/recomposition. Pending operation requires a deadline and unsettled reservation. |
| `Attempt` | `fingerprint: Digest`, `outcome: str`, `progress_key: Digest`, `failure: FailureClass or null` | Fingerprint binds normalized action/arguments/input subject; progress key excludes clocks, telemetry and model self-assessment. |
| `RecoveryDecision` | `action: continue/wait/reground/replan/stop`, `reason: str`, `delay_ms: int >= 0`, `state_digest: Digest`, `remaining_budget_ref: Digest` | No `consult` action in this iteration. Persist decision before next external request. Delay bounded by remaining deadline and allowance. |
| `CacheObservation` | `model_id/serializer_id: str`, `prefix_digest/request_digest: Digest`, `read_tokens/write_tokens: int >= 0 or null`, `source: provider/local_fixture/unavailable` | Provider metrics never inferred from prefix equality; write/read costs remain distinct. |

The versioned wrapper adds lineage/reducer validation to Part 3's reference `MemoryView`. It MUST reuse `SemanticTaskState`, `ProtocolRecoveryState`, existing context blocks and canonicalization; no second authoritative blackboard or retry engine is authorized. Schemas above govern production integration where the report's compact examples omit validation or effect adapters.

### NT-1.3 Context and cache invariants

- **NT-C01:** L1–L3 system/tool/environment bytes are frozen per composition epoch. Tool schemas MUST have stable list order and canonical keys. Changed schemas, instructions, model dialect or context policy require a new recorded epoch. Dynamic state and observations MUST NOT mutate the frozen prefix.
- **NT-C02:** The complete original objective, constraints, active plan/next action, modified resources, last material failure, latest applicable verification, settled-effect identities and remaining budgets MUST survive eviction and restart. Complete task state remains durable. Relevant dead ends are selected as evidence; pinned-state overflow fails explicitly rather than silently discarding obligations.
- **NT-C03:** `usable = window - output - safety - recovery` MUST be positive. Count the final provider-serialized request using an exact counter or documented conservative bound specific to that dialect. Final input count MUST be <= usable. An intermediate JSON envelope or generic character ratio is not proof that a different provider request fits.
- **NT-C04:** Reject or truncate oversize display bodies into artifact-bound receipts before selection; cap item cardinality. Remove stale evidence; elide low-priority bodies; drop low-priority evidence; then drop oldest complete interactions. Preserve the newest complete interaction. Trigger at the high watermark and target the low watermark, allowing irreducible state above low but never above hard usable. If the irreducible request cannot fit, return `CONTEXT_BUDGET_EXCEEDED` without inference.
- **NT-C05:** Capability-card injection MUST stay <= 4096 characters independently of token accounting. External text remains untrusted content. Selection identity and omissions MUST be durable before inference; telemetry failures cannot alter the selected bytes.
- **NT-C06:** Provider serializers negotiate supported cache controls and report actual metrics or null. Stable-prefix tests prove bytes only. No universal 85% cache-hit gate is authorized. Any provider-specific cache-performance threshold requires a frozen provider/workload and separately authorized measured evidence. Reservations assume worst-case uncached usage.

### NT-1.4 Bounded deterministic recovery

**NT-R01:** Normalize attempts using action, validated arguments, input/resource digests and classified outcome. Detect >=3 unchanged signatures in a six-action window and repeated length-two/three cycles; retain at most twelve signatures. A separate verified progress key records new facts/falsified hypotheses, not transcript length or mere patch toggling. This pure detector extends existing recovery and does not schedule speculative workers.

**NT-R02:** Initial policy permits one reground and one replan intervention per task, then stop; transport failures permit at most three retries. These bounds are configurable, versioned, reserved and never reset by restart, approval suspension or model switching. Transient delays use bounded exponential backoff with jitter, chosen once and persisted. Assertions/schema/preimage failures require changed information or a new hypothesis, not sleep. Permission/permanent/budget failures stop or await a separately authorized state change; no automatic authority expansion.

**NT-R03:** Poll an existing pending operation only under its durable deadline and reservation. Unknown external outcomes remain unsettled and MUST be reconciled before replay/refund. Persist state and decisions through the current ledger before dispatch. An exhausted task cannot create an unverified success; existing owned workspace recovery must finish or produce an explicit recovery failure. CAS snapshot promotion is not introduced here.

### NT-1.5 Failure matrix and preservation

| Failure | Required response | Forbidden behavior |
|---|---|---|
| `BASELINE_UNSAFE` / `COLLECTION_INCOMPLETE` | Stop broad qualification; retain diagnostic artifact | Hide import errors or mutate contributor checkout |
| `STATE_IDENTITY_MISMATCH` / `CONTEXT_STALE` | Reject snapshot/evidence; rederive from authorized current facts | Treat old cache or summary as authoritative |
| `CONTEXT_BUDGET_EXCEEDED` | No inference; bounded receipt reduction or explicit recomposition | Trim objective or overspend context |
| `VERIFICATION_STALE` / `TEST_COLLECTION_EMPTY` | Refuse completion; run applicable checks | Convert finish/refusal into success |
| `NO_PROGRESS` / `PROTOCOL_INVALID` | Persist bounded reground/replan/stop decision | Reset counters or launch a specialist |
| `PROVIDER_TRANSIENT` | Bounded deadline-aware retry with retained accounting | Unlimited retries or fictitious zero usage |
| `RECOVERY_FAILED` | Quarantine owned work and report failure | Claim rollback or task success without evidence |

**NT-I01:** Planned kernel delta = 0 LOC; ceiling remains 1438. All additions live above the domain-blind kernel. Ports cannot import agency/kernel; adapters cannot import agency/kernel; runtime cannot execute subprocesses (N-06). Preserve I-6 isolation, I-7 domain blindness, one event writer and grant/budget attenuation. **NT-I02:** New gates `MS-BASELINE` and `MS-CONTEXT` are prerequisites to a new T-26 control freeze, not replacements for historical M-1–M-3/MS-INSTRUMENT/MS-RESUME receipts or M-8–M-10 release predicates. Deterministic 100+ turn fixtures do not change the balanced product ceiling or imply benchmark success. **NT-I03:** Concurrent contributors MUST start from one recorded integration subject, use isolated branches/repositories and hold disjoint write leases. A owns runtime/product consumers, B owns pure context/recovery policy, and C owns schema/catalog generator inputs, preset/catalog configuration, benchmarks/corpora/metrics, execution documentation and the serial merge queue. Branch-local success is candidate evidence only. Leadership acceptance occurs once at the final T-111 boundary unless a proposed change exceeds this specification.

### NT-1.6 Runtime durability and ordering protocol

This protocol governs T-107. An **external boundary** is any model inference, effect dispatch, pending-operation poll, approval request or delay whose repetition or omission changes observable behavior or spends budget. A derived in-memory object is not durable merely because its source events are eventually writable. The fact authorizing the next boundary MUST be accepted by the existing single ledger writer first.

| Transition | Required durable precondition | Required identity/content | Failure disposition |
|---|---|---|---|
| Compose or recompose | Composition and epoch identity validated | subject, manifest/composition, prompt, ordered tool schemas, context policy, model route, serializer, counter and recovery-policy digests | Reject stale/unknown identity; perform no inference or effect. |
| Select context -> infer | Registered `ContextSelectionRecorded` fact appended | `aether.prompt-selection/1`, cursor, prefix/state/policy/request digests, final serialized token count and ordered omissions | `CONTEXT_STALE` or durable-write failure; model call count remains unchanged. |
| Semantic outcome -> recover | Complete recovery snapshot appended through a registered state/recovery fact | `aether.recovery-state/1`, triggering attempt, chosen action/reason/delay, remaining-budget reference and pending-operation/deadline state | `RECOVERY_FAILED`; do not wait, retry, reground, replan or dispatch. |
| Effect intent -> execute | Existing `EffectStarted` intent durably appended | descriptor, grant/lease, idempotency identity, resource, action and reservation | Stop before adapter invocation. |
| Effect settles -> next turn | Existing completion/failure/reconciliation fact durably appended | result or explicit unknown occurrence, actual settlement and artifact/result identity | Keep unknown occurrence unsettled; reconcile before replay or refund. |

`ContextSelectionRecorded` and recovery-carrier payloads are runtime facts, not prompt text. Their payloads MUST contain identities or canonical typed values, not mutable Python objects. `runtime/task_state.py` may recognize compatibility kinds during replay, but recognition alone does not authorize production emission: every emitted kind MUST be registered in the canonical event schema/catalog and covered by `check_event_coverage.py`. `EpisodeStateChanged` remains a permitted carrier where its registered payload can represent the complete recovery state; a distinct `RecoveryStateUpdated` kind requires schema/catalog registration before use.

Cold reconstruction MUST follow this order: verify the event chain; fold semantic task state; validate schema, subject, lineage, reducer and policy identities; reconcile open effect intents and child operations; restore settled descriptors, remaining budgets, recovery counters/history, pending operation/deadline and composition epoch; then compile the next context. It MUST NOT call a model or adapter while reconstructing. A descriptor already settled or occurrence-unknown MUST NOT be dispatched again. An expired pending operation is reconciled or terminated under its original reservation, never replaced with a new operation identity.

Behavior-affecting identity includes at least system instructions, capability-card bytes, ordered tool schemas, model dialect/route, context-selection policy, serializer/counter, recovery policy and product preset. A change to any member creates a new epoch/composition identity and invalidates reuse of an earlier prompt-selection or control-freeze receipt. Telemetry-only fields such as wall-clock observation timestamps do not alter selected bytes or behavior identity.

### NT-1.7 Integrated qualification and control-handoff protocol

T-109 and T-111 are empirical acceptance boundaries. Their receipts MUST be produced on a committed candidate with an empty working tree. Administrative evidence may be recorded in a later documentation-only commit that cites the tested candidate; any executable, schema, prompt, corpus, policy, lockfile or generated-index change creates a new candidate and requires the affected gate to run again.

For every test runner, counts MUST satisfy:

```text
collected = passed + failed + errors + skipped
executed  = passed + failed + errors
failed = 0 and errors = 0
```

If the runner reports a different counting model, the receipt MUST provide an explicit mapping that reconciles every collected test. Import failures are errors, never skips. Focused reruns are diagnostic supplements. They cannot replace a failing or incomplete broad-discovery receipt. Environmental attribution requires a deterministic reproduction plus a passing unchanged candidate in the qualified environment; prose attribution is not a waiver.

The protected acceptance subject comprises tracked source, tests, fixtures/corpora, lockfiles, manifest/schema inputs and generated knowledge outputs. The verifier records pre/post digests and `git status`; mutation invalidates the run even when tests pass. Required commands are the current literal full unittest discovery, `just check`, `just verify`, TypeScript typecheck and declared npm tests. A missing dependency or command is `not_run` and blocks acceptance.

T-110 establishes semantic equivalence between uninterrupted and cold-resumed execution over at least 100 deterministic turns. The comparison vector is:

```text
(objective, constraints, plan, next_action, modified_resources,
 last_material_failure, latest_applicable_verification, settled_effects,
 remaining_budgets, recovery_history_and_counters, pending_operation,
 pending_deadline, composition_epoch, serializer_id, counter_id,
 terminal_status, disposition)
```

Every field MUST match after canonical encoding except event positions explicitly introduced to record restart/reconciliation. The fixture MUST force compaction and restart, exercise misleading external text, stale verification, pending-operation expiry and exhausted recovery, and prove zero duplicate settled effects. Passing the fixture proves deterministic preservation only; it does not prove provider cache hit rate, model quality, live benchmark success or production sandbox strength.

T-111 closes MS-CONTEXT only when MS-BASELINE and all context tasks are accepted on a compatible integrated subject. Its output is an **unfrozen control candidate**. T-26 remains the sole freeze task and MUST still verify applicable T-79/T-89/T-92–T-95 and T-51/T-52 evidence. T-111 performs no paid call, does not close MS-CONTROL and does not authorize T-80, T-96, specialists, CAS, campaigns or memory learning.

Before T-111, C MAY prepare and falsify the hermetic portions of the control corpus,
metrics, evidence-row validation, hypothesis registry and L0 operator recipe. Such
preparation MUST preserve `control_preregistration.json` as `UNFROZEN` with no subject,
MUST NOT execute a paid provider call, and MUST NOT be reported as T-26/T-27 or
MS-CONTROL acceptance. A MAY repair the public product consumers that this instrument
invokes. B MUST NOT own or mutate benchmark, corpus, statistics or preregistration
assets during the context-convergence batch.

## FH-1. Post-control backend horizon [PROPOSAL]

This section defines conditional TARGET contracts for prototype refinement after NT-1. It does not activate implementations, change T-98–T-111, authorize paid runs, or accept milestones. “Sprints 3–5” maps to capability dependencies in tasks, not a calendar. FH-1 governs the future CAS/delegation/evaluation scope where older proposal catalogs differ. Historical accepted subjects remain intact. The reference provenance is [Part 3 §§5–6](../../reports/reviews/aether_v093_review/part3_blueprints_and_interface_contracts.md); its Python protocols are illustrative seams, not a requirement for additional public ports. Gate ownership is in [milestones.md](milestones.md#post-control-horizon-release-predicates-fh-1); algorithms are in [technical.md](technical.md#post-control-reference-handbook-fh-1-proposal).

FH-1.1–FH-1.8 are **PROPOSED contract detail**, retained for branch review. Their
RFC-2119 language is conditional on adoption; these sections are not accepted law
merely because they contain formulas. Formal/prose disagreement is a design defect
to resolve at T-129, never an automatic license to choose the narrower expression.
RUN-1 and accepted constitutional invariants govern current work. No schema or
public port is registered by this document.

### FH-1.1 Immutable workspace contracts

All proposed schemas use NT-1 digest/type validation and existing JCS encoding. Unknown required versions fail closed. These are domain values with no filesystem access. Exact source bytes are blobs; directories and file modes are part of identity.

| Schema | Required fields | Constraints |
|---|---|---|
| `aether.tree/1` | sorted `entries: {path, kind: file/directory, mode, blob: Digest or null}[]` | Relative canonical POSIX paths; no duplicates, traversal, `.git`, backslash or NUL; all parents explicitly directories; modes 0..0777; directories have null blobs, files have verified blobs. Empty directories retained. Reject symlinks, special files, filesystem case/normalization collisions and unsupported metadata before capture. |
| `aether.edit-set/1` | `baseline: Digest`, `edits: {path, expected_node: Digest or null, replacement: entry or null}[]`, `policy: Digest` | Nonempty, unique paths; null expected means absent; null replacement means delete. Exact preimage required. Validate the final complete tree and applicable language syntax before verification. |
| `aether.check-plan/1` | `task, composition: Digest`, `checks: {id, argv, cwd, environment: Digest, timeout_ms, kind, minimum_tests}[]` | Unique IDs, explicit argv, relative cwd, finite positive deadlines; test checks require positive collection; build/static checks may declare zero. Pack/composition owns required checks. |
| `aether.candidate-check/1` | `candidate, plan, command, environment: Digest`, `check_id`, `verifier_identity`, `operation_id`, `exit_code`, `collected/executed: int or null`, `timed_out`, `cancelled`, `outputs: Digest[]`, `attestation` | Authenticated runtime verifier provenance; no model-authored receipt admission. Missing counts cannot satisfy test checks. Successful process exit alone is insufficient. |
| `aether.promotion/1` | `transaction_id, task, composition, grant: Digest`, `branch`, `expected_head, candidate, check_plan: Digest`, `expected_generation: int`, `receipts: Digest[]` | Identity binds all fields except receipt collection; validate full required check set and authorization again at commit. Generation is monotonic, preventing ABA after rollback. |
| `aether.export-journal/1` | `operation_id`, `candidate, destination_baseline: Digest`, `destination_identity`, `preimage_manifest: Digest`, `state`, `completed_paths` | Runtime-owned intent; adapters perform export. States: prepared/publishing/committed/restoring/restored/quarantined. Preserve bytes, modes and existence. |

**FH-C01:** Capture MUST enforce declared path/count/byte bounds and obtain a consistent source snapshot under workspace ownership; a concurrently changing capture is rejected or retried within budget. Persist file blobs and manifest durably before acknowledgement. Reads verify digests and grants; content addressing grants no access. Initial materialization supports only declared regular files/directories. Tests get an immutable source mount plus declared scratch/build outputs; tools requiring source mutation run on a disposable copy whose source digest is rechecked before accepting evidence.

**FH-C02:** Promotion MUST perform idempotency lookup, expected head AND generation comparison, current authority validation, required authenticated verification checks, and commit-event append inside the existing single-writer serialization boundary. The branch head is a fold of registered `mhf.event/2` facts, with any cached projection updated transactionally. There MUST NOT be another independently writable head or ledger. A concurrent loser returns conflict without mutation. A replay of an already committed transaction returns its original result, even if the branch later advanced.

**FH-C03:** Before commit, failure/cancellation/exhaustion leaves the active head unchanged. After an unknown commit reply, reconcile transaction identity before retry or refund. Post-commit rollback is a new authorized compare-and-append to a retained snapshot, never event deletion. Readers pin one head/generation for an operation; atomic visibility applies only to consumers of this workspace abstraction. Existing checkouts receive no atomic multi-file visibility guarantee.

**FH-C04:** Checkout export requires explicit destination ownership, a lock respected by framework writers, durable preimages/journal, and a final baseline comparison. External changes stop publication; unsupported concurrent writers preclude an exclusive-export guarantee. Recover each interrupted operation idempotently; restoration failure quarantines the destination. Return separate promotion and export dispositions. Live heads, pending operations, accepted evidence and authorized retention roots pin CAS blobs; bounded mark/sweep GC cannot reclaim them. Missing/corrupt blobs stop resume or promotion, never reconstruct fabricated evidence.

### FH-1.2 Delegation and campaign contracts

| Schema | Required fields | Constraints |
|---|---|---|
| `aether.specialist-request/1` | `call_id`, `parent_lineage`, `task, composition, policy, grant: Digest`, `role`, `inputs: Digest[]`, `output_schema`, `scope`, `budget`, `deadline`, `depth_limit` | Scope uses existing wire contracts; no kernel type in public ports. Stable request identity binds parent and call ID. Read-only effect allowlist is composition-owned. |
| `aether.specialist-findings/1` | `request: Digest`, `child_lineage`, `subject: Digest`, `claims: {finding, evidence: Digest[], validity}[]`, `limitations`, `terminal_status`, `disposition`, `usage_receipt: Digest` | Bounded payload; verify lineage, subject, schema and evidence before parent incorporation. Findings are advisory and cannot satisfy exterior acceptance. |
| `aether.campaign-plan/1` | `campaign_id`, `version`, `objective: Digest`, `nodes: {id, task, inputs, output_schema, requires, owner, acceptance_plan}[]`, `budget`, `policy: Digest` | Acyclic dependencies; explicit interface contracts and merge owner; plan revisions recorded. Ready means dependencies have applicable accepted artifacts, not merely terminal children. |

**FH-D01:** Extend canonical `SpawnRequest`/`SpawnAdapter`, child runtime and existing agency spawn. Validate current expiry/revocation, scope attenuation and depth at dispatch. Reserve additive sibling envelopes (`usd_micros`, `millis`, `tokens`, `bytes`) through existing governor leases; turns/depth remain structural ceilings. Persist intent and reservation before child dispatch; reconcile partial admission without a second budget accountant. Unknown child outcomes keep reservations unsettled. Parent cancellation propagates deadlines; a timeout never proves no effect occurred.

**FH-D02:** Default treatment permits bounded read-only specialists and one parent writer. No raw authenticated session handle enters child context. Optional parallel implementers require isolated candidates, explicit ownership, MS-CAS acceptance and a separately frozen treatment. Parent integration is a new candidate requiring verification of the combined tree. Child passes, role votes and model preferences cannot promote it.

**FH-D03:** Campaign policy is a runtime client above the existing execution path and has zero arbitrary mutation verbs. Durable node leases, attempts and artifact references use the current ledger; no second EpisodeEngine or scheduler accounting. Restart reconciles pending nodes before dispatch. Replanning cannot silently enlarge objective/grants/budget. Persist blocked/failed/undeterminable outcomes and bounded replan allowances; failed dependencies do not become ready. Full Octopus/HYDRA activation retains the M-OCT/post-M-10 boundary.

### FH-1.3 Evaluator and experiment boundary

**FH-E01:** A versioned `aether.evaluation-manifest/1` MUST freeze corpus source/revision/split, exact instance IDs and digest, runtime SHA, composition/prompt/tool/model identities, environment images, inference/evaluator versions, attempt/feedback policy, seeds or explicit nondeterminism, budget, statistical plan, acceptance margin and stop rule. Null/unfrozen fields forbid scoring. The evaluator materializes the final submitted patch independently and cannot trust the agent's tests or finish message. Official test patches/answers and held-out results MUST NOT enter the worker's context or memory learning. Public availability is not proof of uncontaminated training; disclose unknown exposure.

**FH-E02:** A versioned `aether.evaluation-attempt/1` binds manifest, instance, attempt, base/candidate/patch digests, prediction artifact, evaluator run identity, command/image, raw result/log artifacts, terminal status, task disposition, failure attribution and observed usage/missingness. Emit one canonical row per scheduled attempt, including no-output, invalid-patch, infrastructure and dataset failures. Preserve original attempts when rerunning; a changed patch requires a new evaluator run identity to avoid stale result caches. Unknown cost stays null, never zero.

**FH-E03:** SWE-bench Verified uses pinned upstream evaluation and prediction format; Aider polyglot uses its separately pinned corpus, runner and feedback/attempt rules. Report AETHER-on-Aider results as such; replacing Aider's harness does not reproduce an Aider leaderboard row. First-attempt and retry-assisted outcomes are separate. Greenfield has an independent requirement-based corpus and exterior acceptance. None of these scores are pooled or labeled interchangeable. G-3 and SWE-P5 remain mandatory for official claims.

**FH-E04:** Paired treatments hold tasks and total budgets fixed and vary one declared component. Include coordination, verification, retries and failures in cost/latency. Use prespecified uncertainty estimates and multiplicity/stop handling; do not tune on held-out results. Protocol qualification can close with a valid negative result; treatment promotion requires the predeclared positive predicate. SOTA is a dated, benchmark-specific comparison against a reproducible eligible comparator, with uncertainty and resource differences disclosed. An inconclusive or negative result completes an honest report but does not establish superiority.

### FH-1.4 Tree algebra, preimage law and promotion monotonicity (CAS-01)

These clauses make FH-1.1 computable. Every function below is a pure domain function over values; none reaches a filesystem, clock, process or network. `JCS(.)` is the existing serializer (`domain/canonicalisation/jcs.py::canonical_bytes`) and `H(.)` the existing digest (`domain/canonicalisation/digest.py::digest_bytes`), i.e. `sha256:` followed by 64 lowercase hex (`CT-09`, `SC-2`). No second serializer, digest alphabet or canonical form is introduced.

**FH-C05 (tree identity).** A tree is a flat sorted entry manifest over blob leaves — a depth-2 Merkle structure whose leaves are exact source byte strings:

```text
H_blob(b)  := H(b)                                    -- b is the exact source byte string
ent(e)     := {"blob": beta(e), "kind": kappa(e), "mode": mu(e), "path": pi(e)}
                beta(e)  = H_blob(bytes(e)) if kappa(e) = "file", else null
                kappa(e) in {"file", "directory"}
                mu(e)    in [0, 0o777]
order(T)   := entries of T ascending by UTF-8 byte order of pi(e)   -- total; pi is injective
H_node(e)  := H(JCS(ent(e)))
H_tree(T)  := H(JCS({"entries": [ent(e) : e in order(T)], "schema": "aether.tree/1"}))
```

Recursive per-directory subtree digests are **not** normative: a reader MUST NOT infer subtree identity, structural sharing or rename detection from `H_tree`. The flat manifest costs `O(|T|)` per recomputation, bounded by the capture limits of FH-C01, and is accepted in exchange for exactly one canonical preimage per tree. Consequences that MUST hold: `H_tree(T1) = H_tree(T2)` for `T1 != T2` implies a SHA-256 collision; mode changes and empty directories change `H_tree`; a digest scheme that erases modes or empty directories (git tree semantics) is inadmissible for this profile.

**FH-C06 (capture admissibility).** A captured tree `T` is admissible iff all of:

```text
P1 path shape     pi(e) = normalise(pi(e)); relative; no "", ".", "..", leading "/" or "\",
                  no NUL, no backslash, no empty or trailing segment
P2 reserved       no segment equals ".git"
P3 uniqueness     pi injective on T
P4 parent closure every proper directory prefix of pi(e) is in T with kind "directory"
P5 kind closure   kappa(e) in {"file","directory"}; beta(e) non-null iff kappa(e) = "file"
P6 case/NF safety fold(p) := join(casefold(NFC(segment)) for segment in p); fold injective on pi(T)
P7 declared bounds |T| <= max_entries; sum(size(bytes(e))) <= max_bytes; depth(pi(e)) <= max_depth
```

Violations map to `TREE_PATH_INVALID` (P1–P3), `TREE_PARENT_MISSING` (P4), `TREE_UNSUPPORTED` (P5), `TREE_CASE_COLLISION` (P6) and `CAPTURE_BOUNDS_EXCEEDED` (P7). P6 is what makes a candidate portable to case-insensitive and NFD-normalising hosts: two paths that a target filesystem would merge are rejected at capture, not discovered at export. Symlinks, devices, sockets, FIFOs, hardlink identity, extended attributes and ACLs fail P5 as `TREE_UNSUPPORTED` and MUST NOT be dereferenced — following a link converts a workspace escape into a copied byte string inside the candidate. Capture consistency is proven, not assumed: source identity is recomputed and compared after reading; a mismatch is `CAPTURE_CHANGED`, retried within budget and never partially accepted.

**FH-C07 (exact preimage law).** For edit set `E` over baseline tree `A`:

```text
nu_A(p)   := ent(e) if exists e in A with pi(e) = p, else BOTTOM
D(BOTTOM) := null ;  D(ent) := H(JCS(ent))
admissible(E, A) <=> for all (p, x, r) in E : D(nu_A(p)) = x
A (+) E   := (A \ {e : pi(e) in paths(E)}) union {r : (p, x, r) in E, r != null}
```

`expected_node` is the digest of the **entry object**, not of the blob: a mode-only change therefore has a distinct preimage and cannot be applied under a stale expectation. Admissibility is total and evaluated over all of `E` before any effect; a single mismatch rejects the whole set as `PATCH_PREIMAGE_MISMATCH`. No context window, fuzz factor, offset search, whitespace normalisation or anchor heuristic is admissible in the CAS profile — this is the formal reason every legacy patch frontend must converge on one validated edit set. The result `A (+) E` MUST itself satisfy FH-C06 (P4 in particular: creating `a/b/c.py` requires explicit directory entries for `a` and `a/b`), else `EDIT_SET_INCONSISTENT`. Non-idempotence is intended: `apply(apply(A, E), E)` fails because the preimages no longer match. Workspace-layer replay safety is preimage-based and promotion-layer replay safety is transaction-identity-based (FH-C08); they are different mechanisms and neither substitutes for the other. Language-syntax validation of the resulting complete tree belongs to packs/adapters, never to domain.

**FH-C08 (promotion identity, generation monotonicity, ABA immunity).**

```text
branch state   (head_k, gen_k), with gen_0 = 0
identity       I(P) := H(JCS(P without "receipts"))   -- every promotion field except the receipt set
commit k admissible <=> P.expected_head       = head_{k-1}
                    AND P.expected_generation = gen_{k-1}
                    AND authorised(P.grant, now)
                    AND promotable(P.candidate, P.check_plan, P.receipts)
post-state     head_k = P.candidate ; gen_k = gen_{k-1} + 1
```

`gen` is a strictly monotone fold over registered `mhf.event/2` facts and never decreases, including on rollback — which is a new forward compare-and-append (FH-C03), never event deletion.

*ABA immunity (theorem).* Let the head traverse `A -> B -> A` at commits `k` and `k+1`. A request prepared at `(A, gen_{k-1})` is refused at the later state `(A, gen_{k+1})` because `gen_{k+1} != gen_{k-1}`. Head equality alone never authorises a commit; the compare key is the pair. The two refusals are reported distinctly — `PROMOTION_CONFLICT` when the head differs, `GENERATION_STALE` when the head matches but the generation does not — so a rebase loop can tell an intervening rollback from an ordinary race.

*Idempotency.* Commit is a partial function of `transaction_id`: replaying a committed transaction returns the recorded original result and original generation with no mutation, even if the branch has since advanced. `receipts` is excluded from `I(P)` so that a retry carrying additional receipts is the same transaction; required-check satisfaction is re-evaluated at commit against the receipt set actually presented. A request bearing a known `transaction_id` but a different `I(P)` is `TRANSACTION_IDENTITY_MISMATCH` — refused, and never served the earlier result. The admissibility test and the append are one critical section inside the existing single-writer boundary: exactly one of a concurrent set wins and every loser mutates nothing.

**FH-C09 (verification sufficiency).** For check plan `C`, candidate tree `candidate` and receipt set `R`:

```text
satisfied(c, R) <=> exists r in R :
      r.check_id     = c.id
  AND r.plan         = H(JCS(C))
  AND r.candidate    = H_tree(candidate)
  AND r.environment  = c.environment
  AND r.command      = H(JCS({"argv": c.argv, "cwd": c.cwd}))
  AND r.exit_code    = 0
  AND r.timed_out    = false
  AND r.cancelled    = false
  AND trusted(r.verifier_identity) AND attested(r)
  AND (c.kind = "test" =>
           r.collected != null AND r.executed != null
       AND r.collected >= c.minimum_tests AND r.executed >= c.minimum_tests)

promotable(candidate, C, R) <=> for all c in C.checks : satisfied(c, R)
```

Null counts never coerce to zero and never satisfy a test check (`CHECK_INCOMPLETE`). A receipt bound to a different tree is `VERIFICATION_STALE`, the rebase case included. A model-authored or unattested receipt is `VERIFIER_UNTRUSTED`. Receipt *execution* is an adapter/tool concern under N-06; runtime validates receipts and never spawns processes.

**FH-C10 (retention closure and GC safety).**

```text
Pins        := live heads U pending-operation candidates U accepted evidence subjects
                 U authorised retention roots
reach(X)    := transitive closure of tree -> entry -> blob references from X
collectable(o) <=> o not in reach(Pins)
```

The ordering rule is pin-before-write: a pin covering an object is durable **before** the object is first referenced and is released only after its last reference is dropped. A sweep deletes only objects unreachable at a mark epoch taken inside the single-writer boundary, with no pin registered since that epoch. Deleting a reachable object is `GC_PIN_VIOLATION` — a defect, not a recoverable condition. Missing or corrupt blobs stop resume and promotion (`BLOB_MISSING`, `BLOB_CORRUPT`) and never license reconstructed or inferred evidence.

**FH-C11 (export journal ordering).** The journal is a total order on states; backward transitions are forbidden and each transition is durable before the effect it authorises:

```text
prepared -> publishing -> committed
prepared -> publishing -> restoring -> restored
prepared -> publishing -> restoring -> quarantined
```

Recovery resumes from the recorded state by `operation_id` and is idempotent. Promotion disposition and export disposition are reported separately: a committed promotion with a quarantined export is a truthful pair and MUST NOT be collapsed into a single success or failure.

### FH-1.5 Envelope conservation algebra and settlement lattice (DEL-01)

Grounded in `kernel/budget.py` (`ADDITIVE_DIMENSIONS`, `Reservation`, `Lease`, `Governor`) and `kernel/attenuation.py` (`Scope`, `attenuate`). No second budget accountant is created, and no kernel line is added.

**FH-D04 (additive envelope conservation).** For every additive dimension `d in {usd_micros, millis, tokens, bytes}` and every node `v` of the delegation tree:

```text
spent_d(v) + unsettled_d(v) + SUM[ reserved_d(v -> c) : c in children(v) ] + recovery_d(v)
    <= limit_d(v)

limit_d(c) = reserved_d(v -> c)        -- a child's root limit is exactly its parent's reservation
```

*Aggregate conservation (theorem).* `SUM[ spent_d(w) : w in subtree(v) ] <= limit_d(v)`, by induction on depth: each child's total consumption is bounded by `limit_d(c) = reserved_d(v -> c)`, which is itself a term of the parent's inequality. Because the constraint binds reservations held *simultaneously*, no sibling set can co-consume more than the parent envelope — the cross-sibling overspend defect `F-10` is excluded by construction rather than by sequencing.

Structural ceilings are excluded from the sum: `depth(c) = depth(v) + 1 <= max_depth` and `turns` is a per-episode ceiling. Summing either across siblings is `F-10`.

*Overrun honesty.* An effect may settle above its reservation (`Lease.settlement` is negative in that dimension). The deficit is charged to `recovery_d(v)` first; once `recovery_d(v)` is exhausted, `remaining_d(v) < 0` and `v` is refused every further reservation (`ENVELOPE_OVERCOMMIT`, `BUDGET_DENIED`). The observed overrun is recorded exactly — never clamped to the ceiling, never masked by a compensating refund, and never reported as if the envelope had held.

**FH-D05 (monotone attenuation at dispatch).** For child `c` of `v`, evaluated at dispatch time and not only at issue time:

```text
actions(c)       subset of actions(v)
resources(c)     refines resources(v)         -- kernel attenuate(); K-23 / K-25 / K-26
depth(c)         = depth(v) + 1 <= max_depth
expiry(c)        <= expiry(v)
reserved_d(v -> c) <= remaining_d(v)          for all additive d
```

No dimension may increase after dispatch, and expiry/revocation is re-checked at dispatch. Any fallback path that widens a dimension is `DELEGATION_DENIED` or `SCOPE_ESCALATION_DENIED`; a denial records the requested and grantable sides (`K-25`), never a bare refusal. Refunds are bounded by `refund_d(v -> c) <= reserved_d(v -> c) - settled_d(c)`: a refund is never a source of budget.

**FH-D06 (settlement lattice).** Every delegation call occupies exactly one state, and the order is durable-before-effect, so a crash between any two states is reconcilable by `call_id`:

```text
RESERVED -> INTENT_RECORDED -> DISPATCHED -> RETURNED -> SETTLED
```

| State | Durable before entry | Non-zero conservation term | Permitted exits |
|---|---|---|---|
| `RESERVED` | governor lease held | `reserved_d(v -> c)` | `INTENT_RECORDED`; `SETTLED` (release, nothing dispatched) |
| `INTENT_RECORDED` | intent + reservation record | `reserved_d(v -> c)` | `DISPATCHED`; `SETTLED` (abandon) |
| `DISPATCHED` | child lineage fact | `reserved_d(v -> c)` as `unsettled` | `RETURNED`; `SETTLED` (timeout, at reserved) |
| `RETURNED` | findings + usage receipt | `reserved` resolving to `observed` | `SETTLED` |
| `SETTLED` | settlement record | `spent_d` | terminal |

An unknown outcome keeps the reservation held and unsettled; reconciliation is by `call_id` against the durable record, and `CHILD_UNKNOWN` never releases it. A timeout settles at the **reserved** amount, not zero — a deadline proves nothing about effects already performed, and settling a timed-out call at zero is precisely the defect this rule excludes. Cancellation propagates a deadline to descendants but does not retroactively convert their settled spend into refundable budget. `SETTLED` is terminal and idempotent by `call_id`; a second settlement attempt is refused (`SETTLEMENT_UNRECONCILED`) rather than double-credited.

| Schema | Required fields | Constraints |
|---|---|---|
| `aether.delegation-settlement/1` | `schema`, `call_id`, `request: Digest`, `state`, `reserved: map[dim, int >= 0]`, `observed: map[dim, int >= 0] or null`, `settled: map[dim, int >= 0]`, `deficit: map[dim, int >= 0]`, `reason` | Dimensions restricted to the four additive dimensions; structural ceilings rejected as dimensions (`C-05`). Null `observed` means unknown, never zero. `settled <= reserved + deficit` per dimension. Exactly one terminal record per `call_id`; the parent is its sole writer. |

**FH-D07 (advisory isolation).** A read-only specialist writes no ledger fact of its own beyond its lineage and usage receipt: `writer(findings) = parent`. `aether.specialist-findings/1` is advisory input to a parent candidate and cannot satisfy a check plan, mark a campaign node `PASSED`, or enter acceptance evidence. Formally, the acceptance predicate `Acc` is a function of exterior verification receipts only; findings are not in its domain. No raw authenticated grant, authenticator key or session handle crosses into the child context — the child receives an attenuated grant, never the parent's credential.

### FH-1.6 Campaign DAG readiness algebra and lease fencing (OCT-03)

**FH-D08 (plan admission).** With `G = (V, E)` and `deps(v) = {u : (u, v) in E}`, a campaign plan is admissible iff `V` is finite, every dependency names a node in `V`, and a topological order exists (acyclicity). A plan failing any of these is `CAMPAIGN_PLAN_INVALID` and is never partially dispatched.

**FH-D09 (dependency readiness).**

```text
disposition : V -> {PENDING, RUNNING, PASSED, FAILED, BLOCKED, UNDETERMINABLE}

ready(v) <=> disposition(v) = PENDING
         AND for all u in deps(v):
                   disposition(u) = PASSED
               AND artifact(u) != BOTTOM
               AND validates(artifact(u), Schema_v(u))
               AND artifact_digest(u) is bound into v's input record
```

Terminality is not readiness: a child that terminated without an accepted, schema-valid artifact does not release its dependents. Schema validity is checked against the **consumer's** declared `output_schema` for `u`, not against the producer's self-report. Failure closure is monotone — `disposition(u) in {FAILED, BLOCKED, UNDETERMINABLE}` forces `disposition(w) := BLOCKED` for every `w` reachable from `u`, and a `BLOCKED` node is never ready under the same plan version. A failed dependency cannot be argued ready.

**FH-D10 (lease exclusivity and fencing).** At most one active lease per node, enforced by compare-and-append on the existing ledger inside the single-writer boundary:

```text
count{ l : l.node = v AND l.state = ACTIVE } <= 1
append admissible <=> l.fence_token = current_fence_token(v)
```

A lease carries a strictly increasing `fence_token`. An append from a holder whose token is below the node's current token is refused (`NODE_LEASE_CONFLICT`). Fencing is what makes a resumed or partitioned director unable to duplicate effects: the superseded holder cannot write regardless of what it believes about its own liveness.

| Schema | Required fields | Constraints |
|---|---|---|
| `aether.campaign-lease/1` | `schema`, `campaign_id`, `node_id`, `attempt: int >= 1`, `fence_token: int >= 1`, `holder_identity`, `state`, `deadline`, `operation_id` | `fence_token` strictly increases per node; at most one `ACTIVE` lease per node. Lease expiry alone settles nothing — the outcome is reconciled by `operation_id` under FH-D06. |

**FH-D11 (zero mutation verbs).** `verbs(director) INTERSECT MutatingVerbs = EMPTY`. The director's admissible verb set is exactly `{compile plan, dispatch node, read artifact digest, record disposition, record lease}`. This is a set-theoretic constraint over the live verb inventory (§22) and is mechanically falsifiable: any filesystem, patch, process or network write verb reachable from the campaign client is a defect, not a configuration choice. Edits are performed only by qualified child episodes through the existing execution path — there is no second `EpisodeEngine`, scheduler or budget accountant.

**FH-D12 (replan monotonicity and termination).** A revision `G'` of plan `G` satisfies:

```text
objective(G')  =  objective(G)                          -- digest-equal
grants(G')     subset of grants(G)
budget_d(G')   <= budget_d(G)                           for all additive d
{ v : disposition(v) = PASSED } and their artifacts are preserved unchanged
replans(G')    =  replans(G) + 1  <=  replan_allowance
```

Replanning cannot silently enlarge objective, authority or budget (`SCOPE_ESCALATION_DENIED`); exhausting the allowance is `REPLAN_EXHAUSTED`, a recorded terminal outcome rather than a retry. *Termination:* `V` is finite, failure closure is monotone, each dispatch consumes a strictly positive amount of a finite envelope, and replans are bounded — so the ready set is eventually empty and every node holds a terminal disposition. `BLOCKED`, `FAILED` and `UNDETERMINABLE` are persisted as outcomes; an unfinished campaign never reports completion.

### FH-1.7 Governed learning, lift predicate and revocation algebra (MEM-01 / M-8)

Grounded in `ports/memory.py` (`MemoryAccess`, `RetrievalProvenance`, `require_retrieval_provenance`, `authorize_memory_action`). This section states MEM-01's measurement and revocation law. It does not accept M-8, whose predicates remain independent obligations.

**FH-M01 (partition and contamination).** Fix disjoint instance sets `S_gen` (lessons may be derived from it) and `S_eval` (held out). Let `prov(l)` be the source-artifact digest set of lesson `l`:

```text
contaminated(l) <=> prov(l) INTERSECT ( digests(S_eval) U official_tests U holdout_results ) != EMPTY
```

A contaminated lesson is inadmissible to retrieval, and its presence in any retrieval set of a scored run invalidates that run (`EVALUATION_INVALID`, `LESSON_CONTAMINATED`). The check is mechanical rather than declarative: `RetrievalProvenance.source_record_digests` is joined against the frozen holdout digest set for every admitted retrieval, and a run carrying no retrieval receipts to join is unscored rather than assumed clean. Official test patches, answers and held-out results never enter worker context, generation input, or any cache. Public availability of a corpus is not evidence of uncontaminated training; unknown exposure is disclosed, not omitted.

**FH-M02 (lift predicate).** The study is paired on `S_eval`: treatment `M1` (retrieval enabled at lesson-set version `L`) against control `M0`, identical in every declared component except lesson retrieval, under one frozen `aether.evaluation-manifest/1`.

```text
mu(M)     := primary success rate of M on S_eval under the frozen manifest
Delta_mu  := mu(M1) - mu(M0)
(b, c)    := discordant pair counts (M1 pass / M0 fail, M1 fail / M0 pass)
p         := exact two-sided McNemar p-value, X ~ Binomial(b + c, 1/2)

promote(L) <=> Delta_mu >= 0.05
           AND p < 0.05
           AND false_completion_rate(M1) = 0
           AND n >= n_min                                 -- preregistered
           AND lower(CI_95(Delta_mu)) > 0                 -- internal consistency check
           AND no admitted lesson satisfies contaminated(.)
```

The test, `n_min`, the primary metric, the missingness policy and the stop rule are preregistered before the first measured attempt; choosing between the useful-lift and the cost-saving/noninferiority alternative after viewing results is forbidden. The exact paired test is required rather than a normal approximation because discordant counts at `n` near 30 are small. *Multiplicity:* comparing `k` lesson-set versions or arms against the same holdout requires family-wise control at `0.05` (Holm–Bonferroni) or a single declared primary comparison; a holdout partition serves at most one preregistered decision, and a further decision requires a fresh partition. Reporting `Delta_mu >= 0.05` with `p < 0.05` while `lower(CI_95(Delta_mu)) <= 0` is internally inconsistent and vetoes acceptance instead of being published as a win. A negative or inconclusive study is a complete, honest result that leaves the treatment disabled (`LIFT_UNPROVEN`) and the positive gate open. Generation, evaluation and promotion remain separately authorised steps: the component that writes a lesson never also decides its promotion.

**FH-M03 (lesson identity and revocation epochs).** Lessons are content-addressed and versioned; supersession mints a new digest and never edits in place.

```text
L         := H(JCS({"body": body, "provenance": provenance, "scope": scope, "version": version}))
Revoked_e := set of revoked lesson digests at epoch e
R_e       := H(JCS(sorted(Revoked_e)))          -- revocation root, a fold of mhf.event/2 facts
e         strictly increases on every revocation append
```

| Schema | Required fields | Constraints |
|---|---|---|
| `aether.lesson/1` | `schema`, `lesson: Digest`, `version: int >= 1`, `body: Digest`, `provenance: Digest[]`, `scope`, `authority_grant: Digest`, `supersedes: Digest or null` | Identity is the digest over body, provenance, scope and version; in-place edit is forbidden. Empty provenance forbids admission. |
| `aether.lesson-revocation/1` | `schema`, `lesson: Digest`, `reason`, `epoch: int >= 1`, `authority_grant: Digest`, `revoked_at`, `supersedes: Digest or null` | Appended to the one ledger under the single writer; never rewrites the admission events that preceded it. Epoch strictly monotone. |
| `aether.retrieval-admission/1` | `schema`, `provenance: Digest`, `revocation_root: Digest`, `epoch: int >= 1`, `records: Digest[]`, `cache_identity: str or null` | A cached or live retrieval enters model context only while `revocation_root` equals the current `R_e`. |

**FH-M04 (immediate cache invalidation).**

```text
admissible(retrieval) <=> retrieval.revocation_root = R_current
                      AND records(retrieval) INTERSECT Revoked_current = EMPTY
                      AND require_retrieval_provenance(result) holds
```

Advancing the epoch invalidates every cached retrieval globally in constant time without enumerating caches: a stale entry cannot satisfy the root equality and is recomputed or refused (`REVOCATION_ROOT_STALE`). Each revocation append emits a receipt binding `{revocation, epoch_before, epoch_after, revocation_root_after, cache_identities_invalidated, effective_at}`. The falsifier is direct: after the append, no recall returns the revoked record and no cached entry is admitted under a superseded root.

*Non-retroactivity.* Revocation stops future admission and never rewrites past events. Accepted evidence records the lesson digests and the epoch under which they were admitted; an acceptance that depended on a since-revoked lesson is flagged for re-verification (`LESSON_REVOKED`) — never silently reversed and never silently retained. Rollback of a lesson-set promotion is executed revocation evidence, not an assertion that rollback would work.

### FH-1.8 Failure and compatibility matrix

| Failure | Required outcome |
|---|---|
| `TREE_UNSUPPORTED` / `CAPTURE_CHANGED` / `PATCH_PREIMAGE_MISMATCH` | Reject candidate before active mutation; retain bounded diagnosis. |
| `BLOB_CORRUPT` / `BLOB_MISSING` | Refuse materialization/promotion; repair storage under separate authority. |
| `CHECK_INCOMPLETE` / `VERIFIER_UNTRUSTED` / `VERIFICATION_STALE` | Refuse promotion and task acceptance. |
| `PROMOTION_CONFLICT` | Keep current head; rebase creates a new candidate and invalidates old verification. |
| `PROMOTION_UNKNOWN` / `CHILD_UNKNOWN` | Reconcile durable operation; no blind replay/refund. |
| `EXPORT_CONFLICT` / `RECOVERY_FAILED` | Stop export; restore only owned changes or quarantine; no false rollback claim. |
| `DELEGATION_DENIED` / `BUDGET_DENIED` | No child dispatch; scope and budget never enlarged by fallback. |
| `EVALUATION_INVALID` / `EVALUATION_INCOMPLETE` | Preserve denominator and null metrics; no acceptance. |

The rows below extend the same fail-closed discipline to the formal clauses of FH-1.4–FH-1.7. Every code is a distinct observable outcome: a reader MUST be able to tell which invariant fired, and no code may be widened into a neighbour to make a run look cleaner.

| Failure | Origin clause | Required outcome |
|---|---|---|
| `TREE_PATH_INVALID` / `TREE_PARENT_MISSING` / `TREE_CASE_COLLISION` | FH-C06 P1–P4, P6 | Reject at capture before any blob is persisted; report the offending path pair for a collision. Never repair by renaming. |
| `CAPTURE_BOUNDS_EXCEEDED` | FH-C06 P7 | Refuse the capture; report the declared bound and the observed value. Never truncate the tree and proceed. |
| `EDIT_SET_INCONSISTENT` | FH-C07 | Reject the whole edit set; the post-application tree violated admissibility. No partial application. |
| `GENERATION_STALE` | FH-C08 | Keep the current head; report distinctly from `PROMOTION_CONFLICT` so an intervening rollback is distinguishable from a race. |
| `TRANSACTION_IDENTITY_MISMATCH` | FH-C08 | Refuse; never serve the earlier recorded result to a request whose identity digest differs. |
| `GC_PIN_VIOLATION` | FH-C10 | Stop collection and quarantine the store; a reachable object was collectable, which is a defect, not a recoverable condition. |
| `ENVELOPE_OVERCOMMIT` | FH-D04 | Deny the reservation; record the observed overrun exactly. Never clamp to the ceiling or mask it with a refund. |
| `SCOPE_ESCALATION_DENIED` / `DELEGATION_DEPTH_EXCEEDED` | FH-D05, FH-D12 | No dispatch and no replan; the denial records requested and grantable sides (`K-25`). |
| `SETTLEMENT_UNRECONCILED` | FH-D06 | Keep the reservation held and unsettled; reconcile by `call_id`. Never double-credit and never settle a timeout at zero. |
| `CAMPAIGN_PLAN_INVALID` | FH-D08 | Refuse the plan whole; never dispatch a prefix of a cyclic or dangling graph. |
| `NODE_LEASE_CONFLICT` | FH-D10 | Refuse the append from the superseded fence token; the current holder is unaffected. |
| `DEPENDENCY_BLOCKED` | FH-D09 | Persist `BLOCKED` for the reachable set; the node is never ready under this plan version. |
| `REPLAN_EXHAUSTED` | FH-D12 | Terminal recorded outcome; not a retry and not a completion. |
| `LESSON_CONTAMINATED` | FH-M01 | Refuse admission and invalidate any run that admitted the lesson; preserve the denominator. |
| `LIFT_UNPROVEN` | FH-M02 | Treatment stays disabled and the positive gate stays open; the honest report still completes. |
| `LESSON_REVOKED` / `REVOCATION_ROOT_STALE` | FH-M03, FH-M04 | Refuse admission; recompute under the current root. Flag dependent acceptances for re-verification without rewriting past events. |
| `SCHEMA_UNSUPPORTED` | FH-1.1 preamble | Unknown required schema version fails closed on both read and write paths; no best-effort partial decode. |
| `SYNTAX_REJECTED` | FH-C07 | Reject the candidate before verification; unsupported syntax is refused, never routed to a fuzzy fallback. |
| `ARTIFACT_SCHEMA_INVALID` | FH-D09 | The producer's artifact failed the consumer's declared `output_schema`; the node is `FAILED`, never `PASSED`. |
| `EXPORT_UNOWNED` | FH-C11 | Refuse before acquiring a lock or writing a journal; an undeclared destination root is never exported to. |

**Normative placement.** The formal clauses above change no layer ownership. Placement is itself a falsifiable contract:

| Concern | Owning layer | Forbidden in |
|---|---|---|
| Tree, edit-set, promotion, lease, settlement and lesson values; digest and preimage algebra | `domain/` | any filesystem, process, clock or network access |
| Blob store, snapshot, materialization, export journal I/O | `adapters/` | `runtime/` |
| Check execution and syntax validation | `adapters/`, `tools/`, packs | `runtime/` — N-06 forbids `import subprocess` there |
| Grant, budget and attenuation decisions | existing `kernel/` surfaces only | new kernel lines; planned delta is zero against the 1438 ceiling |
| Composition, receipt validation, `mhf.event/2` emission, campaign client | `runtime/` | any mutating verb reachable from the campaign client (FH-D11) |
| Protocol and port shapes | `ports/` | concrete I/O or kernel types on the public surface |

Schemas/events need registered readers, version migration and coverage falsifiers before activation. Existing events are never rewritten. All legacy patch frontends must converge on one validated edit set for the CAS profile, with explicit compatibility tests; retain old profiles only where their weaker guarantees are stated. Domain stays pure; syntax/filesystem/process work stays in packs/adapters/tools; runtime composes and emits. Planned kernel delta remains zero LOC, ceiling 1438. M-8 acceptance and M-9/M-10 predicates remain independent obligations.

## 0. Normative System Clauses (TARGET Law)

### 0.1 Identity and causal truth
- **`TC-E-001`** AETHER **MUST** remain a general event-sourced agentic-computation substrate, not a domain-specific harness, workflow engine, or certification system.
- **`TC-E-002`** The fundamental execution unit **MUST** be a typed causal operation within an execution lineage.
- **`TC-E-003`** Durable causal events **MUST** be authoritative facts; large content **MUST** be content-addressed artifacts; projections, indexes, caches, and telemetry **MUST NOT** become a second truth.
- **`TC-E-004`** Replay of persisted facts and probabilistic re-execution **MUST** remain distinct.
- **`TC-E-005`** An agent **MUST** be represented as identity, policy, event-derived projection, and execution boundary. No persistent in-memory Agent object may be required for semantic continuation.

### 0.2 Trusted execution
- **`TC-E-022`** The S0–S12 microkernel **MUST** remain a bounded, domain-blind reference monitor for admissibility, authority, generic budgets, and effect settlement.
- **`TC-E-023`** Capability grants constrain agents; isolation policy constrains plugin code. Neither authority system may substitute for the other.
- **`TC-E-029`** All privileged effects **MUST** preserve declared-versus-emitted identity, merge controls at the call site, persist intent before dispatch, and fail closed on forged or widened authority.
- **`TC-E-030`** Production replay parity **MUST** reconstruct durable storage in a fresh process.
- **`TC-E-031`** Evaluation authority **MUST** remain exterior, identity-separated, and cryptographically bound.
- **`TC-E-032`** Plugins **MUST** be untrusted by default and isolation claims **MUST** be measured rather than asserted.
- **`TC-E-033`** The kernel and domain **MUST** remain domain-blind and within the ratified Trusted Core budget.

### 0.3 Composition, turns, and extensibility
- **`TC-E-008`** Static composition declares available capabilities; the durable trajectory records what actually occurred. Neither graph may impersonate the other.
- **`TC-E-038`** The sole production chain **MUST** remain `mhf.manifest/2 -> CanonicalManifest -> FrozenComposition -> ActivationPlan -> RunPlan -> EpisodeEngine`.
- **`TC-E-039`** The canonical turn loop **MUST** remain unary and sequential except where a separately ratified, measured disposition explicitly authorizes a bounded case.
- **`TC-E-040`** Runtime profiles **MUST** be explicit and identity-bearing in `D_R`; unavailable requested containment **MUST** fail closed.
- **`TC-E-041`** Plugin activation **MUST** materialize a usable service or handle, or fail. Lifecycle metadata alone is not activation.
- **`TC-E-027`** JSON Schema, JCS, and golden vectors are the wire source of truth; generated readers SHOULD replace handwritten mirrors.
- **`TC-E-053`** Pure deterministic transforms, bounded protocol recovery with no silent execution, state-dependent tool policy, deterministic failure attribution, and fail-closed preflight are the accepted `ADR-0106` evolution seam.

### 0.4 Delegation, topology, and budgets
- **`TC-E-013`** `agent.spawn` **MUST** be the sole recursive-delegation primitive and re-enter the ordinary runtime through an attenuated child lineage.
- **`TC-E-014`** Child action, resource, constraint, depth, turn, and budget authority **MUST NOT** exceed the parent.
- **`TC-E-042`** Additive resources are exactly `usd_micros`, `millis`, `tokens`, and `bytes`; depth and turns are structural ceilings.
- **`TC-E-017`** Topology declarations carry no authority. Ready roles **MUST** execute as ordinary mediated children and exchange dependency context through authorized artifact references.
- **`TC-E-049`** The required direct, planner/executor/reviewer, and fork/read/merge topologies **MUST** demonstrate real effects and persisted artifact flow before acceptance.
- **`TC-E-052`** `mhf.topology/2` is an accepted workflow seam, not authority for a second runtime or unrestricted concurrent execution.

### 0.5 State, memory, learning, and evidence
- **`TC-E-018`** Memory retrieval **MUST** verify scoped, revocation-aware authorization before ranking and artifact dereference; retention never authorizes capture.
- **`TC-E-019`** Learned compositions **MUST** be immutable, content-addressed, evaluated on held-out workloads, promoted by authority distinct from generator/evaluator, and reversibly rolled back.
- **`TC-E-026`** `D_H`, `D_R`, and `D_X` **MUST** remain distinct identities and bind every behavior-affecting input at their respective planes.
- **`TC-E-035`** A completed trajectory **MUST** preserve invoked-turn attribution, explicit missingness, conserved cost, and the verified pre-crash prefix.
- **`TC-E-043`** New production event envelopes **MUST** use `mhf.event/2`; compatibility readers may accept frozen predecessors without rewriting historical identities.
- **`TC-E-046`** Facts, artifacts, projections, telemetry, and attestations **MUST** remain distinct. Only exact-subject, digest-addressed, independently verified receipts may close mandatory gates.

### 0.6 Context, completion, recovery, and coding-harness evidence
- **`TC-E-054`** Repository intelligence **MUST** remain an optional, authority-free projection above the substrate. A provider **MUST NOT** grant capabilities, propose or dispatch effects, replace canonical documentation or durable causal facts, or become a required dependency of the domain or kernel. Domain packs and adapters **SHOULD** consume it through the existing context and index seams and **MUST** preserve a deterministic source-level fallback.
- **`TC-E-055`** A bounded repository-context packet **MUST** identify the task, repository snapshot, provider and provider version, query, selected references, estimated token cost, and material omissions by stable identities or digests. It **MUST NOT** imply completeness, freshness, or authority merely because retrieval succeeded.
- **`TC-E-056`** Context selection **MUST** satisfy an explicit token budget. For selected items $S$ and context budget $B_C$, $\sum_{i \in S}\operatorname{tokens}(i) \le B_C$. Composition **MUST** reserve sufficient capacity for at least one bounded recovery or verification cycle; a non-compactable prefix and task state **MUST NOT** consume the entire usable context window.
- **`TC-E-057`** Compaction **MUST** retain the task identity and constraints, current plan or next action, modified resources, last material failure, latest applicable verification, settled effects, and remaining budgets. It **MUST** be identity-bearing and observable; it **MUST NOT** silently erase information required to determine whether completion or another effect is admissible.
- **`TC-E-058`** Model-requested finish **MUST NOT** by itself establish successful completion. Where task policy requires verification, completion **MUST** be admitted only by an applicable successful verification receipt bound to the current task and current post-effect subject. A receipt invalidated by a later relevant effect, a zero-test collection, or a mismatched subject **MUST NOT** admit completion.
- **`TC-E-059`** Harness-local verification and exterior evaluation **MUST** remain distinct. Local verification MAY govern operational completion; it **MUST NOT** self-certify benchmark success, assurance, promotion, or release evidence. Exterior evaluators remain subject to `TC-E-031` and `TC-E-046`.
- **`TC-E-060`** Recovery decisions **MUST** be typed, bounded by failure class, budget-aware, and durably attributable. A retry **MUST NOT** repeat an identical action with identical arguments against materially unchanged state unless the classified failure is transient and the policy explicitly admits another bounded attempt. Exhaustion **MUST** terminate or replan explicitly rather than loop silently.
- **`TC-E-061`** A successful patch effect **MUST** bind its input subject, verify the required preimage or anchors, apply every declared hunk within the authorized workspace, and record the resulting postimage identity. Ambiguous anchors, partial application, workspace escape, or a postimage mismatch **MUST** fail closed and **MUST NOT** be represented as patch success.
- **`TC-E-062`** A benchmark-qualifying run record **MUST** bind at minimum the run and task identities, repository snapshot, harness/configuration identity, provider/model identity, trajectory or event-log identity, terminal state and reason, produced patch identity when applicable, verification and evaluator receipt identities, and explicit token, cost, latency, turn, tool-call, and retry values or missingness. Repeated attempts **MUST NOT** be represented as independent task coverage, and a record lacking its immutable trajectory linkage **MUST NOT** support a capability claim.

### 0.7 Product and release boundary
- **`TC-E-047`** M-9 remains a TARGET operational beta: unified configuration and clients, packaged CLI/API/TUI/Studio, real plugin lifecycle, health/readiness, two real workflows, restart/resume, and offline-after-install behavior.
- **`TC-E-048`** M-10 remains a TARGET final release: supported migrations, backup/restore, deployment profiles, fault injection, security/performance qualification, reproducible artifacts, soak evidence, and an exact-subject signed release envelope.
- **`TC-E-050`** Every client start-run path **MUST** select a valid runtime profile consistently with the identity-bearing profile contract.
- **`TC-E-051`** Client surfaces SHOULD converge on a coherent command and configuration model without moving runtime authority into the clients.

### 0.8 Inviolable Architectural Refusals
AETHER does not authorize a second runtime, a domain-aware kernel, authoritative in-memory agent state, a workflow DAG with independent authority, self-certified promotion, silent containment downgrade, or evidence backfill. Any reversal requires current normative amendment and the required falsifiers; implementation convenience is not authority.

## 0. Invariants

- **I-7.** AST preflight SHALL NOT enter `kernel/dispatch.py` S7/S8. Syntax checks: `adapters/environment/`.
- **I-TCB.** Kernel LOC ≤ 1438 (live 1386 at last A linter pass).
- **INV-DELTA-1.** Domain state schemas: stdlib + JCS only.
- **INV-DELTA-2.** This program SHALL NOT grow kernel past the TCB ceiling.
- **INV-DELTA-3.** Multi-file writes are all-or-nothing. Preflight in the adapter. MECHANISM this-branch (T-17). Product MS-CHANGE remains `OPEN` (T-47–T-49 `[PROPOSAL]`). T-18–T-20 are MECHANISM.
- **INV-DELTA-4.** Agents SHALL NOT mutate tests during implementation. Tamper shield MECHANISM this-branch (T-18). Enumerate via IndexPort, not `Path.glob("test/**")`. Product MS-CHANGE remains `OPEN` (T-47–T-49). Session `_tamper_shield.evaluate(...)` is wired through `_admit_completion`; the default manifest supplies the declared repository index.
- **INV-DELTA-5.** L1–L3 prefix-stable. Compaction SHALL NOT drop settled invariants or falsified hypotheses.
- **I-STATE.** σ is a ledger fold (`fold_task_state`). One schema: `SemanticTaskState` with alias `CodingTaskState`. Lock: `domain/task_state.py` MISSING. Branch: LIVE `8637db55`. MS-RESUME `CLOSED`.
- **I-TXN.** 2PC lives in `adapters/environment/transaction.py`. This branch LIVE (T-17 MECHANISM). Lock `66aa7a3c` MISSING. Not kernel.
- **Single-writer.** One writer per workspace.
- **Authorize-before-retrieve.** Memory recall requires grant.

**Canonical path (FACT).** `ApplicationService → Runtime → HarnessSession → EpisodeEngine → Kernel.dispatch`.
Forge/Chimera SHALL NOT be the product path. Coding Max report arms SHALL be ⊆ `{vg-code-fast, vg-code-balanced, vg-code-max}` (T-23).

**Admission (FACT).** `admission_required` is capability-derived: a harness with `patch.apply` is gated; there is no product-default exemption. T-04 retains an open successor obligation for legacy bare-finish fixtures, but the production gate is active.

**VerificationReceipt.passed (FACT).** `exit_code == 0 and executed_test_count > 0`. Unknown → 0. Forge SHALL NOT set `test_count = 1` (T-06). Chimera SHALL NOT invent `executed = 1` on non-zero exit without a runner summary (`63b77116`).

**I-1** (v2) universal signed finish: `[PROPOSAL]` too strong. A §9.4 "Per-class evidence" wins. Fail-to-pass = **bugfix** only (T-38).
**Mutation ≥ 0.80:** T-39 `[PROPOSAL]`.

## 1. Instrument (CLOSED — `63b77116` + T-01–T-03)

B20 discovery SHALL require `aether.b20.membership/1`. Directory names insufficient. `__pycache__` / hidden / tmp are not tasks. Missing oracle, duplicate ids, digest mismatch → fail closed. Digest is order-independent. Every empirical JSON / `BenchmarkReceipt` SHALL bind `subject_sha`. Missing SHA → refuse. `dry_run` ⇒ `pass`/`cost`/`oracle`/`oracle_passed` null. PASS without patch digest → refuse. Dispositions exactly `{passed, failed, undeterminable, not_run}`. Provider / harness / `DATASET_INVALID` ≠ task fail. Qualifying dirty tree → fail closed (`require_clean_subject`). BAAC SHALL require `aether.baac.challenge/1`; bare `TASK.md` is not a challenge.

## 2. Product thesis and non-goals

### 3.1 Product thesis

AETHER should become an event-sourced operating substrate for engineering campaigns.

The unit of truth is a typed causal operation within a lineage.

The unit of delivery is a verified task contract.

The unit of long-horizon coordination is a durable campaign graph of task contracts.

The unit of learning is a promoted policy or skill with held-out evidence and rollback identity.

### 3.2 Definition of a SOTA engineering agent

A SOTA agent is not one that emits impressive prose.

It is one that maximizes accepted engineering value under constraints:

$$
\pi^*
=
\arg\max_{\pi}
\mathbb{E}
\left[
Q_{\text{functional}}
+ \lambda_a Q_{\text{architecture}}
+ \lambda_m Q_{\text{maintainability}}
- \lambda_c C
- \lambda_r R
\right],
$$

subject to:

$$
\text{authority}(a_t)\subseteq\text{grant}_t,
\qquad
\mathbf{B}_{t+1}\preceq\mathbf{B}_t,
\qquad
\text{accept}(\tau)\Rightarrow V_{\text{exterior}}(\tau)=\text{pass}.
$$

The quality terms mean:

- functional correctness under independent tests;
- architectural conformance under repository-specific constraints;
- maintainability across future changes;
- measured money, token, latency, and effect cost;
- security, regression, uncertainty, and evidence risk.

### 3.3 Non-goals for the backend program

The following are explicitly deferred:

- TUI visual design;
- desktop visualization;
- animated topology graphs;
- a second mutable agent-state database;
- a second execution engine for swarms;
- kernel-level coding semantics;
- automatic self-certification;
- uncontrolled autonomous skill installation;
- benchmark-specific hidden-test guessing;
- hardcoded role classes for every engineering title;
- unbounded parallel agents;
- 90% leaderboard marketing before exact reproducible evidence.

---


---

## 3. VerificationReceipt + counts

Session parser target (T-08): `collected`/`executed`/`passed`/`failed`/`skipped`; `Ran 0 tests` / `0 passed` → 0; unknown runner stays unknown. **B landed the session parser and pack `ParsedTestOutput.runner` on `8637db55` (T-08 `[x]`). Do not uncheck.**

`[PROPOSAL]` catalogs below are kept in full. Implementation merge for task state is B §6.12 (see [`technical.md`](technical.md)).

## 6. Target backend architecture

### 6.1 Architectural shape

```text
Campaign Service
  -> durable CampaignPlan projection
  -> OuterLoopPolicy
  -> Runtime application service
  -> HarnessSession
  -> EpisodeEngine
  -> Kernel S0-S12
  -> capability-scoped adapters
  -> immutable receipts
  -> exterior evaluator
  -> campaign reducer
```

**[PROPOSAL]** Campaign Service as an extra layer above runtime execution. Keep the diagram. Director as a runtime client: see B §6.2 `[PROPOSAL]`.

**FACT (HEAD `66aa7a3c`).** The canonical live path is `ApplicationService → Runtime → HarnessSession → EpisodeEngine → Kernel`. There is no live `CampaignService` type on that path.

**Historical claim.** The stack above treats Campaign Service as the top of the product. That remains the long-horizon outer-loop target (Wave 8). It is not present as a live type and is not a second `EpisodeEngine`.

The outer loop is above runtime execution.

It must not bypass `ApplicationService`, `Runtime`, `HarnessSession`, or the kernel.

**Lock note.** The next three sentences restate the Campaign Service FACT above. Keep both wordings; they are not two layers.

**[PROPOSAL]** Campaign Service as an extra layer above the live stack. Keep the diagram; it is the long-horizon outer-loop target, not a live type.

**FACT (HEAD `66aa7a3c`).** The canonical live path is `ApplicationService → Runtime → HarnessSession → EpisodeEngine → Kernel`. Director as a runtime client: see B §6.2 `[PROPOSAL]`.

**Historical claim.** The diagram treats Campaign Service as the top of the stack. That wording remains the wave-8 target shape.

### 6.2 Required new domain values

**[PROPOSAL]** The eventual implementation should define domain-pure values for:

- `GoalContract`;
- `AcceptancePredicate`;
- `TaskClass`;
- `TaskObligation`;
- `Hypothesis`;
- `EvidenceRef`;
- `VerificationLevel`;
- `RepositoryEpoch`;
- `ContextSelection`;
- `CampaignPlan`;
- `CampaignNode`;
- `CampaignEdge`;
- `PackageHandoff`;
- `DirectorDirective`;
- `EscalationReason`;
- `StrategyTreatment`;
- `BenchmarkSubject`.

These values contain no model provider, filesystem I/O, or runtime authority.

**FACT.** Schema is `vanguard/packages/domain/task_state.py` (`SemanticTaskState` / `CodingTaskState` alias). The only fold remains `runtime/task_state.py` `fold_task_state`. A's 17 extra domain types stay `[PROPOSAL]` law-side targets; do not implement them here.

**Historical claim.** This section read as if the 17 values were required next-code. They are `[PROPOSAL]` relative to the live fold.

**AUTHORIZED (Wave 1).** Two further domain-pure values are *not* `[PROPOSAL]`:
`TaskDisposition` and `SettlementReceipt`, specified in §EW-9.1 and landing in
`domain/evidence/disposition.py` (T-72). They are Wave 1 law and are deliberately
absent from the 17-value `[PROPOSAL]` list above; do not re-derive them here.

### 6.3 Required ports

**[PROPOSAL]** Prefer small ports that express stable capabilities:

- `TaskStatePort` for reading durable task projection;
- `RepositoryIntelligencePort` by extending or composing `IndexPort`;
- `VerificationPort` for typed runner evidence;
- `CampaignStorePort` over the existing event store semantics;
- `OuterLoopPolicyPort` for next-action decisions;
- `DirectorReviewPort` for bounded supervisory judgments;
- `StrategyRegistryPort` for qualified treatments;
- `BenchmarkExecutorPort` for exact-subject attempts.

Avoid provider-shaped interfaces.

Avoid a `SeniorDeveloperAgent` class hierarchy.

**FACT.** Live ports that already cover adjacent jobs include `IndexPort`, evaluator, event-store, and memory SPI. This eight-port list is a competing design versus B §6.12 lattice placement. Keep both; do not explode ports before composing existing ones.

### 6.4 Typed verification receipt

A verification receipt should contain at least:

```text
receipt_id
run_id
episode_id
task_digest
composition_digest
workspace_before_digest
workspace_after_digest
repository_epoch
command_argv
runner_kind
runner_version
exit_code
tests_collected
tests_executed
tests_passed
tests_failed
tests_skipped
selected_test_ids_digest
coverage_scope_digest
changed_surface_digest
stdout_artifact
stderr_artifact
started_at
finished_at
effect_receipt_digest
evaluator_identity
signature
```

Unknown fields remain unknown.

They are never converted to a cheerful default.

### 6.5 Progressive context packet

Each turn should receive a packet with explicit sections:

```text
immutable system core
tool schemas
goal contract
repository authority constraints
semantic task state
current plan frontier
active hypothesis and alternatives
ranked repository evidence
latest effect receipts
latest verification receipt
omitted-items report
remaining budget
next-action affordances
```

The packet carries selection identity and repository epoch.

After every write, dependency-changing command, or generated-file update, the epoch changes.

Stale packets cannot justify completion.

### 6.6 Durable campaign state

The campaign reducer should derive:

- declared objective;
- plan versions;
- node readiness;
- leased node ownership;
- attempt identities;
- package artifacts;
- package verdicts;
- unresolved interfaces;
- risk register;
- budget allocations;
- operator interventions;
- next ready nodes;
- terminal disposition.

The reducer must be deterministic.

Checkpoints remain disposable caches with proof obligations.

### 6.7 Content-addressed handoffs

Agents should exchange artifact references, not transcript copies.

A package handoff should contain:

- goal digest;
- plan-node digest;
- relevant source revision;
- changed-surface digest;
- interface delta digest;
- verification receipt references;
- unresolved risks;
- next recommended action;
- explicit uncertainty;
- content digest.

This provides bounded communication and replayable provenance.

### 6.8 Director semantics

The director may emit only:

- `dispatch_ready_node`;
- `request_revision`;
- `request_investigation`;
- `request_integration`;
- `pause_for_operator`;
- `reallocate_budget` within its grant;
- `close_campaign` when predicates resolve;
- `mark_undeterminable`.

The director may not:

- forge verification;
- write around the worker grant;
- mutate historical events;
- promote its own skills;
- declare exterior acceptance;
- silently add scope.

### 6.9 Single-writer rule

Parallel agents may investigate disjoint questions.

Repository writes should default to one active writer per workspace.

Alternative branches may be used only with explicit merge ownership.

Every merge is a new effect with its own verification obligation.

This avoids shared-worktree races and invisible conflict resolution.

---


---

## 4. Task classes and per-class evidence

Per-class evidence wins over v2 I-1. Fail-to-pass (v2 §5.3) applies to class `bugfix`.

### 9.3 Task classes

Completion policy must branch on declared task class, not prompt keyword guessing.

Supported classes:

- `bugfix`;
- `feature`;
- `greenfield`;
- `migration`;
- `refactor`;
- `documentation`;
- `explanation`;
- `research`;
- `benchmark`;
- `architecture_plan`.

### 9.4 Per-class evidence

Bugfix requires:

- reproduced failure or explicit non-reproducibility reason;
- focused regression test;
- changed implementation;
- passing focused falsifier;
- no applicable regression failure.

Feature requires:

- acceptance requirements mapped to tests;
- public interface behavior;
- negative paths;
- compatibility checks;
- documentation obligation classification.

Greenfield requires:

- scaffold baseline;
- declared entrypoint;
- structural checks;
- behavioral tests;
- installation or startup smoke test;
- required files and configuration.

Migration requires:

- enumerated consumers;
- compatibility policy;
- transformed call sites;
- old-path negative check;
- integration verification.

Explanation requires:

- evidence-linked claims;
- inspected-symbol references;
- no workspace mutation unless requested;
- uncertainty markers.

Research requires:

- source provenance;
- claim-to-source mapping;
- date and version boundaries;
- contradiction handling;
- no fabricated citations.

This per-class evidence matrix **wins** as program law over v2 §5.3 / I-1 “no finish without signed `VerificationReceipt`”. That universal signed-finish rule remains `[PROPOSAL]` and is too strong versus this matrix and versus the local vs exterior evaluator split (B §3.4). Fail-to-pass is required for **bugfix**; it is not a universal finish law for explanation or research. Bugfix admission SHALL require a failing pre-verify and a passing post-verify; a vacuous reproducer (pre-verify already passing) SHALL be refused (T-38). `true` and `echo 10 tests passed` SHALL NOT admit completion (T-42).


---

## 10. Prompt, policy, model, security

## 21. Agent prompt and policy architecture

### 21.1 Stable system core

The stable core should teach:

- evidence hierarchy;
- authority limits;
- state and uncertainty semantics;
- tool grammar;
- completion protocol;
- concise communication requirements.

It should not contain a giant tutorial for every task class.

### 21.2 Task policy fragments

Inject small policy fragments based on declared task class:

- bugfix method;
- greenfield method;
- migration method;
- research method;
- explanation method;
- review method.

Fragments are versioned and independently ablatable.

### 21.3 Dynamic state

Render the semantic task state in a compact machine-readable form.

Do not ask the model to reconstruct the plan from raw dialogue.

### 21.4 Tool ergonomics

Follow the Agent-Computer Interface principle:

- concise commands;
- predictable output;
- bounded observations;
- stable error classes;
- explicit truncation;
- exact path and line references;
- atomic patches;
- easy targeted tests;
- no misleading success responses.

### 21.5 Prompt evaluation

Treat prompt modifications as code changes.

Require:

- version identity;
- regression corpus;
- token cost delta;
- protocol compliance;
- paired benchmark evidence;
- rollback path.

---

## 22. Model strategy

### 22.1 Model-neutral substrate

The framework should remain model-neutral.

Model-specific behavior belongs in capability profiles, dialect adapters, and routing policy.

### 22.2 Routing tiers

Candidate tiers:

- cheap fast model for classification and bounded localization;
- balanced coding model for normal implementation;
- frontier model for high-risk architecture, hard recovery, or final review;
- deterministic local or cassette models for protocol testing.

### 22.3 Escalation

Escalate only when grounded conditions hold:

- repeated distinct failures;
- unresolved high-risk ambiguity;
- change surface above threshold;
- architecture decision required;
- current model violates protocol repeatedly;
- expected value exceeds incremental cost.

### 22.4 Provider failure

Provider errors must preserve:

- request identity;
- partial usage if known;
- retry policy;
- idempotency;
- no false task verdict;
- resume state.

### 22.5 Routing experiments

Compare:

- one strong model throughout;
- cheap localizer plus strong implementer;
- strong planner plus cheap implementer;
- cheap worker plus strong reviewer;
- dynamic escalation.

Hold task set, tools, context, and verification fixed.

---

## 23. Security, control, and operator semantics

### 23.1 Least authority

Each role receives the minimum scope needed.

Read-only investigators do not receive patch or shell write capabilities.

Reviewers do not receive promotion authority.

The director does not receive arbitrary workspace write authority.

### 23.2 Budget attenuation

For parent budget vector $\mathbf{B}_p$ and child $\mathbf{B}_c$:

$$
\mathbf{B}_c\preceq\mathbf{B}_p.
$$

Across siblings:

$$
\sum_c \mathbf{B}_c + \mathbf{B}_{\text{reserved}}
\preceq
\mathbf{B}_p.
$$

### 23.3 Human control points

Require operator approval for configurable risk classes:

- external publication;
- credential or secret access;
- destructive data changes;
- dependency release;
- production deployment;
- scope expansion;
- high-cost budget increase;
- benchmark submission;
- skill promotion to default.

### 23.4 TUI-ready backend events

Although frontend work is deferred, backend events should expose:

- campaign state;
- ready/running/blocked nodes;
- active lineage;
- current goal and next action;
- budgets;
- recent effects;
- verification level;
- pending approval;
- uncertainty;
- artifact links;
- director directives.

The future TUI becomes a projection and command client.

It must not become another runtime authority.

---


---

## 11. Stop, simplify, and rollback

## 28. Stop, simplify, and rollback rules

Stop a treatment when:

- false completion rises;
- cost per signed pass worsens beyond preregistered tolerance;
- confidence interval excludes useful lift;
- architecture boundaries are weakened;
- replay identity cannot be maintained;
- operator control becomes ambiguous.

Simplify when:

- two roles produce materially identical outputs;
- an LLM judgment can be replaced by deterministic evidence;
- a topology adds latency without lift;
- a new port duplicates an existing generic port;
- a cache cannot prove freshness.

Rollback when:

- promoted skill regresses held-out tasks;
- model route changes protocol reliability;
- new context policy loses mandatory facts;
- new scheduler produces non-deterministic effect ordering;
- external evaluator reports subject mismatch.

---


---

## 12. Research, explanation, and benchmark taxonomy

## 25. Benchmark task taxonomy

### 25.1 Scope axis

- single symbol;
- single file;
- small multi-file;
- subsystem;
- cross-subsystem;
- repository-wide;
- multi-repository campaign.

### 25.2 Horizon axis

- under 10 expert minutes;
- 10-60 minutes;
- 1-4 hours;
- 4-16 hours;
- 16-40 hours;
- multi-day.

Human duration estimates need provenance and uncertainty.

### 25.3 Work-type axis

- localization;
- bug repair;
- feature delivery;
- migration;
- refactor;
- test creation;
- performance;
- security;
- greenfield;
- architecture;
- research;
- explanation.

### 25.4 Environment axis

- hermetic;
- local toolchain;
- sandboxed;
- networked read-only;
- external service;
- operator-gated.

### 25.5 Failure attribution axis

- model cognitive error;
- context selection error;
- tool interface error;
- protocol error;
- harness error;
- evaluator error;
- dataset invalid;
- provider error;
- budget exhausted;
- policy denial;
- undeterminable.

---

## 26. Research and explanation agents

### 26.1 Shared substrate

Research and explanation should reuse:

- task contracts;
- context selection;
- source provenance;
- budget accounting;
- event sourcing;
- artifact graphs;
- exterior evaluation;
- campaign planning.

### 26.2 Research workflow

```text
scope question
  -> declare freshness requirements
  -> retrieve primary sources
  -> extract claims
  -> triangulate contradictions
  -> maintain claim-evidence graph
  -> synthesize with uncertainty
  -> citation audit
  -> publish artifact
```

### 26.3 Explanation workflow

```text
identify audience
  -> route to symbols and owners
  -> inspect causal slice
  -> build minimal mental model
  -> cite exact code evidence
  -> test explanation against questions
  -> disclose uncertainty
```

### 26.4 Research verification

Verify:

- every material factual claim has a source;
- sources support the claim directly;
- temporal claims include dates;
- primary sources are preferred;
- contradictions are not hidden;
- quotations respect limits;
- local repository claims bind to current source revision.

---


---

## TransformSpec (proposal sketch + live fields)

### 2.4 Pure Artifact-Transform Algebra
All in-memory transformations (diff parsing, AST skeletonization, token estimation, linting) must implement the **Pure Transform Contract** (`domain/transforms/contracts.py`):

**`[PROPOSAL]` alias sketch** (original v2 draft fields `name` / `input_type` / `output_type` / `timeout_ms`). Keep as a naming alias if a later adapter wants friendlier field names. It is **not** the live dataclass.

```python
@dataclass(frozen=True, slots=True)
class TransformSpec:
    name: str
    input_type: str
    output_type: str
    max_input_bytes: int
    max_output_bytes: int
    timeout_ms: int

@dataclass(frozen=True, slots=True)
class TransformResult:
    success: bool
    output_digest: str
    output_payload: Mapping[str, Any]
    diagnostics: tuple[str, ...]
    execution_duration_ms: int
```

**FACT — live `TransformSpec` fields** from [`vanguard/packages/domain/transforms/contracts.py`](../../../vanguard/packages/domain/transforms/contracts.py) lines 20–31 (HEAD `66aa7a3c`):

```python
@dataclass(frozen=True, slots=True)
class TransformSpec:
    """Immutable specification declaring transform capabilities and resource bounds."""

    transform_id: str
    version: str
    input_schema: str
    output_schema: str
    config_digest: str = ""
    deterministic: bool = True
    max_input_bytes: int = 10_000_000
    max_output_bytes: int = 10_000_000
    timeout_seconds: float = 30.0
```

Live sibling types in the same module (FACT, not a replacement of the sketch above): `TransformInput` (`artifact_digest`, `schema_id`, `labels`); `TransformDiagnostic` (`code`, `severity`, `message`, `location`); `TransformOutput` (`status`, `payload`, `output_schema`, `diagnostics`, `confidence_ppm`); live `TransformResult` (`status: TransformStatus`, `output_digest: str | None`, `output_schema: str | None`, `diagnostics`, `confidence_ppm`). `TransformStatus` is `accepted | rejected | unchanged | retryable_error | fatal_error`.

**Invariants on Transforms**:
- **I-TX-1 (Pure Stdlib & Zero I/O)**: Transforms must never execute filesystem writes, subprocess calls, network sockets, or system clocks.
- **I-TX-2 (Idempotency & Provenance)**: The same `(input_digest, config_digest)` must deterministically yield the exact same `output_digest`.
- **I-TX-3 (TCB Exemption)**: Transforms live in `domain/transforms/` and do not consume Kernel TCB lines of code.

---


---

## 9. CLI and verbs

MECHANISM: `run` / `status` / `resume` / `evidence` / `cost`. `[PROPOSAL]`: `cancel` / `doctor` / `checkpoint` / `--non-interactive`.

## 22. Live tool/verb inventory (lock HEAD `66aa7a3c`)

Appended at lock; does **not** replace §3. **FACT** from pack YAML and toolkit source on HEAD `66aa7a3c`.

Harness [`packs/code-default/harness.yaml`](../../../packs/code-default/harness.yaml) declares:

| Verb | Pack source | Notes (FACT) |
|---|---|---|
| `fs.read` | `harness.yaml` capabilities; `plugins/fs.yaml`; `toolkits/fs_toolkit.py` | Windowed: optional `start_line` / `end_line` in schema; full-file digest if omitted |
| `fs.search` | `harness.yaml`; `plugins/fs.yaml`; `FsToolkit` | Pattern search over workspace files |
| `fs.list` | `plugins/fs.yaml` + `FsToolkit` (not listed on the harness.yaml capability block) | Glob list; kernel classifier treats `fs.list` as observation |
| `patch.apply` | `harness.yaml`; `plugins/ast-patch.yaml`; `toolkits/ast_patch.py` | Sequential `GitEnvironment.apply`; post-write `ast.parse` is observation-only |
| `proc.exec` | `harness.yaml`; `plugins/terminal.yaml`; `toolkits/terminal_runner.py` | Allowlisted `git,pytest,ruff,python3` |

**Index toolkit.** [`packs/code-default/plugins/index.yaml`](../../../packs/code-default/plugins/index.yaml) still declares capability verb **`fs.read`**. `IndexToolkit` in `toolkits/repo_map.py` also exposes `index.refresh`. Ranking stays out of `IndexPort` (observation-only). Pack also has `multi_file_completeness.py` and `GreenfieldPolicy` (MECHANISM; see §3.4).

**Facade (MECHANISM).** `CodingMaxFacade`: `run` / `status` / `resume` / `evidence` / `cost`; presets `fast|balanced|max`.

**Still MISSING in HEAD `66aa7a3c` (keep as `[PROPOSAL]`).** `transaction.py` 2PC, `tamper_shield.py`, `progressive.py`, `WorkspaceEpoch`, `agency/prediction/`, `runtime/event_store.py`, `adapters/index/`. Event store owner is `adapters/stores/event_store.py`; index owner is `adapters/stores/repo_index.py`. Edit/2PC mechanics live in **v2**; law/profiles live in **A**.

---

## 23. Product target loop

Appended at lock; does **not** replace §3.2 / §6.1. Product stages (SOTA suggestion):

```text
INGEST → DISCOVER → PLAN → EDIT → VERIFY_TARGETED → RECOVER → VERIFY_BROAD → COMPLETE
```

**FACT.** Stage transitions follow receipts, not conversational `finish`. Live inner loop is `ContextCompiler` freeze of L1–L3 at construction, then `EpisodeEngine`: observe → propose → `recover_proposal` → `Kernel.dispatch` → ingest (`agency/episode/engine.py`). Compile is **not** a step inside `EpisodeEngine`.

**FACT.** `admission_required` exempts `vg-code-default` / `vg-code-lex`, else `"patch.apply" in verbs`. `ADMISSION_GATED_HARNESSES` is unused in runtime. `VerificationReceipt.passed` ⇔ `exit_code == 0 and executed_test_count > 0`. Session `_observed_test_count` returns 0 if unparseable. Forge `parse_test_output` and Chimera bare-exit-0 parsing leave unknown counts at 0 (T-06).

**Pointer.** Reliability order and competency profiles: A. Tickets 01–35 and lattice: this file. 2PC / AST / later phenotypes: v2 as `[PROPOSAL]` except sequential git apply + post-write `ast.parse` (MECHANISM).

---


---

## Progressive context packet (binding placement)

Keep `ContextPacket`. FEATURE_SPEC 4-tier budget is **L4/L5 policy on existing `ContextCompiler`**, not a second compiler class (`PRG-01` alias → T-15).

| FEATURE_SPEC tier | Existing layer | Content |
|---|---|---|
| 0 Invariant anchor | L1 + L4 head | goal, active step, settled invariants |
| 1 Negative memory | L4 | dead ends, falsified hypotheses |
| 2 Active AST slice | L5 | current files, epoch-bound |
| 3 Symbol stubs | L5 remainder | IndexPort stubs with omissions |

## WorkspaceEpoch (T-14)

Lock `66aa7a3c` **MISSING**. This branch **LIVE** — see §6 / §14.

```text
WorkspaceEpoch := { treeHash, indexDigest, sourceRevision, compiledAtTurn }
```

Stale epoch ⇒ refresh or fail closed. Do not put `repo_map` or σ into frozen L3.

## Dialect FACT split

Wire recovery: `adapters/models/dialect.py` T-21 MECHANISM. Truncated JSON, DeepSeek fence, and XML tool tags are classified; malformed never reports `ok`. Malformed → Proposal: `agency/episode/protocol_recovery.py`. Taxonomy in Appendix H §8.

## 2PC / tamper placement

- 2PC: `adapters/environment/transaction.py` this-branch LIVE (T-17 MECHANISM). Lock `66aa7a3c` MISSING. Multi-file `GitEnvironment.apply` preflights `ast.parse` then all-or-nothing flush and restores original bytes and modes on refusal. Stale declared preimages, ambiguous anchors, and incomplete hunks fail closed before write (`adapters/environment/hunks.py`, T-108). Single-file sequential observation (S8-B-09) unchanged. T-18–T-20 MECHANISM; MS-CHANGE stays `OPEN` on T-47–T-49. CAS workspace promotion is not introduced here.
- Tamper: `runtime/governance/tamper_shield.py` this-branch LIVE (T-18). Enumerate via IndexPort; `Path.glob("test/**")` is insufficient. The session freezes and evaluates it through `_admit_completion`; the default product manifest declares `repo_index`.

---

## 5. Task state

Implementation merge is B §6.12: `SemanticTaskState` in `domain/`; `fold_task_state` in `runtime/`; unknown event kinds ignored; no `"test" in action.lower()`. A §6.2 extra types stay `[PROPOSAL]` in §16. `task_class` is a field on the projection (T-43).

Branch: `vanguard/packages/domain/task_state.py` defines `SemanticTaskState` and `CodingTaskState = SemanticTaskState` (`8637db55`).

## 6. Context packet and WorkspaceEpoch

Keep `ContextPacket`. FEATURE_SPEC 4-tier budget is L4/L5 **policy** on existing `ContextCompiler` (not `progressive.py` as a second compiler) — T-15 this-branch **LIVE**. `WorkspaceEpoch := {treeHash, indexDigest, sourceRevision, compiledAtTurn}` this branch **LIVE**; lock `66aa7a3c` **MISSING**. T-14. Product compile stamps epoch on the existing packet; write refreshes the index then rebinds (T-16); stale or missing epoch MUST NOT admit `completed`. Tool bodies are distilled at the effect boundary with a goal echo at L5 (T-36). Packet `omissions` is a ledger; truncated ≠ complete (T-37). IndexPort unbound/down binds epoch from the environment snapshot with explicit `index.port.unbound` or fail-closed `INDEX_UNBOUND` — never invents symbols (T-45). Legacy packets without epoch may still resume via identity fields. T-46 ranking stays `[PROPOSAL]`.

## 7. 2PC and tamper

Living rule: T-17–T-20 MECHANISM — 2PC, IndexPort tamper freeze, greenfield vacuous-oracle reject, brownfield implicated-set fail-closed this-branch LIVE; lock `66aa7a3c` MISSING. Product MS-CHANGE remains `OPEN` (T-47–T-49 `[PROPOSAL]`). Historical CMX-09 schemas remain in Appendix H.

## 8. Dialect

Wire recovery: `adapters/models/dialect.py` T-21 MECHANISM. Truncated JSON, DeepSeek fence, and XML tool tags are classified; malformed never reports `ok`. Proposal recovery remains `agency/episode/protocol_recovery.py`.

## EW-9. Electroweak v0.9.3 Wave 1–2 settlement and control delta

This section is the typed TARGET contract for the Electroweak Wave 1–2 package
set. It points to the product definition in §3.2 of this
specification and does not replace the
historical Wave 0–10 capability recipes in [`technical.md`](technical.md).
Wave 1 is Settlement & Signal Truth; Wave 2 is Frozen Control, Honest
Instrument & Presets. Edit/retrieval, context/reliability, and outer-director
treatments remain outside this delta and MUST NOT be presented as Wave 1–2
next-code.

### EW-9.1 Two-axis settlement wire contract (TRUTH / T-72)

The settlement model SHALL preserve two orthogonal questions:

| Axis | Domain | Values | Existing ledger representation |
|---|---|---|---|
| run termination | `RunTermination` in `agency` | `completed`, `abstained`, `escalated`, `cancelled`, `budget_exhausted`, `instrument_error`, `runtime_error`, `abandoned` | `EpisodeCompleted` with `terminal_status` only |
| task evaluation | `TaskDisposition` in `domain/evidence` | `passed`, `failed`, `undeterminable`, `not_run` | `VerdictRecorded` with `schema: aether.settlement/1` |

`TaskDisposition` is the shared four-state vocabulary. Only `passed` satisfies
an acceptance predicate. `undeterminable` and `not_run` are missingness, not a
negative task result. `disposition_to_outcome()` SHALL refuse `not_run` because
an evidence envelope binds a claim about an executed subject and therefore has
only `passed | failed | undeterminable` outcomes.

`SettlementReceipt` SHALL be a domain-pure, immutable value with this logical
shape; §3.2 of the Synthesis of Record owns the future module body and MUST NOT
be pasted into this specification:

```text
aether.settlement/1 := {
  taskId: non-empty string,
  disposition: TaskDisposition,
  terminalStatus?: string,
  oracleDigest?: digest,
  verificationSubjectDigest?: digest,
  executedTestCount: integer >= 0,
  envelopeDigest?: digest,
  undeterminableReason?: non-empty string
}
```

The value SHALL refuse all of the following:

- `passed` when `executedTestCount == 0`;
- `passed` without both `oracleDigest` and `verificationSubjectDigest`;
- `undeterminable` without `undeterminableReason`;
- `not_run` with any execution count, oracle digest, verification-subject
  digest, or envelope digest;
- an empty `taskId`, a negative test count, or an unknown disposition.

`terminalStatus` remains a plain string in the domain value: `domain` SHALL NOT
import `agency`, and neither axis SHALL be computed from the other. In
particular, oracle `passed` MUST NOT rewrite a run to `completed`.
`terminal_status=abandoned` with `disposition=passed` is legal and MUST replay
without contradiction. Conversely, `EpisodeCompleted` MUST NOT gain a
`disposition` field.

No new ledger event kind is allocated. The existing `EpisodeCompleted` and
`VerdictRecorded` owners SHALL carry the axes above. Adding an event kind still
requires its complete allocation package; this delta does not authorize one.
The benchmark vocabulary SHALL derive from `TaskDisposition`, and readers MUST
use its positive predicate rather than `disposition != failed`.

### EW-9.2 Wave 1 — Settlement & Signal Truth

Wave 1 is Route R repair work across **HAR-01**, **TRUTH**, **INS-01**, and
**BRG-01**. Its acceptance contract is:

| Package | Binding contract |
|---|---|
| HAR-01 | `NATIVE` tool calling is capability-bound. A production route may declare `ToolCallStyle.NATIVE` only after a provider-shape vector verifies native dispatch of both `patch.apply` and `finish`. Unknown or unverified routes retain the fail-closed degradation chain `NATIVE -> JSON_SCHEMA -> FENCED_JSON -> TEXT_GRAMMAR`; no registry-wide promotion is permitted. Manifest approval policy, the declared `finish` tool, minimum orientation commands, effect budgets, workspace initialization, and completion-tool restrictions SHALL reach the product path without hardcoded replacement. Fenced action notes MAY recover into candidate proposals, but unparsed invocations or a mutation-free unsolicited `finish` SHALL be rejected. |
| TRUTH | Record both settlement axes per §EW-9.1. Before T-04 removes the product-default admission exemption, preserve the named RF-25 successor baseline. Mutating completion SHALL bind the mutation receipt, current postimage/epoch, relevant tests collected and executed, zero test exit, tamper evaluation against the frozen test set, and no unresolved omission or stale-index marker. Greenfield evidence SHALL distinguish structural from behavioral success and reject `pass` / `NotImplementedError` vacuity. The greenfield prompt SHALL not prohibit the scaffold -> red oracle -> atomic 2PC workflow. |
| INS-01 | Generate a unique run identity for each invocation; continuation is explicit `--resume <id>`. Product receipts SHALL carry actual model routes, token counts, verified step identities, and cost provenance. This package extends product-path integrity and MUST NOT reopen §1 or `MS-INSTRUMENT`. |
| BRG-01 | Local inference lifecycle is fail-closed: valid flash-attention flag, live child process, matching PID and `/props` identity before `ONLINE`, identity-scoped stop rather than blanket process killing, typed empty/max-token failures, and no retired provider alias on the supported route. |

HAR-01 additionally requires reproduce-first handling for uncertain boundaries.
The streaming abort at T-70a MUST be captured by a failing regression before a
fix is selected and MUST NOT be closed as `no_defect` from an earlier hedge.
Duplicate `EffectStarted`, unpopulated effect budgets, autonomous-loop tool
restriction, and Git initialization SHALL likewise be re-verified at current
HEAD before their repair boundary is chosen. Any resulting kernel change would
require separate authorization and TCB accounting; this documentation delta
does not change the 1386-line TCB baseline.

Wave 1 acceptance requires the L0 public-CLI smoke triad to produce honest
end-to-end evidence. L0 may license only “Wave 1 landed”; it MUST NOT license a
capability or pass-rate claim.

**Implementation checkpoint (non-normative, 2026-09-05).** Phase 0 / `MS-INSTRUMENT`
remains closed on its frozen benchmark-harness subject. The Wave 1 mechanisms
listed above are implemented and their focused trust-spine falsifiers pass;
`MS-TRUTH` remains `MECHANISM`, not empirical close, until T-92/L0, the T-04
successor obligation, and exact-subject convergence evidence are resolved.
The current branch also carries five boundary failures across the new benchmark
slice and `runtime/cli.py`, plus four related-surface failures on the
`coding_max` facade and RF-90 fakeBackend; they must be repaired before any
measured subject is frozen.

### EW-9.3 Wave 2 — Frozen Control, Honest Instrument & Presets

Wave 2 establishes the content-addressed control used by later treatments. It
contains **CMX-01 (T-79)**, the Wave 2 portions of **INS-01**, and **EXP-01**:

- The product path SHALL select the existing `aether.code-preset/1` catalog.
  It SHALL preserve the declared `fast`, `balanced`, and `max` budgets rather
  than inventing new values: respectively `(usd_micros, millis, tokens, turns)`
  are `(50000, 300000, 16000, 8)`, `(150000, 900000, 40000, 20)`, and
  `(400000, 2400000, 96000, 40)`. The facade SHALL NOT impose a universal
  `max_turns=40` default. Additive reservation dimensions remain
  `usd_micros | millis | tokens | bytes`; `turns` and `depth` remain structural
  ceilings and MUST NOT be summed as reservations.
- The frozen subject SHALL execute through the public product path, including
  `runtime.entrypoint.execute`; a direct `Runtime.execute_profiled` benchmark
  is a different subject and cannot qualify what ships.
- The candidate SHA, dirty flag, suite membership/digest, task and oracle
  digests, manifest/preset/model identities, provider/server identities,
  sampling/prompt/tool-schema digests, and cost provenance SHALL be frozen.
- `MS-CONTROL` closes only for single-worker `vg-code-balanced` on the exact
  candidate SHA at L2 with `n >= 30`, Wilson lower bound `>= 0.40`, and
  false-completion rate exactly zero. The result SHALL be published when
  positive, negative, or undeterminable.

**Implementation checkpoint (non-normative, 2026-09-05 session stop).** Wave 2
has no accepted task. T-79/T-89/T-92–T-95 are implementation candidates with
31 named focused tests green. Acceptance is blocked by five architecture-
boundary violations, four related-surface failures (CMX-04 facade ×2; RF-90
fakeBackend ×2), incomplete full verification, and absent live evidence.
T-92's hermetic run proves runner mechanics, not the live L0 disposition.
T-26 remains `UNFROZEN` with the L2 arm pinned (single-worker `vg-code-balanced`
/ `balanced` / `entrypoint.execute`). T-27/T-51/T-52 remain open. **T-97 is
deferred this pass** (filed under INS-01; TypeScript help/`-m`; not vanished).
T-95 does not close `MS-CONTROL`. T-80 and T-96 remain post-control treatments.
Declared `budgetCeiling` MUST match `presets.json`; any tighter loop bound is
recorded separately as `budgetAttenuation` and MUST NOT rewrite the ceiling.

### EW-9.4 Measurement ladder and evidence row (EXP-01)

Rungs answer different questions and SHALL NOT be collapsed:

| Rung | Frozen subject | License |
|---|---|---|
| L0 | `P0-FIB`, `P0-CSV`, `P0-BUG`; three fresh workspaces through the public CLI | Wave 1 smoke only; no pass rate |
| L1 | 4 greenfield + 4 single-file bug + 4 data/CLI tasks | fixture/oracle/instrument readiness only; tasks tuned here MUST NOT be scored |
| L2 | exact-subject product-path multi-class suite, `n >= 30` | control qualification and preregistered single-variable Route L verdicts |
| L3 | immutable `(manifest x model x preset)` bundle, `n >= 30` per arm | relative, task-class-specific arm claims only |

After the first measured attempt at a rung, changing a prompt, tool, fixture,
oracle, model, server flag, sampling policy, or budget resets that rung. Each
rung opens only after the lower rung is green on the current subject SHA; L2
also requires INS-01 and BRG-01, and L3 requires closed `MS-CONTROL`.

The harness SHALL append one immutable evidence row per run and refuse a row
with absent required data. Missingness is an explicit value, never a blank:

```text
identity:     subject_sha, dirty_flag, suite_digest, n, task_id, task_digest,
              oracle_digest, run_id
arm:          manifest_digest, preset, model_id, provider, server_build,
              gguf_digest, quantization, context_size, sampling_digest,
              prompt_digest, tool_schema_digest
execution:    evidence_label, raw_response_digest, valid_tool_calls,
              malformed_tool_calls, recovery_attempts, turns,
              time_to_first_valid_action_s, latency_s
change:       patch_digest, postimage_digest, files_changed, no_op
verification: tests_discovered, tests_executed, tests_passed, tests_failed,
              tamper_digest, tamper_verdict
settlement:   terminal_status, disposition, undeterminable_reason
economics:    prompt_tokens, completion_tokens, cache_read_tokens,
              cache_write_tokens, cost_usd_micros | local_time_proxy_s
provenance:   hypothesis_id | "control", control_digest, varied_dimension
```

`REPLAY`, `LIVE-HISTORICAL`, `STATIC`, `UNDETERMINABLE`, `LIVE-LOCAL`, and
`LIVE-HOSTED` evidence SHALL be labeled. Replay or historical evidence MUST NOT
share a published capability table with current live evidence. Zero model calls
settle as `not_run`, never as model failure. Undeterminable rows require a
reason and are excluded from capability denominators. A result writer SHALL
refuse `pass_rate_pct` when the observed result count is smaller than the frozen
suite size. Every non-control mechanism SHALL bind to a preregistered hypothesis
and one varied dimension.

Every control and treatment report SHALL publish false-completion rate, live
oracle pass rate with Wilson lower bound, valid first-tool-call rate,
malformed-tool/recovery rate, no-op rate, time to first valid action, turn waste
`W`, and token efficiency `kappa`. False-completion rate `= 0` is a hard veto:
no pass rate, lift, latency, token, or cost advantage can override it. Only
`LIVE-*` current rows enter capability rates.

## 13. Stop-rollback / research-explanation remainder

SHALL text for stop/simplify/rollback and research/explanation lives in §§11–12 above. Do not treat handbook prose as HEAD architecture.

## 14. MISSING vs HEAD

| Module | Lock `66aa7a3c` | This branch |
|---|---|---|
| `domain/task_state.py` | MISSING | LIVE (`8637db55`) |
| `runtime/task_state.py` `fold_task_state` | LIVE (old schema) | Fold of domain type (`8637db55`) |
| `adapters/environment/transaction.py` | MISSING | LIVE (T-17 MECHANISM). Lock `66aa7a3c` still MISSING |
| `runtime/governance/tamper_shield.py` | MISSING | LIVE (T-18, session-wired) |
| `agency/context/progressive.py` | MISSING | Do not add — policy on `ContextCompiler` |
| `runtime/event_store.py` | MISSING | Owner remains `adapters/stores/event_store.py` |
| `ADMISSION_GATE_EXEMPT` | FACT | Removed from the production decision; T-04 successor fixtures remain open |
| `domain/workspace_epoch.py` `WorkspaceEpoch` | MISSING | LIVE (T-14). Lock `66aa7a3c` still MISSING |
| Index refresh after write (T-16) | MISSING | LIVE (`33dc7c33`) |
| L4/L5 policy on `ContextCompiler` (T-15) | MISSING | LIVE (`2a4cdaad`); no `progressive.py` |
| ResultDistiller + L5 goal echo (T-36) | MISSING | LIVE (`179f5616`) |
| Packet omission ledger (T-37) | MISSING | LIVE (`81b7b572`) |
| No-index fallback (T-45) | MISSING | LIVE (`c7995195`); `INDEX_UNBOUND` typed |

## 15. Error / verification matrix

Living refusals: T-42 / T-38 / T-25 in §1 and §4. A §24 handbook matrix stays in [`technical.md`](technical.md).

## 16. `[PROPOSAL]` catalogs

A §6.2 17 types, extra ports, CampaignPlan, mutation 0.80 — tagged `[PROPOSAL]`. B §6.12 wins for what to implement.

---

*Historical CMX-09 draft. Living §§ 0–16 win.*

# Appendix H: Historical CMX-09 delta

The following is the pre-PHASE-0 `spec.md` body, preserved in full.

# Feature Delta Specification: W-092-F1 / CMX-09 (Canonical Coding Max Convergence)

## 1. Architectural Base & Invariant Topography

This document is the authoritative typed delta contract for the active execution ticket **`W-092-F1 / CMX-09`**. It defines the exact interfaces, data schemas, transaction protocols, and error matrices added to the codebase. Upon gate passage and PR merge, these contracts are promoted into canonical `docs/architecture/` and `docs/SPEC.md`.

- **Base Architecture Extended**:
  - `docs/architecture/boundaries.md` (Hexagonal boundary flow: `domain <- ports <- kernel <- agency <- runtime -> adapters`)
  - `docs/architecture/data-flow.md` (Monotonic capability dispatch and immutable event emission)
- **Target Subsystems Modified**:
  - `vanguard/packages/domain/task_state.py` (New: Semantic task state vector & DAG)
  - `vanguard/packages/adapters/environment/transaction.py` (New: Two-Phase Commit Multi-File Transaction Manager)
  - `vanguard/packages/runtime/governance/tamper_shield.py` (New: Cryptographic Test Tamper Shield)
  - `vanguard/packages/agency/context/progressive.py` (New: Multi-Tier Progressive Context Compiler)
  - `vanguard/packages/adapters/models/dialect.py` (Enhanced: Multi-pattern recovery & typed failure classes)

---

## 2. Invariants & Boundary Constraints

- **INV-DELTA-1 (Hexagonal Purity)**: All state schemas (`SemanticTaskState`, `TaskStep`) in `domain/` must use Python stdlib only, serialize deterministically via RFC 8785 JCS, and contain zero I/O or adapter imports.
- **INV-DELTA-2 (TCB Line Budget Limit)**: No changes in this feature wave may increase `vanguard/packages/kernel/` beyond the strict $\le 1438$ logical LOC ceiling.
- **INV-DELTA-3 (Two-Phase Commit Atomic Safety)**: No multi-file modification may write partially to disk. All candidate file mutations must pass in-memory AST syntax validation (`ast.parse`) before disk flush. Any syntax error, incomplete hunk, stale preimage, or later-file failure triggers full rollback to pre-transaction content and modes.
- **INV-DELTA-4 (Anti-Tampering Test Isolation)**: Autonomous agents are strictly prohibited from mutating test suites during implementation. All test files are hashed at turn 0; any modification to test baselines produces immediate fail-closed rejection.
- **INV-DELTA-5 (Deterministic Progressive Context)**: System prompts and immutable invariants must form a prefix-stable anchor. Compaction must never truncate `settled_invariants` or `falsified_hypotheses`.

---

## 3. Data Contracts & Domain Schemas

### 3.1 Semantic Task State Vector (`domain/task_state.py`)

```python
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Sequence

class StepState(str, Enum):
    PENDING = "pending"
    READY = "ready"
    ACTIVE = "active"
    VERIFIED = "verified"
    FAILED = "failed"

@dataclass(frozen=True, slots=True)
class TaskStep:
    step_id: str                          # Monotonic ID: e.g. "step-001"
    title: str                            # Human-readable objective
    target_files: tuple[str, ...]         # Target files for this step
    dependencies: tuple[str, ...] = ()    # Pre-requisite step IDs
    state: StepState = StepState.PENDING
    falsification_evidence: str | None = None
    verification_digest: str | None = None

@dataclass(frozen=True, slots=True)
class SemanticTaskState:
    run_id: str
    revision: int                         # Monotonically increasing state version
    overarching_goal: str                 # Top-level immutable objective
    active_step_id: str | None            # Currently executing step
    backlog: tuple[TaskStep, ...]         # Ordered task DAG steps
    falsified_hypotheses: tuple[str, ...] # Negative memory: failed attempts not to repeat
    settled_invariants: tuple[str, ...]   # Verified architectural truths
    changed_files_tree_hash: str          # Current working tree SHA-256
```

---

## 4. Multi-File Two-Phase Commit (`2PC`) Transaction Protocol

### 4.1 Interface Specification (`adapters/environment/transaction.py`)

```python
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Sequence
from vanguard.packages.domain.results import Result

@dataclass(frozen=True, slots=True)
class FileMutation:
    path: str
    content: str
    action: Literal["create", "modify", "delete"]

@dataclass(frozen=True, slots=True)
class TransactionReceipt:
    transaction_id: str
    mutated_files: tuple[str, ...]
    tree_hash_before: str
    tree_hash_after: str

class AtomicMultiFileTransactionManager:
    """Two-Phase Commit transaction manager guaranteeing zero half-broken multi-file states."""
    
    def __init__(self, workspace_root: Path) -> None:
        self._root = workspace_root

    def execute_transaction(
        self,
        mutations: Sequence[FileMutation],
    ) -> Result[TransactionReceipt]:
        """Phase 1: Preflight in-memory shadow tree & AST check.
        Phase 2: Atomic commit to disk, or full rollback on any failure."""
        ...
```

### 4.2 Preflight Validation Rules:
1. Every modified or created `.py` file is validated via `ast.parse(source, filename=path)`. Syntax errors abort immediately.
2. Every imported symbol from local modules within the transaction set must resolve.
3. If any step fails, all original file contents are restored from in-memory pre-image snapshots.

---

## 5. Synthetic Test Oracle Bootstrapping Protocol

For greenfield tasks where no test suite exists in the baseline repository:
1. **Stage 1 (Contract Synthesis)**: Agent authors pure port interfaces / protocols under `vanguard/packages/ports/` or domain types.
2. **Stage 2 (Oracle Synthesis)**: Agent creates a synthetic test suite under `test/` defining terminal behavioral assertions.
3. **Stage 3 (Falsifier Confirmation)**: Agent runs the synthetic test against empty/stub implementations. **The test MUST fail** with expected `NotImplementedError` or assertion failure. If it passes on stubs, it is vacuous and rejected.
4. **Stage 4 (Freeze Oracle)**: The test file SHA-256 is registered in `TestTamperShield`.
5. **Stage 5 (Implementation)**: Agent implements code until the synthetic oracle passes.

---

## 6. Cryptographic Test Tamper Shield (`runtime/governance/tamper_shield.py`)

```python
from __future__ import annotations
import hashlib
from pathlib import Path

class TestTamperShield:
    """Guarantees agents cannot manufacture green passes by altering test files."""
    
    def __init__(self, workspace: Path, test_patterns: tuple[str, ...] = ("test/**", "tests/**", "*_test.py")):
        self._workspace = workspace
        self._patterns = test_patterns
        self._baseline_hashes: dict[str, str] = self._snapshot_hashes()

    def _snapshot_hashes(self) -> dict[str, str]:
        hashes: dict[str, str] = {}
        for pattern in self._patterns:
            for p in self._workspace.glob(pattern):
                if p.is_file() and p.suffix in (".py", ".ts", ".js"):
                    hashes[str(p.relative_to(self._workspace))] = hashlib.sha256(p.read_bytes()).hexdigest()
        return hashes

    def verify_integrity(self) -> tuple[bool, str]:
        """Fails closed if any test file was modified or removed."""
        for rel_path, expected_hash in self._baseline_hashes.items():
            f = self._workspace / rel_path
            if not f.exists():
                return False, f"Test file deleted: {rel_path}"
            if hashlib.sha256(f.read_bytes()).hexdigest() != expected_hash:
                return False, f"Test file tampered with: {rel_path}"
        return True, "Test integrity verified"
```

---

## 7. Progressive Context Compiler (`agency/context/progressive.py`)

Context is budgeted across 4 strict mathematical tiers:

```
Total Turn Budget (e.g., 16,000 tokens)
├── Tier 0: Invariant Anchor [Priority 100, Immutable] (~800 tokens)
│   ├── Overarching Task Goal + System Invariants
│   └── Current Active Step Specification
├── Tier 1: Negative Memory [Priority 90, Prefix-Stable] (~1,200 tokens)
│   └── Falsified Hypotheses List (Past failed patches and error signatures)
├── Tier 2: Active Working Slice [Priority 80, AST Sliced] (~4,000 tokens)
│   └── Exact AST slice of target function/class being edited (not full file)
└── Tier 3: Symbol Topology Stubs [Priority 70, Token-Bounded] (~6,000 tokens)
    └── Signatures and docstrings of directly referenced dependencies
```

---

## 8. Self-Healing Model Dialect Engine (`adapters/models/dialect.py`)

### 8.1 Typed Failure Taxonomy & Corrective Actions

| Failure Class | Root Cause Signature | Corrective Action |
|---|---|---|
| `TRANSPORT` | Socket reset, timeout, HTTP 5xx | `RETRY_TRANSPORT` with exponential backoff |
| `PROTOCOL` | Unparseable JSON, malformed schema | `DEGRADE_DIALECT` to markdown fenced JSON |
| `TRUNCATION` | Premature `finish_reason: length` | `CONTINUE_OUTPUT` requesting remainder |
| `TOOL_CALL` | Invalid tool name or missing args | `REPAIR_TOOL_CALL` feeding schema definition back |
| `PATCH` | Pre-image mismatch, hunk reject | `RELOCATE_AND_RECOMPILE` re-reading target file slice |
| `VERIFICATION` | Test failed with non-zero exit | `RECORD_FALSIFICATION` adding hypothesis to Tier 1 |
| `PERMISSION` | Capability or budget denial | `ESCALATE_APPROVAL` requiring human signature |

---

## 9. CLI Arguments & Invocation Surface

```text
vg code [OPTIONS]

Options:
  --plan PATH              Path to existing task plan DAG JSON.
  --brief PATH             Task description Markdown file (default: TASK.md).
  --preset [fast|balanced|max]
                           Execution profile preset (default: balanced).
  --budget-micros INT      Maximum cost ceiling in USD microdollars.
  --dry-run                Validate preflight syntax and AST without disk mutation.
  --tamper-shield          Enforce strict read-only test suite hash verification (default: true).
  --json                   Stream newline-delimited JSON events to stdout.
```

### Exit Codes
- `0`: Completed successfully; all task steps verified and admission gate passed.
- `1`: Verification failed; reproducer or test assertions failed.
- `2`: Invalid arguments, schema violation, or unparseable task brief.
- `3`: Unavailable; budget exhausted or provider connection refused.
- `127`: Missing system dependencies (e.g., neither `patch` nor `git` available).
