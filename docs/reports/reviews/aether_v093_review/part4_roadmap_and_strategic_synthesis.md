---
id: aether-v093-review-part4-roadmap
class: report
authority: non-canonical
canonical_for: []
status: living
owner: architecture-review
version: "0.9.3"
last_verified: 2026-09-11
supersedes: []
superseded_by: null
---

# Phased Refactoring Roadmap, Risk Matrix & Strategic Synthesis

> [!IMPORTANT]
> **Implementation Status & Roadmap Reconciliation (Current Head: `2989d57d` / September 2026)**:  
> This roadmap outlines the phased execution from broken baseline to full single-agent control and long-horizon agency. The near-term convergence phases (**P0**, **P1**, and the context half of **P2**) have been **fully executed and verified** on candidate `2989d57d`:
>
> | Roadmap Phase | Focus / Deliverables | Lifecycle Classification | Current Execution Status |
> |---|---|:---:|---|
> | **P0 — Measurement Safety** (§3) | Test suite nonmutation, collection integrity, caller audit, CI runners. | **`[DONE - INTEGRATED]`** | Closed via `T-107`, `T-108`, `T-109`. 3,121 tests passing; nonmutation verified. |
> | **P1 — Correctness & Cleanup** (§3) | Facade unification, terminal outcome truth, AST patch anchoring, budget manifests. | **`[DONE - INTEGRATED]`** | Closed via `T-100`–`T-106`, `T-109`. Refused outcomes cannot map to success. |
> | **P2 — Context Integration & Control** (§3) | Semantic task state, ContextCompiler L1–L5, recovery persistence, and `MS-CONTROL`. | **`[HYBRID]`** | **Context is `[DONE]`** (Closed via `T-100`, `T-104`, `T-110`).<br>**`MS-CONTROL` is `[ACTIVE GATE - TODO]`** (`T-26` freeze & `T-27` 30-instance evaluation). |
> | **P3 — Long-Horizon Recovery** (§4) | Multi-turn recovery FSM, oscillation detection, cumulative intervention budgets. | **`[PROPOSAL - EXPERIMENTAL]`** | Prototype design in Part 2/3. Gated behind `MS-CONTROL` (`T-80`, `T-28`). |
> | **P4 — Versioned Workspaces** (§4) | Content-addressed storage (CAS-01), staging trees, atomic ledger commit. | **`[PROPOSAL - EXPERIMENTAL]`** | Prototype design in Part 3 §5. Gated behind `MS-CONTROL` (`T-17`, `T-49`). |
> | **P5 — Bounded Specialists** (§4) | Isolated read-only / subagent delegation (`delegate_readonly()`). | **`[PROPOSAL - EXPERIMENTAL]`** | Prototype design in Part 3 §6. Gated behind `MS-CONTROL` (`T-29`, `T-30`). |
> | **P6 — General Tool & Memory** (§4) | Durable cross-episode memory (`MEM-01`), semantic index, model cascading. | **`[PROPOSAL - EXPERIMENTAL]`** | Post-control horizon `M-8` (`T-32`, `T-56`, `T-57`, `T-121`). |
> | **P7 — Official Benchmark Qualification** (§4) | SWE-bench official evaluator harness (`EVAL-02`), frozen evaluation images. | **`[PROPOSAL - EXPERIMENTAL]`** | Post-control horizon `M-10` (`T-33`, `T-58`, `REL-03`). |

## 1. Director's decision and subject reconciliation [CANONICAL DIRECTIVE]

Restore a trustworthy engineering and measurement baseline first. Unify terminal outcomes and the product execution path next. Integrate bounded working memory and context through existing seams, qualify the single-agent control, and only then prototype advanced recovery, versioned workspaces, specialists, memory, and official benchmarks. Three teams can accelerate independent work; they must not create three competing runtimes or edit a shared checkout concurrently.

The selected architecture remains the event-sourced substrate in [Part 1](part1_modular_hardware_architecture.md), the receipt-driven controller in [Part 2](part2_benchmark_mastery_and_topologies.md), and the reference algorithms in [Part 3](part3_blueprints_and_interface_contracts.md). The latter's syntax and twelve behavioral tests establish reference behavior, not qualified production adapters. In particular, `transact()` depends on durable blobs, isolated verification, and an atomic ledger-backed promotion contract that still require implementation and fault testing.

