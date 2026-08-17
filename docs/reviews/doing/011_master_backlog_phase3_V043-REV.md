# 011 — Phase 3 Master Backlog (Waves W6–W9 / Sprints 7–10)

**Status:** LIVING execution tracker. NON-NORMATIVE — owns *what is being worked on*, never a
contract. Where this file and a v4 owner disagree, the owner wins (`PR-3`). Merge gating is owned
by the Active MVP Contract (`ADR-0046`, `GTS-13C` Ch. 15).
**Date opened:** 2026-08-16 · **Branch/HEAD at open:** `sprints7-8/integration` @ `0238b1a`
**Authorised by:** `DECISION-0005`. Gate status fixed by `ADR-0064`.
**Supersedes:** `docs/scrum/sprints/sprint6B/todo_list_sprint6B.md` as the living tracker (that file
is now a closed Sprint 6B record).

---

## 1. How to read and update this file

**Hierarchy:** `Phase → Wave → Sprint → Task → Sub-task`. One wave per sprint in Phase 3.

**Status vocabulary:**

| Status | Meaning |
|---|---|
| `[DONE]` | Verified complete: named file/test exists and passes |
| `[CLAIMED]` | Lane reports DoD met; **TL has not verified**; not sprint-closed |
| `[IN_PROGRESS]` | Started, has an owner |
| `[TODO]` | Specified, bounded, ready |
| `[BLOCKED]` | Precondition unmet — the blocker is named |
| `[REJECTED]` | Specified but **must not be built**, with the rule it would violate |

**Task id:** `S<sprint>-<lane>-<nn>` · lanes `A` control plane · `B` workload & evidence ·
`C` measurement & lab · `J` joint/leads.

**Rules.** A row is `[DONE]` only when its DoD command passes — not when the code exists. Every
row cites a source (`T-ref`, `D-ref`, report §, or `009` finding). Every PR cites at least one
`req_id` from the Active MVP Contract. **A row that cannot be phrased as a testable statement is
not a backlog row — it is a ticket.**

---

## 2. Current state at open

| Metric | Value |
|---|---|
| Test baseline | **507 tests · 3 failures · 17 errors · 2 skipped** |
| Of which pre-existing | 2 failures + 15 errors (alias layer + node-absent readers) |
| Of which caused by the `docs/agile`→`docs/scrum` restructure | **+1 failure, +2 errors** — `test_repo_root_from_this_file`, `test_three_oracles_are_digest_bound`, `test_registry_does_not_claim_runs_were_completed` |
| TCB | 1,307 / 1,438 LOC — pass |
| `scan_secrets.py` | PASS |
| `scan_secrets.py --all-refs` | **FAIL** — reachable `.env` blob, 21 `refs/original` |
| Gate status (`ADR-0064`) | Q1 partial+regressed · Q2 not demonstrated · Q3 not met · Q4 not met |

**Field note — SUPERSEDED (2026-08-16, morning):** *Sprint 7 is not closed. A: `S7-A-07` only… B: S8-B rows `[CLAIMED]`… C: `S7-C-01` `[IN_PROGRESS]`… Joint J-04…J-08 `[TODO]`.* Retained for audit; the statuses it cites no longer match the tree.

**Field note — SPRINT 7 ENGINEERING CLOSED (2026-08-16, TL + PL verification run):**
Branch `sprints7-8/integration` @ `248be91`. Verified on disk and by command, not by lane report.

| Metric | Value at close |
|---|---|
| Suite | **539 tests · 0 failures · 14 errors · 2 skipped** |
| All 14 errors | `ReaderUnavailable: node is required` — **the exact class the S7 exit gate admits**; 0 other errors |
| `check_boundaries.py` | PASS, 154 source files |
| `run_broken_tests.py` | PASS, **38** broken counterparts observed failing |
| `check_tcb_budget.py` | PASS, 1,315 / 1,438 |
| `grep -rn "runtime.loops\|EpisodeCoordinator" vanguard/` | **empty** |
| `scan_secrets.py` (tree) | **PASS** (was FAIL — see D3) |
| `scan_secrets.py --all-refs` | **still FAIL** — reachable `.env` blob, 21 `refs/original`. `S7-J-04`, carried, **does not block S8/S9** |
| All 12 CI gates | **PASS** (3 were failing on files deleted by `0a9ac8b` — see D1) |

**Lane verdicts.** A: `S7-A-01…A-07` **`[DONE]`**, verified — `runtime/loops/` and `coordination.py`
gone, five rules live in the boundary table with planted counterparts failing. B: `S7-B-01…B-05`
**`[DONE]`**, verified — 13 loader tests, 3 bench tests, metamorphic green. C: `S7-C-01…C-05`
**`[DONE]`**, verified — four runners gone, `guard.py` present, `RETRACTION.md` present, `top: []`
held, no adapter import in `benchmarkings/` (the single `OpenRouterModel` grep hit is a docstring
compliance statement in `zero_hint_v1/run_live_agent.py:7`, not an import).

**Four defects found at close that no lane reported** — D1 `S7-CLEAN-001` (`0a9ac8b`) deleted the
Active MVP Contract and the T0 archaeology traces while three CI gates still referenced them;
D2 the baseline manifest was sealed mid-sprint (`6ed94fe`) then invalidated by `S7-A-03`
(`c5ff05f`) rewriting a sealed file; D3 the `pem-private-key` rule fired on security prose;
D4 `test_lam_models.py` asserted the *retired* band vocabulary, i.e. it asserted that the `top`
spend control does not exist. All four repaired at close. Full evidence with commands and outputs:
**`docs/scrum/sprints/sprint07/evidence/s7-close-receipt.md`**.

