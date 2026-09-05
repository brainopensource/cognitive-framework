# Electroweak v0.9.2 → Living Execution Runway Transition Blueprint

**Authority**: Planning & Staging Resource (`.draft/`) — not law, not a board
**Target Runway**: [`docs/execution/`](../docs/execution/) (`milestones.md`, `backlog.md`, `spec.md`, `technical.md`, `tasks.md`)
**Source Corpus**: `docs/reports/reviews/electroweak_v092/` — `grok/`, `opus/`, `octopus/`, `gpt/`, `gem/`, **`plans/`**
**Companion**: `.draft/ELECTROWEAK_SYNTHESIS_FINAL_v093.md` (Synthesis of Record, 2026-09-04)
**Revision**: v4 — re-aligned 2026-09-04 against the 900-line `.draft/ELECTROWEAK_SYNTHESIS_FINAL_v093.md`
(7 packages, T-69..T-97, §9 evidence standard). Nine drifts corrected: wave mapping, `gem/` status,
capability-bound native profiles, read-before-edit as experiment, T-46 narrowed (not superseded),
MS-TRUTH instrument gating, MS-CONTROL product-path qualification, T-83 split, Defect K precedence.
**Verification basis**: working tree `feat/strongforce_beta_release_v093`, HEAD `537bdb66`

---

## 0. What changed since v1, and why you must not use it

v1 of this blueprint was written from the Gemini draft synthesis, before anyone
diffed the review corpus against the source tree. That audit is now done, and it
found three classes of problem in v1:

1. **One prompt inverts the corpus.** v1 Prompt 02 instructed the agent to make
   `MS-TRUTH` require that *"oracle pass records completed, never abandoned."*
   Opus Part 7 §6 — the very section v1 cites — says the **opposite**:
   *"`disposition` is externally computed and **structurally separate** from
   `terminal`. Had this existed, the inversion would have been visible on day
   one."* v1 would have committed the 8/8 conflation as a gate requirement.
2. **Twelve corpus findings were dropped**, including the two the corpus itself
   ranks highest-ROI (§3 below).
3. **Paths, IDs and numbers drifted.** Six of v1's file paths do not exist; four
   of its six package IDs duplicate live backlog rows; its budget figures
   contradict a frozen catalog already in the tree.

**Use v2. Discard v1.** Every prompt below carries a `Corpus anchor` (where the
claim comes from) and a `Tree status` (what the source says today). Both were
checked by hand; where they disagree, the disagreement is stated rather than
smoothed over.

---

## 1. Corpus provenance and drift

| Fact | Value | Consequence |
|---|---|---|
| Opus review pin | `5243866b` | Reviews are ~1 week behind HEAD |
| Grok review pin | `5243866bc169c7f60cc7d4f74b9a853f60356381` | Same subject; the two reviews are comparable |
| Octopus audit subject | `a8775c3f` (`integration/consolidated-v092`) | **Different tree.** Octopus findings need re-verification before use |
| Grok live trial `gf-orders-001` | run later at `ffc3dc926e80` | `abandoned`, **0 effects** — the only dogfood datum in the corpus |
| Current HEAD | `537bdb66` | Three commits of doc restructuring since |
| `gem/` | **2 files** (`README.md`, `gem_sota_harness_evolution_report.md`) | **Changed since v3.** `gem/` was empty when this blueprint was first written; the Gem technical evaluation has since been filed. Synthesis of Record §0 resolution 5 **integrates** it: Trailing Goal Echo, CTRF distillation, the $d_t = d_{t-2}$ oscillation breaker, greenfield vacuity rejection, and TTC/RTV. Cite `gem/` for those five mechanisms. |
| `plans/` | 6 files, 7,945 lines | **v1 omitted this entirely.** It holds `DEVELOPMENT_FINAL_PLAN{,_B,_v2}.md` and `PHASE-0_...` — the documents `milestones.md` names in its own `derived_from:` frontmatter. Any prompt touching `milestones.md` must read them. |

**Precedence note on Defect K (v4).** Where this blueprint and the Synthesis of
Record disagree, the Synthesis normally wins — it is the authority of record. This
row is the one deliberate exception, because it is the more recent and deeper read
and it was re-verified at HEAD while writing v4:

```
$ sed -n '1090,1112p' vanguard/packages/adapters/models/openrouter.py
    return Result.fail(kind="instrument_error",
        message="provider streaming response was malformed, truncated, or empty")   # :1093
    ...
        return Result.fail(kind="instrument_error",
            message="provider streaming response was malformed, truncated, or empty")  # :1110
```

Neither call site passes `retryable=`. The Synthesis of Record §2 lists
`retryable=True` at `:830, :862, :881, :917, :933` and concludes "verify-first,
may close as `no_defect`" — but those five are the TRANSPORT paths; the two
malformed-stream sites are a different code path and carry no flag at all.
`_MALFORMED_STREAM_MESSAGE` (`:943`) and `_EMPTY_PROPOSAL_RETRIES` (`:946`) exist
and are used at `:972-987`, not here. **T-70a stays reproduce-first as a matter of
discipline, but it is expected to reproduce.** Update the Synthesis of Record §2
row and its §8 residual-uncertainty entry to match; until that edit lands, this
row is the current finding.

**Drift rule for every prompt below:** a corpus claim is a *hypothesis about a
past tree*. Before writing it into the runway, re-run its stated reproduction
command against HEAD. Two corpus claims have already gone stale this way (§4),
and one has gone *more* severe.

---

## 2. The 2-step funnel, corrected

v1's funnel is sound and is kept. What changed is that Step 1 is now genuinely
locked, and a Step 0 has been made explicit because skipping it is what produced
v1's defects.

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ STEP 0: CORPUS RECONCILIATION  (DONE — Synthesis of Record §1)               │
│ - Diff every corpus claim against the current tree, line by line             │
│ - Record pins, drift, and stale claims BEFORE any package is named           │
│ - Refuse any package whose premise no longer reproduces                      │
└───────────────────────────────────┬──────────────────────────────────────────┘
                                    ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ STEP 1: ARCHITECTURAL LOCK  (DONE — Synthesis of Record §2, §4, §6)          │
│ - Resolve the four conflicts (fuzzy vs exact, L2 PPR vs L5, ladder, swarm)   │
│ - Reconcile candidate packages against LIVE backlog IDs — do not invent      │
│ - Fix the two settlement axes; never let one be derived from the other       │
└───────────────────────────────────┬──────────────────────────────────────────┘
                                    ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ STEP 2: SURGICAL DETAILING & RUNWAY STAGING  (these prompts)                 │
