# Project State and Architecture Decision Brief — Execution Plane

**Purpose.** Give leadership verified state, existing constraints, unresolved contradictions, and consequential forks, so that leadership can decide product architecture and the Senior can convert accepted decisions into canonical text and bounded developer packets.

**This brief authorizes nothing.** It contains no rulings. Recommendations, where any exist, are confined to Appendix A and carry no authority.

---

## 1. Provenance and confidence

Repository rule applied throughout: *indexes route; canonical documents constrain; source implements; tests falsify; ledger and benchmark artifacts demonstrate observed behavior* (`AGENTS.md:132-137`).

| Field | Value |
|---|---|
| Subject SHA | `8df561b5` |
| Branch | `feat/aether-framework-electroweak-canonical-agents` |
| Worktree | Clean at session start; no product-code change made by this brief |
| Inspection date | 2026-09-14 (brief compiled 2026-09-15) |
| Paid/provider calls | None |

### 1.1 Commands actually executed for this brief

```
git rev-parse --short HEAD
git hash-object docs/execution/main/{tasks,spec,milestones,technical}.md
wc -l docs/execution/main/*.md docs/execution/**/*.md
sed -n over technical.md ranges; grep -c over the retired block
grep -rn "technical\.md#" --include=*.{md,py,yml,yaml,json}
grep -rn "parallel architecture document|anti-sprawl" AGENTS.md CLAUDE.md docs/execution/
grep -n over tasks.md for READY/ACTIVE status tokens
cat tools/linters/kernel-tcb-budget.json
cat vanguard/packages/runtime/workspace.py
grep -n "worktree|workspace" vanguard/packages/runtime/child_runtime.py
find/ls over docs/execution/ and .draft/
```

No test suite, benchmark, linter or LDA command was executed by this brief.

### 1.2 Evidence tiers — what is directly observed versus reported

| Tier | Content | Confidence |
|---|---|---|
| **Directly observed** (commands above) | Blob/pin mismatch; `technical.md` line counts and retired-block composition; absence of inbound anchors; TCB budget constants; `workspace.py` contents; absence of worktree references in `child_runtime.py`; `AGENTS.md` anti-sprawl text; conflicting status tokens in `tasks.md` | High |
| **Read-agent findings** (file:line citations in §3, §4) | Structural map of `spec.md`/`technical.md`/`backlog.md`; the C-series contradictions; linter inventory and doc-budget ceilings; implementation sites in `vanguard/` | Medium — cited but not independently re-read line by line |
| **Operator-reported, not executed here** | Test suite results (kernel 102, agency 316, packs 92), boundary and TCB linter passes, LDA index health (12,005 symbols / 90,009 relations / 2,139 files), benchmark outcomes | **Unverified by this brief.** Treat as operator receipts, not as evidence this brief produced |

### 1.3 Known stale or unverified evidence

- The four `docs/execution/main` blob pins in `state_of_play.md`, `DEVS.md` and `DIRECTOR.md` **do not match the current tree** (§3.1). By their own clauses, `state_of_play.md`'s snapshot is self-invalidated and both guideline files' assignment sections are self-declared stale.
- `test/contracts/test_adr0090_child_fold.py:13` asserts in prose that `M6_SPAWN_ACTIVE = False`; the source reads `True` (`delegation.py:67`).
- `test/runtime/test_coding_coordinator.py` is a retired suite returning no tests.
- `dev_context_logs/*.json` carries locators against the pre-move path `docs/execution/technical.md`, which no longer exists.
- Line numbers cited in this brief are **review-time locators, not identity**. Prefer the named symbols.

### 1.4 Limitations

This brief did not execute tests, measure linter cost, inspect ledger receipts, or verify acceptance provenance for any claim recorded as ACCEPTED in `tasks.md`. It cannot establish whether as-built behavior is *correct*, only that it exists. Statements about parallel-safety of future edits are inspection, not proof.

---

## 2. How to read this brief

