# Leadership Decision Packet — Execution Plane and Capability Roadmap

**Status: proposal and evidence packet. Nothing here is authorized.** Prepared for Director review; the Senior transfers only what leadership accepts.

### How to read this packet

| Tag | Meaning |
|---|---|
| **[VERIFIED]** | Measured against the tree at HEAD. Not a decision — check it, don't rule on it. |
| **[AUTHORITY]** | An existing accepted ruling or invariant, cited. Unchanged unless leadership supersedes it. |
| **[RECOMMENDED]** | A proposed disposition with its evidence. Confirm, amend, defer or reject. |
| **[DECISION]** | A genuine fork this packet does **not** close. Leadership must rule. |

Where a section carries no tag, treat it as **[RECOMMENDED]**.

## Context

**The problem is not that the code is unfinished. It is that the documents describe the wrong things.**

Exploration of `vanguard/` against `docs/execution/` found an inverted precision gradient. The code is substantially mature:

| Capability | Reality |
|---|---|
| Context compilation | `agency/context/compiler.py:102` — complete. Epoch binding `:289`, budget `layers.py:128`, 3 compaction strategies `compaction.py:130/167/250` |
| Multi-file 2PC | `adapters/environment/transaction.py:46` — real snapshot/preflight/commit/rollback. 8-matcher `resilient_patcher.py:64` |
| Session + resume | `runtime/session.py:779` (2,896 LOC), sigma fold `:2460`, resume identity `:1374`, `checkpoints.py:313` |
| Completion admission | `agency/episode/admission_gate.py:40` — the class exists |
| Delegation / multi-agent | `runtime/delegation.py:407` with `M6_SPAWN_ACTIVE = True`. `runtime/topology.py` is a real graph compiler with 3 frozen BEP-04 topologies |

Meanwhile `technical.md` §Appendix A, self-labelled **"Algorithms (normative for implementers)"**, contains four headings — `A.1 Completion admission`, `A.2 Turn compile`, `A.3 2PC write`, `A.4 Campaign step` — and **no bodies**. `### 3.2 L1–L5 Prefix-Stable Context Architecture` is empty; the layers are defined only in `agency/context/layers.py:42`. `### 6.3 Bounded Protocol Recovery State Machine` is empty. The entire §5.x formal model is empty, twice.

The documents are most rigorous about **FH-1**, the post-control horizon that is explicitly `[PROPOSAL]` and furthest from execution, and vaguest about the surfaces being built right now.

**This is the mechanism behind the gate problem.** A senior developer cannot make an ordinary decision from a document that contains no contract, so every ordinary decision becomes an escalation. Reviews are not heavy because leadership is cautious; they are heavy because the contracts that would make review unnecessary were never written down. `development_philosophy.md:59-65` states the target directly: a developer works two weeks, makes a hundred decisions, and review finds nothing that should have been escalated.

**The decision requested here is not a blank-sheet redesign.** Leadership should separate verified implementation facts from accepted architecture, resolve contradictions that force escalation, and decide which genuinely new capability boundaries are stable enough to lock. As-built code is evidence; it becomes normative only when it also satisfies the governing invariants and acceptance evidence.

### Decisions requested — scope of this packet **[DECISION]**

Three scoping choices were taken in the originating session and are carried here **as proposals for leadership to ratify or overturn**, not as settled authority:

1. **Lock horizon:** control path *and* the SOTA capability plane (context, multi-file, long-session, planner-worker) — accepting that capability design would be locked ahead of control evidence. *Leadership may instead restrict locking to the control path.*
2. **Doc plane:** no sixth execution file. *That constraint is `[AUTHORITY]` (`README.md:96`); leadership must route each accepted result to its semantic owner: normative law and typed deltas in `spec.md`, implementation guidance in `technical.md`, live work in `tasks.md`, stable gates in `milestones.md`, and accepted durable design in the existing architecture/reference documents.*
3. **Envelope:** a fourth long-horizon preset. *Whether a separate pack is the right product boundary is `[DECISION]` — see §3.2.*

### The enabling discovery

`technical.md` is 2,466 lines against a 2,300 ceiling — **over by 166**. But lines 1655–2466 are a retired anchor block: **812 lines, of which 11 are prose** and ~795 are bare headings retained only for old fragment links.

I verified those anchors have **zero inbound links**. The only inbound anchor link in the repository (`spec.md:605`) points at `#post-control-reference-handbook-fh-1-proposal`, which is at line 759 in the live section. The `dev_context_logs/*.json` hits are line-range locators against the pre-move path `docs/execution/technical.md` and are already dead.

Collapsing that block yields ~1,667 lines and **~633 lines of headroom under the existing ceiling.** The recommended handbook content could fit without a governance ceiling raise. Original text stays recoverable at `git show 001911e3:docs/execution/technical.md`.

### Role boundary

`DIRECTOR.md:161` forbids the director from editing execution documents; `roles_and_authority.md:23` assigns task rows and status to the Senior. This packet is therefore written as **recommended dispositions for leadership to rule on, and for the Senior to transfer once accepted**. Items leadership must decide are marked **[DECISION]**; measured claims are marked **[VERIFIED]** and are open to checking, not ruling.

