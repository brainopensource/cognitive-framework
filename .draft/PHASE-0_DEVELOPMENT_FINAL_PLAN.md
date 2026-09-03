---
id: draft.phase-0-development-final-plan
class: planning
authority: non-canonical
truth_plane: PROPOSED
status: draft
owner: repository-governance
version: "1.0.0"
created: 2026-09-03
lock_head: "66aa7a3c0c31"
purpose: >-
  Organization plan to move the locked triad (A, B, v2) into docs/execution/
  as the only development authority, without information loss, without deleting
  drafts, and without mixing future work into present-tense project docs.
inputs:
  - .draft/DEVELOPMENT_FINAL_PLAN.md
  - .draft/DEVELOPMENT_FINAL_PLAN_B.md
  - .draft/DEVELOPMENT_FINAL_PLAN_v2.md
does_not_delete: true
authorizes_code_changes: false
---

# PHASE-0 — Move the locked triad into the execution runway

This file is the **organization plan**. It does not rewrite Vanguard Python. It does not delete anything. When this plan is later applied, editors **copy** triad content into execution files; they do not summarize it away.

**Sources (keep on disk, unused after apply):**

- [`.draft/DEVELOPMENT_FINAL_PLAN.md`](DEVELOPMENT_FINAL_PLAN.md) — **A** (program law)
- [`.draft/DEVELOPMENT_FINAL_PLAN_B.md`](DEVELOPMENT_FINAL_PLAN_B.md) — **B** (ground truth + tickets 01–35)
- [`.draft/DEVELOPMENT_FINAL_PLAN_v2.md`](DEVELOPMENT_FINAL_PLAN_v2.md) — **v2** (architecture catalog + SOTA harness mechanics)

**Rule after apply:** developers read `docs/execution/` only. Drafts remain as forensic reference. Do not link drafts from `README.md`, `AGENTS.md`, or `docs/SPEC.md` as authority.

**No sprints. No waves. No WIP-lane schedule.** Team capacity is decided later. Execution work is a **flat task tree** grouped by context, with tasks and subtasks only.

---

## 0. Split law (present docs vs future execution)

| Plane | Path | Tense | Allowed content | Forbidden |
|---|---|---|---|---|
| **Present** | `docs/SPEC.md`, `docs/architecture/`, `docs/backend/`, `docs/frontend/`, `docs/product/`, `docs/decisions.md` | **is** (HEAD code) | What the lattice, ports, kernel, agency, runtime, adapters, apps **currently do** | Target DAGs, ticket lists, “we will add 2PC”, wave maps, draft citations as law |
| **Future** | `docs/execution/` only | **shall** (RFC-2119 for work not yet in HEAD) | Milestones, spec deltas, technical recipes, backlog packages, flat tasks | Claiming a MISSING module already exists |
| **Reference** | `.draft/` | frozen lock | A, B, v2, this PHASE-0 | Day-to-day development |

**Promotion rule.** When a task merges:

1. Implementation lands in `vanguard/` / `packs/` / `test/`.
2. Typed contracts that are now true move from `docs/execution/spec.md` into `docs/architecture/` / `docs/backend/` / `docs/SPEC.md` (present tense).
3. The task is checked off in `tasks.md`; the package may move to `DONE` in `backlog.md`.
4. Present docs are updated (including links). Execution keeps remaining future work.

**Database / architecture change example.** A SQLite schema change: implement it; update **present** `docs/backend/` (what the schema is); if more work remains, keep it in **execution** spec/tasks. Do not leave “we will migrate” in architecture docs after it has migrated.

---

## 1. Target execution set (edit existing; create one new)

Do **not** remove current files. Edit in place. Create the fifth file.

| File | Action | Role |
|---|---|---|
| [`docs/execution/milestones.md`](../docs/execution/milestones.md) | **Edit** | Stable TARGET outcomes and acceptance predicates. No day-to-day tasks. No sprint calendar. |
| [`docs/execution/spec.md`](../docs/execution/spec.md) | **Edit** (expand; keep historical CMX-09 delta as a named appendix) | Typed contracts, invariants, error matrices, schemas for **all** future work — not only CMX-09. |
| [`docs/execution/technical.md`](../docs/execution/technical.md) | **Create** | Self-explaining engineering handbook: patterns, files to read, lattice placement, pseudocode, tool schemas, workflows, `[PROPOSAL]` variants kept in full. |
| [`docs/execution/backlog.md`](../docs/execution/backlog.md) | **Edit** | Capability packages + lifecycle. Alias table (B `T-NN`, v2 `SUB-*`/`TXN-*`, old `CMX-*`). Research questions, risks, decisions. No sprint queue. |
| [`docs/execution/tasks.md`](../docs/execution/tasks.md) | **Edit** (replace sprint DAG with flat tree; preserve old CMX-09 DAG as a historical appendix) | Tasks and subtasks by **context**. Checkboxes only. `requires:` edges allowed; no wave/sprint numbering. |

When applying, also **edit** (do not delete) [`AGENTS.md`](../AGENTS.md) §6: the “exactly four” execution files become **five**, adding `technical.md`. Fix links that point at `docs/execution/active.md` or `FEATURE_SPEC.md` (see §8).

Optional stub: if something still links to `FEATURE_SPEC.md`, add a one-line pointer file **only if** a broken link would remain; prefer retargeting links to `spec.md`. Do not create `active.md`.

---

## 2. Copy-in-full rule (no information loss)

When applying this PHASE-0:

1. **Copy, then place.** Each triad section listed in §3 is copied into the destination file (or a named subsection). Do not replace a 200-line protocol with a three-bullet summary.
2. **Keep `[PROPOSAL]` variants.** A’s 17 domain types, v2 kernel AST hook, HYDRA heads, mutation ≥ 0.80, Campaign Service layer, second compiler — all stay, tagged. Canonical lattice is B §6.12 / v2 FACT columns.
3. **Keep historical snapshots.** A §1 and B §2 evidence boundaries stay in `technical.md` as “planning snapshots,” not as current HEAD identity. Current HEAD is recorded in execution YAML `last_verified`.
4. **Do not delete** A, B, v2, this PHASE-0, or current execution files.
5. After copy, add a banner on A/B/v2: *Unused reference. Authority is `docs/execution/`.* That is an additive banner, not a content cut.

**Canonical numbering.** Execution task IDs are **`T-01` … `T-35`** from B §18. Additional items from A §31 and v2 that are not already those 35 become **`T-36` onward** in the same flat tree. v2 `SUB-01`, `TXN-01`, `PRG-01`, old `CMX-10A`, `W-092-F2` are **aliases** in `backlog.md`, not second IDs.

---

## 3. Complete routing table (every triad heading)

Copy each source section into the destination. If two sources overlap, copy **both** under adjacent headings (`### From A`, `### From B`) so neither is dropped.

### 3.1 Plan A → destinations

| A section | Destination | Notes |
|---|---|---|
| Lock preamble, epistemic legend, dual mission, reliability identity | All five files: short YAML + pointer. Full legend lives in `technical.md` §0 | Shared law |
| §0 Executive decision | `milestones.md` (program order as TARGET outcomes, **not** a wave calendar); `spec.md` non-goals pointer | Recast 1–10 as capability milestones MS-01… not “Wave 0” |
| §1 Evidence snapshot | `technical.md` appendix “A planning snapshot” | Historical; not HEAD |
| §2 What code provides + gaps G-01…G-12 | `technical.md` “Live substrate”; gaps also seed `backlog.md` package justifications | Present facts belong in `docs/backend/` **after** verify against HEAD; until then keep in execution technical |
| §3 Thesis, SOTA definition, non-goals | `spec.md` product thesis + non-goals; `milestones.md` quality objective | |
| §4 Competency profiles | `milestones.md` done-definitions; `spec.md` profile contracts | |
| §5 Formal model | `technical.md` (full math) | Keep A and B formalisms both |
| §6.1 Architectural shape | `technical.md`; Campaign Service stack tagged `[PROPOSAL]` | FACT path: ApplicationService → … → Kernel |
| §6.2 17 domain values | `spec.md` `[PROPOSAL]` catalog; B merge wins for implementation | Do not drop the list |
| §6.3 8 ports | `spec.md` `[PROPOSAL]`; prefer extend `IndexPort` | |
| §6.4 Verification receipt fields | `spec.md` (normative schema) | |
| §6.5 Progressive packet | `spec.md` + `technical.md` | |
| §6.6–6.8 Campaign / handoffs / director | `spec.md` + `technical.md`; `[PROPOSAL]` until T-31 | |
| §6.9 Single-writer | `spec.md` invariant | |
| §7–18 Wave map and Wave 0–10 bodies | **Do not** recreate as waves. Split: exit gates → `milestones.md`; work packages/falsifiers → `tasks.md` subtasks; likely files → `technical.md` | Strip the word “Wave” from task titles |
| §19 Sprint cadence / DAG | **Drop as schedule.** Keep dependency edges as `requires:` on tasks. Keep WIP policy as optional note in `backlog.md` lifecycle, not a calendar | User forbade sprint/wave proposals |
| §20 File ownership | `technical.md` “where to edit” | Merge with B §17 |
| §21 Prompt/policy | `technical.md` + `spec.md` policy fragments | |
| §22 Model strategy | `spec.md` + tasks context Model routing | |
| §23 Security / operator | `spec.md` + `technical.md` CLI | Merge A §37 |
| §24 Verification matrix | `spec.md` + each task’s falsifier bullets | |
| §25 Benchmark taxonomy | `spec.md` + `backlog.md` SWE/DeepSWE packages | |
| §26 Research/explanation agents | `spec.md` workflows; tasks context Research | |
| §27 Risks | `backlog.md` | |
| §28 Stop/rollback | `spec.md` + each task rollback line | |
| §29 Definition of done by profile | `milestones.md` | |
| §30 Go/no-go checklists | `technical.md` “definition of ready/done per task” (not per sprint) | Rename: before impl / during / before review / before claim |
| §31 First 30 tickets | Merge into `tasks.md` as subtasks of T-01… or new T-36+ if distinct | See §5.2 |
| §32 D-01…D-10 | `backlog.md` decision register | |
| §33 Q-01…Q-15 | `backlog.md` open questions | |
| §34–35 References | `technical.md` bibliography | |
| §36 Final recommendation | `milestones.md` one-page intent | |
| §37 CLI surface | `spec.md` CLI + `technical.md` | Merge v2 §12, current spec.md §9 |
| §38 Loop vs harness | `technical.md` | |
| §39 Four-tier memory | `technical.md` + `spec.md` | |
| Appendix L cross-link matrix | `technical.md` | |

### 3.2 Plan B → destinations