| Category | Meaning |
|---|---|
| **VERIFIED STATE** | Directly observed on subject `8df561b5`. Check it; do not rule on it. |
| **EXISTING AUTHORITY** | An already accepted invariant or decision, cited. Stands unless leadership supersedes it. |
| **CONTRADICTION** | Two or more authoritative statements that cannot both hold. Recorded without disposition. |
| **OPEN DECISION** | A fork this brief does not close. |
| **EVIDENCE NEEDED** | Insufficient basis for any decision yet; the missing evidence is named. |

Contradiction labels `C1`–`C9` and decision labels `OD-1`–`OD-12` are **brief-local identifiers**, not repository IDs. They exist so leadership can reference rows; they carry no authority and should not enter canonical documents under these names.

---

## 3. Current execution truth

### 3.1 Documentation state — VERIFIED STATE

| Item | Observation |
|---|---|
| Blob pins | All four `main/` blobs differ from the values pinned in `state_of_play.md` and both guideline binding blocks |
| `technical.md` | 2,466 lines. Lines 1655–2466 (812 lines) are a retired block containing 11 lines of prose and ~795 bare headings with no bodies. Original text recoverable at `git show 001911e3:docs/execution/technical.md` |
| Inbound anchors into that block | Zero. The single inbound anchor link in the repository (`spec.md:605`) targets a heading in the live section |
| `tasks.md` status tokens | Rows carrying `READY` at lines 287–300, 1520, 1613, 1650 and 1703 conflict with the dispositions recorded at lines 85–109 of the same file. A precedence clause exists at line 40 |
| Empty normative slots in `technical.md` | `Appendix A` (A.1 completion admission, A.2 turn compile, A.3 2PC write, A.4 campaign step), `3.2 L1–L5 context architecture`, `6.3 bounded protocol recovery state machine`, and all `5.x` formal-model sections carry headings with no bodies |

### 3.2 Doc budgets — read-agent finding, not re-measured

`tools/linters/check_doc_budgets.py` carries per-file ceilings. Reported measurements: `spec.md` 2,390/2,150; `tasks.md` 2,500/1,700; `technical.md` 2,466/2,300; `milestones.md` 519/520; `backlog.md` 753/800. The gate is blocking in CI (`ci.yml`, `clean-candidate.yml`) and runs in neither `just check` nor `just verify`. `check_stale_paths.py` has the same placement. Raising a ceiling is governed: *"Lowering a value is always allowed; raising one is a governance decision and must be justified in the commit"* (`check_doc_budgets.py:37-38`).

### 3.3 Task board state — as recorded in `tasks.md`

| State | Rows |
|---|---|
| ACCEPTED | T-134, T-136, T-26a, T-52 |
| ACCEPTED, provenance unreconciled | T-75/T-76, T-78, T-83b, T-138, T-139 — the board names a "final integration subject" without a linked exact SHA, evidence digest or non-author disposition |
| LANDED, independent acceptance pending | T-130, T-135, T-131.6, T-140 |
| REOPENED | T-133 (Q-01 correction), T-51 |
| BLOCKED | T-51, T-26b, T-27 |
| UNFROZEN | T-26 |
| Milestones | MS-INSTRUMENT `CLOSED` (harness subject), MS-RESUME `CLOSED`, MS-TRUTH `MECHANISM`, MS-SEE / MS-CHANGE / MS-CONTROL `OPEN` |

### 3.4 Authorized developer queue — unchanged by this brief

| Owner | Authorized work |
|---|---|
| A | T-131.8 on its exclusive lease; eligible non-author reviews |
| B | Outstanding reviews (T-130, T-135, T-131.6, T-140) and acceptance-record reconciliation; then T-131.3 → T-131.4 → T-131.7 on released leases |
| C | T-133 non-probe work → T-132 → T-137 → hermetic T-51 local readiness |

This queue proceeds under existing authority. Nothing in this brief is a prerequisite for it.

### 3.5 Known lease and serialization points — VERIFIED STATE

- `tasks.md` is Senior-owned and written on every status or lease change; it is the single documentation/development serialization point.
- `justfile` is inside C's T-132 lease, so any linter-placement decision (OD-11) routes through C, not through a documentation edit.
- `tools/diagnostics/write_landing_probe.py` sits in T-133's declared inventory but is gated on B's T-130 disposition.
- `vanguard/packages/runtime/session.py` is held by C until T-140 release and is required by B for T-131.3.