### Executive decision surface

| Decision | Packet posture |
|---|---|
| C1-C9 contradiction dispositions | **[RECOMMENDED]** individually; leadership confirms, amends, defers or rejects |
| Contract promotion and semantic owner | **[DECISION]** based on invariants plus acceptance evidence, not source existence alone |
| Leadership as independent acceptor | **[DECISION]**; eligibility and independence basis must be confirmed |
| W2/W3 capability packets and leases | **[DECISION]**; candidate work only until authorized and assigned by the Senior |
| Long-horizon packaging and envelope | **[DECISION]**; invariants may be locked before provisional numeric values |
| Framework 0.9.4 cut | **[DECISION]** independent of the product-release milestones |

---

## Execution order and ownership

**[VERIFIED] Nothing in this packet blocks developer dispatch.** Phase 0a touches only `technical.md` and `spec.md`; the `tasks.md` retirement is in 0b and re-pinning in 0c. The current A/B/C queue is factual and already authorized — leadership may amend its sequencing, but it need not wait on any phase here.

Documentation and development are **partly parallel, not automatically disjoint**. `tasks.md` is a Senior-owned serialization point, C's T-132 lease includes `justfile`, and production changes may carry canonical-document synchronization obligations. Leadership may prepare decisions concurrently, but the Senior schedules short merge windows and verifies every proposed documentation or source lease before dispatch.

| When | Owner | What |
|---|---|---|
| **First — one commit, no content edits** | CEO + Senior | **Phase 0a** (mechanical only): reclaim `technical.md`'s unlinked anchors, delete the byte-identical dialect duplicate |
| **On leadership ruling** | Senior | **Phase 0b**: the `spec.md` dedup/renumber choices, the `tasks.md` board retirement, and `justfile` linter placement — each selects surviving law or answers an open decision |
| **After the last semantic edit** | Senior | **Phase 0c**: regenerate all four binding pins on the final subject |
| **Immediately under existing authority** | Senior dispatches | **A**: T-131.8 on its exclusive lease. **B**: the four LANDED reviews (T-130/T-135/T-131.6/T-140) → acceptance-record reconciliation (T-75/T-76, T-78, T-83b, T-138, T-139) → T-131.3→4→7 on released files. **C**: T-133 *non-probe files first* → T-132 → T-137 → hermetic T-51 local readiness |
| **Concurrent with dev execution** | Director rules, Senior transfers | **Phases 1–4**: contradictions, as-built contracts, capability plane, measurement math |
| **After Phases 1–4 land** | Senior | **Phase 5**: contract index in `DEVS.md`; escalation triggers unchanged |
| **Last** | CEO | **Phase 6**: `.draft/` sweep; 0.9.4 cut **if** authorized |

**Open [DECISION] items, in one place:** the scope of this packet (§Decisions requested); `technical.md` versus `spec.md` as the home for each contract; `CoordinationPlan` versus the as-built `Topology` against W-OCT-2 (§3.3); the `horizon` envelope and whether a separate pack is the right boundary (§3.2); whether the three W2 rows become task rows and in what order; whether leadership is eligible as non-author acceptor (§5.4); whether a 0.9.4 cut is justified (§6.2); and where the two CI-only linters belong (§0b).

Everything else in this packet is either **[VERIFIED]** measurement or **[RECOMMENDED]** disposition awaiting confirmation.

**Do not wait for Phases 1–4 before dispatching already authorized work.** The contracts remove *future* escalations; they do not gate the work already leased. Review capacity is a current constraint, while documentation ambiguity is a separate source of future escalation.

---

## Work allocation and wave plan

### The current misallocation

Every developer is in the integrity lane: A on T-131.8, B on four reviews plus reconciliation, C on T-133→T-132→T-137. That lane is serialized by file leases, review-heavy by construction, and terminates in an acceptor pool of three. **Three high-capability coding agents with large context are being used as auditors of code that already exists.** That is simultaneously the most expensive and the least parallel way to deploy them.

The remedy is not to abandon integrity work — D-6 F1–F7 is real and the control gate is the right gate. It is to stop routing *all* capacity through the narrowest lane.

### Two streams

The 2026-09-13 CEO directive already decoupled capability from MS-CONTROL. Make that operational:

| | **Stream A — Control & integrity** | **Stream B — Capability** |
|---|---|---|
| Shape | Narrow, serialized, lease-contended | Wide, parallel, mostly new files |
| Review burden | Heavy — non-author acceptance at named evidence boundaries | Focused — new surface has no legacy debt but still needs falsification and acceptance |
| Bound by | Acceptor availability, curator/store authority | Contract, lease and acceptance decisions; hermetic work need not wait on curator/store |
| Output | F-number dispositions, T-27 readiness | The SOTA capability surface |

**Two proposed standing rules.** Stream B never claims a control result or a benchmark score — its output is capability, measured later under Stream A's protocol. A blocked Stream A leaf stops only that leaf; the Senior may move its owner to an already authorized, lease-compatible Stream B row rather than idling or inventing hardening work.

