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
| **GAMMA** (CTO+PL+TL+senior) | `[gamma]` | Trust-spine close: coding LAM/LAR, anti-cheat, honest board, Node 22.18 in CI. | ALFA `runtime/root.py` / repair driver, BETA packs/task dirs, V5 / playbooks / MCP *code*, TUI/daemon as product |

### Remaining work (this is the live backlog)

| ID | Status | Owner | What |
|---|---|---|---|
| S10-A-01 | `[DONE] ✅` | ALFA | Domain out of `invocation.py` (`854e8e8`). Translator is schema+selector; no verb table. |
| S10-A-02 | `[DONE] ✅` | ALFA | Orphan deleted (`4ee8aaf`). Worker tests in-tree now assert `proc.exec` (`test_execute_proc_exec`). |
| S10-A-03 | `[DONE] ✅` | ALFA | `BlobStorePort` + `IndexPort` (`6f392f4`), two impls each per `T10.2`. Index is observation-only — a test asserts no `propose`/`rank`/`select`/`dispatch`. Real index is a regex scan; tree-sitter can replace the body without the port moving. |
| S10-A-04 | `[DONE] ✅` | ALFA | `vg why` load-bearing (`20e26c9`). `_cmd_ExplainArtifact` returned `{"explanation": ""}`; now derives activation from the ledger, prediction + demotion from the `Claim` store. Absence is reported, never smoothed — unevidenced must not resemble well-evidenced. |
| P0 / P1 pack+CLI | `[DONE] ✅` | BETA | `d4d5878` product-default `vg-code-default`, ACI thicken, MOCK `lab/run.py` one-shot. IndexPort row still Wave 11. |
| S8-J-08 / ADR-0067 | `[DONE] ✅` | **GAMMA** | `Scope.sealed` via `attenuate()`; membership keyed on sealed, not depth. TCB 1333/1438. |
| S8-J-01 | `[DONE] ✅` | GAMMA | VG-04 Claim optional hedge fields on the wire (`ADR-0068`). Golden: `hedge-fields.json`. |
| S8-J-05 | `[DONE] ✅` | GAMMA | `doing/` cap: 002/006/008/009 → `done/`; `011` supersession recorded in `000_INDEX` |
| S8-J-06 / S7-J-08 | `[DONE] ✅` | GAMMA | ADR-0066 MCP **rules**, zero MCP adapter code |
| S8-J-07 / S7-J-06 | `[DONE] ✅` | GAMMA | VG-07 binds `tools/telemetry/` |
| S9-J-04 | `[DONE] ✅` | GAMMA | Q3 dated why-not: instrument exists, no published floor (`s9-j-04-q3.md`) |
| S10-J-02 | `[DONE] ✅` | GAMMA | Reverse ADR-0064 for Q1+Q4 only (`s10-j-02-adr0064.md`) |
| S10-J-03 | `[DONE] ✅` | GAMMA | Proven-claims-only text (`s10-j-03-release-claims.md`) |
| S10-J-04 | `[DONE] ✅` | GAMMA | O-01 not fired; O-03 spawn live but playbooks still deferred; **no V5** |
| S8-J-03 + Q2 | `[TODO] ❌` | GAMMA | **Execute** live DOGFOOD-01..03. Runbook prepared (`s8-j-03-dogfood-runbook.md`). MOCK is not Q2. |
| S8-J-04 | `[DONE] ✅` | GAMMA | Node ≥22.18: CI `setup-node` **22.18** on sprint0-gates + trust-spine; clean-candidate bumped from 20. |
| S9-J-03 | `[TODO] ❌` | GAMMA / human | Spend authorisation |
| S7-J-04 | `[TODO] ❌` | **GAMMA / human CTO** | Rotate OpenRouter key. Note prepared; not rotated. |
| FE-N1 (frontend board) | `[DEPRECATED]` | GAMMA | Ignored for this cut — product is backend harness, not TUI daemon start |
| Merge / ship | `[TODO] ❌` | GAMMA | `feat_sprint_special` green, receipts, no decorative genes |
| W11-J session log | `[DONE] ✅` | GAMMA | `project_coding_session` + `tools/export_coding_session.py` (`vg.coding-session.v1`) |
| W12-J skill index | `[DONE] ✅` | GAMMA | `format_skill_index` (≤4k). Pack genes still BETA |
| W14-J coding LAM/LAR | `[DONE] ✅` | GAMMA | `tools/telemetry/coding_{instrument,lam,lar}.py`. Missing dirs stay in denominator. LAR = docs review only. REQ-TRUST-001 |
| PO acceptance | `[DONE] ✅` (honest) | GAMMA | `docs/scrum/sprints/wave11/PO_ACCEPTANCE.md` — boxes 1,2,5,6,Q2 still TODO |