**Integration branch — one name.** `sprints7-8/integration` is canonical and carries Sprint 8.
`sprint7/integration` held **zero** unique commits (strict ancestor) and is **deleted** local and
`origin`. Every S8/S9 kit cites the canonical name; no doc may reintroduce `sprint07/integration`.

---

## 3. Wave / Sprint map

| Wave | Sprint | Theme | Closes | Net LOC |
|---|---|---|---|---|
| **W6** | **S7** | Subtraction & boundary restoration | **Q1** | **−1,530** |
| **W7** | **S8** | Recursion, resume, load-bearing manifests, ACI | Q1, Q2 | +~800 |
| **W8** | **S9** | The instrument: A/A floor, splits, oracles, dogfood | **Q3** | +~900 |
| **W9** | **S10** | Generality: domain de-capture, TableWorld, the gate | **Q4** | +~700 |
| W10+ | — | Phase 4 / V5 (`010`), behind `O-01`/`O-03` triggers | — | — |

---

## 4. WAVE 6 / SPRINT 7 — Subtraction & Boundary Restoration

**Theme:** make the tree's behaviour match the tree's description. **No features.**
**Exit gate:** every effect in every executable path traverses `Kernel.dispatch`, proven by an
architecture test that fails against a planted broken counterpart.

### 4.1 Lane A — Control Plane

| ID | Status | Task | Sub-tasks | DoD / verification | Target files | Requires | Source |
|---|---|---|---|---|---|---|---|
| `S7-A-01` | `[DONE]` | **Lattice-completeness CI rule** | 1 Add rule: any top-level package under `vanguard/packages/` not named in `VG-03 §4` `LT-1..LT-8` fails the build · 2 Plant broken counterpart · 3 Wire into CI | `check_boundaries.py` exits non-zero on a planted rogue package; `test/broken/` counterpart fails | `tools/check_boundaries.py` (**already AST-based**, table at :32 — extend the table, do not build a checker) | — | `003` A2, `007 §8` |
| `S7-A-02` | `[DONE]` | **No-subprocess-outside-sandbox rule** | 1 Rule: `subprocess` importable only from `adapters/sandbox/` · 2 Broken counterpart · 3 CI | Planted `subprocess` import in `agency/` fails the build | `tools/check_boundaries.py` | — | `003` A3, `006` S3 |
| `S7-A-03` | `[DONE]` | **No-evaluator-import rule** | 1 Rule: no path from `agency/**` or `runtime/**` to `adapters/evaluators/**` · 2 Broken counterpart | Planted import fails; `A-05` provable statically | `tools/check_boundaries.py` | — | `003` A3, `T10.4` |
| `S7-A-04` | `[DONE]` | **DELETE `runtime/loops/`** | 1 Delete package + `test/runtime/test_meta_loop.py` · 2 Confirm no importers · 3 Record salvage mapping in the PR body | `grep -rn "runtime.loops"` empty; suite no worse than baseline | `vanguard/packages/runtime/loops/` | `S7-A-02`, `S7-A-03` | `001 §3.1`, `007` D1–D2 |
| `S7-A-05` | `[DONE]` | **DELETE `runtime/coordination.py`** | 1 Delete · 2 Remove `root.py:712-723` wiring and the `... or 100` at `:793` · 3 Convert `test_coordination.py` into a ledger-projection test | No second budget store; depth derives from ledger events | `runtime/coordination.py`, `runtime/root.py`, `runtime/ledger/projections.py` | `S7-A-04` | `003 §4`, `007` D3 |
| `S7-A-06` | `[DONE]` | **Remove hardcoded composition values** | 1 `/usr/bin/bwrap` → `shutil.which` probe with a named remedy · 2 `approval_required_above="low"` → TODO marker for `S8-B-04` · 3 `Reservation(100,1000)` → from budget policy | Composition succeeds on a host with `bwrap` elsewhere on PATH; no absolute-path literal remains | `runtime/root.py:659,693,775` | — | `003 §5.1`, `007` R1–R4 |
| `S7-A-07` | `[DONE]` | **Repair restructure breakage** | 1 `tools/repo_paths.py`: `docs/agile` → `docs/scrum` · 2 Fix `test_repo_paths.py`, `test_oracle_registry.py`, `test/contracts/__init__.py` | The 3 restructure-caused failures went green. **2F/15E baseline later voided** by in-flight C/B + shared dirty tree — do not cite as S7 exit. | `tools/repo_paths.py`, 3 test files | — | `011 §2` |

### 4.2 Lane B — Workload & Evidence

