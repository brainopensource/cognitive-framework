# Staged plan — M0-code and M0-purge

**Status: staged, not active.** This plan is filed for when history-rewrite and skeleton work are
separately authorised — the Foundation Lock (`docs/MASTER_REFACTOR_GUIDELINE_FINAL.md`) is docs-only and
explicitly refuses to execute this as part of the concept-lock wave: *"Execute TECH_LEAD_REVIEW's M0 as
literally written (mass delete, git filter-repo, drop GUI/IDE, scaffold layer0/) [...] couples an
irreversible history rewrite to a concept lock that isn't signed yet."*

Struck from `docs/TECH_LEAD_REVIEW/03_SPRINTS_PARALLEL_EXECUTION_PLAN.md` §1's Sprint-1 board:
`S-M0-A-05` (history rewrite), `S-M0-B-01…06` (code skeleton, schemas, pytest migration), and frontend
deletion. These become active only after `docs/SPEC.md` is signed off and a human explicitly authorises
the irreversible steps below (force-push window, `git filter-repo` pass).

## M0-purge (Dev A lane, when authorised)

| ID | Task | Acceptance |
|---|---|---|
| S-M0-A-04 | Delete (after archive, not from live tree): confirm `docs/archive/v045/` covers everything `docs/TECH_LEAD_REVIEW/01_SPECS_MIGRATION_MATRIX.md` §0 named for deletion — it does, verify no gaps | `find docs -name '*.md' \| wc -l` trending toward ≤30 (M0-full target, not this wave's gate) |
| S-M0-A-05 | **History rewrite** (single `git filter-repo` pass): `SEC-01` `.env` blob, `lam.sqlite`, `tools/001_*/outputs/`, `runs/**`, sprint-evidence JSONL, `vanguard-gui/`, `vanguard-ide/`, `benchmark_results.json` | `python3 tools/scan_secrets.py --all-refs` PASS; `git count-objects -vH` ≤ 3 MB pack; purge manifest committed and co-signed |
| S-M0-A-06 | CI reset: drop TCB-LOC badge + test-count badge (once M1's metric triple lands — not before); add lane-ownership gate | pipeline green on rewritten `main` |

## M0-code (Dev B lane, when authorised)

| ID | Task | Acceptance |
|---|---|---|
| S-M0-B-01 | Scaffold `layer0/{events,kernel,spi,registry,scheduler,compose}/`, `plugins/`, `packs/`, `test/layer0/` with `__init__` stubs + lane ownership file | `check_lane_ownership.py` recognises all paths; empty-package import test green |
| S-M0-B-02 | Author `schemas/mhf/plugin.schema.json` + 6 golden vectors | vectors validate; invalid vectors fail with expected error paths |
| S-M0-B-03 | Author `schemas/mhf/harness.schema.json` + port `vg-code-default` to a draft `packs/code-default/harness.yaml` (non-executing) | schema-validates; digest computed via existing JCS |
| S-M0-B-04 | **SPI RFC** — freeze method sets for the five SPIs (`docs/adr/ADR-M0-03-five-spis.md`) + first-party ports | reviewed + signed; becomes the IF-1 checklist for M1 |
| S-M0-B-05 | Migrate `unittest discover` → `pytest` config for the retained suite | `pytest -q` green on retained set; port-map committed |
| S-M0-B-06 | Blob-store evidence relocation tool for purged sprint evidence | round-trip: `fetch(digest)` returns byte-identical artifact for 3 samples |

## Explicit gate before this plan activates

A human must sign off `docs/SPEC.md` as the concept lock, separately from approving this document's
existence. This file being staged is not that sign-off.
