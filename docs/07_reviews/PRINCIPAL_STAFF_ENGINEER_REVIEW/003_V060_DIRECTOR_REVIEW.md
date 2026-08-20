# AETHER / Vanguard v0.6 — Engineering Director Final Review

**Classification:** Engineering Director / Chief Engineer independent review.
**Verdict:** **APPROVED** — the v0.6 foundation and documentation are finalized; **Wave 0 may begin** (`ADR-0075`).
**Date:** 2026-08-20 · **Baseline:** main `4f9f8b1`, clean tree.
**Scope:** Backend core only (kernel, ledger, dispatch, authority boundaries, plugin runtime). Frontend/CLI/TUI excluded per mandate.
**Law after this review:** `docs/SPEC.md` + ADRs `0069`–`0075` + `docs/04_annex/{KERNEL,MEASUREMENT}.md`. Living roadmap: [`002`](002_V060_FOUNDATION_ROADMAP_AND_GAP_REGISTER.md).

---

## 1. What was reviewed

- **Code:** `vanguard/packages/` (kernel S0–S12 dispatch, attenuation, grants, budget; agency `EpisodeEngine.spawn()`; runtime `root.py`, governance Ed25519, SQLite WAL ledger; adapters — evaluator daemon, models, sandbox), `layer0/` fork (driver, ceiling, SPI/jsonrpc), `packs/code-default/`, `tools/` linters, `.github/workflows/ci.yml`.
- **Docs:** SPEC v0.6.0; ADRs `0069`–`0074` plus the historical register (`0000`+, `ADR-M0-*`, `DEFERRED_REJECTED`, `INDEX`); `KERNEL.md`; `MEASUREMENT.md`; GAMMA; the `002` register; the forensic discovery; the four advisory `*_suggestion.md` reviews and the superseded proposals (now consolidated — see §5).
- **Fresh test baseline:** full suite + per-directory suites + all seven static linters, executed during this review (recorded durably in [`test/README.md`](../../../test/README.md)).

## 2. Verdict rationale (why APPROVED, not BLOCKED)

1. **The lock tells the truth about the code.** Every load-bearing claim was re-verified on disk: F1's fabricated `VerdictRecorded {verdict: "pass"}` is exactly where ADR-0072 says; the fail-open ceiling (`if not capabilities: return True`) is exactly where ADR-0074 says; living CI gates `test/layer0` and linters while `test/kernel` (95 OK) is unwired, exactly as ADR-0073 says. A concept lock that names its own false gates, with bound falsifiers and an ordered repair sequence, is the correct posture to approve.
2. **The production kernel matches its constitution.** `vanguard/packages/kernel/dispatch.py` implements KERNEL.md §2 rule-for-rule: K-04 (resolve before lease), K-05 (verify at point of effect), K-06 (release before emit), K-07 (overruns debited), K-08/F-05 (classifier call, fail-closed on raise), K-47/S8a (durable intent before dispatch), F-22 (undeterminable preserved, never resolved), F-24/F-21a (paging alarms). The WAL+FULL ledger, nonce-carrying signing evaluator daemon, and fail-closed spawn attenuation all exist on the packages path.
3. **The decisions are correctly shaped.** Python-first packages-canonical convergence (0069), Agent = Principal + HarnessInstance with `spawn` as the sole delegation primitive (0070), decision/state plane split with the identity trinity and replay taxonomy (0071), wire-first plugins with an exterior judge (0072), an explicit lock/defer/reject partition (0073), and the GAMMA tightenings (0074 — typed budget algebra, writer authority, complete `D_H`, Project, trajectory, verdict binding) are internally consistent, consistent with the prior ADR corpus, and consistent with the code. Nothing material from the four advisory lanes was lost: GAMMA §2 adjudicates every claim, and the rejections (Rust core, third tree, evaluator-as-plugin, hot-swap, byte-identical concurrent ledgers) carry reversal conditions.
4. **The roadmap is the right order.** Wave 0 (make CI measure the real subject and land the falsifiers red) before Wave 1 (trust spine) before convergence, extensibility, and one E2E stop condition — this is the only sequence that does not re-create "docs claim done."
5. **Every open defect is registered.** Nothing found in this review contradicts a locked concept; the four new findings (§3) are additions to Wave 0, not reopenings.

## 3. New findings from this review (added to `002` §4.2 as F-18…F-21)

