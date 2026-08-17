# Backend roadmap

Status: living board  
Updated: 2026-08-17  
Branch: `feat_sprint_special`

**Spec (locked):** `docs/main_v4/` — especially `13_C_gts_mvp_program_and_engineering_plan.md` (plan/rationale, not a second board) and VG-02 / VG-03 / VG-04 / VG-05.  
**How-to:** `docs/scrum/sprints/sprint07` … `sprint10` (lane kits). Do not copy status into the kits.  
**Product harvest:** `features_to_add_v430.md` (atoms from Aider / OpenCode / Claude Code — not a second board).

This file is the only backend backlog. Mark `[DONE] ✅` here when the DoD command passed. `[DEPRECATED]` = scheduling or duplicate row; do not execute. `[BLOCKED]` = design named, not coded.

---

## Now — v0.4.3 coding CLI (who does what)

Goal: one `vg run` harness in the middle of **Aider** (repo map as observation), **OpenCode** (pack + `AGENTS.md` + headless), **Claude Code** (`Read`/`Grep`/`Edit`/`Bash`, `max_turns`, isolated spawn). Greenfield and bugfix are the same command. Not a second agent loop.

| Owner | Prefix | Does | Does not |
|---|---|---|---|
| **ALFA** | `[alfa]` | ✅ all rows done. Green `t7` + keep `approval_policy` kind row. **S10-A-01…04** (`invocation.py` domain out, `proc.test` bind/delete, `BlobStorePort`+`IndexPort`, `vg why`). | `kernel/**`, `agency/episode/**`, packs, CLI default, telemetry, ADR-0067 |
| **BETA** | `[beta]` | Product-default pack + `vg run` default + ACI tool-schema thicken + bind IndexPort when ALFA lands it. P0/P1 in `features_to_add_v430.md`. | `kernel/**`, `engine.py`, `runtime/root.py`, TableWorld/lab rebuild, dogfood-as-DONE without a human |
| **GAMMA** (CTO+PL+TL+senior) | `[gamma]` | **Everything else still `[TODO]` / `[BLOCKED]` on this file** — Joint, kernel sealed-flag ADR, dogfood *execution*, spend/release text, node suite, daemon J1, Claim wire. See table below. | ALFA’s S10-A files, BETA’s product pack/CLI default, V5 / \(G_C\) / playbooks / MCP *code* |

### Remaining work (this is the live backlog)