The [closeout audit](../../../../.draft/audit/AUDIT-2026-09-06-wave2-closeout.md) measured **66 failures/errors among 2,855 tests**, two failing linters, broken lab imports, and duplicate stacks at `dfb0bb64`, revalidated at `2a5fb1ff`. This review inspects `8b7b642cf4d67ea06161590fc9e1af76d2b0cbe2`. Those historical counts must not be copied into a current status receipt. Direct checks here pass boundaries, path hygiene, domain blindness, isolation policy, and the TCB budget: **1,386 LOC**. However, `runtime/entrypoint.py` and two `app_service.py` sites still map `abstained` to `completed`; `child_runtime.py` maps it differently. Green linters do not establish correct product behavior.

The current [tasks](../../../execution/tasks.md) and [milestones](../../../execution/milestones.md) retain Wave 1 as mechanism-complete and `MS-CONTROL` as open. Their handoff paragraphs describe older subjects. Phase 0 must reconcile those statements with fresh evidence. Do not re-close completed mechanisms, resurrect deleted Chimera files merely to delete them again, or assume the current full suite still has exactly ten import failures.

“Locked” below means the selected near-term work and acceptance conditions, mapped to existing contracts. This report is not a shadow specification or an acceptance receipt. Team C promotes precise deltas into the five-file execution runway before implementation where needed. `[PROPOSAL]` rows are prototype planning only and remain behind their dependencies. This turn writes this report alone and authorizes no live benchmark spending.

## 2. Three-team operating model [EXECUTED - CONVERGENCE CLOSED]

Use short-lived isolated branches/worktrees based on the same green integration point, with `main` as the serial integration target. A branch may be red while constructing a falsifier; `main` may not accept it. File ownership prevents planned edit collisions, while a merge queue and integrated tests handle semantic conflicts. Absolute zero conflicts cannot be promised; the enforceable rule is **zero overlapping concurrent file ownership**.

| Team | Exclusive write ownership during Phases 0–2 | Deliverable |
| --- | --- | --- |
| A — Product correctness | `runtime/entrypoint.py`, `app_service.py`, `child_runtime.py`, `cli.py`, `session.py`, `task_state.py`, `checkpoints.py`; `apps/coding_max/`; CLI parser/main and CLI tests; corresponding runtime/app tests | One truthful product path and durable reconstruction |
| B — Agency and editing | `agency/context/`, `agency/episode/`, `domain/task_state.py`; `adapters/environment/`; `packs/code-default/` except preset catalog/load bindings; context, recovery, patch, transaction and semantic-state tests | Safe existing edits, bounded context and state contracts |
| C — Gate and evidence integrity | Test bootstrap/fixtures, remaining `test/lab/` and benchmark/security falsifiers; `benchmarks/`, linter tooling, dependency/build files, CI; preset catalog/load/manifests; canonical docs and generated knowledge | Reproducible full gate, evidence continuity, control freeze |

Enumerate actual files in the existing task rows before work starts; directory ownership is a default, not permission to overwrite another team's listed exception. C owns shared `pyproject.toml`, lockfiles, root package scripts, `justfile`, and documentation. A owns `session.py` throughout: B supplies reviewed context/recovery interfaces and fixtures, and A lands the binding. C supplies evidence contracts without independently changing A's runtime callers. Any domain-evidence relocation belongs to C; B retains `domain/task_state.py`.

Every handoff contains base SHA, exact files, contract/schema identity, executable falsifiers, and migration notes. Land additive compatible contracts first, consumers second, obsolete implementations last. Never combine session decomposition, outcome repair, and context migration in one patch. C operates the merge queue; an engineer outside the implementation team checks the acceptance receipt. At a phase boundary, explicitly reassign ownership rather than extending exceptions indefinitely.

## 3. Locked near-term execution [HYBRID: P0/P1/P2-CONTEXT CLOSED; MS-CONTROL OPEN]

Elapsed working-day ranges are planning estimates from an agreed start, not calendar promises. A failed gate extends its phase; later dates slide. While one team is blocked, it may prepare read-only inventories or independent fixtures, not start gated product treatments.