| ID | Finding | Evidence | Disposition |
|---|---|---|---|
| F-18 | `check_domain_blindness.py` enforces I-7 on `layer0/` only; SPEC I-7 also names `vanguard/packages/{domain,kernel}/`. The linter is weaker than the invariant. | Tool output: "no coding\|pytest\|ast tokens in layer0/" | Wave 0: extend the scan surface |
| F-19 | `test/integration/` (13 tests) and `test/governance/` are missing `__init__.py` and are **silently excluded from every discovery run**. | `unittest discover` ImportError on both; root discovery collects 1119, per-dir sum ≈ 1138 | Wave 0: make importable or retire with reason |
| F-20 | `preregistered_oracles.json` exists nowhere in the tree — it was deleted with the sprint-6B docs, not relocated. `test_oracle_registry` (2 errors) and `test_repo_paths` (2 failures) share this root cause. | `find` across repo: no match; `docs/03_sprints/evidence/` does not exist | Wave 0 (with P1-15): restore artifact at a canonical path or retire tests |
| F-21 | The three `test_model_invocation` errors are **real gaps in `ProposalTranslator`**: a `parameters`-key tool call and two fenced-payload forms degrade to prose (`kind: "finish"`). Reproduced directly against `invocation.py`. Not "legacy output shape" as the old test README claimed. | Direct reproduction in this review | Wave 0/1 (with P1-17): implement lifting or re-scope tests, decided with the selector contract |

Additional documentation corrections applied (no normative rule changed):
- SPEC and both annexes cited `docs/archive/v045/` and `docs/TECH_LEAD_REVIEW/` — **neither exists on disk**. Citations now say the corpus lives in git history (anchor `4f9f8b1`).
- SPEC's §8 gate note spelled the stale sprint-6B path literally, keeping `check_stale_paths` red on SPEC itself; reworded. The checker remains legitimately red on the forensic discovery (historical evidence) until Wave 0 resolves P1-15/F-20.
- `test/README.md` §4–6 refreshed with the verified baseline and corrected root causes; CI subject-of-record statement added.
- `CLAUDE.md`, `docs/README.md`, and GAMMA's header links updated for the consolidation below; hold status updated to "approved — Wave 0 authorized, not started."

## 4. Fresh test baseline (2026-08-20, main `4f9f8b1`)

Full root discovery: **1119 tests — 7 failures, 5 errors, 8 skipped**; suites of record all green: kernel 95/95, contracts 121/121, agency 107/107, packs 27/27, layer0 25/25, security 45/45, trust 22/22, registry 26/26, lab 54/54, tools 38/38. All 12 reds decompose into exactly three known families: 3 Ollama-offline env-sensitive (runtime), 4 stale-oracle-path (F-20), 5 translator/selector (F-21 + P1-17). Linters: 6 of 7 pass; `check_stale_paths` red (known, P1-15). Full breakdown and durable guidance: [`test/README.md`](../../../test/README.md).

## 5. Documentation consolidation executed

Removed from the active tree after absorption (all recoverable at git `4f9f8b1`; see [`../ARCHIVE.md`](../ARCHIVE.md)): the entire `OLD_TECH_LEAD_REVIEW_archive/` (4 advisory reviews, 4 working logs, gap audit, MHF blueprint, migration matrix, sprint plans), the forensic TODO, the concept-lock prompt, and the superseded phase/proposal documents (ALFA, BETA, DELTA, principal engineer proposal, Full Refactor v3.1, execution plan, parecer v4, Aether waves). Their durable conclusions live in SPEC (I-1…I-11, §8.1/8.2), ADRs `0069`–`0075` (decisions + rejected alternatives), the annexes, GAMMA §2 (claim-by-claim adjudication), and `002` (falsifiers + waves).

**Surviving active set:** `docs/SPEC.md` · `docs/05_adr/` · `docs/04_annex/` · GAMMA · `002` register · forensic discovery · this review.

## 6. Conditions attached to approval (not blockers)

1. Wave 0's exit gate now includes F-18…F-21 alongside F-01…F-17. Red falsifiers are acceptable; uncollected or misattributed ones are not.
2. The first code commit of Wave 0 must be the CI subject-of-record rewire, per ADR-0073.
3. No scope beyond the `002` register without a new ADR.

**— Engineering Director / Chief Engineer**