| ID | Status | Task | Sub-tasks | DoD / verification | Target files | Requires | Source |
|---|---|---|---|---|---|---|---|
| `S7-B-01` | `[DONE]` | **Canonical alias shape + fail-closed validation** | 1 Pick the flat `{"alias":"verb"}` form (4 of 5 packs use it) · 2 Migrate the tests, not the data · 3 At composition assert every alias target ∈ declared verbs · 4 Assert every tool schema `name` ∈ aliases ∪ verbs · 5 Broken counterpart | 3 red tests go green; a planted mismatched alias raises `CompositionError`; **`to_canonical` no longer falls back to identity** | `agency/manifests/loader.py:41-71`, `*/aliases.json`, `test/agency/test_manifest_loader.py` | — | `005` H1–H2, `N-17` |
| `S7-B-02` | `[DONE]` | **"An unread component is a composition error"** | 1 `compose()` asserts every `components` entry has a registered consumer · 2 Broken counterpart with an orphan component | A manifest declaring an unconsumed component fails composition. **This is the rule that kills `FT-10` structurally** | `runtime/root.py` `compose`, `domain/artifacts/manifest.py` | `S7-B-01` | `005` H3 |
| `S7-B-03` | `[DONE]` | **Metamorphic policy-digest test** | 1 Recompose with a mutated `context_policy` · 2 Assert ≥1 observable differs | Lane B reports green via `S8-B-02` — **TL verify**; originally expected FAIL until Sprint 8 | `test/agency/test_manifest_metamorphic.py` (new) | `S7-B-02` | `005` H4 |
| `S7-B-04` | `[DONE]` | **Emit `gene_digests` into results** | 1 `gene_digests` **already exists** at `root.py:606-609` — emit into `RunResult` and `result.json` `K_compat` | Two composes of the same pack give identical digests; a prompt byte change moves exactly one | `runtime/root.py`, `benchmarkings/zero_hint_v1/run_live_agent.py` | — | `005` H0, `009 §5` |
| `S7-B-05` | `[DONE]` | **Fix `test_bench` alias `KeyError`** | 1 `vg-shell-only` undeletability guard currently errors, so the `L-15` protection is not running | `test/lab/test_bench.py` green; undeletable flag actually asserted | `test/lab/test_bench.py` | `S7-B-01` | `005 §5.2` |

### 4.3 Lane C — Measurement & Lab

| ID | Status | Task | Sub-tasks | DoD / verification | Target files | Requires | Source |
|---|---|---|---|---|---|---|---|
| `S7-C-01` | `[DONE]` | **`benchmarkings/` dependency gate** | 1 Rule: `benchmarkings/**` may import `runtime.root` + `ports` only · 2 Broken counterpart | Full-tree boundary check passes after bypass cleanup; planted adapter import fails. | `tools/check_boundaries.py` | — | `002` M1, `003` A1 |
| `S7-C-02` | `[DONE]` | **`benchmarkings/guard.py` refusal conditions** | 1 `pre_passed` on a repair task → `inconclusive:precondition_satisfied` · 2 zero effects + post-pass → `inconclusive:no_intervention` · 3 zero tokens → `inconclusive:model_not_invoked` · 4 provider error → `inconclusive:instrument_error`, excluded from **both** numerator and denominator · 5 evaluator absent → `inconclusive:no_verdict` · 6 containment absent → publication blocked · 7 broken counterpart per condition | Six planted degenerate runs are refused, not scored. | `benchmarkings/guard.py` (new), `test/broken/` | — | `002` M2, `009 §3.4` |
| `S7-C-03` | `[DONE]` | **DELETE the four bypassing runners** | 1 `swe_pro_tiers/runner.py` · 2 `swe_pro_tiers/run_matrix_evaluation.py` · 3 `run_agentic_live_challenge.py` · 4 `run_live_proof.py` | `grep -rn "OpenRouterModel" benchmarkings/` returns only the promoted runner | `benchmarkings/**` | `S7-C-01` | `007` D4–D7 |
| `S7-C-04` | `[DONE]` | **Retraction sweep** | 1 `matrix_results_*.json` → `benchmarkings/_retracted/` + `RETRACTION.md` naming the defect, date and preventing rule · 2 Non-degenerate rows → `_external_model_probes/` relabelled as model probes · 3 Apply the 9-label regime | Retracted and external-probe artifacts are separated, labelled, and retain stated cause/limitation. | `benchmarkings/**` | `S7-C-03` | `002` M3, `002 §2.1` |
| `S7-C-05` | `[DONE]` | **Promote the honest runner** | 1 `zero_hint_v1/run_live_agent.py` is the sole benchmark entrypoint · 2 Label `lab-execute-harness` · 3 Record `labDepartures` | Sole retained production runner calls `Runtime.execute_harness` and records guard, label, and departures. | `benchmarkings/zero_hint_v1/` | `S7-C-03` | `002` M4 |
| `S7-C-06` | `[DONE]` | **`models.json` `top` fail-closed** | 1 Set `top: []` · 2 `models_for_band("top")` raises until the Project Lead names ids in the Decision Register · 3 Reconcile the drifted `tier1_local…tier6_cloud` bands against `free/medium/high/top` | Canonical bands are `free/medium/high/top`; `top` raises with the PL message. | `tools/002_LLM_API_MOCK/models.json`, `models.py` | — | `D-13`, `009 §3.1` |
| `S7-C-07` | `[DONE]` | **LAM competitor persona removed** | Verified during `009` verification: `simulate.py:23-27` `SYSTEM` reads the pack's own `system-prompt.txt` with a neutral fallback | No competitor persona in the gym | `tools/002_LLM_API_MOCK/simulate.py` | — | `009 §5a` |

### 4.4 Joint / Leads