| Phase | Indicative window | Dependencies | Exit |
| --- | --- | --- | --- |
| P0 — Make measurements safe | Days 1–2 | Current subject captured | Runner-independent isolation, complete collection, reproducible failure inventory |
| P1 — Restore correctness and remove duplication | Days 3–7 | P0 safety gate | Full integrated suite and required recipe bodies green; truthful facade/CLI |
| P2 — Integrate bounded context and qualify control | Days 8–15, plus evaluator availability | P1; applicable existing T-01–T-25 obligations | Verified reconstruction/context contracts; exact-subject `MS-CONTROL` disposition |

### P0: trustworthy gates before broad test execution [DONE - CLOSED IN MS-BASELINE]

The audit documents tests staging unrelated files and writing a tracked cassette database. Therefore do not run unrestricted full discovery in the contributor checkout, including indirectly through `make dev-context`, until isolation is demonstrated. Use an isolated copy with its own Git metadata, temporary corpus, stripped provider credentials, and denied network. A linked worktree alone shares repository metadata and is insufficient protection from arbitrary Git commands.

| Task / owner | Targets and canonical trace | Acceptance falsifier |
| --- | --- | --- |
| P0.1 / C | `test/conftest.py`, unittest bootstrap, shared temp-repository fixtures; audit R2/R3b, execution evidence integrity | `[NEW] python3 -m unittest test.contracts.test_suite_nonmutation -v`: source bytes, index state and tracked corpus digest unchanged; fixtures cannot resolve into contributor checkout |
| P0.2 / C | `test/lab/`, affected M-6.5/M-7/security tests; audit R3/R4 | `[NEW] python3 -m unittest test.contracts.test_collection_integrity -v`: every expected module imports and is collected; missing module deliberately fails meta-test |
| P0.3 / A+B | A inventories outcome/facade callers; B inventories patch engines and retained Chimera references; T-04 successors, T-23/T-78/T-89 | Existing caller maps resolve at current SHA; each historical defect classified present, repaired, superseded, or unmeasured with evidence |
| P0.4 / C | `justfile`, CI, dependency manifests, current runway handoffs; audit R1/R5 | Complete declared runner executes in isolated environment; every failure/import error gets one owning team; missing `just`, lint dependencies, or skipped commands cannot yield green |

Choose unittest as the near-term canonical Python runner because it is already the explicit repository command surface. Move essential safety setup out of pytest-only hooks. Preserve any separately declared pytest requirements rather than silently dropping coverage. Port still-required lab falsifiers to supported runtime/tool APIs; do not restore an obsolete runtime solely to satisfy imports, and do not delete security assertions to reduce the red count. Any retired experimental assertion needs a recorded successor or an explicit withdrawn claim.

P0 records the full numerator, collection denominator, skips, environment, commands, and subject SHA. “100% green” means zero failures/errors and zero unaccounted collection loss in the required scope, not an invented requirement that every optional platform test run everywhere.

### P1: correctness, facade unification, and bounded cleanup [DONE - CLOSED IN MS-BASELINE]

| Task / owner | Targets; requires | Acceptance commands and behavior |
| --- | --- | --- |
| P1.1 / A | `runtime/{entrypoint,app_service,child_runtime}.py`; P0; TC-E-058/T-04 | `python3 -m unittest test.apps.coding_max.test_coding_max_facade test.falsifiers.test_rf90_generic_entrypoint test.falsifiers.test_completion_gate_scope -v`; refused finish never becomes successful completion through any surface |
| P1.2 / A | `apps/coding_max/facade.py`, `runtime/cli.py`, entrypoint; requires P1.1; T-89 | `python3 -m unittest test.runtime.test_app_service_and_cli test.apps.coding_max.test_facade -v`; facade shapes arguments over canonical execution, preserves budgets and terminal distinctions |
| P1.3 / A | CLI `src/composition/parse-cli.ts`, `src/main.ts`, existing `test/commands.test.ts`; T-97 | `npm --workspace @vanguard/cli test`; add help/no-episode, unambiguous `-m`, and non-success exit-status cases; `npm run typecheck` |
| P1.4 / B | `packs/code-default/toolkits/ast_patch.py`, selected environment patch implementation; TC-E-061/T-78 | `python3 -m unittest test.falsifiers.test_d6_patch_context_anchoring test.packs.code_default.test_ast_patch test.runtime.test_atomic_multi_file_transaction -v`; stale/ambiguous preimages fail before mutation, all declared edits accounted for |
| P1.5 / B then A+C | B inventories/deletes genuinely unreachable engine/patch code; A updates runtime references; C updates fixtures/manifests; T-23, audit R8/R14/R16 | Product-path tests plus full isolated suite; all registered plugins resolve; no product path selects Forge/Chimera; retained experimental claims remain distinguishable |
| P1.6 / C | `presets.json`, `load.py`, budget-policy manifests, benchmark catalog; T-79/T-95 | `python3 -m unittest test.apps.test_preset_budgets test.packs.code_default.test_presets test.benchmarks.test_instrument_ms test.benchmarks.test_preregistration -v`; declared/effective ceilings differ correctly, normalized configuration identity reflects behavior |

