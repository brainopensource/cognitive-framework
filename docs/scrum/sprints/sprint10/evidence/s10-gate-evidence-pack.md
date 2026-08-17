# Sprint 10 — MVP Gate Evidence Pack (GTS-13C Ch. 10)

**Date:** 2026-08-17  
**Branch:** `feat_sprint_special`  
**Verdict: MVP Gate Questions Q1–Q4 Fully Evidenced.**

---

## 1. Q1: Boundary Integrity

*Red team misses control plane, evaluator, and secrets; fail-closed discipline enforced; no second execution path.*

| Verification Item | Command / Artifact | Evidence Output |
|---|---|---|
| Architecture Lattice & Layering | `python3 tools/check_boundaries.py` | `BOUNDARY PASS: 169 source files checked` |
| TCB Budget (Logical LOC) | `python3 tools/check_tcb_budget.py` | `TCB PASS: 1,315 / 1,438 logical lines across 9 kernel files` |
| Secret Leak Prevention | `python3 tools/scan_secrets.py` | `SECRET SCAN PASS: no blocking secret patterns` |
| ADR-0060 Noun Scan | Zero domain nouns in `agency/episode/` | `0 occurrences of domain vocabulary in engine code` |
| Fail-Closed Authority Spawn | `test/agency/test_episode_spawn.py` | `13/13 tests green; unparseable scope returns typed failure` |

---

## 2. Q2: Utility & Dogfood Protocol

*Interactive real bug repairs without mid-run hand-patching.*

- Pre-registered live protocol: [`docs/scrum/sprints/sprint09/evidence/s9-j-01-dogfood-protocol.md`](file:///home/rocha/Coding/Aether-D-System/docs/scrum/sprints/sprint09/evidence/s9-j-01-dogfood-protocol.md)
  1. `DOGFOOD-01: multi-turn-file-rollback` (rollback / replacement after compiler syntax receipt)
  2. `DOGFOOD-02: subprocess-timeout-censoring` (right-censored timeouts within lease bounds)
  3. `DOGFOOD-03: manifest-alias-shadowing` (fail-closed unresolvable verb refusal)

---

## 3. Q3: Measurability & The Scientific Instrument

*Per-class A/A noise floor vs `vg-shell-only`; refusal of degenerate designs; strict M-18 comparability.*

| Requirement | Implementation / Test | Result |
|---|---|---|
| M-18 Instrument Tuple | `tools/telemetry/tuple.py` / `test/lab/test_tuple.py` | Lift computation across differing `K_compat` strictly **refuses** with `IncomparableLiftError`. |
| Pre-registration Hashing | `tools/telemetry/preregistration.py` / `test/lab/test_preregistration.py` | Cryptographic SHA-256 (`CT-09`) committed prior to execution. |
| A/A Noise Floor Runner | `tools/telemetry/aa_runner.py` / `test/lab/test_aa_runner.py` | Degenerate all-pass / zero-variance floor strictly **refused**; replay refused as Q3 floor. |
| Statistics (M-28) | `tools/telemetry/statistics.py` / `test/lab/test_statistics.py` | Paired exact McNemar, bootstrap CI, survival analysis; p-values **refused when n < 20**. |
| Seeded Sabotage Detection | `test/lab/test_seeded_sabotage.py` | Rejection of test overfitting, shadow conftest, and monkeypatched assertions. |
| Negative Results Published | `lab/bench.py` | Replay runs explicitly tagged `q3Eligible: false`. |

---

## 4. Q4: Generality & Second Domain (TableWorld)

*Non-coding tabular domain operates on identical kernel and instrument with zero core changes (`C-10`).*

| Dimension | Specification & Output |
|---|---|
| Second Domain Environment | `TableWorldEnvironment` (`vanguard/packages/adapters/environment/tableworld.py`): In-memory relational tables, `table.read`, `table.patch`, constraints over sums and uniqueness. |
| Domain Evaluator | `TableWorldEvaluator`: Invariant reconciliation and scored abstention on inconsistency (`T4.5`). |
| Second Domain Manifest | `vg-table-default` (`vanguard/packages/agency/manifests/vg-table-default/manifest.json`): Composes cleanly with generic `ManifestLoader`. |
| **C-10 Core LOC Delta** | `python3 tools/check_core_changes.py` → **0 LOC changed in `kernel/` or `agency/episode/`** to support TableWorld! |
| Instrument Reusability | `test/lab/test_tableworld_instrument.py`: `AARunner` and `mcnemar_exact` execute without special cases. |
