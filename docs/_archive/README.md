# Review-corpus archive note

> **NON-NORMATIVE / FROZEN PROVENANCE**
>
> This material preserves research and decision history. It cannot authorize implementation.
> Implementation work must cite current SPEC/law leaves, an accepted ADR, the active execution
> board, and a named executable falsifier. This banner covers `reviews/` and its `archive/proposals/`
> tree, plus the research corpus under `references/`. Historical links inside frozen documents may
> retain their original paths; the link linter resolves those provenance aliases without creating
> live compatibility stubs.

The v0.6 Concept Lock review corpus was consolidated during the Director review
(`ADR-0075`, [`003_V060_DIRECTOR_REVIEW.md`](reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/003_V060_DIRECTOR_REVIEW.md)).
Everything removed remains recoverable in git history at commit **`4f9f8b1`**.

Removed (durable conclusions absorbed into SPEC, ADRs `0069`–`0075`, annexes, GAMMA §2, and the `002` register):

- `OLD_TECH_LEAD_REVIEW_archive/` — Tech Lead / Principal Architect / AI Agentic / Systems-Eng
  advisory reviews and working logs; `CRITICAL_GAP_ANALYSIS_AND_AUDIT.md` (source of I-1…I-10);
  `NEXT_GEN_META_HARNESS_SPECIFICATION.md` (SPEC's direct ancestor); `01_SPECS_MIGRATION_MATRIX.md`;
  roadmap/sprint planning and purge TODO files.
- `TODO_DONT_COMMIT_BEFORE_DOING_IT_v2.md` — forensic TODO, closed as investigation.
- `PROMPT_ARCHITECTURE_CONCEPT_LOCK_V060.md` — prompt artifact.
- `PRINCIPAL_STAFF_ENGINEER_REVIEW/001_V060_concept_phase_{ALFA,BETA,DELTA}.md` — superseded by GAMMA.
- `PRINCIPAL_STAFF_ENGINEER_REVIEW/principal_engineer_proposal.md`,
  `Vanguard-substrate-060-full-refactor-v3-1.md`, `vanguard-substrate-060-execution-plan.md`,
  `vanguard-arquitetura-v4-parecer-e-plano.md`, `aether-v1-roadmap-waves.md` — advisory proposals,
  adjudicated (and where applicable rejected) by ADRs `0069`–`0074` and GAMMA §2.

Kept: [`VANGUARD_V060_FORENSIC_DISCOVERY.md`](reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/VANGUARD_V060_FORENSIC_DISCOVERY.md) (evidence cited by the lock ADRs),
[GAMMA](reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/001_V060_concept_phase_GAMMA.md) (lock plan),
[`002`](reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/002_V060_FOUNDATION_ROADMAP_AND_GAP_REGISTER.md) (historical gap register),
[`003`](reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/003_V060_DIRECTOR_REVIEW.md) (Director review).

## Proposal decision anchors

- [`001 — ALFA Tier S+ Architecture Decision Briefing`](reviews/archive/proposals/001_alfa_review_full_decision.md)
  records the final advisory disposition of proposals 002–008 and the corrections later reflected
  by accepted ADRs 0077–0084.
- [`006 — AETHER Tier S+ Master Architecture`](reviews/archive/proposals/006_fi_review_full_gptsol_proposal.md)
  is the detailed source proposal selected by 001. Its draft ADR numbers, schemas, paths, and version
  choices are historical and are superseded wherever the canonical SPEC or accepted ADRs differ.

These files validate design lineage; they do not reopen accepted decisions or authorize roadmap work.