### Leadership as non-author acceptor **[DECISION]**

The acceptor deadlock is recorded in `tasks.md` as an external staffing blocker. **This packet proposes that it is not one. Leadership must confirm or reject its own eligibility; this is not a conclusion the packet can reach on leadership's behalf.**

`roles_and_authority.md:72-88` states that **review independence is per-change, not per-role-label**, and that the Senior records the independence basis. Leadership authored none of A/B/C's deltas, so it is non-author by construction and eligible on every one of them. This dissolves the deadlock without hiring.

**The constraint that makes it legitimate:** `DIRECTOR.md:37-43` says the Director does not approve every edit, and that strategic review and ordinary code review are different gates. So leadership accepts **only at batched acceptance boundaries** — a completed leaf with its full receipt — never per-commit and never as routine diff review. Ordinary review stays with the Senior. Record the independence basis each time.

This is the single highest-leverage action available right now: it unblocks B's entire queue and every downstream leaf that waits on a non-author disposition.

### Leadership and implementation boundary **[DECISION]**

The recommended default is that leadership owns decision and acceptance semantics while the Senior assigns implementation. Leadership writes code only if its role authority explicitly permits it and independence for later acceptance remains available. The following surfaces require leadership rulings even when a developer implements them:

- **Kernel-adjacent changes.** TCB is 1,386 logical LOC against a 1,438 alarm ceiling — **52 lines of headroom.** Any kernel edit is a leadership call by arithmetic alone.
- **Measurement math.** `roles_and_authority.md:20-26` assigns "statistical meaning" to the Director. The Wilson bound and false-completion semantics require leadership decisions; implementation remains delegable.
- **Cross-cutting seam repairs** surfaced during acceptance, where the fix spans more than one developer's lease.
- **Wave sequencing and contract authorship** (Phases 1–4).

Explicitly **not** leadership work: feature implementation, test authoring, corpus maintenance, status upkeep, routine diff review.

### Wave plan

**W1 — now (Stream A, finish what is leased)**

| Owner | Work |
|---|---|
| A | T-131.8 to completion |
| B | Four LANDED reviews → acceptance-record reconciliation → T-131.3→4→7 |
| C | T-133 (non-probe files first) → T-132 → T-137 |
| Leadership | Decide Phase 0 and begin Phases 1–2; accept completed leaves only if it confirms its eligibility and independence |

**W2 — the capability sprint (Stream B, genuinely parallel)**

**[DECISION] These three rows are proposed, not authorized.** Leadership decides whether each becomes a task row, in what dependency order, and under whose acceptance. Leases and falsifiers below are recommended starting points, not permanent architecture; the Senior compiles each against `work_packet_protocol.md`'s sixteen required fields before dispatch and assigns owners.

Three candidate surfaces, each substantially new code. The Senior must verify their final leases against the live board before parallel dispatch; this packet does not prove that future edits remain disjoint.

**B2-1 — Per-child worktree isolation** *(Senior assigns the owner)*
> **The correctness blocker for parallel workers.** `child_runtime.py` contains *zero* worktree or workspace references; `runtime/workspace.py` is a 21-line re-export shim. `git worktree` exists only as a `GitEnvironment` constructor option (`git.py:153-168`) that nothing in the delegation path uses. Today two parallel workers edit the same tree.
> **Outcome:** every spawned child receives an isolated worktree; parent tree is unreachable from a child; a failing child cannot mutate it; worktrees are reclaimed on every exit path including crash.
> **Lease:** `runtime/child_runtime.py`, `runtime/workspace.py`, `runtime/delegation.py` (spawn path only), new `test/runtime/test_child_worktree_isolation.py`.
> **Falsifier:** a child that writes outside its worktree is refused; a crashed child leaks no worktree; two concurrent children writing the same path do not interfere; disabling isolation makes the oracle fail.
> **Why it is hard:** crash-safe reclamation interacts with the `finally`-path teardown in `EpisodeEngine.spawn:1452` and with budget release ordering (S11 before S12).

**B2-2 — `packs/code-horizon/` and compaction at scale** *(Senior assigns the owner)*
> **Candidate outcome:** a long-horizon capability isolated from `code-default` so the frozen control subject survives, with mandatory bounded compaction, checkpoint policy and sigma durability across restart. A separate pack and `StructuredConsolidateStrategy` are recommended options, not preselected law.
> **Lease:** new `packs/code-horizon/**`, `agency/context/compaction.py`, `runtime/checkpoints.py`, new `test/packs/code_horizon/**`.
> **Falsifier:** a 200-turn session at 200k context survives a mid-run process kill and resumes with task/candidate/evidence/budget identity intact; compaction preserves the `TC-E-057` preservation set; a dropped carrier is detected, not silently repaired.
> **Why it is hard:** the compaction strategies exist but have never run at this scale. Identity preservation across ~10 compaction cycles plus a restart is the real test, and it is exactly where long-session agents fail.