| ID | Status | Task | Sub-tasks | DoD | Source |
|---|---|---|---|---|---|
| `S7-J-01` | `[DONE]` | **`ADR-0063`** ratify Python, reverse `ADR-0001` | Appended to `VG-09 §12`; `VG-02 §9` stack table corrected | Register + charter updated | `006 §1`, `009 §5` |
| `S7-J-02` | `[DONE]` | **`ADR-0064`** record gate status | Q1 partial+regressed, Q2/Q3/Q4 not met; per-gate reversal named | `VG-09 §12` | `ADR-0064` |
| `S7-J-03` | `[DONE]` | **`ADR-0065`** adopt D-01…D-15 as binding | Locked decisions moved from review prose into the register | `VG-09 §12` | `009 §3.4` |
| `S7-J-04` | `[TODO]` | **`SEC-01` remediation** | 1 **Rotate at the provider first** · 2 Owner-authorised history rewrite across every affected ref · 3 Remove `refs/original` (21) · 4 Force-update remote; invalidate stale clones · 5 Verify `--all-refs` **and** a clean-clone scan · 6 **CI runs `--all-refs`, not the lenient default** | `scan_secrets.py --all-refs` PASSes. **Never place the secret value in a ticket, log or receipt** | `DECISION-0006`, `009 §3.1`, `007 §6` |
| `S7-J-05` | `[TODO]` | **Add `LICENSE`** | Apache-2.0 text matching `pyproject.toml` metadata | `ls LICENSE` succeeds | `009 §3.1` |
| `S7-J-06` | `[TODO]` | **Promote the measurement science into `VG-07`** | C1–C12 · 9 evidence labels · splits `M-19`/`M-20` · outcome algebra · 12-layer FUAA · three evidence levels | `VG-07` amended; `VG-00 §6` index updated | `009 §3.4` |
| `S7-J-08` | `[TODO]` | **`ADR-0066`: MCP adapter rules, pre-recorded** | An MCP tool is an `EffectAdapter`, never a second dispatch path · its tool list is untrusted content, discovered between episodes under signed allow-listing · egress is a `privileged` effect with a `host` selector | Rules recorded before any MCP code exists | `006 §4.4` |
| `S7-J-07` | `[TODO]` | **Review WIP protocol** | Cap `doing/` at 8 documents; `todo/` abolished (done); closure header required on archive | Protocol recorded in `VG-00 §11` | `007 §5.2` |

### 4.5 Sprint 7 exit gate

- [ ] Baseline returns to **2 failures / 15 errors** (`S7-A-07`), then the 3 alias failures go green (`S7-B-01`, `S7-B-05`) → **0 failures**, errors only from node-absent readers
- [ ] Architecture tests prove: no second loop · no `subprocess` outside `adapters/sandbox/` · no evaluator import from `agency`/`runtime` · no package outside `LT-1..LT-8` · `benchmarkings/` cannot import adapters
- [ ] **Each new rule fails against its planted broken counterpart** (`A-10`)
- [ ] A planted degenerate run is refused by the scorer
- [ ] Composition fails on an undeclared alias target **and** on an unread component
- [ ] `scan_secrets.py --all-refs` PASSes
- [ ] `check_tcb_budget.py` still passes; net LOC ≈ **−1,530**

---

## 5. WAVE 7 / SPRINT 8 — Recursion, Resume & Load-Bearing Manifests

**Exit test:** a parent episode spawns a child under an attenuated grant and a child lease; the
child's exploration never enters the parent's context; the whole run reconstructs from the ledger.

### 5.1 Lane A — Control Plane

| ID | Status | Task | DoD | Source |
|---|---|---|---|---|
| `S8-A-01` | `[DONE]` | **Decompose `execute_harness`** → `compose / HarnessSession / run`; **one `Kernel` per run** (three are built today); ports injected | `HarnessSession` unit-testable without a live model; `_WitnessKernel` deleted | `003` A7, `007` D9 |
| `S8-A-02` | `[IN_PROGRESS]` | **Suspend/resume from the ledger** — approval suspension becomes terminal-with-continuation inside the engine; re-entry reduces the ledger for that `episodeId`; delete the segment loop | An episode suspended and resumed reconstructs an identical `state_digest` **from the ledger alone**; `max_turns` and no-progress detection survive an approval | `003` A9, `T3.6` |
| `S8-A-03` | `[DONE]` | **`RandomPort` + determinism-complete `ClockPort`** | Replay is byte-identical; `Recording` can drive counterfactual re-execution | `004` G3, `003` A12 |
| `S8-A-04` | `[DONE]` | **`RecordCorrection` calls `parse_wire("CorrectionRecord")`** | Invalid `style` + `scope: general` is **rejected**; valid record round-trips; no promotion path | `009 §3.1`, `D-07` |
| `S8-A-05` | `[DONE]` | **`Claim` as a `domain/` type** — non-empty `invalidationConditions` at parse; ≥1 **automatic** condition (substrate-digest change); `support_count`/`last_corroborated_at`/`protection_class` recorded-not-consumed | Empty invalidation array fails at parse; a substrate change marks the claim stale **without human review** (`C-12`) | `004` G1–G2 |

### 5.2 Lane B — Workload & Evidence

