---
id: adr-0102-convergence-and-baseline-succession
adr: 0102
class: decision
authority: binding-decision
canonical_for:
  - 2026-08-26-convergence
  - m5a-baseline-disposition
  - successor-baseline
  - active-document-retirement
status: accepted
owner: engineering-leadership
version: "1.0.0"
last_verified: 2026-08-26
accepted_date: 2026-08-26
extends:
  - ADR-0095
  - ADR-0096
supersedes:
  - ADR-0097 Decision 5 baseline identity only
  - ADR-0098 Decision 7 baseline creation claim only
superseded_by: null
---

# ADR-0102 — 2026 Convergence and Experimental Baseline Succession

## Verified findings

At repository HEAD `15fbb7514ec3d8030da5259d2291acdf37c8686d`:

- the configured remote has no `refs/tags/M-5A-BASE-v2`;
- the local name is a lightweight tag at `1b4ce1a19e5d6ef2fd0575743fa60ecea0055fdd`;
- M-5b, M-6, M-6.5, M-7, and M-8 implementation files occur in that tag's ancestry;
- RF-86 fails because 111 protected-substrate lines were added after the tag;
- no repository RF-95 evidence bundle or independent M-4 review receipt exists.

The tag is therefore both unavailable to remote clean-clone CI and scientifically contaminated as a
control for successor features. Its historical local ref is preserved and never moved, deleted,
recreated, pushed as a valid control, or renamed into validity.

## Decision

1. `M-5A-BASE-v2` has disposition `CONTAMINATED_UNPUBLISHED`. It remains historical provenance,
   not an experimental baseline. Existing SAT execution is engineering demonstration/regression
   evidence, not admissible historical zero-substrate-diff proof.
2. After the convergence repairs, declared dependency installation, full qualified gates, and
   independent review are green, Leadership may create one annotated immutable successor tag named
   `CONVERGENCE-BASE-v1`. It must have a signed `aether.baseline/1` manifest binding tag object,
   commit, tree digest, package version, dependency lock, schema/reducer pins, prohibited treatment
   paths, required gate receipts, creator, and independent review.
3. The successor tag is not created during documentation convergence and is never treated as valid
   until it resolves on the configured remote and its manifest verifies.
4. After the successor baseline, M-5b is requalified with a materially different deterministic
   formal witness (graph coloring is the selected low-cost pack). RF-86 and RF-98 compare the new
   treatment to `CONVERGENCE-BASE-v1`. The SAT pack remains a regression domain.
5. M-4 is provisional for continued development only; M-5a mechanism is implemented but baseline
   acceptance is open; later milestones retain package or preparation states until ADR-0101
   evidence gates are met.
6. Leadership plans, duplicated reviews, and temporary sprint reports are archived as
   non-authorizing provenance after their decisions are absorbed. Canonical active planning is only
   `docs/03_execution/{milestones,backlog,sprint_active,sprint_upcoming}.md`.
7. No history rewrite, historical receipt reconstruction, tag-name reuse, or evidence backfill is
   authorized.

## Successor baseline verifier

The verifier must resolve the annotated remote tag, check tag-object and commit equality, recompute
tree and manifest digests, verify dependency/schema/reducer pins and independent signature, and
reject treatment contamination. Failure is `BLOCKED`, never a warning.

## Consequences

The existing missing-tag RF-86 default remains useful as a fail-closed historical diagnostic but
cannot close M-5b. The successor comparator must be introduced only with the reviewed baseline.
This decision changes experimental control provenance, not the architectural lattice or M-1 through
M-3 compatibility.