### 3.6 External blockers — EVIDENCE NEEDED

None of the following is resolvable by any documentation or code change:

| Blocker | Blocks |
|---|---|
| Independent curator not appointed | T-51 admission |
| Sealed store not provisioned | T-51 admission |
| Fresh 30-member corpus not produced or validated | T-51, F3 |
| Run and aggregate-resource authorization absent | T-27, F7 |
| Non-author acceptor availability | Every leaf requiring independent disposition (see OD-7) |

`tasks.md` additionally records that curator/store is **not** the sole T-51 blocker: T-133 guard/authority correction and T-132 discovery remain local work.

### 3.7 Work that can safely continue during deliberation

A's T-131.8, B's outstanding reviews and reconciliation, and C's T-133 non-probe files are all authorized, lease-disjoint from documentation, and independent of every decision in §5.

---

## 4. Contradictions — recorded without disposition

Each row is a **CONTRADICTION**: two authoritative statements that cannot both hold. No disposition is proposed here. Leadership rules; the Senior transfers.

| ID | Statement A | Statement B | Why it blocks implementation |
|---|---|---|---|
| **C1** | `spec.md:1051` — `admission_required` is capability-derived; no product-default exemption. Marked FACT | `spec.md:1885` — exempts `vg-code-default` / `vg-code-lex`. Also marked FACT | Determines whether the product path can complete without admission |
| **C2** | `spec.md:1896/1934/1871`, `technical.md:377` — do not create `progressive.py`; tiering is L4/L5 policy on the existing compiler | `spec.md:2186/2334` — specifies `agency/context/progressive.py` as a new module with tier token budgets | Determines whether a second context compiler exists |
| **C3** | `domain/task_state.py:210` — one `SemanticTaskState` schema | `spec.md:2204` dataclass, `:1928` (`task_class`), `:504` (cursor/lineage/reducer), `technical.md:614` (recovery/budget fields) — four incompatible field sets | No implementer can determine the durable state shape |
| **C4** | `spec.md:769-794` FH-D04/D05 — four named dimensions, dispatch-time, refund bound, structural ceilings excluded. Marked `[PROPOSAL]` | `spec.md:1581-1595` §23.2 — abstract vector, issue-time, no dimension list | §23.2 permits summing `depth`/`turns`, which FH-D04 names as defect `F-10` |
| **C5** | `spec.md:1037-1043` — terse `INV-DELTA-1..5` | `spec.md:2192-2196` — verbose `INV-DELTA-1..5` carrying "stale preimage" and an IndexPort enumeration requirement the terse copy omits | The two define different invariants under one identifier |
| **C6** | `technical.md:569` — epoch of 7 components | `spec.md:1910` `WorkspaceEpoch` of 4; `spec.md:563` of 8 | Unclear whether these are one epoch or several; epoch identity gates completion |
| **C7** | `spec.md:1915-1917` dialect section | `spec.md:1940-1942` — byte-identical duplicate | Duplication only; no semantic divergence observed |
| **C8** | `technical.md:1531-1534` — T-83b wave placement resolved by fiat, "the dependency governs" | `spec.md` — uncorrected | The contradiction re-presents itself to every reader of the spec |
| **C9** | `kernel/dispatch.py:3-21` defines S0–S12 | `S0–S12`, `I-6`, `N-06`, `F-10`, `C-05`, `K-23/K-25/K-26`, `G-01…G-12` are referenced across the five files but defined in none of them | Referenced-undefined invariants cannot be implemented or falsified |

---

## 5. Open decisions

Each decision states present state, existing constraints, viable options, trade-offs, and evidence needed. **No option is preselected.**

### OD-1 — Threshold for converting as-built behavior into a durable contract

