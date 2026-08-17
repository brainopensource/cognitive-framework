# Backend roadmap

Status: living board  
Updated: 2026-08-16  
Branch: `sprints7-8/integration`

**Spec (locked):** `docs/main_v4/` — especially `13_C_gts_mvp_program_and_engineering_plan.md` (plan/rationale, not a second board) and VG-02 / VG-03 / VG-04 / VG-05.  
**How-to:** `docs/scrum/sprints/sprint07` … `sprint10` (lane kits). Do not copy status into the kits.

This file is the only backend backlog. Mark `[DONE]` here when the DoD command passed.

---

## Roadmap (high level)

Build the smallest system that can honestly say whether machine competence accumulates. First client: coding. Not a chatbot wrapper.

| Wave | Sprint | Makes true | Gate |
|---|---|---|---|
| Closed (S0–S6B) | — | Kernel, ledger, episode loop, daemon, packs, sandbox | Phase 2 beta machinery |
| W6 | **7** | Every effect goes through `Kernel.dispatch` | Q1 restore |
| W7 | **8** | Parent spawns child; resume from ledger; manifests change behaviour | Recursion + DNA |
| W8 | **9** | A/A floor vs `vg-shell-only`; runner refuses junk | Q2 / Q3 |
| W9 | **10** | TableWorld + published core line-count | Q4 → v0.4.3 |
| Later | V5 | After O-01 / O-03 | `docs/reviews/doing/010_…` |

**v0.4.3 ships when GTS-13C Ch. 10 is evidenced:** boundary real · three real bugs on the installed path · A/A floor · non-coding env with measured core churn. CI green alone does not ship.

**Do not start:** competence graph \(G_C\), operator registry, playbooks, offline optimiser, MCP code, training on the corpus.

**LLM rule (S8–S9):** MOCK first · Ollama if present · OpenRouter `free` only · `top: []` forever until Project Lead names ids · no lifts until S9 floor + spend sign-off.

---

## Already done (before Sprint 7)

Simplified. Detail lives in closed sprint folders under `docs/scrum/sprints/sprint0` … `sprint6B`.

| ID | Status | What |
|---|---|---|
| S0–S4 | `[DONE]` | Contracts, kernel dispatch S0–S12, ledger, must-fail suite, `spike/`/`slice/` disposable by CI |
| S5–S6 | `[DONE]` | Episode engine depth-1, environments, evaluators exterior, wire VG-04 |
| S6B | `[DONE]` | Ed25519 approvals, `RuntimeService`, bwrap worker, LAM/Ollama ports, `--candidate` contract |
| Packs | `[DONE]` | `vg-code-default`, `vg-shell-only`, claude/opencode/swe-mini shaped manifests (prompt+alias; DNA still thin until S8) |
| Lab CLI | `[DONE]` | `lab/{bench,diff,build}.py` exist |

---

## Sprint 7 — Subtraction & boundary restoration · W6

Sentence: every executable path traverses `Kernel.dispatch`, proven by planted broken counterparts.

Evidence: `docs/scrum/sprints/sprint07/evidence/s7-close-receipt.md` (539 tests, 0 failures, 14 node-absent errors, 38 counterparts).

### Lane A

| ID | Status | Task |
|---|---|---|
| S7-A-01 | `[DONE]` | Lattice CI: no extra top-level package under `vanguard/packages/` |
| S7-A-02 | `[DONE]` | `subprocess` only from `adapters/sandbox/` |
| S7-A-03 | `[DONE]` | No evaluator import from `agency/` or `runtime/` |
| S7-A-04 | `[DONE]` | Delete `runtime/loops/` |
| S7-A-05 | `[DONE]` | Delete `coordination.py`; depth = ledger projection |
| S7-A-06 | `[DONE]` | No hardcoded bwrap path / reservation / fake tokens |
| S7-A-07 | `[DONE]` | `repo_paths` after `docs/agile` → `docs/scrum` |

### Lane B