**B2-3 — Greenfield oracle vacuity detector** *(Senior assigns the owner)*
> **Outcome:** a real detector behind `VACUOUS_ORACLE_REJECTED`, which is currently a code with no implementation. `spec.md:2287-2297` gives five prose stages whose load-bearing predicate — *"if it passes on stubs, it is vacuous"* — has no formal form.
> **Lease:** `adapters/environment/analysis.py`, `agency/multi_file_completeness.py`, new detector module, `test/packs/code_default/` greenfield cases.
> **Falsifier:** an oracle that passes against `pass`/`NotImplementedError` stubs is rejected; a real oracle is admitted; the detector cannot be satisfied by test mutation.
> **Why it is hard:** it must reject vacuity without rejecting legitimately simple tests — the false-positive side is what makes this a design problem rather than a grep.

Proposed leadership work during W2: decide Phases 3–4, including false-completion and Wilson semantics, and disposition W1 leaves where leadership has confirmed its independence.

**W3 — proposed convergence**

If leadership accepts the prerequisite packets, exercise planner→worker→verifier end to end on the selected long-horizon configuration over a real multi-file greenfield task, with accepted isolation and exterior-verifier merge. This would be a capability demonstration, **not** a control result — MS-CONTROL still requires Stream A's protocol.

---

## Phase 0 — Reclaim and re-pin **[RECOMMENDED]**

`README.md:108-110`: *"A documentation topology move is isolated from semantic edits."*

**Correction.** An earlier revision of this packet labelled all of Phase 0 "mechanical, no semantic content." That was wrong, and the document contradicted itself: Phase 1's table routes dispositions **C5** and **C7** through Phase 0, and three further items below change law or pre-empt a decision leadership has been asked to make. The phase is split accordingly. **Only 0a is proposed as mechanical. Leadership must verify that classification; 0b requires rulings and does not proceed without them.**

### Phase 0a — Genuinely mechanical (its own commit, on leadership authorization)

Byte-level operations with no choice of surviving content. **This packet does not self-authorize them** — leadership authorizes, the Senior executes.

**0a no longer blocks developer dispatch.** With the `tasks.md` retirement moved to 0b and re-pinning to 0c, 0a touches only `technical.md` and `spec.md`. A/B/C can be dispatched independently of this entire phase.

1. **`technical.md`**: delete lines 1656–2466, keeping the 11-line retirement note and its `git show` pointer. Verified: zero inbound anchor links. Result ~1,667 lines / 2,300 ceiling.
2. **`spec.md`**: delete the dialect duplicate at `1940–1942` — byte-identical to `1915–1917`, so nothing is chosen.
**Receipt:** blob comparison before/after confirming no semantic delta, plus `check_markdown_links.py` and `check_execution_truth.py` green.

**Note:** 0a alone does not bring `spec.md` or `tasks.md` under ceiling. Those depend on 0b, so the budget gate stays red until leadership rules.

**Re-pinning is deliberately NOT in 0a.** All four blobs currently mismatch, so `state_of_play.md` self-invalidates and `DEVS.md`/`DIRECTOR.md` self-declare their assignment sections stale — but 0b rewrites `spec.md` and `tasks.md`, which would invalidate any pin taken now. Pins are regenerated **once, in Phase 0c**, on the final intended documentation subject.

### Phase 0b — Requires leadership ruling before execution

Each item selects which of two conflicting texts becomes law, or decides a question leadership has been asked.

| Item | Why it is not mechanical |
|---|---|
| **`spec.md`** — collapse the two `INV-DELTA-1..5` copies (`1037–1043` terse, `2192–2196` verbose) | The copies differ materially. The verbose one carries "stale preimage" and the IndexPort enumeration requirement; the terse one drops them. Choosing the survivor **changes the invariant**. This is ruling **C5**. |
| **`spec.md`** — fold the second document at `2174–2390` | It duplicates §6.5/§5/§7/§8 with *conflicting* definitions. Selecting winners is a ruling, not a move. Its Python dataclasses are the only real typed contracts in the corpus and are retained for Phase 2 regardless. |
| **`spec.md`** — renumber the incoherent heading sequence | Section numbers are cited across the corpus (`§23.2`, `A §9.4`). Renumbering rewrites those references and can break anchors. |
| **`tasks.md`** — retire the superseded historical board | Deciding what is "superseded" is a **status judgment**, which `roles_and_authority.md` assigns to the Senior under leadership ruling, not a topology move. |
| **`justfile`** — placement of `check_doc_budgets.py` and `check_stale_paths.py` | Both run in `.github/workflows/ci.yml` but in neither `just check` nor `just verify`, so local green does not predict CI green. **But which recipe they belong in is an open decision** — `docs-check`, `check`, or `verify` — and depends on measured cost. Leadership decides; this packet does not pre-empt it. |

### Phase 0c — Final re-pin (after every applicable semantic edit)

Regenerate the binding blocks in `state_of_play.md`, `DEVS.md` and `DIRECTOR.md` against the final documentation subject — after 0b and after any Phase 1–4 edit that changes the four pinned files. Regenerate through the prescribed path; **never blind `git hash-object` substitution**, since the pin attests a verified snapshot, not a string match. A pin taken before its subject stops changing is worse than no pin: it reads as attested and is not.

---