**TL audit complete (2026-08-16). Verdict: ACCEPTED as the Sprint 8 starting point — not sent back.**
Lane B put real, tested code on the tree ahead of the sprint. `ADR-0060` holds: `agency/episode/`
introduces **no domain vocabulary** (`spawn` speaks scope, lease, depth, causation — no `file`,
`repo`, `patch`, `test`). TCB unchanged at 1,315 — recursion did not grow the kernel. Row statuses
below are the TL's, not the lane's, and were set by reading the tree.

**One material gap, and it is in the centre row.** `S8-B-01`'s DoD names three property tests. One
exists. The other two — *"budget conserved two levels deep"* and *"child overrun debits the
parent"* — are absent, **and the mechanism they would test is not wired**: `spawn` builds the child
`EpisodeEngine` on the shared `Kernel`, but no `parent_lease` is ever set on an effect request
(`engine.py:196`), so the `Governor` lease tree is never built. Shared ceilings give conservation
*incidentally*; the DoD asks for it *structurally*, and `Governor.reserve(..., parent_lease_id=…)`
already implements `F-13` ("a closed parent cannot fund a child") waiting to be called.
**This is a finish, not a rewrite — it is Lane B's first Sprint 8 task.** `spawn` is otherwise sound
and Lane A must **not** delete or relocate it while decomposing `root.py` (`S8-A-01`).

| ID | Status | Task | DoD | Source |
|---|---|---|---|---|
| `S8-B-01` | `[CLAIMED]` | **`EpisodeEngine.spawn`** — child scope ⊆ parent (reuse `kernel/attenuation.py`), child lease on remainder (reuse `Governor`), `depth` a real budget dimension, child events carry `causationId`, return is text/payload **never a handle**, workspace destroyed in `finally` | **Attenuation/depth/causation/typed-return/workspace-finally: VERIFIED** (7 tests, `test/agency/test_episode_spawn.py`). **Budget half NOT wired** — no `parent_lease` on any effect request; the two budget property tests are absent. Finish = `S8-B-01a` | `003 §3.4`, `T4.4`, `T4.10` |
| `S8-B-02` | `[DONE]` | **`CompactionStrategy` protocol + registry** — register `result_eviction`, `recency_window`; selected by `context_policy`; frozen at composition | `S7-B-03` metamorphic test goes **green**; changing `context_policy` changes an observable | `004` G5, `005` H5 |
| `S8-B-03` | `[DONE]` | **`ModelRouter` protocol + registry** — wire the existing unwired `adapters/models/routing.py`; selected by `routing_policy` | Changing `routing_policy` changes the model selected | `005` H6, `010` §4 |
| `S8-B-04` | `[TODO]` | **`approval_policy` manifest component** — replaces the hardcoded `"low"` threshold | **NOT DONE.** Registered in `manifests/loader.py:36`, but `root.py:740` still carries `TODO(S8-B-04)` and the literal, and no test asserts the behaviour. Two packs with different approval policies behave differently | `005` H7, `S7-A-06` |
| `S8-B-05` | `[DONE]` | **Operator context isolation** — child gets a fresh compiler prefix; only the return enters the parent's L5 | Test: a child's intermediate turns are absent from the parent's compiled context | `VG-03 §10.3`, `003 §3.4` |
| `S8-B-06` | `[DONE]` | **ACI-1 paginated `fs.read`** (100 lines + offset) | Adapter + schema + prompt convention; large file no longer dumps | `010 §2` |
| `S8-B-07` | `[DONE]` | **ACI-2 succinct `fs.search`** (file hits first, capped snippets) | Search returns a file list, not a dump | `010 §2` |
| `S8-B-08` | `[DONE]` | **ACI-3 empty-output acknowledgement** on `proc.exec` | Silent command returns explicit text, not `""` | `010 §2` |
| `S8-B-09` | `[DONE]` | **ACI-4 lint-on-patch as an observation receipt** | Syntax failure is a **receipt**, never a verdict — `A-05` preserved | `010 §2` |
| `S8-B-10` | `[DONE]` | **ACI-6 `maxTurns` from `budget_policy`** | Engine reads the frozen policy; a 32-turn pack runs 32 turns | `010 §2`, `D-12` |

### 5.3 Lane C — Measurement & Lab

| ID | Status | Task | DoD | Source |
|---|---|---|---|---|
| `S8-C-01` | `[TODO]` | **Depth as a ledger projection** — replaces the deleted SQLite table; `Atom/Molecule/Polymer/Cell/Body` are labels a projection applies, **never classes** | Depth query answered from ledger events only | `003 §4`, `GTS-13C §4.3` |
| `S8-C-02` | `[TODO]` | **Cache-hit-rate metric over a fixed replay** — the largest unmeasured cost lever | Prefix-stability is a monitored CI metric | `006` S5, `004` C6, `010 §3` |
| `S8-C-03` | `[TODO]` | **V5-L prefix-miss attribution** — record *why* the prefix broke (`system`/`tools`/`compact`/`snip`) | Every model call carries a miss reason or a hit | `010 §4.3` |
| `S8-C-04` | `[TODO]` | **LAM schema `t0-`/`t6-` regex reconciliation** | Corpus and validator agree; no waiver needed | `009`, LAM plan §8.2 |

### 5.4 Sprint 8 exit gate