| ID | Status | Owner | What |
|---|---|---|---|
| S10-A-01 | `[DONE] ✅` | ALFA | Domain out of `invocation.py` (`854e8e8`). Translator is schema+selector; no verb table. |
| S10-A-02 | `[DONE] ✅` | ALFA | Orphan deleted (`4ee8aaf`) from `WorkerProtocol.SUPPORTED_OPERATIONS` + dispatch. Also fixed: `sandboxed.py` sent `operation="proc.test"` for **every** process call, so the allowlist and ledger saw a name the harness never granted — now `proc.exec`. 3 agreement tests both directions. ⚠️ `test/adapters/test_sandbox_worker.py::test_execute_proc_test` + `::test_proc_test_rejects_shell_string` are red — they assert the deleted op; owner must retarget at `proc.exec`. |
| S10-A-03 | `[DONE] ✅` | ALFA | `BlobStorePort` + `IndexPort` (`6f392f4`), two impls each per `T10.2`. Index is observation-only — a test asserts no `propose`/`rank`/`select`/`dispatch`. Real index is a regex scan; tree-sitter can replace the body without the port moving. |
| S10-A-04 | `[DONE] ✅` | ALFA | `vg why` load-bearing (`20e26c9`). `_cmd_ExplainArtifact` returned `{"explanation": ""}`; now derives activation from the ledger, prediction + demotion from the `Claim` store. Absence is reported, never smoothed — unevidenced must not resemble well-evidenced. |
| P0 / P1 pack+CLI | `[TODO] ❌` | BETA | **Plan approved — execute** `plan_p0_p1_product_pack.md`. Also retarget `test_translate_unknown_tool_fails` (unknown verbs fail at composition, not a builtin list). |
| S8-J-08 / ADR-0067 | `[DONE] ✅` | **GAMMA** | `Scope.sealed` via `attenuate()`; membership keyed on sealed, not depth. TCB 1333/1438. |
| S7-J-04 | `[TODO] ❌` | **GAMMA / human CTO** | Rotate OpenRouter key in the dashboard **first**. No history rewrite until then |
| S8-J-01 | `[TODO] ❌` | GAMMA | VG-04 Claim reader fields + golden vectors; then emit `support_count` / `last_corroborated_at` / `protection_class` |
| S8-J-03 + Q2 | `[TODO] ❌` | GAMMA | **Execute** DOGFOOD-01..03 (protocol is `[DONE]` as S9-J-01). Interactive, no mid-run hand-patch. LAM cassettes do not count |
| S8-J-04 | `[TODO] ❌` | GAMMA | Full suite with `node` installed (clear the 14–15 reader errors) |
| S8-J-05 | `[TODO] ❌` | GAMMA | `doing/` 12 → 8 + record `011` supersession (`49b7628`) |
| S8-J-06 / S7-J-08 | `[TODO] ❌` | GAMMA | ADR-0066 MCP **rules** (no MCP adapter code) |
| S8-J-07 / S7-J-06 | `[TODO] ❌` | GAMMA | Promote measurement science into VG-07 |
| S9-J-03 | `[TODO] ❌` | GAMMA / human | Spend authorisation (written sign-off). Until then: MOCK / Ollama / OpenRouter `free` only |
| S9-J-04 | `[TODO] ❌` | GAMMA | Q3 evidence vs ADR-0064 (dated “why not” is allowed) |
| S10-J-02 | `[TODO] ❌` | GAMMA | Reverse ADR-0064 only where evidence holds |
| S10-J-03 | `[TODO] ❌` | GAMMA | Release text = proven claims only |
| S10-J-04 | `[TODO] ❌` | GAMMA | Evaluate O-01 / O-03 **before** V5 — do not start V5 |
| FE-N1 (frontend board) | `[TODO] ❌` | GAMMA | Real daemon supervisor so `vg daemon` is not `not_available` — **after** ALFA S10-A; do not collide with BETA’s default-manifest CLI work |
| Merge / ship | `[TODO] ❌` | GAMMA | `feat_sprint_special` green, receipts, no decorative genes |

### Deprecated (do not execute; left for audit)

| Item | Status | Why |
|---|---|---|
| “Sprint 9 opens for Lane C only” / “A and B blocked from S9” | `[DEPRECATED]` | S8-A-02 and spawn are `[DONE]`. S9 coding rows are `[DONE]` |
| “HARD STOP — no A/A number until S8-A-02” as a coding blocker | `[DEPRECATED]` | A-02 green. Publishing a **lift** still needs S9-J-03 / S9-J-04 |
| S7-J-06, S7-J-07, S7-J-08 as separate builds | `[DEPRECATED]` duplicates | Use S8-J-07, S8-J-05, S8-J-06. Close the S7 rows when the S8 twin lands |
| Recreate `011` / `ROADMAP.MD` / `backlog_backend.md` | `[DEPRECATED]` | This file is the only backend board |
| V5, \(G_C\), playbooks, MCP **code**, optimiser, training | `[DEPRECATED]` for v0.4.3 | “Not this version” below. ADR-0066 text is in-scope; MCP implementation is not |
| Kernel membership in `policy.py` alone | `[DEPRECATED]` approach | Measured and reverted (`cf97e77`). Needs `attenuation.py` sealed flag |
| Mock-kernel tests as spawn proof | `[DEPRECATED]` | Real Kernel only (`NarrowedChildCannotEscalate`) |