│ - Exact code recipes into technical.md; typed wire contracts into spec.md    │
│ - Atomic dependency trees into tasks.md (T-69 onward; current max is T-68)   │
│ - TCB held at 1386 — not "under 1438"                                        │
└──────────────────────────────────────────────────────────────────────────────┘
```

Steps 0 and 1 are complete. **Feed the prompts below one at a time**, in the
order given. Prompt 00 is a pre-flight gate; Prompt 10 is the highest-ROI item
in the suite and v1 did not contain it at all.

---

## 3. What v1 dropped — twelve corpus findings, now restored

Each row was absent from v1's eleven prompts. The last column says which v2
prompt now carries it.

| # | Finding | Corpus anchor | Tree status at HEAD | Prompt |
|---|---|---|---|---|
| **1** | `pass_rate_pct` is written for `n=1` runs with the same schema as `n=21` runs. `runner.py` must refuse `pass_rate` when `len(results) < suite_size`; add `n` + `suite_digest`. *"the highest-ROI item in this entire audit."* | `octopus/…/draft-synthesis-evidence-audit.md` §1 (F1) | Not fixed | **10** |
| **2** | Adopt `opus/evidence/matrix_runner.py` as the results schema: `disposition` **externally computed and structurally separate from** `terminal`, plus `suite_digest`, `suite_size`, `model_real`, `cost_provenance`, `proposals[]`, `denials[]`, `oracle_tail`. Poison aggregates containing `model_real:false` into `undeterminable`; make a second `*_report.json` a lint failure. | `opus/part7…` §6 | Not adopted | **10** |
| **3** | `routing-policy.json` files use **mutually incompatible vocabularies**; `vg-code-swe-mini` believes it routes DeepSeek-Coder with a Qwen fallback and does not — it silently falls through to env defaults. Any score attributed to that manifest is mislabeled. Needs a JSON Schema with `additionalProperties:false`, fail-closed at compose. | `octopus/…/draft-synthesis-evidence-audit.md` §3b | Not fixed | **10** |
| **4** | `runtime/entrypoint.py` defaults `run_id` to the fixed literal `"run-cli"`, so two invocations in one workspace **share a ledger**; one corpus benchmark row had to be discarded for exactly this. Needs UUID/ULID identity and explicit `--resume <id>`. | `gpt/…` §B + "Excluded identity collision" | **Confirmed live** at `entrypoint.py:56`. The mitigation at `:82` routes only the *fake-backend preview* to an in-memory store; real runs still collide. | **10** |
| **5** | `_completion_allowed_tools` is bound at engine construction *inside* the `while True:` re-entry loop, so in a fully autonomous preset with no approval round-trip the restriction **never applies**. | `octopus/…evidence-audit.md` §2 | Needs re-verification (different tree) | **03** |
| **6** | Defect F — the `proc.exec` allowlist blocks orientation commands: `command binary 'pwd' is not in allowlisted commands`. | `opus/opus_solution.md` §2.6 | **Confirmed live.** `proc://exec/allow/git,pytest,ruff,python3` in both `vg-code-default/manifest.json:43` and `packs/code-default/harness.yaml:67` | **03** |
| **7** | Defect H — the environment map advertises `kind=git` but `init` never runs `git init`: `[exit 129] warning: Not a git repository`. | `opus/opus_solution.md` §2.6 | Not verified this pass | **03** |
| **8** | Defect I / J — `.pytest_cache/` is counted as agent-authored output, and **44 of 88** baseline ledger events are plugin lifecycle churn (11 plugins × Discovered/Resolved/Verified/Activated + Quiesced/Retired) for 3 turns of work. | `opus/opus_solution.md` §2.6 | Not verified this pass | **07** |
| **9** | Greenfield evidence mapping **aliases** `structural_passed` = `behavioral_passed` = `verification.passed` and never sets `oracle_failed_on_stub`. The system prompt's "do not read first" law *fights* the pack's scaffold + oracle-fail-on-stub policy. | `grok/README.md` hole 4 | Not verified this pass | **07** |
| **10** | Semantic test-output distillation on `proc.exec` results (~1200→180 tokens/turn) is *"the single highest-leverage unimplemented item."* `parse_test_output` exists in `forge/engine.py`; the distillation filter does not. | `octopus/…evidence-audit.md` §4 | Partially covered by T-36 | **07** |
| **11** | A **kill list** is normative, not advisory: no second `EpisodeEngine`; no Forge/Chimera product score; no new provider abstraction; no kernel AST; no leaderboard mixing live/replay/error/zero-call rows; and *"AHE-class evidence: tools/middleware/memory beat system prompts — do not spend a quarter on `system-prompt.txt`."* | `gpt/…` "What not to build yet"; `grok/README.md` "What this review is not" | — | **13** |
| **12** | `plans/` (7,945 lines) is the `derived_from:` authority for `milestones.md` and was never opened. | `docs/execution/milestones.md` frontmatter | — | **00** |

---

## 4. Two corpus claims that did not survive the tree, and one that got worse

Recorded because a prompt suite that repeats a stale claim manufactures work.

| Claim | Corpus | HEAD | Disposition |
|---|---|---|---|
| *"`ProgressVector` should be built"* → corrected in-corpus to *"it already exists (`domain/ledger/progress.py`, 237 LOC); it should be **wired**, not built."* | `opus_solution.md` §3.2 | `progress.py` is 237 lines **and is now imported by `runtime/session.py`** | **CLOSED.** Wiring landed. Do not re-open. |
| *"Prompt caching: the free half skipped"* (D3) — walked back in-corpus: DeepSeek returns `cached_tokens: 2048/2304`, so the prefix-stable compiler *already earns its design there*; **"§D3 overstated the severity."** | `opus/part2` §D3 vs `opus_solution.md` §3.1 | `prefix_freeze: true` declared in `harness.yaml` | **DOWNGRADE.** Explicit `cache_control` still matters for Anthropic-style providers. Do not budget it as a headline defect. |
| Defect K — malformed SSE chunk is non-retryable, killing the whole episode **(this row OVERRIDES the Synthesis of Record — see note below)** | `opus/part7` §3.1, naming `openrouter.py:1095` and `:1112` | **Still unfixed, and confirmed at those exact lines.** Neither call site passes `retryable=True`; `_MALFORMED_STREAM_MESSAGE` (`:943`) and `_EMPTY_PROPOSAL_RETRIES` (`:946`) exist and are unused there. | **UPGRADE.** The Synthesis of Record hedged this as "verify-first, may be `no_defect`" from a shallower read; that hedge was wrong. It is a live 3-line fix, and it **biases every A/B** — DeepSeek is routed non-streaming and so is structurally immune. |

---

## 5. Prompt suite

```text
  00. Corpus Reconciliation & Drift Pre-Flight            (gate — run first)
  01. Backlog Registration & Legacy Reconciliation        (backlog.md)
  02. Milestone Overlay Gates & Release Predicates        (milestones.md)
  03. HAR-01 — Harness Preconditions                      (technical.md, spec.md)
  04. Settlement Truth & the Two-Axis Disposition         (technical.md, spec.md)
  05. Edit Primitive — exact str_replace on existing 2PC  (technical.md, spec.md)
  06. IDX-01 — LDA-backed IndexPort & cache stability     (technical.md, spec.md)
  07. Greenfield Oracle, Workspace Hygiene & Distillation (technical.md, spec.md)
  08. Preset Catalog Unification (CMX-01)                 (technical.md, spec.md)
  09. Outer Director (OCT-03) — staged post-MS-CONTROL    (technical.md, spec.md)
  10. Instrument Integrity  ← HIGHEST ROI, absent from v1 (technical.md, spec.md)
  11. Atomic Task Work-Tree Deconstruction                (tasks.md)
  12. Constitutional Invariant & TCB Budget Audit         (verification)
  13. Kill List & Non-Goals Register                      (backlog.md §Risks)
```

**Wave mapping** (Synthesis of Record §7 — note this CHANGED in v4; the v3 mapping
had the pre-correction order):

| Wave | Prompts | Rationale |
|---|---|---|
| **1 — Settlement & Signal Truth** | 03, 04, **10** (INS-01/BRG-01 halves) | The agent must be able to call tools, write, finish — and the instrument must not lie |
| **2 — Frozen Control, Honest Instrument & Presets** | **08**, 10 (EXP-01 half) | `MS-CONTROL` closes here. Presets are a *control* problem, not a late optimisation |
| **3 — Edit & Retrieval Treatments** | **05**, **06** | Post-control. Opus Part 7 demoted `str_replace` and LDA from product blockers to **treatments whose lift must be measured** |
| **4 — Context Economy & Reliability** | 07 | Post-control. T-77, T-80 |
| **5 — Outer Director & Arms** | 09 | Blocked on a closed `MS-CONTROL` |

**Do not restore the v3 mapping** (05–06 in Wave 2, 08 in Wave 4). It inverts the
ordering correction: it would qualify the control *after* the treatments it is
supposed to measure them against. Prompt 11's own WAVES block already carries the
corrected order — v3 contradicted itself between §5 and Prompt 11.

---

### Prompt 00: Corpus Reconciliation & Drift Pre-Flight

* **Target**: none — this is a gate that produces a findings table
* **Goal**: refuse to write any runway change whose premise no longer reproduces

```markdown
# ASSIGNMENT: Corpus Reconciliation & Drift Pre-Flight
Scope: docs/reports/reviews/electroweak_v092/ vs. the working tree at HEAD

The review corpus is pinned to `5243866b` (grok, opus) and `a8775c3f` (octopus).
HEAD is `537bdb66`. Every corpus claim is a hypothesis about a past tree.

1. Read `plans/` in full (6 files, 7,945 lines) — `DEVELOPMENT_FINAL_PLAN.md`,
   `_B`, `_v2`, `PHASE-0_DEVELOPMENT_FINAL_PLAN.md`, `DOCUMENTATION_REFACTOR.md`.
   `docs/execution/milestones.md` names these in its own `derived_from:`
   frontmatter, so any milestone edit that contradicts them is a silent fork.
   Report contradictions; do not resolve them unilaterally.
2. For every defect a prompt below will act on, re-run its stated reproduction
   command against HEAD and record: STILL PRESENT / FIXED / CHANGED SEVERITY /
   NOT REPRODUCIBLE.
3. Treat octopus findings with extra care: they were verified against
   `integration/consolidated-v092` (`a8775c3f`), a DIFFERENT tree from the one
   grok and opus reviewed. Re-verify before use.
4. `gem/` now holds two files (it was empty when this suite was first drafted).
   The Gemini *draft synthesis* remains superseded by
   `.draft/ELECTROWEAK_SYNTHESIS_FINAL_v093.md`, but the Gem *technical
   evaluation* is INTEGRATED by §0 resolution 5 and is citable for exactly five
   mechanisms: Trailing Goal Echo, CTRF distillation, the $d_t = d_{t-2}$
   oscillation breaker, greenfield vacuity rejection, and TTC/RTV. Cite it for
   those and nothing else.

OUTPUT: a table of {claim, corpus anchor, reproduction command, verdict at HEAD}.
Any claim that is FIXED or NOT REPRODUCIBLE is struck from its downstream prompt.
Do not proceed to Prompt 01 until this table exists.
```

---

