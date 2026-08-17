# 009 — Prior Review Reconciliation

**Status:** NON-NORMATIVE. Where this file and a v4 owner disagree, the owner wins (`PR-3`).
**Date:** 2026-08-16 · **Branch/HEAD:** `sprints7-8/integration` @ `0238b1a`
**Owns:** the finding-level verdict on all 13 prior review/plan documents, the evidence for each
verdict, and the routing of every surviving finding into `010`/`011` or the normative corpus.
**Method:** every document read in full; every claim spot-verified against the tree at `0238b1a`.
**Supersedes:** the coarse per-document rulings in `007 §5.3` and `001 §3.13`.

---

## 0. Why this document exists

`001`–`008` were written from the code, the v4 corpus, and the **headers** of 13 prior documents.
That was a defensible triage for a consolidation ruling. It was **not** a verification, and it was
wrong in both directions:

- Three documents carry material that is **stronger than the corresponding v0.4.3 report** and had
  been marked merely "promote".
- Five documents are **substantially closed by Sprint 6B** and were being carried as live debt.
- Nine findings are **still true**, and **two of them appear in no `001`–`008` report at all** —
  including a **High-severity secret-history finding** that `007 §6` got wrong.

That last item is the justification for the whole pass. `007 §6` stated secrets were "in good
shape" on the evidence of `git ls-files` returning zero tracked matches. `git ls-files` reports
**HEAD**, not **history**. Running the project's own tool with the flag the prior audit specified:

```
$ python3 tools/scan_secrets.py            → SECRET SCAN PASS
$ python3 tools/scan_secrets.py --all-refs → SECRET SCAN FAIL: reachable-object: env-named blob .env
$ git for-each-ref | grep -c refs/original → 21
```

**A gate that is only ever run in its passing mode is not a gate** (`A-10`). The `--all-refs` mode
exists, the prior audit named it, and nobody ran it. Corrected in `007 §6` and raised to a Sprint 7
Joint-track row in `011`.

---

## 1. Verdict vocabulary

| Verdict | Meaning | Action |
|---|---|---|
| `FIXED` | The defect is closed in the tree; evidence cited | Archive with the closing evidence |
| `STILL-TRUE` | Reproduced at `0238b1a` | → `011` backlog row |
| `PARTIAL` | Mechanism landed, obligation not discharged | → `011` backlog row, scoped to the remainder |
| `SUPERSEDED` | A later decision or document replaced it | Archive, name the successor |
| `WRONG` | The claim was false, or is false now | Archive with the disproof, so it is not re-raised |
| `PROMOTE` | Correct, valuable, and belongs in the normative corpus | → `VG-07` / `VG-09` amendment |

---

## 2. Document-level rulings

| # | Document | Lines | Ruling | Rationale |
|---|---|---|---|---|
| P1 | `sota_harness_scientific_benchmarking_programme_2026-08-16.md` | 836 | **PROMOTE + partially FIXED** | Its C1–C12 taxonomy, evidence-label regime, splits and budget protocol are **stronger than `002`**. Its headline defect (C6) is now fixed. → `VG-07` amendment |
| P2 | `vanguard_LAM_manifests_plan_sprint-7-to-9.md` | 749 | **PROMOTE (D-01…D-15 → ADRs) + adopt packets** | A better decomposition than `008`. Decisions are locked-in-prose and must become ADRs |
| P3 | `vanguard_v042_and_v5_from_harness_src.md` | 465 | **PROMOTE → `010`** | 16-tree competitor harvest + V5-A…V5-M. Covered nowhere in `001`–`008` |
| P4 | `vanguard_harness_cli_architectural_review_phase_2_REV2.md` | 197 | **PROMOTE → `VG-07`** | 12-layer FUAA + three-evidence-level model + defensible competitor matrix |
| P5 | `vanguard_harness_cli_architectural_review_phase_2.md` | 380 | **SUPERSEDED by P4** | Same thesis, superseded revision. Archive |
| P6 | `BETA-MVP-AUDIT-REPORT.md` | 463 | **~90% FIXED by 6B** | 8 of 9 blockers closed (§3). Its 8 SOTA properties → `guidelines/00` |
| P7 | `mvp_beta_delivery_audit_2026-08-16.md` | 358 | **~85% FIXED by 6B** | P0-01…P0-07 closed; **P0-08 and P1-01 STILL-TRUE** (§3) |
| P8 | `phases_0-2_review_full_rev2.md` | 982 | **SUPERSEDED by 6B closure** | Beta/GA fence (§7.1) → `011` framing. Rest closed |
| P9 | `phases_0-2_review_full_rev3.md` | 42 | **SUPERSEDED + 2 WRONG rows** | Two claims disproved at `0238b1a` (§3) |
| P10 | `phases_review.md` | 407 | **SUPERSEDED by `ADR-0058`** | It produced that ADR; the ADR is the durable artifact |
| P11 | `superpowers/…-phase-3-sprints-7-10-blueprint.md` | 51 | **SUPERSEDED by `008`** | Contradicts five locked decisions (`001 §3.13`) |
| P12 | `superpowers/…-harness-dna-pack-improvements.md` | 105 | **ADOPT into `011`** | Task 1 already done (`gene_digests`); Tasks 2–6 are real Sprint 7/8 rows |
| P13 | `superpowers/…-lam-benchmark-corpus.md` | 459 | **ADOPT into `011`, subordinate to `002`** | Tasks 1–4 partly done; the strategic fence is correct and binding |

