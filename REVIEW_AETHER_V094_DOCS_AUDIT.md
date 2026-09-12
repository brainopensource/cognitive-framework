# Executive Engineering Briefing: Execution Runway & Baseline Status (v0.9.4 Audit)

**To:** Engineering Director  
**From:** Principal Systems Architect / Ground-Truth Auditor  
**Date:** 2026-09-12  
**Subject:** Ground-Truth Baseline, Documentation Architecture, and Runway State  
**Current HEAD Commit:** `41429f91` (`feat/aether-framework-electroweak-canonical-agents`)  
**Historical Anchor:** `24712896` (T-26a / T-51 Initial Landing)  
**Repository State:** Zero test regressions on canonical suites; path hygiene and boundary checks PASS; 6 CI documentation budget ceilings failing; T-51 holdout verification currently failing on oracle digest mismatch.

---

## 1. Ground-Truth Verification of Briefing Claims

A deep audit was performed comparing the draft briefing against the actual source tree in `vanguard/packages/`, the benchmark suites in `benchmarks/` and `test/benchmarks/`, and the five runway documents in `docs/execution/`.

### Verified Facts vs. Outdated Delta

| Briefing Claim | Verified Ground-Truth State | Verdict |
|---|---|---|
| **HEAD Commit: `24712896`** | HEAD is at `41429f91`. Commit `24712896` is an ancestor commit that landed T-26a and T-51. Since then, 6 subsequent commits landed T-52 (`53e7bf3c`), accepted T-52 (`4a24f2c9`), and landed T-26b runner integration (`2fb7bd58`). | **EVOLVED / UPDATED** |
| **TCB Budget $\le 1438$ LOC** | `check_tcb_budget.py` confirms **1386 logical LOC** across 9 files in `vanguard/packages/kernel/` (52 LOC headroom). Hexagonal boundaries pass across all 833 source files. | **TRUE (100%)** |
| **T-26a Landed** | Implemented manifest admission boundary (`control.py:125`), typed refusals (`control.py:58`), population reconciliation (`evidence.py:117`), and report admission (`metrics.py:149`). | **TRUE (100%)** |
| **T-51 Holdout Corpus** | 30-task L2 holdout suite defined in `benchmarks/ladder/suite.json`. However, `test_control_corpus.py` actively fails (2 of 8 tests) with `ValueError: oracle digest mismatch` on hardened tasks 04 & 05. | **TRUE (BLOCKED)** |
| **T-52 Wilson & Cost $\kappa$** | Landed in `53e7bf3c` and accepted by independent review in `4a24f2c9`. Scheduled slots reconciled, missingness separated from denominator, $\kappa$ usage provenance enforced. | **ACCEPTED (A)** |
| **T-26b Runner Gate** | Landed in `2fb7bd58` routing reports through product runner; independent review is currently blocked awaiting T-51 holdout reacceptance. | **BLOCKED (B)** |
| **Write-Landing Defect (BLOCK-T27)** | Multi-file tool executions in `runtime/entrypoint.py` / agency drop writes on candidate workspaces, leaving files untouched. Addressed by Director Charter II (T-130 / RUN-13). | **TRUE (DIVERGENT)** |
| **CI Doc Budget Ceilings** | `tools/linters/check_doc_budgets.py` currently fails on 6 documents exceeding their line limits (`tasks.md`, `agency.md`, `runtime-execution.md`, `runtime-service.md`, `PRD_AETHER_DESKTOP.md`, `PRD_FRONTEND_PLATFORM.md`). | **TRUE (FAILING)** |

---

## 2. Structure of the Authoritative Runway Documents (`docs/execution/`)

Operational authority in this repository is strictly partitioned into **exactly five canonical runway files** under `docs/execution/`. No additional plans, markdown files, or scratch registries are authorized:

| Document | Absolute Filepath | Documented Purpose & Authority |
|---|---|---|
| **`tasks.md`** | `docs/execution/main/tasks.md` | **Active Task Registry:** Flat work tree by context. Defines authoritative state (`READY` vs `BLOCKED`), task ownership, strict disjoint file leases, acceptance criteria, and explicit `requires:` dependency edges. |
| **`spec.md`** | `docs/execution/main/spec.md` | **Normative Law & Delta Spec:** Compact, typed schemas, operational invariants (RUN-01 through RUN-13), error matrices, and boundary contracts. |
| **`milestones.md`** | `docs/execution/main/milestones.md` | **Milestone Gates:** Stable TARGET outcomes and release predicates (M-0 to M-10 plus MS-* overlay, including MS-CONTROL). Free of calendar schedules. |
| **`backlog.md`** | `docs/execution/main/backlog.md` | **Capability Inventory:** Stable capability package definitions (SUB-*, MEM-*, CMX-*, OCT-*, T-* aliases). Free of sprint backlogs. |
| **`technical.md`** | `docs/execution/main/technical.md` | **Engineering Handbook:** Authoritative engineering recipes, factual status records, fault-injection indices, and implementation notes (FACT vs `[PROPOSAL]`). |

---

## 3. Current Control Task DAG & Execution State

