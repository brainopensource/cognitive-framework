---
id: execution.active
canonical_id: execution.active
class: execution
authority: execution
truth_plane: TARGET
status: living
implementation_status: BACKEND_FINISH_ACTIVE
owner: repository-governance
canonical_for:
  - current work/state/ownership
purpose: Represent the current authorized backend finish sequence and its exact evidence gaps.
audience:
  - contributor
  - release-owner
analysis_subject_sha: ea152f92fe9c9711035dfc7ff77b0c213380fe1f
version: 0.9.2a3
last_verified: 2026-09-02
normative_authority:
  - docs/SPEC.md
  - docs/decisions.md
relationships:
  - execution.milestones
  - execution.backlog
  - decision.index
reviewer: repository-governance
confidence: high
---

# Current Execution Intent

## Authoritative disposition

This file is the sole current execution board. It supersedes older status prose in
the README, drafts, review reports, generated indexes, benchmark filenames, and
historical evidence bundles. Those artifacts may supply evidence, but they do not
authorize work or close a gate.

The backend is in a **finish and convergence phase**, not a greenfield architecture
phase. The general substrate already provides one mediated runtime, event-sourced
state, bounded turns and budgets, model adapters, repository-index and context
seams, completion admission, recursive delegation, application services, and
exterior evaluation. The remaining work is to connect those mechanisms on one
production Coding Max path, prove long-session continuation and task-appropriate
completion, repair the empirical runner, and qualify the exact subject.

M-8 remains blocked. M-9 and M-10 remain unauthorized. No local challenge,
cassette, green suite, or self-authored oracle is an official SWE-bench or SOTA
result.

## Navigation and evidence health

The source subject audited for this board is
`ea152f92fe9c9711035dfc7ff77b0c213380fe1f`.

- `.generated/knowledge/report.json` is `VALIDATED` with non-zero document,
  symbol, link, and code-mapping counts. The supported generator was rerun after
  this board changed; generated projections still do not authorize status.
- `dev_context_logs/context_summary.md` records subject `7d46c7f...` and is stale
  for current-status claims.
- After the locked development dependencies were installed, `lda doctor --json`
  and `lda check --json` reported `index_healthy: true`, non-zero entities, and
  current `HEAD` `ea152f92fe9c...`. A prescribed full rebuild reduced sampled
  stale symbol paths from 300 to zero. The tool still reports 5,207 orphan FTS
  rows, 29 sampled low-signal paths, documentation-drift warnings, and duplicate
  document candidates after that rebuild; these are navigation-tool hygiene debt
  and cannot override resolved canonical files or source.
- The investigation used both healthy LDA bounded context and the deterministic
  verification path: `docs_rag_v0.py`, reverse file routing, generated symbols
  only after path resolution, targeted `rg`, canonical owners, current source,
  tests, Git history, and durable benchmark artifacts.

`W-092-F0` has restored the minimum HEAD-bound navigation prerequisite, but must
also close the residual hygiene findings and the runtime/canary evidence defects
below before any later exact-subject qualification is accepted.

## Current board and WIP

Each lane has WIP=1. A package may advance only when its exit predicate is
demonstrated on the current subject.

| Lane | Active package | State | Current objective |
|---|---|---|---|
| A — runtime/product | `CMX-09` / `W-092-F1` | `IN_PROGRESS` | Converge all useful Coding Max/Forge/Chimera behavior onto one `ApplicationService -> Runtime -> HarnessSession -> EpisodeEngine` product path |
| B — evidence/evaluation | `REL-01R` / `W-092-F0` | `IN_PROGRESS` | Repair navigation and benchmark subject integrity before another live qualification run |

Everything else is queued, blocked, or experimental. In particular, `TLS-03`,
`TLS-04`, speculative checkpoints, mutation, SBFL, branch search, swarm execution,
and skill promotion are not active WIP.

## Current-source audit findings

### What is real and reusable

- `HarnessSession` owns the canonical mediated run path, one kernel, one ledger,
  approval re-entry, trajectory capture, and exterior evaluation.
- `EpisodeEngine` preserves prior turns and seen verbs across approval re-entry;
  repeated-action detection no longer includes the ever-growing episode digest.
- `PromptAssembler` and `ContextCompiler` provide deterministic L1-L5 assembly,
  stable prefixes, bounded compaction, prompt/model-output capture, and provenance.