| ID | Status | Task |
|---|---|---|
| S7-B-01 | `[DONE]` | One alias shape; unknown alias fails at compose |
| S7-B-02 | `[DONE]` | Unread manifest component fails compose |
| S7-B-03 | `[DONE]` | Metamorphic context_policy test (green via S8 compaction) |
| S7-B-04 | `[DONE]` | `gene_digests` on results |
| S7-B-05 | `[DONE]` | `vg-shell-only` undeletable bench test |

### Lane C

| ID | Status | Task |
|---|---|---|
| S7-C-01 | `[DONE]` | `benchmarkings/` may import `runtime.root` + `ports` only |
| S7-C-02 | `[DONE]` | `guard.py` refuses degenerate runs |
| S7-C-03 | `[DONE]` | Delete four bypass runners |
| S7-C-04 | `[DONE]` | Retraction + `_external_model_probes/` |
| S7-C-05 | `[DONE]` | Sole runner: `zero_hint_v1/run_live_agent.py` |
| S7-C-06 | `[DONE]` | `models.json` `top: []` fail-closed |
| S7-C-07 | `[DONE]` | LAM gym uses pack system prompt, not competitor persona |

### Joint

| ID | Status | Task |
|---|---|---|
| S7-J-01 | `[DONE]` | ADR-0063 Python; reverse ADR-0001 |
| S7-J-02 | `[DONE]` | ADR-0064 gate status |
| S7-J-03 | `[DONE]` | ADR-0065 D-01…D-15 binding |
| S7-J-04 | `[TODO]` | SEC-01. **Blocked on the CTO: rotate in the OpenRouter dashboard first** — engineering cannot and must not do this. Tree is clean (`.env` untracked + gitignored, scan PASS); disclosure is historical: 1 reachable `.env` blob, **21 `refs/original/**`**, 3 remote branches. Rewrite stays gated on rotation + written per-ref sign-off. Detail: `docs/scrum/sprints/sprint08/evidence/s7-j-04-key-rotation.md`. Does not block S8/S9 coding |
| S7-J-05 | `[DONE]` | `LICENSE` Apache-2.0 on disk |
| S7-J-06 | `[TODO]` | Promote measurement science into VG-07 |
| S7-J-07 | `[TODO]` | `doing/` cap 8 (now over) |
| S7-J-08 | `[TODO]` | ADR-0066 MCP rules **before** MCP code |

---

## Sprint 8 — Recursion, resume, load-bearing manifests · W7

Sentence: parent spawns child under attenuated grant + child lease; child turns stay out of parent context; resume from ledger alone.

### Lane A

| ID | Status | Task |
|---|---|---|
| S8-A-01 | `[DONE]` | `compose` / `HarnessSession` / `run`; one `Kernel`; delete `_WitnessKernel` |
| S8-A-02 | `[DONE]` | Suspend/resume from ledger; `max_turns` survives approval |
| S8-A-03 | `[DONE]` | `RandomPort` + complete `ClockPort` |
| S8-A-04 | `[DONE]` | `RecordCorrection` via `parse_wire` |
| S8-A-05 | `[DONE]` | `Claim` domain type; empty invalidation fails; substrate auto-stale |

### Lane B

| ID | Status | Task |
|---|---|---|
| S8-B-01 | **`[SENT BACK]`** | `spawn` is now **reachable** from a model proposal (`ProposalKind.SPAWN`, `engine.py:198`) — that half is done. **But the child is not attenuated on that path and it fails open:** `parse_proposal` yields plain dicts and `Scope` is never built from `args`, so `isinstance(raw_scope, Scope)` is always false and `child_scope` falls back to `self._scope` — the parent's **full** scope. Probed: a model asking to narrow to `fs.read` got a child with `patch.apply` + `proc.exec`, request silently discarded. Fix list in the close receipt §3 |
| S8-B-01a | `[DONE]` | `parent_lease` on child requests; budget conservation properties (`fc9f5f4`) |
| S8-B-02 | `[DONE]` | `CompactionStrategy` registry; metamorphic green |
| S8-B-03 | `[DONE]` | `ModelRouter` from `routing_policy` |
| S8-B-04 | `[DONE]` | `approval_policy` component (`fc9f5f4`) |
| S8-B-05 | `[DONE]` | Child isolation: only return in parent L5 |
| S8-B-06 | `[DONE]` | ACI paginated `fs.read` |
| S8-B-07 | `[DONE]` | ACI succinct `fs.search` |
| S8-B-08 | `[DONE]` | ACI empty `proc.exec` ack |
| S8-B-09 | `[DONE]` | Lint-on-patch as receipt, not verdict |
| S8-B-10 | `[DONE]` | `maxTurns` from `budget_policy` |