## Phase 1 — Proposed contradiction dispositions **[RECOMMENDED]**

**The contradictions are [VERIFIED]; the dispositions are [RECOMMENDED] only.** `roles_and_authority.md:20-26` places "architecture, invariants, public contracts, genuine forks" in the Director's box, so each row below is a proposal with its evidence attached — not a ruling already made. Leadership confirms, amends, defers or rejects each.

Note also `DIRECTOR.md:54-63`: *"Silence on a decision means the existing decision stands."* A row left unruled does not default to the recommendation.

| ID | Conflict **[VERIFIED]** | Recommended disposition **[RECOMMENDED]** |
|---|---|---|
| **C1** | `admission_required`: `spec.md:1051` "capability-derived, no product-default exemption" vs `:1885` "exempts `vg-code-default`/`vg-code-lex`" — both marked FACT | `:1051` governs. An exemption that survives into the product path is precisely the false-completion route MS-TRUTH exists to close. Delete `:1885`. |
| **C2** | `progressive.py`: `spec.md:1896/1934/1871` and `technical.md:377` forbid creating it; `spec.md:2186/2334` specifies it as a new module | Forbidden. The 4-tier budget is **L4/L5 policy on the existing `ContextCompiler`**. Delete the `2334` ASCII tree; its tier token numbers move into the L4/L5 policy table (Phase 2). |
| **C3** | `SemanticTaskState`: four incompatible field sets (`spec.md:2204` dataclass, `:1928` `task_class`, `:504` cursor/lineage, `technical.md:614` recovery/budget fields) | `domain/task_state.py:210` is the single schema. Document the as-built; record the other three as drift, not as alternatives. |
| **C4** | Budget algebra: FH-D04/D05 (`spec.md:769-794`, four named dimensions, dispatch-time, refund bound, structural ceilings excluded) vs §23.2 (`:1581-1595`, abstract vector, issue-time, no dimensions) | FH-D04/D05 governs and is promoted from `[PROPOSAL]` to FACT — `kernel/budget.py:83` already implements it, and `Reservation:63` already excludes `depth`/`turns` as FH-D04 requires. §23.2 would permit summing structural ceilings, which FH-D04 itself names as defect `F-10`. Delete §23.2. |
| **C5** | Two `INV-DELTA` copies | Verbose wins — it carries "stale preimage" and the IndexPort enumeration the terse copy drops. Executed in **Phase 0b**, not 0a: this selects surviving law. |
| **C6** | Epoch membership: 7 components (`technical.md:569`) vs 4 (`spec.md:1910` `WorkspaceEpoch`) vs 8 (`:563`) | **These are two different epochs and the conflation is the bug.** `WorkspaceEpoch` = repository state (`session.py:1987`). `composition_epoch` = prompt/tool/policy identity (`compiler.py:289`). Name both, define both, state the relationship. |
| **C7** | Dialect section duplicated verbatim | Phase 0a — the two blocks are byte-identical, so nothing is chosen. |
| **C8** | T-83b wave placement, resolved by fiat in the handbook, never corrected in `spec.md` | Transfer the ruling into `spec.md`. A contradiction resolved only in the handbook re-litigates itself every time someone reads the spec. |
| **C9** | `S0–S12`, `I-6`, `N-06`, `F-10`, `C-05`, `K-23/K-25/K-26`, `G-01…G-12` referenced but defined nowhere | S0–S12 *are* defined — in `kernel/dispatch.py:3-21`. Promote that docstring into `technical.md` as the canonical table. Define or delete the rest; a referenced-undefined invariant is an escalation generator. |

---

## Phase 2 — Candidate contracts from accepted behavior **[RECOMMENDED]**

Fill empty contract slots only after triangulating governing invariants, accepted evidence and current implementation. **Source existence alone is insufficient.** Each accepted contract cites stable symbols and executable falsifiers so drift is detectable.

Route normative predicates and typed deltas to `spec.md`, implementation algorithms and recipes to `technical.md`, and accepted durable design to its existing architecture/reference owner. Reclaimed space in `technical.md` is available for handbook content, not as a substitute normative plane.

### 2.1 Appendix A — the four algorithms, actually written

Currently four empty headings labelled "normative for implementers."

- **A.1 Completion admission** — from `admission_gate.py:46` + `session.py:_admit_completion`. The conjunction is stated in prose twice, differently (`technical.md:1527`, `spec.md:2017`). Write it once as a predicate: mutation receipt ∧ current postimage/epoch ∧ tests collected ∧ tests executed ∧ `exit_code == 0` ∧ `executed_test_count > 0` ∧ tamper shield clean ∧ zero unresolved omissions ∧ non-stale index.
- **A.2 Turn compile** — `technical.md:556-596` already has working Python. Move it here.
- **A.3 2PC write** — from `transaction.py:52-185`. Phase 1 snapshot/preflight, Phase 2 staged `.tmp` + rename, `_restore` on any failure, `_tree_hash` before/after.
- **A.4 Campaign step** — `technical.md:1175-1290` already has labelled pseudocode. Move it.

### 2.2 The L1–L5 lattice — define it once, per layer