| B section | Destination | Notes |
|---|---|---|
| YAML lock identity, triad roles | execution YAML `derived_from`, `lock_head` | |
| Epistemic legend + SUPERSEDED redefinition | `technical.md` §0 | |
| §1 Executive decision | `milestones.md` + `spec.md` | Includes score-band ASPIRATION table — copy in full, keep ASPIRATION |
| §2 Evidence / historical CONTRADICTION | `technical.md` appendix | Keep ebad36e snapshot |
| §3 Inventory 3.1–3.7 | `technical.md` “HEAD inventory”; after code verify, promote facts to `docs/backend/` | |
| §4 Proven gaps 4.1–4.13 | `backlog.md` (gap → package); `tasks.md` (gap → T-id); FEATURE_SPEC vs source table → `spec.md` “MISSING vs HEAD” | |
| §5 Formal model 5.1–5.14 | `technical.md` (full) | Alongside A §5 |
| §6.1–6.12 Architecture | `technical.md` + `spec.md` (6.12 lattice is **canonical placement**) | |
| §7 Competency | merge with A §4 into `milestones.md` | |
| §8 Wave 0–10 bodies | Same split as A waves: gates / tasks / files — **no wave titles in tasks.md** | Keep `[PROPOSAL]` on meta/specialists/director/memory-product/official-benches |
| §9 Sprint sequence | **Do not copy as a schedule.** Dependencies already on tickets | |
| §10–12 Greenfield / brownfield / research workflows | `technical.md` + `spec.md` per-class evidence | Merge A §9.4, v2 §21 |
| §13 Model routing | `spec.md` + tasks Model | |
| §14 Multi-agent policy | `spec.md` + `technical.md` | `[PROPOSAL]` default off |
| §15 Memory and skills | `spec.md` + `technical.md` | |
| §16 Benchmark methodology | `spec.md` + `milestones.md` SWE-P* keep | |
| §17 File-by-file routing | `technical.md` | |
| §18 Tickets 01–35 | `tasks.md` **verbatim** as T-01…T-35 with all falsifiers/files/requires | Canonical work list |
| §19 Risks | merge A §27 into `backlog.md` | |
| §20–21 References + session appendix | `technical.md` | |
| Appendix A algorithms | `technical.md` (pseudocode) | |
| Appendix B wave DAG | omit as schedule; keep `requires:` | |
| Appendix C vs A | `technical.md` | |
| Appendix D operator one-pager | `tasks.md` intro: T-01–08 then T-09–13 first **as a recommended reading order**, not a sprint | |
| §22–23 tool inventory / product loop (lock append) | `technical.md` + `spec.md` verbs | |
| Appendix E cross-link | merge with A L / v2 appendix | |

### 3.3 Plan v2 → destinations

| v2 section | Destination | Notes |
|---|---|---|
| Lock preamble, complements A+B | execution relationships YAML | |
| §1 Dual mission + MERGED historical | `milestones.md` dual mission; MERGED note in `technical.md` | |
| §2.1 16 primitives + FACT owner column + `[PROPOSAL]` packages | `technical.md` (full table) | |
| §2.2 Phenotype | `technical.md` `[PROPOSAL]` | |
| §2.3 Workflow node kinds | `technical.md` | |
| §2.4 TransformSpec sketch + live `contracts.py` fields | `spec.md` + `technical.md` | Must include live `transform_id` / `input_schema` |
| §3 Context economics P1–P5, L1–L5, ResultDistiller, salience, dead-ends, knapsack | `technical.md` + `spec.md` context packet | L3 dump bug stays FACT |
| §4.2 2PC protocol | `spec.md` (already partial) + `technical.md` **full** ASCII protocol | |
| §4.3 AST snippet | `technical.md` with `[PROPOSAL]` kernel hook **rejected** I-7; FACT adapter placement | Keep snippet |
| §4.4 Speculative git checkpoints | `technical.md` `[PROPOSAL]` | |
| §5 Tamper, fail-to-pass, mutation 0.80 | `spec.md` tamper; fail-to-pass **bugfix class** (A §9.4 wins); mutation `[PROPOSAL]` | Keep mutation section in full |
| §6 Dialect pipeline | `spec.md` (extend current §8) + `technical.md` | Split dialect.py vs protocol_recovery.py FACT |
| §7 Director, Meta-Conductor, HYDRA, 5 heads | `technical.md` `[PROPOSAL]`; `backlog.md` OCT/HYD packages; `milestones.md` TARGET outcomes without wave IDs | Chimera Head 3: product implementer = EpisodeEngine+pack |
| §8 Package inventory SUB/TXN/SHD/PRG/WRN/VER/OCT/HYD | `backlog.md` aliases → T-ids | Not a second DAG |
| §9 Lattice + invariant matrix | `spec.md` invariants + `technical.md` layer table | I-1 universal signed finish `[PROPOSAL]` vs A per-class |
| §10 Conclusion | skip or one paragraph in milestones | |
| §11–24 SOTA lock append (loop, CLI, toolkit, edit stack, context, index, memory, skills, loop vs harness, meta, long/brown/green, other pieces, picture, build order) | `technical.md` **in full**; CLI overlap → `spec.md`; build order → `tasks.md` reading-order note only | Do not compact |
| Cross-link appendix | `technical.md` | |

---

## 4. What each execution file must contain after apply

### 4.1 `milestones.md` — TARGET outcomes only

Keep existing **M-0–M-10**, G-1/G-2/G-3, SWE-P0–P5 rows (they are TARGET, not a sprint). Add capability TARGET rows **without** W-092-F* / Wave names:

| ID | TARGET outcome | Acceptance (copy predicates from A/B exit gates) |
|---|---|---|
| **MS-INSTRUMENT** | Exact-subject, schema-valid, dry-run-null empirical instrument | B Wave 0 §8.4/8.5 predicates; enumerator digest; no `__pycache__` tasks |
| **MS-TRUTH** | No `completed` without bound verification; Forge cannot invent counts; one gating function | A §9.7; B Wave 1 exit; AdmissionGate + VerificationReceipt.passed |
| **MS-RESUME** | Fresh process restores episode_id, σ, prefix L1–L3; σ not in L3 | A §10.7; B Wave 2 |
| **MS-SEE** | Epoch-bound packets, omissions explicit, one ContextCompiler | A §11.9; B Wave 3; v2 §3 target (not current L3 dump) |
| **MS-CHANGE** | 2PC multi-file, adapter preflight, tamper, implicated-set, greenfield oracle | A §12.8; B Wave 4; v2 §4.2 |
| **MS-CONTROL** | One EpisodeEngine coding path qualified; Forge/Chimera not in product scores | A §13.6; B Wave 5; facade fast/balanced/max |
| **MS-META** | Controller off unless paired study valid | A §14.7; `[PROPOSAL]` |
| **MS-SPECIALIST** | Treatments vs control; exterior merge | A §15.6; `[PROPOSAL]` |
| **MS-CAMPAIGN** | Director as runtime client; CAS handoffs | A §16.8; v2 §7.1; `[PROPOSAL]` |
| **MS-MEMORY** | Product memory behind grants; held-out lift; rollback | A §17.7; M-8 remaining empirical; `[PROPOSAL]` product wiring |
| **MS-OFFICIAL** | SWE-P5 / DeepSWE wrapper; local ≠ official | A §18.8; G-3 |
| **MS-SENIOR … MS-LEAD** | Copy A §29.1–29.4 verbatim | Profiles |

Remove from the living overlay: “Active in tasks.md” sprint language. Status of MS-* is `OPEN` until receipts exist. Keep W-092-F* table as **historical alias → MS-*** in an appendix so old links still resolve.

Octopus W-OCT-1…4 stay as TARGET rows (already there); add HYDRA TARGET rows from v2 §7 as `[PROPOSAL]` outcomes, not a schedule.

### 4.2 `spec.md` — typed delta for the whole program

Retitle from “W-092-F1 / CMX-09” to **Feature delta contracts (execution)**. Keep current CMX-09 schemas as **Appendix: historical CMX-09 draft**.

Must include, copied not summarized:

- Invariants: INV-DELTA-1…5, I-7, I-TCB, I-STATE, I-TXN (adapter, not kernel), I-SHD, single-writer, authorize-before-retrieve
- `VerificationReceipt` field list (A §6.4) + `passed` definition from `admission_gate.py`
- Per-class evidence (A §9.3–9.4) **wins** over v2 I-1; v2 fail-to-pass copied under class `bugfix`
- `SemanticTaskState` / `TaskStep` (current spec §3) **and** live `CodingTaskState` fields; merge note B §6.12
- 2PC `FileMutation` / `TransactionReceipt` (current spec §4) + v2 §4.2 protocol text
- Tamper shield (current spec §6) + B ticket 18 IndexPort enumeration (glob is insufficient)
- Progressive packet (current spec §7) as **L4/L5 policy on existing ContextCompiler**, not a second assembler
- Dialect taxonomy (current spec §8) + FACT split `dialect.py` / `protocol_recovery.py`
- CLI (current spec §9 + A §37 + v2 §12): MECHANISM `run/status/resume/evidence/cost`; `[PROPOSAL]` `cancel/doctor/checkpoint/non-interactive`
- Admission: `admission_required` vs unused `ADMISSION_GATED_HARNESSES`; exemption FACT
- WorkspaceEpoch schema `[PROPOSAL]`
- Tool verb table from B §22 / v2 §13
- Error matrix / exit codes
- Non-goals (A §3.3)
- `[PROPOSAL]` catalogs: 17 domain types, extra ports, mutation 0.80, CampaignPlan types

Kernel: spec MUST say AST preflight SHALL NOT enter `kernel/dispatch.py` S7/S8.

### 4.3 `technical.md` — new self-explaining handbook (5th file)

This file exists so a developer does **not** need A/B/v2. Copy:

0. Epistemic legend; how to navigate (LDA golden order, `docs_rag_v0.py --file`, present docs to read first)
1. Dual mission (coding agent + harness builder)
2. HEAD inventory (B §3) with source paths
3. Product loop diagrams (B §6.1, v2 §11, v2 §23) labeled FACT vs `[PROPOSAL]`
4. 16 primitives table with FACT owners
5. L1–L5, ResultDistiller, dead-ends, progressive mapping B §6.8
6. Edit stack v2 §14; 2PC full protocol; `git.py` sequential FACT
7. Admission/Forge/resume bugs (B §4.1–4.4) as “current defects”
8. Greenfield / brownfield / research workflows (A, B, v2) in full
9. Prompt architecture, tool ergonomics, model routing
10. Appendix A algorithms from B (admission, compile, 2PC, campaign)
11. File-by-file routing (B §17 + A §20)
12. Bibliography (A §34–35, B §20)
13. Cross-link matrix
14. Go/no-go checklists renamed per-task
15. Formal models A §5 and B §5 in full
16. HYDRA / director / phenotype **in full** as `[PROPOSAL]`
17. Planning snapshots A §1, B §2

**Present-docs to open while coding** (repeat beside each context in tasks.md):

| Context | Read first (present) |
|---|---|
| Kernel / TCB | `docs/architecture/boundaries.md`, `vanguard/packages/kernel/dispatch.py` |
| Turn loop | `docs/backend/architecture/agency.md`, `episode/engine.py`, `session.py` |
| Context | `agency.md`, `compiler.py`, `layers.py`, `compaction.py` |
| Runtime / resume | `docs/backend/architecture/runtime-execution.md`, `app_service.py`, `task_state.py` |
| Index | `ports/index.py`, `adapters/stores/repo_index.py` |
| Packs | `packs/code-default/` plugins + middleware |
| Memory | `docs/backend/architecture/memory-learning.md`, `ports/memory.py` |
| Eval | `docs/backend/architecture/assurance-evaluation.md` |