### Lane C

| ID | Status | Task |
|---|---|---|
| S8-C-01 | `[DONE]` | `EpisodeDepthProjection` (landed in S7-A-05; do not rebuild) |
| S8-C-02 | `[DONE]` | Cache-hit / prefix-stability over cassette (`a0c15fc`) |
| S8-C-03 | `[DONE]` | Prefix-miss: `system` / `tools` / `compact` / `snip` |
| S8-C-04 | `[DONE]` | LAM `t0-`/`t6-` regex vs corpus |

### Joint

| ID | Status | Task |
|---|---|---|
| S8-J-01 | `[TODO]` | VG-04 Claim wire (reader fields, golden vectors). **A did NOT jump the gun** — `support_count` / `last_corroborated_at` / `protection_class` are on the domain type, defaulted, and withheld from `to_wire()`, with a test citing this row as the gate. `additionalProperties:false` confirms emitting them now would be rejected by the normative reader. Joint owns the amendment; **A must not emit until it lands** |
| S8-J-02 | **`[DONE]`** | **ADR-0060 HELD.** `docs/scrum/sprints/sprint08/evidence/s8-j-02-adr0060-diff.md`. Sprint 8 changed **5 lines** in `agency/episode/`, all `parent_lease` (kernel budget vocabulary, not domain). Wide noun scan: 2 hits, both prose (`source class`, `dead code`). TCB unchanged 1315. **Caveat: re-run if Lane B wires `spawn` to a ProposalKind** — a spawn proposal is where domain nouns would most plausibly leak |
| S8-J-03 | `[TODO]` | Q1/Q2 evidence; dogfood bugs named `DOGFOOD-01..03` (do not count LAM cassettes) |
| S8-J-04 | `[TODO]` | Full suite with `node` installed (today: 14 reader errors) |
| S8-J-05 | `[TODO]` | `doing/` 12 → 8 — **and record the `011` supersession**: `49b7628` deleted the master backlog (TL-verified statuses + Lane B audit) without the authorising row. Consolidation is fine; the silent drop is not |
| S8-J-06 | `[TODO]` | ADR-0066 (was S7-J-08) |
| S8-J-07 | `[TODO]` | VG-07 promotion (was S7-J-06) |

**S8 exit still open until:** ~~S8-A-02 green~~ ✅ · **`spawn` attenuation fixed (B)** ❌ · ~~Joint J-02~~ ✅ · clean close receipt.

### Close attempt 2026-08-17 — **REFUSED.** Sprint 8 remains OPEN.

Receipt: `docs/scrum/sprints/sprint08/evidence/s8-close-receipt.md`.
615 tests · 0 failures · 14 node-absent errors · 12/12 gates · TCB 1315 unchanged · boundaries PASS (167 files).

- **Lane A `S8-A-02`: CLEARED.** `max_segments` → 0; resume reconstructs `state_digest` from the ledger alone; the 8×8=64 bound is dead. Verified, not reported.
- **Lane B `S8-B-01`: SENT BACK.** Model-proposed spawn works, but grants the child the parent's **full authority** and silently drops the model's narrowing request. Fails open — the one direction this codebase never fails. Fix list: close receipt §3.
- **Joint `S8-J-02`: RE-RUN on the spawn diff, ADR-0060 HELD.** Zero domain nouns; `brief`/`scope`/`spawn` are episode-kernel vocabulary. Must be re-run **again** after B's fix.