### Prompt 01: Backlog Registration & Legacy Reconciliation

* **Target File**: `docs/execution/backlog.md`
* **Corpus anchor**: Synthesis of Record §4; `backlog.md` §2.9/§2.10/§3
* **Tree status**: four of the six draft package IDs duplicate live rows

```markdown
# ASSIGNMENT: Backlog Registration & Legacy Reconciliation
Target Document: `docs/execution/backlog.md`
Authority Tier: Execution Runway (Living Document)
Source: `.draft/ELECTROWEAK_SYNTHESIS_FINAL_v093.md` §4

Register the accepted Electroweak disposition. Reconcile packages to prevent R-01 (architecture sprawl), while registering the seven authoritative capability packages established in Synthesis of Record §4.1:

ADD to a new §2.11 — exactly SEVEN packages:
  - `HAR-01` Harness Precondition Repair (`domain` / `agency` / `runtime` / `adapters`, Lane A, APPROVED). Precondition of CMX-09. Allocates T-69..T-74, T-82.
  - `INS-01` Product Instrument Integrity (`runtime` / `benchmarks` / `clients`, Lane A, APPROVED Route R). Allocates T-84, T-85, T-89, T-97.
  - `DLG-01` Live Dialect Validation & Provenance (`adapters`, Lane A, APPROVED Route R). Allocates T-86, T-90.
  - `BRG-01` Local Inference Instrument Fail-Closed (`tools/llama_cpp`, Lane B, APPROVED Route R). Allocates T-87, T-88, T-91.
  - `EXP-01` Measurement Ladder & Preregistration (`benchmarks`, Lane B, APPROVED Route R). Allocates T-92..T-95.
  - `ARM-01` Comparative Arm Program (`benchmarks` / `agency/manifests`, Lane B, PROPOSED Route L). Allocates T-96. Gated on closed MS-CONTROL.
  - `IDX-01` LDA-Backed Repository Intelligence (`adapters` / `agency`, Lane B, APPROVED). New adapter only (`IndexPort` unmodified). Allocates T-75..T-77.

RECORD AS ALIASES — do not create new package rows:
  - `SET-01` ≡ TRUTH  (T-04/T-05/T-07 + T-18/T-19/T-20, CMX-10A)
  - `EDT-01` ≡ CHANGE (T-47, with T-17 already DONE; TLS-04/TLS-05)
  - `PRF-01` ≡ CMX-01 (already `REOPENED (product divergence)`)
  - `DIR-01` ≡ OCT-03 (+ T-31/T-54). Keep §2.10's OCT-* rows authoritative.
    NOTE: the octopus proposal's IDs are `ORCH-01..11` and `ORCH-M1..M3`, which
    are NOT the backlog's `OCT-01..04`. Map explicitly.

AMEND IN PLACE:
  - `T-18` → `REOPENED`. `TestTamperShield` (`runtime/governance/tamper_shield.py`)
    has ZERO production callers; the only importer repo-wide is
    `test/runtime/test_tamper_shield.py`. It is recorded `[x]` MECHANISM today.
    A mechanism with no caller is a test fixture. Reopen it in the SAME commit
    that records the grep as its falsifier.
  - `CMX-01` → `APPROVED`, absorbing draft PRF-01 (unifying preset catalogs).
  - `TLS-04` → `DONE (mechanism)` — `ast.parse` preflight already lives in
    `adapters/environment/transaction.py` and aborts before durable flush.
  - `CMX-02` dependency → IDX-01.
  - `OCT-03` title gains "(≡ draft DIR-01)"; dependency on MS-CONTROL made explicit.

REQUIREMENTS:
- Every row carries ID, Title, Subsystem, Lane, Status, Target Milestone, an
  explicit Reconciliation field, and an executable acceptance falsifier.
- Every row DECLARES ITS ADMISSION ROUTE (Synthesis of Record §9.1). This is the
  anti-sprawl mechanism and it is not optional:
    * `Route R` (Repair) — a defect verified at a named source line; the falsifier
      is a regression test; NO experiment is required. Measuring whether a broken
      instrument beats a broken instrument is not science.
    * `Route L` (Lift) — a mechanism claimed to improve an outcome the control
      already produces; requires a PREREGISTERED single-variable ablation against
      the Wave 2 control before it may leave `PROPOSED`.
  A row that can state neither route stays `PROPOSED`. A Route L row that loses
  its ablation moves to `DEFERRED` WITH ITS CONFIGURATION DIGEST RETAINED —
  retired, not deleted (§9.1).
- Update §3's package index rows (TRUTH, SEE, CHANGE, CONTROL, INSTRUMENT, COMPARISON, CAMPAIGN).
- Append the alias-table rows matching Synthesis of Record §4.4.
- Do NOT restamp `SUB-01` (§2.9's own standing instruction) or any DONE row not
  listed above.
```

---

### Prompt 02: Milestone Overlay Gates & Release Predicates

* **Target File**: `docs/execution/milestones.md`
* **Corpus anchor**: Synthesis of Record §6; **`opus/part7…` §5–§6**
* **Tree status**: v1's `MS-TRUTH` predicate contradicted the corpus it cited

```markdown
# ASSIGNMENT: Milestone Overlay Gates & Release Predicates
Target Document: `docs/execution/milestones.md` §3
Source: `.draft/ELECTROWEAK_SYNTHESIS_FINAL_v093.md` §6

Replace five overlay rows: MS-TRUTH, MS-SEE, MS-CHANGE, MS-CONTROL, MS-CAMPAIGN.

*** CRITICAL — READ BEFORE WRITING MS-TRUTH ***
An earlier revision of this blueprint instructed: "terminal state reporting fixed
(oracle pass records completed, never abandoned)". DO NOT WRITE THAT. It is
wrong three ways:
  (a) `agency/episode/state.py::RunTermination` documents itself as the
      run-termination axis ONLY, "because collapsing this with the evaluation
      outcome is how instrument failure silently becomes task failure".
  (b) `ICD §3` keeps the evaluation axis out of `agency/`, and
      `check_boundaries.py` enforces it structurally (`agency: {domain, ports,
      kernel}` — an evaluator import would not link).
  (c) The corpus says the opposite of the instruction. `opus/part7…` §6:
      "`disposition` is externally computed and STRUCTURALLY SEPARATE from
      `terminal`. Had this existed, the inversion would have been visible on day
      one." Opus's stated fix in §5 is the `finish` verb plus an admission gate
      that accepts a greenfield success shape — never a relabelled termination.

The 8/8 finding is NOT a mislabelled termination. Those runs genuinely exhausted
`max_turns`; `abandoned` is CORRECT on that axis. What was missing is that the
evaluation axis was never recorded at all, so the reporting layer printed the
only terminal word it had.

MS-TRUTH gate condition (correct form):
  - Eliminate `ADMISSION_GATE_EXEMPT` for coding packs (T-04) — live at
    `runtime/session.py:134` as `frozenset({"vg-code-default","vg-code-lex"})`
    — ONLY under the RF-25 successor baseline. Grok's review is explicit that it
    "is not authorization to shrink ADMISSION_GATE_EXEMPT" without it.
  - Wire `TestTamperShield` into `session._admit_completion` (T-18, REOPENED).
  - Bind a typed verification subject (T-07).
  - Greenfield oracle observed red-on-stub before green-on-impl (T-19).
  - Record BOTH settlement axes (T-72), neither derived from the other.
  - Greenfield vacuity rejection (T-81): a suite passing on empty stubs
    (`pass` / `NotImplementedError`) is rejected `VACUOUS_ORACLE_REJECTED`.
  - GATED ALSO ON THE INSTRUMENT (added in v4, matching §6 of the Synthesis of
    Record): INS-01 (**T-84**, **T-85**) and BRG-01 (**T-87**, **T-88**). A
    settlement claim recorded by an instrument that reuses a fixed run id,
    publishes an empty receipt, or may have addressed a different model than the
    one launched is not evidence.
  - FALSIFIER: a run may legitimately record `terminal_status=abandoned` AND
    `disposition=passed`, and the ledger replays it without contradiction.

For MS-SEE / MS-CHANGE / MS-CONTROL / MS-CAMPAIGN, copy §6 of the Synthesis of
Record verbatim. Corrected constants — do not re-round:
  - `.lda/index.db`: 80,618 relations at HEAD (the corpus's 77,610 was accurate
    at its own pin; the index is live and has grown — cite both if useful).
  - Kernel TCB: 1386 / 1438.
  - Presets: fast $0.05/8t/16k, balanced $0.15/20t/40k, max $0.40/40t/96k, from
    the EXISTING `packs/code-default/presets.json` (`aether.code-preset/1`).
    Do NOT invent $0.05/12, $0.20/25, $1.00/60 — that would restamp a frozen catalog.

Preserve all existing M-0..M-10 gates and the table schema.
```

---

### Prompt 03: HAR-01 — Harness Preconditions

