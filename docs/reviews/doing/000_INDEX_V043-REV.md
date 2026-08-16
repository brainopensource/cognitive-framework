# 000 — Index: Aether Vanguard v0.4.3 Review Set

**Date:** 2026-08-16 · **Branch/HEAD:** `sprints7-8/integration` @ `0238b1a`
**Status:** NON-NORMATIVE. Not in `docs/main_v4/00_vanguard_registry_v040.md` Ch. 2.
Where any of these files and a v4 owner disagree, the owner wins (`PR-3`).
**Scope reviewed:** `docs/main_v4/` (VG-00…VG-12 + GTS-13C, 4,928 lines) · `vanguard/packages/`
(93 files, 15,569 LOC) · `schemas/v4/` · `test/` (507 cases executed) · `benchmarkings/` ·
`docs/reviews/todo/` (10 documents) · `docs/superpowers/plans/` (3 documents) · 2026 external
literature.

---

## Read in this order

| # | Document | Owns | Read if you are |
|---|---|---|---|
| **001** | [Executive Architectural Review](001_executive_architectural_review_V043-REV.md) | The ruling, severity-ranked findings, MVP-gate status, the order of work | **everyone — start here** |
| **002** | [Measurement & Evidence Integrity](002_measurement_and_evidence_integrity_V043-REV.md) | Benchmark triage, evidence-class labelling, the A/A programme, what we may and may not say | Tech Lead, measurement, anyone about to publish a number |
| **003** | [Core Architecture & Coupling](003_core_architecture_and_coupling_V043-REV.md) | The three-loop problem, recursion, resume, the composition-root decomposition, layer contracts | Senior A + Senior B |
| **004** | [Cognition, Competence & Self-Improvement](004_cognition_competence_and_self_improvement_V043-REV.md) | $G_C/G_E/A_t$, operators-as-data, memory and library drift, context engineering, what to defer | Research Lead, Tech Lead |
| **005** | [The Harness Manifest Framework](005_harness_manifest_framework_V043-REV.md) | What a manifest must express before `C-01` is testable; decorative fields; S7 repairs | Senior B, product |
| **006** | [Tech Stack, Protocols & Polyglot Seams](006_tech_stack_protocols_and_polyglot_seams_V043-REV.md) | Python ratification and the `ADR-0001` defect, MCP/ACP/A2A posture, performance levers, security | Tech Lead, Senior A |
| **007** | [Cleanup, Dedup & Docs Consolidation](007_codebase_cleanup_dedup_and_docs_consolidation_V043-REV.md) | The concrete delete/merge/relocate list; the review-WIP protocol | Everyone doing Sprint 7 |
| **008** | [Corrected v0.4.3 Delivery Plan, S7–S10](008_v043_delivery_plan_sprints_7_10_V043-REV.md) | The sprint plan, gates, deferrals with triggers, the stakeholder paragraph | Project Lead, Scrum, Tech Lead |

---

## The five findings that matter most

| # | Finding | Severity | Where |
|---|---|---|---|
| 1 | `runtime/loops/meta_loop.py` (Sprint 9) is a second agent loop that executes code outside the sandbox with no grant and **grades its own work** — inverting the project's central safety property | **Critical** | `001 §3.1`, `003 §2.1` |
| 2 | Four benchmark runners bypass `Runtime.execute_harness` entirely; the "3 harness manifest matrix" evaluated three hardcoded prompt strings, and **every row scored a task that had already passed before the agent acted** (`pre_passed:true`, `patch_length:0`) | **Critical** | `001 §3.2`, `002 §2` |
| 3 | Three of the four terms of $S_t=(G_C,G_E,L,A_t)$ are unimplemented; `A-02`/`L-3` "operators are data" — declared irreversible — has no code. And the `O-01` trigger that would license building them **can never fire, because the A/A floor does not exist** | **Critical** | `001 §3.3`, `004 §1–2` |
| 4 | The manifest is a prompt selector: `context_policy` and `routing_policy` are hashed into the composition digest and **read by nothing**, so two harnesses can differ in digest and be identical in behaviour. `C-01` is untested while being recorded as tested | **High** | `001 §3.4–3.5`, `005` |
| 5 | `EpisodeEngine` is depth-1 and non-recursive; the parent/child model that does exist (`runtime/coordination.py`) is a second budget ledger outside the event store | **High** | `001 §3.6`, `003 §3–4` |