- [ ] Property: child grant strictly narrows verb, selector, constraints, expiry, uses, budget
- [ ] Property: budget conserved across a two-level spawn
- [ ] Test: child turns absent from the parent's compiled context
- [ ] Test: suspend→resume reconstructs identical `state_digest` **from the ledger alone**
- [ ] Test: `max_turns` is a hard bound **across** an approval boundary
- [ ] Metamorphic: `context_policy` and `routing_policy` digests each change an observable
- [ ] `Claim` with empty invalidation fails at parse; substrate change auto-stales
- [ ] Cache-hit rate recorded as a CI metric


### 5.5 Sprint 8 — Joint track

| ID | Status | Task | DoD | Source |
|---|---|---|---|---|
| `S8-J-01` | `[TODO]` | **`VG-04` wire amendment for `Claim`** — optional reader-profile fields (`support_count`, `last_corroborated_at`, `protection_class`); golden vectors; migration rehearsal (`T1.15`) | Old readers survive a minor bump; format locked (`L-1`) | `004` G1–G2 |
| `S8-J-02` | `[TODO]` | **Confirm `ADR-0060` held through recursion** — S8 is the only sprint editing `agency/episode/` | Zero domain vocabulary introduced; TCB still under budget | `ADR-0060` |
| `S8-J-03` | `[TODO]` | **Q1/Q2 evidence review** — preregister the three dogfood bugs now, so tasks cannot be chosen after seeing the harness behave | `ADR-0064` rows updated only where evidence supports | `GTS-13C` Ch. 10 |

---

## 6. WAVE 8 / SPRINT 9 — The Instrument (Q3)

**Exit test:** an A/A noise floor exists per task class against `vg-shell-only`, and the runner
**refuses to report** when the design is degenerate.

> **Reassignment.** The previous Sprint 9 was "Meta-Harness Loop & Self-Correction". That work is
> `[REJECTED]` (§8). Sprint 9 becomes what `ADR-0057` said S7–S9 were for: **Q3**.

| ID | Status | Lane | Task | DoD | Source |
|---|---|---|---|---|---|
| `S9-C-01` | `[TODO]` | C | **Wire the `M-18` instrument tuple** — `tools/telemetry/tuple.py` is **implemented and unwired**; emit into every `result.json`; **refuse any lift computation without tuple equality**; fail closed on placeholder digests | No lift is computable across differing `K_compat` | `009 §3.1` |
| `S9-C-02` | `[TODO]` | C | **Pre-registration artifact** — hypotheses, primary metric, alpha, correction, manifest digest, stopping rule, hashed **before any arm runs**; fix the `preregistered_not_executed` status drift | CI rejects an arm run without a prior hash | `002` M5, `T8.4` |
| `S9-C-03` | `[TODO]` | C | **A/A runner** — identical manifest vs itself, N repeats, ≥3 task classes, against `vg-shell-only`; **refuses when any arm is degenerate or the floor is zero** | A per-class floor number with a CI; refuses on a planted degenerate config | `002` M6, `T8.1` |
| `S9-C-04` | `[TODO]` | C | **Statistics module** — McNemar exact (paired binary), paired bootstrap (cost/latency), survival (timeouts/censoring). **No p-values at n<20** | Paired comparison reports an effect with an interval | `002` M7, `T8.3` |
| `S9-C-05` | `[TODO]` | C | **Splits + touch ledger** — `DEV/HOLDOUT/SEALED/LIVE/DEPLOYMENT`, one-way contamination, per-instance membership check | Using HOLDOUT to tune a prompt burns it to DEV, recorded | `002` M8, `M-19`, `M-20` |
| `S9-C-06` | `[TODO]` | C | **Oracle hardening** — `bug-001` is **already** a property oracle (`009 §5a`). Remaining: audit the other suites for source-substring assertions; add mutation checks and isomorphic perturbation per task class | A comment-only patch fails every suite; a known-wrong patch is rejected by the mutation oracle | `002` M9 |
| `S9-C-07` | `[TODO]` | C | **Seeded-sabotage suite** — plant proxy-exploiting candidates; confirm rejection | A gate never proven able to fail is not a gate | `002` M10, `T8.8` |
| `S9-B-01` | `[TODO]` | B | **Real reconstructions** — rebuild `claude-shaped`/`opencode-shaped`/`swe-mini` so they differ on ≥3 of the ten dimensions, now that compaction/routing/approval are real. `REFERENCE.md` per pack citing public sources | `lab harness diff` shows more than a prompt delta | `005` H9, `D-09` |
| `S9-B-02` | `[TODO]` | B | **`vg harness build \| run \| diff \| bench`** — as `lab/` entrypoint first (`D-10`) | Two packs compose; diff JSON stable; labelled `lab` | `005` H10, `T7.5` |
| `S9-J-01` | `[TODO]` | J | **Q2 dogfood ×3** — three real bugs, interactive, **no hand-patching mid-run**, corrections captured with reason codes; record the honest *"would you reach for it again?"* — **including if it is no** | Three runs + a signed judgement | `GTS-13C` Ch. 10 Q2 |

**Sprint 9 exit gate:** a per-class A/A floor exists with N and MDE derived from it · the runner
refuses a planted degenerate config · one pre-registered paired comparison reports an effect with
an interval · per-arm instrument-error rate reported · a seeded proxy-exploiter is rejected ·
three dogfood runs recorded · reconstructions demonstrably differ.