- `AdmissionGate`, pack completion middleware, `CodingTaskState`, `ContextPacket`,
  `IndexPort`, `FileRepoIndex`, and the thin `CodingMaxFacade` exist with focused
  tests.
- OpenRouter message conversion accepts assembled conversations, retains tool
  descriptions, and maps the explicit `agency.finish` tool.
- Local challenge artifacts demonstrate that the canonical application service
  can produce externally oracle-passing multi-file patches on small controlled
  workspaces. They are useful development evidence, not release qualification.

### P0 integration defects

1. **Production preset divergence.** The public Coding Max facade selects
   `vg-code-fast`, `vg-code-balanced`, and `vg-code-max`, while later successful
   development artifacts use `vg-code-max-v3luna`, `vg-code-chimera`, and
   `vg-1-forge-v2`. The public presets currently share effectively the same base
   manifest. Later behavior has not been reconciled into the public catalog.
2. **Parallel engines are not production proof.** `ForgeEngine` and
   `ChimeraEngine` implement their own turn/context/tool loops. The hard-challenge
   reports named for Forge/Chimera actually invoke their manifests through
   `ApplicationService`; they do not prove the separate engines are integrated.
   A second production runtime would violate the locked thin-app/thick-composition
   boundary.
3. **Completion binding was inconsistent.** The runtime now uses
   `admission_required()` at the engine seam and the application policy is bound
   from declared `patch.apply` capability rather than preset names. Remaining
   work is to remove compatibility-only name-set assertions and prove arbitrary
   new manifests through a contract test.
4. **Verification count was fabricated at the runtime boundary.** The runtime
   now parses stable unittest/pytest summaries and returns zero when output is
   unknown, so a zero-test or unparsable result fails closed. Remaining work is
   typed framework/result evidence and broader task-kind policies.
5. **Long-session resume was only a one-turn continuation.** Resume now records
   and restores the original `maxTurns` and interactive approval mode rather than
   deriving a new ceiling from proposal count. Remaining work is exact model,
   profile, policy, phase, budget and 40+ turn cold-restart parity.
6. **Semantic task state is under-produced.** `CodingTaskState` can fold rich
   plan, discovery, dead-end, TODO, change-surface, verification, next-action,
   and budget fields, but current production code has no general event producer
   for most of those fields. The type and unit tests do not by themselves prove
   meaningful cold continuation.
7. **Repository context was not progressive.** The public Coding Max manifests
   now declare the file index and `HarnessSession` constructs a bounded,
   omission-bearing `ContextPacket` instead of an unbounded flat prefix. Remaining
   work is staged retrieval by task/change epoch, dependency/test ranking and
   post-edit refresh.
8. **The product presets did not request the index.** Fast/balanced/max now bind
   the shared repository-index component. Successful historical hard runs remain
   non-integrated evidence because they predate this change and must be rerun.
9. **The LDA A/B evidence is not an LDA adapter ablation.** Its treatment adds an
   LDA hint and a hand-authored `lda_index.py` helper to the task workspace. The
   hard runner named `run_3_hard_lda.py` does not call LDA. These artifacts must
   not support a repository-intelligence lift claim.
10. **M-8 live execution is structurally improved but cannot yet prove lift.**
    `RuntimeTaskExecutor` now uses the canonical `vg-code-max` application path,
    a bounded multi-turn attempt, interactive execution mode, durable state, and
    patch-artifact extraction. The frozen canary still maps several workload
    titles to unrelated or repeated workspaces, and the live path still requires
    successor-subject repair and exterior-verdict qualification.

### Evidence interpretation

The retained three-hard-task reports show `3/3` exterior-oracle passes for both
`vg-code-max-v3luna` and the `vg-1-forge-v2` manifest on self-authored fixtures.
They demonstrate promising model-plus-harness behavior. They do **not** close
`CMX-07`, M-8, M-9, or any SOTA claim because their rows lack an exact repository
subject and full immutable event/trajectory bundle; the Forge-labelled run does
not execute `ForgeEngine`; and the runtime admission/policy gaps above remain.

The independent v0.9.1 report is retained as historical evidence for its exact
subject. Its recorded LDA head and current code subject differ, so it is not a
current acceptance receipt.

## Delivered implementation slice