---

## The verdict in one table

| `GTS-13C` Ch. 10 | Status | Blocker |
|---|---|---|
| **Q1** Is the boundary real? | **Partially, and regressed since `v0.4.0-sprint4`** | Two bypass paths execute effects outside the kernel |
| **Q2** Is it useful? | Not demonstrated | No record of three real bugs fixed interactively |
| **Q3** Is it measurable? | **No** | No A/A floor. The comparative results that exist are degenerate |
| **Q4** Is it general? | **No** | TableWorld does not exist; the coding domain has already leaked into `adapters/models/invocation.py` |

**Recommendation:** do not ship v0.4.3 as planned. Run the corrected plan in `008` —
Sprint 7 subtraction (≈1,500 LOC deleted, three architecture rules added, zero features),
then recursion, then the instrument, then generality. **8–10 weeks.**

---

## What is genuinely excellent and must not be churned

Stated first in `001 §2` and repeated here because remediation programmes reliably damage the
parts that were already right:

- **`kernel/dispatch.py`** — the S0–S12 sequence, every ordering rule traceable to a real shipped
  defect. Close to publishable. **Freeze; shrink only.**
- **`schemas/v4/`** — RFC 8785 canonicalisation with ~40 triples, ~60 selector-inclusion vectors,
  writer/reader profile split. This is the corpus format (`L-1`). **Freeze.**
- **`domain/selectors/resource_selector.py`** — a decidable per-kind inclusion relation that
  *denies* undefined pairs. This is what makes `L-02` real rather than aspirational.
- **`agency/context/compiler.py`** — prefix frozen at construction so stability is a property of
  the type; breakpoint ceiling raised at assembly; the brief compaction-exempt.
- **The refusing instruments** — `test/contracts/readers` refuses without node; there is
  deliberately no `FakeEvaluator` binding because *"absence is inconclusive, not a pass."*
  This instinct is the project's best cultural asset and `002 §3.2` extends it.
- **The v4 specification corpus itself** — `VG-02` and `VG-03` are the best charter/architecture
  pair I have reviewed on an agent programme, and they predicted every failure in this report:
  `RSK-04` (measurement theatre), `RSK-11` (core drift), `RSK-12` (ossification), `FT-10`
  (decorative switch), `A-10` (a gate that cannot fail), Ch. 14 (disposable becomes architecture).

**The specification is not the problem. It is the asset.** The problem is that delivery pressure
produced a second implementation path and nothing in CI forbade it — and the mechanism that
would have forbidden it (`T10.1` dependency gating, which successfully made `spike/` and
`slice/` disposable by construction) already exists and simply was never pointed at the new code.

Point it there. That is three rules and one day.

---

## Provenance

Prior review work that reached compatible conclusions and should be credited rather than
duplicated:

- `docs/reviews/todo/sota_harness_scientific_benchmarking_programme_2026-08-16.md` — reached the
  benchmark-integrity conclusion independently, on the same day. **Correct, and not actioned.**
  `002` supersedes its triage section with per-file rulings.
- `docs/reviews/todo/phases_0-2_review_full_rev2.md` — the Beta/GA fence in its §7.1 is good
  practice and survives into `008`.
- `docs/reviews/todo/vanguard_harness_cli_architectural_review_phase_2*.md` — the three-evidence-level
  model and the produto/harness/modelo/protocolo separation should be **promoted into `VG-07`**,
  not left as review material.

`007 §5` gives the closure ruling for all ten prior documents and the WIP protocol that stops an
eleventh from being written before these are closed.