---

## Roadmap (high level)

Build the smallest system that can honestly say whether machine competence accumulates. First client: coding. Not a chatbot wrapper.

| Wave | Sprint | Makes true | Gate |
|---|---|---|---|
| Closed (S0–S6B) | — | Kernel, ledger, episode loop, daemon, packs, sandbox | Phase 2 beta machinery |
| W6 | **7** | Every effect goes through `Kernel.dispatch` | Q1 restore |
| W7 | **8** | Parent spawns child; resume from ledger; manifests change behaviour | CLOSED (2026-08-17) |
| W8 | **9** | A/A floor vs `vg-shell-only`; runner refuses junk | Q2 / Q3 |
| W9 | **10** | TableWorld + published core line-count | Q4 (B/C `[DONE]`; A still open) |
| W10 | **product** | One coding `vg run` (Aider/OpenCode/Claude middle) | ALFA S10-A + BETA P0/P1 + GAMMA Joint/dogfood |
| Later | V5 | After O-01 / O-03 | `docs/reviews/doing/010_…` — **not this tag** |

**v0.4.3 ships when GTS-13C Ch. 10 is evidenced:** boundary real · three real bugs on the installed path · A/A floor · non-coding env with measured core churn. CI green alone does not ship.

**Do not start:** competence graph \(G_C\), operator registry, playbooks, offline optimiser, MCP code, training on the corpus.

**LLM rule (S8–S9):** MOCK first · Ollama if present · OpenRouter `free` only · `top: []` forever until Project Lead names ids · no lifts until S9 floor + spend sign-off.

---

## Already done (before Sprint 7)

Simplified. Detail lives in closed sprint folders under `docs/scrum/sprints/sprint0` … `sprint6B`.

| ID | Status | What |
|---|---|---|
| S0–S4 | `[DONE] ✅` | Contracts, kernel dispatch S0–S12, ledger, must-fail suite, `spike/`/`slice/` disposable by CI |
| S5–S6 | `[DONE] ✅` | Episode engine depth-1, environments, evaluators exterior, wire VG-04 |
| S6B | `[DONE] ✅` | Ed25519 approvals, `RuntimeService`, bwrap worker, LAM/Ollama ports, `--candidate` contract |
| Packs | `[DONE] ✅` | `vg-code-default`, `vg-shell-only`, claude/opencode/swe-mini shaped manifests (prompt+alias; DNA still thin until S8) |
| Lab CLI | `[DONE] ✅` | `lab/{bench,diff,build}.py` exist |

---

## Sprint 7 — Subtraction & boundary restoration · W6

Sentence: every executable path traverses `Kernel.dispatch`, proven by planted broken counterparts.

Evidence: `docs/scrum/sprints/sprint07/evidence/s7-close-receipt.md` (539 tests, 0 failures, 14 node-absent errors, 38 counterparts).

### Lane A

| ID | Status | Task |
|---|---|---|
| S7-A-01 | `[DONE] ✅` | Lattice CI: no extra top-level package under `vanguard/packages/` |
| S7-A-02 | `[DONE] ✅` | `subprocess` only from `adapters/sandbox/` |
| S7-A-03 | `[DONE] ✅` | No evaluator import from `agency/` or `runtime/` |
| S7-A-04 | `[DONE] ✅` | Delete `runtime/loops/` |
| S7-A-05 | `[DONE] ✅` | Delete `coordination.py`; depth = ledger projection |
| S7-A-06 | `[DONE] ✅` | No hardcoded bwrap path / reservation / fake tokens |
| S7-A-07 | `[DONE] ✅` | `repo_paths` after `docs/agile` → `docs/scrum` |

### Lane B