The current worktree contains the first convergence slice: capability-derived
runtime admission, capability-derived code-pack policy binding, durable
`maxTurns`/interactive resume metadata, conservative verification-count parsing,
bounded production `ContextPacket` construction, repository-index declarations
for all public Coding Max presets, cold-index MCP compatibility output, durable
patch/verification artifact capture, and a canonical multi-turn M-8 executor.
Unattended privileged benchmark effects still require an injected approval
authority from the benchmark caller.
These changes are covered by focused runtime, application, context, falsifier and
M-8 tests. They do not by themselves close the remaining exact-subject,
task-state, progressive-refresh, 40+ turn, or empirical-lift predicates.

## Authorized backend finish sequence

The sequence is dependency-ordered. Later packages may prepare fixtures or test
doubles, but may not claim completion before their prerequisites close.

### Sprint F0 — exact-subject truth (`REL-01R`, Lane B, active)

Deliverables:

1. Make `lda doctor --json` work in the supported development environment and
   bind the index to current `HEAD`; refresh Tier-1 context and generated
   knowledge through supported generators, never manual edits.
2. Repair `RuntimeTaskExecutor` so an empirical attempt uses the selected
   write-capable, admission-gated composition; distinguishes one agent attempt
   from its bounded multi-turn episode; obtains a patch from a durable runtime
   artifact; retains trajectory/event identity; and uses an exterior evaluator.
3. Replace the current canary with a successor manifest whose task title,
   payload, workspace preimage, oracle, split, base revision, and content digest
   identify the same subject. Preserve the old frozen artifact; never rewrite a
   previously executed subject.
4. Add negative falsifiers for no patch, no trajectory, subject mismatch,
   duplicate/contaminated tasks, zero tests, unavailable evaluator, budget
   exhaustion, timeout, and a second agent attempt.

Exit predicate: hermetic preflight plus fake/cassette integration proves the
complete runtime-to-patch-to-exterior-verdict chain, and every material identity
in the bundle resolves on the audited subject. Live provider execution remains
`NOT_RUN` at this sprint exit.

### Sprint F1 — one canonical Coding Max (`CMX-09`, Lane A, active)

Deliverables:

1. Select one production preset lineage and fold accepted v3luna/Forge/Chimera
   prompt, tool, patch, recovery, and context improvements into data-selected
   `fast`, `balanced`, and `max` compositions.
2. Keep `CodingMaxFacade` thin and route all run/status/resume/evidence/cost
   operations through `ApplicationService` and the canonical runtime.
3. Use `admission_required(harness)` as the single generic decision for every
   write-capable composition. Bind `ICompletionPolicy` by declared component or
   capability, not a second preset-name allowlist.
4. Remove the separate Forge/Chimera engines from the supported product path.
   Retain them only as experimental/reference code until useful mechanisms are
   ported and parity tests prove the canonical runtime owns all effects,
   persistence, approval, budgets, and evidence.
5. Make every manifest tool name/verb/selector and environment allowlist resolve
   from one compiled contract. Decorative capability strings are stop-ship.

Exit predicate: CLI/API/preset contract tests show all three presets invoke one
runtime and one completion path; a new write-capable manifest cannot complete
without fresh applicable evidence; no app or experimental engine performs a
direct effect or provider call.

### Sprint F2 — truthful completion (`CMX-10A`, Lane A, queued)

Deliverables:

- Produce typed verification receipts from the mediated command result: command,
  exit code, framework, collected/executed/failed/skipped counts when observable,
  output/result digest, task digest, and current postimage digest.
- Fail closed on zero collection, unparsable required evidence, stale receipts,
  partial patches, modified-but-uninspected files, incomplete multi-file change
  surfaces, and post-verification edits.
- Define explicit completion policy for bugfix, feature/refactor/migration,
  greenfield, repository-without-tests, and read-only/explain tasks.
- Make completion rejection model-visible and bounded; repeated finish rejection
  with unchanged evidence becomes typed no-progress, not an infinite loop.

Exit predicate: end-to-end falsifiers reach the actual runtime boundary for each
failure above; no synthetic test count or boolean-only verification can admit a
write-capable completion.

### Sprint F3 — durable long sessions (`CMX-10B`, Lane A, queued)

Deliverables:

- Persist identity-bearing events/artifacts for plan and TODO state,
  discoveries, hypotheses, dead ends, implicated/change-surface files,
  verification plan/result, route decisions, settled effects, next action, and
  remaining additive/structural budgets.
- Restore the original task, composition, profile, model-route policy,
  completion policy, approval semantics, total turn ceiling, spent/remaining
  budget, phase, and task-state digest after a fresh-process restart.