`### 3.2` is empty and **no layer is individually defined anywhere.** Source of truth is `agency/context/layers.py:42`.

Critical correction: **the lattice is L1–L5, not L0–L5.** `L0` is an unrelated overloaded term meaning the smoke-test measurement rung (`spec.md:2087`). Fix the terminology, or the first developer to implement "L0" invents a layer.

Per layer: membership rule, ordering, cache/prefix status, serialization. Plus `LAYER_ORDER:53`, `PREFIX_LAYERS:60` (L1–L3 cached), `BREAKPOINT_LAYERS:67` (L5 deliberately excluded — say *why*), `PINNED_L4_SOURCES:80`, `PINNED_L5_SOURCES:98`, `CAPABILITY_PREFIX_CEILING:104`.

### 2.3 Both epochs, per C6

`WorkspaceEpoch` (`session.py:1987`, `:1940`) and `composition_epoch` (`compiler.py:289`, `:162`, `_declared_identity:604`) — membership, derivation, invalidation trigger, and the three refusal gates in `packet.py:167/186/194`.

### 2.4 Bounded protocol recovery state machine

`### 6.3` is empty. Source: `protocol_recovery.py` — `ProtocolRecoveryState:299`, `decide_recovery:220`, `ProtocolRecoveryPolicy:714`, `classify:776`. Write states, transitions, attempt bounds, terminal conditions, and the encode/decode contract that survives suspend/resume (`:470/:474`).

### 2.5 Consolidated error registry

`spec.md §15` is a two-line pointer. ~25 distinct error codes are in use across the corpus with no registry: `ENVELOPE_OVERCOMMIT`, `BUDGET_DENIED`, `PROMOTION_CONFLICT`, `GENERATION_STALE`, `NODE_LEASE_CONFLICT`, `INDEX_UNBOUND`, `VACUOUS_ORACLE_REJECTED`, `CONTEXT_BUDGET_EXCEEDED`, and the rest. One table: code, raising site, meaning, caller guidance.

### 2.6 Port signatures

`spec.md:1212-1231` names eight ports with **zero method signatures**. The real ports are in `vanguard/packages/ports/` as typed `Protocol` classes. Replace the name list with a table pointing at each declaration, and delete the ports that were speculative — `:1229` preserves "both designs" where one of the two is an empty heading.

---

## Phase 3 — Candidate capability plane **[RECOMMENDED]**

The three surfaces named in the objective. Each builds on shipped code.

### 3.1 Greenfield multi-file editing

Present: `transaction.py`, `hunks.py`, `multi_file_completeness.py:164`, `tamper_shield.py:33`, `analysis.py:57`.

**Proposed contract:** define the greenfield oracle-vacuity protocol. `spec.md:2287-2297` gives five prose stages whose load-bearing predicate — *"if it passes on stubs, it is vacuous and rejected"* — has no formal form and no detector, though `VACUOUS_ORACLE_REJECTED` is already a code. Also resolve `spec.md:2283`, *"every imported symbol from local modules must resolve"*, which is unimplementable as written (no definition of "local module", no resolution algorithm, no conditional-import behaviour).

### 3.2 Long sessions and large context — the `horizon` preset **[DECISION]**

Present: compaction strategies, checkpoints, sigma fold, `InferenceMeter:150`.

**[RECOMMENDED] — the preset does not go in `code-default`.** `/packs/code-default/presets.json` holds the three frozen presets. D-6 F1 pins manifest and cost identity for the control subject; adding a fourth entry changes that file's bytes and risks invalidating the frozen arm. **Create `packs/code-horizon/` as a separate pack.** `code-default` bytes stay untouched and the control subject survives.

**Recommended starting envelope — experimental values, not locked architecture.** Lock the *invariants* (mandatory compaction, sigma durable across restart, separate-pack boundary); treat every number below as provisional until long-context qualification produces evidence:

```
horizon:  usd_micros 2_000_000   ($2.00)
          turns      200
          tokens     5_000_000
          context_window_tokens 200_000
          compaction MANDATORY (StructuredConsolidateStrategy)
          checkpoint cadence: every N turns, sigma durable across restart
```

Leadership should decide whether to lock what is currently one sentence (`spec.md:1315`, *"Checkpoints remain disposable caches with proof obligations"*): format, cadence, invalidation, and what "proof obligation" means — informed by `checkpoints.py:313` and acceptance evidence.

### 3.3 Planner and worker agents

**Present and working, contrary to the documents.** `M6_SPAWN_ACTIVE = True` at `delegation.py:67`; `topology.py` compiles declarative graphs with cycle-checking `_validate_graph:274`, authority refusal `_reject_authority:173`, attenuation validation `_validate_attenuation:436`; three frozen topologies at `qualification_topology:343` — sequential planner→implementer→verifier, reviewer-in-loop, parallel-investigators.

