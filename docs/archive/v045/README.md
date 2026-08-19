# Archive v0.4.5

**Not normative.** The living spec is `docs/SPEC.md` (+ `docs/annex/`, `docs/adr/`). CI must not treat
any RFC-2119 language (MUST/SHALL/SHOULD) found in this tree as law — `tools/check_stale_paths.py` and
the markdown-link gate both exclude this directory from living-doc enforcement for exactly that reason.

This is evidence, not law. No ticket, ADR, or SPEC section may cite a file under here as a requirement —
only as historical context for *why* a decision was made. If content here still matters, it has already
been copied (not moved) into `docs/SPEC.md`, `docs/annex/`, or `docs/adr/` with its own citation; this
tree is the paper trail behind that citation, not a second copy of the requirement itself.

## What's here

- `01_specs/` — the full VG-00…VG-13C backend + frontend spec corpus (`docs/01_specs/backend/`,
  `docs/01_specs/frontend/`). Superseded by `docs/SPEC.md` per
  `docs/TECH_LEAD_REVIEW/01_SPECS_MIGRATION_MATRIX.md`.
- `00_executive/` — `vision.md` (the 14-tier cosmology, `docs/adr/ADR-M0-10-no-metaphysics.md`) and
  `pitch.md`. Killed as living content (AP-1); kept for archaeology only.
- `reviews/` — the `doing/`/`todo/` review-triage inbox. Triaged into
  `docs/02_roadmap/backlog.md` per `docs/TECH_LEAD_REVIEW/02_ROADMAP_BACKLOG_AND_REVIEW_TRIAGE.md` §2.
  `todo/deepseek_v050_review_and_v060_plan.md` in particular carries mismatched terminology
  (ALFA/BETA lane phrasing, "ArtifactNode/Edge Merkle-DAG", "Semantic Vector Index") not used anywhere
  else in this corpus — treat it as low-confidence source material, not an accepted design.
- `SYSTEM_SPEC_THEORY.md`, `SYSTEM_SPEC_ASBUILT.md` — the pre-lock theory/as-built pair. Their surviving
  content is absorbed into `docs/SPEC.md`.
- `SYSTEM_SPEC_DRIFTS.md` — the pre-lock drift diagnostic. Frozen, unabridged, at
  `docs/adr/DRIFT_REGISTER_v045.md`; this copy is kept alongside its THEORY/ASBUILT siblings for the
  section-mirrored cross-references between the three.

## Why archived, not deleted

`docs/MASTER_REFACTOR_GUIDELINE_FINAL.md` (the Foundation Lock guideline) is explicit: `git mv`, never
`rm`. History-rewrite, secret purge, and repo-size reduction are a **separately authorised** later wave
(`docs/03_sprints/plans/m0-code-and-purge.md`), not this one. This tree exists so that the archaeology
survives the docs collapse without keeping three competing sources of truth alive at once (the AP-2
anti-pattern this wave exists to end).
