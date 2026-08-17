# Sprint 7 — Exit Gate Evidence Receipt

**Sprint:** 7 (Wave 6) — Subtraction & Boundary Restoration
**Integration branch:** `sprints7-8/integration` (canonical; `sprint7/integration` retired — see §5)
**Closed by:** Tech Lead + Project Lead (Joint track)
**Run date:** 2026-08-16
**Runner:** local `python3` 3.12, `node` **absent** (see §3)

This file is the structured `evidence_receipt` target for the covered rows in
`docs/scrum/sprints/sprint0/active-mvp-contract.json`. Every claim below is a command
and its observed output, not a summary.

---

## 1. The sentence Sprint 7 had to make true

> Every effect in every executable path in this repository traverses `Kernel.dispatch`, and an
> architecture test proves it by failing against a planted broken counterpart.

**Verdict: TRUE.** `check_boundaries.py` passes over 154 source files, and all 38 planted broken
counterparts are observed failing (§2).

---

## 2. Exit gate commands and observed output

| # | Command | Result |
|---|---|---|
| 1 | `python3 tools/check_boundaries.py` | `BOUNDARY PASS: 154 source files checked` (exit 0) |
| 2 | `python3 tools/run_broken_tests.py` | `BROKEN HARNESS PASS: 38 broken counterparts observed failing` (exit 0) |
| 3 | `python3 tools/check_tcb_budget.py` | `TCB PASS: 1315 logical lines across 9 files (alarm above 1438)` (exit 0) |
| 4 | `grep -rn "runtime.loops\|EpisodeCoordinator" vanguard/` | **empty** (exit 1 = no match) |
| 5 | `python3 -m unittest test.agency.test_manifest_loader` | `Ran 13 tests … OK` |
| 6 | `python3 -m unittest test.lab.test_bench` | `Ran 3 tests … OK` |
| 7 | `python3 -m unittest test.agency.test_manifest_metamorphic` | `Ran 1 test … OK` |
| 8 | `python3 tools/check_schema_archaeology.py` | `ARCHAEOLOGY STRUCTURE PASS: 4 traces, 26 append-only steps` (exit 0) |
| 9 | `python3 tools/check_sprint0_governance.py` | exit 0 |
| 10 | `python3 tools/check_stale_paths.py` | exit 0 |
| 11 | `python3 tools/check_markdown_links.py` | exit 0 |
| 12 | `python3 tools/check_pr_requirements.py` | exit 0 |
| 13 | `python3 tools/scan_secrets.py` | `SECRET SCAN PASS: no blocking secret patterns in scanned surfaces` (exit 0) |
| 14 | `python3 tools/check_baseline_manifest.py` | `BASELINE PASS: 8 local artifacts match APPROVAL-0002 manifest` (exit 0) |

Gate 2 detail — every planted counterpart reported
`{"expected_failure_observed": true, "result": "pass"}`, covering `MF-S0-001..009`,
`MF-KRN-001..011`, `MF-S7-A-01-001`, `MF-S7-A-02-001`, `MF-S7-A-03-001`,
`MF-S7-C-001`, `MF-S7-C-02-001..006`, `MF-S4-001`, `MF-GOV-001`, `MF-GOV-PATH-001`,
`MF-CTX-001..002`, `MF-SEC-002`, `MF-SEC-SCAN-001`, `MF-TEL-001`.

## 3. Full suite

```
python3 -m unittest discover -s test -t .
Ran 539 tests — errors=14, failures=0, skipped=2
```

All **14** remaining errors are `test.contracts.readers.ReaderUnavailable: node is required`
raised from `test/contracts/readers/__init__.py:40` because `node` is not installed on this
runner. The S7 exit gate admits exactly this class ("errors only from node-absent readers").
The reader deliberately refuses to degrade — a run without the TypeScript reader proves nothing
about cross-language agreement — so this is the harness working as designed, not a defect.

**On a runner with `node` present this must be 0 errors.** That is an S8 Joint check, not a
Sprint 7 debt: see `S8-J-02`.

## 4. Structural deletions confirmed on disk

| Path | Required state | Observed |
|---|---|---|
| `vanguard/packages/runtime/loops/` | gone | gone |
| `vanguard/packages/runtime/coordination.py` | gone | gone |
| `benchmarkings/swe_pro_tiers/runner.py` | gone | gone |
| `benchmarkings/swe_pro_tiers/run_matrix_evaluation.py` | gone | gone |
| `benchmarkings/run_agentic_live_challenge.py` | gone | gone |
| `benchmarkings/run_live_proof.py` | gone | gone |
| `benchmarkings/guard.py` | exists | exists |
| `benchmarkings/_retracted/RETRACTION.md` | exists | exists (488 bytes) |
| `tools/002_LLM_API_MOCK/models.json` → `top` | `[]` | `[]` |

`grep -rn "OpenRouterModel" benchmarkings/` returns exactly one hit:
`benchmarkings/zero_hint_v1/run_live_agent.py:7`, inside the module docstring stating
*"The lab seam constructs `OpenRouterModel`; this entrypoint never imports an adapter directly."*
That is a compliance statement, not an import. **No adapter import remains in `benchmarkings/`.**

## 5. Branch name resolution

Two names were in circulation: `sprint07/integration` (docs) and `sprints7-8/integration` (Dev B).

`git log sprint7/integration..sprints7-8/integration` shows 29 commits; the reverse direction shows
**zero**. `sprint7/integration` is a strict ancestor and holds no unique work, so retiring it loses
nothing. **`sprints7-8/integration` is the single canonical integration branch** and carries Sprint 8.
`sprint7/integration` is deleted locally and on `origin`.