Recommended decisions for leadership review:
- The topology contract from `topology.py`, and the director-has-no-mutating-verbs rule `verbs(director) ∩ MutatingVerbs = ∅` (`spec.md:850`), whose falsifier is already stated: grep the campaign client for an `EpisodeEngine` construction and the count must be zero.
- **[DECISION] `CoordinationPlan` versus the as-built `Topology`.** An earlier revision of this packet ruled that `CoordinationPlan` "will not be created." That overstepped: `milestones.md` **W-OCT-2 / OCT-02** names *"Declarative CoordinationPlan DAG"* as a terminal acceptance boundary, and MS-CAMPAIGN carries it too. Overturning a milestone's stated acceptance boundary is leadership's call, not this packet's.
  *The argument for collapsing them:* `Topology` + `RunPlanExtension:113` already compiles declarative graphs with cycle-checking and attenuation validation; a second plan type risks the duplicate planner `DIRECTOR.md:165` forbids.
  *The argument against:* `CoordinationPlan` carries per-mille budget shares and named merge policies (`CONCAT`/`FIRST_COMPLETE`/`SYNTHESISE`/`UNANIMOUS`) that `Topology` does not express, and per-mille allocation appears nowhere in the corpus today.
  **Leadership decides: extend `Topology`, or admit `CoordinationPlan` as a distinct type, or amend W-OCT-2.**
- Merge policy, already correctly stated at `technical.md:1292` and worth making normative: *merge is a candidate, not a vote.* Exterior verifier verdict only — never role agreement, never tournament rank.
- **Gap to disposition:** no per-worker git-worktree isolation is wired into spawn. `git worktree` exists only as a `GitEnvironment` constructor option (`git.py:153-168`); nothing in `delegation.py`/`child_runtime.py` creates one per child. Before parallel mutation is claimed, leadership should decide the isolation invariant and, if accepted, authorize the Senior to create a task row.
- **Fix stale assertions:** `test/contracts/test_adr0090_child_fold.py:13` claims `M6_SPAWN_ACTIVE = False`. `test/runtime/test_coding_coordinator.py` is a retired empty suite, so "coding coordinator" has no live test.

---

## Phase 4 — Measurement decisions **[RECOMMENDED]**

### 4.1 Wilson bound — write the formula

`95% Wilson lower bound ≥ 0.40` is the release gate. It is referenced twice (`spec.md:75`, `technical.md:1300`) and **the formula is written nowhere.** Leadership should decide and record the expression, one- versus two-sided interpretation (D-6 F7 says two-sided), continuity correction, and denominator when `U` undeterminable outcomes exist. `technical.md:1300` reports `[R/N, (R+U)/N]` as descriptive bounds and explicitly says they are *not* a confidence interval, but never says what Wilson consumes.

### 4.2 False-completion veto — define the detector

Named as a release gate independent of pass rate at `spec.md:65/75/131` and D-6 F7 requires **zero observed**. There is no detector, no predicate, no evidence schema, no threshold. A gate with no detector cannot return zero honestly — it returns zero because nothing looked. Lock the predicate, the evidence schema, and the upper confidence bound on the unobserved rate that "zero observed at n=30" actually supports.

### 4.3 Promote the budget algebra

FH-D04/D05 (`spec.md:769-794`) is the best-specified content in the corpus — equations, induction proof, refund bound, structural-ceiling exclusion — and it is marked `[PROPOSAL]` while `kernel/budget.py` already implements it. Promote to FACT per C4.

---

## Phase 5 — Proposed gate simplification **[RECOMMENDED]**

Only after Phases 1–4 land. Advisory files only (`AGENTS.md:317`).

1. **`DEVS.md`** — add a contract index: capability → locked section → implementing module → falsifier. `README.md:91`: *"A row that cannot be started without reading all five documents is a malformed row."*
2. **RUN-04 restated** against the now-existing contracts: a locked contract is a decision already made. A developer implementing to a locked contract does not escalate.
3. **Escalation triggers unchanged.** `roles_and_authority.md:45-57` lists six. `:59-60`: *"The value of this list is entirely in what it excludes. Each addition costs a fortnight of autonomy."* This packet proposes no addition or removal. Gate reduction should come from clearer contracts, not from silently deleting safeguards.
4. **The acceptor constraint — open fork.** Non-author acceptance with a pool of three can deadlock: B authors T-131.3/4/7 and T-26b; A is excluded wherever it authored the accepted delta; C cannot accept C/B integration. `tasks.md` records an external staffing blocker. Leadership must confirm whether it is eligible and sufficiently independent to accept at batched boundaries under `roles_and_authority.md:72-88`; otherwise it must name an uninvolved qualified acceptor. The Senior records the independence basis either way.

---

## Phase 6 — Proposed closeout **[DECISION]**

### 6.1 Sweep `.draft/`

**Not before Phase 1 completes.** `.draft/` holds the only recoverable record of the prior leadership decisions that the C1–C9 rulings cite — deleting it mid-transfer destroys the provenance those rulings depend on. It sits outside `docs/`, so it costs nothing against the linters and there is no urgency; `AGENTS.md:267` already makes it non-authoritative ("do not infer authorization from archived proposals … or unused `.draft/` triad files").