- Reconcile in-flight effects before model re-entry and never replay a settled
  patch, command, child, or evaluator call.
- Add checkpoint/compaction triggers based on context pressure and durable work
  boundaries. Checkpoints accelerate replay but never replace the ledger.
- Prove at least three cold restarts during one 40+ turn scripted task, including
  interruption after patch approval and after verification.

Exit predicate: the resumed run performs the same next admissible action and
produces the same final postimage/evidence as an uninterrupted control, within
declared nondeterminism and without duplicated settled effects.

### Sprint F4 — repository-scale context and change closure (`CMX-11`, Lane A, queued)

Deliverables:

1. Call `IndexPort.repo_map()` and build a real `ContextPacket` with task,
   repository/index snapshot, provider/version, query, selected files/symbols,
   dependencies, related tests, token estimate, omissions, and packet digest.
2. Keep the initial prefix small. Use progressive, epoch-safe retrieval:
   orientation -> implicated symbols/files -> callers/dependencies/tests ->
   changed-surface refresh -> verification context.
3. Reserve context for at least one edit/verification/recovery cycle. Compaction
   must retain goal, constraints, plan, modified files, latest failure and
   verification, next action, settled effects, and remaining budgets.
4. Fall back deterministically to source search when an index is absent, stale,
   empty, unhealthy, or points at unresolved paths. LDA remains an optional
   provider behind the generic port; Vanguard never requires it.
5. Drive affected-test and interface-closure checks from observed dependency and
   test associations, with explicit incompleteness when language coverage is
   insufficient.

Exit predicate: controlled large-repository tests prove bounded prompts, no
lost-in-the-middle regression, deterministic fallback, snapshot refresh after
edits, and multi-file/interface closure. A treatment must improve success or
cost-adjusted success on held-out tasks before becoming the default.

### Sprint F5 — product qualification (`CMX-07`, Lane B, blocked on F0–F4)

Run an immutable, preregistered set covering:

- single-file bugfix with a failing baseline reproducer;
- multi-file behavioral bugfix;
- cross-package public-interface feature;
- API/schema migration with backward-compatibility assertions;
- Python and non-Python greenfield projects with multiple files;
- repository-scale task with distractors and bounded context;
- interrupted/resumed long task;
- read-only explanation/review task with source-grounded evidence;
- adversarial noisy output, malformed tools, zero tests, stale verification,
  path escape, budget exhaustion, and provider interruption.

Each row binds exact source, task, preimage/postimage, composition, model/provider,
context policy and packet, event/trajectory, patch, verification, exterior
verdict, terminal, missingness, turns, tool calls, retries, tokens, cost, latency,
and resume parity. Report per-class results and confidence intervals; do not hide
invalid or unavailable rows.

Exit predicate: all stop-ship integrity predicates pass and the preregistered
product thresholds are met. A negative result is recorded honestly and returns
the failing mechanism to the appropriate sprint; thresholds are not retuned
after observation.

### Sprint F6 — optional specialists (`CMX-06`, Lane B, blocked on F5)

Compare the accepted single-worker control with one treatment at a time:
localizer, test investigator, reviewer, or bounded planner. Children must use
mediated `agent.spawn`, attenuated budgets/capabilities, artifact-digest handoff,
and the same verifier. Enable a role only when preregistered held-out evidence
improves success or cost-adjusted success without exceeding the reliability
regression budget.

### Sprint F7 — M-8 and release disposition (`FIN-A1` / `W-092-5`)

After F0–F5, execute the separate governed-memory control/treatment required by
M-8. Coding Max qualification does not substitute for memory lift. A valid
positive, negative, or undeterminable independent disposition closes the
experiment; only an accepted positive result satisfying the M-8 predicate can
authorize M-9.

## Product acceptance matrix

| Task class | Required operational completion evidence |
|---|---|
| Bugfix | Baseline reproducer fails when feasible; implicated source is inspected; patch applies; reproducer and affected regression checks pass on current postimage |
| Multi-file feature/refactor | Public interfaces, callers, serialization/configuration and tests are in the declared change surface; targeted and affected checks pass |
| Migration | Forward behavior, backward compatibility or explicit break contract, data/schema transition, rollback/recovery, and consumer checks pass |
| Greenfield | Empty/scaffold baseline is recorded; requested files are created; build/type/syntax checks and at least one behavioral smoke/contract test pass |
| Repository without tests | Pack declares or creates the smallest executable acceptance harness; syntax-only success is insufficient for behavioral work |
| Explain/review/read-only | No fabricated patch is required; every material conclusion cites resolved source/symbol/test evidence and satisfies an explicit requirements checklist |
| Long session | State survives compaction and fresh-process restart; no settled effect is duplicated; final evidence is bound to the resumed postimage |

