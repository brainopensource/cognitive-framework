---
id: draft.development-final-plan-b
class: planning
authority: non-canonical
truth_plane: PROPOSED
status: draft
owner: repository-governance
version: "1.0.0"
triad_role: ground-truth
triad_complements: [A, v2]
observed_head: "66aa7a3c0c31cb68a2c0387a1ddf237c80084253"
observed_branch: "main"
observed_worktree: dirty
lda_index_head: "66aa7a3c0c31"
lda_freshness_vs_head: FRESH
lock_head: "66aa7a3c0c31"
lock_date: 2026-09-03
created: 2026-09-03
last_verified: 2026-09-03
supersedes: []
superseded_by: null
historical_does_not_modify: ".draft/DEVELOPMENT_FINAL_PLAN.md"
historical_observed_head: "ebad36e675f0eab6c4635851a91423f5a6541290"
historical_lda_index_head: "7e08462c2cbb"
historical_lda_freshness_vs_head: STALE
navigation_mode: degraded-locator-plus-source
lock_navigation_mode: lda-fresh-plus-source
paid_usd_this_session: 0.00
---

> **Unused reference.** Day-to-day development authority is [`docs/execution/`](../docs/execution/): [`milestones.md`](../docs/execution/milestones.md), [`spec.md`](../docs/execution/spec.md), [`technical.md`](../docs/execution/technical.md), [`backlog.md`](../docs/execution/backlog.md), [`tasks.md`](../docs/execution/tasks.md). This draft remains forensic lock at HEAD `66aa7a3c`. Do not treat it as the work board.

# AETHER Plan B — Backend-First Development Program for Long-Horizon Software-Engineering Agents

> **Epistemic status.** This file is a non-authoritative draft. It proposes work; it authorizes nothing.
> Current source and executable tests outrank this file, outrank [`.draft/DEVELOPMENT_FINAL_PLAN.md`](DEVELOPMENT_FINAL_PLAN.md), and outrank every research treatise cited below.
> Canonical synchronization belongs in the ordinary execution workflow after a proposal is accepted.

## Locked triad roles (lock 2026-09-03)

This file is **Plan B (ground truth)** in a three-document lock. Shared lock preamble is duplicated so each document stands alone. This triad **does not authorize** implementation, kernel AST, a second `EpisodeEngine`, or default HYDRA.

```text
A  = Program law: reliability identity, wave order, competency profiles,
     formal model, per-class evidence, non-goals, D-01–D-10
B  = Ground truth: live inventory, proven gaps, lattice placement,
     tickets 01–35, operator one-pager (01–13 first)
v2 = Architecture catalog: 16 primitives (map, not new cores),
     context economics, 2PC/tamper/dialect mechanics, later phenotypes
     (director / HYDRA / mutation) as [PROPOSAL]
```

Build order (locked, from B, aligned with the SOTA suggestion):

```text
cannot-lie → can-resume → can-see → can-change-many-files
  → qualify one EpisodeEngine coding agent
  → then meta / specialists / campaign / skills-memory
```

**Lock identity.** `lock_head: 66aa7a3c0c31`, `lock_date: 2026-09-03`, `lda_freshness: FRESH` (index matches HEAD). Planning-session snapshot HEAD `ebad36e675f0eab6c4635851a91423f5a6541290` / LDA `7e08462c2cbb` `STALE` is retained in §2 and is **not** the lock subject.

**Dual mission** (from v2 §1.1 + SOTA suggestion). Vanguard/AETHER is simultaneously (1) a closed-loop coding harness (`Coding Max` / `EpisodeEngine` product path) and (2) a composable agent framework (hexagonal substrate, packs, ports). The CLI (`vg`) is an operator surface — a client of `ApplicationService` — not the brain. CLI must not patch, grade, or enlarge budget.

**Reliability identity** (same law as §1):

\[
R = \prod_{t} \Pr(\text{honest progress}_t \mid \text{honest state}_{t-1})
\]

**Complements.** Plan A = law/profiles/done-definitions. Plan v2 = architecture catalog and later phenotypes as `[PROPOSAL]`. Critical-path numbering remains tickets **01–35** in this file. YAML `does_not_modify` A is **retired**; this file complements A and v2 rather than promising not to mention them.

## Epistemic legend (applies to every later claim)

This legend is **shared law** for A, B, and v2. Do not delete this copy.

| Tag | Meaning | Promotion rule |
|---|---|---|
| **FACT** | Observed in current source, tests executed this session, or an official primary source fetched on 2026-09-03 | May be treated as current truth for planning |
| **MECHANISM** | Code exists and unit/contract tests exist | Not a product or benchmark claim |
| **INFERENCE** | Reasonable engineering conclusion from FACT + MECHANISM | Must not be restated as evidence |
| **PROPOSAL** | Recommended next work | Requires a later ticket, falsifier, and WIP slot |
| **ASPIRATION** | Desired competitive position | Forbidden as a forecast of a specific score |
| **CONTRADICTION** | Two authorities disagree; source wins | Record both sides; do not silently pick the nicer one |
| **SUPERSEDED** | Attractive draft idea that current lattice or source rejects | Keep the text in place, mark `[PROPOSAL]`, and cite the better location. Do not drop the paragraph. |

**Historical SUPERSEDED rule (pre-lock, 2026-09-03 planning session).** The original cell read: “Keep the insight, drop the proposed location or second runtime.” That “drop the text” reading is **rejected** by this lock. Insights stay in full; only the proposed location or second runtime may be marked `[PROPOSAL]` with a pointer to the lattice-correct write-up.

---

## Table of contents

