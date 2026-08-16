# T0 reproduction evidence

This file preserves the three real repository defects used for schema archaeology. The repository's `.git` directory contains no usable history, so the original source snapshots cannot be recovered by commit. The observations below were captured while fixing the repository on 2026-08-14; current file digests identify the accepted repairs.

## BUG-01 — audit silently inspected zero documents

- Shape: single-file.
- Original behavior from repository root: `python3 tools/audit_v4.py` printed `BROKEN: none` and exited zero.
- Root cause: `DOCS = glob.glob("[0-9][0-9]_vanguard_*.md")` and `REGISTRY = "00_vanguard_registry_v040.md"` were resolved against the caller's working directory, not the repository.
- Repair: `tools/audit_v4.py` resolves its own repository root and changes to `docs/v4` before discovery.
- Accepted evidence: the repaired tool discovers the registered corpus and `tools/cv_checks.py` reports registry/disk equality for documents `00` through `12`.
- Accepted file digest: `sha256:38647f7ed43030751c77162d0ab7e01f173d59908ddf4a7c70abadaf873739e7`.

## BUG-02 — acceptance verification crashed from repository root

- Shape: multi-file because the verifier invokes the audit and word-count tools.
- Original behavior: `python3 tools/cv_checks.py` raised `FileNotFoundError: 00_vanguard_registry_v040.md` in `harvest_rows()`.
- Root cause: registry/document paths and nested tool paths each assumed a different working directory.
- Repair: `cv_checks.py` anchors on its repository root, changes to `docs/v4`, and invokes audit/word-count tools by absolute paths; `audit_v4.py` was made independently cwd-safe.
- Accepted evidence: `12/12 mechanical checks pass` from repository root.
- Accepted file digest: `sha256:cd1f1d302c65c7b8d17423b5ce336d1fd87a0c1b316730dc9e0b638fdd28f5cb`.

## BUG-03 — rule coverage falsely reported zero after a test run

- Shape: test-reactive; the defect became concrete only after the generator was run and its output inspected.
- Original behavior: `python3 tools/rule_test_map.py` printed `rules=0 tested=0 untestable=0 gaps=0`, exited zero, and created incorrectly named `docs/v4/rule-test-map.md` and `docs/v4/phase0-rule-backlog.md`.
- Root cause: inputs were globbed from the caller's directory while outputs were prefixed with `docs/v4`, an incompatible pair of cwd assumptions.
- Repair: anchor to repository root, change to `docs/v4`, and write the registered generated artifacts `00_rule-test-map.md` and `00_phase0-rule-backlog.md`.
- Accepted evidence: the generator reports `rules=203 tested=28 untestable=42 gaps=133`; the generated-file digests remain byte-identical across regeneration.
- Accepted file digest: `sha256:9097c1b1397f47a1076325197fd24220bdb3af34cfaa2b8c2ced9050f8a22bf4`.

## NONCODE-01 — authority and scope reconciliation

- Shape: structured reconciliation.
- Inputs: Sprint 0 mandate authority order, GTS-13C document map, six-package request, VG-03 topology, VG-04 wire ownership, VG-05 dispatch text.
- Invariants: one owner per contract; no silent conflict resolution; exact six top-level physical packages; GTS-13C owns no normative rule.
- Findings: standalone governance was absent from the requested six packages; universal dispatch language conflicts with privileged-only kernel mediation; GTS-13C selector/envelope projections differ from VG-04.
- Accepted result: `runtime/governance` mapping in the ICD; ADR-0051 records the mediation decision; VG-04 remains wire authority pending T0-driven schema ADRs.
- Residual: ADR-0051 requires the joint baseline approval recorded after archaeology review.

## Timing limitation

Command wall times were captured by the execution environment, but human hands-on time was not measured when these defects were originally fixed. No value is backfilled. This prevents claiming a human throughput baseline from these retrospective traces and is carried as `GAP-006` in the inventory.