- **Present state.** Substantial behavior exists in `vanguard/` with no corresponding written contract: context compilation and compaction, multi-file 2PC, session/resume and sigma fold, completion admission, delegation and topology. Meanwhile the slots labelled "normative for implementers" are empty (§3.1).
- **Existing constraints.** `AGENTS.md:132-137` — source implements, tests falsify, receipts demonstrate; none of these alone constrains. `AGENTS.md:335` — feature extensions are expressed as deltas in `spec.md` and promoted to `docs/architecture/` **upon milestone gate passage**. MS-SEE, MS-CHANGE and MS-CONTROL are OPEN.
- **Viable options.** (a) Promote only behavior with independent acceptance over an exact subject. (b) Promote behavior with focused falsifiers even absent milestone closure, marked as provisional. (c) Promote nothing until the relevant milestone closes, leaving the slots empty. (d) A per-surface split.
- **Trade-offs.** (a) is safest and leaves most slots empty for now. (b) unblocks developer autonomy but risks enshrining defects as invariants — F5's eight RUN-09 defect rows are open against exactly these seams. (c) preserves the current escalation load indefinitely.
- **Evidence needed.** For each candidate surface: an exact subject, a non-author disposition, and the falsifier that would fail if the behavior were wrong.

### OD-2 — Semantic owner for each accepted result

- **Present state.** Contracts, algorithms, status and gates are interleaved across the five files; a second self-contained document sits inside `spec.md` at 2174–2390.
- **Existing constraints.** `README.md:26-35` ownership table; `AGENTS.md:309-314` five-file definition; `AGENTS.md:335` — `technical.md` is a handbook, **not** a second architecture plane; `README.md:96` — no sixth canonical document.
- **Viable options.** (a) Normative predicates to `spec.md`, algorithms to `technical.md`, accepted durable design to `docs/architecture/`. (b) Concentrate contracts in `technical.md` for proximity to implementers. (c) Per-contract routing decided individually.
- **Trade-offs.** (b) risks the second-architecture-plane failure `AGENTS.md:335` names. (a) requires splitting some contracts across two files. (c) is most accurate and most expensive.
- **Evidence needed.** None external; this is a governance choice.

### OD-3 — Disposition of contradictions C1–C9

- **Present state.** §4.
- **Existing constraints.** `roles_and_authority.md:20-26` assigns invariants and public contracts to the Director. `DIRECTOR.md:54-63` — *"Silence on a decision means the existing decision stands"*, so an unruled row does not resolve by default.
- **Viable options.** Per row: rule for A, rule for B, rule a third form, or defer with named evidence.
- **Trade-offs.** C1, C3, C4 and C6 govern runtime behavior and block implementation while open. C5 changes an invariant's content. C7 is duplication only. C2, C8, C9 are resolvable without runtime consequence.
- **Evidence needed.** For C1 and C4, whether current product behavior already follows one branch — determinable from the F5 dispositions and the T-131 rows.

### OD-4 — How long-horizon behavior is isolated from frozen control identity

- **Present state.** `/packs/code-default/presets.json` declares `fast`, `balanced` and `max`. No long-horizon configuration exists. Compaction strategies, checkpointing, sigma fold and inference metering exist and have not been exercised at long-horizon scale.
- **Existing constraints.** D-6 F1 pins manifest, prompt/tool bytes, model/provider/registry, sampling/serializer/context/recovery policy, environment and cost identities for the control subject. `spec.md:496` records the three preset envelopes. `spec.md` RUN-04 forbids a developer changing presets unilaterally.
- **Viable options.** (a) A separate pack. (b) A fourth preset inside `code-default`. (c) A runtime profile orthogonal to packs. (d) A separate manifest reusing the existing pack. (e) Another boundary leadership designs.
- **Trade-offs.** (b) changes `code-default` bytes and may invalidate the frozen arm's identity under F1. (a) duplicates pack scaffolding and raises the question of which pack owns shared policy. (c) introduces a configuration axis that does not exist today. The identity risk in (b) is asserted from F1's wording and **has not been empirically confirmed**.
- **Evidence needed.** Whether adding a preset entry actually perturbs the pinned manifest identity — determinable by computing the manifest digest before and after a candidate edit, which this brief did not do. Also: measured behavior of the existing compaction strategies at long-horizon scale, which does not exist.

### OD-5 — `Topology` versus `CoordinationPlan`