* **Target Files**: `technical.md` (§ Harness & Agent Protocols), `spec.md` (§ Model Profiles & Tool Wire Formats)
* **Corpus anchor**: `opus/opus_solution.md` §2 (Defects A–J), `opus/part7…` §3 (K–O)
* **Tree status**: Defects A, C, E, F, K confirmed live; L, M, N, H need re-verification

```markdown
# ASSIGNMENT: technical.md + spec.md for HAR-01 (Harness Preconditions)
Source Evidence: opus_solution.md §2 (Defects A–J), part7 §3 (Defects K–O)

No settlement gate is REACHABLE until the agent can call tools, write, and
finish. Document the exact recipe, signatures, error types and falsifiers.

1. Native tool-calling profiles — `domain/models/profile.py`
   TREE: `ModelCapabilityProfile.tool_call_style` defaults to `FENCED_JSON`, and
   `_PROFILES` holds exactly TWO entries (`fake`, `openrouter/free`). Every
   production model hits the fallthrough `ModelCapabilityProfile(key)` and gets
   `FENCED_JSON`, so `dialect.py:124` dumps schemas as prose into the system
   prompt and the model's function-calling head never engages.
   FIX — CAPABILITY-BOUND, not blanket (narrowed in the Synthesis of Record §2;
   an earlier revision of this prompt said "per production model" and that is now
   wrong): add an explicit `ToolCallStyle.NATIVE` profile ONLY for production
   routes whose native-tool support is VERIFIED by a provider-shape vector:
   DeepSeek V4 Flash (`deepseek/deepseek-v4-flash-0731`) as primary, GLM 5.3 Flash
   (`z-ai/glm-5.3-flash`) as first fallback, DeepSeek V4 Pro (`deepseek/deepseek-v4-pro`)
   as second fallback, and `openrouter/free` for simple tasks. GLM 5.2 is excluded.
   Unverified and unknown registry entries MUST retain the honest degradation
   chain NATIVE→JSON_SCHEMA→FENCED_JSON→TEXT_GRAMMAR via `degraded()`.
   FALSIFIER: every native-declared route dispatches `patch.apply` and `finish`
   with no protocol degradation; an unverified route is never silently promoted.


2. Approval threshold — `runtime/session.py:656`
   TREE: `approval_required_above=(None if self.scope.sealed else "low")`.
   The manifest ALREADY DECLARES the policy the runtime ignores:
   `vg-code-default/approval-policy.json` = `{"mode":"assisted",
   "threshold":"standard","escalate_on":["proc.exec"]}`, registered under
   `components.approval_policy`. This is not a new artifact — it is a declared
   component the composition root never reads. Pure wiring.

3. `finish` verb declaration
   TREE: `finish-tool.json` exists in `vg-chimera-v1`, `vg-code-chimera`,
   `vg-code-max-v3`, `vg-code-max-v3luna` — and in NONE of the four product
   presets. The domain already accepts it (`ProposalKind.FINISH`,
   `adapters/models/invocation.py:94`). Only the declaration is missing.
   Specify the payload and place the file per Prompt 12's layout rules.

4. Defect K — SSE abort, `adapters/models/openrouter.py:1095` and `:1112`
   RE-VERIFIED AT HEAD: STILL PRESENT. Neither call site passes
   `retryable=True`, so `protocol_recovery` never engages and one bad chunk
   discards 2–3 completed effects. The module DEFINES
   `_MALFORMED_STREAM_MESSAGE` (`:943`) and `_EMPTY_PROPOSAL_RETRIES` (`:946`)
   and uses neither here; the sibling at `:930` IS retryable.
   WHY IT IS TOP PRIORITY: deepseek is routed non-streaming and is structurally
   IMMUNE, so the harness is silently biased toward its own default model. Any
   deepseek-vs-streaming A/B today measures the stream parser. ~3 lines.

5. Defect F — orientation commands blocked
   TREE CONFIRMED: `proc://exec/allow/git,pytest,ruff,python3` in both
   `vg-code-default/manifest.json:43` and `packs/code-default/harness.yaml:67`.
   `pwd`, `ls`, `cat` all denied. Specify the minimum orientation set and why
   each is safe under the existing selector grammar.

6. Defect L — duplicate `EffectStarted` (adjacent, identical `descriptorDigest`
   AND `leaseId`; present in all 9 corpus runs, every model).
   TREE: `runtime/ledger_emitter.py:83` declares `"EffectStarted":
   frozenset({"kernel"})` — kernel is the SOLE authorized originator, so a
   duplicate is a kernel-owner violation, materially worse than double-counting.
   REPRODUCE FIRST with a ledger-replay falsifier. Any fix landing in `kernel/`
   requires an ADR and consumes part of the 52-line TCB headroom.

7. Defect M — typed budgets not populated for effects. Re-verify, then specify.

8. `_completion_allowed_tools` binding (octopus §2) — the restriction is bound at
   engine construction INSIDE the `while True:` re-entry loop, so a fully
   autonomous preset with no approval round-trip iterates once and never applies
   it. Fix: re-check inside the turn loop. RE-VERIFY FIRST (octopus audited a
   different tree, `a8775c3f`).

9. Defect H — env map advertises `kind=git` but `init` never runs `git init`
   (`[exit 129] warning: Not a git repository`). Re-verify, then specify.

10. Purge `provider: ollama` from `packs/code-default/harness.yaml` tier 1
    (`qwen2.5:1.5b`) and resolve the unexpanded `"$FRONTIER"` literal at tier 3.
    Ollama is banned repository-wide per the llama-cpp standard and commit
    `ffc3dc92` ("wiped ollama from the project"); this config contradicts a
    shipped ban.

Provide exact snippets, signatures, typed error codes, and executable falsifiers.
```

---

### Prompt 04: Settlement Truth & the Two-Axis Disposition

* **Target Files**: `technical.md` (§ Settlement & Verification), `spec.md` (§ Evidence Models & Invariants)
* **Corpus anchor**: `grok/README.md` holes 1–4; `opus/part7…` §5–§6
* **Tree status**: exemption live; shield unwired; disposition axis absent from the domain

```markdown
# ASSIGNMENT: technical.md + spec.md for Settlement Truth
Source: grok §A.1–A.5, opus part7 §5–§6, Synthesis of Record §3
NOTE: this is NOT a package named "SET-01". It is the TRUTH package
(T-04/T-05/T-07 + T-18/T-19/T-20, CMX-10A). Use the live T-ids.

1. `ADMISSION_GATE_EXEMPT` removal (T-04)
   TREE: live at `runtime/session.py:134`. `admission_required()` already gates
   every OTHER preset by declared `patch.apply` capability — the name allowlist
   is the last bypass and it exempts the PRODUCT DEFAULT.
   CONSTRAINT: grok's review states this is "not authorization to shrink
   ADMISSION_GATE_EXEMPT without the RF-25 successor baseline named in T-04".
   Specify the baseline-recording step as a precondition, not a footnote.
   Also update the frozen assertion at
   `test/runtime/test_observed_test_counts.py:50`.

2. `TestTamperShield` wiring (T-18, REOPENED)
   TREE: zero production callers. `session._admit_completion` (`:1655`) checks
   epoch, omissions, and `policy.evaluate` — never tamper.
   Specify the join per GPT §A: completion for an implementation task must bind
   ALL of — mutation receipt AND postimage/epoch matching the current workspace
   AND relevant tests collected and executed AND zero test exit code AND tamper
   shield evaluated against the frozen test set AND no unresolved omission or
   stale-index marker. Do not rewrite T-18's shield or the epoch/refresh work.

3. Implicated tests as verification subject (T-20)
   TREE: grok hole 3 — session does not pass `implicated_files` /
   `callers_by_symbol` into pack completeness, so a 40-file signature change can
   "complete" after one file plus an unrelated pytest.

4. THE TWO-AXIS SETTLEMENT CONTRACT — `domain/evidence/disposition.py` (NEW)
   Copy §3.2 of the Synthesis of Record VERBATIM. Key points:
   - The enum is `TaskDisposition`, not `ExecutionDisposition` (an earlier draft
     used the latter; align on one name before writing spec.md).
   - `SettlementReceipt` carries `terminal_status` as a plain `str`, NEVER a
     `RunTermination`: `domain` cannot import `agency`, and the coupling would be
     wrong even if it linked.
   - `__post_init__` refuses: PASSED with `executed_test_count == 0`; PASSED
     without a bound oracle + verification subject; UNDETERMINABLE without a
     reason; NOT_RUN carrying any execution evidence.
   - `disposition_to_outcome()` REFUSES on NOT_RUN. `envelope.py::OUTCOMES` has
     three members by design — an envelope binds a claim to an EXECUTED subject,
     so a task that never ran has nothing to sign. The vocabularies differ by
     exactly one member and that difference is load-bearing.
   - `satisfies_predicate` is a property so no caller can spell the G-1 check as
     `!= FAILED` and quietly admit `undeterminable`.