| ID | Status | Task |
|---|---|---|
| S7-B-01 | `[DONE] ✅` | One alias shape; unknown alias fails at compose |
| S7-B-02 | `[DONE] ✅` | Unread manifest component fails compose |
| S7-B-03 | `[DONE] ✅` | Metamorphic context_policy test (green via S8 compaction) |
| S7-B-04 | `[DONE] ✅` | `gene_digests` on results |
| S7-B-05 | `[DONE] ✅` | `vg-shell-only` undeletable bench test |

### Lane C

| ID | Status | Task |
|---|---|---|
| S7-C-01 | `[DONE] ✅` | `benchmarkings/` may import `runtime.root` + `ports` only |
| S7-C-02 | `[DONE] ✅` | `guard.py` refuses degenerate runs |
| S7-C-03 | `[DONE] ✅` | Delete four bypass runners |
| S7-C-04 | `[DONE] ✅` | Retraction + `_external_model_probes/` |
| S7-C-05 | `[DONE] ✅` | Sole runner: `zero_hint_v1/run_live_agent.py` |
| S7-C-06 | `[DONE] ✅` | `models.json` `top: []` fail-closed |
| S7-C-07 | `[DONE] ✅` | LAM gym uses pack system prompt, not competitor persona |

### Joint

| ID | Status | Task |
|---|---|---|
| S7-J-01 | `[DONE] ✅` | ADR-0063 Python; reverse ADR-0001 |
| S7-J-02 | `[DONE] ✅` | ADR-0064 gate status |
| S7-J-03 | `[DONE] ✅` | ADR-0065 D-01…D-15 binding |
| S7-J-04 | `[TODO] ❌` | SEC-01. **Blocked on the CTO: rotate in the OpenRouter dashboard first** — engineering cannot and must not do this. Tree is clean (`.env` untracked + gitignored, scan PASS); disclosure is historical: 1 reachable `.env` blob, **21 `refs/original/**`**, 3 remote branches. Rewrite stays gated on rotation + written per-ref sign-off. Detail: `docs/scrum/sprints/sprint08/evidence/s7-j-04-key-rotation.md`. Does not block S8/S9 coding |
| S7-J-05 | `[DONE] ✅` | `LICENSE` Apache-2.0 on disk |
| S7-J-06 | `[DEPRECATED]` → S8-J-07 | Promote measurement science into VG-07 (**do S8-J-07**, then mark this done) |
| S7-J-07 | `[DEPRECATED]` → S8-J-05 | `doing/` cap 8 (**do S8-J-05**) |
| S7-J-08 | `[DEPRECATED]` → S8-J-06 | ADR-0066 MCP rules **before** MCP code (**do S8-J-06**) |

---

## Sprint 8 — Recursion, resume, load-bearing manifests · W7 · **CLOSED (2026-08-17)**

Sentence: parent spawns child under attenuated grant + child lease; child turns stay out of parent context; resume from ledger alone.

### Lane A

| ID | Status | Task |
|---|---|---|
| S8-A-01 | `[DONE] ✅` | `compose` / `HarnessSession` / `run`; one `Kernel`; delete `_WitnessKernel` |
| S8-A-02 | `[DONE] ✅` | Suspend/resume from ledger; `max_turns` survives approval |
| S8-A-03 | `[DONE] ✅` | `RandomPort` + complete `ClockPort` |
| S8-A-04 | `[DONE] ✅` | `RecordCorrection` via `parse_wire` |
| S8-A-05 | `[DONE] ✅` | `Claim` domain type; empty invalidation fails; substrate auto-stale |

### Lane B