---

## 3. Finding-level table

Every row verified at `0238b1a`. `lands in` names the destination.

### 3.1 STILL-TRUE — these become backlog rows

| Src | Finding | Evidence at `0238b1a` | Sev | Lands in |
|---|---|---|---|---|
| P7 P0-08 · P9 | **Secret history not purged.** `.env` blob reachable; 21 `refs/original` | `scan_secrets.py --all-refs` → **FAIL: reachable-object: env-named blob .env**; `git for-each-ref \| grep -c refs/original` → **21** | **High** | `011` S7 Joint · corrects `007 §6` |
| P7 P1-01 | **No `LICENSE` file** while `pyproject.toml` declares Apache-2.0 | `ls LICENSE*` → no such file; `pyproject.toml:license = {text="Apache-2.0"}` | Medium | `011` S7 Joint |
| P2 D-07 · P6 §5.1.6 | **`RecordCorrection` does not `parse_wire`** | `runtime/service/service.py:236` `_cmd_RecordCorrection`, no `parse_wire` call | High | `011` S8 Lane A |
| P2 D-13 | **`models.json` `top` must be `[]` until PL names ids** | `top` has **4 ids**; bands also drifted to `tier1_local`…`tier6_cloud` alongside `free/medium/high/top` | Medium | `011` S7 Lane C |
| P1 §9.2 | **`M-18` instrument tuple is implemented and unwired** | `tools/telemetry/tuple.py` exists; no runner emits it | **High** | `011` S9 Lane C |
| P2 §3.1 | **`proc.test` in `KNOWN_TOOLS` but not in `DEFAULT_BINDINGS`** | `adapters/models/invocation.py` vs `root.py:519-526` | Low | `011` S10 Lane B |
| P1 §11.1 | **Pre-registration status drift** — files say `preregistered_not_executed` while `runs/` exist | `benchmarkings/zero_hint_v1/` | Medium | `011` S9 Lane C |

### 3.2 FIXED — archive with the closing evidence