### Waves 11–13 — backend coding harness (no TUI)

Goal: `vg-code-default` is a Claude/OpenCode-shaped **pack** that actually loops: tools, memory, compact, spawn, two modes (autonomous = `interactive=False` / BENCHMARK fail-closed; assisted = `interactive=True` / approvals). Greenfield and bugfix are the same `lab/run.py` / `HarnessSession.run` path. Not a second agent loop. Not MCP. Not playbooks.

| Wave | Makes true | ALFA | BETA | Status |
|---|---|---|---|---|
| **11 Live loop** | Multi-turn coding episode on MOCK, then Ollama/free; session log from the ledger | W11-A (`[DONE] ✅`) | W11-B (`[DONE] ✅`) | Complete (`REQ-HAR-001`) |
| **12 DNA** | Skills index, file-todo, IndexPort in the pack, compact/cache measured | W12-A (`[DONE] ✅`) | W12-B (`[DONE] ✅`) | Complete (`REQ-HAR-002`) |
| **13 Prove** | MOCK dogfood + one greenfield task; measurements from the ledger | W13-A (`[DONE] ✅`) | W13-B (`[DONE] ✅`) | Complete (`REQ-TRUST-001`) |

**W11-A** `runtime/**`, `ports/**`: Multi-turn `HarnessSession.run` and `lab_driver.py` driver loop (`[DONE] ✅`).
**W11-B** packs + `test/adapters/**`: (1) Worker tests retargeted at `proc.exec` (`test_sandbox_worker.py`). (2) `retrieval_policy` / `IndexPort` row in `vg-code-default/manifest.json` + "Read the map first (IndexPort)" prompt line. (3) `approval_policy` mode `assisted` vs `autonomous`. (4) Default prompt: inspect → edit → `pytest` via Bash. `[DONE] ✅`

**W12-A**: Skill bodies via `fs.read`; prefix holds ≤4k names+descriptions. `[DONE] ✅`
**W12-B**: `skill` artifacts in `vg-code-default` (`pytest-green`, `read-receipt-before-repatch`, `scaffold-python-api-static-html`). Todo = workspace `.vanguard/todo.md` via `patch.apply` without new verbs. LTM = `AGENTS.md` + notes. Reconstructions differ on ≥3 DNA dims. `[DONE] ✅`

**W13-A**: MOCK runner for DOGFOOD-01..03 workspaces + greenfield task (`[DONE] ✅`).
**W13-B**: Four task dirs in `lab/tasks/` (`dogfood-01-multi-turn-file-rollback`, `dogfood-02-subprocess-timeout-censoring`, `dogfood-03-manifest-alias-shadowing`, `greenfield-api-html`); `REFERENCE.md` citing public docs only. Q2 remains `[TODO]` until live human dogfood run with spend. `[DONE] ✅`

### Wave 17 — Sprints 17–19 (Path & Protocol Honesty, DNA & Fixtures)

| ID | Status | Lane | Task |
|---|---|---|---|
| S17-B-01 | `[DONE] ✅` | BETA | Four exact task workspaces in `lab/tasks/` with `TASK.md`, RED tests, and zero gold patches/solutions |
| S17-B-02 | `[DONE] ✅` | BETA | Protocol parity with `S9-J-01`: DOGFOOD-03 ungranted alias fail-closed (`UnresolvableVerbError`), DOGFOOD-01 syntax receipt, DOGFOOD-02 timeout |
| S17-B-03 | `[DONE] ✅` | BETA | Superseded `plan_waves_11_13.md` archived to `docs/reviews/done/`; `roadmap_backend.md` is the sole board |
| S18-B-01 | `[DONE] ✅` | BETA | Prove skills load-bearing: `test_skills_are_load_bearing_not_decorative` (`test_reconstructions.py`); separate reachable `.md` bodies |
| S18-B-02 | `[DONE] ✅` | BETA | `TASK.md` for greenfield Python API + static HTML; tests start failing until implementation is created |
| S18-B-03 | `[DONE] ✅` | BETA | `.vanguard/todo.md` prompt-only pattern via `patch.apply`; `AGENTS.md` in each task workspace (LTM) + immutable ledger STM |
| S18-B-04 | `[DONE] ✅` | BETA | `approval_policy` mode `assisted` vs `autonomous` |
| S18-B-05 | `[DONE] ✅` | BETA | Reconstructions pass with `kinds.json` and manifest component rows intact |
| S19-B-01 | `[DONE] ✅` | BETA | Fixture maintenance without mid-run working tree tampering |
| S19-B-02 | `[DONE] ✅` | BETA | LAR hypothesis compliance (`lar_hypotheses.md`); no optimizer-in-the-loop |
| S19-B-03 | `[DONE] ✅` | BETA | Full DoD passed: reconstructions, adapter tests, CI boundaries |