If leadership accepts the cleanup, the Senior should preserve necessary provenance while removing redundant working copies after their durable content is transferred. The recommendation is to retain this decision packet and `AETHER_VANGUARD_LEADERSHIP_IMPLEMENTATION_GUIDE.md`, retire dated handoffs (`130926_*`) whose content is demonstrably represented in canonical files, and leave `audit/`, `logs/`, `quick_benchs/`, and `todo/` untouched unless separately reviewed.

### 6.2 Cut 0.9.4 **[DECISION]**

Whether a 0.9.4 framework cut is justified at all, and its exact acceptance predicate, is leadership's call. **If** authorized, the recommendation is to cut after Phases 0–4, defined as *"execution plane locked + `code-horizon` pack exists."* A version bump that precedes the contracts just renames the current ambiguity.

**Numbering collision — resolve explicitly in the commit message.** Two schemes run in opposite directions and the framework number is already *higher* than the release target:

| Line | Current | Next |
|---|---|---|
| Framework (aether) | v0.9.3 | **v0.9.4** ← this cut |
| Product release | M-9 beta `0.9.0b1` → M-10 `0.9.0` | **unchanged; still blocked on M-8** |

State which line `0.9.4` refers to, or the first person who reads it will conclude beta shipped. M-9 remains `UNAUTHORIZED` behind M-8 under invariant G-2; this cut does not touch that.

---

## Critical files

| File | Change |
|---|---|
| `docs/execution/main/technical.md` | Proposed Phase 0 reclaim; handbook target for accepted implementation algorithms and recipes |
| `docs/execution/main/spec.md` | Proposed dedup/renumber plus leadership-approved normative dispositions |
| `docs/execution/main/tasks.md` | Senior records accepted status cleanup and any newly authorized task rows |
| `docs/execution/main/milestones.md` | **1 line headroom** — touch only if a status token changes |
| `docs/execution/management/state_of_play.md` | Regenerate; re-pin |
| `docs/execution/guidelines/*.md` | Re-pin; contract index (**9 lines headroom** in `DIRECTOR.md`) |
| `justfile` | Leadership chooses `docs-check`, `check` or `verify` after measured-cost evidence; C/T-132 owns the live lease |
| `packs/code-horizon/` | **Proposed option** — create only if leadership accepts the boundary and the Senior assigns a packet |

**Sources to inspect alongside invariants and acceptance evidence:** `agency/context/layers.py`, `compiler.py`, `compaction.py`, `packet.py`; `adapters/environment/transaction.py`, `hunks.py`; `runtime/session.py`, `checkpoints.py`, `task_state.py`, `inference_meter.py`, `delegation.py`, `topology.py`; `agency/episode/admission_gate.py`, `protocol_recovery.py`, `engine.py`; `kernel/dispatch.py`, `budget.py`; `vanguard/packages/ports/*.py`.

---

## Verification

**Phase 0a** (must be its own commit)
- `just docs-check` — metadata, links, markdownlint
- `python3 tools/linters/check_markdown_links.py` — confirms the anchor deletion broke nothing
- `python3 tools/linters/check_doc_budgets.py` — record the actual remaining overages; 0a is not expected to resolve 0b-dependent budgets
- `python3 tools/linters/check_execution_truth.py` — five files intact, milestone status vocabulary preserved
- Blob comparison receipt: no semantic delta

**Phases 1–4**
- Run focused checks for each changed contract and `just check` during incremental work; run `just verify` once on the final exact acceptance subject unless a specific risk justifies another full run
- Every accepted contract cites stable symbols or section anchors; use line numbers only as review-time locators
- `check_doc_metadata.py` — `id` and `canonical_for` stay globally unique
- Re-pinned blobs verified through the prescribed generator, not string substitution

**Phase 3 drift checks, if the corresponding changes are authorized**
- `test/contracts/test_adr0090_child_fold.py:13` corrected to `M6_SPAWN_ACTIVE = True`
- Director-verb falsifier: grep campaign client for `EpisodeEngine` construction, expect zero
- Worktree isolation gap carries a task row and a falsifier before any parallel-worker claim

**Standing boundaries — unchanged by this packet**
- No provider calls, no paid runs, no control freeze, no benchmark score, no SOTA claim
- T-26 UNFROZEN, T-27 unauthorized, MS-CONTROL OPEN
- D-6 closed at F1–F7; **an eighth predicate requires an explicit successor ruling.** A documentation packet is exactly where a new prerequisite can be smuggled in — this one proposes none.

---

## Assumptions most likely to be wrong

1. **That the as-built code is correct enough to inform a contract.** Phase 2 must not convert implementation into law without acceptance evidence. A defect in `admission_gate.py`, for example, must remain a defect rather than becoming a documented invariant. *Exposed by:* the F5 row dispositions, which are open for exactly these seams.
2. **That ~633 reclaimed lines is enough.** Nine contract sections plus the math may not fit. *Exposed by:* `check_doc_budgets.py` at Phase 2 close. If it fails, the overflow is a ceiling raise with justification in the commit (`check_doc_budgets.py:37`) — **not** a sixth file.
3. **That contracts are what is actually blocking autonomy.** If throughput stays flat after Phase 5, reviewer capacity or another operational constraint may be dominant; leadership must measure that rather than assuming this packet is sufficient.