| Src | Finding | Closed by | Evidence |
|---|---|---|---|
| P1 C6 | LAM `passed` = `"passed" in output OR calls > 1` | 6B | `simulate.py:83` → `pytest_passed(workspace)` |
| P1 P1 | No evidence labels | 6B | `tools/002_LLM_API_MOCK/verdict.py:60` `evidence_label`, `:82` `leak_paths` |
| P2 Packet 0 | `store.py` imported by `ladder.py` but absent | 6B | `tools/002_LLM_API_MOCK/store.py` exists |
| P6 GOV-01 · P7 P0-05 · P9 | Runtime holds symmetric HMAC signing authority | `W1-03` / `ADR-0062` | `runtime/governance/approvals.py`, 25 Ed25519 refs |
| P6 CLI-LIVE · P7 P0-01 | CLI false-success on non-TTY stdin | `W2-01` | `main.tsx:120` gates feed on explicit `--feed`; `live.ts:484` fails `not_available` |
| P7 P0-02 · P6 CTX-01 | Provider `{text,toolCalls}` vs parser `{kind,action,…}` | `W1-04` | `adapters/models/invocation.py` `ProposalTranslator` |
| P7 P0-03 | LAM/Ollama not behind `ModelPort` | `W4-01` | `adapters/models/lam.py:29` `LamModelAdapter`; `ollama.py:18` `OllamaModel` |
| P7 P0-04 · P6 SBOX-01 · P9 | Only `proc.exec` sandboxed; fs verbs on host | `W1-05` | `root.py:664-666` builds `RootlessSandboxRunner`→`WorkerProtocol`→`SandboxedEnvironmentAdapter`, injected into **every** binding via `BindingContext.environment` |
| P7 P0-06 · P6 EVAL-01 | Evaluator daemon has no entry point / not packaged | `W1-06` | `daemon.py:161` `def main()`, `:219` `__main__`; `pyproject.toml:31` `vanguard-evaluator` script |
| P7 P0-07 · P6 GATE-01 | `run_active_contract_tests.py` PASSes with 0 commands | `W0-06` | `--candidate` mode; `:67-68` fails explicitly on 0 commands |
| P6 CLI-LIVE · P9 | No `RuntimeService` daemon | `W1-01` | `runtime/service/service.py`, 9 `_cmd_*` handlers |
| P12 Task 1 | Gene digests for comparability | S7 | `root.py:606-609` `gene_digests` |
| P12 Task 4 | Pairing protocol document | S7 | `benchmarkings/zero_hint_v1/PAIRING.md` |
| P1 §4.2 C4 | **String-in-source oracle** — `bug-001` asserted `"(A + B) * B"` in source text, so a comment satisfied the judge | S7 | `…/bug-001-single-file/test_oracle.py` is now a **property oracle**; its docstring reads *"Property oracle: formula behaviour, not a source substring."* It asserts `fn(2,3)==15`, `fn(0,4)==16`, `fn(1,1)==2` |
| P1 §8.4 | **LAM hardcoded a "You are OpenCode" persona**, confounding Plane-B DNA claims | S7 | `simulate.py:23-27` — `SYSTEM` now reads the **pack's** `system-prompt.txt` with a neutral fallback |
| P6 NODE-01 | 14 reader tests error without `node` | *by design* | `test/contracts/readers/__init__.py:40` **refuses** rather than skipping — correct instrument behaviour |

### 3.3 WRONG — archive with the disproof

| Src | Claim | Disproof |
|---|---|---|
| P9 row 4 | "Composition executes directly through `GitEnvironment`, never `RootlessSandboxRunner`" | `root.py:659-666` composes `RootlessSandboxRunner`; `GitEnvironment` is not constructed on the product path |
| P9 row 5 | "Runtime creates the signing authority from a default/shared HMAC key" | `root.py:732-733`: `can_verify = approval_key is not None`; `ApprovalAuthority` is verify-only, Ed25519 |
| P6 §1.4 | "`tools/001_LLM_API_ROUTER` and `002_LLM_API_MOCK` were not present in the tree" | Both exist and are populated; auditor indexed a different view |

### 3.4 PROMOTE — into the normative corpus

| Src | Material | Destination |
|---|---|---|
| P1 §4.1 | **C1–C12 cheating taxonomy** — operational definition of an invalid run | `VG-07` amendment; mirrored in `guidelines/03` |
| P1 §3 | **Evidence labels** (`lam-replay`, `cassette`, `single-shot-complete`, `chat-patch-loop`, `lab-execute-harness`, `product-cli`, `sealed-evaluator`, `aa-floor`, `paired-holdout`) | `VG-07`; already partly coded in `verdict.py` |
| P1 §6.1 | **Splits** `DEV/HOLDOUT/SEALED/LIVE/DEPLOYMENT` + one-way contamination + touch ledger | `VG-07` (`M-19`/`M-20`) |
| P1 §6.2 | **Tier model T0–T5** as calibration rungs, not significance theatre | `VG-07`; `011` S9 |
| P1 §5.3 | **Outcome algebra** — `pass`/`public_overfit`/`fail`/`abandoned`/`inconclusive`/`invalid` | `VG-07`; `002` amendment |
| P1 §10 | **Budget protocol** — calibration-first spend order, hard stop at 0 | `guidelines/03` |
| P2 §4 | **D-01…D-15** locked decisions with reversal conditions | `VG-09` as `ADR-S7-01`…`ADR-S7-06`+ |
| P2 §7.1 | **Core-change detector** — reconstruction PRs may not touch `kernel/**`, `agency/episode/**`, `domain/wire/**` | `011` S7 CI rule; `guidelines/01` |
| P4 §2 | **12-layer FUAA** — the architectural question + minimum evidence per layer | `VG-07`; `guidelines/00` |
| P4 §preamble | **Three evidence levels** — public contract / architectural inference / unverifiable | `VG-07`; `guidelines/03` |
| P6 §0 | **8 SOTA properties** of an agentic coding harness | `guidelines/00` |
| P8 §7.1 | **Beta/GA fence** — not every finding is Beta-blocking | `011` framing |

---

## 4. Content absent from `001`–`008` entirely