### 4.4 `backlog.md` — packages, not a sprint board

Keep lifecycle states (PROPOSED…DONE). Remove “Active in active.md”. Queue section becomes **“Package index”** with no “next-up sprint” numbering.

Each package row: ID, aliases, owner path, status, related T-ids, acceptance one-liner, source (A/B/v2 section).

Must list at least:

- Existing CMX-01…CMX-11, REL-01R, OCT-01…04, TLS-*, MEM-*, TUI-01 (keep; do not delete)
- New/alias rows: INSTRUMENT (T-01–03, 24–25), TRUTH (T-04–08, 23), STATE (T-09–13), SEE (T-14–16), CHANGE (T-17–20), DIALECT (T-21–22), CONTROL (T-26–27), META (T-28), SPECIALIST (T-29–30), CAMPAIGN (T-31), MEMORY (T-32), OFFICIAL (T-33), LATTICE (T-34–35), plus T-36+ packages
- v2 SUB-01→T-04/05, TXN-01→T-17, SHD-01→T-18, PRG-01→T-15, PRG-02 ResultDistiller as T-36, WRN-01→T-21, WRN-02 pager T-37, VER-01 fail-to-pass T-38, VER-02 mutation T-39 `[PROPOSAL]`, HYD-01/02 `[PROPOSAL]`
- Decision register D-01–D-10 (A §32) in full
- Questions Q-01–Q-15 (A §33) in full
- Risks R-01–R-12 (A) merged with B §19
- Score-band ASPIRATION table (B §1)

### 4.5 `tasks.md` — flat tasks and subtasks by context

Replace the living “Active Sprint W-092-F1 / CMX-09” DAG as the **primary** view. Append the old DAG under `## Appendix: historical CMX-09 DAG (do not execute as the program)`.

Header must say: no sprints, no waves, no WIP=1 calendar. Team picks tasks later. `requires:` is the only order hint.

**Recommended reading order (not a sprint):** T-01–T-08, then T-09–T-13 (B Appendix D). Everything else unordered except `requires:`.

Structure:

```text
## Context: <name>
### T-NN Title
- Status, requires, files, present-docs to read
- Subtasks (checkboxes)
- Falsifier
- Rollback
```

---

## 5. Flat task tree (copy into `tasks.md`)

IDs T-01–T-35 are B §18 **verbatim** (files, requires, falsifiers). Below, each is expanded with subtasks from A/B/v2 so nothing of the ticket bodies is lost. Additional T-36+ absorb A §31 leftovers and v2 pillars not already covered.

### Context: Instrument truth

**T-01 Enumerator membership digest** (B)  
- [ ] Schema-valid task manifest required; directory names insufficient  
- [ ] Reject `__pycache__`, hidden, tmp, missing oracle, duplicate IDs, digest mismatch  
- [ ] Order-independent task-set digest  
- Files: `benchmarks/benchmark_20_suite/runner.py`; create `test/benchmarks/test_b20_membership.py`  
- Falsifier: `__pycache__` is not a task  

**T-02 Subject SHA on every empirical JSON** (B)  
- [ ] Bind `subject_sha` = frozen candidate `git rev-parse HEAD`  
- [ ] Missing SHA ⇒ receipt refused  
- Files: `benchmarks/protocols.py`, B20 writer  
- Requires: T-01  

**T-03 Dry-run empirical field ban** (B)  
- [ ] `dry_run ⇒` pass/cost/oracle_passed null  
- Files: runners; cousin `test/benchmarks/test_m8_bundle.py`  

**T-24 Patch identity on results** (B)  
- [ ] PASS row without patch digest refused  
- Requires: T-02  

**T-25 Missingness taxonomy** (B)  
- [ ] Distinct `passed` / `failed` / `undeterminable` / `not_run`  
- [ ] Provider ≠ task fail; harness ≠ model; `DATASET_INVALID` ≠ fail  
- Requires: T-01, T-02  

**T-40 Dirty-subject fail-closed** (A §31.9)  
- [ ] Qualifying run on dirty tree fails closed  
- Related: T-02  

**T-41 BAAC schema-valid discovery** (A §31.7)  
- [ ] Require schema-valid manifests in BAAC (if distinct from T-01, keep both)  

### Context: Admission and verification truth

**T-04 Remove default admission exemption** (B) `[PROPOSAL]` + successor baseline  
- [ ] Record RF-25 / M-2 successor baseline **before** shrinking `ADMISSION_GATE_EXEMPT`  
- [ ] Falsifier: `vg-code-default` + `finish` + no patch ⇒ not completed  
- FACT: exemption pinned by `test/falsifiers/test_completion_gate_scope.py`  
- Files: `runtime/session.py`  

**T-05 One gating source of truth** (B)  
- [ ] Delete unused `ADMISSION_GATED_HARNESSES` **or** make it the only source  
- Requires: T-04  
- Files: `session.py`; `test_completion_gate_scope.py`  

**T-06 Remove Forge `test_count = 1`** (B)  
- [ ] Delete `forge/engine.py` L309–311 fallback  
- [ ] Chimera `executed = 1` on bare exit 0 — same treatment (subtask from A G-01)  
- Falsifier: exit 0 + empty output ⇒ not passed  

**T-07 Typed verification command subject** (B)  
- [ ] Bind argv digest + workspace digest + task digest  
- [ ] `python3 -c 'print("OK")'` is not verification  
- Requires: T-04  