5. LEDGER REPRESENTATION — allocate NO new event kind.
   `domain/ledger/events.py` states that adding a kind "requires a full kind
   package — ADR, allocation, writer, reducer, schema, golden vector, and
   coverage proof — never a one-line addition". `READABLE_KINDS` is derived from
   `schemas/mhf/event_envelope.schema.json`; `WRITABLE_KINDS` holds 55 members.
   Map the two axes onto two kinds that already exist:
     - run termination  → `EpisodeCompleted`, payload `terminal_status` only,
       shape UNCHANGED, and it must never gain a `disposition` field.
     - task disposition → `VerdictRecorded`, payload `SettlementReceipt.to_wire()`
       under `schema: aether.settlement/1`.

6. Collapse the duplicate vocabulary. `benchmarks/protocols.py:30` owns
   `RESULT_DISPOSITIONS` as a bare frozenset of strings, invisible to the
   runtime. Rebind it to `frozenset(d.value for d in TaskDisposition)` and have
   `classify_disposition()` return the enum, preserving its existing
   `_UNDETERMINABLE_MARKERS` precedence (missingness beats a PASS status — that
   is already correct).

FALSIFIER SET: PASSED@0-tests raises; UNDETERMINABLE without reason raises;
NOT_RUN with an envelope digest raises; `disposition_to_outcome(NOT_RUN)` raises;
a ledger with `terminal_status="abandoned"` + `disposition=passed` replays
without contradiction; `EpisodeCompleted` payloads contain no `disposition` key.
```

---

### Prompt 05: Edit Primitive — exact `str_replace` on the existing 2PC

* **Target Files**: `technical.md` (§ Edit Engine), `spec.md` (§ Patch Primitives & Errors)
* **Corpus anchor**: `opus/part3…` §5.2–5.3; `opus/README.md` §Divergences
* **Tree status**: 2PC and AST preflight already exist — only `str_replace` is new

```markdown
# ASSIGNMENT: technical.md + spec.md for the edit primitive
Source: opus part3 §5.2–5.3, opus README §Divergences, grok (atomic 2PC)
NOTE: this is NOT a package named "EDT-01". It amends T-47 in the CHANGE package
(T-17 is already DONE; TLS-04/TLS-05 cover preflight and checkpoints).

1. REJECT the treatise's 9-strategy fuzzy cascade — and record the full argument,
   because it is load-bearing rather than stylistic:
   - In indentation-sensitive languages indentation IS semantics, so
     "indentation-flexible" matching can apply a syntactically valid edit at the
     WRONG NESTING LEVEL and produce a silent behavioural change with no error.
   - The treatise's own F1 case study records that the actual damage came from
     the model's FALLBACK TO A WHOLE-FILE OVERWRITE after rejection — not from
     the rejection. So the correct fixes are: a clean rejection that re-shows
     current file content, a parse preflight before commit, and REMOVING
     whole-file overwrite as a recovery path.
   - Strategies 1–2 (exact, trimmed-EOL) are safe. Strategies 3+ trade a loud
     failure for a quiet one.

2. Exact-match `str_replace`: unique preimage required. Non-unique or not found
   → fail closed with typed `PATCH_PREIMAGE_MISMATCH` carrying line offsets,
   forcing a targeted `fs.read` re-anchor. No fuzzy relocation, no full-file
   overwrite fallback.

3. Read-before-edit — AN EXPERIMENT, NOT A UNIVERSAL PROHIBITION. This changed
   in the Synthesis of Record §2 and an earlier revision of this prompt has the
   old form ("move the check to `patch.apply` dispatch"). DO NOT WRITE THAT as an
   unconditional gate: a hard dispatch prohibition repeats the `derive_phase`
   error — controlling the PATH instead of the OUTCOME — which §0 resolution 3
   rejects.
   TREE: `_completion_inspected_files` is already tracked in session and consulted
   at completion.
   SPECIFY INSTEAD: (a) read-before-edit as prompt guidance in the default pack,
   and (b) a declared STRICT PROFILE that enforces it at `patch.apply` dispatch
   with typed `MODIFIED_FILE_NOT_INSPECTED`, switchable independently so it can be
   A/B-ablated against the Wave 2 control. Security-sensitive profiles may require
   it explicitly. This is a Route L row (§9.1): it claims lift, so it needs a
   preregistered ablation, not an argument.

4. 2PC — DO NOT REBUILD. TREE: `adapters/environment/transaction.py` already
   ships `AtomicMultiFileTransactionManager`, `FileMutation`,
   `TransactionReceipt`, `TXN_TMP_MARKER`, and opens with the docstring
   "I-7 / I-TXN: `ast.parse` lives here, never in `kernel/`." Route `str_replace`
   THROUGH it. Document the existing shadow-staging → validate-all →
   commit-or-restore state machine; do not author a second one.

5. AST preflight — ALREADY DONE. It is in `transaction.py`, NOT in `git.py` as an
   earlier revision of this blueprint claimed. `grep -c "import ast"
   vanguard/packages/kernel/*.py` is 0. Close TLS-04 as mechanism-present rather
   than specifying it as new work.

FALSIFIER: a 5-file edit with a syntax error in file 4 leaves all five
byte-identical (`tree_hash_before == tree_hash_after`); no fuzzy path exists by
inspection; and — for the read-before-edit treatment — a strict-profile run and a
control run differ ONLY by the declared read-before-edit policy, with the strict
run rejecting a patch to an uninspected file at dispatch and the control run not.
```

---

### Prompt 06: IDX-01 — LDA-backed `IndexPort` & cache stability

* **Target Files**: `technical.md` (§ Repository Intelligence), `spec.md` (§ Index Port Contracts)
* **Corpus anchor**: `opus/part3…` §6.2; `opus/README.md` §Divergences 2; `ports/index.py`
* **Tree status**: port exists and is not modified; two adapters exist; `.lda/index.db` has grown

```markdown
# ASSIGNMENT: technical.md + spec.md for IDX-01
Source: opus part3 §6.2, opus README §Divergences 2, ports/index.py