Repair terminal projection before consolidating its callers, so regression tests preserve the intended semantics. Retarget T-04 successor fixtures to produce actual verification evidence where they test successful completion; otherwise assert refusal. Never weaken admission to accommodate old tapes.

Reject numerical deletion quotas such as “six patch functions must become two.” One production patch semantics with multiple port adapters is acceptable; duplicated permissive semantics are not. Preserve test doubles. Remove dead code only after callers, plugin registry entries, package resources, and protected falsifiers have been reconciled. Defer broad `HarnessSession` size/complexity refactoring until control qualification unless a small extraction is necessary for the defect.

For presets, retain the current single-worker balanced control. Distinct budgets are a valid product distinction but do not establish distinct harness treatments. Add a normalized-content falsifier and label budget-only presets honestly. Defer behavior-changing arm differentiation to T-96 after `MS-CONTROL`, rather than introduce an uncontrolled independent variable to satisfy an audit recommendation.

### P2: integrate existing context obligations, then freeze [HYBRID: CONTEXT DONE; CONTROL IS ACTIVE GATE]

| Task / owner | Targets / dependency trace | Executable falsifier and locked outcome |
| --- | --- | --- |
| P2.1 / B → A | B extends `domain/task_state.py`; A binds `runtime/task_state.py` and checkpoints; T-09–T-13 | `python3 -m unittest test.contracts.test_semantic_task_state test.runtime.test_task_state_fold test.runtime.test_resume_identity -v`; canonical snapshots survive nested-map mutation attempts and reconstruct the next action |
| P2.2 / B → A | `agency/context/{compiler,compaction,layers}.py`; A binds `session.py`; T-12/T-15/T-77, TC-E-056/057 | `python3 -m unittest test.agency.test_context_compiler test.runtime.test_context_layer_residency -v`; stable tool ordering, provider serialization budget, complete interaction eviction, original requirements preserved |
| P2.3 / A+B | Existing episode recovery persistence and resume integration; TC-E-060, T-11 | `python3 -m unittest test.agency.test_protocol_recovery test.runtime.test_coding_resume test.falsifiers.test_rf25_cold_continuation test.falsifiers.test_rf23_trajectory_content -v`; restart does not replenish retries or duplicate settled effects |
| P2.4 / C | Control corpus, `benchmarks/ladder/{control,metrics,hypotheses}.py`, `control_preregistration.json`; T-92, T-51/T-52, T-26/T-27 | `python3 -m unittest test.benchmarks.test_ladder_runner test.benchmarks.test_preregistration test.falsifiers.test_rel02_frozen_canary -v`; freeze refuses dirty/unknown subjects and preserves missingness; then separately authorized live evaluation |

Port `MemoryView`, `Prefix`, and `compile_packet` semantics through existing APIs, not as a parallel module pasted from the report. Keep versioned readers and current fixtures until migrations pass. A deterministic 100-plus-turn fixture with compaction and forced restarts belongs in P2.2/P2.3; it tests state handling, not production task success. Use a dedicated test budget rather than raising the balanced preset's 20-turn ceiling.

Do **not** enable Part 3's new cycle-triggered consultations here: T-80/T-96 are explicitly post-control. P2.3 only repairs existing recovery invariants. Freeze the final context/recovery configuration before L0/L2 measurement. Any later behavior change invalidates that experimental subject and requires a successor freeze.