**T-08 Parse counts without inventing** (B)  
- [ ] collected/executed/passed/failed/skipped (A §31.2–3)  
- [ ] `Ran 0 tests` / `0 passed` ⇒ 0  
- [ ] Unrecognized runner remains unknown  
- Requires: T-07  

**T-42 Adversarial coding verification suite** (A §31.6)  
- [ ] Replace retired `test/runtime/test_coding_verification.py` empty suite  
- [ ] `true` / `echo 10 tests passed` cannot admit  
- [ ] Unrelated suite cannot satisfy task relevance  
- [ ] Stale verification after write rejected  
- [ ] Foreign task/composition digest rejected  

**T-38 Fail-to-pass reproducer (bugfix class)** (v2 §5.3, A §9.4)  
- [ ] Pre-verify MUST fail; post-verify MUST pass; vacuous reproducer rejected  
- [ ] Not a universal finish law (docs/research/explanation excluded)  

**T-23 Quarantine Forge/Chimera from Coding Max reports** (B)  
- [ ] Product arms ⊆ `{vg-code-fast,balanced,max}`  
- Requires: T-06  

### Context: Semantic state and resume

**T-09 Domain SemanticTaskState** (B) `[PROPOSAL]` merge with `CodingTaskState`  
- [ ] Create `domain/task_state.py` (**MISSING**) stdlib + JCS  
- [ ] Do not create a second authority beside `fold_task_state`  
- [ ] A §6.2 extra types remain `[PROPOSAL]` catalog in spec, not this task’s scope  

**T-10 Runtime fold** (B)  
- [ ] Fold events; unknown ignored; remove `"test" in action.lower()` inference  
- [ ] Durable events: classified, hypothesis open/support/reject, obligation open/satisfied, etc. (A §10.2)  
- Requires: T-09  

**T-11 Preserve episode_id on resume** (B)  
- [ ] Stop synthesizing only `episode-{run_id}`  
- Requires: T-10  

**T-12 Stop dumping resume_state into L3** (B)  
- [ ] σ in L4/L5; L1–L3 prefix identity after resume+write  
- Requires: T-10  

**T-13 ContextPacket resume identity** (B)  
- [ ] Populate `validate_resume_identity` fields  
- Requires: T-12  

**T-43 Task class on projection** (A §31.11)  
- [ ] Explicit task class on state (if not inside T-09 schema)  

**T-44 Resume parity vectors** (A §31.16–19)  
- [ ] All semantic fields; restart-after-patch; restart-after-verification; 40-turn fresh-process  
- Requires: T-11, T-12  

### Context: Context, index, epoch

**T-14 WorkspaceEpoch** (B)  
- [ ] `{treeHash, indexDigest, sourceRevision, compiledAtTurn}`  
- [ ] Stale packet cannot justify completion  
- Files: `ports/index.py`, `adapters/stores/repo_index.py`, session  

**T-15 Progressive L4/L5 strategy** (B)  
- [ ] Policy on existing `ContextCompiler`; **not** a second compiler (`PRG-01` alias)  
- [ ] Settled invariants / dead ends non-evictable  
- [ ] ResultDistiller at effect boundary (v2 §3.3) → if large, split T-36  
- Requires: T-12, T-14  

**T-16 Index refresh after patch.apply** (B)  
- [ ] Callers after write include new symbol or explicit omission  
- Requires: T-14  

**T-36 ResultDistiller + output caps** (v2 §3.3, §13, WRN-02)  
- [ ] Compact text + full artifact digest; ~1–2k char tool bodies  
- [ ] Goal echo at tail of L5 (v2 §15)  

**T-37 Omission ledger in packet** (A §11.5, §31.20)  
- [ ] Explicit omitted-items report; truncated ≠ complete  

**T-45 Deterministic no-index fallback** (A §31.23)  
- [ ] Evidence when IndexPort unavailable  

**T-46 Phase-aware ranking** (A §31.22) `[PROPOSAL]` keep ranking out of IndexPort (B)  

### Context: Multi-file edit, 2PC, tamper, completeness

**T-17 Atomic multi-file transaction** (B, v2 §4.2)  
- [ ] Shadow tree; `ast.parse` in **adapter**; all-or-nothing  
- [ ] File 4 of 5 syntax fail rolls back all  
- [ ] Kernel MUST NOT gain AST  
- Files: create `adapters/environment/transaction.py`; `git.py`  
- Requires: T-08 (honest verify)  

**T-18 TestTamperShield** (B, spec §6)  
- [ ] Enumerate tests via IndexPort, not only `Path.glob("test/**")`  
- [ ] Assertion edit ⇒ admission reject  
- Requires: T-17, T-14  

**T-19 Greenfield oracle vacuity** (B, A §12.4, v2 §21.3)  
- [ ] Tests that pass on stubs rejected  
- Requires: T-18  

**T-20 Brownfield implicated-set fail-closed** (B, A §12.2–12.3)  
- [ ] Empty primary + coverage_ratio 1.0 cannot admit  
- [ ] Greenfield bypass cannot apply to `bugfix`  
- [ ] Public signature change ⇒ call sites in same transaction  
- Requires: T-16  

**T-47 Read-before-edit + multi-strategy apply** (v2 §14) `[PROPOSAL]`  
- [ ] Refuse patch if file/hunk not observed; exact → whitespace → indent → fuzzy → unified diff  

**T-48 Workspace fingerprint circuit breaker** (v2 §14.5) `[PROPOSAL]`  
- [ ] Cyclic `d_t = d_{t-2}` ⇒ change hypothesis  

**T-49 Speculative git checkpoint rollback** (v2 §4.4) `[PROPOSAL]`  