0. [Locked triad roles](#locked-triad-roles-lock-2026-09-03)
1. [Executive decision](#1-executive-decision)
2. [Evidence boundary and snapshot](#2-evidence-boundary-and-snapshot)
3. [Current implementation inventory](#3-current-implementation-inventory)
4. [Proven gaps](#4-proven-gaps)
5. [Formal agent model](#5-formal-agent-model)
6. [Target backend architecture](#6-target-backend-architecture)
7. [Competency profiles](#7-competency-profiles)
8. [Development waves](#8-development-waves)
9. [Sprint sequence](#9-sprint-sequence)
10. [Greenfield workflow](#10-greenfield-workflow)
11. [Brownfield workflow](#11-brownfield-workflow)
12. [Research and explanation workflows](#12-research-and-explanation-workflows)
13. [Model routing](#13-model-routing)
14. [Multi-agent policy](#14-multi-agent-policy)
15. [Memory and skills](#15-memory-and-skills)
16. [Benchmark methodology](#16-benchmark-methodology)
17. [File-by-file routing](#17-file-by-file-routing)
18. [Initial engineering tickets](#18-initial-engineering-tickets)
19. [Risks](#19-risks)
20. [References](#20-references)
21. [Session validation appendix](#21-session-validation-appendix)
22. [Live tool/verb inventory](#22-live-toolverb-inventory-lock-head-66aa7a3c)
23. [Product target loop](#23-product-target-loop)
24. [Cross-link matrix](#appendix-e--cross-link-matrix-locked-triad)

---

## 1. Executive decision

**Recommended ordering.** Make one coding lineage truthful before adding more agents, more context, or more memory.

The program order is:

1. Restore benchmark and navigation identity so no later score can be laundered through a stale SHA, a `__pycache__` task, or a dry-run.
2. Close false-positive completion on the product path (`vg-code-default` exemption, Forge `test_count = 1`, regex test-count inference).
3. Promote semantic task state from a runtime fold dumped into frozen L3 into a domain value that the compiler, admission gate, and resume path all consume.
4. Bind repository intelligence to a workspace epoch so progressive context cannot silently serve a pre-write snapshot.
5. Prove greenfield scaffold-and-oracle and brownfield blast-radius closure on frozen internal tasks.
6. Qualify a **single-agent** Coding Max control with Wilson intervals and explicit missingness.
7. Add metacognition as a bounded, opt-in policy with paired ablations.
8. Add specialist topologies only as named treatments against that control.
9. Add a durable outer-loop campaign director only after inner-loop completion is fail-closed.
10. Promote memory and skills only through held-out lift, separated authorities, and executable rollback.
11. Enter official DeepSWE v1.1 / SWE-bench Pro / SWE-bench Verified programs as a **separate measurement lane**, never as the implementation definition of done.

**Central architectural thesis.** AETHER already has the right substrate: a domain-blind kernel, an event-sourced ledger, one public run path, and pack-owned coding semantics. The product is blocked not by missing swarm machinery but by **untruthful settlement**. An agent that can declare success without a bound verification receipt, resume into a stale prefix, or be scored on an invalid task set cannot become a senior engineer no matter how many specialist roles are bolted on.

The reliability law this plan obeys is:

\[
R_{\text{campaign}} = \prod_{t=1}^{T} \Pr(\text{honest progress}_t \mid \text{honest state}_{t-1})
\]

If any factor is an unmeasured heuristic (invented test counts, keyword task classification, frozen resume dumps, ungated `finish`), the product collapses with horizon \(T\). Multi-agent branching multiplies that product by a merge-error term. Therefore Plan B forbids default multi-agent behavior until a single lineage has a measured \(R\) on frozen tasks.

**What this plan is not.**

- It is not an authorization to start Waves 6–10.
- It is not a claim that AETHER currently scores 60–90 on DeepSWE or SWE-bench Pro. **FACT:** no official receipt exists for HEAD `ebad36e`.
- It is not a claim that Coding Max, Forge, and Chimera are one product. **FACT:** Forge and Chimera are parallel loops.
- It is not a frontend plan. CLI/TUI control is a later consumer of this backend.

**Score bands (ASPIRATION, not forecast).**

| Band | Internal meaning | External meaning | Premature if claimed today |
|---|---|---|---|
| Qualification | Frozen internal multi-class suite, exact-subject, Wilson lower bound \(\ge 0.40\) on \(n \ge 30\), zero synthetic success | Instrument-valid harness; not an official score | Yes |
| Credible competitive | Same protocol on official DeepSWE v1.1 public tasks, lower bound overlapping the mid-pack (currently roughly 50–63% on mini-swe-agent) | Comparable to `deepseek-v4-flash [max]` 53%±4% and `glm-5.3-flash [max]` 63%±4% on DeepSWE v1.1 as of 2026-09-02 | Yes |
| Frontier parity | Official DeepSWE v1.1 pass@1 whose CI overlaps the 2026-09-02 leaders (gemini-3.8-flash / claude-opus-5 at 74%) **and** Scale SWE-bench Pro public standardized scores in the current 55–62% band | Harness + model jointly competitive | Yes |
| Stretch | DeepSWE \(\ge 80\%\) or Scale Pro public \(\ge 70\%\) under the **same** official scaffold | Would require model generation plus harness; not a Plan B exit | Yes |
| Unsupported | “90/100”, “replaces staff engineers”, “beats all vendor scaffolds” | Professional replacement is not a benchmark outcome | Always |

The user-requested 60–90 band is therefore a **mixture**: 60 is a plausible later qualification/competitive threshold on DeepSWE-class tasks; 90 is a stretch that current public leaderboards do not support as a near-term AETHER claim. SWE-bench Verified is saturating near 95%+ under vendor scaffolds and is the wrong trophy. SWE-bench Pro standardized scores remain far lower than vendor-scaffold scores; mixing those numbers is a methodology error this plan forbids.

---

## 2. Evidence boundary and snapshot

### 2.1 Identity (FACT)

**Lock identity (2026-09-03, HEAD `66aa7a3c0c31`).** LDA index matches this HEAD (`FRESH`). This is the lock subject.

| Field | Value |
|---|---|
| Repository | `/home/rock-dev/Coding/cognitive-framework` |
| Branch | `main` |
| Lock HEAD | `66aa7a3c0c31cb68a2c0387a1ddf237c80084253` |
| LDA index HEAD | `66aa7a3c0c31` |
| LDA freshness vs HEAD | `FRESH` |
| Lock date | 2026-09-03 |
| Package version string | `0.9.0b1` in `pyproject.toml` (not M-9 acceptance) |
| Kernel TCB | **1386 / 1438** logical LOC (lock-time reconfirm not required for this draft-lock) |
| Domain-blindness | Invariant I-7 still law; kernel remains domain-blind |

**Planning-session snapshot (historical, HEAD `ebad36e`).** The following table is the original inspection identity from the 2026-09-03 planning session that produced this draft. It is **not** the lock subject. Kept in full:

| Field | Value |
|---|---|
| Repository | `/home/rock-dev/Coding/cognitive-framework` |
| Branch | `main` |
| HEAD | `ebad36e675f0eab6c4635851a91423f5a6541290` |
| Worktree | dirty (pre-existing user work; this task created only this file) |
| Date of inspection | 2026-09-03 |
| Package version string | `0.9.0b1` in `pyproject.toml` (not M-9 acceptance) |
| Kernel TCB | **1386 / 1438** logical LOC, `alarm_delta_lines=131` |
| Domain-blindness linter | PASS (no `coding\|pytest\|ast` tokens in `domain/` or `kernel/`) |

### 2.2 Navigation health (FACT, degraded mode)

**Lock-time FACT (HEAD `66aa7a3c0c31`, 2026-09-03).** `uv run lda identity --json` reports `index_head_sha=66aa7a3c0c31`, `freshness_vs_head=FRESH`, `dirty=true`. `uv run lda doctor --json` reports `index_healthy=true`, `status=HEALTHY`. [`docs/execution/active.md`](../docs/execution/active.md) is **absent**. Execution runway files present: [`docs/execution/tasks.md`](../docs/execution/tasks.md), [`docs/execution/spec.md`](../docs/execution/spec.md), [`docs/execution/milestones.md`](../docs/execution/milestones.md), [`docs/execution/backlog.md`](../docs/execution/backlog.md). W-092-F0 HEAD-bound LDA is satisfied for this lock worktree. `FEATURE_SPEC.md` remains a historical name in this draft; the current delta file is `spec.md`.

**Historical CONTRADICTION (ebad36e).** The following table and two CONTRADICTION paragraphs were true at planning-session HEAD `ebad36e` with LDA `STALE` vs index `7e08462c2cbb`. They are retained as the forensic snapshot. They are **not** current at lock HEAD `66aa7a3c`.

| Artifact | Recorded subject | Current HEAD | Usable as |
|---|---|---|---|
| `uv run lda identity --json` | `index_head_sha=7e08462c2cbb`, `freshness_vs_head=STALE`, `dirty=true`, `local_changes=58` | `ebad36e…` | Locator only |
| `uv run lda doctor --json` | `index_healthy=true`, `status=HEALTHY`, symbols=10671, relations=79040 | same HEAD string, stale graph | Health of the **old** index, not of HEAD |
| `.generated/knowledge/report.json` | `"status": "VALIDATED"`, timestamp `2026-08-30T01:00:00Z`, 136 documents | file is dirty in the worktree | Routing hint; not architectural authority |
| `dev_context_logs/context_summary.md` | Branch `feat/beta-release_electroweak-v091`, HEAD `7d46c7f5528c…` | neither current branch nor HEAD | Historical packet; **do not cite as current gates** |
| `python3 tools/docs_rag_v0.py "SOTA long-horizon…"` | Ranked `PRD_FRONTEND_PLATFORM.md` / `PRD_AETHER_DESKTOP.md` | query was backend-first | Knowledge-index routing failure |
| `--file` routing for `agency/episode/engine.py` | owner `docs/backend/architecture/agency.md` | current | Useful owner pointer |
| `--file` routing for `runtime/session.py` | subsystem null in catalog; symbol owner `docs/backend/architecture/runtime-execution.md` | current | Partial catalog hole |

**Degraded mode declared.** LDA was **not** rebuilt (would have mutated `.lda/index.db` without being requested). Indexes were used only to pin symbols. All architectural claims below were checked against current source, current tests, or official URLs.

**Historical CONTRADICTION (ebad36e).** [`docs/execution/milestones.md`](../docs/execution/milestones.md) marks **W-092-F0** as `DONE` with predicate “LDA/index health is HEAD-bound”. Current `lda identity` reports `STALE` versus HEAD `ebad36e`. Plan B treats W-092-F0 as **not currently satisfied** for this worktree, regardless of the milestone table.

**Historical CONTRADICTION (ebad36e).** [`README.md`](../README.md) says [`docs/execution/active.md`](../docs/execution/active.md) is the sole current-state source. The file currently contains the same `id: execution.tasks` body as [`docs/execution/tasks.md`](../docs/execution/tasks.md). Plan B treats `tasks.md` + `FEATURE_SPEC.md` as the in-flight delta contract and treats `active.md` as a duplicate, not a second authority.

### 2.3 Commands run this session (FACT)

```text
git status --short
git rev-parse HEAD
env UV_CACHE_DIR=/tmp/vanguard-uv-cache uv run lda identity --json
env UV_CACHE_DIR=/tmp/vanguard-uv-cache uv run lda doctor --json
cat .generated/knowledge/report.json
python3 tools/docs_rag_v0.py "SOTA long-horizon software engineering agents framework architecture DeepSWE SWE-bench Pro" --budget 8000
python3 tools/docs_rag_v0.py --file vanguard/packages/agency/episode/engine.py
python3 tools/docs_rag_v0.py --file vanguard/packages/agency/context/compiler.py
python3 tools/docs_rag_v0.py --file vanguard/packages/runtime/session.py
python3 tools/docs_rag_v0.py --file vanguard/packages/runtime/task_state.py
env UV_CACHE_DIR=/tmp/vanguard-uv-cache uv run lda symbol EpisodeEngine --exact
env UV_CACHE_DIR=/tmp/vanguard-uv-cache uv run lda symbol ContextCompiler --exact
env UV_CACHE_DIR=/tmp/vanguard-uv-cache uv run lda symbol CodingTaskState --exact
env UV_CACHE_DIR=/tmp/vanguard-uv-cache uv run lda symbol HarnessSession --exact
python3 tools/linters/check_tcb_budget.py
python3 tools/linters/check_domain_blindness.py
env UV_CACHE_DIR=/tmp/vanguard-uv-cache uv run python -m unittest \
  test.agency.test_episode.Terminals.test_completion_admission_rejection_returns_to_the_model \
  test.agency.test_coding_state \
  test.agency.test_context_compiler.Budget \
  test.agency.test_protocol_recovery -v
env UV_CACHE_DIR=/tmp/vanguard-uv-cache uv run python -m unittest \
  test.falsifiers.test_rf25_cold_continuation \
  test.runtime.test_topology_lowering \
  test.falsifiers.test_m8_skill_lifecycle \
  test.benchmarks.test_sota_protocols -v
```

### 2.4 Tests run this session (FACT)

| Command | Result | Interpretation |
|---|---|---|
| 16 agency tests (admission, coding state, compiler budget, protocol recovery) | 16 OK in 0.004s | MECHANISM of admission reject-and-retry, CodingTaskState digest, L1/L2 immunity, brief exemption |
| 52 tests (RF-25, topology lowering, M-8 skill lifecycle, SOTA protocols) | 52 OK in 0.553s | MECHANISM of cold continuation, topology value boundary, held-out promotion refusal, Wilson/McNemar protocol objects |
| Full `just verify` | **not run** | Do not claim repository-wide green from this session |
| Official DeepSWE / SWE-bench Pro | **not run** | No external score |

### 2.5 Benchmark artifacts inspected (FACT)

| Artifact | Observed | Claim permitted |
|---|---|---|
| [`benchmarks/sota_preregistration.json`](../benchmarks/sota_preregistration.json) | `subject_sha=ca47eef7da1b…` ≠ HEAD; B1 membership is 20 named tasks; B2 gated on B1 | Protocol intent only |
| [`benchmarks/sota_spend_ledger.json`](../benchmarks/sota_spend_ledger.json) | SOTA-08 B1: 21 calls, `$0.002037315`, `observed_tasks=21`, `passed=2`, `failed=19`, `disposition=INVALID_PREREGISTRATION_STOP`, reason `__pycache__` membership, `wilson_interval_valid=false`, `b2_authorized=false` | Historical invalid campaign; **not** a Coding Max score |
| `benchmarks/benchmark_20_suite/benchmark_20_results.json` and `…_vg_code_max.json` | Byte-twin 21-row results; 2 PASS / 19 FAIL; claimed 9.5%; many `turns=1`; no patch digest; no source SHA | Invalid membership |
| `benchmarks/benchmark_20_suite/benchmark_20_results_vg_1_forge.json` | 1/1 PASS, `$0.002364`, one task | One-task result; no CI |
| Current `benchmarks/benchmark_20_suite/runner.py:845` | `not d.name.startswith("__")` | **Current** enumerator would exclude `__pycache__`; historical run did not |
| `benchmarks/agentic_matrix_benchmark_results.json` | cassette/golden-deterministic coding arm | Synthetic |
| `benchmarks/independent_v091/artifacts/report.json` | 5/5 on small fixtures; LDA head `8d9e37e…` ≠ HEAD | Not SWE-class evidence |
| BAAC / ladder reports | frequent `mode=lam`, n=1, `HARNESS_ERROR` mixed into fail | Smoke only |
| [`benchmarks/protocols.py`](../benchmarks/protocols.py) | `SUPPORTED_PROTOCOLS = {SWE-bench Verified, SWE-Bench Pro, DeepSWE v1.1}`; docstring: does not execute a provider or evaluator | Contract stub, not a runner |

### 2.6 Paid cost this session (FACT)

**US$0.00.**

No OpenRouter call was issued. The $0.10 authorization was not used because:

1. The last paid B1 campaign is already recorded as `INVALID_PREREGISTRATION_STOP`.
2. Preregistration is bound to SHA `ca47eef7…`, not HEAD `ebad36e…`.
3. A single cheap completion cannot distinguish harness error from model failure, cannot produce a Wilson interval, and cannot repair membership.
4. Spending money on an untrustworthy enumerator would create a new historical number that later drafts would be tempted to cite.

A later Wave 0 canary is authorized only after membership, subject SHA, and missingness contracts are executable.

### 2.7 Pre-existing dirty worktree (FACT)

Unrelated user work exists under `vanguard/clients/tui*`, `vanguard/clients/cli`, `docs/product/frontend/PRD_AETHER_TUI.md`, `docs/execution/{backlog,tasks}.md`, generated knowledge files, and `vanguard/packages/runtime/{profiles,session,wiring}.py`. Plan B did not revert, restage, or reformat those files.

### 2.8 How to read the rest of this document

Sections 3–4 are FACT/MECHANISM. Section 5 is mathematics with stated assumptions. Sections 6–18 are PROPOSAL constrained by the lattice. Section 16 states what would be required before any ASPIRATION score is speakable.

---

## 3. Current implementation inventory

Legend for **Disposition**: `keep` = preserve and harden; `repair` = present but untruthful; `promote` = move to the correct layer; `defer` = do not productize yet; `reject-as-default` = keep as experiment, never the production loop.

Lock-time verb inventory matching pack YAML is appended as **§22** (does not replace this section). Product target loop is **§23**. Edit/2PC mechanics live in v2; law/profiles live in A.

### 3.1 Substrate and control plane

| Capability | Owner | Actual implementation | Current evidence | Gap | Disposition |
|---|---|---|---|---|---|
| S0–S12 dispatch, typed budgets, attenuation | `vanguard/packages/kernel/` | 9 files, 1386 LOC; `dispatch.py` owns the pipeline | `check_tcb_budget.py` PASS; domain-blindness PASS this session | 52 LOC headroom; coding semantics must never enter | keep |
| Hexagonal ports | `vanguard/packages/ports/` | `ModelPort`, `EvaluatorPort`, `IndexPort`, SPI in `spi.py`; **no** symbol `KernelPort` (kernel collaborators are `Clock`/`EffectAdapter`/`Ledger`) | contract tests exist | docs that say `KernelPort` are stale | keep + doc repair later |
| Event-sourced ledger | `runtime/ledger_emitter.py`, SQLite WAL | single-writer; `State = fold(events)` | RF-25 test OK this session | resume episode-id synthesis (see §4.4) | keep + repair identity |
| Canonical composition | `runtime/compose.py`, `runtime/wiring.py` | one activation plan | M-3C historical | Forge/Chimera bypass this path | keep; isolate bypasses |
| Execution profiles | `runtime/profiles.py` | `product`/`local`/`sandboxed`/`hermetic` | mechanism | plan-mode slices exist in dirty worktree; not this plan’s subject | keep |

### 3.2 Agency inner loop

| Capability | Owner | Actual implementation | Current evidence | Gap | Disposition |
|---|---|---|---|---|---|
| Episode turn loop | `agency/episode/engine.py` `EpisodeEngine` L189–1072 | observe → propose → recover → admit finish → spawn or `kernel.dispatch` | `test_episode.py` OK | `_view` omits CodingTaskState | keep; enrich view via compiler, not a second loop |
| Completion admission | `agency/episode/admission_gate.py` `AdmissionGate.evaluate` L46–152 | write presets need changed files, inspection, bound `VerificationReceipt`, `executed_test_count > 0` | unit tests OK | preset-name substring heuristic; `**_` ignores greenfield kwargs; default pack exempt in session | repair |
| Session gate wiring | `runtime/session.py` `admission_required` L127–138 | exempt `vg-code-default`, `vg-code-lex`; else `patch.apply` in verbs | `ADMISSION_GATED_HARNESSES` L119–121 is **unused** | default product path can `finish` with zero effects | repair |
| Protocol recovery | `agency/episode/protocol_recovery.py` | fingerprint anti-repeat; truncation/patch-as-text retries | unit tests OK | string-marker `classify`; conversational accept when no patch required | keep + typed dialect later |
| Context compiler L1–L5 | `agency/context/compiler.py` L80–244, `layers.py`, `compaction.py` | prefix-frozen; brief exempt; result eviction | Budget tests OK this session | token estimate ≈ 4 chars/token; structured consolidate is keyword scrape; no `progressive.py` | keep L1–L5; add progressive as L4/L5 policy, not a fourth compiler |
| Context packet | `agency/context/packet.py` `ContextPacket` L19–68 | digestable packet with omissions | `validate_resume_identity` exists | session orientation packet often omits `repository_identity` / `selection_policy_identity` | repair |
| In-process spawn | `EpisodeEngine.spawn` L948–1072 | attenuated child for tests/legacy | spawn tests | production recursion is `RuntimeChildRunner` | keep as test path only |

### 3.3 Runtime session, state, resume

| Capability | Owner | Actual implementation | Current evidence | Gap | Disposition |
|---|---|---|---|---|---|
| HarnessSession | `runtime/session.py` L465–1443 | constructs one kernel; injects meta-controller; observes completion; exterior evaluate | session tests exist | test-count regex fail-closed (good) but coarse; resume dumps state into L3 | repair |
| CodingTaskState | `runtime/task_state.py` L84–234, `fold_task_state` L237+ | discoveries, dead ends, todos, routes, implicated files | `test_coding_state` OK | lives in **runtime**, not domain; not consumed by ContextCompiler; `ProposalProduced` verification inference uses `"test" in action.lower()` | promote schema to domain; keep fold in runtime |
| SemanticTaskState | `docs/execution/FEATURE_SPEC.md` §3 | **absent** / **MISSING** (`vanguard/packages/domain/task_state.py` does not exist) | claimed falsifier `test/contracts/test_semantic_task_state.py` absent | CMX-09 T2 not implemented | implement as domain value, fold from events |
| Checkpoints | `runtime/checkpoints.py` | blob-verified reconstruct; warm/cold parity | RF-96 tests exist | optional (needs blobs) | keep |
| ApplicationService.resume | `runtime/app_service.py` L385–389 | `episode_id=f"episode-{resolved_run_id}"` | RF-25 proves **event fold** continuation | synthesized episode id may not match original ledger episode | repair |
| CodingMaxFacade | `apps/coding_max/facade.py` L23–71 | thin client of `ApplicationService`; presets `fast|balanced|max` → `agency/manifests/vg-code-{preset}/manifest.json` | mechanism | no intelligence in apps; correct lattice | keep thin |

### 3.4 Packs, verification, change surface

| Capability | Owner | Actual implementation | Current evidence | Gap | Disposition |
|---|---|---|---|---|---|
| code-default pack | `packs/code-default/` | harness.yaml, presets, plugin SPI, toolkits | pack tests exist | keyword `classify_task`; greenfield bypasses multi-file completeness | repair classifier; keep greenfield explicit |
| Change surface | `domain/transforms/repository/change_surface.py` `ChangeSurfaceEstimator` L26+ | traceback/brief regex + optional edges; `truncated` flag | mechanism | coverage_ratio can be 1.0 when primary empty; Python-path regex | repair estimator; do not treat ratio as proof |
| Implicated files | pack `implicated_files.py` | depth 1 / 128 file caps | mechanism | truncated sets must fail admission (already a reason code) except greenfield bypass | keep fail-closed; remove silent bypass |
| Git environment | `adapters/environment/git.py` `GitEnvironment.apply` ~L853 | sequential writes; syntax is observation-only `ast.parse` | mechanism | **no** `transaction.py` 2PC | implement adapter 2PC; keep kernel blind |
| IndexPort | `ports/index.py` | observation-only repo map; `truncated` | port comment forbids ranking | no HEAD/mtime epoch protocol; pack IndexToolkit is regex, comment says no tree-sitter | add epoch; keep port policy-free |
| Exterior evaluator | `adapters/evaluators/`, `runtime/evaluator_gateway.py` | signed binding required to ledger a verdict | daemon/signing tests exist | product coding loop still uses local test output as admission evidence | keep gateway; bind local verify ≠ exterior verdict |

### 3.5 Parallel engines, topology, memory

| Capability | Owner | Actual implementation | Current evidence | Gap | Disposition |
|---|---|---|---|---|---|
| ForgeEngine | `agency/forge/engine.py` | own tools, own admission, **bypasses Kernel.dispatch**; `if exit_code == 0 and test_count == 0: test_count = 1` at L309–311 | forge unit tests | second runtime semantics; false-positive completion | reject-as-default; quarantine from Coding Max scores |
| ChimeraEngine | `agency/chimera/engine.py` | parallel loop | chimera tests | same lattice tension | reject-as-default |
| Role manifests | `agency/manifests/{localizer,reviewer,test_investigator}.py` | helpers that write artifacts; reviewer has **no admission authority** | CMX-08 falsifiers | not autonomous agents | keep as treatments after Wave 5 |
| Topology lowering | `runtime/topology.py` | sequential default; rejects authority fields | topology tests OK this session | not a coding agent | keep |
| WorkflowScheduler | `runtime/workflow_scheduler.py` | sequential + `bounded_parallel` ThreadPoolExecutor | workflow tests | synthetic LeaseAcquired without kernel leases | repair parallel path or keep sequential-only in product |
| Child runtime | `runtime/child_runtime.py` | sole public recursion via `run_composed`; drops meta-controller | RF-101 tests | correct lattice | keep |
| Meta-controller | `runtime/meta_controller.py` | guarded consult; fail-closed on budget enlargement | M-6.5 falsifiers | opt-in; published study undeterminable | defer as default |
| Memory / skills | `runtime/memory.py`, `skill_lifecycle.py`, `skill_evaluation.py`, `governance/learning.py` | ports, unsigned registry refuses promote, held-out evaluator | M-8 lifecycle tests OK this session | no product wiring; MEM-02 blocked; presence≠use already encoded | defer productization |
| Tamper shield / 2PC / progressive compiler | FEATURE_SPEC §4–7 | **files absent** in `vanguard/` | claimed tests absent | T3–T5 of current sprint are unimplemented | implement on lattice, not as copies of review-tree code |

### 3.6 Models

| Capability | Owner | Actual implementation | Current evidence | Gap | Disposition |
|---|---|---|---|---|---|
| Registry | `adapters/models/models_registry.json` | default `deepseek/deepseek-v4-flash-0731`; tier2 also `z-ai/glm-5.3-flash`; tier3 `openai/gpt-5.6-luna`; pricing micros recorded | file is source of truth | harness.yaml aliases can omit `-0731` | fail-closed resolve |
| Routing | `adapters/models/routing.py` | Single / TierEscalation / Fallback routers | mechanism | `resolve_route` swallows resolve exceptions; capabilities always empty tuple | repair |
| Dialect | `adapters/models/dialect.py` `normalize_response` | native tool_calls → fenced/balanced JSON; failures `not_json`/`truncated`/`missing_kind` | mechanism | FEATURE_SPEC taxonomy (`TRANSPORT`…`PERMISSION`) not implemented; `test/contracts/test_dialect_recovery.py` absent | enhance in adapter, not kernel |

### 3.7 What VISION already forbids (FACT)

From [`VISION.md`](../VISION.md): event sourcing is the ontology; agents are projections not objects; memory/topology/learning are derived families not new cores; promotion requires separated generator/evaluator/promoter; mechanism ≠ acceptance. Plan B does not reopen those decisions.

---

## 4. Proven gaps

Each gap answers: what exists, where, what is missing, why it blocks long-horizon work, smallest next change, dependents, falsifier, promotion evidence, rollback.

### 4.1 False-positive completion on the default path

**Exists.** `AdmissionGate` is strict when wired. `admission_required` exempts `vg-code-default` and `vg-code-lex`. `ADMISSION_GATED_HARNESSES` is documented and tested in spirit but **not consulted**.

**Why it blocks.** Long-horizon reliability is a product of honest terminals. If `finish` is a conversational act, compaction and resume preserve a lie.

**Smallest change.** Delete the exemption or replace it with an explicit `read_only` capability. Drive gating from verbs + task class, not from a second name set.

**Depends on this.** Every later wave’s pass rate.

**Falsifier.** A `vg-code-default` episode that issues `finish` with zero `patch.apply` receipts must be `abandoned`/`rejected`, not `completed`.

**Rollback.** If frozen RF-95 evidence depended on ungated default, record a successor baseline rather than silently widening the exemption again.

### 4.2 Invented test counts (Forge)

**Exists.** `agency/forge/engine.py` L309–311 sets `test_count = 1` when `exit_code == 0` and parse failed.

**Contrast.** `runtime/session.py` `_observed_test_count` L363–375 returns 0 on unparseable output (correct fail-closed).

**Why it blocks.** Forge can admit “green” on empty or unparsed suites. Any benchmark that scores Forge against Coding Max is then incomparable.

**Smallest change.** Remove the fallback. If a later adapter cannot parse a CTRF/JUnit document, count is 0 and admission fails.

**Falsifier.** `exit_code == 0` + empty output ⇒ `VerificationReceipt.passed is False`.

### 4.3 Heuristic verification classification

**Exists.** Session treats argv containing `pytest`/`unittest` or substring `"test"` as verification; exit code from `[exit N]` in detail; pack parsers accept `"OK" in output`.

**Why it blocks.** `python3 -c 'print("OK")'` and `ruff` on tests can look like verification. Test-count 0 should already fail admission; substring `"test"` can still attach a receipt to the wrong command.

**Smallest change.** Bind verification to an explicit subject: argv digest + workspace digest + task digest (AdmissionGate already has these fields). Refuse receipts whose command is not in the frozen verification plan.

### 4.4 Incomplete restart identity

**Exists.** RF-25 proves fresh-process fold continuation. `ApplicationService.resume` synthesizes `episode_id=f"episode-{run_id}"`. Session dumps `task.resume_state` JSON into **immutable L3** at construction (`session.py` L619–622). `ContextPacket.validate_resume_identity` is not fully populated on that path.

**Why it blocks.** Cognitive state (plan, dead ends, active file) is frozen in the prefix-cached environment. Later writes do not update L3. The model reasons about a snapshot that is definitionally stale after the first post-resume edit. Synthesized episode ids can fork attribution.

**Smallest change.** Persist original `episode_id`. Put `CodingTaskState` in L4 (stable notes) / L5 (turn-local), never L3. Recompile L4 from the fold every turn.

**Falsifier.** After resume + one write, the prefix bytes of L1–L3 match the pre-write prefix; L4 digest changes; original episode_id is preserved in events.

### 4.5 Stale repository intelligence

**Exists.** IndexPort is observation-only (correct). Session pulls `repo_map(token_budget=4000)` once at construction into env_parts. Pack indexer comments that it is not tree-sitter. No workspace epoch / mtime / HEAD binding.

**Why it blocks.** After `patch.apply`, symbols and callers can be wrong. Progressive retrieval then maximizes the wrong subgraph.

**Smallest change.** Define `WorkspaceEpoch = (tree_hash, index_digest, source_revision)`. Invalidate the packet when tree_hash changes. Force `index.refresh` (mediated) before the next compile.

**Falsifier.** Write a function, then query callers: packet `truncated` or refresh required; never a pre-write caller set presented as current.

### 4.6 Change-surface incompleteness

**Exists.** Regex estimator + depth-1 implicated builder. Completeness policy can reject empty/truncated sets, except greenfield bypass.

**Why it blocks.** Brownfield bugs whose names do not appear in the brief are under-localized. Over-broad directory prefixes dump noise into context.

**Smallest change.** Require IndexPort dependency/test edges for write presets. Treat `coverage_ratio` as non-evidence when `primary_files` is empty. Keep truncation as admission failure.

### 4.7 Insufficient long-run evidence

**Exists.** Mechanism tests for 40-turn budgets, RF-25 death, compaction. **No** HEAD-bound live run of 40+ turns with exact patch identity.

**Why it blocks.** Compaction and resume bugs appear after the unit-test horizon.

**Smallest change.** After Waves 0–2, a frozen 40-turn internal task with ledger replay parity, not a leaderboard run.

### 4.8 Benchmark membership errors

**Exists.** B1 included `__pycache__`; current runner filters `startswith("__")`; spend ledger already marked INVALID.

**Why it blocks.** Any citation of 9.5% or Forge 100% is contamination of the planning process itself.

**Smallest change.** Wave 0: enumerator contract test that the task set digest equals preregistration; refuse `__pycache__`, `.pytest_cache`, `.vanguard`.

### 4.9 Multi-agent mechanisms without measured lift

**Exists.** Topology lowering, child runtime, localizer/reviewer manifests, workflow scheduler.

**Missing.** Paired ablation showing \(\Delta\) pass@1, \(\Delta\) cost, \(\Delta\) merge failures vs single-agent control.

**Disposition.** `reject-as-default` until Wave 5 control exists.

### 4.10 Memory without held-out promotion on the product path

**Exists.** M-8 **mechanism** is strong (this session: contamination refused, lift threshold enforced, three authorities distinct, rollback executable).

**Missing.** MEM-02 empirical canary; product composition does not retrieve durable memory by default (`memory.py` comment: no public wiring before ADR-0100).

**Disposition.** Do not “turn memory on” to chase scores.

### 4.11 Orchestration proposals not implemented

Octopus mailbox, CoordinationPlan DAG, outer-loop director, Hydra emergent agency, Chimera as default: **research**. FEATURE_SPEC T2–T5 files: **absent**. Plan B will not copy review-tree file paths that violate the lattice (for example, putting coding oracles in `kernel/`).

### 4.12 FEATURE_SPEC vs source (CONTRADICTION table)

| FEATURE_SPEC path | Source on HEAD `ebad36e` |
|---|---|
| `vanguard/packages/domain/task_state.py` | missing / **MISSING** |
| `vanguard/packages/adapters/environment/transaction.py` | missing |
| `vanguard/packages/runtime/governance/tamper_shield.py` | missing |
| `vanguard/packages/agency/context/progressive.py` | missing |
| `test/contracts/test_semantic_task_state.py` | missing |
| `test/runtime/test_atomic_multi_file_transaction.py` | missing |
| `test/runtime/test_tamper_shield.py` | missing |
| `test/agency/test_progressive_context_compiler.py` | missing |
| `test/contracts/test_dialect_recovery.py` | missing |
| `adapters/models/dialect.py` | **exists**, narrower than FEATURE_SPEC taxonomy |

Sprint `tasks.md` still lists T2–T6 as the active DAG. Plan B **agrees with the dependency order** (state → atomic writes → tamper → progressive context → dialect) and **disagrees with any reading that those modules already exist**.

### 4.13 Draft reconciliation (do not copy blindly)

| Draft / research | Useful residue | Rejected or corrected |
|---|---|---|
| [`.draft/DEVELOPMENT_FINAL_PLAN.md`](DEVELOPMENT_FINAL_PLAN.md) | Same reliability-first ordering | Bound to SHA `7e08462c2cbb…`, not this HEAD; do not copy its evidence snapshot |
| [`.draft/todo/SOTA_CODING_HARNESS_ENGINEERING_ROADMAP.md`](todo/SOTA_CODING_HARNESS_ENGINEERING_ROADMAP.md) | Five systems challenges; pre-mutation impact | Overclaims “undisputed SOTA”; some file targets ignore packs vs kernel |
| [`.draft/todo/development_plan_guidelines_0209.md`](todo/development_plan_guidelines_0209.md) | Lattice, no second runtime, WIP | Forbids git; this planning task required git identity — planning ≠ that implementation prompt |
| [`.draft/HYDRA_MULTI_AGENT_TOPOLOGY_AND_EMERGENT_AGENCY.md`](HYDRA_MULTI_AGENT_TOPOLOGY_AND_EMERGENT_AGENCY.md) | Mailbox metaphor | Default swarm; competing runtime authority |
| [`.draft/SONNET_SUPER_AGENT.md`](SONNET_SUPER_AGENT.md) | Competency rhetoric | Model folklore as architecture |
| Octopus `long-horizon-context-engine.md` / `outer-loop-orchestrator.md` | Progressive packets; campaign director **above** EpisodeEngine | Not implemented; must not become a second engine |
| `docs/research/coding_harness/VANGUARD_VS_LIM_INSIGHTS_SOTS_TECHNIQUES.md` | LIM as **skunkworks**; prefix-cache hypothesis | Empirical 83% turn reduction / $0.00033 claims are **not** exact-subject for HEAD `ebad36e`; LIM is not runtime authority ([`README.md`](../README.md)) |
| FEATURE_SPEC synthetic oracle protocol | Greenfield TDD stages | Tamper shield hashing via `Path.glob("test/**")` is incomplete on real trees; implement with explicit test-file enumeration from IndexPort |

---

## 5. Formal agent model

Assumptions are stated. Constants that are not estimated from this repository are marked **unidentified**.

### 5.1 Constrained POMDP

Let an episode be a constrained POMDP

\[
\mathcal{M} = \langle \mathcal{S}, \mathcal{A}, \mathcal{O}, T, Z, R, \gamma, \mathcal{C} \rangle
\]

- \(\mathcal{S}\): workspace tree, test oracle, hidden bug/feature semantics, budget remaining, epoch.
- \(\mathcal{A}\): mediated effects (`fs.read`, `patch.apply`, `test.run`, `spawn`, `finish`, …) plus `abstain`.
- \(\mathcal{O}\): receipts, compiler packet, admission feedback — **not** the true tree.
- \(T(s'|s,a)\): deterministic for filesystem effects if the adapter is honest; stochastic for models and flaky tests.
- \(Z(o|s',a)\): observation channel; compaction and stale indexes corrupt \(Z\).
- \(R\): 1 iff exterior (or bound local) verifier accepts **and** admission is admissible; 0 if fail; **undefined** if missing — missing is not 0.
- \(\gamma \in (0,1]\): not identified; do not pick 0.99 for rhetoric.
- \(\mathcal{C}\): capability + budget constraints. Kernel enforces \(\mathcal{C}\) independently of \(R\).

Policy \(\pi\) is **not** inside the kernel. \(\pi\) is the composition of model, compiler, pack completion policy, and optional meta-controller.

**Constraint.** For all \(a\) not authorized by the current grant, \(T\) is not invoked; a denial event is appended. This is already MECHANISM.

### 5.2 Event-sourced semantic task state

Let \(E_{1:n}\) be the ledger. A projection \(\Phi\) yields task state:

\[
\sigma_n = \Phi(E_{1:n}) \in \Sigma
\]

Today \(\Phi\) is `fold_task_state` producing `CodingTaskState` (runtime). FEATURE_SPEC wants \(\Sigma =\) `SemanticTaskState` (domain) with monotonic `revision`.

**Required properties (PROPOSAL, testable):**

1. **Immutability of prefixes:** \(\Phi(E_{1:k})\) depends only on \(E_{1:k}\).
2. **Monotone revision:** \(k < n \Rightarrow \sigma_n.\mathrm{revision} \ge \sigma_k.\mathrm{revision}\).
3. **JCS digest stability:** `digest_of(canonical(\(\sigma\)))` is RFC 8785 stable ([RFC 8785](https://www.rfc-editor.org/rfc/rfc8785)).
4. **No I/O in \(\Phi\)** if \(\sigma\) lives in domain.

**INFERENCE.** Dumping \(\sigma\) into L3 violates (1) for the *prompt* even if the ledger fold remains correct: the prompt is a second, stale projection.

### 5.3 Progress potential

Define a Lyapunov-like potential on \(\sigma\):

\[
V(\sigma) = \alpha_1 U_{\text{unverified}} + \alpha_2 |\mathrm{open\ todos}| + \alpha_3 |\mathrm{uninspected\ modified}| + \alpha_4 \mathbf{1}[\neg \mathrm{epoch\ fresh}]
\]

with \(\alpha_i > 0\) **unidentified**. Admission of `finish` requires \(V(\sigma)=0\) on the **gated** coordinates (modified files inspected, verification bound, epoch fresh). Do not optimize \(V\) inside the kernel.

A turn is *honest progress* if \(V(\sigma_{t}) < V(\sigma_{t-1})\) or a new dead-end is recorded that strictly reduces the remaining hypothesis set. Repeating a semantically equal failed patch is not progress (`protocol_recovery` already fingerprints attempts — MECHANISM).

### 5.4 Context optimization

Let token budget \(B\). Layers \(L_1,\ldots,L_5\) with freeze prefix \(L_1{\parallel}L_2{\parallel}L_3\).

\[
\max_{C \subseteq \mathcal{U}} \; F(C) \quad \text{s.t.} \quad \sum_{c \in C} \hat{\tau}(c) \le B - \tau_{\text{prefix}}
\]

where \(\mathcal{U}\) is the universe of candidate snippets (AST slices, stubs, receipts). \(F\) should be submodular if greedy packing is used (LDA’s compiler already uses submodular packing for **docs**; coding packets currently use truncation + recency).

**Token estimator.** Current \(\hat{\tau}(s) \approx |s|/4\). Error \(\varepsilon_\tau\) biases packing. PROPOSAL: calibrate \(\hat{\tau}\) per dialect on held-out traces; until then treat \(\hat{\tau}\) as biased and keep a reserve (session already reserves 1000 tokens in packet build — MECHANISM).

**Non-theorem.** More tokens \(\not\Rightarrow\) higher \(\Pr(\text{pass})\). DeepSWE prompts are ~half of SWE-bench Pro length with harder tasks ([DeepSWE paper](https://arxiv.org/abs/2607.07946)). Plan B therefore optimizes *relevant* \(F(C)\), not \(|C|\).

### 5.5 Retrieval value of information

For a candidate snippet \(c\):

\[
\mathrm{VoI}(c) = \mathbb{E}[R \mid C \cup \{c\}] - \mathbb{E}[R \mid C]
\]

This expectation is **unidentified** at planning time. Practical surrogate (PROPOSAL):

\[
\widetilde{\mathrm{VoI}}(c) = \mathbb{1}[c \in \mathrm{implicated}(\sigma)] \cdot w_{\text{kind}}(c) \cdot \mathbb{1}[\mathrm{epoch}(c)=\mathrm{epoch}(\sigma)]
\]

Zero VoI if epoch mismatch. IndexPort must not compute \(\pi\) (port comment already forbids ranking “on the agent’s behalf”). Ranking belongs in the **pack compiler policy**, which is a replaceable \(\pi\) component, not in the indexer.

### 5.6 Blast-radius closure

Let \(G=(V,E)\) be the file/symbol dependence graph from IndexPort. For a patch \(P\) touching \(V_P\):

\[
\mathrm{Blast}(P) = \mathrm{Reach}_{E}^{k}(V_P) \cup \mathrm{Tests}(V_P)
\]

Admission for brownfield write tasks requires:

\[
V_P \subseteq \mathrm{Inspected}(\sigma) \quad \text{and} \quad \mathrm{Tests}(V_P) \subseteq \mathrm{VerifiedSubject}(\sigma) \quad \text{or truncated} \Rightarrow \text{fail closed}
\]

Current estimator is not \(G\); it is regex. Until IndexPort edges are epoch-bound, treat \(\mathrm{Blast}\) as an **upper bound with `truncated` bit**, never as complete.

### 5.7 Verification confidence lattice

Define a lattice (bottom = least confidence):

\[
\bot \prec \text{parsed-output} \prec \text{bound-local-receipt} \prec \text{tamper-checked-local} \prec \text{signed-exterior-verdict}
\]

- `parsed-output`: regex on stdout. Current session path.
- `bound-local-receipt`: `VerificationReceipt` fields already on AdmissionGate (MECHANISM) **if** populated.
- `tamper-checked-local`: FEATURE_SPEC T4 (absent).
- `signed-exterior`: `evaluator_gateway` (MECHANISM) — product coding admission does not require this today.

**Law.** A higher node may imply a lower node; never the reverse. Model self-review is **not on this lattice**. Boolean `verification_passed=True` without a receipt is already rejected (`admission_gate.py` L113–121).

Forge’s `test_count=1` is an illegal jump from \(\bot\) to `parsed-output`.

### 5.8 Strategy selection

Let treatments \(u \in U = \{\text{single}, \text{localize-then-patch}, \text{test-first}, \ldots\}\). Choose

\[
u^\star = \arg\max_{u \in U} \left( \hat{p}_u - \lambda \hat{c}_u - \rho \widehat{\mathrm{Var}}(p_u) \right)
\]

subject to: \(u=\text{single}\) remains the **control**; any other \(u\) requires a paired study. \(\lambda\) is cost aversion (preregistration already has `lambda_usd_per_success: 1.0` — protocol constant, not a physical law). Meta-controller today is a consult with value-in/value-out guards, not this optimizer.

### 5.9 Multi-agent bifurcation

A bifurcation of a parent lineage into children \(i=1..m\) with merge \(\mu\):

\[
R_{\mu} = \Pr(\mu(\{P_i\}) \text{ passes}) \le \sum_i \Pr(P_i \text{ passes}) \quad \text{(union bound; usually much worse)}
\]

For isolated patches with exterior selection, a tighter model is:

\[
R_{\text{sel}} = \Pr(\exists i: P_i \text{ passes} \land \mathrm{selector} \text{ picks a passing } i)
\]

If the selector is the same model, \(\mathrm{selector}\) is correlated with generators (not independent). Plan B requires the selector to be **exterior tests**, not a reviewer LLM, for any treatment that claims lift.

### 5.10 Campaign reliability

For \(K\) tasks i.i.d. Bernoulli(\(p\)):

\[
\hat{p} = \frac{S}{K_{\text{evaluated}}}, \quad K_{\text{evaluated}} = K - K_{\text{missing}}
\]

Missing (harness error, provider 5xx, invalid membership) **must not** enter the denominator as failures or the numerator as successes. Wilson interval:

\[
\hat{p}_W = \frac{\hat{p} + \frac{z^2}{2n}}{1+\frac{z^2}{n}} \pm \frac{z}{1+\frac{z^2}{n}}\sqrt{\frac{\hat{p}(1-\hat{p})}{n}+\frac{z^2}{4n^2}}
\]

with \(z=1.96\) as in `sota_preregistration.json`. Protocol tests for Wilson/McNemar **exist** (`test_sota_protocols` OK this session) and are not a substitute for a valid \(n\).

### 5.11 Cost per signed pass

\[
\kappa = \frac{\sum \mathrm{USD} + \lambda_h \sum \mathrm{harness\_hours}}{\#\{\text{signed exterior or bound-local passes}\}}
\]

Report \(\kappa\) with the same missingness rules. Do not minimize \(\kappa\) by skipping verification.

### 5.12 Iterative architectural erosion

Let quality \(Q_t\) be a hidden attribute (type-check cleanliness, invariant preservation). A naive loop that patches until tests pass can decrease \(Q\):

\[
Q_{t+1} = Q_t - \eta \mathbb{1}[\text{tests pass} \land \text{no review of } \mathrm{Blast}(P)]
\]

\(\eta\) unidentified. Mitigations that **are** lattice-legal: blast-radius tests, tamper shield, reviewer treatment **without** admission authority (already true of `reviewer.py`).

### 5.13 Budget attenuation

Kernel already implements monotonic attenuation: child budgets \(\le\) parent remainder. Formally a residual vector \(b \in \mathbb{N}^d\):

\[
b_{\text{child}} \le b_{\text{parent}} - b_{\text{reserved}}, \quad b \ge 0
\]

Do not add a second governor in Forge. Children must not inherit meta-controller authority (`child_runtime.py` already drops it — MECHANISM).

### 5.14 Skill promotion lift

Let \(p_0, p_1\) be held-out pass rates without/with skill composition. Promote only if:

\[
\hat{p}_1 - \hat{p}_0 \ge \delta, \quad \delta = 0.05 \text{ (M-8 backlog constant)}
\]

and generator \(\neq\) evaluator \(\neq\) promoter (already refused in tests this session). A single successful trajectory is \(\delta\)-inadmissible almost surely for any interesting \(n\).

---

## 6. Target backend architecture

Preserve:

```text
domain ← ports ← kernel ← agency ← runtime → adapters
                              ↓
                         apps/ (runtime client)
```

Coding semantics stay in **packs + agency callbacks + runtime session policy**. Kernel remains domain-blind. `apps/coding_max/facade.py` stays thin.

### 6.1 Inner loop (canonical)

```text
ApplicationService.run
  → Runtime.execute_profiled / compose
  → HarnessSession
       → ContextCompiler(L1–L5 + progressive L4/L5 from Φ(events))
       → EpisodeEngine.run
            → ModelPort.propose
            → protocol_recovery
            → completion_admitter (pack + AdmissionGate)
            → Kernel.dispatch            [only effect path]
            → ledger events
  → EvaluatorGateway (optional signed verdict)
```

**Forbidden.** ForgeEngine / ChimeraEngine on this path. Direct subprocess from packs. Apps importing kernel.

### 6.2 Outer loop

A campaign director is a **runtime client** that submits a DAG of `TaskContext` values to the same `Runtime.run_composed`, persisting handoffs as blob digests. It is not an EpisodeEngine subclass and not a kernel stage.

```text
CampaignDirector (runtime)
  → for node in CoordinationPlan:
        artifact_in = CAS.get(digest)
        result = Runtime.run_composed(role_manifest, task)
        CAS.put(result.artifacts)
  → merge policy (CONCAT | FIRST_COMPLETE | EXTERIOR_SELECT | UNANIMOUS)
```

`UNANIMOUS` without exterior tests is just correlated LLM agreement. Default merge for patches is **EXTERIOR_SELECT**.

### 6.3 Campaign projection

`CampaignState = fold(campaign_events)` analogous to `CodingTaskState`. Lives in domain as values; runtime folds. Never a mutable `Agent` object (VISION).

### 6.4 Content-addressed handoffs

Handoffs are `digest_of(payload)` blobs already in the store. Roles communicate by digest references in `task.artifact_refs` (session already renders those into env_parts — MECHANISM). Do not add shared mutable memory between roles.

### 6.5 Director policy

Director may **choose treatments** (Wave 7+) from a frozen catalog. It may not grant capabilities, enlarge budgets, or mark `completed`. Those remain kernel + admission + evaluator.

### 6.6 Typed verification

Replace stdout folklore with, in order:

1. CTRF/JUnit/unittest parsed counts (0 if unknown).
2. `VerificationReceipt` identity fields (already specified).
3. Tamper shield on enumerated test files (Wave 1–2).
4. Optional signed exterior verdict for release claims.

### 6.7 Repository epoch

```text
WorkspaceEpoch := {
  treeHash,           # git or hashed tree
  indexDigest,        # IndexPort snapshot
  sourceRevision,     # already on RepositoryMap
  compiledAtTurn
}
```

Compiler inputs include epoch. Resume identity includes epoch. Stale epoch ⇒ refresh or fail closed.

### 6.8 Progressive context packet

Keep `ContextPacket`. Populate `repository_identity` and `selection_policy_identity` on every product compile. FEATURE_SPEC 4-tier budget is a **policy over L4/L5**, not a replacement of L1–L5 prefix freeze (INV-DELTA-5).

Proposed mapping:

| FEATURE_SPEC tier | Existing layer | Content |
|---|---|---|
| 0 Invariant anchor | L1 + L4 head | goal, active step, settled invariants |
| 1 Negative memory | L4 | dead ends, falsified hypotheses from \(\sigma\) |
| 2 Active AST slice | L5 | current files, epoch-bound |
| 3 Symbol stubs | L5 remainder | IndexPort stubs with omissions |

### 6.9 One-writer workspace policy

One episode writes; children that write must be sequential or isolated worktrees (`git.py` already has worktree isolation MECHANISM). Parallel writers on one tree are forbidden in product profiles. WorkflowScheduler’s parallel leases must not imply parallel writes.

### 6.10 Exterior evaluation

Keep UID-isolated daemon. Product `completed` may use bound-local lattice node for internal qualification; **official** SWE/DeepSWE claims require the official harness + separate verifier container (DeepSWE v1.1 already grades committed patches in a fresh container — [DeepSWE v1.1 blog](https://deepswe.datacurve.ai/blog/deepswe-v1-1)).

### 6.11 Operator control

Approvals remain Ed25519-gated (`runtime/governance/approvals.py`). TUI/CLI is a client of `ApplicationService` (`run`/`resume`/`status`/`evidence`/`cost` already on CodingMaxFacade). This plan does not specify OpenTUI.

### 6.12 Where FEATURE_SPEC modules belong (corrected)

| Module | Correct layer | Why |
|---|---|---|
| `SemanticTaskState` | `domain/` | pure values, JCS |
| `fold_semantic_task_state` | `runtime/` next to `fold_task_state` | I/O-free fold still may live in runtime if it imports events; alternatively domain reducer if event types are domain |
| `AtomicMultiFileTransactionManager` | `adapters/environment/` | disk I/O |
| `TestTamperShield` | `runtime/governance/` or pack testing middleware | policy; not kernel |
| Progressive compiler | `agency/context/` as strategy of existing compiler | do not fork a second ContextCompiler class hierarchy if a strategy suffices |
| Dialect taxonomy | `adapters/models/dialect.py` | already the owner |

---

## 7. Competency profiles

These are **measurable product profiles**, not job-title claims about replacing humans. Benchmark scores do not equal professional replacement ([OpenAI, separating signal from noise](https://openai.com/index/separating-signal-from-noise-coding-evaluations/)).

METR’s 50% time-horizon is a different construct (human-expert duration at 50% success on METR’s suite) and is saturating at long durations; METR warns measurements above 16 hours are unreliable with the current suite ([METR time horizons](https://metr.org/time-horizons/)). Plan B uses METR only as a **qualitative horizon language**, not as a pass criterion.

### 7.1 Senior Developer

| Axis | Requirement |
|---|---|
| Scope | 1–20 files; bugfix/feature within an existing architecture; 15–60 turns |
| Default topology | Single agent, `vg-code-balanced` |
| Abilities | Reproduce, localize with IndexPort, surgical patch, affected tests, truthful `finish` |
| Artifacts | Patch, bound verification receipt, ledger |
| Verification | Bound-local lattice ≥ `bound-local-receipt`; tamper shield on brownfield |
| Completion gate | AdmissionGate + pack completeness; zero-test fail closed |
| Internal criterion | Frozen senior-class suite Wilson LB \(\ge 0.50\) at \(n\ge 30\) **after** Waves 0–5 |
| External | Not claimed; DeepSWE-like tasks are often harder than “senior afternoon bugs” |

### 7.2 Staff Engineer

| Axis | Requirement |
|---|---|
| Scope | Cross-module change; migration; 40–120 turns; resume ≥1 |
| Default topology | Single agent + optional `test_investigator → implementer` **after** ablation |
| Abilities | Blast-radius closure, epoch refresh, dead-end memory, budget-aware escalation |
| Artifacts | Plan DAG in \(\sigma\), implicated set, verification subject list |
| Verification | Affected-test closure + regression set; truncated ⇒ fail |
| Completion gate | All TaskSteps `VERIFIED` (once SemanticTaskState exists) |
| Internal criterion | Staff-class frozen suite LB \(\ge 0.40\) **and** resume parity on ≥5 tasks |
| External | SWE-bench Pro public is the closest published analogue; **do not** quote vendor 80% as this profile |

### 7.3 Principal Architect

| Axis | Requirement |
|---|---|
| Scope | Greenfield multi-package or brownfield architectural change; contracts before code |
| Default topology | `architect-plan` (single writer) then implementer; reviewer has no admit authority |
| Abilities | Extract requirements, write ports/types first, synthetic failing oracle, topological file DAG |
| Artifacts | Architecture notes in \(\sigma.settled\_invariants\), oracle digest, scaffold |
| Verification | Oracle fail-on-stub (FEATURE_SPEC §5) then pass-on-impl; no test mutation |
| Completion gate | Behavioral oracle + smoke + files exist; greenfield completeness policy |
| Internal criterion | Greenfield suite \(n\ge 15\) with oracle-vacuity checks |
| External | DeepSWE’s original tasks are closer than mined SWE-bench; still not “principal architect” |

### 7.4 Tech Lead

| Axis | Requirement |
|---|---|
| Scope | Campaign of multiple tasks; merge policy; operator checkpoints |
| Default topology | Outer-loop director; inner loop still single-writer episodes |
| Abilities | Decompose, sequence, refuse to start Wave-7 treatments without control, report missingness |
| Artifacts | CoordinationPlan, per-node receipts, campaign fold |
| Verification | Each node independently admitted; campaign success ≠ OR of conversational summaries |
| Completion gate | All required nodes signed; rollback of a node does not corrupt others’ CAS artifacts |
| Internal criterion | Campaign fixture of ≥8 nodes, one forced crash, resume of remaining DAG |
| External | Not a public leaderboard |

### 7.5 Mapping to public benches (cautious)

| Profile | Internal suite | Public analogue (not equivalent) |
|---|---|---|
| Senior | B1-class 20 tasks **after membership repair** | SWE-bench Verified is too saturated to certify this |
| Staff | Multi-file brownfield 30+ | SWE-bench Pro public (731), Scale standardized ~55–62% frontier as of 2026-09-03 |
| Principal / long-horizon | Greenfield + original tasks | DeepSWE v1.1 (113 tasks, 91 repos); leaders 74%±1–4% on mini-swe-agent |
| Tech lead | Campaign DAG | None; do not fake one |

---

## 8. Development waves

WIP=1 in the implementation lane. Evaluation lane is independent and may only **invalidate**, never silently repair product code.

Shared rollback for every wave: revert the wave’s files; do not weaken falsifiers; do not update preregistration SHA to match a bad run.

### Wave 0 — Truth baseline and benchmark integrity

- **Objective.** HEAD-bound identity; enumerator membership digest; dry-run cannot emit pass/cost; no `__pycache__` tasks.
- **Dependencies.** None.
- **Source files.** `benchmarks/benchmark_20_suite/runner.py`, `benchmarks/protocols.py`, `test/benchmarks/test_m8_heldout_runner.py`, `benchmarks/sota_preregistration.json` (new subject SHA **after** freeze — evaluation lane).
- **Contracts.** Task-set digest == preregistration membership; `dry_run ⇒ empirical fields null`.
- **Packages.** `benchmarks/`, `test/benchmarks/`.
- **Tests.** Enumerator golden; refuse `__*`, `.pytest_cache`; subject SHA equals `git rev-parse HEAD` of the **frozen** candidate, not of a dirty tree.
- **Adversarial falsifiers.** Drop a `__pycache__` dir into the suite; runner must not count it. Cassette arm must not write `oracle_passed` into empirical tables.
- **Metrics.** `wilson_interval_valid` may be false until n is valid; that is OK. Invalid campaigns must self-stop (already happened for B1 — keep that behavior).
- **Acceptance.** New preregistration bound to a clean tree; W-092-F0 predicate actually true (`lda identity` FRESH or documented degraded mode in the receipt).
- **Rollback.** If enumerator “fixes” by shrinking the suite without a new prereg, reject.
- **Exit gate.** Evaluation lane signs “instrument valid, no score claimed”.

### Wave 1 — Truthful task-aware completion

- **Objective.** No `completed` without bound verification; Forge cannot invent counts; default pack gated.
- **Dependencies.** Wave 0 instrument (so later scores are not compared to B1).
- **Source files.** `runtime/session.py` (`admission_required`, `_observed_test_count`, `_observe_completion_dispatch`); `agency/episode/admission_gate.py`; `agency/forge/engine.py` L309–311; pack completeness/parser.
- **Contracts.** `VerificationReceipt.passed ⇔ exit_code==0 ∧ count>0 ∧ identities match`; task class from pack policy, not substring alone.
- **Packages.** agency, runtime, packs/code-default, forge quarantine.
- **Tests.** Existing admission tests plus: default harness cannot finish empty; Forge fallback removed; greenfield vs bugfix policies explicit.
- **Adversarial.** `print("OK")` command; `exit 0` with 0 tests; modify tests to pass (expect fail until Wave 2 shield).
- **Metrics.** False-complete rate on a frozen negative suite → 0.
- **Acceptance.** W-092-F2 predicates on mechanism tests; no live score required.
- **Rollback.** If RF-95 default-harness evidence depends on exemption, successor baseline.
- **Exit gate.** Coding Max presets and default either gate or are explicitly read-only.

### Wave 2 — Durable semantic task state and restart parity

- **Objective.** Domain `SemanticTaskState` + runtime fold; resume preserves episode_id; state not in L3; 40-turn / crash continuation.
- **Dependencies.** Wave 1 (do not persist false completes).
- **Source files.** **Create** `vanguard/packages/domain/task_state.py` (**MISSING** in HEAD); fold in `runtime/task_state.py` or sibling; `app_service.py` resume; `session.py` L619–622; `agency/context/packet.py` identity fields.
- **Contracts.** FEATURE_SPEC §3 plus provenance fields already on `CodingTaskState` (discoveries, dead_ends) merged, not duplicated forever.
- **Packages.** domain, runtime, agency (view/compiler consumption), tests/contracts.
- **Tests.** `test/contracts/test_semantic_task_state.py` as specified; RF-25 still green; new test: L3 prefix stable across resume+write.
- **Adversarial.** Corrupt checkpoint blob (existing RF-96); mismatched episode_id.
- **Metrics.** Resume divergence rate 0 on hermetic fixtures.
- **Acceptance.** W-092-F3 mechanism.
- **Rollback.** If domain schema forces kernel imports, abort — domain must stay stdlib.
- **Exit gate.** One coding resume path; `CodingTaskState` becomes a view of `SemanticTaskState` or is formally deprecated in a later ticket (not both as authorities).

### Wave 3 — Progressive context and repository intelligence

- **Objective.** Epoch-bound packets; progressive L4/L5; IndexPort refresh after writes; omissions explicit.
- **Dependencies.** Wave 2 (\(\sigma\) must exist to place negative memory).
- **Source files.** `agency/context/compiler.py`, **create** `agency/context/progressive.py` *or* strategy module; `ports/index.py` epoch fields if needed (keep ranking out); `adapters/stores/repo_index.py`; `session.py` repo_map block L623–679.
- **Contracts.** FEATURE_SPEC §7 budgets as policy; INV-DELTA-5 prefix freeze.
- **Packages.** agency, ports (minimal), adapters, packs context middleware.
- **Tests.** `test/agency/test_progressive_context_compiler.py`; prefix residency tests remain green; post-write refresh falsifier.
- **Adversarial.** Index truncated=true presented as complete; force token overflow; ensure L1/L2 untouched.
- **Metrics.** Prefix-cache byte identity across turns (already a design goal); omission rate reported not hidden.
- **Acceptance.** W-092-F4 mechanism.
- **Rollback.** If progressive compiler duplicates ContextCompiler into a second loop, reject.
- **Exit gate.** Product path uses one compiler.

### Wave 4 — Greenfield and brownfield change-surface closure

- **Objective.** 2PC multi-file writes; tamper shield; implicated-set admission; greenfield oracle protocol.
- **Dependencies.** Waves 1–3.
- **Source files.** **Create** `adapters/environment/transaction.py`; **create** `runtime/governance/tamper_shield.py`; `git.py` sequential apply replaced for multi-file product writes; pack `greenfield.py`, `implicated_files.py`, `multi_file_completeness.py`.
- **Contracts.** INV-DELTA-3, INV-DELTA-4; FEATURE_SPEC §5 oracle fail-on-stub.
- **Packages.** adapters, runtime, packs, tests.
- **Tests.** Atomic rollback of 5-file set; tamper on assertion change; greenfield vacuous-oracle reject.
- **Adversarial.** Syntax error in file 4 of 5; delete a test file; greenfield completeness bypass used on a brownfield brief.
- **Metrics.** Partial-write incidents 0 on fixtures.
- **Acceptance.** Internal greenfield+brownfield fixtures pass hermetically with fake model scripts **and** one live canary **after** Wave 0 (evaluation lane).
- **Rollback.** If 2PC lives in kernel, reject.
- **Exit gate.** `GitEnvironment.apply` either calls the transaction manager or is restricted to single-file.

### Wave 5 — Strong single-agent qualification

- **Objective.** Frozen internal multi-class suite on exact subject; Wilson; missingness; cost \(\kappa\); **single** EpisodeEngine path.
- **Dependencies.** Waves 0–4.
- **Source files.** Coding Max manifests only; quarantine Forge/Chimera from the report; `apps/coding_max/facade.py` unchanged.
- **Contracts.** Preregistration: n, model id from registry, max USD, stop rules.
- **Packages.** benchmarks, packs, apps (no new intelligence).
- **Tests.** Protocol tests already green; add subject-binding of patch digest.
- **Adversarial.** Provider 5xx labeled `provider_error` not `FAIL`; harness traceback not `NO_PATCH` if no model turn occurred.
- **Metrics.** pass@1, Wilson LB, \(\kappa\), missingness table. **No** DeepSWE claim.
- **Acceptance.** Evaluation lane disposition: positive / negative / undeterminable. Negative can still close the wave.
- **Rollback.** If score requires ungated finish, rollback Wave 1 violation.
- **Exit gate.** Single-agent control exists as a numbered receipt.

### Wave 6 — Adaptive strategy and metacognition `[PROPOSAL]`

- **Objective.** Meta-controller on only if paired study vs Wave 5 control is valid (M-6.5).
- **Dependencies.** Wave 5 receipt.
- **Source files.** `runtime/meta_controller.py`, session `_consult_meta_controller`.
- **Contracts.** Cannot enlarge budget; cannot admit completion; children do not inherit.
- **Tests.** Existing M-6.5 falsifiers plus paired-study runner honesty (inconclusive stays inconclusive).
- **Adversarial.** Controller suggests `finish` without receipt — must not bypass gate.
- **Metrics.** McNemar on paired tasks; \(\Delta \kappa\).
- **Acceptance.** Valid positive **or** valid negative. Default remains off on negative.
- **Rollback.** Controller off.
- **Exit gate.** Documented disposition.

### Wave 7 — Specialist agents and topology treatments `[PROPOSAL]`

- **Objective.** Named treatments against control; merge = exterior select.
- **Dependencies.** Wave 5; Wave 6 optional.
- **Source files.** manifests localizer/reviewer/test_investigator; `runtime/topology.py`; `child_runtime.py`.
- **Contracts.** Reviewer cannot admit; parallel reads only; writes single-writer.
- **Tests.** Ablation harness; merge policy tests.
- **Adversarial.** Two conflicting patches; LLM reviewer prefers the failing one — exterior must win.
- **Metrics.** \(\Delta p\), \(\Delta \kappa\), merge-error rate.
- **Acceptance.** Each treatment independently accepted or deferred. No default swarm.
- **Rollback.** Default topology sequential single agent.
- **Exit gate.** Catalog of treatments with receipts.

### Wave 8 — Durable outer-loop campaign director `[PROPOSAL]`

- **Objective.** M-OCT-1..3 as runtime client; CAS mailboxes; CoordinationPlan.
- **Dependencies.** Wave 5; preferably Wave 7 catalog.
- **Source files.** new `runtime/campaign/` (name TBD) **not** `agency/campaign_engine.py` as a second loop; domain plan values.
- **Contracts.** \(\sum\) budget shares \(\le 1000\) per-mille; no kernel changes.
- **Tests.** Crash mid-DAG; resume remaining nodes; duplicate effect suppression.
- **Adversarial.** Director marks campaign complete while a node is ungated.
- **Metrics.** Node-level missingness; campaign success definition frozen in preregistration.
- **Acceptance.** Tech-lead profile fixture.
- **Rollback.** Disable director; inner loop remains product.
- **Exit gate.** One writer per workspace epoch.

### Wave 9 — Governed memory, skills, and learning `[PROPOSAL]`

- **Objective.** Product-optional memory behind grants; MEM-02 canary; no self-certification.
- **Dependencies.** Wave 5; M-8 mechanism already present.
- **Source files.** `runtime/memory.py` wiring **after** ADR-0100; `skill_*`; `governance/learning.py`.
- **Contracts.** Authorization precedes retrieval; held-out \(\delta \ge 0.05\); rollback executable (already tested).
- **Tests.** Reuse M-8 suite; add product-path “no retrieve without grant”.
- **Adversarial.** Promote from one trajectory; generator=evaluator.
- **Metrics.** Held-out lift, residual failures recorded.
- **Acceptance.** M-8 empirical disposition. Negative closes honestly.
- **Rollback.** Unwire retrieval; registry unsigned.
- **Exit gate.** Memory off by default in `fast` preset.

### Wave 10 — External benchmark and release qualification `[PROPOSAL]`

- **Objective.** SWE-P5 official procedures; DeepSWE v1.1 Harbor/Pier separate verifier; Scale Pro only if licensed/eligible.
- **Dependencies.** Waves 0–5 minimum; 6–9 only if their receipts are positive.
- **Source files.** Official adapters under `benchmarks/` **wrappers**, not a fork of EpisodeEngine; REL-03 container bridge.
- **Contracts.** G-3: local suites never official. Receipt subject = HEAD of the **release candidate**.
- **Tests.** Wrapper dry-run identity; no empirical fields.
- **Adversarial.** Git-history cheating (DeepSWE v1.1 deleted future history); test deletion (CTRF missing tests = fail).
- **Metrics.** Official pass@1 + CI + cost; report scaffold (`mini-swe-agent` vs Vanguard harness) **separately**.
- **Acceptance.** Independent evaluation lane. AETHER-harness scores are not comparable to Datacurve mini-swe-agent leaders without a cross-harness study.
- **Rollback.** Unpublished / withdrawn if membership or verifier isolation fails.
- **Exit gate.** M-9/M-10 still require M-8 per milestones; Wave 10 does not override G-2.

---

## 9. Sprint sequence

Implementation lane (WIP=1) and evaluation lane (WIP=1) never share a writer.

```text
Sprint S0  (eval+impl): Wave 0 enumerator + identity receipts
Sprint S1  (impl):      Wave 1 completion truth (session + forge + default pack)
Sprint S2  (impl):      Wave 2 domain SemanticTaskState + resume identity
Sprint S3  (impl):      Wave 3 progressive context + epoch
Sprint S4  (impl):      Wave 4 2PC + tamper + implicated admission
Sprint S5  (eval):      Wave 5 single-agent canary (REL-02R successor)
Sprint S6  (impl):      only if S5 valid: Wave 6 controller study harness
Sprint S7  (impl):      Wave 7 one treatment (test_investigator→implementer) + ablation
Sprint S8  (impl):      Wave 8 director MVP on fixtures
Sprint S9  (eval):      Wave 9 MEM-02 if REL runners honest
Sprint S10 (eval):      Wave 10 official wrapper, no score fishing
```

**Mapping to current board.** `tasks.md` T2–T6 ≈ S2–S4 + dialect slice of S1. Plan B inserts **S0 and S1 before T2** because completing SemanticTaskState on an ungated default pack would persist false completions. Dialect recovery (T6) can ride with S1 because it is adapter-local.

**WIP discipline.** TUI work in the dirty tree is not a third lane occupant for this program. Do not expand CMX-09 to OpenTUI.

**Independent evaluation lane.** Re-runs B1 only after S0. Never uses Forge as the Coding Max arm. Never cites LAM 100% as lift.

---

## 10. Greenfield workflow

Target: Principal Architect profile, FEATURE_SPEC §5, pack `GreenfieldPolicy`.

```text
1. Requirements extraction
   - Brief → σ.overarching_goal (immutable)
   - Explicit non-goals → constraints
   - Unknowns stay unknown (do not invent APIs)
2. Architectural contracts
   - Ports/types/schemas first (domain/pack, not kernel)
   - Public entrypoints named
3. Multi-file DAG
   - TaskSteps with dependencies (SemanticTaskState)
   - Topological order: types → impl → tests already written as failing oracles
4. Scaffold
   - Directory layout, install metadata, README
   - PATH_ESCAPE fail closed (existing GreenfieldPolicy)
5. Oracle synthesis
   - Tests MUST fail on stubs (vacuity check)
   - Freeze hashes (tamper shield)
6. Implementation turns
   - One logical step / bounded files per turn (prompt already says one file/turn on empty src — pack prompt)
   - 2PC for multi-file
7. Integration
   - Smoke command from policy
8. Entrypoint + installation
   - Documented command; fail if missing
9. Behavioral verification
   - Oracle pass + smoke; count>0
10. Maintainability
    - Settled invariants recorded in σ; no undocumented dependency
```

**Falsifiers.** Vacuous oracle; tests modified after freeze; partial scaffold left on disk after syntax failure.

---

## 11. Brownfield workflow

Target: Senior/Staff profiles; SWE-agent style localize-then-edit ([SWE-agent](https://arxiv.org/abs/2407.01489), [SWE-bench](https://arxiv.org/abs/2310.06770)) without copying their second loop.

```text
1. Reproduction
   - Run implicated tests first; record failing names (not “OK” substring)
2. Repository routing
   - IndexPort repo_map bounded; omissions listed
3. Localization
   - Traceback + symbols + callers (IndexPort), not brief regex alone
   - Optional localizer child: read-only
4. Caller/callee analysis
   - Blast(P) at depth k; truncated ⇒ more retrieve or fail
5. Hypothesis ranking
   - Record in σ.hypotheses; dead_ends on failure (already types)
6. Surgical patching
   - Single writer; 2PC; syntax preflight
7. Affected-test closure
   - Tests(Blast(P)) plus smoke
8. Integration
   - Pass-to-pass regressions (SWE-bench Pro methodology: fail-to-pass AND pass-to-pass)
9. Regression verification
   - Bound receipt to workspace digest after last write
10. Documentation debt
    - Only if behavior/contract changed; canonical owners via docs_rag --file
```

**Agentless** ([arxiv 2407.01489 companion line; Agentless paper](https://arxiv.org/abs/2407.01489)) shows localization can be a pipeline without a heavy agent. If a treatment copies Agentless, it must still emit Vanguard events and cannot bypass Kernel.dispatch.

**CodePlan** ([arxiv 2309.12499](https://arxiv.org/abs/2309.12499)) is a planning DAG — maps to SemanticTaskState steps, not a new runtime.

---

## 12. Research and explanation workflows

Same substrate, different admission policy (read-only presets already exist in AdmissionGate).

**Research.**

- Tools: read, search, IndexPort, optional memory **if granted**.
- Terminal: `task_requirements_satisfied` with citations (ledger blob digests), not a patch.
- Forbidden: mutating tests to match a narrative; claiming empirical lift from cassettes.

**Explanation.**

- Produce a bounded packet: files, symbols, omissions, epoch.
- Must fail if epoch stale.
- No `completed` that implies code changed.

Both workflows reuse EpisodeEngine. They do not fork Chimera.

---

## 13. Model routing

Registry is the only catalog. Current defaults (FACT):

| Role | Identifier | Pricing (micros / 1M tok) |
|---|---|---|
| Default / fast / coding | `deepseek/deepseek-v4-flash-0731` | 65000 / 180000 |
| Secondary flash | `z-ai/glm-5.3-flash` | 75000 / 250000 |
| Free | `openrouter/free` and other tier1 | 0 |
| Escalation (tier3) | `openai/gpt-5.6-luna` | 1000000 / 4000000 |
| Fake/cassette | `FakeModel` / cassette adapters | 0 |

**Routing policy (PROPOSAL, must be measured):**

1. **Classifier/localizer** — cheapest model that meets a localization fixture score; not assumed to be flash.
2. **Implementer** — registry `coding` alias.
3. **Escalation** — only on typed failure classes (truncation storm, repeated admission reject, budget remaining).
4. **Deterministic** — tests and dry-run; never mixed into empirical tables.

DeepSWE v1.1 (official, 2026-09-02, mini-swe-agent): `deepseek-v4-flash [max]` **53%±4%** at **$0.46/task**; `glm-5.3-flash [max]` **63%±4%** at **$0.24/task**; leaders **74%±1–4%**. These are **not** AETHER scores and use a different harness. They bound **model** competence, not Vanguard competence.

Do not hardcode “Sonnet is better at review”. If a treatment uses a second model, preregister it and ablate.

Repair `resolve_route` exception swallowing before any routing study.

---

## 14. Multi-agent policy

**Mandatory control.** Wave 5 single-agent receipt.

Candidate treatments (each a separate ticket after control):

| ID | Pipeline | Write policy | Merge |
|---|---|---|---|
| T-LI | localizer → implementer | implementer only | n/a |
| T-TI | test investigator → implementer | implementer only | n/a |
| T-IR | implementer → reviewer | implementer; reviewer advisory | reject if exterior fail, not if reviewer nack alone |
| T-AIR | architect → implementer → reviewer | implementer | same |
| T-PRL | parallel read-only localization | none | CONCAT evidence blobs |
| T-ISO | isolated candidate patches | separate worktrees | EXTERIOR_SELECT |

**Required paired ablations.** Same tasks, same model unless the treatment’s hypothesis is the model split. McNemar; missing pairs excluded (already tested).

**Not inherently superior.** Hydra/Octopus/multi-agent papers often improve coverage at quadratic cost. OpenHands ([github.com/All-Hands-AI/OpenHands](https://github.com/All-Hands-AI/OpenHands)) is a reference system, not a second Vanguard runtime.

---

## 15. Memory and skills

Reuse M-8 laws; productize only in Wave 9.

| Rule | Source in tree | Plan B |
|---|---|---|
| Authorization before retrieval | memory falsifiers | product path must call grants |
| Provenance | Discovery.source already on CodingTaskState | keep |
| Held-out lift | `test_m8_skill_lifecycle` OK this session | MEM-02 still blocked |
| Independent promotion | three authorities | no CLI “promote because it worked” |
| Rollback | executable, signed | keep |
| No self-certification | generator≠evaluator | keep |
| No single-trajectory promotion | lift tests | keep |

Skills are composition units, not prompt seasoning (`test_skills_are_load_bearing_not_decorative` exists). Turning them on without Wave 5 will confound scores.

---

## 16. Benchmark methodology

### 16.1 Task taxonomy (internal)

| Class | Examples | Notes |
|---|---|---|
| Bugfix | B1 `01_rate_limiter_lease_recovery` | needs reproducer |
| Feature | new API in existing package | change-surface |
| Migration | schema/format | staff profile |
| Refactor | behavior-preserving | pass-to-pass heavy |
| Greenfield | independent_v091 greenfield fixture is **too small** to certify | need larger frozen set |
| Research/explain | read-only | different gate |
| Invalid | `__pycache__`, missing tests, harness crash | missingness, not fail |

### 16.2 Official corpora (external; do not treat as interchangeable)

| Corpus | Size / notes | Official metric | Current frontier snapshot (2026-09-03) | AETHER status |
|---|---|---|---|---|
| DeepSWE v1.1 | 113 original tasks, 91 repos, 5 languages; isolated verifier container | pass@1, 95% CI from reruns ([paper](https://arxiv.org/abs/2607.07946), [site](https://deepswe.datacurve.ai/)) | gemini-3.8-flash 74%±1%; claude-opus-5 74%±4%; gpt-5.6-sol 73%±3%; deepseek-v4-flash 53%±4% | protocol name only |
| SWE-bench Pro public | 731 of 1865; GPL contamination barrier; ~107 LOC / 4.1 files ([Scale](https://labs.scale.com/leaderboard/swe_bench_pro_public), [arxiv 2509.16941](https://arxiv.org/abs/2509.16941)) | resolve rate fail-to-pass ∧ pass-to-pass | Scale standardized: Muse Spark 1.1 **61.50±3.10**; gpt-5.4 xHigh **59.10±3.56**. Page still narrates GPT-5 / Opus 4.1 ~23% (stale narrative vs table). Vendor-scaffold aggregators quote ~80% — **not comparable** | protocol name only |
| SWE-bench Verified | 500 human-filtered ([swebench.com/verified](https://www.swebench.com/verified), [arxiv 2310.06770](https://arxiv.org/abs/2310.06770)) | resolve rate | saturating ~95–96% under various scaffolds | not a useful north star |
| SWE-bench Live | continuously updated | time-varying | contamination/drift | optional later |
| Multi-SWE-bench | multilingual | per-language | — | not wired |
| SlopCodeBench | quality/erosion | — | — | research only |
| METR horizons | HCAST/RE-Bench/SWAA | 50%/80% duration | dashboard live; long-horizon CIs wide | competency language only |

Independent audits of DeepSWE v1.1 still report residual transparency issues ([june.kim audit](https://june.kim/auditing-deepswe-v1-1)). Plan B therefore treats even official boards as **imperfect oracles**.

### 16.3 Statistics (mandatory)

- pass@1 primary; pass@k secondary and preregistered.
- Wilson 95% CI; no interval if membership invalid.
- McNemar or exact McNemar on paired arms; exclude missing pairs.
- Hierarchical repository effects: mixed-effects or cluster-robust SEs when many tasks share a repo (SWE-bench Pro and DeepSWE both have repo clusters).
- Sequential testing: α-spend (e.g. alpha-spending function) if peeking; otherwise freeze n.
- Multiple comparisons: Bonferroni or predeclared primary endpoint (usually pass@1 vs control).
- Cost per signed pass \(\kappa\).
- Missingness classes: `provider_error`, `harness_error`, `dataset_invalid`, `undeterminable`. None convert to FAIL/PASS.
- Contamination: refuse training-split overlap for skills; DeepSWE is original-by-construction but still not a license to overclaim.
- Scaffold disclosure: mini-swe-agent vs Vanguard vs SWE-agent vs OpenHands.

### 16.4 What 60–90 means under this methodology

| Target | Interpretable as | Not interpretable as |
|---|---|---|
| 60 | Competitive with mid DeepSWE flash/pro pack **if** official DeepSWE + same effort flags | “60/100 staff engineer” |
| 70 | Overlapping weaker frontier DeepSWE configs (fable/glm-5.3/kimi ~69–70) | Scale Pro vendor 80% |
| 74–80 | Overlap with 2026-09-02 DeepSWE leaders | Guaranteed Pro public 60% |
| 90 | Stretch beyond current DeepSWE public leaders (74%) | Near-term plan exit |

SWE-bench Pro **standardized** frontier is ~60%, not ~90%. A 90% Pro public claim today would be a vendor-scaffold number or a mistake.

### 16.5 Why this session did not buy a data point

See §2.6. Additionally, OpenAI’s evaluation note: coding evals mix signal and harness noise. A $0.10 flash call cannot estimate \(p\) with useful CI (\(n=1\) Wilson width is enormous).

---

## 17. File-by-file routing

| Work | Create / modify | Tests | Canonical docs **after** acceptance (not this draft) |
|---|---|---|---|
| SemanticTaskState | **C** `vanguard/packages/domain/task_state.py` (**MISSING**) | **C** `test/contracts/test_semantic_task_state.py` | `docs/backend/architecture/runtime-execution.md`, FEATURE_SPEC promote |
| Fold | **M** `vanguard/packages/runtime/task_state.py` | `test/agency/test_coding_state.py` | same |
| Resume identity | **M** `vanguard/packages/runtime/app_service.py` | `test/runtime/test_resume_from_ledger.py`, RF-25 | runtime-execution |
| Stop L3 dump | **M** `vanguard/packages/runtime/session.py` | `test/runtime/test_context_layer_residency.py` + new | agency.md |
| Packet identity | **M** `vanguard/packages/agency/context/packet.py` | `test/agency/test_context_packet.py` | agency.md |
| Progressive policy | **C** `vanguard/packages/agency/context/progressive.py` | **C** `test/agency/test_progressive_context_compiler.py` | agency.md |
| Admission verbs | **M** `runtime/session.py`, `agency/episode/admission_gate.py` | `test/falsifiers/test_completion_gate_scope.py` | FEATURE_SPEC, agency.md |
| Forge count | **M** `agency/forge/engine.py` | `test/agency/test_forge.py` | note quarantine in backlog |
| 2PC | **C** `adapters/environment/transaction.py`; **M** `git.py` | **C** `test/runtime/test_atomic_multi_file_transaction.py` | adapters/environment docs |
| Tamper | **C** `runtime/governance/tamper_shield.py` | **C** `test/runtime/test_tamper_shield.py` | governance |
| Dialect | **M** `adapters/models/dialect.py` | **C** `test/contracts/test_dialect_recovery.py` | adapters/models |
| Index epoch | **M** `ports/index.py`, `adapters/stores/repo_index.py` | adapter index tests | ports ICD |
| Change surface | **M** `domain/transforms/repository/change_surface.py` | domain/pack tests | domain transforms |
| Pack policies | **M** `packs/code-default/**` | `test/packs/code_default/` | pack README only if contract |
| Facade | rarely **M** `apps/coding_max/facade.py` | app tests | product PRD later |
| Enumerator | **M** `benchmarks/benchmark_20_suite/runner.py` | `test/benchmarks/` | never claim official |
| Child/topology | **M** only if Wave 7 | existing M-7/RF-101 | topology docs |
| Memory wiring | **M** `runtime/memory.py` Wave 9 | M-8 suite | ADR-0100 |
| Campaign | **C** `runtime/campaign/` Wave 8 | new workflow tests | architecture after M-OCT |
| Kernel | **avoid** | TCB tests | SPEC only if invariant |
| Clients TUI | **out of scope** | — | — |

`docs_rag --file` owners observed: EpisodeEngine/ContextCompiler → `docs/backend/architecture/agency.md`; HarnessSession/CodingTaskState → `docs/backend/architecture/runtime-execution.md`.

---

## 18. Initial engineering tickets

Dependency key: `requires:`. Status: all `PROPOSED` unless noted.

### Ticket 01 — Enumerator membership digest
- **Files:** `benchmarks/benchmark_20_suite/runner.py`; `test/benchmarks/test_b20_membership.py` (create)
- **Requires:** none
- **Falsifier:** `__pycache__` directory is not a task; digest matches frozen list of 20 names
- **Done when:** B1-style INVALID cannot recur without stop

### Ticket 02 — Subject SHA on every empirical JSON
- **Files:** benchmark writers; `benchmarks/protocols.py`
- **Requires:** 01
- **Falsifier:** missing `subject_sha` ⇒ receipt refused (`test_sota_protocols` already has binding — extend to B20 writer)

### Ticket 03 — Dry-run empirical field ban
- **Files:** runners; `test/benchmarks/test_m8_bundle.py` already has a cousin
- **Requires:** none
- **Falsifier:** dry-run JSON has null pass/cost

### Ticket 04 — Remove default admission exemption
- **Files:** `runtime/session.py` `ADMISSION_GATE_EXEMPT`
- **Requires:** none
- **Falsifier:** `vg-code-default` + `finish` + no patch ⇒ not completed
- **Rollback:** if a named compatibility harness must stay exempt, shrink set with a recorded governance note — do not restore lex+default silently
- **FACT (lock HEAD `66aa7a3c`).** The exemption is pinned, not accidental. [`test/falsifiers/test_completion_gate_scope.py`](../test/falsifiers/test_completion_gate_scope.py) asserts `vg-code-default` ∉ `ADMISSION_GATED_HARNESSES` and documents that frozen M-2 falsifiers compose bare finishes through the default harness. Live `admission_required` (`runtime/session.py` L127–138) exempts `vg-code-default` / `vg-code-lex` via `ADMISSION_GATE_EXEMPT`; RF-25 cold-continuation evidence is on that product path. **Implementation of this ticket remains `[PROPOSAL]`** and requires a **successor baseline** for RF-25 / M-2 / `test_completion_gate_scope.py` before the exemption is removed — do not silently retarget those tests.

### Ticket 05 — Delete unused `ADMISSION_GATED_HARNESSES` or make it the only source
- **Files:** `session.py`; `test/falsifiers/test_completion_gate_scope.py`
- **Requires:** 04
- **Falsifier:** one function decides gating; name set cannot drift

### Ticket 06 — Remove Forge `test_count = 1`
- **Files:** `agency/forge/engine.py` L309–311; `test/agency/test_forge.py`
- **Requires:** none (can parallel 04)
- **Falsifier:** exit 0 + empty output ⇒ not passed

### Ticket 07 — Typed verification command subject
- **Files:** `session.py` `_observe_completion_dispatch`; admission_gate
- **Requires:** 04
- **Falsifier:** `python3 -c 'print("OK")'` is not a verification subject

### Ticket 08 — Parse pytest `N passed` without inventing counts
- **Files:** `_observed_test_count`; pack `test_output_parser.py` if present
- **Requires:** 07
- **Falsifier:** unittest `Ran 0 tests` ⇒ count 0; pytest `0 passed` ⇒ 0

### Ticket 09 — Domain SemanticTaskState
- **Files:** create `domain/task_state.py` (**MISSING** in HEAD); FEATURE_SPEC §3
- **Requires:** none technically; **schedule after** 04 so we do not persist false completes
- **Falsifier:** `test/contracts/test_semantic_task_state.py` as specified
- **FACT (lock HEAD `66aa7a3c`).** `vanguard/packages/domain/task_state.py` is **MISSING**. Live fold is [`runtime/task_state.py`](../vanguard/packages/runtime/task_state.py) `CodingTaskState` + `fold_task_state`. This ticket remains **`[PROPOSAL]`**: merge FEATURE_SPEC `SemanticTaskState` with `CodingTaskState` per B §6.12 (this lattice **wins** over Plan A §6.2’s 17 domain types, which stay as a competing `[PROPOSAL]` in A). Do not invent a second task-state authority.

### Ticket 10 — Runtime fold of SemanticTaskState
- **Files:** `runtime/task_state.py`
- **Requires:** 09
- **Falsifier:** fold monotonic revision; unknown events ignored; `"test" in action.lower()` removed or replaced

### Ticket 11 — Preserve episode_id on resume
- **Files:** `app_service.py` L385–389
- **Requires:** 10
- **Falsifier:** resumed events use original episode_id

### Ticket 12 — Stop dumping resume_state into L3
- **Files:** `session.py` L619–622; compiler
- **Requires:** 10
- **Falsifier:** L3 prefix identity; L4 contains σ digest

### Ticket 13 — Populate ContextPacket resume identity
- **Files:** `packet.py`; session orientation block
- **Requires:** 12
- **Falsifier:** `validate_resume_identity` fails on policy mismatch

### Ticket 14 — WorkspaceEpoch
- **Files:** ports/index.py (additive fields); repo_index adapter; session
- **Requires:** 13
- **Falsifier:** write ⇒ epoch change ⇒ packet invalid until refresh

### Ticket 15 — Progressive L4/L5 strategy
- **Files:** create `agency/context/progressive.py` **or** `compaction.py` strategy; `compiler.py`
- **Requires:** 12, 14
- **Falsifier:** settled invariants never truncated; FEATURE_SPEC budget caps

### Ticket 16 — Index refresh after patch.apply
- **Files:** session observe path; pack IndexToolkit
- **Requires:** 14
- **Falsifier:** callers after write include new symbol or explicit omission

### Ticket 17 — Atomic multi-file transaction manager
- **Files:** create `adapters/environment/transaction.py`; `git.py`
- **Requires:** 08 (verification still honest)
- **Falsifier:** 5-file syntax fail rolls back all

### Ticket 18 — TestTamperShield with IndexPort enumeration
- **Files:** create `runtime/governance/tamper_shield.py`
- **Requires:** 17 for greenfield freeze timing; 14 for file list
- **Falsifier:** assertion edit ⇒ admission reject; `Path.glob("test/**")` is insufficient — use enumerated tests

### Ticket 19 — Greenfield oracle vacuity
- **Files:** pack greenfield policy
- **Requires:** 18
- **Falsifier:** tests that pass on stubs rejected

### Ticket 20 — Brownfield implicated-set fail-closed
- **Files:** `multi_file_completeness.py`; change_surface.py
- **Requires:** 16
- **Falsifier:** empty primary + coverage_ratio 1.0 cannot admit; greenfield bypass cannot apply to `bugfix` brief

### Ticket 21 — Dialect typed failure classes
- **Files:** `dialect.py`; create `test/contracts/test_dialect_recovery.py`
- **Requires:** none (parallel)
- **Falsifier:** truncated JSON, DeepSeek fence, XML tool tags classified without false `ok`

### Ticket 22 — Fail-closed model resolve
- **Files:** `routing.py` L42–44; harness.yaml aliases
- **Requires:** 21 optional
- **Falsifier:** `deepseek-v4-flash` without `-0731` either aliases or errors, never silent unknown

### Ticket 23 — Quarantine Forge/Chimera from Coding Max reports
- **Files:** benchmark arm lists; `runtime/root.py` exports remain but labeled experimental
- **Requires:** 06
- **Falsifier:** Wave 5 preregistration arms ⊆ `{vg-code-fast,balanced,max}`

### Ticket 24 — Patch identity on results
- **Files:** B20 result schema; session evidence
- **Requires:** 02
- **Falsifier:** PASS row without patch digest refused

### Ticket 25 — Missingness taxonomy in runners
- **Files:** BAAC + B20 diagnosis mapping
- **Requires:** 01, 02
- **Falsifier:** traceback-only row is `harness_error` not `FAIL`

### Ticket 26 — Frozen Wave 5 preregistration
- **Files:** new prereg JSON bound to candidate SHA after S4
- **Requires:** 01–25 as applicable
- **Falsifier:** n, models, λ, stop rule frozen before first paid call

### Ticket 27 — Single-agent canary execution (eval lane)
- **Files:** none in product if wrappers exist
- **Requires:** 26
- **Falsifier:** spend ledger disposition in {POSITIVE, NEGATIVE, UNDETERMINABLE, INVALID}; never silent

### Ticket 28 — Meta-controller paired study harness
- **Files:** `paired_evaluation.py`; meta_controller
- **Requires:** 27 control receipt
- **Falsifier:** inconclusive ≠ negative; budget cannot grow

### Ticket 29 — Treatment T-TI ablation
- **Files:** manifests; topology
- **Requires:** 27
- **Falsifier:** reviewer/investigator cannot call patch.apply; McNemar table includes missingness

### Ticket 30 — Isolated patch EXTERIOR_SELECT
- **Files:** child_runtime; git worktrees
- **Requires:** 27, 17
- **Falsifier:** selector is test verdict; LLM preference ignored

### Ticket 31 — Campaign director fixture
- **Files:** create `runtime/campaign/` (Wave 8)
- **Requires:** 27
- **Falsifier:** crash after node 3; resume nodes 4–8 without duplicate writes

### Ticket 32 — Memory grant on product path
- **Files:** `runtime/memory.py` wiring
- **Requires:** 27; ADR-0100
- **Falsifier:** retrieve without grant denied; MEM-02 still independent

### Ticket 33 — Official DeepSWE wrapper (no score fishing)
- **Files:** `benchmarks/` Harbor/Pier adapter
- **Requires:** 27; REL-03
- **Falsifier:** wrapper dry-run produces no pass%; committed-patch-only grading

### Ticket 34 — WorkflowScheduler lease honesty
- **Files:** `workflow_scheduler.py` L225–242
- **Requires:** none (lattice hygiene)
- **Falsifier:** parallel path either uses kernel leases or is disabled in product profiles

### Ticket 35 — TCB and boundary freeze
- **Files:** none expected
- **Requires:** each impl ticket
- **Falsifier:** `check_tcb_budget.py` still PASS; `check_boundaries.py`; domain-blindness PASS

Tickets 01–08 are the true critical path for long-horizon **truth**. Tickets 09–20 are the critical path for long-horizon **competence**. 21–25 are hygiene. 26–27 are the first honest score. 28–35 are gated. Waves 6–10 and tickets 28–35 are **`[PROPOSAL]`**; this lock does not authorize them.

---

## 19. Risks

| Risk | Why it is real here | Mitigation | Rollback |
|---|---|---|---|
| Architecture sprawl | Forge/Chimera already second loops; Octopus/Hydra drafts want a third | One EpisodeEngine product path; quarantine | Delete product wiring, keep modules experimental |
| God-object growth | `HarnessSession` ~1000 lines; `EpisodeEngine` ~900 | New behavior as injected policies, not more branches | Split only with tests; no drive-by rewrite |
| Benchmark gaming | B1 `__pycache__`; Forge count=1; vendor vs Scale Pro | Wave 0–1; scaffold disclosure | INVALID stop |
| False-positive completion | default exemption | Tickets 04–08 | Restore exemption only with named harness + test |
| Multi-agent cost explosion | DeepSWE leaders already $2–$26/task on mini-swe-agent | Control first; \(\kappa\) primary | Treatments off |
| Context compression loss | structured consolidate keyword scrape | Progressive invariants | Disable new strategy |
| Stale repository intelligence | map at session start | Epoch + refresh | Fail closed on stale |
| Self-reinforcing memory | M-8 mechanism exists, product wiring tempting | Wave 9 after control | Unwire |
| Restart divergence | L3 dump; synthesized episode_id | Tickets 11–13 | Disable resume product claim |
| Evaluator coupling | local tests vs signed daemon | Lattice of confidence | Official claims require official eval |
| Overclaiming professional equivalence | user asked senior/staff/principal/lead | Profiles are suites, not HR | Ban job-title marketing |
| Documentation drift | active.md = tasks.md; W-092-F0 DONE vs LDA STALE; FEATURE_SPEC files missing | This draft records contradictions; do not “fix” canonical docs in this task | Canonical updates after implementation |
| LIM technique import | README forbids LIM as authority | Reimplement behind ports | Reject LIM calls from runtime |
| Dirty worktree confusion | TUI + runtime profile edits exist | Do not touch | — |
| Spending into noise | $0.10 cannot estimate p | No paid run this session | — |
| Kernel contamination | FEATURE_SPEC discipline is good; drafts sometimes ignore it | TCB 1386/1438 | revert kernel diffs |
| Adapter importing agency | hexagonal rule | `check_boundaries.py` | revert |
| Greenfield tamper gap | agents write tests then change them | Ticket 18–19 | fail closed |
| Parallel writes | WorkflowScheduler thread pool | Ticket 34 | sequential only |
| Stale Scale page narrative | ~23% GPT-5 story vs 61.5% table | Cite table + date | Re-fetch at Wave 10 |

---

## 20. References

### 20.1 Repository-relative

- [`VISION.md`](../VISION.md)
- [`AGENTS.md`](../AGENTS.md)
- [`README.md`](../README.md)
- [`docs/SPEC.md`](../docs/SPEC.md)
- [`docs/decisions.md`](../docs/decisions.md)
- [`docs/execution/active.md`](../docs/execution/active.md)
- [`docs/execution/milestones.md`](../docs/execution/milestones.md)
- [`docs/execution/backlog.md`](../docs/execution/backlog.md)
- [`docs/execution/FEATURE_SPEC.md`](../docs/execution/FEATURE_SPEC.md)
- [`docs/execution/tasks.md`](../docs/execution/tasks.md)
- [`docs/backend/architecture/agency.md`](../docs/backend/architecture/agency.md)
- [`docs/architecture/workflows/end-to-end-execution.md`](../docs/architecture/workflows/end-to-end-execution.md)
- [`vanguard/packages/agency/episode/engine.py`](../vanguard/packages/agency/episode/engine.py)
- [`vanguard/packages/agency/episode/admission_gate.py`](../vanguard/packages/agency/episode/admission_gate.py)
- [`vanguard/packages/agency/context/compiler.py`](../vanguard/packages/agency/context/compiler.py)
- [`vanguard/packages/agency/context/packet.py`](../vanguard/packages/agency/context/packet.py)
- [`vanguard/packages/agency/forge/engine.py`](../vanguard/packages/agency/forge/engine.py)
- [`vanguard/packages/runtime/session.py`](../vanguard/packages/runtime/session.py)
- [`vanguard/packages/runtime/task_state.py`](../vanguard/packages/runtime/task_state.py)
- [`vanguard/packages/runtime/app_service.py`](../vanguard/packages/runtime/app_service.py)
- [`vanguard/packages/runtime/child_runtime.py`](../vanguard/packages/runtime/child_runtime.py)
- [`vanguard/packages/runtime/meta_controller.py`](../vanguard/packages/runtime/meta_controller.py)
- [`vanguard/packages/runtime/topology.py`](../vanguard/packages/runtime/topology.py)
- [`vanguard/packages/apps/coding_max/facade.py`](../vanguard/packages/apps/coding_max/facade.py)
- [`vanguard/packages/adapters/models/models_registry.json`](../vanguard/packages/adapters/models/models_registry.json)
- [`vanguard/packages/ports/index.py`](../vanguard/packages/ports/index.py)
- [`vanguard/packages/domain/transforms/repository/change_surface.py`](../vanguard/packages/domain/transforms/repository/change_surface.py)
- [`benchmarks/protocols.py`](../benchmarks/protocols.py)
- [`benchmarks/sota_preregistration.json`](../benchmarks/sota_preregistration.json)
- [`benchmarks/sota_spend_ledger.json`](../benchmarks/sota_spend_ledger.json)
- [`.draft/DEVELOPMENT_FINAL_PLAN.md`](DEVELOPMENT_FINAL_PLAN.md) (non-authority; different SHA)
- [`.draft/todo/SOTA_CODING_HARNESS_ENGINEERING_ROADMAP.md`](todo/SOTA_CODING_HARNESS_ENGINEERING_ROADMAP.md)
- [`.draft/todo/development_plan_guidelines_0209.md`](todo/development_plan_guidelines_0209.md)
- [`.draft/HYDRA_MULTI_AGENT_TOPOLOGY_AND_EMERGENT_AGENCY.md`](HYDRA_MULTI_AGENT_TOPOLOGY_AND_EMERGENT_AGENCY.md)
- [`.draft/SONNET_SUPER_AGENT.md`](SONNET_SUPER_AGENT.md)
- [`docs/research/theory/SOTA_AGENTIC_CODING_HARNESS_ENGINEERING_TREATISE.md`](../docs/research/theory/SOTA_AGENTIC_CODING_HARNESS_ENGINEERING_TREATISE.md)
- [`docs/research/coding_harness/VANGUARD_FRONTIER_SWE_BENCH_AND_AGENTIC_METAFRAMEWORK_REPORT.md`](../docs/research/coding_harness/VANGUARD_FRONTIER_SWE_BENCH_AND_AGENTIC_METAFRAMEWORK_REPORT.md)
- [`docs/research/coding_harness/VANGUARD_VS_LIM_INSIGHTS_SOTS_TECHNIQUES.md`](../docs/research/coding_harness/VANGUARD_VS_LIM_INSIGHTS_SOTS_TECHNIQUES.md)
- [`docs/reports/reviews/electroweak_v092/octopus/agents/long-horizon-context-engine.md`](../docs/reports/reviews/electroweak_v092/octopus/agents/long-horizon-context-engine.md)
- [`docs/reports/reviews/electroweak_v092/octopus/agents/meta-conductor.md`](../docs/reports/reviews/electroweak_v092/octopus/agents/meta-conductor.md)
- [`docs/reports/reviews/electroweak_v092/octopus/consolidation/outer-loop-orchestrator.md`](../docs/reports/reviews/electroweak_v092/octopus/consolidation/outer-loop-orchestrator.md)
- [`docs/reports/reviews/electroweak_v092/octopus/consolidation/outer-loop-coding-patterns.md`](../docs/reports/reviews/electroweak_v092/octopus/consolidation/outer-loop-coding-patterns.md)
- [`.agents/skills/lda-navigator/SKILL.md`](../.agents/skills/lda-navigator/SKILL.md)

### 20.2 External

- DeepSWE leaderboard (fetched 2026-09-03): <https://deepswe.datacurve.ai/>
- DeepSWE v1.1 blog: <https://deepswe.datacurve.ai/blog/deepswe-v1-1>
- DeepSWE paper: <https://arxiv.org/abs/2607.07946>
- DeepSWE GitHub: <https://github.com/datacurve-ai/deep-swe>
- DeepSWE v1.1 audit (independent, residual issues): <https://june.kim/auditing-deepswe-v1-1>
- SWE-bench Pro Scale public leaderboard (fetched 2026-09-03): <https://labs.scale.com/leaderboard/swe_bench_pro_public>
- SWE-bench Pro paper: <https://arxiv.org/abs/2509.16941>
- SWE-bench: <https://github.com/SWE-bench/SWE-bench> · <https://arxiv.org/abs/2310.06770>
- SWE-bench Verified: <https://www.swebench.com/verified>
- METR time horizons: <https://metr.org/time-horizons/>
- METR long-task paper: <https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/>
- OpenAI: separating signal from noise in coding evals: <https://openai.com/index/separating-signal-from-noise-coding-evaluations/>
- SWE-agent: <https://arxiv.org/abs/2407.01489>
- CodePlan: <https://arxiv.org/abs/2309.12499>
- OpenHands: <https://github.com/All-Hands-AI/OpenHands>
- mini-SWE-agent: <https://github.com/SWE-agent/mini-swe-agent>
- RFC 8785 JCS: <https://www.rfc-editor.org/rfc/rfc8785>
- Harbor verifier environments (DeepSWE v1.1 grading): <https://www.harborframework.com/docs/tasks#verifier-environment-shared-vs-separate>
- Additional papers named in the task prompt for later Wave 10 literature control: <https://arxiv.org/abs/2603.24755>, <https://openreview.net/forum?id=mXpq6ut8J3>, <https://arxiv.org/abs/2510.00615>, <https://arxiv.org/abs/2608.06503>, <https://arxiv.org/abs/2504.21798>

---

## 21. Session validation appendix

### 21.1 Navigation limitations (repeat)

| When | LDA index SHA | Subject HEAD | Freshness |
|---|---|---|---|
| **Lock-time row (2026-09-03)** | `66aa7a3c0c31` | `66aa7a3c0c31cb68a2c0387a1ddf237c80084253` | `FRESH` |
| Planning-session snapshot | `7e08462c2cbb` | `ebad36e675f0eab6c4635851a91423f5a6541290` | `STALE` |

**Lock-time FACT.** `uv run lda identity --json` / `lda doctor --json` report `freshness_vs_head=FRESH`, `index_healthy=true`, `status=HEALTHY` at HEAD `66aa7a3c0c31`. The original bullets below are the **planning-session snapshot** and remain as forensic text.

- LDA index SHA `7e08462c2cbb` ≠ HEAD `ebad36e675f0eab6c4635851a91423f5a6541290` (`STALE`).
- Doctor `HEALTHY` describes the stale populated index, not HEAD-binding.
- `docs_rag` task query routed to frontend PRDs; `--file` routing worked for agency engine.
- `dev_context_logs/context_summary.md` bound to `7d46c7f…` / other branch.
- Knowledge `report.json` dated 2026-08-30 and dirty in worktree.
- Index **not** rebuilt.

### 21.2 Tests actually executed

16 + 52 = **68 unittest cases, all OK**. Commands in §2.3. `just verify` not run. `check_tcb_budget.py` PASS 1386/1438. `check_domain_blindness.py` PASS.

### 21.3 Paid spend

**$0.00** this session. Historical B1 spend `$0.002037315` is not this session and is INVALID.

### 21.4 Scope confirmation (to be re-checked after write)

This task’s intended unique created file:

`/home/rock-dev/Coding/cognitive-framework/.draft/DEVELOPMENT_FINAL_PLAN_B.md`

No production code, tests, canonical docs, generated indexes, package metadata, benchmark artifacts, or existing drafts were to be modified.

---

## Appendix A — Algorithms (normative for implementers, still PROPOSAL)

### A.1 Completion admission (target)

```text
function ADMIT_FINISH(σ, receipt, harness):
    if harness.verbs does not contain patch.apply and task_class in READ_ONLY:
        return task_requirements_satisfied(σ)
    if σ.modified_files is empty:
        return REJECT MISSING_SOURCE_PATCH
    if σ.modified_files ⊈ σ.inspected_files:
        return REJECT MODIFIED_FILE_NOT_INSPECTED
    if receipt is null or receipt.count == 0 or receipt.exit_code != 0:
        return REJECT VERIFICATION_FAILED
    if receipt.workspace_digest != epoch.treeHash:
        return REJECT VERIFICATION_STALE
    if receipt.command_digest not in σ.verification_plan:
        return REJECT VERIFICATION_FOREIGN_SUBJECT
    if tamper_shield broken:
        return REJECT TEST_TAMPER
    if pack.completion_policy fails (implicated, greenfield, …):
        return REJECT TASK_REQUIREMENTS_UNSATISFIED
    return ADMIT
```

This is the existing AdmissionGate plus epoch, command digest, tamper, and pack policy — not a new engine.

### A.2 Turn compile (target)

```text
function COMPILE(σ, epoch, budget):
    prefix ← freeze(L1, L2, L3_environment_without_σ)
    inv  ← encode(σ.goal, σ.active_step, σ.settled_invariants)  # never compact
    neg  ← encode(σ.dead_ends, σ.falsified_hypotheses)
    slice ← ast_slices(σ.active_files, epoch)                   # omit if stale
    stubs ← index.stubs(neighbors(slice), budget_remainder)
    packet ← ContextPacket(..., omissions=..., repository_identity=epoch)
    validate_resume_identity(packet, last_packet)
    return prefix ∥ pack(inv, neg, slice, stubs, budget)
```

### A.3 2PC write (target)

```text
function COMMIT(mutations):
    preimage ← read_all(paths)
    for m in mutations:
        if python(m): ast.parse(m.content) else syntax_check_lang(m)
    if any fail: return Err, disk unchanged
    try:
        write_all(mutations)
    catch:
        restore(preimage)
        return Err
    return Receipt(tree_before, tree_after)
```

### A.4 Campaign step (target)

```text
function RUN_NODE(plan_node, cas):
    inputs ← [cas.get(d) for d in plan_node.needs]
    result ← Runtime.run_composed(plan_node.manifest, task(inputs))
    if result.outcome not in {completed, abandoned, undeterminable}:
        record missingness
    cas.put(result.artifacts)
    return result
```

Unknown outcomes stay `undeterminable` (`child_runtime.py` already maps instrument_error that way — MECHANISM).

---

## Appendix B — Dependency graph (waves)

```text
W0 truth
 └─ W1 completion
     └─ W2 semantic state + resume
         └─ W3 progressive context + epoch
             └─ W4 greenfield/brownfield closure
                 └─ W5 single-agent qualification ── control receipt
                      ├─ W6 meta-controller (optional)
                      ├─ W7 treatments (optional, needs W5)
                      │    └─ W8 campaign director
                      ├─ W9 memory (optional, needs W5 + M-8 empirical)
                      └─ W10 official benches (needs W5; W6–9 only if positive)
```

No edge from W7 to W5 in reverse. No edge that lets Forge define W5.

---

## Appendix C — Why Plan B is not Plan A copied

[`.draft/DEVELOPMENT_FINAL_PLAN.md`](DEVELOPMENT_FINAL_PLAN.md) is bound to `7e08462c2cbb…`. This file is bound to `ebad36e675f0…` plus this session’s 68 tests, TCB 1386, official DeepSWE/Scale fetches on 2026-09-03, and the observation that FEATURE_SPEC modules are **still missing**. Plan A’s reliability-first thesis is retained because **current source still supports it**, not because the earlier draft is authority.

**Lock-time addendum (2026-09-03, HEAD `66aa7a3c0c31`).** A, B, and v2 are now a locked triad: A = law, B = ground truth (this file, tickets 01–35), v2 = architecture catalog. YAML no longer says `does_not_modify` A; complements are A and v2. The `ebad36e` / LDA `STALE` binding above remains the planning-session snapshot. FEATURE_SPEC modules remain **MISSING** at lock HEAD.

**Lock-time addendum (HEAD `66aa7a3c0c31`).** This file is now also bound to lock HEAD `66aa7a3c0c31` / LDA `FRESH`. The `ebad36e` binding above is the planning-session snapshot, kept. Complements are A (law) and v2 (architecture), not a merged fourth plan. FEATURE_SPEC-named modules remain **MISSING** at lock HEAD.

---

## Appendix D — Operator one-pager

If only one sprint can be staffed after this draft:

1. Ticket 01–08 (truth).
2. Ticket 09–13 (state/resume).
3. Do not enable multi-agent, memory, or DeepSWE spend.

That sequence is the smallest path that can eventually support senior-developer **internal** qualification. Staff/principal/lead profiles and 60–90 public bands remain gated on Waves 5 and 10.

---

## 22. Live tool/verb inventory (lock HEAD `66aa7a3c`)

Appended at lock; does **not** replace §3. **FACT** from pack YAML and toolkit source on HEAD `66aa7a3c`.

Harness [`packs/code-default/harness.yaml`](../packs/code-default/harness.yaml) declares:

| Verb | Pack source | Notes (FACT) |
|---|---|---|
| `fs.read` | `harness.yaml` capabilities; `plugins/fs.yaml`; `toolkits/fs_toolkit.py` | Windowed: optional `start_line` / `end_line` in schema; full-file digest if omitted |
| `fs.search` | `harness.yaml`; `plugins/fs.yaml`; `FsToolkit` | Pattern search over workspace files |
| `fs.list` | `plugins/fs.yaml` + `FsToolkit` (not listed on the harness.yaml capability block) | Glob list; kernel classifier treats `fs.list` as observation |
| `patch.apply` | `harness.yaml`; `plugins/ast-patch.yaml`; `toolkits/ast_patch.py` | Sequential `GitEnvironment.apply`; post-write `ast.parse` is observation-only |
| `proc.exec` | `harness.yaml`; `plugins/terminal.yaml`; `toolkits/terminal_runner.py` | Allowlisted `git,pytest,ruff,python3` |

**Index toolkit.** [`packs/code-default/plugins/index.yaml`](../packs/code-default/plugins/index.yaml) still declares capability verb **`fs.read`**. `IndexToolkit` in `toolkits/repo_map.py` also exposes `index.refresh`. Ranking stays out of `IndexPort` (observation-only). Pack also has `multi_file_completeness.py` and `GreenfieldPolicy` (MECHANISM; see §3.4).

**Facade (MECHANISM).** `CodingMaxFacade`: `run` / `status` / `resume` / `evidence` / `cost`; presets `fast|balanced|max`.

**Still MISSING in HEAD `66aa7a3c` (keep as `[PROPOSAL]`).** `transaction.py` 2PC, `tamper_shield.py`, `progressive.py`, `WorkspaceEpoch`, `agency/prediction/`, `runtime/event_store.py`, `adapters/index/`. Event store owner is `adapters/stores/event_store.py`; index owner is `adapters/stores/repo_index.py`. Edit/2PC mechanics live in **v2**; law/profiles live in **A**.

---

## 23. Product target loop

Appended at lock; does **not** replace §3.2 / §6.1. Product stages (SOTA suggestion):

```text
INGEST → DISCOVER → PLAN → EDIT → VERIFY_TARGETED → RECOVER → VERIFY_BROAD → COMPLETE
```

**FACT.** Stage transitions follow receipts, not conversational `finish`. Live inner loop is `ContextCompiler` freeze of L1–L3 at construction, then `EpisodeEngine`: observe → propose → `recover_proposal` → `Kernel.dispatch` → ingest (`agency/episode/engine.py`). Compile is **not** a step inside `EpisodeEngine`.

**FACT.** `admission_required` exempts `vg-code-default` / `vg-code-lex`, else `"patch.apply" in verbs`. `ADMISSION_GATED_HARNESSES` is unused in runtime. `VerificationReceipt.passed` ⇔ `exit_code == 0 and executed_test_count > 0`. Session `_observed_test_count` returns 0 if unparseable. Forge still sets `test_count = 1` on green-empty.

**Pointer.** Reliability order and competency profiles: A. Tickets 01–35 and lattice: this file. 2PC / AST / later phenotypes: v2 as `[PROPOSAL]` except sequential git apply + post-write `ast.parse` (MECHANISM).

---

## Appendix E — Cross-link matrix (locked triad)

Identical appendix in A, B, and v2. Duplication is required so no file is a stub.

| Concern | Canonical write-up | Competing variants kept as `[PROPOSAL]` |
|---|---|---|
| Reliability order | A §0, B §8 | v2 HYDRA-first topologies |
| Live gaps / tickets | B §4, §18 | A §31 (less precise on exemption); v2 §8 IDs |
| Lattice placement | B §6.12 | A §6.2–6.3 port explosion; v2 new packages |
| L1–L5 + σ | v2 §3 + B §4.4 | dumping σ into L3 (current code, not target) |
| 2PC / AST | v2 §4.2 adapter | v2 §4.3 kernel hook (rejected) |
| Completion policy | A §9.4 per class | v2 I-1 universal signed finish |
| Forge/Chimera | B §3.5 quarantine | v2 Head 3 Chimera as product |
| Director / HYDRA | v2 §7, A waves 7–8, B waves 7–8 | default swarm |
| Mutation 0.80 | v2 §5.4 | as admission law |
| CLI | A appended operator surface | TUI visual design (A non-goal) |

---

*End of Plan B. Non-authoritative. Source and tests win. Locked triad 2026-09-03 / HEAD `66aa7a3c0c31` / LDA `FRESH`.*