**Sprint 10: not started, not authorised.**

### TL audit 2026-08-17 — two blockers, status corrections

Full audit: `docs/scrum/sprints/sprint08/evidence/s8-audit-2026-08-17.md`.
604 tests · 0 failures · 14 node-absent errors · 12/12 gates PASS · TCB 1315/1438 · LLM rule respected.

| ID | Was | Now | Why |
|---|---|---|---|
| S8-B-01 | `[DONE]` | **`[CLAIMED — UNREACHABLE]`** | `spawn` has **no production call site**, no `ProposalKind.SPAWN`, no manifest verb, and `SpawnResult` has no consumer. `engine.py:17-19` and `state.py:167` still say *"never re-enters itself"* / *"spawns no sub-episode"* — and both are still accurate. The sprint sentence is true of the test suite, not the system. |
| S8-B-01a | `[DONE]` | `[DONE]` | Confirmed real: `parent_lease` reaches `Governor.reserve`; F-13 tested. Attribution is wrong though — production code landed in untagged `ce15850`; `c8976fc` added tests only; the cited `fc9f5f4` is the approval_policy commit. |
| S8-A-02 | `[DONE]` | `[DONE]` | Segment loop deleted; `grep -c max_segments root.py` → 0. Measured before: `max_turns=4` gave 8 proposals. After: 2→2, 4→4, 8→8, terminal ABANDONED with the exhaustion stated. Re-entry reduces the ledger via `domain/ledger/reducer.py`; `state_digest()` reproduced with the session object deleted. `agency/episode/engine.py` untouched. |

**Sprint 9 opens for Lane C only.** C starts `S9-C-01`→`C-02`→`C-03` now; both blockers are independent of it.
**C must not publish an A/A floor until S8-A-02 is green** — a floor measured against a 64-turn bound we intend to change is not a floor.
**A and B are blocked from S9** until their row above is cleared.

**Commit discipline:** a lane-prefixed commit must carry the production change it names. Three of this sprint's rows were fixed, verified and recorded in three different commits.

### Lane B — `spawn` choice: **(a) WIRE IT, chosen `7e42230`. Reachability accepted; attenuation SENT BACK.**

Lane B has committed nothing since the audit. The choice is B's to make and must be written **here**,
signed, before `S8-B-01` moves off `[CLAIMED — UNREACHABLE]`.

| Option | What B must deliver | Consequence for S9 |
|---|---|---|
| **(a) Wire it** | `ProposalKind.SPAWN` + spawn tool schema + manifest capability; update the two stale docstrings (`engine.py:17-19`, `state.py:167`); one test where a **model proposal** — not a direct Python call — produces a child episode | Recursion counts as a DNA dimension for `S9-B-01`. **`S8-J-02` must be re-run** against the change |
| **(b) Declare dormant** | One paragraph here stating recursion is on no executable path; tests retained | `S9-B-01` must find its ≥3 dimensions **without** recursion |

**Not permitted:** leaving `S8-B-01` `[DONE]` and unreachable. That is the contamination pattern
Sprint 7 was spent removing.

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
> Also preserved from `011`: `S8-B-04` was corrected `[CLAIMED]` → `[TODO]` at the S7 close because
> `root.py:740` still carried the `TODO(S8-B-04)` literal with no test. It has since landed properly
> (`fc9f5f4`) and is `[DONE]`. `S8-B-02/03/05/06..10` were TL-verified `[DONE]` at that audit.

---

## Sprint 9 — The instrument · W8

Sentence: A/A noise floor per task class vs `vg-shell-only`; refuse degenerate designs.

Lane C leads. No published delta. No cloud spend until S9-J-03.

**OPEN FOR LANE C ONLY (2026-08-17).** C is cleared to code `S9-C-01`, `S9-C-02`, `S9-C-03` now,
against `vg-shell-only` with `tools/002_LLM_API_MOCK`. Both Sprint 8 blockers are independent of C.