| ID | Status | Task |
|---|---|---|
| S8-B-01 | `[DONE] ✅` | `EpisodeEngine.spawn` (model proposal `ProposalKind.SPAWN` + fail-closed `args["scope"]` parsing + attenuation + causation + typed return + workspace `finally`) |
| S8-B-01a | `[DONE] ✅` | `parent_lease` on child requests; budget conservation properties (`fc9f5f4`) |
| S8-B-02 | `[DONE] ✅` | `CompactionStrategy` registry; metamorphic green |
| S8-B-03 | `[DONE] ✅` | `ModelRouter` from `routing_policy` |
| S8-B-04 | `[DONE] ✅` | `approval_policy` component (`fc9f5f4`) |
| S8-B-05 | `[DONE] ✅` | Child isolation: only return in parent L5 |
| S8-B-06 | `[DONE] ✅` | ACI paginated `fs.read` |
| S8-B-07 | `[DONE] ✅` | ACI succinct `fs.search` |
| S8-B-08 | `[DONE] ✅` | ACI empty `proc.exec` ack |
| S8-B-09 | `[DONE] ✅` | Lint-on-patch as receipt, not verdict |
| S8-B-10 | `[DONE] ✅` | `maxTurns` from `budget_policy` |

### Lane C

| ID | Status | Task |
|---|---|---|
| S8-C-01 | `[DONE] ✅` | `EpisodeDepthProjection` (landed in S7-A-05; do not rebuild) |
| S8-C-02 | `[DONE] ✅` | Cache-hit / prefix-stability over cassette (`a0c15fc`) |
| S8-C-03 | `[DONE] ✅` | Prefix-miss: `system` / `tools` / `compact` / `snip` |
| S8-C-04 | `[DONE] ✅` | LAM `t0-`/`t6-` regex vs corpus |

### Joint

| ID | Status | Task |
|---|---|---|
| S8-J-01 | `[TODO] ❌` | VG-04 Claim wire (reader fields, golden vectors). **A did NOT jump the gun** — `support_count` / `last_corroborated_at` / `protection_class` are on the domain type, defaulted, and withheld from `to_wire()`, with a test citing this row as the gate. `additionalProperties:false` confirms emitting them now would be rejected by the normative reader. Joint owns the amendment; **A must not emit until it lands** |
| S8-J-02 | **`[DONE] ✅`** | **ADR-0060 HELD.** `docs/scrum/sprints/sprint08/evidence/s8-j-02-adr0060-diff.md`. Re-run over final spawn diff: 0 domain nouns. TCB unchanged 1315. Boundary check PASS. |
| S8-J-03 | `[TODO] ❌` | Q1/Q2 evidence; dogfood bugs named `DOGFOOD-01..03` (do not count LAM cassettes) |
| S8-J-04 | `[TODO] ❌` | Full suite with `node` installed (today: 14 reader errors) |
| S8-J-05 | `[TODO] ❌` | `doing/` 12 → 8 — **and record the `011` supersession**: `49b7628` deleted the master backlog (TL-verified statuses + Lane B audit) without the authorising row. Consolidation is fine; the silent drop is not |
| S8-J-06 | `[TODO] ❌` | ADR-0066 (was S7-J-08) |
| S8-J-07 | `[TODO] ❌` | VG-07 promotion (was S7-J-06) |

**Sprint 8 is formally CLOSED (2026-08-17).** S8-A-02 verified green · S8-B-01 verified fail-closed on model proposal · Joint J-02 ADR-0060 verified (0 domain nouns) · Sprint close receipt: `docs/scrum/sprints/sprint08/evidence/s8-close-receipt.md`.

### TL audit 2026-08-17 — status corrections

Full audit: `docs/scrum/sprints/sprint08/evidence/s8-audit-2026-08-17.md`.
604 tests · 0 failures · 14 node-absent errors · 12/12 gates PASS · TCB 1315/1438 · LLM rule respected.