## Stop-ship conditions

- Any second production turn engine, runtime, ledger, tool broker, evaluator, or
  authority path.
- Direct provider HTTP or host subprocess execution in app/pack/product logic.
- Completion admitted from model prose, a preset-name omission, a fabricated test
  count, zero tests, stale verification, or a mismatched postimage.
- Resume that changes the task/composition identity, silently resets budgets or
  approval semantics, grants fresh turns, or duplicates settled effects.
- A repository map that consumes the entire usable prompt, lacks snapshot
  identity/omissions, or overrides current source and tests.
- Benchmark rows without baseline validity, immutable trajectory/event linkage,
  patch identity, exterior verdict, exact cost/token/latency/turn values or typed
  missingness.
- Calling a local, synthetic, self-authored, or unofficial run SWE-bench, SOTA,
  or release evidence.
- Enabling specialists, swarms, SBFL, mutation, speculative rollback, skill
  promotion, or self-modification without a preregistered held-out benefit.

## Required validation before package closure

During implementation run focused falsifiers and `just check`. Before any sprint,
task, PR, milestone, or release-completion claim run `just verify` on the exact
subject. A package handoff records commands actually executed, pass/fail/skip
counts, known environment limitations, subject digest, generated evidence
digests, and unresolved missingness.

The 2026-09-02 audit installed the locked development environment and reran the
relevant suites. Agency tests passed `179/179`. Contract tests ran 440 tests and
ended with one failure, two errors, and five skips: the cold-index MCP fallback
returned catalog routing without the required `bounded_context`, and two UDS
subprocess lifecycle cases timed out before binding. The earlier focused
episode/context/state/Forge/M-8 selection passed 83 tests once dependencies were
available. The M-8 dry-run completed and truthfully emitted only `NOT_RUN`
empirical records.

`just check` and `just verify` were both executed. Lock validation, frozen
dependency sync, boundaries (`754` files), TCB (`1386/1438` logical lines),
domain-blindness, and isolation passed. Both recipes stopped at
`check_path_hygiene.py`, which found machine-local paths and usernames in retained
BAAC, ladder, and hard-run artifacts that predate this documentation change.
Documentation metadata, links, stale-path checks, Markdown lint, knowledge-base
generation, event coverage, execution-truth checks, RF-ID validation, secret
scanning, and the 97-test kernel suite passed when run directly. TypeScript
typecheck passed; the JavaScript workspace test command reached client-core with
six passing and one failing Wave-5 test in the pre-existing frontend worktree.
The strict MkDocs build also remains red on two pre-existing unresolved `R13`
cross-references in non-canonical Chimera review documents. Therefore no
full-repository green or milestone-completion claim is made.

Post-change focused validation passed: resume, bounded repository context,
Coding Max facade, M-8 runner, M-8 turn-loop, wave falsifiers and cold-index MCP
fallback. Boundary validation passed for 762 source files and TCB remained at
1386/1438 logical lines. LAM synthetic smoke passed 5/5 with zero network cost.
Two isolated DeepSeek V4 Flash smokes were within the requested budget (2 turns /
6,298 tokens / approximately $0.000556, then 1 turn / 3,029 tokens /
approximately $0.000435); both correctly stopped at their explicit turn ceilings
and are not quality or benchmark claims.

## Locked decisions

- Thin apps, thick declarative composition; one canonical runtime and ledger.
- Coding policy remains outside the domain-blind kernel.
- Effects, tests, child agents, and evaluation remain mediated by ports and
  capability/budget policy.
- Context/index providers are optional observations, never authority.
- Local completion admission and exterior evaluation remain separate.
- Sequential single-worker execution is the default until an ablation accepts a
  specialist treatment.
- M-8, M-9, M-10, 1.0, and official benchmark claims remain exact-evidence gated.

Numeric prompt/turn/token/USD ceilings, ranking weights, model routes, specialist
triggers, and concurrency remain measured variables. Conservative defaults may
be implemented, but they become release defaults only through preregistered
evidence with a rollback path.