> **HARD STOP — no A/A number until `S8-A-02` is green.** Build the runner and its refusal path;
> **hold the number.** The real turn bound today is `max_turns 8 × max_segments 8 = 64`, and
> `S8-A-02` is about to change it. A floor measured against a bound we intend to change is not a
> floor, and re-measuring afterwards invalidates everything derived from it.
> Emitting a floor before A-02 is green is a Sprint 9 stop condition, not a scheduling preference.

**Lanes A and B are NOT open for Sprint 9** until `S8-A-02` is green and B's `spawn` choice is
recorded in writing above.

| ID | Status | Lane | Task |
|---|---|---|---|
| S9-C-01 | `[TODO]` | C | Wire M-18 tuple; refuse lift if `K_compat` differs |
| S9-C-02 | `[TODO]` | C | Pre-registration hashed before any arm |
| S9-C-03 | `[TODO]` | C | A/A runner; refuse zero/degenerate floor (not on LAM replay) |
| S9-C-04 | `[TODO]` | C | McNemar / bootstrap / survival; no p-values at n<20 |
| S9-C-05 | `[TODO]` | C | Splits DEV/HOLDOUT/SEALED/LIVE/DEPLOYMENT |
| S9-C-06 | `[TODO]` | C | Oracle hardening + isomorphic perturbation |
| S9-C-07 | `[TODO]` | C | Seeded sabotage: cheats must fail |
| S9-B-01 | `[TODO]` | B | Real reconstructions: differ on ≥3 DNA dimensions |
| S9-B-02 | `[TODO]` | B | `vg harness build\|run\|diff\|bench` (`bench` waits C-02) |
| S9-A-01 | `[TODO]` | A | Instrument fields on `RunResult` (after S8-A-01 — now unblocked) |
| S9-A-02 | `[TODO]` | A | Integer micros/tokens/USD only |
| S9-A-03 | `[TODO]` | A | Recording enough to replay a bench run |
| S9-A-04 | `[TODO]` | A | Ledger queries for paired runner |
| S9-J-01 | `[TODO]` | J | Q2 dogfood ×3, installed CLI, no hand-patch |
| S9-J-02 | `[TODO]` | J | Countersign pre-reg hashes; no optional stopping |
| S9-J-03 | `[TODO]` | J | Spend authorisation |
| S9-J-04 | `[TODO]` | J | Q3 evidence vs ADR-0064 |

---

## Sprint 10 — Generality and the MVP gate · W9

Sentence: non-coding env runs; kernel + episode LOC delta published whatever it is.

| ID | Status | Lane | Task |
|---|---|---|---|
| S10-A-01 | `[TODO]` | A | Domain out of `invocation.py` into manifest rows |
| S10-A-02 | `[TODO]` | A | `proc.test` bind or delete orphan |
| S10-A-03 | `[TODO]` | A | `BlobStorePort` + `IndexPort` (fake + real) |
| S10-A-04 | `[TODO]` | A | `vg why <artifact>` |
| S10-B-01 | `[TODO]` | B | TableWorld (no shell, no paths as domain) |
| S10-B-02 | `[TODO]` | B | CI core-change detector (C-10) |
| S10-B-03 | `[TODO]` | B | `structured_consolidate` + `deadEnds` |
| S10-B-04 | `[TODO]` | B | `regroundPolicy` as a granted effect |
| S10-C-01 | `[TODO]` | C | Instrument unchanged on second domain |
| S10-C-02 | `[TODO]` | C | Verifier–deployment gap freeze |
| S10-C-03 | `[TODO]` | C | Gate evidence pack (include negatives) |
| S10-J-01 | `[TODO]` | J | Four-question review with evidence paths |
| S10-J-02 | `[TODO]` | J | Reverse ADR-0064 only where evidence holds |
| S10-J-03 | `[TODO]` | J | Release text = proven claims only |
| S10-J-04 | `[TODO]` | J | Evaluate O-01 / O-03 before V5 |

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
