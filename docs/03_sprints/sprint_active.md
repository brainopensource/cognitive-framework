---
id: SPRINT-M0-DOCS-ACTIVE
file: docs/03_sprints/sprint_active.md
title: "Active sprint — SUPERSEDED by v0.6.0 Concept Lock"
status: SUPERSEDED
milestone: historical M0 (of M0–M6); next work is Wave 0 after director approval
predecessor: v0.6.0 "Molecular Lattice" board (SUPERSEDED)
branch: feat/substrate_upgrade
spec: docs/SPEC.md
plan: docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/002_V060_FOUNDATION_ROADMAP_AND_GAP_REGISTER.md
last_reviewed: 2026-08-20
---

# Sprint board — SUPERSEDED (v0.6.0 Concept Lock)

**This M0 Docs Lock board is closed as a *next-work* document.**

The v0.5.0 Foundation Lock docs wave (SPEC collapse, ADR-M0-*, annexes, archive) remains historical
fact. It is **not** the authorization to start M1 “port the kernel into `layer0/`”.

**Current authority**

| Rank | File |
|---|---|
| Law | `docs/SPEC.md`, ADRs `0069`–`0074`, `docs/04_annex/{KERNEL,MEASUREMENT}.md` |
| Lock plan | `docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/001_V060_concept_phase_GAMMA.md` |
| Roadmap / gap register | `docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/002_V060_FOUNDATION_ROADMAP_AND_GAP_REGISTER.md` |

**Next authorized phase:** Engineering Director / Chief Engineer review of GAMMA + 002.  
**After approval:** Wave 0 (CI subject-of-record + named falsifiers).  
**Not authorized:** production coding, CI rewire, runtime convergence, plugin implementation, new sprint dates, or a replacement of this file with an M1 layer0 rewrite board.

The checklist below is the closed v0.5.0 docs-lock record. Do not reopen it as current work.

## 0. Law (historical)

Invariants I-1…I-11 (`docs/SPEC.md`). The v0.5.0 wave was docs-only.

## 1. Board (closed record)

- [x] Step 0 — Ground-truth verification (v0.5.0)
- [x] Step 1 — `docs/SPEC.md` authored (later rewritten at v0.6.0 Concept Lock)
- [x] Step 2 — `docs/05_adr/` minted (plus later `0069`–`0074`)
- [x] Step 3 — annexes landed (KERNEL destination amended at v0.6.0)
- [x] Step 4 — MERGE rows applied
- [x] Step 5 — Legacy corpus archived
- [x] Step 6 — `docs/02_roadmap/` rewritten (now historical; see 002)
- [x] Step 7 — This board rewritten (now superseded)
- [x] Step 8 — Hygiene: `CLAUDE.md` / `AGENTS.md` v0.6.0 pointers (Concept Lock)
- [x] Step 9 — `docs/SPEC.md` self-review against ADRs `0069`–`0074` (Concept Lock)

## 2. Explicitly not next

Kernel changes · event taxonomy · SPI implementations · plugin code · `layer0/` scaffolding as destination · pytest migration · Wave 0 CI YAML until director approval.

---

*Next board: none until director approval. Then Wave 0 as defined in 002, not `docs/03_sprints/plans/m1-m2-lanes.md` as written.*