- **Present state.** `runtime/topology.py` compiles declarative graphs with cycle-checking, authority refusal and attenuation validation, and carries three frozen topologies (sequential planner→implementer→verifier, reviewer-in-loop, parallel-investigators). No type named `CoordinationPlan` exists in the source.
- **Existing constraints.** `milestones.md` W-OCT-2 / OCT-02 names *"Declarative CoordinationPlan DAG"* with per-mille budget shares (∑ ≤ 1000) and merge policies `CONCAT` / `FIRST_COMPLETE` / `SYNTHESISE` / `UNANIMOUS` as a terminal acceptance boundary; MS-CAMPAIGN carries it. `DIRECTOR.md:165` — prefer extending existing mechanisms over a second planner. `spec.md` RUN-10 — one canonical EpisodeEngine, no second agent loop.
- **Viable options.** (a) Extend `Topology` to cover W-OCT-2's properties and amend the milestone. (b) Admit `CoordinationPlan` as a distinct type at the campaign layer. (c) Defer until MS-CONTROL closes, since MS-CAMPAIGN is gated on it.
- **Trade-offs.** Per-mille allocation and the four named merge policies appear nowhere in the corpus today; `Topology` does not express them. (a) requires amending a stated milestone boundary. (b) risks the duplicate-planner failure. (c) costs nothing now but leaves the capability roadmap ambiguous.
- **Evidence needed.** Whether per-mille shares and the four merge policies are still wanted, or are residue from a superseded design.

### OD-6 — Isolation invariant required before parallel mutation

- **Present state — VERIFIED.** `vanguard/packages/runtime/child_runtime.py` contains no worktree or workspace reference. `runtime/workspace.py` is a 21-line re-export shim over `domain/workspace.py`. `git worktree` appears only as a `GitEnvironment` constructor option (`git.py:153-168`) that nothing in the delegation path invokes. `EpisodeEngine.spawn` destroys the child workspace in a `finally` block, but the workspace is whatever `workspace_factory` supplies.
- **Existing constraints.** Kernel S11-before-S12 release/emit ordering. One-writer-per-workspace (`spec.md:1047`, `:1358-1374`) is stated in prose with no acquisition protocol, fencing or violation detection for the workspace (fencing exists only for campaign nodes).
- **Viable options.** (a) Require per-child filesystem isolation before any parallel mutating topology is enabled. (b) Permit parallel mutation with a serialization mechanism other than isolation. (c) Restrict parallel topologies to read-only roles, which the existing specialist manifests already are. (d) Defer, since no parallel mutating topology is currently authorized.
- **Trade-offs.** (d) is honest today but leaves the planner/worker capability claim unsupported. (c) preserves current safety and limits the capability. (a) is the strongest guarantee and the largest change.
- **Evidence needed.** Whether any currently authorized path can run two mutating children concurrently — determinable by inspecting the scheduling in `runtime/root.py:348-372`, which this brief did not trace to completion.

### OD-7 — Acceptance authority

- **Present state.** Non-author acceptance is required. The pool is three: B authored T-131.3/4/7 and T-26b; A is excluded wherever it authored the delta under acceptance; C cannot accept C/B integration. `tasks.md` records an external staffing blocker.
- **Existing constraints.** `roles_and_authority.md:72-88` — review independence is per-change, not per-role-label; the Senior records the independence basis. `DIRECTOR.md:37-43` — the Director does not approve every edit; strategic review and ordinary code review are different gates. `roles_and_authority.md:59-60` — adding an escalation trigger is a CEO decision.
- **Viable options.** (a) Leadership accepts at named evidence boundaries, with the Senior recording independence per change. (b) An uninvolved qualified reviewer is appointed. (c) Rotate authorship so that no developer authors work it must later accept. (d) Accept sequentially and absorb the throughput cost.
- **Trade-offs.** (a) costs no hire but places the Director close to routine review, which `DIRECTOR.md:37-43` cautions against. (b) resolves cleanly and requires staffing. (c) constrains lane assignment. (d) preserves every guarantee and serializes the queue.
- **Evidence needed.** None. This is a role-authority decision only leadership can make.

### OD-8 — Capability direction and sequencing