### Context: Dialect and model routing

**T-21 Dialect typed failure classes** (B, spec §8)  
- [ ] Truncated JSON, DeepSeek fence, XML tags classified without false `ok`  
- Files: `adapters/models/dialect.py`; create `test/contracts/test_dialect_recovery.py`  

**T-22 Fail-closed model resolve** (B)  
- [ ] Alias or error; never silent unknown (`deepseek-v4-flash` vs `-0731`)  
- Files: `routing.py`  

**T-50 Routing experiments harness** (A §22.5) `[PROPOSAL]`  
- [ ] Hold task/tools/context/verify fixed; compare routes  

### Context: Single-agent qualification

**T-26 Frozen control preregistration** (B; strip “Wave 5” from title)  
- [ ] n, models, stop rule frozen before first paid call  
- Requires: T-01–T-25 as applicable  

**T-27 Single-agent canary (eval)** (B)  
- [ ] Disposition in {POSITIVE, NEGATIVE, UNDETERMINABLE, INVALID}  
- Requires: T-26  

**T-51 Internal multi-class corpus freeze** (A §31.28, B Wave 0 corpus sizes)  
- [ ] Keep A’s 10×6 class mix as `[PROPOSAL]` size; do not treat as a sprint  

**T-52 Wilson intervals + cost κ on control** (A §13.5, B §16)  

### Context: Meta, specialists, merge `[PROPOSAL]`

**T-28 Meta-controller paired study** (B)  
- [ ] Inconclusive ≠ negative; cannot enlarge budget; cannot admit completion  
- Requires: T-27  

**T-29 Treatment T-TI ablation** (B)  
- [ ] Investigator cannot `patch.apply`; McNemar includes missingness  
- Requires: T-27  

**T-30 Isolated patch EXTERIOR_SELECT** (B)  
- [ ] Selector is test verdict; LLM preference ignored  
- Requires: T-27, T-17  

**T-53 Role catalog** (A §15.2 localizer/reviewer/test_investigator) — subtasks under T-29 if not split  

### Context: Campaign and HYDRA `[PROPOSAL]`

**T-31 Campaign director fixture** (B)  
- [ ] Crash after node 3; resume 4–8; no duplicate writes  
- [ ] Director has zero mutating tools (v2 §7.1)  
- Files: create `runtime/campaign/` **not** a second EpisodeEngine  
- Requires: T-27  

**T-54 CAS mailbox + CoordinationPlan** (v2 OCT-01/02, A §6.7) — may be subtasks of T-31  

**T-55 HYDRA bifurcation + living horizon** (v2 §7.3–7.4) `[PROPOSAL]`  
- [ ] Product implementer remains EpisodeEngine+pack, not ChimeraEngine  

**T-34 WorkflowScheduler lease honesty** (B)  
- [ ] Parallel path uses kernel leases or is disabled in product profiles  

### Context: Memory and skills `[PROPOSAL]` product wiring

**T-32 Memory grant on product path** (B)  
- [ ] Retrieve without grant denied; generator ≠ evaluator ≠ promoter  
- Requires: T-27; ADR-0100  
- Present docs: `memory-learning.md`  

**T-56 Skill catalog progressive disclosure** (v2 §18, A §17.4–17.5)  
- [ ] Names in L2/L3; body on invoke; exterior promote; rollback  

**T-57 Counterfactual replay** (A §17.6)  

### Context: Official benches `[PROPOSAL]` / blocked on control

**T-33 Official DeepSWE wrapper** (B)  
- [ ] Dry-run produces no pass%; committed-patch-only grading  
- Requires: T-27; REL-03  
- G-3: local suites never official  

**T-58 SWE-P5 official procedure adapter** (A §18, milestones SWE-P*)  

### Context: CLI / operator

**T-59 Facade stays thin** (A §2.3, v2 §12)  
- [ ] CLI does not assemble prompts, patch, or grade  
- MECHANISM: `run/status/resume/evidence/cost`  
- `[PROPOSAL]`: `cancel`, `doctor`, `checkpoint`, `--non-interactive`, NDJSON  

**T-60 TUI-ready backend events** (A §23.4) `[PROPOSAL]` — events only; no TUI visual design (A non-goal)  

### Context: Packs, prompts, policies

**T-61 Task-class policy fragments** (A §21.2) versioned, ablatable  

**T-62 Pack keyword classifier repair** (B §3.4 `classify_task`)  

**T-63 Greenfield vs completeness silent bypass removal** (B §3.4, T-20)  

### Context: Lattice hygiene

**T-35 TCB and boundary freeze** (B)  
- [ ] `check_tcb_budget.py`, `check_boundaries.py`, domain-blindness PASS on every impl  
- Requires: each impl task  

**T-64 Kernel AST prohibition regression test** (v2 I-7 vs §4.3)  
- [ ] No `ast.parse` in `vanguard/packages/kernel/`  

### Context: Research / explanation agents

**T-65 Explanation completion policy** (A §26.3, §9.4)  
- [ ] Evidence-linked claims; no mutation unless requested  

**T-66 Research completion policy** (A §26.2, §9.4)  
- [ ] Provenance; no fabricated citations  

### Context: Present-docs promotion (after merges)

**T-67 Promote landed contracts**  
- [ ] Move true schemas from `execution/spec.md` into `docs/architecture/` / `docs/backend/` / `docs/SPEC.md`  
- [ ] Run `docs_rag_v0.py --file` on every changed production path  
- [ ] `just docs-knowledge` — never hand-edit `.generated/`  

**T-68 Link repair** (see §8) — can start immediately; does not wait for T-01  

---

