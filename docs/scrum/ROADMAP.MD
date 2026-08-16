# Aether Vanguard — Product Roadmap

> **Living staffing & delivery map** for Phase 3 (backend sprints 7–10) and the interaction-plane frontend track.
>
> **This file is a navigator and effort view — not a second source of truth.**
> If this file and an owner disagree, the owner wins (`VG-00` **PR-3** / **PR-4**).

---

## Table of contents

0. [Authority map — stop drift](#0-authority-map--stop-drift)
1. [Roadmap overview](#1-roadmap-overview)
2. [How to read this board](#2-how-to-read-this-board)
3. [Wave map & MVP gates](#3-wave-map--mvp-gates)
4. [Staffing model](#4-staffing-model)
5. [Delivery playbook (ASAP)](#5-delivery-playbook-asap)
6. [BACKEND — Phase 3 Task Board (Sprints 7–10)](#backend)
7. [FRONTEND — Interaction plane](#frontend)

---

## 0. Authority map — stop drift

### 0.1 One owner per kind of truth

| Layer | Owns | Path | Does **not** own |
|---|---|---|---|
| **Concepts / contracts** | What the system *is* (planes, wire, gates, ADRs) | [`docs/main_v4/`](../main_v4/) — start [`00_vanguard_registry`](../main_v4/00_vanguard_registry_v040.md) | Sprint task lists, LOC estimates |
| **Reviews** | Findings & rulings that feed tickets | [`docs/reviews/doing/`](../reviews/doing/) — index [`000_INDEX`](../reviews/doing/000_INDEX_V043-REV.md) | Normative contracts (never) |
| **Master backlog** | **Task IDs + status** for backend Phase 3 | [`011_master_backlog_phase3_V043-REV.md`](../reviews/doing/011_master_backlog_phase3_V043-REV.md) | Architecture law |
| **Sprint kits** | How / who / DoD for a sprint | [`docs/scrum/sprints/`](sprints/) | New task IDs inventing work |
| **This roadmap** | Staffing view, effort heuristics, navigation | [`docs/scrum/ROADMAP.MD`](ROADMAP.MD) | Status flips, new requirements |
| **Canvas** | Filterable view of the same board | `canvases/s7-s10-task-board.canvas.tsx` | Anything (mirror only) |
| **Frontend concepts** | Interaction-plane contracts (when created) | `docs/front_v4/` — **does not exist yet** | Control-plane law |
| **Frontend sprints** | FE sprint kits (when created) | `docs/scrum/sprints_front/` — **does not exist yet** | Backend `S7–S10` IDs |

```text
  docs/main_v4/          NORMATIVE (VG-00…VG-12, GTS-13C)
        ▲ cite only
        │
  docs/reviews/doing/    NON-NORMATIVE findings → tickets
        │
        ▼
  011 master backlog     LIVING task IDs + [TODO|IN_PROGRESS|DONE]
        │
        ├── docs/scrum/sprints/sprint07..10/     playbooks (lanes A/B/C/J)
        └── docs/scrum/ROADMAP.MD                this file (mirror + links)
              │
              └── canvas (optional UI mirror)

  docs/front_v4/  +  docs/scrum/sprints_front/   FE track (create next; same pattern)
        ▲ cite
  development_guides/cli_tui_architecture.md    interim FE foundation (until front_v4)
```

### 0.2 Anti-hallucination rules (bind every PR)

1. **Status** changes only in [`011`](../reviews/doing/011_master_backlog_phase3_V043-REV.md) (backend) — never “done” only here.
2. **Contracts** change only via ADR / register under [`docs/main_v4/09_…`](../main_v4/09_vanguard_decision_register_v040.md) — never by editing a sprint README.
3. **Roadmap rows** must cite a source ID (`S7-A-01`, review §, or future `FE-…` owned by a sprint kit). Rows without a source are tickets, not backlog.
4. **Do not restate** `main_v4` rules in sprint kits or this file — link the anchor (`PR-1`).
5. **Review WIP cap** = 8 docs in `doing/` ([`007`](../reviews/doing/007_codebase_cleanup_dedup_and_docs_consolidation_V043-REV.md) §5.2). New reviews do not create parallel roadmaps.

### 0.3 Naming — one alphabet, two tracks (do not mix)

| Namespace | Pattern | Example | Folder |
|---|---|---|---|
| Backend Phase 3 | `S{7–10}-{A\|B\|C\|J}-{nn}` | `S7-A-04` | [`sprints/sprint07`](sprints/sprint07/) … [`sprint10`](sprints/sprint10/) |
| Backend waves | `W6…W9` inside **Phase 3** | Sprint 7 = Wave 6 | same kits + [`011`](../reviews/doing/011_master_backlog_phase3_V043-REV.md) |
| Frontend (interim) | `FE-{wave}{nn}` | `FE-101` = FE Wave 1 | **not** `S1` — avoids colliding with closed backend Sprint 1 |
| Legacy (closed / partial) | `sprint6B/`, `sprint7_8/` | historical | read-only; do not schedule new work there |

> **FE “Sprint 1” ≠ backend Sprint 1.** Prefer saying **FE Wave 1** (or `FE-1xx`) so calendars and standups cannot collide.

### 0.4 Backend sprint navigation (canonical names)

| Phase | Wave | Sprint | Theme | Kit | Backlog section | Plan / review |
|---|---|---|---|---|---|---|
| **3** | **W6** | **Sprint 7** | Subtraction & boundary restoration | [`sprints/sprint07/`](sprints/sprint07/) · [README](sprints/sprint07/README.md) · [A](sprints/sprint07/lane-a-control-plane.md) · [B](sprints/sprint07/lane-b-workload-evidence.md) · [C](sprints/sprint07/lane-c-measurement-lab.md) · [J](sprints/sprint07/joint-track.md) | [`011` §4](../reviews/doing/011_master_backlog_phase3_V043-REV.md) | [`008` delivery plan](../reviews/doing/008_v043_delivery_plan_sprints_7_10_V043-REV.md) |
| **3** | **W7** | **Sprint 8** | Recursion, resume, load-bearing manifests | [`sprints/sprint08/`](sprints/sprint08/) · [README](sprints/sprint08/README.md) · [A](sprints/sprint08/lane-a-control-plane.md) · [B](sprints/sprint08/lane-b-workload-evidence.md) · [C](sprints/sprint08/lane-c-measurement-lab.md) · [J](sprints/sprint08/joint-track.md) | [`011` §5](../reviews/doing/011_master_backlog_phase3_V043-REV.md) | same `008` |
| **3** | **W8** | **Sprint 9** | The instrument (Q3) | [`sprints/sprint09/`](sprints/sprint09/) · [README](sprints/sprint09/README.md) · [A](sprints/sprint09/lane-a-control-plane.md) · [B](sprints/sprint09/lane-b-workload-evidence.md) · [C](sprints/sprint09/lane-c-measurement-lab.md) · [J](sprints/sprint09/joint-track.md) | [`011` §6](../reviews/doing/011_master_backlog_phase3_V043-REV.md) | same `008` |
| **3** | **W9** | **Sprint 10** | Generality & MVP gate (Q4) | [`sprints/sprint10/`](sprints/sprint10/) · [README](sprints/sprint10/README.md) · [A](sprints/sprint10/lane-a-control-plane.md) · [B](sprints/sprint10/lane-b-workload-evidence.md) · [C](sprints/sprint10/lane-c-measurement-lab.md) · [J](sprints/sprint10/joint-track.md) | [`011` §7](../reviews/doing/011_master_backlog_phase3_V043-REV.md) | same `008` |

**Closed / do-not-extend:** [`sprint6B/`](sprints/sprint6B/) · [`sprint7_8/`](sprints/sprint7_8/) (partial S7/S8 already landed; leftovers live as `S7-B-01` / `S7-B-05` in `011`).

### 0.5 Concept docs — navigate from work to law

| When you are working on… | Read first (normative) | Supporting |
|---|---|---|
| Boundaries, planes, spawn | [`03` Architecture](../main_v4/03_vanguard_architecture_planes_and_execution_model_v040.md) | [`001`](../reviews/doing/001_executive_architectural_review_V043-REV.md), [`003`](../reviews/doing/003_core_architecture_and_coupling_V043-REV.md) |
| Wire / Claim / corrections | [`04` Contracts](../main_v4/04_vanguard_core_contracts_and_wire_schema_v040.md) | `S8-J-01`, `S8-A-04/05` |
| Kernel / grants / sandbox | [`05` Kernel](../main_v4/05_vanguard_kernel_capabilities_and_security_v040.md) | |
| Measurement / A/A / promotion | [`07` Loop & measurement](../main_v4/07_vanguard_loop_engineering_and_measurement_v040.md) · [`13_C` GTS MVP](../main_v4/13_C_gts_mvp_program_and_engineering_plan.md) | [`002`](../reviews/doing/002_measurement_and_evidence_integrity_V043-REV.md) |
| Decisions / gate status | [`09` Decision register](../main_v4/09_vanguard_decision_register_v040.md) (`ADR-0063`…`0065`, `DECISION-0005`) | |
| Deferred / rejected | [`10` Deferred & rejected](../main_v4/10_vanguard_deferred_and_rejected_register_v040.md) | [`011` §8](../reviews/doing/011_master_backlog_phase3_V043-REV.md) |
| Implementer practice | [`development_guides/`](development_guides/) (`00`…`05`, TDD, boundaries) | |

### 0.6 Frontend gap (honest)

| Expected | Status today |
|---|---|
| `docs/front_v4/` | **Missing** — create as FE concept set (mirror `main_v4` discipline: registry + one owner per contract) |
| `docs/scrum/sprints_front/` | **Missing** — create FE Wave 1–4 kits with `FE-xxx` IDs matching the table below |
| Interim FE architecture | [`development_guides/cli_tui_architecture.md`](development_guides/cli_tui_architecture.md) |
| FE task rows in this roadmap | **Staging only** until moved into `sprints_front/` + a FE backlog sibling of `011` |

Until those folders exist, FE work must still obey: client of the runtime only — no second control plane ([`cli_tui_architecture.md`](development_guides/cli_tui_architecture.md)).

### 0.7 Are we badly organized?

**Backend Phase 3: no — if you follow one chain.** The intended pattern is already SOTA for this repo:

`main_v4` (law) → `reviews/doing` (why) → `011` (what + status) → `sprints/sprintNN` (how) → code.

Mess appears when people treat **this roadmap**, **old `sprint7_8/`**, **reviews**, and **`011`** as four equal boards. They are not.

**What is messy today (fix later, do not invent parallel systems):**

| Issue | Fix |
|---|---|
| ROADMAP duplicates `011` without status authority | Keep roadmap as mirror; flip status only in `011` |
| `sprint7_8/` vs `sprint07`/`sprint08` | Treat `sprint7_8/` as archive; active kits are zero-padded `sprint07`…`10` |
| FE “Sprint 1–4” vs backend “Sprint 7–10” | Rename speech to **FE Wave 1–4**; keep `FE-xxx` IDs |
| No `front_v4` / `sprints_front` | Create them with the **same** folder pattern as backend — do not put FE law into `main_v4` or FE tasks into `011` |
| Many review files | Cap `doing/` at 8; archive via `009` rulings |

**For three developers:** follow sprint order + lane write scopes. They do not need to reconcile every review file daily — only `011` + their lane kit + linked `main_v4` anchors.

---

## 1. Roadmap overview

Phase 3 closes the **four MVP questions** (`GTS-13C` Ch. 10) in strict order. Frontend work can proceed in parallel on the **interaction plane** (CLI / TUI / IDE), but must not invent a second control plane or bypass the kernel.

| Horizon | Focus | Client-visible outcome |
|---|---|---|
| **Now — Sprint 7** | Subtraction & boundary restoration | Honest Q1: every effect through `Kernel.dispatch` |
| **Next — Sprint 8** | Recursion, resume, load-bearing manifests | Useful recursion + real policy digests |
| **Then — Sprint 9** | Measurement instrument (A/A floor) | Q3: measurable, refuse degenerate claims |
| **Gate — Sprint 10** | Generality (TableWorld) + four-question review | Shipable v0.4.3 claims only |
| **Parallel — Frontend** | CLI demo → live daemon → IDE fork | Instant demo, then installable CLI, then desktop IDE |

---

## 2. How to read this board

| Column | Meaning |
|---|---|
| **ID** | Backend: `S<sprint>-<lane>-<nn>` from [`011`](../reviews/doing/011_master_backlog_phase3_V043-REV.md). Frontend: `FE-<wave><nn>` (staging until `sprints_front/`) |
| **Cx** | Complexity **0–100** (planning heuristic) |
| **Tier** | Experience needed: ★ very simple → ★★★★★ principal / tech lead |
| **Days** | Effort-days heuristic (recalibrate after Sprint 7 actuals) |
| **LOC** | Estimated delta (negative = deletion) |
| **Depends** | Hard prerequisites before the row may start |

> Estimates are **planning heuristics for staffing — not contracts**. Normative truth stays in `docs/main_v4/`. Status flips live only in `011`.

---

## 3. Wave map & MVP gates

| Wave | Sprint | Theme | Closes |
|---|---|---|---|
| **W6** | **S7** | Subtraction & boundary restoration | **Q1** |
| **W7** | **S8** | Recursion, resume, load-bearing manifests, ACI | Q1, Q2 |
| **W8** | **S9** | The instrument: A/A floor, splits, oracles, dogfood | **Q3** |
| **W9** | **S10** | Generality: domain de-capture, TableWorld, the gate | **Q4** |

| Gate | Question | Required evidence (summary) |
|---|---|---|
| **Q1** | Boundary real? | No second execution path; architecture tests fail planted counterparts |
| **Q2** | Useful? | Three real bugs fixed interactively; honest “would you reach for it again?” |
| **Q3** | Measurable? | A/A floor vs `vg-shell-only`; paired comparison with interval |
| **Q4** | General? | TableWorld added; core-change line count published |

Full gate text: [`GTS-13C`](../main_v4/13_C_gts_mvp_program_and_engineering_plan.md) Ch. 10 · status: [`ADR-0064`](../main_v4/09_vanguard_decision_register_v040.md).

---

## 4. Staffing model

| Lane | Owner | Write scope |
|---|---|---|
| **A** | Senior A — Control Plane | `tools/check_boundaries`, `repo_paths`, `runtime/**`, `test/runtime` |
| **B** | Senior B — Workload & Evidence | `agency/manifests`, `adapters`, `test/agency`, `test/lab` |
| **C** | Senior C — Measurement & Lab | `benchmarkings/**`, LAM mock, `lab/**`, `test/broken` |
| **J** | Tech + Project Lead — Joint | `docs/main_v4`, `LICENSE`, secrets history |
| **FE** | Frontend track | `vanguard/clients/cli/**`, `vanguard-ide/**` |

---

## 5. Delivery playbook (ASAP)

1. **Single tracker** — Update only [`011_master_backlog_phase3_V043-REV.md`](../reviews/doing/011_master_backlog_phase3_V043-REV.md) statuses. Sprint kits under [`docs/scrum/sprints/sprint07..10/`](sprints/) are the playbooks. Do not open new review docs (cap = 8).
2. **Order of sprints (do not skip)** — S7 subtraction (Q1) → S8 recursion/manifests (Q1/Q2) → S9 instrument (Q3) → S10 TableWorld + gate (Q4). Features before S7 exit gate contaminate every later measurement.
3. **Daily rhythm** — Morning: pick next `[TODO]` in your lane with depends met → mark `[IN_PROGRESS]` in `011`. PR cites ≥1 `req_id`. Done only when DoD command passes. Hand-off file conflicts via PR comment (especially `runtime/root.py`).
4. **Client ASAP definition** — Client delivery = Sprint 10 four-question gate with evidence pack (`S10-C-03` / `S10-J-01`), not green CI alone. Ship honest claims only (`S10-J-03`). Parallelize ACI (`S8-B-06..09`) and junior tasks (`S7-A-07`, `S7-J-05`, `S8-B-08`, `S10-A-02`) to keep seniors on spawn / resume / A/A / TableWorld.
5. **Frontend fast path** — Demo (`FE-203` + `FE-104`) → live wire (`FE-101`/`102`/`201`) → IDE fork (`FE-301`…). Promote rows into `sprints_front/` before treating them as authoritative.

---

# BACKEND

## Phase 3 Task Board — Sprints 7–10

**Task provenance:** every backend row below is a staffing mirror of [`011_master_backlog_phase3_V043-REV.md`](../reviews/doing/011_master_backlog_phase3_V043-REV.md). Playbooks: [`sprint07`](sprints/sprint07/) … [`sprint10`](sprints/sprint10/). Concepts: [`docs/main_v4/`](../main_v4/). Delivery narrative: [`008`](../reviews/doing/008_v043_delivery_plan_sprints_7_10_V043-REV.md).

Estimates are planning heuristics (complexity 0–100, LOC Δ, effort-days) for staffing — not contracts. Normative truth stays in `docs/main_v4/`.

### Snapshot

| Metric | Value |
|---|---|
| Total tasks | **81** |
| Open | **77** |
| Done | **4** |
| Open effort (sum) | **~147d** |
| Lane A open | **~40d** |
| Lane B open | **~42d** |
| Lane C open | **~42d** |
| Joint open | **~23d** |

### Staffing snapshot

Three coding lanes are already defined (A/B/C) plus Joint for leads. Parallelism works only inside a sprint’s dependency order — Sprint 7 subtraction first. Net open LOC Δ ≈ 9445 (negative = deletion). Calendar ~8–10 weeks per delivery plan 008 if lanes stay full-time.

### Task table

Columns: ID · Sprint/Wave · Lane · Status · Task · Sub-tasks · Surfaces · Cx · Why · Files · LOC · Modules · Tier · Effort · Depends · Notes

| ID | S/W | Lane | Status | Task | Sub-tasks | Code / surfaces | Cx | Why complex | Files | LOC | Modules | Tier | Days | Depends | Notes |
|---|---|---|---|---|---|---|---:|---|---:|---:|---|---|---:|---|---|
| S7-A-01 | S7 W6 | A | TODO | Lattice-completeness CI rule | 1 Extend LT-1..LT-8 table · 2 Plant broken counterpart · 3 Wire CI | check_boundaries.py table extend; test/broken/ | 25 | Mechanism exists; mainly table + planted fail case. | 3 | 40 | tools/check_boundaries.py | ★★☆☆☆ junior | 1 | — | Do early; unblocks other boundary rules. |
| S7-A-02 | S7 W6 | A | TODO | No-subprocess-outside-sandbox rule | 1 Rule · 2 Broken counterpart · 3 CI | AST import rule + planted import | 30 | AST walk already there; edge cases in imports/tests. | 3 | 50 | tools/check_boundaries.py | ★★★☆☆ mid | 1 | — | Prerequisite for deleting runtime/loops. |
| S7-A-03 | S7 W6 | A | TODO | No-evaluator-import rule | 1 Ban agency/runtime → evaluators · 2 Broken counterpart | import-graph rule | 35 | Need correct allowed/denied path matrix. | 3 | 60 | tools/check_boundaries.py | ★★★☆☆ mid | 1.25 | — | Pairs with A-02 before MetaLoop delete. |
| S7-A-04 | S7 W6 | A | TODO | DELETE runtime/loops/ | 1 Delete package + test · 2 Confirm no importers · 3 Salvage map in PR | delete runtime/loops/**, test_meta_loop.py | 40 | Deletion is easy; verifying no silent importers + salvage mapping is the work. | 8 | -400 | runtime/loops/MetaLoopEngine (delete) | ★★★★☆ senior | 2.5 | S7-A-02, S7-A-03 | REJECTED to rebuild. Net LOC strongly negative. |
| S7-A-05 | S7 W6 | A | TODO | DELETE runtime/coordination.py | 1 Delete · 2 Unwire root.py · 3 Convert test → ledger projection | coordination.py, root.py:712-723,793; projections | 55 | Must re-home depth/budget semantics into ledger projections without breaking resume later. | 5 | -200 | runtime/coordination, runtime/root, ledger/projections | ★★★★☆ senior | 2.25 | S7-A-04 | Depth returns as S8-C-01 projection. |
| S7-A-06 | S7 W6 | A | TODO | Remove hardcoded composition values | 1 bwrap via which · 2 approval TODO→S8-B-04 · 3 Reservation from budget_policy | root.py:659,693,775 | 35 | Small edits; careful not to invent S8 policy early. | 2 | 40 | runtime/root.compose | ★★★☆☆ mid | 1.25 | — | approval_required_above stays TODO until S8-B-04. |
| S7-A-07 | S7 W6 | A | TODO | Repair docs/agile→docs/scrum restructure breakage | 1 repo_paths.py · 2 Fix 3 tests/contracts | tools/repo_paths.py + 3 tests | 15 | Path string fix + green the 3 known failures. | 4 | 20 | tools/repo_paths | ★☆☆☆☆ very simple | 0.5 | — | Day-1 unblocker for everyone. |
| S7-B-01 | S7 W6 | B | TODO | Canonical alias shape + fail-closed validation | 1 Flat {alias:verb} · 2 Migrate tests · 3 Assert targets ∈ verbs · 4 Schema names ∈ aliases∪verbs · 5 Broken counterpart | agency/manifests/loader.py:41-71, aliases.json, tests | 50 | Data vs test migration choice + fail-closed without breaking good packs. | 10 | 120 | agency/manifests/loader.to_canonical | ★★★☆☆ mid | 2 | — | Turns 3 red alias tests green. |
| S7-B-02 | S7 W6 | B | TODO | Unread component = composition error | 1 compose() asserts consumer · 2 Broken orphan component | runtime/root.compose, domain/artifacts/manifest | 45 | Needs consumer registry mapping; touches shared root.py (Lane A owns). | 4 | 80 | runtime/root.compose, Manifest | ★★★★☆ senior | 1.5 | S7-B-01 | Coordinate with A on root.py. |
| S7-B-03 | S7 W6 | B | TODO | Metamorphic policy-digest test | 1 Mutate context_policy · 2 Assert ≥1 observable differs | test/agency/test_manifest_metamorphic.py (new) | 30 | Writing a good red metamorphic test; goes green in S8-B-02. | 1 | 80 | test only (intentionally red) | ★★★☆☆ mid | 1.25 | S7-B-02 | Expected FAIL until Sprint 8. |
| S7-B-04 | S7 W6 | B | TODO | Emit gene_digests into results | 1 Already at root.py:606-609 · 2 Emit RunResult + result.json K_compat | runtime/root, zero_hint_v1/run_live_agent.py | 25 | Plumbing; gene_digests already computed. | 3 | 40 | Runtime.RunResult, K_compat | ★★☆☆☆ junior | 1 | — | Quick win for measurement honesty. |
| S7-B-05 | S7 W6 | B | TODO | Fix test_bench alias KeyError | 1 Undeletability guard currently errors first | test/lab/test_bench.py | 20 | Depends on B-01 alias shape. | 2 | 30 | lab bench tests | ★★☆☆☆ junior | 0.75 | S7-B-01 | Exit-gate item for S7. |
| S7-C-01 | S7 W6 | C | TODO | benchmarkings/ dependency gate | 1 Only runtime.root + ports · 2 Broken counterpart | check_boundaries.py | 30 | Import allowlist design. | 3 | 50 | tools/check_boundaries | ★★★☆☆ mid | 1 | — | Before deleting runners. |
| S7-C-02 | S7 W6 | C | TODO | benchmarkings/guard.py refusal conditions | 1–7 refusal labels + broken counterparts | benchmarkings/guard.py (new); reuse MOCK verdict.py | 60 | 7 refusal conditions + correct numerator/denominator exclusion. | 6 | 250 | benchmarkings.guard, verdict helpers | ★★★★☆ senior | 2.75 | — | Core of Q1 measurement integrity. |
| S7-C-03 | S7 W6 | C | TODO | DELETE four bypassing runners | 1–4 named runners | swe_pro_tiers/*, run_agentic_live_challenge, run_live_proof | 35 | Delete + grep proof + update docs/refs. | 8 | -600 | benchmarkings runners (delete) | ★★★☆☆ mid | 3 | S7-C-01 | Critical finding #2 remediation. |
| S7-C-04 | S7 W6 | C | TODO | Retraction sweep | 1 Move to _retracted · 2 Relabel probes · 3 9-label regime | benchmarkings/** JSON + RETRACTION.md | 40 | Judgement calls on which rows are probes vs claims. | 15 | 80 | benchmarkings artifacts (relabel) | ★★★☆☆ mid | 1.5 | S7-C-03 | Communication hygiene for client. |
| S7-C-05 | S7 W6 | C | TODO | Promote honest runner | 1 Sole entrypoint zero_hint_v1 · 2 Label · 3 labDepartures | benchmarkings/zero_hint_v1/ | 25 | Mostly docs + entrypoint discipline. | 4 | 40 | run_live_agent.py | ★★☆☆☆ junior | 1 | S7-C-03 | Pairs with B-04 digests. |
| S7-C-06 | S7 W6 | C | TODO | models.json top fail-closed | 1 top:[] · 2 models_for_band raises · 3 Reconcile band names | tools/002_LLM_API_MOCK/models.json, models.py | 20 | Band rename reconciliation is fiddly. | 3 | 40 | LAM models_for_band | ★★☆☆☆ junior | 0.75 | — | Spend control. |
| S7-J-04 | S7 W6 | J | TODO | SEC-01 remediation | 1 Rotate · 2 History rewrite · 3 Remove refs/original · 4 Force-update · 5 Verify --all-refs + clean clone · 6 CI strict mode | git history, tools/scan_secrets.py CI | 70 | Provider rotate + authorized rewrite + remote force + clone verification; irreversible ops. | 2 | 30 | scan_secrets CI; git ops (owner-only) | ★★★★★ principal/TL | 2.25 | repo owner auth | Never put secret in tickets. Parallel early. |
| S7-J-05 | S7 W6 | J | TODO | Add LICENSE | Apache-2.0 matching pyproject | LICENSE | 5 | Copy text. | 1 | 200 | LICENSE | ★☆☆☆☆ very simple | 0.75 | — | 5 minutes. |
| S7-J-06 | S7 W6 | J | TODO | Promote measurement science into VG-07 | C1–C12 · labels · splits · FUAA · evidence levels | docs/main_v4/07_…, VG-00 §6 | 55 | Large normative edit; must not invent new contracts. | 3 | 400 | VG-07, VG-00 | ★★★★★ principal/TL | 3 | — | Can parallel with coding lanes. |
| S7-J-07 | S7 W6 | J | TODO | Review WIP protocol | Cap doing/ at 8; closure headers | VG-00 §11 | 15 | Process write-up. | 1 | 60 | VG-00 | ★★★★☆ senior | 0.75 | — | Prevents getting lost in loops. |
| S7-J-08 | S7 W6 | J | TODO | ADR-0066 MCP adapter rules (pre-record) | EffectAdapter only · untrusted tool list · privileged egress | VG-09 register | 25 | Careful ADR wording; no code. | 1 | 80 | ADR register | ★★★★★ principal/TL | 1 | — | Phase 4 deferred; record now. |
| S8-A-01 | S8 W7 | A | TODO | Decompose execute_harness | compose / HarnessSession / run; one Kernel per run; inject ports | runtime/root.py → HarnessSession | 75 | Large refactor of composition root; three Kernels today. | 8 | 350 | Runtime.execute_harness, HarnessSession (new) | ★★★★☆ senior | 3.5 | S7 exit | Biggest S8 control-plane unlock. |
| S8-A-02 | S8 W7 | A | TODO | Suspend/resume from ledger | Terminal-with-continuation; re-entry reduces ledger; delete segment loop | EpisodeEngine / ledger reduce | 90 | Correctness-critical; max_turns across approval; digest identity. | 10 | 400 | EpisodeEngine, ledger, approval path | ★★★★★ principal/TL | 4 | S8-A-01 | S8 exit-gate centerpiece. |
| S8-A-03 | S8 W7 | A | TODO | RandomPort + ClockPort complete | Byte-identical replay; Recording drives counterfactuals | ports + adapters fakes | 55 | All nondeterminism sources must be inventoried. | 6 | 180 | RandomPort, ClockPort, Recording | ★★★★☆ senior | 2.25 | S8-A-01 | Enables V5-A later. |
| S8-A-04 | S8 W7 | A | TODO | RecordCorrection parse_wire | Reject invalid style+general; round-trip valid; no promotion | parse_wire(CorrectionRecord) | 35 | Schema + rejection paths. | 4 | 80 | CorrectionRecord, parse_wire | ★★★☆☆ mid | 1.25 | — | D-07. |
| S8-A-05 | S8 W7 | A | TODO | Claim as domain type | Non-empty invalidation; ≥1 automatic; support fields recorded-not-consumed | domain/ Claim type + parse | 65 | New domain type + C-12 auto-stale semantics. | 6 | 220 | domain.Claim | ★★★★☆ senior | 2.75 | S8-J-01 (wire) | Coordinate with Joint wire amendment. |
| S8-B-01 | S8 W7 | B | TODO | EpisodeEngine.spawn | Attenuated grant · child lease · depth budget · causationId · no handle return · destroy workspace | agency/episode, kernel/attenuation, Governor | 95 | Property tests on attenuation + budget conservation two levels deep. | 12 | 450 | EpisodeEngine.spawn, attenuation, Governor | ★★★★★ principal/TL | 4.25 | S7 boundary rules | Highest S8 risk; Lane B primary. |
| S8-B-02 | S8 W7 | B | TODO | CompactionStrategy protocol + registry | result_eviction, recency_window; selected by context_policy | compaction registry + compose freeze | 70 | Protocol design + observable change proof. | 8 | 280 | CompactionStrategy, context_policy | ★★★★☆ senior | 3 | S7-B-03 | Salvage from rejected MetaLoop. |
| S8-B-03 | S8 W7 | B | TODO | ModelRouter protocol + registry | Wire adapters/models/routing.py; selected by routing_policy | routing.py (exists unwired) | 55 | Existing code; wiring + freeze-at-compose. | 6 | 150 | ModelRouter, routing_policy | ★★★★☆ senior | 2.25 | — | ACI harvest related. |
| S8-B-04 | S8 W7 | B | TODO | approval_policy manifest component | Replace hardcoded low threshold | manifest component + compose | 45 | Closes S7-A-06 TODO. | 5 | 120 | approval_policy | ★★★☆☆ mid | 1.75 | S7-A-06 | Mid complexity. |
| S8-B-05 | S8 W7 | B | TODO | Operator context isolation | Fresh child compiler prefix; only return enters parent L5 | context compiler / L5 | 70 | Subtle context-leak bugs; needs strong test. | 5 | 150 | context compiler, spawn return path | ★★★★☆ senior | 2.5 | S8-B-01 | VG-03 §10.3. |
| S8-B-06 | S8 W7 | B | TODO | ACI-1 paginated fs.read | 100 lines + offset; schema + prompt convention | fs.read adapter + schema | 30 | Straightforward adapter change. | 4 | 80 | fs.read | ★★☆☆☆ junior | 1.25 | — | Parallelizable ACI batch. |
| S8-B-07 | S8 W7 | B | TODO | ACI-2 succinct fs.search | File hits first, capped snippets | fs.search | 30 | Similar to B-06. | 3 | 70 | fs.search | ★★☆☆☆ junior | 1.25 | — | ACI batch. |
| S8-B-08 | S8 W7 | B | TODO | ACI-3 empty-output acknowledgement | Silent command → explicit text | proc.exec | 15 | Tiny adapter fix. | 2 | 25 | proc.exec | ★☆☆☆☆ very simple | 0.5 | — | Junior-friendly. |
| S8-B-09 | S8 W7 | B | TODO | ACI-4 lint-on-patch observation receipt | Syntax failure is receipt never verdict | patch.apply observation path | 40 | Must not invent evaluator path. | 4 | 90 | patch.apply receipts | ★★★☆☆ mid | 1.5 | — | A-05 sensitive. |
| S8-B-10 | S8 W7 | B | TODO | ACI-6 maxTurns from budget_policy | Engine reads frozen policy | budget_policy → EpisodeEngine | 35 | Must survive approval boundary (with A-02). | 4 | 70 | budget_policy, max_turns | ★★★☆☆ mid | 1.25 | S8-A-02 (hard bound across approval) | D-12. |
| S8-C-01 | S8 W7 | C | TODO | Depth as ledger projection | Atom…Body labels as projection never classes | ledger/projections | 55 | Semantic remapping after S7-A-05 delete. | 5 | 180 | ledger projections (depth labels) | ★★★★☆ senior | 2.25 | S7-A-05 | Salvage of rejected class hierarchy. |
| S8-C-02 | S8 W7 | C | TODO | Cache-hit-rate metric over fixed replay | Prefix-stability CI metric | telemetry + CI | 50 | Need stable replay harness for metric. | 5 | 150 | prefix/cache metrics | ★★★☆☆ mid | 2 | S8-A-03 helpful | 006 S5. |
| S8-C-03 | S8 W7 | C | TODO | V5-L prefix-miss attribution | system/tools/compact/snip reasons | telemetry on model calls | 55 | Instrumentation across compiler stages. | 6 | 160 | context compiler telemetry | ★★★★☆ senior | 2.25 | S8-C-02 | Feeds cost control. |
| S8-C-04 | S8 W7 | C | TODO | LAM schema t0-/t6- regex reconciliation | Corpus and validator agree | LAM corpus + validator | 35 | Regex/corpus alignment grind. | 5 | 60 | LAM schemas | ★★☆☆☆ junior | 1.25 | — | Junior/mid friendly. |
| S8-J-01 | S8 W7 | J | TODO | VG-04 wire amendment for Claim | Optional reader fields · golden vectors · migration rehearsal | schemas/v4, VG-04, golden vectors | 60 | Wire is forever; migration care. | 6 | 200 | VG-04, schemas/v4 Claim | ★★★★★ principal/TL | 2.5 | pairs S8-A-05 | Do before Claim code merges. |
| S8-J-02 | S8 W7 | J | TODO | Confirm ADR-0060 through recursion | Zero domain vocab in agency/episode; TCB budget | TCB + review | 25 | Review discipline not coding. | 1 | 20 | ADR-0060 check | ★★★★★ principal/TL | 0.75 | S8-B-01 ongoing | Continuous during S8. |
| S8-J-03 | S8 W7 | J | TODO | Q1/Q2 evidence review + preregister dogfood bugs | Name 3 bugs before seeing harness behave | ADR-0064 updates | 40 | Scientific integrity judgement. | 2 | 80 | ADR-0064, dogfood prereg | ★★★★★ principal/TL | 1.5 | S7 Q1 progress | Before S9 dogfood runs. |
| S9-C-01 | S9 W8 | C | TODO | Wire M-18 instrument tuple | Emit into result.json; refuse lift without tuple equality; fail closed on placeholders | tools/telemetry/tuple.py → runners | 55 | Exists; wiring + refuse paths + placeholder detection. | 6 | 120 | telemetry.tuple, result.json | ★★★★☆ senior | 2 | S7-B-04 digests | Finding 0b from INDEX. |
| S9-C-02 | S9 W8 | C | TODO | Pre-registration artifact | Hypotheses/metrics/alpha/hash before arms; fix status drift | lab prereg + CI gate | 60 | Process + tooling + status machine. | 7 | 200 | preregistration store/CI | ★★★★☆ senior | 2.5 | — | T8.4. |
| S9-C-03 | S9 W8 | C | TODO | A/A runner | Identical manifest vs itself; N repeats; ≥3 classes; refuse degenerate/zero floor | new A/A runner + CI | 85 | Scientific core of Q3; refusal logic + floors. | 10 | 400 | A/A runner, vg-shell-only control | ★★★★★ principal/TL | 4 | S7-C-02, S9-C-01 | Expect large floor (9.5–20 pts). |
| S9-C-04 | S9 W8 | C | TODO | Statistics module | McNemar · paired bootstrap · survival; no p at n<20 | stats module | 70 | Correct stats + guardrails against misuse. | 5 | 300 | lab/statistics | ★★★★★ principal/TL | 3 | S9-C-03 | PhD-adjacent care. |
| S9-C-05 | S9 W8 | C | TODO | Splits + touch ledger | DEV/HOLDOUT/SEALED/LIVE/DEPLOYMENT; one-way burn | split membership + ledger | 65 | Policy + enforcement + burn recording. | 6 | 220 | splits M-19/M-20 | ★★★★☆ senior | 2.75 | — | Prevents cheating the floor. |
| S9-C-06 | S9 W8 | C | TODO | Oracle hardening | Audit substring asserts; mutation + isomorphic perturbation | oracle suites | 60 | Many suites; mutation design per class. | 12 | 250 | adapters/evaluators oracles | ★★★★☆ senior | 2.75 | — | bug-001 already property oracle. |
| S9-C-07 | S9 W8 | C | TODO | Seeded-sabotage suite | Plant proxy-exploiters; confirm rejection | test/broken sabotage candidates | 50 | Adversarial cases must be realistic. | 5 | 150 | sabotage suite | ★★★★☆ senior | 2 | S9-C-06 | T8.8. |
| S9-B-01 | S9 W8 | B | TODO | Real reconstructions | Rebuild 3 packs differ on ≥3/10 dims; REFERENCE.md | reconstruction packs | 55 | Needs S8 compaction/routing/approval real. | 20 | 300 | claude/opencode/swe-mini packs | ★★★☆☆ mid | 2.75 | S8-B-02,03,04 | lab harness diff proof. |
| S9-B-02 | S9 W8 | B | TODO | vg harness build\|run\|diff\|bench | lab/ entrypoint first (D-10) | lab/{build,run,diff,bench}.py | 50 | Partial work exists; finish + stabilize JSON. | 8 | 200 | lab CLI | ★★★☆☆ mid | 2.25 | S9-B-01 helpful | Client-facing lab UX. |
| S9-A-01 | S9 W8 | A | TODO | Surface instrument fields on RunResult | gene_digests, composition digest, instrument-error, int turn/token/cost | RunResult API | 40 | API surface + serialization. | 5 | 100 | RunResult | ★★★☆☆ mid | 1.5 | S7-B-04 | Unblocks Lane C. |
| S9-A-02 | S9 W8 | A | TODO | Integer telemetry discipline | Integer micros/tokens/USD micros; no float truth | telemetry types | 45 | Hunt floats across stack. | 8 | 120 | telemetry numeric types | ★★★☆☆ mid | 1.75 | — | S6B-MD-009. |
| S9-A-03 | S9 W8 | A | TODO | Recording sufficiency for benchmark replay | Record gaps vs Phase 4 V5-A | Recording | 50 | Audit completeness judgement. | 4 | 100 | Recording | ★★★★☆ senior | 1.75 | S8-A-03 | Gap doc acceptable. |
| S9-A-04 | S9 W8 | A | TODO | Ledger query support for paired runner | Queries Lane C needs | ledger query API | 45 | API design for paired comparisons. | 4 | 120 | ledger queries | ★★★★☆ senior | 1.75 | — | Hand-off to C. |
| S9-J-01 | S9 W8 | J | TODO | Q2 dogfood ×3 | 3 real bugs; interactive; no mid-run hand-patch; reason codes; honest judgement | dogfood runs + signed judgement | 50 | Operational + honesty; not LOC. | 3 | 40 | evidence pack / receipts | ★★★★☆ senior | 1.75 | S8-J-03 prereg | Calendar time > coding. |
| S9-J-02 | S9 W8 | J | TODO | Pre-registration sign-off | Countersign hashes; Holm–Bonferroni; no optional stopping | process + ADR | 35 | Process rigor. | 2 | 40 | prereg governance | ★★★★★ principal/TL | 1.25 | S9-C-02 | Lead duty. |
| S9-J-03 | S9 W8 | J | TODO | Spend authorisation | Cloud after local patch.apply; top=[]; 10 calls→ledger line | spend policy | 25 | Policy enforcement. | 2 | 40 | models spend gate | ★★★★☆ senior | 1 | S7-C-06 | Protect budget. |
| S9-J-04 | S9 W8 | J | TODO | Q3 evidence review | Floor? paired interval? gap number or dated why-not? | ADR-0064 | 40 | Honest gate judgement. | 1 | 40 | ADR-0064 | ★★★★★ principal/TL | 1.25 | S9-C-03..05 | End of S9. |
| S10-A-01 | S10 W9 | A | TODO | Domain de-capture | Move verb/args/selector binding out of invocation.py into manifest capability row | adapters/models/invocation.py → manifest rows | 80 | Rip coding-domain leak without breaking packs. | 10 | 300 | invocation.py, capability rows | ★★★★★ principal/TL | 3.5 | S8 manifests load-bearing | Do BEFORE TableWorld. |
| S10-A-02 | S10 W9 | A | TODO | proc.test binding | Prefer allowlisted proc.exec; delete orphan | KNOWN_TOOLS / DEFAULT_BINDINGS | 25 | Small consistency fix. | 3 | 40 | tool bindings | ★★☆☆☆ junior | 1 | — | Quick. |
| S10-A-03 | S10 W9 | A | TODO | BlobStorePort + IndexPort | Fake + real each | ports + adapters | 55 | New ports + fakes + wiring. | 8 | 250 | BlobStorePort, IndexPort | ★★★★☆ senior | 2.5 | — | GTS-13C §5.2. |
| S10-A-04 | S10 W9 | A | TODO | vg why \<artifact\> | Evidence activated · predicts · demote conditions | CLI/client command | 60 | UX + evidence graph traversal. | 6 | 200 | clients/cli why, Claims | ★★★★☆ senior | 2.5 | S8-A-05 Claim | T6.5. |
| S10-B-01 | S10 W9 | B | TODO | TableWorld | Versioned tables; select/derive/update/validate; invariants; no VCS/shell/paths | new EnvironmentAdapter + packs + evaluator | 90 | Whole new domain through standard adapter; 4 VG-08 stories. | 25 | 700 | TableWorld EnvironmentAdapter | ★★★★★ principal/TL | 5 | S10-A-01 | Q4 centerpiece. Non-zero kernel LOC is a finding. |
| S10-B-02 | S10 W9 | B | TODO | Core-change detector CI | Count lines in kernel/episode/wire; fail reconstruction PRs that touch | CI script | 35 | CI + policy. | 3 | 80 | tools core-change detector | ★★★☆☆ mid | 1.25 | — | Build early while TableWorld lands. |
| S10-B-03 | S10 W9 | B | TODO | structured_consolidate → StructuredRecord | Incl. deadEnds; quality via transcript-replacement replay | consolidate path | 70 | Replay measurement design. | 8 | 250 | StructuredRecord, consolidate | ★★★★☆ senior | 3 | — | 004 G6. |
| S10-B-04 | S10 W9 | B | TODO | regroundPolicy as authorised observation effect | Traverse Kernel.dispatch | reground effect path | 55 | Must go through kernel grants. | 5 | 140 | regroundPolicy effect | ★★★★☆ senior | 2 | — | 004 G7. |
| S10-C-01 | S10 W9 | C | TODO | Instrument unchanged on second domain | A/A, splits, stats on TableWorld; no special case; floors not pooled | reuse S9 instrument | 50 | Finding if special-cased. | 5 | 100 | A/A runner × TableWorld | ★★★★☆ senior | 1.75 | S10-B-01, S9-C-03 | Symmetric to C-10. |
| S10-C-02 | S10 W9 | C | TODO | Verifier–deployment gap dashboard + freeze | Build freeze now even if nothing to freeze | dashboard + freeze hook | 55 | Policy + logging while promotion absent. | 6 | 180 | gap dashboard, freeze | ★★★★☆ senior | 2.25 | S9 instrument | T8.7. |
| S10-C-03 | S10 W9 | C | TODO | Gate evidence pack | Commands+outputs; include negatives | evidence pack docs/artifacts | 40 | Assembly + honesty. | 8 | 100 | gate evidence pack | ★★★☆☆ mid | 1.5 | all S10 exit evidence | Client deliverable. |
| S10-J-01 | S10 W9 | J | TODO | Four-question gate review | Named evidence per Q1–Q4 | ADR-0064 evaluation | 50 | Executive judgement under evidence rules. | 2 | 60 | gate review | ★★★★★ principal/TL | 1.75 | S10-C-03 | Client milestone. |
| S10-J-02 | S10 W9 | J | TODO | Reverse ADR-0064 per gate honestly | Unproven gates stay unreversed | VG-09 | 35 | Integrity. | 1 | 40 | ADR-0064 | ★★★★★ principal/TL | 1.25 | S10-J-01 | — |
| S10-J-03 | S10 W9 | J | TODO | Claim discipline at v0.4.3 | Publish only proven; no AGI/SOTA language | README, release text | 20 | Editorial. | 3 | 50 | README | ★★★★☆ senior | 0.75 | S10-J-01 | NC-01. |
| S10-J-04 | S10 W9 | J | TODO | Phase 4 authorisation | Evaluate O-01/O-03; order V5 from 010 starting V5-A | decision + 010 | 40 | Roadmap judgement. | 2 | 60 | Phase 4 auth | ★★★★★ principal/TL | 1.5 | S9 floor (O-01) | After gate. |

### Critical path (cx ≥ 70 or tier 5)

| ID | Task | Lane | Cx | Tier | Days | Why |
|---|---|---|---:|---|---:|---|
| S8-B-01 | EpisodeEngine.spawn | B | 95 | ★★★★★ | 4.25 | Property tests on attenuation + budget conservation two levels deep. |
| S8-A-02 | Suspend/resume from ledger | A | 90 | ★★★★★ | 4 | Correctness-critical; max_turns across approval; digest identity. |
| S10-B-01 | TableWorld | B | 90 | ★★★★★ | 5 | Whole new domain through standard adapter; 4 VG-08 stories. |
| S9-C-03 | A/A runner | C | 85 | ★★★★★ | 4 | Scientific core of Q3; refusal logic + floors. |
| S10-A-01 | Domain de-capture | A | 80 | ★★★★★ | 3.5 | Rip coding-domain leak without breaking packs. |
| S8-A-01 | Decompose execute_harness | A | 75 | ★★★★☆ | 3.5 | Large refactor of composition root; three Kernels today. |
| S7-J-04 | SEC-01 remediation | J | 70 | ★★★★★ | 2.25 | Provider rotate + authorized rewrite + remote force + clone verification; irreversible ops. |
| S8-B-02 | CompactionStrategy protocol + registry | B | 70 | ★★★★☆ | 3 | Protocol design + observable change proof. |
| S8-B-05 | Operator context isolation | B | 70 | ★★★★☆ | 2.5 | Subtle context-leak bugs; needs strong test. |
| S9-C-04 | Statistics module | C | 70 | ★★★★★ | 3 | Correct stats + guardrails against misuse. |
| S10-B-03 | structured_consolidate → StructuredRecord | B | 70 | ★★★★☆ | 3 | Replay measurement design. |
| S8-J-01 | VG-04 wire amendment for Claim | J | 60 | ★★★★★ | 2.5 | Wire is forever; migration care. |

### How to deliver ASAP

#### 1. Single tracker

Update only `011_master_backlog_phase3_V043-REV.md` statuses. Sprint kits under `docs/scrum/sprints/sprint07..10/` are the playbooks. Do not open new review docs (cap = 8).

#### 2. Assign by lane (3 developers)

| Lane | Owner | Write scope | Start with |
|---|---|---|---|
| A | Senior A — Control Plane | check_boundaries, repo_paths, runtime/**, test/runtime | S7-A-07 → A-01..03 → A-04/05 → A-06 |
| B | Senior B — Workload & Evidence | agency/manifests, adapters, test/agency, test/lab | S7-B-01 → B-05 → B-02 → B-04 → B-03(red) |
| C | Senior C — Measurement & Lab | benchmarkings/**, LAM mock, lab/**, test/broken | S7-C-01 → C-03 → C-02 → C-04/05 → C-06 |
| J | Tech + Project Lead — Joint | docs/main_v4, LICENSE, secrets history | S7-J-05, J-07 parallel; J-04 (SEC) ASAP with owner auth |

#### 3. Order of sprints (do not skip)

S7 subtraction (Q1) → S8 recursion/manifests (Q1/Q2) → S9 instrument (Q3) → S10 TableWorld + gate (Q4). Features before S7 exit gate contaminate every later measurement.

#### 4. Daily rhythm

Morning: pick next [TODO] in your lane with depends met → mark [IN_PROGRESS] in 011. PR cites ≥1 req_id. Done only when DoD command passes. Hand-off file conflicts via PR comment (especially runtime/root.py).

#### 5. Client ASAP definition

Client delivery = Sprint 10 four-question gate with evidence pack (S10-C-03 / S10-J-01), not green CI alone. Ship honest claims only (S10-J-03). Parallelize ACI (S8-B-06..09) and junior tasks (S7-A-07, S7-J-05, S8-B-08, S10-A-02) to keep seniors on spawn/resume/A/A/ TableWorld.

---

# FRONTEND

## Interaction-plane task board

**Task provenance (staging):** rows below are **not** yet owned by a `docs/front_v4/` registry or `docs/scrum/sprints_front/` kits — those folders **do not exist yet**. Until they do, treat this table as a draft backlog. Interim architecture: [`cli_tui_architecture.md`](development_guides/cli_tui_architecture.md). Prefer speech **FE Wave 1–4** (not “Sprint 1”) so IDs never collide with backend Sprint 7–10.

| Task ID | Sub-Tasks | Description | Feature / Code | Sprint & Wave | Complexity (0–100) | Files & LOC | Modules & Classes | Tier |
|---|---|---|---|---|---|---|---|---|
| FE-101 | • Socket connect • NDJSON frame parser • RPC caller • Event dispatcher | Build resilient UDS & Named Pipe client with auto-reconnect and frame buffering. | LiveDaemonClient handleData() callRPC() scheduleReconnect() | Sprint 1 Wave 1 | 65 / 100 Stream chunk boundary splitting & network reconnection resilience. | 2 files ~320 LOC | vanguard/clients/cli/ • adapters/live.ts • contract/wire.ts | 4★ Senior Dev |
| FE-102 | • Keypair generation • RFC 8785 JCS • Ed25519 signing • Key storage (0600) | Cryptographic operator signer for approving high-risk agent capabilities outside Python memory. | OperatorSigner canonicalize() signApproval() | Sprint 1 Wave 1 | 75 / 100 RFC 8785 byte canonicalization and asymmetric signature parity with Python. | 2 files ~180 LOC | vanguard/clients/cli/ • adapters/signer.ts • application/signer.ts | 4★ Senior / Tech Lead |
| FE-103 | • Session hook • Ring buffer (5k) • Token stream reducer | React hook managing session lifecycle (idle → running → waiting_approval). | useVanguardRun useEventStream resolveApproval() | Sprint 1 Wave 1 | 50 / 100 Managing fast-firing state events without UI stutter or re-render lag. | 2 files ~260 LOC | vanguard/clients/cli/ • ui/hooks/useVanguardRun.ts • application/session.ts | 3★ Normal Dev |
| FE-104 | • Stream renderer • Diff viewer • Approval modal • Budget gauge | React + Ink visual components for token streaming, thinking collapsible, diffs, and prompts. | \<StreamRenderer\> \<DiffViewer\> \<ApprovalModal\> \<BudgetMeter\> | Sprint 1 Wave 1 | 55 / 100 Terminal Flexbox layout math and ANSI color formatting. | 5 files ~580 LOC | vanguard/clients/cli/ • ui/StreamRenderer.tsx • ui/DiffViewer.tsx • ui/ApprovalModal.tsx | 3★ Normal Dev |
| FE-105 | • CLI main entry • Ink render bootstrap • Unit test suite | CLI entrypoint bootstrap and unit tests using ink-testing-library. | main.ts tui.tsx render() | Sprint 1 Wave 1 | 45 / 100 Terminal lifecycle and exit signal handling (SIGINT/SIGTERM). | 3 files ~220 LOC | vanguard/clients/cli/ • main.tsx • tui.tsx • test/tui.test.ts | 3★ Normal Dev |
| FE-201 | • Health probe • Auto-spawn daemon • Lockfile & PID • /shutdown command | Auto-supervise Python background daemon on vg launch without user intervention. | DaemonSupervisor checkHealth() spawnDaemon() stopDaemon() | Sprint 2 Wave 2 | 70 / 100 Cross-platform process detachment, PID file locks, orphan process reaping. | 2 files ~290 LOC | vanguard/clients/cli/ • runtime/supervisor.ts • runtime/paths.ts | 4★ Senior Dev |
| FE-202 | • Fetch manifests • Manifest card • Grant badges • Budget tuner | Interactive manifest selector (vg-code-default, vg-code-swe-mini, vg-shell-only). | ManifestExplorer \<ManifestCard\> tuneBudget() | Sprint 2 Wave 2 | 45 / 100 Dynamic form generation and CLI prompt routing. | 2 files ~240 LOC | vanguard/clients/cli/ • application/ManifestExplorer.ts • ui/ManifestCard.tsx | 3★ Normal Dev |
| FE-203 | • Replay adapter • JSONL fixtures • --demo CLI flag | Zero-API-key interactive demo mode with realistic token streaming delays for presentations. | ReplayAdapter streamFixture() demoCLI() | Sprint 2 Wave 2 | 40 / 100 Simulating asynchronous timers and keystroke mock events. | 4 files ~310 LOC | vanguard/clients/cli/ • adapters/replay.ts • fixtures/sessions/*.jsonl | 2★ Junior / Mid Dev |
| FE-204 | • Binary packaging • install.sh script • Shell PATH config | NPM package configuration and one-line zero-dependency curl \| sh installer script. | npm run build install.sh configurePath() | Sprint 2 Wave 2 | 50 / 100 Cross-platform shell portability (POSIX sh, Bash, Zsh, PowerShell). | 2 files ~180 LOC | • vanguard/clients/cli/package.json • tools/distribution/install.sh | 3★ DevOps / Senior |
| FE-301 | • Track Code-OSS • Strip MS telemetry • Open-VSX config • Dark theme assets | Debloat Code-OSS / VSCodium base: remove Microsoft telemetry, accounts, and proprietary URLs. | scrub_code_oss.sh product.json gulpfile.vscode.js | Sprint 3 Wave 3 | 80 / 100 Navigating upstream VS Code build systems, Gulp pipelines, and patching product configs. | 3 files ~380 LOC | vanguard-ide/ • product.json • tools/ide/scrub_code_oss.sh | 5★ Principal / Lead |
| FE-302 | • Extension manifest • WebviewProvider • React bundle embed • CSP headers | Built-in VS Code extension embedding React Vanguard interface in the Secondary Sidebar. | VanguardViewProvider resolveWebviewView() postMessage() | Sprint 3 Wave 3 | 65 / 100 Webview security sandbox isolation and React packaging in VS Code. | 4 files ~420 LOC | vanguard-ide/extensions/ • vanguard-panel/src/extension.ts • VanguardViewProvider.ts | 4★ Senior Dev |
| FE-303 | • Extension socket • Bidirectional relay • Stream persistence | Extension Host Node.js socket connecting Webview to local Vanguard daemon over UDS. | DaemonBridge onMessage() forwardToDaemon() | Sprint 3 Wave 3 | 60 / 100 Three-way event propagation: Webview ↔ Extension Host ↔ Python Socket. | 2 files ~290 LOC | vanguard-ide/extensions/ • vanguard-panel/src/DaemonBridge.ts | 4★ Senior Dev |
| FE-304 | • Active file watcher • Cursor selection • Git branch reader • Context bar pill | Live editor context sync: inject active file, cursor range, and git status into Vanguard prompt bar. | WorkspaceContext onDidChangeActiveEditor getGitStatus() | Sprint 3 Wave 3 | 50 / 100 VS Code Extension API subscription management and debounce optimizations. | 2 files ~260 LOC | vanguard-ide/extensions/ • vanguard-panel/src/WorkspaceContext.ts | 3★ Normal Dev |
| FE-401 | • Monaco decorations • CodeLens buttons • Inline diff sign • Clear highlights | Render proposed agent code changes directly in the active editor with [Accept & Sign] buttons. | InlineDiffProvider ApprovalCodeLens applyDecoration() | Sprint 4 Wave 4 | 75 / 100 Monaco editor text range calculation and coordinate-accurate inline diff painting. | 2 files ~360 LOC | vanguard-ide/extensions/ • InlineDiffProvider.ts • ApprovalCodeLens.ts | 4★ Senior Dev |
| FE-402 | • Secret regex engine • Masking formatter • DLP rule config | Local Data Loss Prevention filter redacting API keys, passwords, and PII before API calls. | DLPFilter maskSecrets() loadBlocklist() | Sprint 4 Wave 4 | 55 / 100 High-speed non-backtracking regex parsing over large codebase buffers. | 2 files ~220 LOC | vanguard/clients/cli/ • application/dlp.ts • vanguard-panel/src/DLPFilter.ts | 3★ Normal Dev |
| FE-403 | • Headless E2E tests • Vector conformance • 100-run soak test | Comprehensive E2E test suite running real SWE tasks against live daemon and mock engine. | run_e2e_scenarios() verify_vectors() run_soak_test() | Sprint 4 Wave 4 | 60 / 100 Orchestrating multi-process test runners and verifying 0-leak memory profiles. | 3 files ~340 LOC | vanguard/clients/cli/ • test/e2e/*.test.ts • tools/ci/run_soak.sh | 4★ QA / Senior Dev |
| FE-404 | • Linux AppImage • Windows MSI installer • macOS DMG build | Desktop application packaging for Linux, Windows, and macOS with embedded runtimes. | package-desktop.sh InnoSetup.iss build_matrix.yml | Sprint 4 Wave 4 | 70 / 100 Cross-platform binary code signing, bundling embedded runtimes and DLLs. | 4 files ~280 LOC | vanguard-ide/build/ • package-desktop.sh • tools/release/build_matrix.yml | 4★ DevOps / Release |

## Simple Execution Instructions: What to Do & How (Fast Delivery)

To deliver this product to your client as quickly and cleanly as possible, follow this exact sequence:

### Step 1: Deliver the Instant Demo Beta (Within 2–3 Days)

• Assign TASK-FE-203 and TASK-FE-104 to 1 or 2 developers.
• Hook up the React+Ink terminal UI to replay.ts with the pre-recorded fixture.
• Client Deliverable: Run `npx @vanguard/cli --demo`. The client immediately sees a beautiful Claude Code-level terminal UI streaming tokens, showing diffs, and requesting operator approvals with zero setup or API keys.

### Step 2: Wire Up the Live Python Backend (Sprint 1 & 2)

• Implement TASK-FE-101 (LiveDaemonClient) and TASK-FE-102 (OperatorSigner).
• Implement TASK-FE-201 (DaemonSupervisor) so that when the user runs vg, it automatically starts the Python backend daemon in the background invisibly.
• Client Deliverable: `curl -fsSL https://your-domain.com/install.sh | sh` gives the user a working live AI coding CLI on their machine.

### Step 3: Launch the VS Code Fork (Sprint 3 & 4)

• Run the Code-OSS debloating script (TASK-FE-301) to strip Microsoft telemetry and brand the IDE.
• Embed the React UI inside the Secondary Sidebar (TASK-FE-302 & TASK-FE-303).
• Hook up the live file watcher and inline Monaco diffs (TASK-FE-304 & TASK-FE-401).
• Client Deliverable: A standalone IDE (like Cursor / Windsurf) distributed as an .AppImage (Linux) and .exe / .msi (Windows).