The immediate control runway progression at HEAD (`41429f91`):

```text
┌─────────────────────────┐
│ T-26a: Enforce freeze   │───┐
│ [LANDED & ACCEPTED]     │   │
└─────────────────────────┘   │     ┌───────────────────────────┐     ┌───────────────────────────┐     ┌───────────────────────────┐
                              ├───> │ T-52: Wilson + cost κ     │───> │ T-26b: Runner integration │───> │ T-27: Live single-worker  │
┌─────────────────────────┐   │     │ [ACCEPTED on 4a24f2c9]    │     │ [LANDED; review blocked   │     │ canary                    │
│ T-51: L2 holdout freeze │───┘     └───────────────────────────┘     │  on T-51 reacceptance]    │     │ [BLOCKED on T-26b]        │
│ [REOPENED on digest err]│                                           └───────────────────────────┘     └───────────────────────────┘
└─────────────────────────┘
```

### Detailed Task Inspection

#### 1. Task T-51 (`docs/execution/main/tasks.md:906`)
* **State:** `REOPENED / BLOCKED` (fails `test_control_corpus.py` on tasks 04 & 05 oracle digest mismatch).
* **Owner:** Dev C (reviewed by Dev B).
* **Falsifier:** `python3 -m unittest test.benchmarks.test_control_corpus -v`
* **Defect:** `ValueError: oracle digest mismatch` in `test_frozen_suite_is_complete_and_digest_bound` and `test_rejects_duplicate_ids`.
* **Resolution Path:** Re-bind oracle digests in `benchmarks/ladder/suite.json` upon Director D1/D2 authorization.

#### 2. Task T-52 (`docs/execution/main/tasks.md:1079`)
* **State:** `ACCEPTED` (Independent review, Dev B 2026-09-12).
* **Landed Changes:** Reconciled 30 scheduled slots without replacement; separated binary denominator from missingness; enforced genuine token usage and cost $\kappa$ provenance; two-sided Wilson bounds.
* **Falsifier:** `python3 -m unittest test.benchmarks.test_metric_veto test.benchmarks.test_control_accounting -v` (34 tests passing).

#### 3. Task T-26b (`docs/execution/main/tasks.md:852`)
* **State:** `BLOCKED` (Implementation landed in `benchmarks/product_path.py` via commit `2fb7bd58`; review blocked pending T-51 reacceptance).
* **Owner:** Dev C (product identity reviewed by Dev A).
* **Leased Files:** `benchmarks/agentic_harness_matrix_benchmark.py`, `benchmarks/product_path.py`, `benchmarks/ladder/control.py`, `test/benchmarks/test_product_path_subject.py`.

---

## 4. Deep Investigation Matrix: Code vs. Docs vs. Execution

| Dimension / Subsystem | Implementation Code (`vanguard/`, `benchmarks/`) | Main Architecture Docs (`docs/architecture/`, `docs/backend/`) | Execution Runway (`docs/execution/`) | Alignment Status | Required Action |
|---|---|---|---|---|---|
| **TCB Kernel & Boundaries** | `vanguard/packages/kernel/`: 1,386 / 1,438 LOC. 13-stage dispatch pipeline (S0–S12). Pure Python stdlib. | `kernel.md` details S0–S12 stages, capability descriptors, monotonic attenuation. | `spec.md` defines Invariants I-1 through I-10 and TCB ceilings. | **PERFECT (100%)** | None. Continuously enforced by `check_tcb_budget.py` and `check_boundaries.py`. |
| **Product Entrypoint & Write-Landing** | `entrypoint.py:execute()` drops writes on multi-file tool outputs in candidate workspaces; files remain unmutated. | `runtime-execution.md` claims the end-to-end lifecycle is fully IMPLEMENTED. | `tasks.md` & `spec.md` identify write-landing as active defect `BLOCK-T27`. | **DIVERGENT** | Implement Director Charter II causal write fix (T-130 / RUN-13); align `runtime-execution.md`. |
| **Control Benchmark Corpus (T-51)** | Hardened tasks 04 & 05; `test_control_corpus.py` fails 2/8 assertions on digest mismatch. | `assurance-evaluation.md` describes evaluator gateway and oracle bindings. | `tasks.md` truthfully marks T-51 REOPENED / BLOCKED on oracle digest mismatch. | **TRUTHFUL & ACCURATE** | Re-bind suite SHA-256 digests in `benchmarks/ladder/suite.json` upon Director authorization. |
| **Control Report Gate (T-26b)** | Implemented in `benchmarks/product_path.py` and `benchmarks/ladder/control.py`. | `manifests.md` defines control manifest schema. | `tasks.md` records implementation landed, review awaiting T-51 reacceptance. | **TRUTHFUL & ACCURATE** | Conduct four-eyes independent review once T-51 is green. |
| **Model Cascade & Escalation** | Committed local-only cascade in `autofix_harness.py`; hosted cascade unlanded. | `add-adapter-or-provider.md` documents adapters for OpenRouter, llama-server. | `spec.md` RUN-04/RUN-06 bounds cascade to local-only; T-27 spend unapproved. | **ALIGNED** | Preserve local boundary; do not activate paid cascade until Director signs D6. |
| **CI Doc Budgets (`check_doc_budgets.py`)** | Linter checks line counts against hard ceilings in `tools/linters/check_doc_budgets.py`. | `agency.md` (400/200), `runtime-execution.md` (216/200), `runtime-service.md` (201/200) over budget. | `tasks.md` over calibrated ceiling (1,838 / 1,700 lines). | **FAILING (RED)** | Compress historical sprint rows in `tasks.md`; calibrate or consolidate verbose backend docs before release. |
| **Directive Artifact Hygiene** | `director_task_instruction.md` exists in repo root; `.draft/` contains local audit notes. | Architecture hierarchy forbids ephemeral directive files committed in git. | Rule: 5 execution files only; zero scratch docs committed in `docs/`. | **NEEDS CLEANUP** | Keep `director_task_instruction.md` untracked per line 9; store local notes in `.draft/`. |