- **Present state.** All three developers are in the integrity lane. Capability surfaces with no current owner include: worker isolation (OD-6), long-horizon configuration (OD-4), greenfield oracle vacuity (no detector behind the existing `VACUOUS_ORACLE_REJECTED` code), the false-completion detector (OD-9), memory and skills (MEM-01/MEM-02/T-56), specialist treatments (MS-SPECIALIST), CAS promotion (MS-CAS), and external evaluation (MS-EVAL).
- **Existing constraints.** The 2026-09-13 CEO directive decoupled capability from MS-CONTROL. `milestones.md` Leadership disposition (2026-09-12) orders these: single-controller qualification first, then governed memory and skills, then recoverable workspace and bounded specialist, then external evaluation, then campaign director. Several are `[PROPOSAL]` gated on MS-CONTROL.
- **Viable options.** (a) Hold all capacity in the integrity lane until MS-CONTROL closes. (b) Split capacity between integrity and one or more capability surfaces. (c) Reprioritize the 2026-09-12 ordering.
- **Trade-offs.** (a) is the most conservative and is bounded by acceptor availability and external blockers, both of which are outside developer control. (b) requires leadership to select surfaces and accept that capability advances without a control baseline. (c) supersedes a standing leadership disposition.
- **Evidence needed.** Whether the integrity lane's throughput is actually acceptor-bound — measurable from elapsed time per leaf between LANDED and accepted, from existing handoffs.

### OD-9 — Measurement semantics

- **Present state.** `95% Wilson lower bound ≥ 0.40` is referenced at `spec.md:75` and `technical.md:1300`; the formula appears nowhere. `technical.md:1300` reports `[R/N, (R+U)/N]` as descriptive bounds and states they are not a confidence interval, without saying which denominator feeds Wilson. The false-completion veto is named as a release gate at `spec.md:65/75/131` and required at zero observed by D-6 F7; no detector, predicate, evidence schema or threshold exists.
- **Existing constraints.** `roles_and_authority.md:20-26` assigns statistical meaning to the Director. D-6 F7 specifies two-sided. `roles_and_authority.md:62-69` reserves control thresholds to the CEO.
- **Viable options.** For Wilson: fix one- versus two-sided, continuity correction, and the treatment of `U`. For false completion: define a detector predicate and evidence schema, or replace "zero observed" with a stated upper confidence bound on the unobserved rate, or both.
- **Trade-offs.** A gate with no detector returns zero because nothing looked, which is not the same as zero false completions. Defining the detector after the corpus exists risks fitting it to observed data.
- **Evidence needed.** None to define the semantics. The detector's false-positive behavior needs evidence before it gates a release.

### OD-10 — Which semantics survive documentation consolidation

- **Present state.** §3.1 and §4. `spec.md` additionally contains duplicate top-level numbering (`## 0.`, `## 6.`, `## 22.`, `## 23.` each twice) and a second self-contained document at 2174–2390 whose Python dataclasses are the only typed contracts in the corpus.
- **Existing constraints.** `README.md:108-110` — a topology move is isolated from semantic edits and carries a blob-comparison receipt; a commit mixing new law, task changes and path migration cannot claim content untouched. `check_markdown_links.py` validates heading anchors, so renaming a heading breaks inbound links. `check_execution_truth.py` hard-codes the five filenames and the milestone status vocabulary.
- **Viable options.** Per duplicate pair: keep A, keep B, merge, or retain both with an explicit precedence note.
- **Trade-offs.** Deleting the wrong copy silently changes an invariant (C5 is exactly this). Retaining both preserves the current escalation source.
- **Evidence needed.** For each pair, which version current implementation and accepted receipts actually follow.

### OD-11 — Placement of the two CI-only linters

- **Present state — VERIFIED.** `check_doc_budgets.py` and `check_stale_paths.py` run in `ci.yml` and `clean-candidate.yml` with no `continue-on-error`, and in neither `just check` nor `just verify`. Local green therefore does not predict CI green.
- **Existing constraints.** `justfile` is inside C's T-132 lease. `just check` is the in-loop gate; `just verify` is the final-subject gate.
- **Viable options.** `docs-check`, `check`, `verify`, or leave CI-only.
- **Trade-offs.** Earlier placement catches regressions sooner and adds cost to every loop iteration.
- **Evidence needed.** Measured wall-clock cost of both linters on this repository. Not measured by this brief.

