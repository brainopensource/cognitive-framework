---
id: SPRINT-M0-DOCS-ACTIVE
file: docs/03_sprints/sprint_active.md
title: "Active sprint — v0.5.0 MHF M0: Docs Lock"
status: ACTIVE
milestone: M0 (of M0–M6, docs/SPEC.md §8)
predecessor: v0.6.0 "Molecular Lattice" board (SUPERSEDED — see docs/adr/ + docs/02_roadmap/backlog.md §1)
branch: feat/substrate_upgrade
spec: docs/SPEC.md            # the ONLY normative document
plan: docs/03_sprints/plans/m1-m2-lanes.md
last_reviewed: 2026-08-18
---

# Sprint board — M0: Docs Lock (Foundation Lock, v0.5.0 concept lock)

**Sentence this sprint makes true:**

> One normative spec + ADR log remain; the legacy spec/vision/review corpus is archived, not deleted;
> the roadmap and sprint board tell the same story as `docs/SPEC.md`; the repo-paths stale-doc bug is
> fixed — so M0-code and M1 can start on a documentation tree that agrees with itself.

This is **single-owner editorial work**, not the two-engineer M0 from
`docs/TECH_LEAD_REVIEW/03_SPRINTS_PARALLEL_EXECUTION_PLAN.md` §1 — that model is sized for parallel code
work (skeleton scaffolding, schema authoring) which this wave explicitly does not do. See
`docs/03_sprints/plans/m1-m2-lanes.md` for the full two-lane plan, staged for when M1 actually starts.

## 0. Law

Invariants I-1…I-11 (`docs/SPEC.md` preamble + §1.1). No runtime code changes this sprint — this is a
**docs-only** wave. Legacy `TSK-*` rows are closed only with `superseded_by:` pointers
(`docs/02_roadmap/backlog.md`).

## 1. Board

- [x] Step 0 — Ground-truth verification: `tools/repo_paths.py` dead `docs/scrum`/`docs/main_v4`
      sentinels fixed; `test/test_repo_paths.py` assertion corrected; `tools/check_stale_paths.py`
      widened to `docs/**/*.md`; `tools/check_schema_archaeology.py` retires gracefully on
      pre-purged evidence; D-05/D-06/D-07/D-08/D-42 re-verified live (not `[DONE]`-tag-trusted)
- [x] Step 1 — `docs/SPEC.md` authored from `NEXT_GEN_META_HARNESS_SPECIFICATION.md` + concept-lock
      deltas
- [x] Step 2 — `docs/adr/` minted: VG-09 split into 68 files, VG-10 copied to `DEFERRED_REJECTED.md`,
      ADR-M0-01…13 landed
- [x] Step 3 — `docs/annex/KERNEL.md` + `docs/annex/MEASUREMENT.md` landed with amendments
- [x] Step 4 — MERGE rows applied into `docs/SPEC.md` (folded into the Step 1 authoring pass)
- [x] Step 5 — Legacy corpus archived (`git mv`) to `docs/archive/v045/`; `docs/CONTRIBUTING.md` landed
- [x] Step 6 — `docs/02_roadmap/{milestones,backlog}.md` rewritten
- [x] Step 7 — This board rewritten; `docs/03_sprints/plans/{m0-code-and-purge,m1-m2-lanes}.md` staged
- [ ] Step 8 — Hygiene: README taxonomy removed, `CLAUDE.md`/`AGENTS.md` pointers updated
- [ ] Step 9 — `docs/SPEC.md` self-review for TBD/TODO/contradictions

## 2. Verification (this sprint's own gate)

```bash
python3 -m unittest test.test_repo_paths
python3 tools/check_schema_archaeology.py
python3 tools/check_stale_paths.py
python3 tools/check_markdown_links.py
grep -rnE "\b(MUST|SHALL|REQUIRED)\b" docs/ | grep -v "docs/SPEC.md" | grep -v "docs/annex/" | grep -v "docs/archive/"
python3 tools/check_boundaries.py
python3 tools/check_tcb_budget.py
```

## 3. Explicitly not this sprint

Kernel changes · event taxonomy · SPI implementations · any plugin code · `layer0/` scaffolding ·
`schemas/mhf/` · pytest migration · `coding_*` re-extraction into `packs/` (M3) · history rewrite /
secret purge / frontend deletion (staged in `docs/03_sprints/plans/m0-code-and-purge.md`, separately
authorised) · anything on the Phase-2/3 deferred list (`docs/adr/DEFERRED_REJECTED.md`).

---

*Next board: M0-code-and-purge (staged, `docs/03_sprints/plans/m0-code-and-purge.md`), then M1 Sprint 2
(`docs/03_sprints/plans/m1-m2-lanes.md` §2).*