## 5.2 Merge map: A §31 → T-ids (no dropped tickets)

| A §31 # | Maps to |
|---|---|
| 1 inferred test counts | T-06, T-08 |
| 2 runner identity | T-07 |
| 3 collected/executed/… | T-08 |
| 4 bind epoch | T-14 |
| 5 bind selected test IDs | T-07 subtask |
| 6 retired suite | T-42 |
| 7 BAAC manifests | T-41 |
| 8 task-set digest | T-01 |
| 9 dirty subject | T-40 |
| 10 failure classes | T-25 |
| 11 task class | T-43 |
| 12 hypothesis events | T-10 |
| 13 obligation events | T-10 |
| 14 repository epoch | T-14 |
| 15 context selection identity | T-13 |
| 16–19 resume falsifiers | T-44 |
| 20 omission report | T-37 |
| 21 post-write index | T-16 |
| 22 phase-aware ranking | T-46 |
| 23 no-index fallback | T-45 |
| 24 change-surface callers | T-20 |
| 25 task-to-test association | T-07 / T-20 |
| 26 greenfield DAG | T-19 |
| 27 test-tamper | T-18 |
| 28 60-task corpus | T-51 |
| 29 single-agent CI | T-52 |
| 30 first positive treatment | T-29 |

---

## 6. Apply procedure (later; not this PHASE-0 write)

Order of file edits when someone executes this PHASE-0:

1. Create `docs/execution/technical.md` with YAML `id: execution.technical`, copy §4.3 contents from triad (full sections).
2. Expand `spec.md` per §4.2; move current body to appendix.
3. Rewrite `milestones.md` living overlay per §4.1; keep M-0–M-10 and SWE-P*; appendix alias W-092-*.
4. Expand `backlog.md` per §4.4; keep all existing package rows.
5. Rewrite `tasks.md` primary view to §5; appendix historical CMX-09 DAG.
6. Edit `AGENTS.md` execution-file count 4→5; documentation hierarchy bullet.
7. Fix links §8.
8. Add unused-reference banner to A, B, v2 (additive).
9. Integrity: every A/B/v2 `##` heading appears in the routing table as copied; grep T-01…T-35 headings in `tasks.md`; `wc -l` of execution set **increases**; no draft file deleted.

Do **not** in that apply: invent sprints, authorize kernel AST, enable HYDRA by default, or treat drafts as remaining authority.

---

## 7. Present `docs/` updates (only when code is true)

| Trigger | Present file to update |
|---|---|
| Admission/verification behavior changes | `docs/backend/architecture/agency.md`, `assurance-evaluation.md` |
| Resume/σ/compiler | `agency.md`, `runtime-execution.md` |
| New domain types actually merged | `docs/backend/reference/` schemas, `docs/SPEC.md` |
| 2PC actually in git adapter | environment adapter docs under `docs/backend/` |
| Index epoch actually on port | ports ICD |
| Invariant change | `docs/SPEC.md` + possibly `docs/decisions.md` **only** if a new ADR is required (do not mint ADRs for ordinary deltas) |

Until then, those behaviors stay in **execution** spec/technical as SHALL.

---

## 8. Link and ref fixes (T-68)

Broken or stale references to retarget (do not delete the old documents):

| Current | Target |
|---|---|
| `docs/execution/active.md` | `docs/execution/tasks.md` (file absent) |
| `docs/execution/FEATURE_SPEC.md` | `docs/execution/spec.md` |
| `backlog.md` relationship `execution.active` | `execution.tasks` |
| README “sole current-state source = active.md” | five execution files; present docs for HEAD |
| `AGENTS.md` “exactly four” execution files | five, including `technical.md` |
| Drafts cited as implementation authority | “reference only; see docs/execution” |
| `file:///home/rock-dev/...` absolute links in v2 | repo-relative `docs/execution/...` |

Search and retarget in: `README.md`, `AGENTS.md`, `docs/execution/*`, `docs/research/**` (research may keep historical names but should note absence).

---

## 9. Information-loss checklist

Before declaring the apply done:

- [ ] A §0–§39 and appendices each have a destination in §3.1  
- [ ] B §1–§23 and appendices A–E each have a destination in §3.2  
- [ ] v2 §1–§24 and appendix each have a destination in §3.3  
- [ ] T-01–T-35 exist in `tasks.md` with original falsifiers  
- [ ] A §31 all 30 lines mapped in §5.2  
- [ ] D-01–D-10 and Q-01–Q-15 in `backlog.md`  
- [ ] Risks copied  
- [ ] 16 primitives table includes FACT owners and `[PROPOSAL]` paths  
- [ ] `ast.parse` snippet retained with I-7 rejection  
- [ ] Live `TransformSpec` fields present in spec or technical  
- [ ] `adapters/stores/event_store.py` listed as STORE owner  
- [ ] `domain/task_state.py` always marked MISSING until T-09 lands  
- [ ] HYDRA / mutation 0.80 / 17 domain types / Campaign Service still present as `[PROPOSAL]`  
- [ ] `.draft/DEVELOPMENT_FINAL_PLAN*.md` still on disk  
- [ ] No sprint/wave calendar in `tasks.md` primary view  

---

## 10. What this PHASE-0 does *not* do

- Does not implement T-01+.
- Does not delete drafts or execution history.
- Does not assign owners, dates, or sprints.
- Does not authorize default multi-agent, kernel coding semantics, or official leaderboard claims.
- Does not rewrite present-tense architecture docs as if 2PC/tamper/progressive already shipped.

---

*End of PHASE-0. Apply by copying triad content into the five execution files using §3–§6. Authority after apply: `docs/execution/`. Drafts remain unused reference.*