> **Expect the floor to be large.** The field measures 9.5–20 points of harness-only variance on
> fixed models. If the floor swallows the deltas we intended to claim, **that is the finding** —
> `RSK-06` requires acting on it rather than raising N until something is significant.


### 6.1 Sprint 9 — support and Joint rows

| ID | Status | Lane | Task | DoD | Source |
|---|---|---|---|---|---|
| `S9-A-01` | `[TODO]` | A | Surface instrument fields on `RunResult`: `gene_digests`, composition digest, per-arm instrument-error reason, integer turn/token/cost | The instrument reads them without touching internals | `011 §6` |
| `S9-A-02` | `[TODO]` | A | **Integer telemetry discipline** — integer micros, integer tokens, integer USD micros. No floats as truth | No float appears as an authoritative metric | `S6B-MD-009` |
| `S9-A-03` | `[TODO]` | A | `Recording` sufficiency for replaying a benchmarked run; record any gap against Phase 4 `V5-A` | Gap named or closed | `010 §4.3` |
| `S9-A-04` | `[TODO]` | A | Ledger query support for the paired runner | Lane C unblocked | `011 §6` |
| `S9-J-02` | `[TODO]` | J | **Pre-registration sign-off** — countersign every hash before its arms run; family declared before arms; Holm–Bonferroni; **optional stopping forbidden** | No arm runs without a countersigned prior hash | `T8.4`, `L-08` |
| `S9-J-03` | `[TODO]` | J | **Spend authorisation** — cloud only after local calibration shows `patch.apply`; `top` stays `[]` unless named; 10 calls → a ledger line | No unauthorised paid call | `D-13`, `002 §9` |
| `S9-J-04` | `[TODO]` | J | **Q3 evidence review** — floor? paired comparison with interval? gap number or a dated statement of why not? | `ADR-0064` Q2/Q3 rows updated only where evidence supports | `GTS-13C` Ch. 10 |

---

## 7. WAVE 9 / SPRINT 10 — Generality & The MVP Gate (Q4)

| ID | Status | Lane | Task | DoD | Source |
|---|---|---|---|---|---|
| `S10-A-01` | `[TODO]` | A | **Domain de-capture** — move verb/args/selector binding out of `adapters/models/invocation.py` into the manifest capability row (`args_schema` + `selector_binding`) | `invocation.py` holds **zero** domain knowledge; unknown alias fails at composition | `003` A11, `005` H8 |
| `S10-A-02` | `[TODO]` | A | **`proc.test` binding** — present in `KNOWN_TOOLS`, absent from `DEFAULT_BINDINGS`. Prefer keeping tests as allowlisted `proc.exec` and deleting the orphan | No verb in `KNOWN_TOOLS` lacks a binding | `009 §3.1` |
| `S10-B-01` | `[TODO]` | B | **TableWorld** — versioned tables; `select/derive/update/validate`; constraints over sums, uniqueness, ranges; **no version control, no shell, no paths as a domain concept**; deterministic evaluator over invariants | Four `VG-08` Increment-C stories pass through the standard `EnvironmentAdapter` | `T9.1–T9.3`, `VG-03 §7.3` |
| `S10-B-02` | `[TODO]` | B | **Core-change detector** — CI counts lines changed in `kernel/**`, `agency/episode/**`, `domain/wire/**` to add a domain; reconstruction PRs touching them **fail** | The count is the `C-10` measurement and is **published whatever it is** | `T9.3`, `D-15`, LAM plan §7.1 |
| `S10-B-03` | `[TODO]` | B | **`structured_consolidate`** emitting `StructuredRecord` incl. `deadEnds`; consolidation quality measured by transcript-replacement replay | *"That is a number, not an opinion"* | `004` G6, `VG-03 §10.4` |
| `S10-B-04` | `[TODO]` | B | **`regroundPolicy`** as an **authorised observation effect**, not a side channel | Re-grounding traverses `Kernel.dispatch` like any other effect | `004` G7, `VG-03 §6.1` |
| `S10-A-03` | `[TODO]` | A | **`BlobStorePort` + `IndexPort`** | Two implementations each (fake + real) | `003` A12, `GTS-13C §5.2` |
| `S10-A-04` | `[TODO]` | A | **`vg why <artifact>`** — what evidence activated it, what it predicts, what would demote it | *"If the operator cannot interrogate governance, they will bypass it"* | `T6.5`, `005 §7` |
| `S10-J-01` | `[TODO]` | J | **The four-question gate review** with named evidence per question | `ADR-0064` reversal conditions evaluated one by one | `GTS-13C` Ch. 10 |

**Sprint 10 exit gate — the actual MVP gate:**

| # | Question | Required evidence |
|---|---|---|
| **Q1** | Boundary real? | Red team reaches neither control plane, evaluator, nor secrets. Every must-fail test fails against its counterpart. Kill/restart preserves known vs uncertain. **No second execution path exists, proven by architecture test** |
| **Q2** | Useful? | Three real bugs fixed interactively without hand-patching; the recorded answer to *"would you reach for it again?"* |
| **Q3** | Measurable? | A/A floor per task class vs `vg-shell-only`; one paired comparison; a verifier–deployment gap number **or** a written statement of why it is not yet computable, with a date |
| **Q4** | General? | TableWorld added, and **the measured line count changed in `kernel/` + `agency/episode/` is published** |