Three bodies of work were invisible to the v0.4.3 review set. Two are routed to `010`; one to `011`.

1. **The V5 roadmap and the 16-tree competitor harvest** (P3). ACI gifts, Reasonix prefix
   discipline, V5-A…V5-M, the rewrite-vs-evolve ruling. → **`010`**.
2. **The measurement science apparatus** (P1). C1–C12, splits, tier model, outcome algebra,
   budget protocol, experiment registry. → **`VG-07` + `002` amendment**.
3. **The packet decomposition** (P2 §11, Packets 0–14) with explicit "may start when"
   preconditions and stop conditions. → **`011` + sprint kits**.

---

## 5. Corrections to `001`–`008`

Recorded here so the corrections are auditable rather than silent (`VG-09 §4` discipline).

| Report | Statement | Correction |
|---|---|---|
| `007 §6` | *"Secrets… This is in good shape."* | **Wrong.** Based on `git ls-files` (HEAD only). `scan_secrets.py --all-refs` FAILS; 21 `refs/original` remain. Raised to a High-severity Sprint 7 row |
| `007 §5.3` | Per-document close/promote rulings | Replaced by §2 of this document |
| `001 §3.13` | Phase-3 blueprint contradictions | Retained; extended by §2 P11 |
| `002` | Evidence-class table (6 classes) | Superseded by P1's 9-label regime (§3.4); `002` amended |
| `005` | Gene-digest task proposed | Already implemented at `root.py:606`; task reduced to *emit into `result.json`* |
| `008` | Sprint themes | Retained; re-mapped onto Waves W6–W9 in `011` |

---

## 5a. Two corrections to this document, made during its own verification

Recorded rather than silently edited, because the mechanism is the point.

| Row as first drafted | Verdict | Disproof |
|---|---|---|
| `bug-001` uses a string-in-source oracle (`STILL-TRUE`) | **FIXED** | The file is now a property oracle asserting `fn(2,3)==15`, `fn(0,4)==16`, `fn(1,1)==2`. Its docstring explicitly says *"not a source substring"* |
| LAM hardcodes a "You are OpenCode" persona (`STILL-TRUE`) | **FIXED** | `simulate.py:23-27` reads the pack's own `system-prompt.txt` |

**Both were carried forward from the source document without re-verification — the exact failure
this document exists to prevent.** They were caught by the automated evidence re-check in the
verification pass (`V1`), not by review.

The lesson generalises beyond these two rows: **a finding is only as current as its last
verification.** That is why every `STILL-TRUE` row here carries a `file:line`, and why the `V1`
check that re-runs those assertions should be kept as a CI job rather than a one-off.

---

## 6. What the reconciliation proves about the process

Three observations worth carrying into `011`, because each is a process defect with a mechanism:

1. **Reviews were correct and unactioned.** P1 identified the benchmark contamination on
   2026-08-16 and my `002` re-derived it independently on the same day. Two correct audits, zero
   closure. The WIP limit in `007 §5.2` addresses the accumulation; the **backlog row per finding**
   in `011` addresses the closure.
2. **Sprint 6B closed 8 of 9 P0 blockers and nobody updated the audits.** The documents stayed in
   `todo/` reading as live NO-GOs long after the work landed. **A review document with no closure
   protocol becomes disinformation** — it was actively misleading me two turns ago.
3. **A gate run only in its passing mode is not a gate.** `scan_secrets.py` was run; `--all-refs`
   was not. `A-10` is the rule; the fix is that CI must run the strict mode, not the lenient one.

---

## 7. Routing summary

| Destination | Rows |
|---|---|
| `010` — V5/ACI roadmap | P3 in full |
| `011` — Sprint 7 | secret history, LICENSE, `models.json top`, LAM persona, core-change CI rule, alias repair |
| `011` — Sprint 8 | `RecordCorrection` `parse_wire`, P12 Tasks 2–6, P13 Tasks 5–11 |
| `011` — Sprint 9 | `M-18` tuple wiring, oracle hardening, pre-registration status, splits, tier model |
| `011` — Sprint 10 | `proc.test` binding, domain de-capture |
| `VG-07` amendment | C1–C12, evidence labels, splits, outcome algebra, FUAA, evidence levels |
| `VG-09` ADRs | D-01…D-15 → `ADR-S7-01`+; `ADR-0063` Python; `ADR-0064` gate status |
| `guidelines/` | 8 SOTA properties, budget protocol, evidence levels, core-change detector |
| `docs/reviews/done/` | All 13 source documents, with closure headers |