---

## 5. Strategic Documentation Policy: Avoiding Overengineering vs. Stale Rot

The user raised a fundamental engineering dilemma:
> *"Note that we will change the code so it may drift again, but im not sure when to document, if its too stale it may hurt development and if its overengineered or too documented every time its hurt productivity."*

### The Law of Documentation Leverage

In a high-velocity codebase with automated AST indexing, manual documentation must follow **The Rule of Three Invariants**:

```text
               ┌──────────────────────────────────────────────────────────┐
               │           THE RULE OF THREE DOCUMENTATION INVARIANTS     │
               └────────────────────────────┬─────────────────────────────┘
                                            │
           ┌────────────────────────────────┼────────────────────────────────┐
           ▼                                ▼                                ▼
  1. CONTRACTS & GATES             2. MACHINE KNOWLEDGE             3. IMPLEMENTATION INTERNALS
  • Ports (vanguard/ports)         • Symbols & line numbers         • Private helper methods
  • Wire schemas (domain)          • Upstream caller graphs         • Ephemeral test fixtures
  • Milestone states & RUN deltas  • Test falsifier associations    • Temporary refactoring state
  ─────────────────────────────    ─────────────────────────────    ─────────────────────────────
  MUST BE DOCUMENTED MANUALLY      MAINTAINED VIA AUTOMATION (LDA)  NEVER DOCUMENT MANUALLY
  Update in spec.md / milestones   `uv run lda index --delta` (<25ms) Let source code & tests be
  before claiming gate closure.    Zero human/agent markdown drift. the sole ground truth.
```

### When to Document
1. **Public Interfaces & Schemas:** When a port in `vanguard/packages/ports/` or a wire schema in `vanguard/packages/domain/` changes, document it immediately in `docs/backend/reference/ports.md` or `docs/execution/main/spec.md`. Stale contracts break downstream components and cause agent hallucinations.
2. **Governance Transitions:** When a milestone gate closes or a decision is ratified (e.g., closing `MS-BASELINE`, reopening `T-51`), record it in `docs/execution/main/tasks.md` and `docs/execution/main/milestones.md`.
3. **Architectural Rationale:** When a fundamental invariant is added (e.g., Invariant I-7 domain blindness, N-06 no subprocess in runtime), record it in `docs/backend/architecture/`.

### When NOT to Document
1. **Never Document AST Locations Manually:** Do not maintain tables of line numbers, function names, or file paths in markdown. Run `uv run lda index --delta` (<25ms) or `just docs-knowledge`. LDA indexes the live AST deterministically into SQLite with zero human effort.
2. **Never Update Snapshot SHAs on Feature Commits:** Fields like `analysis_subject_sha` in doc frontmatter are audit snapshot markers from historical reviews. Updating them on every git commit creates massive git diff noise with zero engineering value.
3. **Never Document Unlanded Speculation:** Do not write extensive PRDs or multi-page architecture designs for unstarted features. Use compact `[PROPOSAL]` delta contracts in `docs/execution/main/spec.md` until code is written.

---

## 6. Immediate Action Items to Unblock the Control Runway

1. **Unblock T-51 Holdout Corpus:**  
   Update `benchmarks/ladder/suite.json` with the correct SHA-256 digests for hardened tasks 04 & 05 once Director D1/D2 authorization is issued, ensuring `test_control_corpus.py` passes 8/8 tests.
2. **Execute Independent Review on T-26b:**  
   Conduct four-eyes verification of the product runner gate in `benchmarks/product_path.py` and transition T-26b from `BLOCKED` to `ACCEPTED`.
3. **Execute Causal Write-Landing Fix (T-130 / RUN-13):**  
   Implement the atomic write-landing protocol in `runtime/entrypoint.py` and `agency/episode/` so multi-file tool proposals reliably mutate candidate workspaces.
4. **Clean Git Working Tree & Artifact Hygiene:**  
   Ensure `director_task_instruction.md` remains untracked in `.gitignore` or uncommitted per its header instruction, keeping the git status clean.
5. **Calibrate Doc Budget Ceilings:**  
   Compress stale historical sprint entries in `docs/execution/main/tasks.md` to bring it under the 1,700-line limit before final release qualification.