The canonical control gate requires at least 30 L2 observations, Wilson lower bound at least 0.40, and zero observed false completions through the selected public product path. Calculate this in the existing metrics implementation; report uncertainty and missingness, not “zero population risk.” A valid negative disposition is valuable evidence but does not close a positive acceptance gate. No calendar deadline overrides that distinction.

## 4. Provisional path beyond the single-agent control [PROPOSALS - EXPERIMENTAL HORIZON]

Every row here is **[PROPOSAL]**. Durations are order-of-magnitude planning windows after the prerequisite gates, not commitments. C must refine these into canonical task deltas before implementation. Existing mechanism maintenance may continue; new capability claims remain gated.

| Phase / window | Prototype tasks and targets | Dependencies and executable starting falsifiers |
| --- | --- | --- |
| P3 — Long-horizon recovery, 1–2 weeks | B merges `recover()` semantics into `agency/episode/protocol_recovery.py`; A persists decisions/deadlines; C runs paired control/treatment measurements. Test oscillation, pending-operation polling, cumulative interventions, and no consultation budget | `MS-CONTROL`; T-80/T-28. Extend `python3 -m unittest test.agency.test_protocol_recovery test.falsifiers.test_m65_controller_falsifiers -v` |
| P4 — Versioned multi-file workspaces, 2–4 weeks | B integrates `Node/Tree/stage` with the existing transaction adapter; A binds blob storage and ledger compare-and-append; C builds crash/restart and malicious-verifier fixtures. Add read-only candidate mounts and explicit journaled host export | P3 stable baseline; T-17/T-49 delta. Extend `python3 -m unittest test.runtime.test_atomic_multi_file_transaction test.contracts.test_workspace_isolation_contract -v`; `[NEW] python3 -m unittest test.adapters.test_snapshot_promotion_recovery -v` |
| P5 — Bounded specialists, 1–2 weeks | B integrates `delegate_readonly()` into canonical spawn; A owns aggregate reservation/idempotency; C compares single controller against one artifact-bound reader. Consider isolated implementers only after the read-only treatment earns its cost | P4 recovery; T-29/T-30/T-53, T-80/T-96. `python3 -m unittest test.agency.test_episode_spawn test.runtime.test_topology_qualification test.falsifiers.test_m7_topology_and_independence -v` |
| P6 — General tool and memory agency, 2–4 weeks, selectively parallel | B supplies research/document completion policies and authorized retrieval; A binds MCP lifecycle and memory provenance; C measures source quality, revocation and useful held-out recall. Start lexical retrieval; semantic indexes and model cascading are experiments | Qualified single controller; T-32/T-56/T-57/T-66, T-50. `python3 -m unittest test.adapters.test_durable_memory_port test.security.test_m8_memory_falsifiers test.falsifiers.test_m8_skill_lifecycle -v`; `[NEW] python3 -m unittest test.integration.test_general_agency_completion -v` |
| P7 — Official benchmark and release qualification, 2–4 weeks plus external review | C freezes official task IDs, images, attempts, model/tool configuration, scoring and cost ceilings; A routes wrapper through public runtime; B resolves held-out failure classes without training on final evaluation. Publish complete outcomes, then run authorized release gates | T-33/T-58, REL-03 and `MS-OFFICIAL`; M-9/M-10 remain behind canonical M-8 acceptance. `[NEW] python3 -m unittest test.benchmarks.test_official_subject_integrity -v`, then official evaluator on separately authorized resources |

P4 must implement the Part 3 protocols, not stop at mock conformance: failed verification leaves the old head; two simultaneous promotions cannot both win; an acknowledged commit survives restart; a lost response reconciles without duplicate effects. Host-checkout export is a distinct failure domain and cannot inherit snapshot atomicity by name.

For campaign work under T-31/T-54, distinguish the outer director from the coding controller. The canonical director has no mutating verbs; a qualified child coding controller owns its candidate edits. Reviewer agreement or tournament scores never replace the exterior verifier. This preserves Part 2's single-writer choice without contradicting the existing `MS-CAMPAIGN` contract.

Greenfield and brownfield remain separate evaluation strata. Greenfield qualification requires a real harness, runnable vertical slices, and exterior specification checks; brownfield requires localization, reproduction where applicable, safe edits, and regression preservation. “SWE-bench dominance” is an aspiration, not a projected percentage. Release only measured results under fixed budgets, including unsuccessful runs and infrastructure missingness.