### OD-12 — Framework version cut

- **Present state.** The framework line is at v0.9.3. The product release line targets M-9 beta `0.9.0b1` then M-10 `0.9.0`. The framework number is numerically higher than the release target.
- **Existing constraints.** Invariant G-2 — M-9 cannot be authorized before M-8 has an exact producer-verifiable bundle and independent acceptance. M-8 is `BLOCKED`.
- **Viable options.** (a) Cut a framework version with a stated acceptance predicate. (b) No cut. (c) Renumber one line to remove the collision.
- **Trade-offs.** Any cut labelled `0.9.4` will be read by some audience as beta shipping. A cut before contracts stabilize renames ambiguity rather than resolving it.
- **Evidence needed.** None. This is a naming and release-policy decision.

---

## 6. Documentation consolidation — facts, and a separable decision

Reported and observed facts are in §3.1, §3.2 and §4. Leadership's input is required only on **which semantics survive** (OD-10) and **linter placement** (OD-11).

If leadership accepts a consolidation, the ordering that satisfies the existing constraints is:

1. Apply accepted semantic rulings.
2. Promote accepted durable behavior to its canonical semantic owner.
3. Compact completed execution history into subject-bound receipts, retaining still-relevant constraints and evidence.
4. Perform purely mechanical reclamation as a separate commit with a blob-comparison receipt (`README.md:108-110`).
5. Regenerate indexes and binding pins **last**, on the final intended subject.

Step 5 is load-bearing: a pin regenerated before its subject stops changing reads as attested and is not. The four pins are already in that failed condition (§1.3).

---

## 7. Leadership request

Return a disposition containing:

1. **Product architecture decisions** — OD-1 through OD-12, each ACCEPTED / AMENDED / DEFERRED / REJECTED with the operative ruling.
2. **Durable invariants** to be locked now, separated from values that remain experimental.
3. **Contradiction rulings** for C1–C9, naming which statement survives.
4. **Rejected and deferred options**, so they are not re-proposed.
5. **Evidence still required** before any deferred decision can be taken, and who produces it.
6. **Short- and mid-term capability outcomes** — desired properties, not task designs.
7. **Parallelization boundaries** — which surfaces may proceed concurrently and which serialize.
8. **Acceptance authority** — who accepts what, and the independence basis.
9. **Instructions for the Senior** — which canonical documents change, in what order, and which decisions convert into bounded developer packets with leases, falsifiers and acceptors.

Standing boundaries this brief does not touch: zero provider or paid calls; T-26 UNFROZEN; T-27 unauthorized; MS-CONTROL OPEN; D-6 closed at F1–F7, an eighth predicate requiring an explicit successor ruling. This brief proposes no new prerequisite.

---

## Appendix A — Non-authorizing observations

**Nothing in this appendix is a recommendation for adoption. It records what the compiling analysis noticed, so leadership can discount or use it.**

- The corpus is most formally rigorous in FH-1, which is `[PROPOSAL]` and gated behind MS-CONTROL, and least rigorous — or empty — on the surfaces currently under construction. Whether that inversion matters is a leadership judgment.
- The empty `Appendix A` slots in `technical.md` are self-labelled "normative for implementers." Whichever way OD-1 is decided, that label currently describes nothing.
- `technical.md` carries ~795 heading-only lines with no inbound links. Git preserves the original text at `001911e3`. Reclaiming them would free roughly 633 lines under the existing ceiling; whether that space should be used, and for what, follows from OD-1 and OD-2 rather than preceding them.
- Three of five `main/` files are over their doc-budget ceilings. Because the gate is CI-only, this is not currently visible in local runs.
- `roles_and_authority.md:59-60` observes that each added escalation trigger costs a fortnight of autonomy. This brief proposes no addition and no removal; if gate load is a concern, `development_philosophy.md:59-65` states the test — a developer works two weeks, makes a hundred decisions, and review finds nothing that should have been escalated.
