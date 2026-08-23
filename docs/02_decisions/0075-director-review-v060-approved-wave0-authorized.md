---
adr: 0075
title: "Director review of the v0.6 Concept Lock: APPROVED; Wave 0 authorized; review corpus consolidated; four register additions; citation corrections"
status: accepted
source_section: "v0.6 Director Review"
---

# ADR-0075: Director review — v0.6 Concept Lock approved, Wave 0 authorized

**Context.** The Concept Lock (SPEC v0.6.0, ADRs `0069`–`0074`, annexes, GAMMA, the
`002` foundation register) was submitted for final independent Engineering Director review
at main `4f9f8b1` before production development. The review inspected the live system
(packages lattice, `layer0/` fork, kernel/agency/runtime, ledger, evaluator, sandbox,
packs), reran the full test suite as a fresh baseline (root discovery: 1119 tests, 7
failures, 5 errors, 8 skipped — matching GAMMA §9's snapshot), reran every static linter,
and verified the headline defects on disk (F1 fabricated pass at
`layer0/scheduler/driver.py`; fail-open ceiling at `layer0/spi/ceiling.py`; living CI
gating `test/layer0` while `test/kernel` is unwired). Frontend/CLI/TUI surfaces were out
of scope per the review mandate. Full findings:
`docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/003_V060_DIRECTOR_REVIEW.md`.

**Decision.**

1. **APPROVED.** The v0.6 Concept Lock (SPEC + ADRs `0069`–`0074` + `0075` +
   `docs/04_annex/{KERNEL,MEASUREMENT}.md`) is locked. The `002` foundation register is
   the living roadmap. **Wave 0 (CI subject-of-record + named falsifiers) is authorized
   as the next code change.** No Wave 0–4 implementation was performed in this review.

2. **Four additions to the gap register** (found during review; all Wave 0 scope,
   recorded as falsifiers F-18…F-21 in `002` §4.2):
   - **F-18 (I-7 enforcement scope).** `tools/check_domain_blindness.py` scans only
     `layer0/`; SPEC I-7 also covers `vanguard/packages/{domain,kernel}/`. The linter is
     weaker than the invariant it certifies.
   - **F-19 (silent test exclusion).** `test/integration/` and `test/governance/` lack
     `__init__.py`; their test modules are silently excluded from every discovery run.
     A test that cannot be collected is a false gate of the same family as lexical E-COV.
   - **F-20 (missing oracle registry artifact).** `preregistered_oracles.json` exists
     nowhere in the tree (it was **not** relocated; it vanished with `docs/sprint6B`).
     `repo_paths.preregistered_oracles()` points at a nonexistent file; Wave 0 must
     restore the artifact at a canonical path or retire the tests with a recorded reason.
   - **F-21 (translator lifting gaps are real).** The three `test_model_invocation`
     errors are genuine behavioral gaps in `ProposalTranslator`
     (`vanguard/packages/adapters/models/invocation.py`): the `parameters`-key call
     spelling and two fenced-payload forms degrade to prose (`kind: "finish"`). These are
     production-path adapter defects (or ahead-of-implementation tests), not stale tests.

3. **Citation corrections (docs-only, applied in this review).** `docs/archive/v045/`
   and `docs/TECH_LEAD_REVIEW/` are cited by SPEC and both annexes but do not exist on
   disk; the pre-lock corpus lives only in git history. Citations are amended to say so.
   This corrects false statements of fact in normative documents; no normative rule
   changes.

4. **Review-corpus consolidation executed.** After verifying their durable conclusions
   are absorbed into SPEC, ADRs `0069`–`0074`, the annexes, and GAMMA's adjudication
   tables, the following were **removed from the active tree** (all recoverable at git
   `4f9f8b1`): `docs/07_reviews/OLD_TECH_LEAD_REVIEW_archive/` (15 files),
   `TODO_DONT_COMMIT_BEFORE_DOING_IT_v2.md`, `PROMPT_ARCHITECTURE_CONCEPT_LOCK_V060.md`,
   and the superseded advisory/phase documents under `PRINCIPAL_STAFF_ENGINEER_REVIEW/`
   (ALFA, BETA, DELTA, `principal_engineer_proposal.md`, Full Refactor v3.1, execution
   plan, parecer v4, `aether-v1-roadmap-waves.md`). Kept: GAMMA (lock plan), `002`
   (living register), `VANGUARD_V060_FORENSIC_DISCOVERY.md` (evidence cited by ADRs),
   `003` (this review's report). `docs/07_reviews/ARCHIVE.md` records the removal.

5. **Test baseline is law until Wave 0 changes it.** `test/README.md` is the durable
   record of the fresh baseline: which suites are the production path, the expected reds
   and their verified root causes, and the intended CI subject of record. Its two
   incorrect root-cause claims (oracle registry "relocated"; model-invocation reds
   "legacy output shape") are corrected there.

**Alternative considered (and rejected).** BLOCKED verdict: rejected — every open defect
is honestly registered with a bound falsifier and an assigned wave; none contradicts the
locked concepts; blocking on already-registered Wave 0 work would repeat the
"docs claim done" inversion in the opposite direction. Fixing F-18…F-21 during this
review: rejected — they are code/CI changes, which this phase forbids. Keeping the full
review corpus: rejected — two competing plan corpora is how dual runtimes survived;
evidence belongs in git history once adjudicated.

**Evidence / bound test / links.** `003_V060_DIRECTOR_REVIEW.md` (fresh baseline tables);
`test/README.md`; `tools/check_domain_blindness.py`; `test/integration/`,
`test/governance/` (no `__init__.py`); `vanguard/packages/adapters/models/invocation.py`;
`002` §4.2 F-18…F-21.

**Reversal condition.** A newer ADR reopening a named P0 with evidence the lock is wrong
in substance. Regret about deleted evidence is not reversal (git history retains it).

**Owner · status.** Engineering Director / Chief Engineer · accepted · 2026-08-20