| ID | Was | Now | Why |
|---|---|---|---|
| S8-B-01 | `[CLAIMED — UNREACHABLE]` | **`[DONE] ✅`** | Option (a) delivered: `ProposalKind.SPAWN` wired into episode loop; child `Scope` built fail-closed from `args["scope"]` (missing/junk fails closed); updated docstrings. **Correction (`8f5f16d`, alfa):** the earlier "narrowing to `fs.read` prevents `patch.apply`" claim was verified only against a mock kernel whose own `dispatch` implemented the scope check. Against the real `Kernel`/`StandardPolicy` the child **executed** `patch.apply` — `authorize` never checks `request.action ∈ requested_scope.actions` and the widening predicate reads the principal's held authority, not the episode scope. Child engines are now `attenuated=True` and refuse to emit a request outside their grant; 3 new tests verified failing without the guard. Kernel-side enforcement remains open — needs an ADR (`ADR-0054`). |
| S8-B-01a | `[DONE] ✅` | `[DONE] ✅` | Confirmed real: `parent_lease` reaches `Governor.reserve`; F-13 tested. |
| S8-A-02 | `[DONE] ✅` | `[DONE] ✅` | Segment loop deleted; `grep -c max_segments root.py` → 0. Measured before: `max_turns=4` gave 8 proposals. After: 2→2, 4→4, 8→8, terminal ABANDONED with the exhaustion stated. Re-entry reduces the ledger via `domain/ledger/reducer.py`; `state_digest()` reproduced with the session object deleted. `agency/episode/engine.py` untouched. |

**`[DEPRECATED]` scheduling (2026-08-17):** “Sprint 9 opens for Lane C only” / “A and B blocked from S9”. S8-A-02 and spawn are closed; S9 lanes A/B/C coding are `[DONE]`. Remaining S9 work is Joint (J-03 spend, J-04 Q3).

**Commit discipline:** a lane-prefixed commit must carry the production change it names. Three of this sprint's rows were fixed, verified and recorded in three different commits.

### Lane B — `spawn` choice: **DELIVERED: OPTION (a) Wired & Fail-Closed** (2026-08-17)

Lane B selected Option (a) and delivered:
1. `ProposalKind.SPAWN` parsed from model proposals in `state.py`.
2. Fail-closed child `Scope` parsing from `args["scope"]` via `_parse_child_scope` in `engine.py` (missing or unparseable scope returns typed failure receipt `scope_unparseable` without granting parent scope).
3. Monotone attenuation holds on spawn: child narrowed to `fs.read` is strictly prohibited from executing unauthorized actions such as `patch.apply`.
4. Stale docstrings updated in `engine.py:17-19` and `state.py:178`.
5. Verified across all 13 property and loop tests in `test/agency/test_episode_spawn.py`. ADR-0060 respected (zero domain vocabulary in the engine).

### Restored — Lane B audit trail (was in `011`, deleted by `49b7628`; `011` is not being recreated)

Preserved here because the finding is still load-bearing and its original home was removed.

> **TL audit of Lane B's pre-Sprint-8 `spawn`, 2026-08-16 (S7 close).** Verdict: **ACCEPTED as the
> Sprint 8 starting point, not sent back.** Attenuation, depth ceiling, `causationId`, typed
> `SpawnResult` and workspace-destroy-in-`finally` verified across 7 tests. `ADR-0060` held; TCB
> unchanged.
>
> **One material gap, in the centre row.** `S8-B-01`'s DoD named three property tests; one existed.
> The missing pair was the budget properties — *"budget conserved two levels deep"* and *"child
> overrun debits the parent"* — and the mechanism was unwired: `spawn` built the child on the shared
> `Kernel`, but no `parent_lease` was set on any effect request (`engine.py:196`), so the `Governor`
> lease tree was never built. Shared ceilings gave conservation *incidentally*; the DoD asked for it
> *structurally*. Recorded as a finish, not a rewrite → `S8-B-01a`.
>
> **Closed 2026-08-17.** `parent_lease` now reaches `Governor.reserve`; F-13 (a closed parent cannot
> fund a child) is tested. The finding is resolved. Attribution remains wrong: the production change
> landed in untagged `ce15850`, `c8976fc` added tests only, and the backlog cited `fc9f5f4`.
>
> Also preserved from `011`: `S8-B-04` was corrected `[CLAIMED]` → `[TODO] ❌` at the S7 close because
> `root.py:740` still carried the `TODO(S8-B-04)` literal with no test. It has since landed properly
> (`fc9f5f4`) and is `[DONE] ✅`. `S8-B-02/03/05/06..10` were TL-verified `[DONE] ✅` at that audit.