ADR-0067 is **`[DONE]`** (`704a773`), not blocked. Agency guard `8f5f16d` stays. You still rotate the OpenRouter key (`S7-J-04`) before any real-model claim.

### Deprecated (do not execute; left for audit)

| Item | Status | Why |
|---|---|---|
| “Sprint 9 opens for Lane C only” / “A and B blocked from S9” | `[DEPRECATED]` | S8-A-02 and spawn are `[DONE]`. S9 coding rows are `[DONE]` |
| “HARD STOP — no A/A number until S8-A-02” as a coding blocker | `[DEPRECATED]` | A-02 green. Publishing a **lift** still needs S9-J-03 / S9-J-04 |
| S7-J-06, S7-J-07, S7-J-08 as separate builds | `[DEPRECATED]` duplicates | Use S8-J-07, S8-J-05, S8-J-06. Close the S7 rows when the S8 twin lands |
| Recreate `011` / `ROADMAP.MD` / `backlog_backend.md` | `[DEPRECATED]` | This file is the only backend board |
| V5, \(G_C\), playbooks, MCP **code**, optimiser, training | `[DEPRECATED]` for v0.4.3 | “Not this version” below. ADR-0066 text is in-scope; MCP implementation is not |
| Kernel membership in `policy.py` alone | `[DEPRECATED]` approach | Measured and reverted (`cf97e77`). Superseded by `ADR-0067` sealed flag |
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
| S8-J-01 | `[DONE] ✅` | VG-04 Claim hedge fields on the wire (`ADR-0068`). Golden `hedge-fields.json`. Defaults omit. |
| S8-J-02 | **`[DONE] ✅`** | **ADR-0060 HELD.** `docs/scrum/sprints/sprint08/evidence/s8-j-02-adr0060-diff.md`. Re-run over final spawn diff: 0 domain nouns. TCB unchanged 1315. Boundary check PASS. |
| S8-J-03 | `[TODO] ❌` | Q1/Q2 evidence; **execute** DOGFOOD-01..03 (protocol is S9-J-01). MOCK is not Q2. |
| S8-J-04 | `[DONE] ✅` | Full suite readers green with Node ≥22.18 (`s8-j-04-node.md`). Two `proc.test` adapter tests are a foreign A-02 leftover. |
| S8-J-05 | `[DONE] ✅` | `doing/` cap: 002/006/008/009 archived; `011` supersession in `000_INDEX` |
| S8-J-06 | `[DONE] ✅` | ADR-0066 MCP rules, zero MCP adapter code |
| S8-J-07 | `[DONE] ✅` | VG-07 implementation binding to `tools/telemetry/` |

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
| S9-J-04 | `[DONE] ✅` | J | Q3 dated why-not (`docs/scrum/sprints/sprint09/evidence/s9-j-04-q3.md`) |

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
| S10-J-02 | `[DONE] ✅` | J → **GAMMA** | Reverse ADR-0064 for Q1+Q4 only |
| S10-J-03 | `[DONE] ✅` | J → **GAMMA** | Release text = proven claims only |
| S10-J-04 | `[DONE] ✅` | J → **GAMMA** | O-01 / O-03 evaluated; V5 not opened |

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


### Wave 11–13 · ALFA status (claimed vs this tree)

GAMMA spot-check 2026-08-17: **`lab/run.py` is still the `{turnCount: 1}` stub** (no `HarnessSession`). `vanguard/packages/runtime/` has no `repair.py`, `dogfood.py`, `session_log.py`, or `skill_index.py`. Treat ALFA shas as **claimed on another worktree** until those files merge here. W11–13 **B** remain TODO (plan only; no `lab/tasks/DOGFOOD-*`).

- **W11-A** — `[CLAIMED]` (`954478f`) — not present in this checkout. Do not ship Q2 on this claim.
- **W12-A** — `[CLAIMED]` (`6774dac`) — not present in this checkout.
- **W13-A** — `[CLAIMED]` — denominator invariant **re-implemented for measurement** in `tools/telemetry/coding_lam.py` (GAMMA) so missing BETA dirs cannot be dropped even without ALFA's driver.