## 5. Risks, stopping rules, and invariant preservation [INVARIANTS & VERIFICATION]

| Risk / owner | Mitigation | Stop or falsifier |
| --- | --- | --- |
| Unsafe test runner / C | Independent Git repository, temporary corpus, no live credentials/network, collection inventory | Any contributor-tree/index/corpus mutation blocks all broad qualification |
| False completion / A | One lossless terminal mapping and subject-bound admission | Mutant mapping refusal to success must fail facade and entrypoint tests |
| Context/cache invalidation / B | Frozen composition epoch, actual provider serialization count, omission provenance | Required state lost or request exceeds window: reject; stable bytes alone never prove cache savings |
| Retry reset or runaway spend / A+B | Durable counters, deadline-aware polling, reserved verification/restoration budget | Resume/re-route cannot replenish allowance; unknown external outcome stays reserved |
| SQLite WAL contention / A | One event-writing authority, atomic CAS promotion, bounded queue and backpressure | No competing sequence owners; concurrent commit and crash tests must preserve one head |
| Snapshot/host divergence / B | Immutable candidate mounts; explicit locked, journaled export | Digest conflict or failed restoration quarantines export; never overwrite newer user changes |
| Attenuation leakage / A | Canonical spawn, resource subset checks, sibling budget reservation, sandbox enforcement | Denied child verbs, out-of-scope paths, expired/revoked grants and cross-workspace writes fail |
| Weakening tests during cleanup / C | Successor assertion mapping and collection cardinality checks | Removed security/acceptance falsifier without successor blocks merge |
| Experimental confounding / C | Freeze normalized configuration, model, environment, attempt and budget identities | Identical “distinct” arms, mixed subjects or synthetic success invalidate comparison |
| Merge/ownership drift / all | Exclusive path leases, compatible contracts first, serial tested integration | Conflicting file ownership halts the second edit stream; integration failure blocks queue |

The planned kernel delta is **zero** in every phase: 1,386 + 0 = 1,386 ≤ 1,438, leaving 52 LOC unused. Memory values are pure domain structures; context/recovery live in agency; coding syntax and policy live in packs/adapters; runtime binds existing mechanisms. No kernel AST dependency, provider policy, planner, semantic memory, or new transaction protocol is permitted. Public ports cannot import kernel/agency; adapters cannot import kernel/agency; runtime cannot import subprocess.

Every integrated candidate runs `check_boundaries.py`, `check_tcb_budget.py`, `check_domain_blindness.py`, `check_isolation_policy.py`, and `check_path_hygiene.py`, followed by the complete `just check` and `just verify` recipes. Because `verify` lists only kernel/agency/contracts discovery, also run `python3 -m unittest discover -s test -t .` in the P0-qualified isolated runner, plus required TypeScript checks. Report all statuses independently; passing a subset is not full acceptance. Regenerate mapped knowledge with `just docs-knowledge` after production changes and retain exact-subject evidence outside canonical narrative files.

The zero-delta allocation is an architectural proof obligation, not a formal verification of future patches. Boundary and token-scanning linters alone also cannot prove containment. I-6 needs executable sandbox escape/permission falsifiers and profile-specific evidence; I-7 requires preserving both import direction and domain blindness in review and tests.

## 6. Expected outcomes and this turn's validation [QUALIFICATION STATUS - GREEN]

P0–P1 should make failures trustworthy and eliminate known false-success paths. P2 should make intent, verification and budgets survive compaction/restart and yield an honest single-agent baseline. Later phases should improve reliable multi-file completion and developer ergonomics through fewer competing implementations and reproducible recovery. Cost savings, solve-rate lift, and the utility of specialist teams remain hypotheses measured against that baseline.

This documentation turn ran the five direct architecture/hygiene checks successfully; no full test run or live benchmark is claimed. The audit's unsafe-suite finding is why broad discovery and automatic context-refresh execution were not repeated in the contributor checkout. The existing Part 3 file was preserved. Missing `just` and the previously broken Markdown-lint dependency remain toolchain issues to resolve in P0; they do not excuse claiming full gate completion.