---

## Sprint 9 — The instrument · W8

Sentence: A/A noise floor per task class vs `vg-shell-only`; refuse degenerate designs.

Lane C coding `[DONE]`. No published **lift** / no cloud spend until S9-J-03.

**`[DEPRECATED]` (2026-08-17):** “OPEN FOR LANE C ONLY” and the A-02 64-turn hard stop as a *coding* gate. `S8-A-02` is `[DONE]`. The runner exists (`S9-C-03`). A published floor number still waits on spend (S9-J-03) and Q3 write-up (S9-J-04).

| ID | Status | Lane | Task |
|---|---|---|---|
| S9-C-01 | `[DONE] ✅` | C | Wire M-18 tuple (`tools/telemetry/tuple.py`); refuse lift if `K_compat` differs |
| S9-C-02 | `[DONE] ✅` | C | Pre-registration hashed before any arm (`tools/telemetry/preregistration.py`) |
| S9-C-03 | `[DONE] ✅` | C | A/A runner (`tools/telemetry/aa_runner.py`); refuse zero/degenerate floor (not on LAM replay) |
| S9-C-04 | `[DONE] ✅` | C | McNemar / bootstrap / survival (`tools/telemetry/statistics.py`); no p-values at n<20 |
| S9-C-05 | `[DONE] ✅` | C | Splits DEV/HOLDOUT/SEALED/LIVE/DEPLOYMENT with one-way burn touch ledger (`tools/telemetry/splits.py`) |
| S9-C-06 | `[DONE] ✅` | C | Oracle hardening + metamorphic properties (`test/lab/test_oracle_hardening.py`) |
| S9-C-07 | `[DONE] ✅` | C | Seeded sabotage: cheats must fail (`test/lab/test_seeded_sabotage.py`) |
| S9-B-01 | `[DONE] ✅` | B | Real reconstructions: 4 packs differ on ≥3 DNA dimensions (`test/agency/test_reconstructions.py`) + `REFERENCE.md` per pack |
| S9-B-02 | `[DONE] ✅` | B | `vg harness build\|run\|diff\|bench` (`lab/build.py`, `lab/run.py`, `lab/diff.py`, `lab/bench.py`) with pre-reg hash enforcement |
| S8-J-08 | `[DONE] ✅` | A | **ADR-0067 accepted.** `Scope.sealed` set by `attenuate()` when the parent withholds verbs; `authorize` denies `action ∉ requested_scope.actions` only when sealed. Spine trusted-widening preserved. TCB 1333/1438. |
| S9-A-01 | `[DONE] ✅` | A | Instrument fields on `RunResult` — `gene_digests`, `state_digest`, per-arm `instrument_error`. **Finding:** `composition_digest` binds `episode_id`, so `gene_digests` is the cross-run pack identity attribution must group on. Recorded, not changed (`L-1`). |
| S9-A-02 | `[DONE] ✅` | A | Integer micros/tokens/USD only — `runtime/telemetry.py::RunTelemetry`, rejects floats and `bool`; absent stays `None`, never `0`. |
| S9-A-03 | `[DONE] ✅` | A | `RunResult.replay_gaps()` — executable audit vs Phase 4 `V5-A`, with a failing counterpart (`A-10`). |
| S9-A-04 | `[DONE] ✅` | A | `state_digest` + `HarnessSession.ledger_state()` for Lane C's paired runner. |
| S9-J-01 | `[DONE] ✅` | J | Q2 dogfood ×3 pre-registered protocol (`docs/scrum/sprints/sprint09/evidence/s9-j-01-dogfood-protocol.md`) |
| S9-J-02 | `[DONE] ✅` | J | Countersigned CT-09 sha256 hash format over canonical JCS bytes |
| S9-J-03 | `[TODO] ❌` | J | Spend authorisation |
| S9-J-04 | `[TODO] ❌` | J | Q3 evidence vs ADR-0064 |