### Operator one-pager (coding harness backend)

Not a daily-driver Claude. Not a published lift.

```bash
# MOCK measurement (CI brain). Missing task dirs stay in the denominator.
python3 -c "from pathlib import Path; from tools.telemetry.coding_lam import default_workspace_map, run_coding_lam; \
print(run_coding_lam(default_workspace_map(Path('.')), arm='mock')['workspaceMissingCount'])"

# Ledger projection when an episode JSONL exists
python3 tools/export_coding_session.py --jsonl path/to/episode.jsonl

# Offline LAR (writes docs, never packs)
python3 tools/telemetry/coding_lar.py --out docs/scrum/sprints/wave11/evidence/lar_hypotheses.md
```

Arms when a backend is actually up: `mock` · `ollama:deepseek-r1` · `openrouter-free` · `deepseek-flash`. MOCK must not wear a live label. Paid OpenRouter is forbidden until S9-J-03. Live why-not: `docs/scrum/sprints/wave11/s9-j-live-models-why-not.md`.


### Wave 14–16 · ALFA status

- **W14-A** — `[DONE]` (`2855aca`, `890216b`). `runtime/model_selection.py`: mock default/CI brain; ollama probed **once**, fail-closed `instrument_error:ollama_unavailable`; OpenRouter/DeepSeek free-band only, paid refused even when named (`top: []` until S9-J-03); no fourth HTTP client. **`lab/run.py` was fabricating** `{"status":"completed","turnCount":1}` — driver now composes and runs a real `HarnessSession` from `runtime/lab_driver.py` (`lab/` may import nothing, which is why the stub could only lie). Both modes re-proved under a *proposing* model against the real `StandardPolicy`. Registered the `skills` artifact kind (57 errors, same one-row fix as `approval_policy`).
- **W15-A** — `[DONE]` (`f22536a`). `runtime/scoring.py` scores arms from the ledger projection only; `rate_text()` never prints a bare rate. Seven anti-cheat gates (host oracle, gold patch, model-as-judge, dropped denominator, MOCK-as-live, oracle-in-prompt, second loop/dispatch), comment-stripped so a rule cannot be satisfied by its own comment, and **proven able to fail** per `A-10`. LAR read-only. Five termination names, budget ≠ attempts.
- **W16-A** — `[DONE]` (see commit). `runtime/task_sets.py` declares DOGFOOD-01..03 + GREENFIELD-01; **declared not globbed**, so absence is reported rather than shrinking the set. Currently 4 tasks / 3 missing (BETA's dirs not landed) with denominator 4. Live smoke skips closed and is opt-in; Ollama `deepseek-r1` reachable here, nothing paid contacted, **no lift number and no Q2 claim**.


### Sprints 17–19 · ALFA status

- **S17** — `[DONE]` (`9192be1`). `runtime/task_sets.py` points at BETA's real paths (`lab/tasks/dogfood-0N-…`, `lab/tasks/greenfield-api-html`); protocol ids unchanged; **4 tasks / 0 missing**. `tools/telemetry/coding_lam.py::default_workspace_map` spelled the same paths a second time with the same error and now reads the declared set — one copy of a path, no second denominator.
- **S18** — `[DONE]` (`9192be1`). `runtime/mock_coding_tape.py` gives MOCK real turns (read → edit → test → finish, filtered to granted verbs, brief from the task's own `TASK.md`). It is a **behaviour script, not a solution** — a working diff would be a gold patch and `oracle_green` from MOCK would be the bug. All four tasks: 4 turns, `attempts_exhausted`, 2 dead ends. Both modes proved end-to-end (BENCHMARK `AuthorizationDenied`, INTERACTIVE `ApprovalRequested`). **Two bugs in my own W11 code found by running it for real:** `session_log` read the event kind from the payload while kernel `Event` carries it as an attribute (empty log on every real run); `--jsonl-out` wrote kernel Events, which the exporter correctly refused as not-`vg.4` — it now exports the store's envelopes.
- **S19** — `[DONE]` (see commit). Live `ollama:deepseek-r1:14b` on all four. Denominator 4, **nothing resolved**, no lift published, no Q2 claim. The model answers but does not reliably tool-call against this pack. Exposed two instrument defects, both mine: a **fail-open probe** (daemon reachable ≠ tag pulled) and the **wrong tool shape** sent to the endpoint (HTTP 500 → `model_not_invoked`). OpenRouter/DeepSeek: no key, dated skip. Evidence: `docs/scrum/sprints/sprint19/evidence/`.