## 6. Defects found during close (not present in the lane reports)

### D1 — `S7-CLEAN-001` destroyed three load-bearing CI artifacts

Commit `0a9ac8b` ("Purge legacy sprint0-6 doc bloat") deleted, along with genuine bloat:

- `docs/agile/sprint0/active-mvp-contract.json` — referenced by `ci.yml` (2 gates), the README badge, `AGENTS.md`, and `CLAUDE.md`
- `docs/agile/sprint0/schema-archaeology/traces/{BUG-01,BUG-02,BUG-03,NONCODE-01}.tsv` — the T0 archaeology evidence

Three CI gates had been failing on missing files since that commit. This is the same failure mode as
`S7-A-07` (stale paths after the `docs/scrum` restructure) and was not caught because the gates were
never run after the purge.

**Repaired in this close:** traces restored verbatim from `0a9ac8b^` to
`docs/scrum/sprints/sprint0/schema-archaeology/traces/`; contract restored **thin** (§7).

### D2 — baseline manifest sealed mid-sprint, then invalidated by the same sprint

Lane B sealed the baseline at `6ed94fe` (`S7-B-04`). Lane A then modified `tools/check_boundaries.py`
at `c5ff05f` (`S7-A-03`), which is a *sealed* artifact. `check_baseline_manifest.py` reported
digest drift from that point on.

This is a lane-ordering defect, not a Lane A or Lane B error: the seal task had no dependency edge on
the Lane A rules that rewrite the sealed files. **Re-sealed at close.**
**Rule adopted for S8/S9: the baseline seal is the last task in the sprint, never a mid-sprint row.**

### D3 — `pem-private-key` secret rule had no key-material requirement

`tools/scan_secrets.py` flagged `docs/front_v4/010_…md`, which quotes the literal
`-----BEGIN PRIVATE KEY-----` in prose *describing the DLP redaction rule*. No key material.

The rule matched a bare PEM header. A real PEM always carries a base64 body on the following line, so
the rule now requires one. Verified against both directions:

| Input | old | new |
|---|---|---|
| doc prose quoting the header inline | HIT | miss ✅ |
| header with no body | HIT | miss ✅ |
| real `PRIVATE KEY` PEM | HIT | HIT ✅ |
| real `RSA PRIVATE KEY` PEM | HIT | HIT ✅ |
| real `OPENSSH PRIVATE KEY` PEM | HIT | HIT ✅ |
| real `EC PRIVATE KEY` PEM, CRLF | HIT | HIT ✅ |

The `MF-SEC-SCAN-001` must-fail fixture is unaffected: `test/broken/fixtures/secret_leak/` trips
`openrouter-key-assignment` and `generic-sk-live`, independent of the PEM rule.

**Detection was narrowed to exclude non-key-material only.** No secret class was removed.

### D4 — `test/tools/test_lam_models.py` asserted a retired band vocabulary

The test required `tier1_local`/`tier2_local`/`tier3_cloud` keys and `len(top) >= 3`. The band
vocabulary is now `free|medium|high|top`, and `top` is deliberately `[]` so that
`models_for_band("top")` **refuses** — that refusal is the spend control.

The test was asserting that the budget control does not exist. Rewritten under CTO authorisation to
assert the refusal, assert the retired names stay absent, and reject unknown bands.
`top: []` is unchanged. No frontier ids were invented.

### D5 — `python3 -m unittest test.tools` exits 5

`test.tools` is a package, not a module; loading it discovers zero tests and `unittest` returns
exit 5 (`NO TESTS RAN`). The command was wrong in the kits, not the tests.

**Correct command: `python3 -m unittest discover -s test/tools -t .`** — 37 tests, exit 0.
Corrected in the Sprint 8 and Sprint 9 kits.

## 7. Active MVP Contract — restored thin

Restored at the live path `docs/scrum/sprints/sprint0/active-mvp-contract.json` with **14** rows,
down from 50. Selection rule: a row is present only if its registered command **passes on this
runner today**. Nothing is marked `covered` on the strength of a past claim.

Two Sprints-0–6 rows were deliberately **not** carried forward as covered
(`REQ-SCHEMA-*`, `REQ-CONF-001`) because their command `python3 -m unittest test.contracts.test_t1`
requires `node`. They are recorded as `open`, not silently dropped and not falsely covered.

```
python3 tools/check_active_mvp_contract.py   → CONTRACT PASS
python3 tools/run_active_contract_tests.py   → CONTRACT TEST PASS, 14 covered test IDs / 11 distinct commands
```

The pre-existing vacuity defect flagged in `docs/reviews/done/mvp_beta_delivery_audit_2026-08-16.md`
("PASS with 0 covered tests, 0 commands") is therefore closed: the gate now executes real commands and
fails if any of them fails.

## 8. What is NOT closed by this receipt

| Item | State | Owner | Due |
|---|---|---|---|
| `S7-J-04` git history rewrite for the leaked key | **open** — key rotation at provider is the CTO's action and is not verifiable from this repo | CTO + Tech Lead | does **not** block S8/S9 coding |
| `node`-absent reader errors | open | Joint `S8-J-02` | Sprint 8 |
| `ADR-0066` (MCP adapter rules) | open | Joint `S8-J-04` | Sprint 8 |
| `docs/reviews/doing/` over cap (12 files, cap 8) | open | Joint `S8-J-03` | Sprint 8 |
| `VG-07` reconciliation | open | Joint `S8-J-05` | Sprint 8 |

`--all-refs` secret scanning and the history rewrite are **not** evidenced here. `scan_secrets.py`
tree mode is green; ref-history mode is a separate, owner-gated action under `S7-J-04`.