1. `LdaRepoIndex` — NEW adapter at `adapters/stores/lda_index.py`, a THIRD
   implementation beside the existing `FileRepoIndex` and `InMemoryRepoIndex` in
   `adapters/stores/repo_index.py`. `ports/index.py` is NOT modified — it already
   declares `Symbol`, `DependencyEdge`, `TestAssociation`, `RepositoryMap`, and
   `IndexPort`. Today the agent's `IndexPort` resolves to a five-regex file scan
   while an 80,618-edge graph sits unused.
   MEASURED AT HEAD: relations 80,618 · symbols 10,580 · entities 14,033 ·
   files 3,372 · documents 262 · doc_sections 5,244 · FTS5 corpus 90,028 ·
   39 index runs. (The corpus cites 77,610 at its own pin; the index is live.)
   Return VALUE-ONLY results — "a caller cannot reach back through a symbol into
   the indexer's state". A missing or stale DB returns a deterministic
   `Result.fail`, never a partial map (preserves T-45's documented fallback).

2. Observation tools into L5 ONLY: `repo.search_symbols`, `repo.get_callers`,
   `repo.get_dependencies`, `repo.get_tests`. Bounded outputs.

3. REJECT PPR auto-injection into L2, recording BOTH corpus objections:
   - ARCHITECTURAL: `ports/index.py` states the rule directly — "a retrieval
     component that decided what the agent should look at next would be a second
     policy wearing the word 'index'" (A-05, AT-01).
   - MECHANICAL: `agency/context/layers.py` documents that L2 is inside the cache
     prefix and that mid-run additions to L1–L4 destroy every downstream cache
     hit — forfeiting the ~90% saving the same treatise advocates elsewhere.
   PageRank over the LDA graph IS valuable — as a ranking function BEHIND an
   agent-issued `refs`/`callers` query returning into L5. Ranking is pack policy
   (`context_ranker`), never the port. T-46 is therefore NARROWED, NOT ERASED
   (Synthesis of Record §4.1/§6 — an earlier revision said "superseded", which
   reads as deletion): optional query-local PPR ranking survives as an A/B-able
   pack policy inside an agent-issued request. No ranking enters `IndexPort`, the
   store adapter, or L1-L3.

4. Provider cache breakpoints at the L3 boundary; record `cache_read_tokens` /
   `cache_write_tokens`.
   CALIBRATION: caching is NOT wholly absent. `opus_solution.md` §3.1 walks back
   part2 §D3 — DeepSeek returns `cached_tokens: 2048/2304`, so the prefix-stable
   compiler already earns its design there, and `harness.yaml` already declares
   `context.config.prefix_freeze: true`. Explicit `cache_control` still matters
   for Anthropic-style providers. Specify it as telemetry + breakpoint emission,
   not as a headline defect.

BOUNDARY: `check_boundaries.py` grants `adapters: {domain, ports}`. The adapter
CANNOT import agency or runtime, so the L5 tool binding lives in the pack
(`packs/code-default/toolkits/`, `plugins/index.yaml`) and `adapters/bindings/`.

FALSIFIER: `repo.get_callers` over a 40-file blast radius leaves the L1–L3 digest
BIT-IDENTICAL across 10 turns; turn ≥2 cache-hit rate exceeds 85%; no ranking
logic exists in `lda_index.py` by inspection.
```

---

### Prompt 07: Greenfield Oracle, Workspace Hygiene & Distillation

* **Target Files**: `technical.md`, `spec.md`
* **Corpus anchor**: `opus_solution.md` §2.6 (F–J); `grok/README.md` hole 4; `octopus/…evidence-audit.md` §4
* **Tasks**: T-15, T-19, T-36, T-37, T-74

```markdown
# ASSIGNMENT: technical.md + spec.md for Greenfield Oracle & Hygiene
Source: opus_solution §2.6 (Defects F–J), grok README hole 4, octopus §4

1. Defect G — workspace `.pyc` churn. `PYTHONPYCACHEPREFIX` writes INTO the
   workspace (~30 `.pyc` under `<ws>/cache/python/...`, quantified at 178x
   amplification in part7 §3.5). Opus: this "silently poisons the exact signal
   AdmissionGate and your benchmark oracles depend on. Any before/after digest
   comparison is meaningless while it persists." Route to tmpfs OUTSIDE the tree.
   TREE NOTE: `adapters/stores/repo_index.py` already excludes `__pycache__` from
   INDEXING via `_IGNORED`; workspace DIGESTS are computed elsewhere and remain
   exposed. Do not mistake the first for the second.

2. Defect I — `.pytest_cache/` counted as agent-authored output (corpus rows 8–9
   list four `.pytest_cache` entries beside the two real files).

3. Defect J — ledger churn: 44 of 88 baseline events are plugin lifecycle
   (11 plugins × Discovered/Resolved/Verified/Activated, plus Quiesced/Retired)
   for THREE turns of work. Specify a retention/scope policy. Do not delete kinds
   — `DEPRECATED_KINDS` discipline in `domain/ledger/events.py` makes historical
   kinds permanently readable; this is a WRITE-VOLUME question, not a vocabulary one.

4. Greenfield red-then-green (T-19) — and fix the SPECIFIC defect grok names:
   the evidence mapping ALIASES `structural_passed` = `behavioral_passed` =
   `verification.passed` and NEVER SETS `oracle_failed_on_stub`. Until those are
   distinct fields the red-then-green obligation is unrepresentable.
   Also resolve the contradiction grok names: the system prompt's "do not read
   first" law FIGHTS the pack policy (scaffold + oracle-fail-on-stub). State
   which wins and edit the loser.
   Reject vacuous passes on `pass` / `NotImplementedError`.

5. Semantic test-output distillation on `proc.exec` results (~1200→180
   tokens/turn). Octopus §4 calls this "the single highest-leverage unimplemented
   item". `parse_test_output` already exists in `forge/engine.py` — reuse the
   parser, add the filter. Note Forge is quarantined from PRODUCT SCORES (T-23,
   D-02); reusing a pure parsing function is not running a second engine, but say
   so explicitly so the boundary linter's intent is not misread.

6. Cache telemetry — see Prompt 06 §4 for the severity calibration.
```

---

### Prompt 08: Preset Catalog Unification (CMX-01)

* **Target Files**: `technical.md` (§ Presets & Control Baseline), `spec.md` (§ Product Presets & Budgets)
* **Corpus anchor**: `grok/README.md` hole 8; `opus/part7…` §3.6 (Defect O)
* **Tree status**: the differentiated catalog already exists and the product path never reads it

```markdown
# ASSIGNMENT: technical.md + spec.md for CMX-01 (Preset Unification)
Source: grok README hole 8 ("fast/balanced/max being identical is a product
lie"), opus part7 §3.6 (Defect O)
NOTE: this is NOT a new package named "PRF-01". It is CMX-01, already REOPENED
in backlog §2.9 as "product divergence".

*** DO NOT INVENT BUDGET NUMBERS ***
An earlier revision specified fast $0.05/12t/32k, balanced $0.20/25t/64k, max
$1.00/60t/128k. Those figures appear NOWHERE in the tree and would restamp a
frozen catalog. There is no `$1.00` literal in the runtime composition path.

TREE — two disjoint catalogs, and the product path reads the dead one:
  - `packs/code-default/presets.json` (`aether.code-preset/1`), loaded by
    `packs/code-default/load.py`, ALREADY declares differentiated budgets:
      fast     usd_micros 50000  · millis 300000  · tokens 16000 · turns 8
      balanced usd_micros 150000 · millis 900000  · tokens 40000 · turns 20
      max      usd_micros 400000 · millis 2400000 · tokens 96000 · turns 40
    with per-preset planner/context overlays.
  - `packs/code-default/harness.yaml` base budget: usd_micros 250000, millis
    1800000, tokens 64000, bytes 0, turns 40, depth 2.
  - `apps/coding_max/facade.py::_manifest()` routes preset → 
    `agency/manifests/vg-code-{preset}/manifest.json`. Those three manifests are
    BYTE-IDENTICAL ALIAS SHELLS: every `components` entry points at
    `vg-code-default/*`, and all three share `budgetPolicy:
    vg-code-default/budget-policy.json` = `{tokens, wallClockMillis, effects,
    evaluations, depth}` — carrying NO COST and NO TURN dimension at all.
  - The facade additionally hardcodes `max_turns: int = 40` as a Python default,
    overriding whatever a preset declares.

THE WORK is unification, not authorship: make the product path select from
`presets.json`, give each manifest a real per-preset `budgetPolicy`, and delete
the facade's turn default. Then verify passthrough to `EpisodeStarted.budgetCeiling`.

NOTE on dimensions: `kernel/budget.py` declares
`ADDITIVE_DIMENSIONS = {usd_micros, millis, tokens, bytes}` and documents that
`depth` and `turns` are STRUCTURAL ceilings deliberately excluded from
`Reservation`, because summing sibling depths is wrong. Any spec text must
respect that split rather than describing "typed budgets" as one flat bag.

MS-CONTROL: frozen ≥30-task multi-class canary, Wilson lower bound ≥ 0.40 on
single-worker `vg-code-balanced`, EXECUTED THROUGH `runtime/entrypoint.py`
(**T-89**, finding **C-18**): `benchmarks/agentic_harness_matrix_benchmark.py:98`
calls `Runtime.execute_profiled` directly today and therefore qualifies a
DIFFERENT SUBJECT than the product ships. MS-CONTROL qualifies what ships, or it
qualifies nothing.

Report under the §9 evidence standard: **false-completion rate = 0 is a HARD
VETO** that no pass rate, token efficiency, or cost advantage overrides, and
Wilson LB is computed only over `evidence_label=LIVE-*` rows.

T-80 (anti-thrashing oscillation breaker) is a POST-CONTROL TREATMENT and does
NOT gate this baseline. Release law: zero specialist or director lift claims
authorized before this gate closes (D-03).
```

---

### Prompt 09: Outer Director (OCT-03) — staged post-MS-CONTROL

* **Target Files**: `technical.md` (§ Campaign Orchestrator), `spec.md` (§ Campaign DAG & Mailbox)
* **Corpus anchor**: `octopus/consolidation/outer-loop-orchestrator.md`, `proposed-backlog-outer-loop.md`
* **Tree status**: `runtime/campaign/` and `runtime/outer_loop/` do not exist

```markdown
# ASSIGNMENT: technical.md + spec.md for the Outer Director
Source: octopus outer-loop-orchestrator.md + proposed-backlog-outer-loop.md
NOTE: this is NOT a new package named "DIR-01". It is OCT-03, already PROPOSED in
backlog §2.10.

ID HYGIENE — an earlier revision said "stages OCT-01..11". There is no OCT-05..11.
  - The backlog's own family is `OCT-01..04` (§2.10).
  - The octopus proposal's IDs are `ORCH-01..11` (Lane A) and `ORCH-M1..M3`
    (Lane B), with its own milestone ladder `M-O1..M-O5`.
  These are DIFFERENT NAMESPACES. Map explicitly; do not merge by resemblance.

SEQUENCING IS THE WHOLE POINT. Every reviewer converged on it independently:
  - opus README: "an outer loop that dispatches a harness which cannot patch a
    file multiplies zero."
  - grok README: "Until (1), (2) is a false-completion factory with extra DAG nodes."
  - octopus §5: "the substrate cannot yet reliably run ONE agent for six turns
    and know when it has succeeded. Swarms multiply that uncertainty by k."
  Record this as the gate rationale, not as commentary.

1. `SequentialDirector` in `runtime/campaign/director.py` (NEW) — a runtime
   CLIENT of `EpisodeEngine` with ZERO mutating tools (`patch.apply`,
   `proc.exec` withheld). Not a second engine (D-02).
2. Ephemeral git worktrees per child episode; siblings cannot reach each other.
3. CAS mailbox (OCT-01) + `CoordinationPlan` DAG (OCT-02) with
   `Σ budget_share ≤ 1000` per-mille shares and merge policies CONCAT /
   FIRST_COMPLETE / SYNTHESISE / UNANIMOUS.
4. Merge by `ExternalVerifier` test verdict ONLY. REJECT `ORCH-10`'s evolutionary
   / LLM-quorum merge: code merges are decided by compilers and tests, never votes.
5. Crash at node K resumes at K+1 with no duplicate effects.

Adopt the octopus non-goals verbatim: no kernel change; no new persistence engine
(`EventBus` is a PROJECTION over the existing SQLite-WAL ledger); no forked
memory/retrieval system (extend LDA); `ORCH-10` is off the critical path.
```

---

### Prompt 10: Instrument Integrity & Measurement Ladder (INS-01, BRG-01, DLG-01, EXP-01)

* **Target Files**: `technical.md` (§ Benchmark Instrument), `spec.md` (§ Results Schema & Evidence Standard)
* **Corpus anchor**: `octopus/…evidence-audit.md` §1/§3b/§5; `opus/part7…` §6; `gpt/…` §B/§E/§PR-2/§PR-3; Synthesis of Record §4.1, §9
* **Packages**: `INS-01` (T-84, T-85, T-89, T-97), `BRG-01` (T-87, T-88, T-91), `DLG-01` (T-86, T-90), `EXP-01` (T-92..T-95)
* **Wave**: 1 (P0) → Wave 2 (MS-CONTROL) — gates the interpretation of every measurement

```markdown
# ASSIGNMENT: technical.md + spec.md for Instrument Integrity (INS-01, BRG-01, DLG-01, EXP-01)
Source: Synthesis of Record §4.1, §9; octopus evidence-audit §1, §3b; opus part7 §6; gpt §B, §E, §PR-2/PR-3

WHY THIS IS FIRST. Octopus: these items "are collectively a few hundred lines.
They are worth more than any new layer, because every new layer is currently
being evaluated against numbers that do not mean what they appear to mean."
Opus part7 §5: "no benchmark this project runs can be believed, in either
direction — and that includes these results."

Deliver the four instrument packages:

1. RESULTS SCHEMA & EVIDENCE ROW (EXP-01, T-93, T-94).
   Add `n`, `suite_digest`, and enforce §9.3's append-only evidence row schema.
   `runner.py` must REFUSE to write `pass_rate_pct` when `len(results) < suite_size`.
   Adopt §9.4 metric set with **false-completion rate = 0** as a HARD VETO: no pass
   rate or cost advantage overrides it. Wilson LB is computed only over rows with
   `evidence_label=LIVE-*`.

2. ADOPT TWO-AXIS RESULTS SCHEMA (T-72, T-93).
   - `disposition` (TaskDisposition: passed, failed, undeterminable, not_run)
     externally computed and structurally separate from `terminal` (RunTermination).
   - An oracle-tamper digest — without it, a tests-pass oracle is unfalsifiable.
   - Separate `REPLAY` and `LIVE-*` rows into disjoint tables. Zero model calls
     (provider outage, HTTP error) is recorded as `not_run`, never model failure.
   - Hypothesis registry (T-95): bind every Route L mechanism to a preregistered
     single-variable ablation against the control.

3. LIVE DIALECT VALIDATION & PROVENANCE (DLG-01, T-86, T-90).
   Pass manifest `aliases.json` into `ProposalTranslator.translate` on the live
   path (`openrouter.py:1204`). Validate tool name/arguments against declared
   schema; reject undeclared tools fail-closed (no fuzzy guessing). Record
   raw-response digest and typed classifier class in the ledger.

4. DURABLE RUN IDENTITY (INS-01, T-84).
   Replace `entrypoint.py:56` literal `"run-cli"` with generated UUID/ULID per run.
   Resume is EXPLICIT opt-in (`--resume <id>`).
   FALSIFIER: two successive invocations in one workspace produce DIFFERENT ledgers.

5. PRODUCT RECEIPT TELEMETRY (INS-01, T-85).
   `entrypoint.py:218` must pass through real `modelRoutes`, non-null token counts,
   `verifiedStepIds`, and cost provenance from `compose.py` / `app_service.py`.

6. BENCHMARKS EXECUTE PRODUCT PATH (INS-01, T-89).
   Change `agentic_harness_matrix_benchmark.py:98` to execute via
   `runtime.entrypoint.execute` rather than calling `Runtime.execute_profiled`
   directly. MS-CONTROL qualifies what ships, or it qualifies nothing.

7. LOCAL INFERENCE INSTRUMENT FAIL-CLOSED (BRG-01, T-87, T-88, T-91).
   In `tools/llama_cpp/cli.py`: fix `--flash-attn` flag; readiness requires
   `proc.poll() is None`, matching child PID, and `/props` identity match;
   `stop` never issues blanket `pkill`. In `mcp_server.py`: return typed empty
   failures. Purge `ollama` from `packs/code-default/harness.yaml`.
```

---

### Prompt 11: Atomic Task Work-Tree Deconstruction (T-69 through T-97)

* **Target File**: `docs/execution/tasks.md`
* **Source**: Synthesis of Record §4.5 (T-69..T-97)

```markdown
# ASSIGNMENT: Atomic Task Staging in tasks.md (T-69 through T-97)
Source: `.draft/ELECTROWEAK_SYNTHESIS_FINAL_v093.md` §4.5

Populate `docs/execution/tasks.md` with flat, dependency-ordered tasks covering
the complete Electroweak v0.9.3 scope (T-69 through T-97).

ID ALLOCATION: current maximum is T-68. Start at T-69. Allocate through T-97.
Do not renumber prior tasks.

SUBSYSTEM VOCABULARY matching `tools/linters/check_boundaries.py::PACKAGE_NAMES`:
  domain | ports | kernel | agency | runtime | adapters | apps | packs/ | benchmarks/ | tools/

Schema per task:
  ### T-XX: <Title>
  - **package**: HAR-01 | INS-01 | DLG-01 | BRG-01 | EXP-01 | ARM-01 | IDX-01 | TRUTH | CHANGE | CONTROL | CAMPAIGN
  - **subsystem**: <subsystem>
  - **lane**: Lane A (Build/Core) | Lane B (Audit/Test)
  - **requires**: [T-YY, ...]
  - **file_touches**: [<paths VERIFIED to exist, or marked [NEW]>]
  - **specification**: <2–3 sentences>
  - **acceptance_falsifier**: <exact executable command or test>

TASK INVENTORY TO COMMIT (from Synthesis of Record §4.5):
  - T-69: Capability-bound native tool-call profiles (HAR-01, Lane A)
  - T-70: Approval threshold from declared approval_policy (HAR-01, Lane A)
  - T-70a: Reproduce mid-stream SSE abort before flag change (HAR-01, Lane B)
  - T-71: Declare finish-tool.json in product presets (HAR-01, Lane A)
  - T-72: Two-axis settlement contract domain/evidence/disposition.py (HAR-01, Lane A)
  - T-73: EffectStarted single-emission ledger falsifier (HAR-01, Lane B)
  - T-74: Workspace .pyc hygiene via tmpfs (HAR-01, Lane A)
  - T-75: LdaRepoIndex adapter over .lda/index.db (IDX-01, Lane B)
  - T-76: repo.* observation tools bound into L5 only (IDX-01, Lane B)
  - T-77: Cache breakpoints, CTRF distillation & Trailing Goal Echo (IDX-01, Lane A)
  - T-78: Exact-match str_replace primitive in 2PC transaction manager (CHANGE, Lane A)
  - T-79: Unify preset catalog on presets.json (CMX-01, Lane A)
  - T-80: Anti-thrashing workspace oscillation breaker dt == dt-2 (CONTROL, Lane A)
  - T-81: Greenfield oracle vacuity rejection check (TRUTH, Lane B)
  - T-82: Fenced JSON action unwrapping & anti-premature finish (HAR-01 / TRUTH, Lane A)
  - T-83a: Greenfield prompt modernization — purge "Write ONE file per turn /
      do not read or search first" from `system-prompt.txt` (TRUTH, Lane A).
      requires: [] — a pure prompt edit with NO dependency. WAVE 1.
  - T-83b: `callers_by_symbol` completion admission — wire `IndexPort.get_callers`
      into `session._admit_completion` via `multi_file_completeness.py`
      (CHANGE, Lane A). requires: [T-75]. WAVE 3.
      *** SPLIT REQUIRED — DO NOT FILE T-83 AS ONE TASK ***
      Synthesis of Record §4.5 gives T-83 `depends_on: T-75, T-78` while §7 places
      it in Wave 1 — but T-75 (`LdaRepoIndex`) and T-78 (`str_replace`) are BOTH
      Wave 3. Filed as a single task it is unbuildable: the caller-admission half
      would call `IndexPort.get_callers` two waves before the index adapter that
      makes it useful exists. The prompt half has no such dependency and belongs
      in Wave 1 with the rest of the greenfield law. Split it, and record the
      split back into the Synthesis of Record §4.5/§7 so the three documents do
      not diverge.
  - T-84: Unique durable run identity; explicit resume (INS-01, Lane A)
  - T-85: Product receipt telemetry passthrough (INS-01, Lane A)
  - T-86: Live-path alias & tool-name validation (DLG-01, Lane A)
  - T-87: Bridge lifecycle fail-closed (BRG-01, Lane B)
  - T-88: MCP fail-closed completions (BRG-01, Lane B)
  - T-89: Benchmarks execute product path entrypoint.execute (INS-01 / EXP-01, Lane A)
  - T-90: Raw-response digest & dialect classifier provenance (DLG-01, Lane B)
  - T-91: Native-only alias & environment purge (BRG-01 / HAR-01, Lane B)
  - T-92: L0 smoke triad through public CLI (EXP-01, Lane A)
  - T-93: L1 frozen pre-canary & evidence row schema (EXP-01, Lane B)
  - T-94: Metric set & false-completion veto = 0 (EXP-01, Lane B)
  - T-95: Hypothesis registry & preregistration harness (EXP-01, Lane B)
  - T-96: Arm matrix & LAM-first comparison protocol (ARM-01, Lane B)
  - T-97: CLI product surface — reproduce then repair (INS-01, Lane A)

WAVES (Synthesis of Record §7):
  Wave 1 — HAR-01 (T-69..T-74, T-82) + TRUTH (T-04, T-05, T-07, T-18 REOPENED, T-81, T-83a) + INS-01 (T-84) + BRG-01 (T-87, T-88, T-91)
  Wave 2 — CMX-01 (T-79) + INS-01 (T-85, T-89) + EXP-01 (T-92..T-95) + MS-CONTROL canary (N ≥ 30)
  Wave 3 — CHANGE (T-78 exact str_replace, T-83b caller admission) + IDX-01 (T-75..T-77) + DLG-01 (T-86, T-90)
  Wave 4 — Context Economy & Trailing Echo (T-77) + Anti-thrashing breaker (T-80)
  Wave 5 — OCT-01..04 (T-31, T-54) + ARM-01 (T-96), blocked on MS-CONTROL closed

COLLISION NOTE: runtime/session.py carries FOUR Wave-1 edits at four distinct
sites (:134 exemption, :656 approval, :1655 tamper wiring, caller admission).
Lane A serializes them; Lane B touches the file only through test/.

No sprint calendars, no dates, no WIP tags. requires: edges only.
```

---

### Prompt 12: Constitutional Invariant & TCB Budget Audit

* **Target**: the whole runway + linters

```markdown
# ASSIGNMENT: Constitutional Invariant & TCB Budget Audit

1. TCB CEILING. Run `python3 tools/linters/check_tcb_budget.py`. It must report
   1386 UNCHANGED — not merely "under 1438". Current: 1386 logical lines across
   9 files, baseline 1307, threshold 1438, i.e. 52 lines of headroom. Headroom is
   not a budget to spend. The ONE Wave-1 item that could touch it is the
   duplicate-`EffectStarted` fix, since `ledger_emitter.py:83` names `kernel` the
   sole authorized originator — that fix needs an ADR.

2. DOMAIN BLINDNESS (I-7). `grep -c "import ast"
   vanguard/packages/kernel/*.py` must be 0. AST preflight is confined to
   `adapters/environment/transaction.py` — NOT `git.py`, which an earlier
   revision of this blueprint claimed. T-64 already exists as the kernel AST
   prohibition regression test.

3. HEXAGONAL FLOW. Verify against `check_boundaries.py::ALLOWED`, which is the
   authority, not prose:
     kernel:  {domain, ports}
     agency:  {domain, ports, kernel}
     adapters:{domain, ports}          ← may NOT import kernel OR agency
     runtime: {domain, ports, kernel, agency, adapters, governance}
     apps:    everything; nothing imports apps back
   `SUBPROCESS_HOME = adapters/sandbox/` — process creation cannot migrate inward.
   `ports/index.py` stays a neutral protocol with no embedded ranking.

4. SINGLE RUNTIME PATH (D-02). One `EpisodeEngine` on the product path.
   Chimera/Forge quarantined from product scores (T-23, DONE). Reusing a pure
   parsing function from `forge/` is not running a second engine — say which.

5. MANIFEST LAYOUT. `components` is a MAP in `manifest.json`, whose values are
   paths relative to the MANIFESTS ROOT (which is what lets `vg-code-fast`
   reference `vg-code-default/read-tool.json`). Tool schemas are FLAT
   `<verb>-tool.json` at the manifest directory root. There is NO
   `components/tools/` directory anywhere — an earlier revision invented it. The
   `tools/` subdirectory exists in exactly ONE of 32 manifests (`vg-herbs`) and
   is not canonical. Skills are `skills/<n>.json` + `<n>.md` PAIRS. Kinds come
   from `manifests/kinds.json` (17); registration from `manifests/registry.json`.
   Assert: no manifest introduces a `components/` directory.

6. ANTI-SPRAWL. Zero new markdown under `docs/reports/` or `docs/architecture/`.
   All runway updates confined to the canonical five files. This blueprint and
   the Synthesis of Record stay in `.draft/` and are not runway files.

OUTPUT: formal PASS/FAIL per invariant, with an exact remediation diff on failure.
```

---

### Prompt 13: Kill List & Non-Goals Register

* **Target File**: `docs/execution/backlog.md` (§7 Risks / a new Non-Goals block)
* **Corpus anchor**: `gpt/…` "What not to build yet"; `grok/README.md` "What this review is not"

```markdown
# ASSIGNMENT: Kill List & Non-Goals Register
Source: gpt "What not to build yet", grok README "What this review is not"

Every reviewer independently produced a kill list, and v1 of this blueprint
carried none of them. A backlog that records only what to build will re-grow the
rejected items as "new ideas" next quarter. Register these as NON-GOALS with
their rationale, so a future proposal must argue against a recorded decision
rather than into a vacuum:

- No second `EpisodeEngine`; no Forge/Chimera in product scores; no swarm or
  topology as a DEFAULT (D-02, T-23).
- No new provider abstraction or local inference plane.
- No kernel coding semantics, AST machinery, memory, or learning layers.
- No broad UI work before truthful headless JSON.
- No leaderboard mixing live results, replay, provider errors, or zero-call rows.
- No claim that grammar constraints or min-p remove semantic hallucination.
- NO PROMPT-REWRITE QUARTER. Grok: "AHE-class evidence: tools/middleware/memory
  beat system prompts. Do not spend a quarter on `system-prompt.txt`." This is
  the most easily violated item on the list because prompt edits feel productive
  and are cheap to ship.
- No shrinking of `ADMISSION_GATE_EXEMPT` without the RF-25 successor baseline.
- No official SWE/DeepSWE claim from local runs (G-3).
- `ORCH-*` packs, the SONNET four paradigms, and any "RATIFIED" badge in
  `future_improvements_sota_harness_2808.md` are NOT HEAD.

Also register GPT's DEFINITION OF THE FIRST REAL PRODUCT as the Coding-P0
acceptance predicate — it is the most concrete "done" statement in the corpus:
  1. a fresh repository changed through the public CLI, with unique durable run
     identity and an inspectable ledger;
  2. the local model executes declared canonical tools or emits a typed honest
     protocol failure — prose cannot become an effect or a success;
  3. `completed` binds current mutation, postimage, tamper evaluation, and a
     passing frozen EXTERNAL oracle;
  4. P0-FIB, P0-CSV, P0-BUG pass in fresh workspaces, or failure is honest and
     trajectory-backed;
  5. a frozen 12-task canary retains model/server/task identity, routes, tokens,
     turns, latency, costs/missingness, false-completion rate, trajectories;
  6. replay can reproduce decisions without being presented as fresh model skill.
```

---

## 6. Standing rules for whoever runs this suite

1. **Prompt 00 is a gate.** Do not start 01 until the drift table exists.
2. **One prompt per commit.** These edit living documents that three other
   documents cross-reference.
3. **Corpus claims are hypotheses.** Re-run the reproduction command. Three
   claims have already moved: `ProgressVector` is now wired (CLOSED), prompt
   caching was downgraded by its own author, and Defect K turned out MORE severe
   than the Synthesis of Record's first hedge.
4. **Never derive one settlement axis from the other.** It is the single defect
   that corrupted every historical number in this repository, and it entered v1
   of this blueprint as a *requirement*.
5. **Reviews are layer-5 Communication.** Grok, opus, octopus and gpt all say so
   in their own frontmatter. They authorize nothing. `docs/execution/` is the
   board; `.draft/` is lock, not product.
6. **When a corpus number and the tree disagree, cite both with their pins.**
   80,618 relations today vs 77,610 at `5243866b` is not an error to hide — it
   is evidence the index is live.
