---
id: adr-0093-aether-higgs-v070-release-baseline
adr: 0093
class: decision
authority: binding-decision
canonical_for:
  - aether-higgs-v070-release-baseline
  - zero-breakage-rebrand-convention
status: accepted
owner: engineering-director
version: "0.7.0"
last_verified: 2026-08-24
accepted_date: 2026-08-24
extends:
  - ADR-0088
  - ADR-0089
  - ADR-0092
supersedes: []
superseded_by: null
---

# ADR-0093 — AETHER — Higgs Release Baseline (v0.7.0)

## Context

The repository has achieved baseline composition convergence (M-3C), completed product runtime profiles (W-3D), and established an empirical measurement workflow (ADR-0092). The primary project identity is **AETHER**, while major release iterations receive named release titles. The v0.7.0 major release is designated the **Higgs** update ("AETHER — Higgs Release v0.7.0").

To prevent breaking import paths, git refactoring conflicts, and linter regressions across 1,300+ tests, the rebrand is executed at the metadata, specification, and execution documentation surface without mutating the underlying `vanguard/packages/` module paths on disk.

## Decision

1. **Version Baseline & Release Branding:** The official repository version is updated to `0.7.0` across `pyproject.toml`, `README.md`, `docs/SPEC.md`, `docs/03_execution/sprint_active.md`, and `docs/03_execution/milestones.md`. The release designation is **AETHER — Higgs Release (v0.7.0)**.
2. **Substrate & Import Invariance:** The physical directory structure under `vanguard/packages/` (`domain`, `ports`, `kernel`, `agency`, `runtime`, `adapters`) remains unchanged. Internal Python imports (`from vanguard.packages...`) remain canonical.
3. **Core Invariants Preserved:** The Trusted Computing Base ceiling ($\le 1438$ LOC), S0–S12 effect dispatch pipeline, 6D typed budget algebra, monotonic attenuation, SQLite-WAL event store, and exterior signed evaluator boundaries remain strictly binding and unaffected by the documentation/metadata version bump.

## Consequences

- The project baseline is locked at **AETHER — Higgs Release (v0.7.0)**.
- All existing contract, kernel, security, and falsifier tests remain 100% green without refactoring churn.