> **A non-zero Q4 count is a finding, not a failure.** `VG-03 §7.3` says building TableWorld early
> exists to falsify generality *"early, cheaply, and therefore usefully."* Only a **hidden**
> non-zero count is a failure.


### 7.1 Sprint 10 — measurement and Joint rows

| ID | Status | Lane | Task | DoD | Source |
|---|---|---|---|---|---|
| `S10-C-01` | `[TODO]` | C | **Instrument works unchanged against a second domain** — A/A runner, splits, statistics. A domain special case in the instrument is a finding symmetric to `C-10`. Per-domain floors are separate numbers and must not be pooled | TableWorld floor computed with no instrument special case | `011 §7` |
| `S10-C-02` | `[TODO]` | C | **Verifier–deployment gap dashboard + automatic freeze** — build the freeze now, while there is nothing to freeze | Widening past threshold freezes promotions (logging is acceptable while autonomous promotion does not exist) | `T8.7`, `002` M11 |
| `S10-C-03` | `[TODO]` | C | **Gate evidence pack** — commands and outputs, not prose; **includes the negative results** | Four questions answered with evidence paths | `VG-02 §11.9` |
| `S10-J-02` | `[TODO]` | J | **Reverse `ADR-0064` per gate, honestly** — a gate whose evidence does not support reversal stays unreversed | Each gate evaluated individually | `ADR-0064` |
| `S10-J-03` | `[TODO]` | J | **Claim discipline at v0.4.3** — publish only what is proven; no AGI / SOTA / autonomous-evolution language | README and any release text match the evidence | `NC-01`, `002 §5` |
| `S10-J-04` | `[TODO]` | J | **Phase 4 authorisation** — evaluate the `O-01` and `O-03` triggers; order V5 work from `010 §4`, starting with **V5-A exact corpus** | Triggers evaluated explicitly; unfired triggers keep their work unbuilt | `010`, `GTS-13C` Ch. 3 |

---

## 8. Rejected — specified but must not be built

| ID | Item | Why rejected | Salvage |
|---|---|---|---|
| `S9-OLD-01` | **`MetaLoopEngine` / `runtime/loops/meta_loop.py`** | Executes `subprocess.run` on the host with no grant (`A-03`, `N-06`); **runs the evaluator inside the loop and branches on the verdict** (`A-05`, `ADR-0004`, `VG-03 §3`); emits zero events (`A-07`); `NameError` on the default path. Marking it `[TODO]` would schedule rebuilding the thing that breaks Q1 | Compaction → `S8-B-02` · failure-driven retry → **the loop itself** (`VG-03 §2.2`: *"repair does not exist"*) · tier escalation → `S8-B-03` |
| `S9-OLD-02` | `Atom→Molecule→Cell→Body→Biome` **class hierarchy** | `GTS-13C §4.3`: *"Build the classes and you have hand-authored the hierarchy you claimed would emerge."* | Depth labels as a ledger **projection** → `S8-C-01` |
| `S9-OLD-03` | `vanguard/packages/manifests/builder.py`, `vanguard/cli/`, `vanguard/tui/` | Outside `LT-1..LT-8`; inverts the daemon boundary | Manifests stay in `agency/manifests`; clients stay in `clients/` |
| `S9-OLD-04` | Sprint-10 gate = "100% tests pass + tag git" | `GTS-13C` Ch. 10: *"Tickets merged, CI green, and a demo that worked once do not close it."* | §7 four-question gate |
| — | Parallel tool calls / independence groups | `D-02`; no independence-group type exists; `C-04` unmeasurable without a floor | Phase 4 `V5-E` |
| — | `proc.interactive` / live PTY | `D-03`; a PTY is a capability-widening session | Chunked `proc.exec` receipts |
| — | MCP / ACP adapters | `DEF-04`; rules pre-recorded in `006 §4.4` | Phase 4 `V5-H` |
| — | Competence graph $G_C$, operator registry, playbooks, offline optimiser | `O-01`/`O-03` triggers have not fired — and **cannot fire until the A/A floor exists** | Phase 4, after `S9-C-03` |
| — | Training on the corpus | `DEF-09`, `MEM-7` | Phase 4+ |
| — | Public leaderboard publication | `DEF-08`; no floor, no splits | After Q3 |

---

## 9. Sprint 6B traceability (closed)

All Sprint 6B waves W0–W5 are `[DONE]` and receipted; the record lives at
`docs/scrum/sprints/sprint6B/todo_list_sprint6B.md`. Closure evidence verified during this
reconciliation (`009 §3.2`): Ed25519 approvals (25 refs), `RuntimeService` (9 commands), unified
bwrap worker, evaluator daemon entry point + packaging, `--candidate` contract mode, LAM/Ollama
`ModelPort` adapters, LAM `pytest_passed` honesty fix, `store.py`.

**Sprint 7/8 Lane A+B (partial):** manifest loader, alias engine, workspace discovery, four
reconstruction packs, `vg-shell-only`, `lab/{bench,diff,build}.py` are `[DONE]` — **except** the
alias translation defect, carried as `S7-B-01`/`S7-B-05`.

---

## 10. Change log

| Date | Change |
|---|---|
| 2026-08-16 | Opened. Supersedes `todo_list.md` as the living tracker. Seeded from `008`, `009 §3.1`, LAM-plan Packets 0–14, and the two adopted superpowers plans. Authorised by `DECISION-0005` |