---

## Sprint 10 — Generality and the MVP gate · W9

Sentence: non-coding env runs; kernel + episode LOC delta published whatever it is.

| ID | Status | Lane | Task |
|---|---|---|---|
| S10-A-01 | `[DONE] ✅` | A → **ALFA** | Domain out of `invocation.py` (`854e8e8`) |
| S10-A-02 | `[TODO] ❌` | A → **ALFA** | **DELETE `proc.test` orphan**; tests via allowlisted `proc.exec` (BETA freezes pack JSON) |
| S10-A-03 | `[TODO] ❌` | A → **ALFA** | `BlobStorePort` + `IndexPort` (fake + real; Aider repo-map slot) |
| S10-A-04 | `[TODO] ❌` | A → **ALFA** | `vg why <artifact>` |
| S10-B-01 | `[DONE] ✅` | B | TableWorld (`adapters/environment/tableworld.py`, `vg-table-default` pack, invariant evaluator, abstention on inconsistency) |
| S10-B-02 | `[DONE] ✅` | B | CI core-change detector (`tools/check_core_changes.py`, C-10 measurement publisher) |
| S10-B-03 | `[DONE] ✅` | B | `structured_consolidate` + `deadEnds` (`agency/context/compaction.py`) |
| S10-B-04 | `[DONE] ✅` | B | `regroundPolicy` as a granted effect (`agency/context/regrounding.py`) |
| S10-C-01 | `[DONE] ✅` | C | Instrument unchanged on second domain (`test/lab/test_tableworld_instrument.py`) |
| S10-C-02 | `[DONE] ✅` | C | Verifier–deployment gap freeze (`tools/telemetry/gap_freeze.py`) |
| S10-C-03 | `[DONE] ✅` | C | Gate evidence pack including negatives (`docs/scrum/sprints/sprint10/evidence/s10-gate-evidence-pack.md`) |
| S10-J-01 | `[DONE] ✅` | J | Four-question review with evidence paths in gate evidence pack |
| S10-J-02 | `[TODO] ❌` | J → **GAMMA** | Reverse ADR-0064 only where evidence holds |
| S10-J-03 | `[TODO] ❌` | J → **GAMMA** | Release text = proven claims only |
| S10-J-04 | `[TODO] ❌` | J → **GAMMA** | Evaluate O-01 / O-03 before V5 |

---

## Not this version

| Item | When |
|---|---|
| \(G_C\), promotion topology | O-01: one artifact clears the A/A floor |
| Operator registry, playbooks | O-03: spawn too shallow for a real task |
| Offline optimiser / GEPA | After S8 replay ports **and** S9 floor |
| MCP adapter | After ADR-0066; post-v0.4.3 |
| A2A, independence groups, training, public leaderboard | Triggers in VG-10 / 008 §7 |

Rejected forever here: second agent loop that grades itself; Atom→Biome classes; runtime workflow DAG.

---

## MVP gate (copy of GTS-13C Ch. 10)

1. **Q1 Boundary?** Red team misses control plane / evaluator / secrets. Must-fail counterparts fail. Kill/restart keeps known vs uncertain. No second execution path.
2. **Q2 Useful?** Three real bugs, interactive, no mid-run hand-patch. Honest “reach for it again?”
3. **Q3 Measurable?** Per-class A/A vs `vg-shell-only`. One paired comparison. Gap number or dated “why not”.
4. **Q4 General?** TableWorld added; published LOC change in `kernel/` + `agency/episode/`.
