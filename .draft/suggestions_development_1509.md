
Subject: Executive Dispatch Directive — Execution Plane Locks & Immediate Lane Assignments

To: Senior Tech Lead
From: Architecture Leadership / Decisor
Date: 2026-09-15
Subject HEAD: 1a2cb2b6 (clean; leadership review examined 953d9d76, advanced only by two draft-file renames)
Authority: Executive Ruling & Binding Dispatch Directive

---

1. Executive Rulings & Invariant Locks (Non-Negotiable)

Locked into law effective immediately. Do not re-litigate or reopen:

1. Admission is capability-derived. Gated purely on "patch.apply" presence in verbs (runtime/session.py:280). No name set, no preset allowlist, no product default. Remove the stale exemption text at spec.md:1885 (C1).
2. Substrate unification. One compiler, one EpisodeEngine, one fold-produced SemanticTaskState. Context tiering is L4/L5 policy on the existing compiler; progressive.py is historical material, not a live fork. Versioned continuation wrappers are distinct contracts, not competing task schemas.
3. Budget currency is four additive dimensions: USD micros, wall-clock milliseconds, tokens, bytes. These are summed. Depth and turn ceilings are structural constraints and are never sibling-summed. Authority is rechecked at dispatch. Refunds cannot create budget. This adopts no quarantined FH settlement machinery.
4. Three identity layers, explicitly bound, never collapsed into one digest: workspace identity, behavior/composition identity, verification-subject identity.
5. Topology is pure configuration, never a secondary execution authority. VISION.md governs; the README's absolute rejection text is superseded.
6. Measurement rigor. Wilson lower bound ≥ 0.40 stays two-sided and uncorrected, over observed binary LIVE outcomes; the 18/30 boundary holds. All 30 scheduled slots are preserved; unresolved slots remain explicit and block positive control acceptance. Zero observed false completions is a hard veto. Zero observations do not prove zero underlying risk.
7. No empty headings as contracts. A normative heading in technical.md either carries a concrete executable contract or is deleted. An empty slot is never cited.
8. SOTA qualification. SOTA is a dated, reproducible, resource-disclosed empirical comparison. No architecture or mechanism count earns the label.

---

2. Decisor Rulings on the Two Blockers

OD-7 — Acceptor deadlock (RESOLVED). Routine component leaves remain with pairwise non-author developer review (A reviews eligible B/C; B reviews eligible A/C; any author or material supplier of the repair is excluded). To prevent serialization of a three-person pool, Leadership acts as the independent fourth acceptor exclusively at batched milestone boundaries — integrated F-receipts and combined A/B/C claims.

Binding condition: a Director title does not by itself establish independence. For every claim Leadership accepts, the Senior records the author set, the exact subject, the reproduced evidence, and the explicit independence basis — including whether Leadership authored the ruling the claim implements. Where Leadership materially supplied the change under acceptance, the claim is marked LANDED / acceptance pending rather than accepted. No manufactured signer, no manufactured date.

OD-11 — Scope collision (RESOLVED). Dev C's T-132 lease covers the three execution documents only: spec.md, tasks.md, technical.md. The six non-execution overruns — docs/backend/architecture/agency.md (400/200), docs/backend/architecture/runtime-execution.md (275/200), docs/backend/reference/events.md (201/200), docs/backend/reference/runtime-service.md (201/200), docs/product/frontend/PRD_AETHER_DESKTOP.md (209/200), docs/product/frontend/PRD_FRONTEND_PLATFORM.md (349/200) — are carved out and logged as decoupled technical debt under their existing semantic owners.

Binding sequence: check_doc_budgets.py and check_stale_paths.py are appended to the docs-check target — which is inherited by both just check and just verify — only after the three execution documents are under ceiling. Wiring the gate while nine files fail would red every developer's in-loop gate on files nobody is authorized to touch. Ceilings are never raised to obtain green. Lowering remains always permitted (check_doc_budgets.py:37-38).

---

3. Immediate Action Plan — Senior Tech Lead

Step 1 — Establish the Ruling Ledger (D1).
Write the Ruling Ledger mapping each C-item and OD-item to its operative ruling, its target file, and its code-level acceptance citation. Semantic content only.

Step 2 — Mechanical documentation corrections (Bucket 1), as semantic edits.

- C1: delete the stale product-default exemption at spec.md:1885; cite session.py:280 as acceptance basis.
- Data-flow rewrite: correct docs/architecture/data-flow.md:87 to the true 14-stage sequence per kernel/dispatch.py:1-21 — S0 ENTER, S1 PARSE, S2 RESOLVE, S3 DESCRIBE, S4 CLASSIFY, S5 AUTHORIZE, S6 GRANT, S7 RESERVE, S8 VERIFY, S8a INTENT, S9 DISPATCH, S10 COMMIT, S11 RELEASE, S12 EMIT. S8a must appear explicitly: durable intent is appended and fsynced before effect. Do not collapse S5–S9 into a range.
- C2, C5, C7, C8, C9 per the ledger's rulings.
- README: replace the absolute topology/graph-validation rejection with the Lock 5 formulation.

Step 3 — Reclamation, as a separate commit.
Reclaim the 812 unlinked heading-only lines in technical.md (original text preserved at git show 001911e3:docs/execution/technical.md), recovering roughly 633 lines of headroom. This is mechanical work and must not share a commit with any semantic edit — it carries a blob-comparison receipt per README.md:108-110. Whether the recovered headroom is used, and for what, follows from OD-1 and OD-2; it is not spent by this step.

Step 4 — Lane dispatch (parallel, disjoint leases).

┌──────┬─────┬─────────────────────────────────┬──────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Lane │ Dev │        Authorized scope         │                                               Synchronization                                                │
├──────┼─────┼─────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ A    │ Dev │ T-131.8                         │ Start immediately on exclusive lease. Perform eligible non-author reviews of B/C handoffs.                   │
│      │  A  │                                 │                                                                                                              │
├──────┼─────┼─────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│      │ Dev │ Acceptance-record               │ Reconcile exact integration subjects, evidence digests and non-author dispositions for T-75/T-76, T-78,      │
│ B    │  B  │ reconciliation → T-131.3 →      │ T-83b, T-138, T-139 first; where none exists, mark LANDED / acceptance pending. Acquire session.py only on   │
│      │     │ T-131.4 → T-131.7               │ explicit C release of T-140, never from mechanism presence.                                                  │
├──────┼─────┼─────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│      │ Dev │ T-133 non-probe → T-132         │ Start T-133 guard files immediately, excluding tools/diagnostics/write_landing_probe.py, which waits on B's  │
│ C    │  C  │ (+OD-11) → T-137 → hermetic     │ valid T-130 disposition. T-132 bounded strictly to the three execution documents. justfile and CI changes    │
│      │     │ T-51 readiness                  │ serialize through this lease.                                                                                │
└──────┴─────┴─────────────────────────────────┴──────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

Step 5 — OD-8 capability packet (assigned: Senior).
Prepare one bounded long-session/isolation packet, falsifiers first. Required evidence targets: isolation violations are rejected, combined-tree verification, crash reconciliation, bounded long-session behavior. No CAS journal, planner algorithm or wire schema is pre-approved. Preparation is authorized now; execution waits on disjoint leases and an eligible acceptor. Note the starting point: child_runtime.py carries no worktree or workspace reference, and git worktree appears only as an uninvoked GitEnvironment constructor option (git.py:153-168).

Step 6 — Binding pins, last.
Index regeneration and hash-pin updates (state_of_play.md, DEVS.md, DIRECTOR.md, tasks.md) happen last, on the final exact subject, in a single mechanical commit with a blob-comparison receipt. The four current pins are already in the failed state where they read as attested and are not — LDA doctor reports index_healthy: true against revision 8a370db6, not the reviewed HEAD. Regenerating before the subject stops changing recreates that defect. Verify actual subject binding after regeneration.

---

4. Explicit Non-Actions

- Zero paid or provider calls. No live API spend.
- No control freeze. T-26 remains UNFROZEN, T-27 unauthorized, MS-CONTROL OPEN until F1–F7 carry accepted, mutually compatible receipts. D-6 stays closed at F1–F7; an eighth predicate requires an explicit successor ruling.
- No speculative architecture. No CoordinationPlan execution engine, no CAS journal, no second compiler, no new preset names or numeric envelopes, no per-mille budget representation, no wholesale FH-1 implementation.
- No version cut or renumbering (OD-12 DEFERRED).
- No private-corpus import, infrastructure provisioning or milestone closure.

Report back once D1 and the C1 / data-flow edits are staged for inspection.

---

The prompt

Execute Step 1 and Step 2 of the Executive Dispatch Directive dated 2026-09-15,
subject HEAD 1a2cb2b6.

Step 1 — Write the Ruling Ledger at .draft/todo/ruling_ledger_1509.md. One row per
item for C1-C9 and OD-1 through OD-12. Columns: item ID, operative ruling (one
sentence, imperative), target file, code-level acceptance citation (file:symbol,
and file:line as a review-time locator only), and status (mechanical / engineering /
blocked-external). Prefer named symbols over line numbers for identity. Semantic
content only — no file moves, no reclamation, no pin regeneration in this commit.

Step 2 — Stage these edits, do not commit:
  - spec.md:1885 — delete the stale vg-code-default / vg-code-lex admission
    exemption. Acceptance basis: runtime/session.py:280, whose docstring records
    that ADMISSION_GATE_EXEMPT and ADMISSION_GATED_HARNESSES are both removed.
    Verify the surviving FACT at spec.md:1051 reads as capability-derived.
  - docs/architecture/data-flow.md:87 — rewrite the dispatch stage map to the true
    14-stage sequence from kernel/dispatch.py:1-21: S0 ENTER, S1 PARSE, S2 RESOLVE,
    S3 DESCRIBE, S4 CLASSIFY, S5 AUTHORIZE, S6 GRANT, S7 RESERVE, S8 VERIFY,
    S8a INTENT, S9 DISPATCH, S10 COMMIT, S11 RELEASE, S12 EMIT. S8a must appear
    explicitly with durable-intent-before-effect stated. Do not collapse S5-S9 into
    a range. Preserve the K-04/K-05/K-06/K-07 ordering rationale where data-flow.md
    references it.

Constraints: no source changes, no justfile changes (C's T-132 lease), no tasks.md
status or lease edits beyond what Senior serialization requires, no index or pin
regeneration, zero paid calls. Do not raise any doc budget ceiling.

Then report: the ledger path, a diff summary of the two staged edits, and any place
where a ruling had no clean target file or its acceptance citation could not be
verified in source.



 Decisive leadership disposition

  Authorize three bounded capability outcomes alongside the existing integrity queue: isolated child workspaces, long-session continuity, and trustworthy oracle
  completeness. Authorize planner→worker→verifier integration only after those foundations are accepted.

  This supersedes blanket deferral of those outcomes until MS-CONTROL closes. It does not adopt the packet’s proposed implementations or the remaining FH-1
  machinery.

  ## Evidence basis

  The brief now resides at .draft/todo/leadership_improvements_exec_plane_1409.md. Its content is unchanged from the prior review.

  HEAD remains 1a2cb2b67e6ebb69fdaf6af351a04ede9538a54d; relevant source, tests and canonical documents are unchanged from reviewed subject
  953d9d7694dff0ff8d726bef420af0411dc9a187. An unrelated staged QUICKSTART edit remains untouched.

  VERIFIED STATE: The prior review ran 140 passing focused tests. Full qualification remains unestablished: just check failed existing path hygiene; just verify
  stopped at uv permissions; documentation budgets failed. LDA’s populated index reports healthy but carries an older revision and stale references. No tests were
  rerun this turn.

  EXISTING AUTHORITY: Historical acceptance remains bound to its original subject. Green focused tests and implemented mechanisms do not independently accept
  pending integration work.

  ## 1. Contradictions C1–C9

   Item    Finding and surviving contract
  ━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   C1      Real conflict. Capability-derived completion admission survives. Remove product-name exemptions.
  ──────  ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
   C2      Historical conflict, not a new fork. Extend the existing context compiler through policies; reject a second compiler.
  ──────  ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
   C3      Mixed layers and historical examples. Preserve one fold-produced SemanticTaskState; versioned continuation envelopes may wrap it without becoming
           another authoritative state.
  ──────  ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
   C4      Real ambiguity. Sum additive resource dimensions only; depth and turn ceilings remain structural constraints. Revalidate grants at dispatch and prohibit
           budget-creating refunds. Proposed FH settlement schemas remain unapproved.
  ──────  ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
   C5      Duplicated historical wording. Preserve stale-preimage rejection, atomic rollback and IndexPort enumeration. Consolidation must retain all three
           protections.
  ──────  ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
   C6      Distinct identities, not competing field counts. Keep workspace, behavior/composition and verification-subject identities separate and explicitly bound.
  ──────  ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
   C7      Editorial duplication. Retain one dialect contract.
  ──────  ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
   C8      Stale execution history. Current dependencies govern T-83b; its unreconciled acceptance provenance still requires repair.
  ──────  ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
   C9      Overstated. Several definitions already exist. Link unresolved identifiers to their canonical owners rather than duplicating definitions throughout the
           runway.

  Also correct the erroneous dispatch numbering in docs/architecture/data-flow.md:87, including durable intent before effect. VISION’s topology/scheduler separation
  overrides README’s absolute prohibition on topology or graph validation.

  ## 2. Disposition of every open decision

   Decision                           Status      Operative ruling
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   OD-1: Durable promotion            AMENDED     Promote accepted baseline behavior with its original subject, scope and limitations. Record pending
                                                  implementations as as-built observations. New target contracts enter spec.md immediately; acceptance claims
                                                  require independent evidence.
  ─────────────────────────────────  ──────────  ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────
   OD-2: Semantic ownership           ACCEPTED    Preserve the five-file runway and existing architecture/reference owners. technical.md is guidance, never
                                                  competing law.
  ─────────────────────────────────  ──────────  ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────
   OD-3: Contradictions               AMENDED     Apply the rulings above; historical examples cannot override living contracts.
  ─────────────────────────────────  ──────────  ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────
   OD-4: Long-session boundary        AMENDED     Use a separately identified bounded composition over the existing pack, compiler and runtime. Do not modify
                                                  control presets. Defer public packaging and numerical envelopes until identity sensitivity and workload evidence
                                                  justify them.
  ─────────────────────────────────  ──────────  ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────
   OD-5: Topology/CoordinationPlan    AMENDED     Extend Topology and its existing runtime lowering. A plan may be a versioned input artifact, but cannot introduce
                                                  another scheduler, agent loop or authority. Defer per-mille allocation and named aggregation algorithms.
  ─────────────────────────────────  ──────────  ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────
   OD-6: Worker isolation             ACCEPTED    Require isolated writable views and exclusive, fenced mutation ownership before concurrent mutating workers.
                                                  Shared-workspace mutation remains serialized. Git worktrees alone do not prove containment.
  ─────────────────────────────────  ──────────  ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────
   OD-7: Independent acceptance       AMENDED     Leadership may accept batched evidence when genuinely independent of the implementation and material repair.
                                                  Otherwise use an eligible developer or an uninvolved reviewer.
  ─────────────────────────────────  ──────────  ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────
   OD-8: Capability sequencing        AMENDED     Admit the bounded packets below without waiting for MS-CONTROL. Preserve current integrity work and existing
                                                  leases. Campaigns and broad FH-1 activation remain deferred.
  ─────────────────────────────────  ──────────  ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────
   OD-9: Measurement                  AMENDED     Preserve existing Wilson semantics and fixed-slot accounting; qualify stronger false-completion detection and
                                                  exact-candidate evidence.
  ─────────────────────────────────  ──────────  ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────
   OD-10: Consolidation               ACCEPTED    Preserve receipts and surviving semantics before removing duplication or completed history.
  ─────────────────────────────────  ──────────  ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────
   OD-11: Documentation gates         ACCEPTED    Add budget and stale-path checks to docs-check, inherited by check and verify, through C’s T-132 lease. Resolve
                                                  baseline failures without silently raising ceilings.
  ─────────────────────────────────  ──────────  ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────
   OD-12: Framework version           DEFERRED    No cut now. A later cut needs coherent public contracts, compatible migration behavior, reproducible
                                                  installation, passing final gates and independent acceptance. Development numbering cannot imply M-9/M-10
                                                  closure.

  ### What can become durable architecture now

  Retain and accurately document the historically accepted baseline: canonical composition, one execution family, ledger-derived state, capability-mediated effects,
  bounded context compilation and demonstrated compaction/restart behavior.

  Preserve accepted ADR-0107/0108/0110 contract boundaries. Their existence does not accept their implementations.

  Do not promote pending T-130/T-135/T-131.6/T-140 or provenance-unreconciled integration claims as newly accepted capabilities. Newly passing focused tests
  strengthen their evidence; they do not supply the missing independent disposition.

  ## 3. Durable invariants

  1. One substrate. Coding semantics live above a domain-blind kernel. Roles share the EpisodeEngine family, ports, capabilities, budgets and evidence primitives.
  2. Bounded context. Enforce the actual serialized input limit. Summaries cannot replace authoritative state or invent evidence. Retrieval content cannot grant
     authority.

  3. Crash-safe continuation. Preserve objective, constraints, revisions, unresolved work, evidence references, grants, budgets and pending/settled effects. Never
     replay settled effects. Reconcile uncertain outcomes before retrying.

  4. Identity continuity. Bind workspace state, composition and verification subjects explicitly. Incompatible behavior changes require an authorized migration or a
     new run.

  5. Isolated mutation. Children cannot implicitly modify the parent or sibling candidate. Ownership expiry, stale writers and recovery races must fail closed.
  6. Merge authority. Workers produce immutable candidate references. Authorized integration validates the base, combines changes and obtains exterior verification
     of the combined tree. Rebase or mutation invalidates affected evidence. Consensus cannot mint merge authority.

  7. Completion authority. Distinguish requested completion, runtime-admitted completion and independent evaluation. Admitted completion stops further effects.
  8. Honest accounting. Include retries, children, coordination and verification. Unknown consumption is not zero; restart cannot replenish spent resources.

  ### Completion and measurement

  The existing detector is insufficient for a broad trustworthy-completion claim.

  Require candidate-bound evidence establishing applicable behavioral checks, completeness and non-vacuity. Missing or stale verification blocks admission. An
  independently failed required oracle contradicts a claimed success; unavailable oracle evidence remains unresolved, rather than becoming success or an invented
  binary result.

  Preserve:

  - Two-sided, uncorrected 95% Wilson with the existing z=1.96.
  - Observed binary LIVE outcomes as its denominator.
  - All 30 scheduled slots, one measured attempt each, with explicit missingness.
  - Positive control acceptance only with all required binary outcomes, the existing 18/30 boundary and zero observed false completions.
  - Descriptive missingness bounds reported separately from confidence intervals.

  Zero observed false completions is not proof of zero underlying risk. “SOTA” requires a dated, reproducible comparison with disclosed resources and uncertainty.

  ## 4. Next bounded packets for the Senior

  These are outcome authorizations. The Senior assigns task IDs, owners, exact leases, compatible predecessors and eligible acceptors. Developers choose ordinary
  implementation mechanics.

   Packet                     Isolated child workspace lifecycle
   Authorization and outcome  AUTHORIZED: child-local mutation, recoverable candidate retention and controlled integration over the existing execution path.
   Required falsifiers        Attempt parent/sibling escape; stale-writer mutation; competing ownership; crash during mutation, handoff and cleanup. Prove no
                              partial accepted candidate, lost accepted artifact or duplicate settled effect.
  ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
   Packet                     Long-session continuity
   Authorization and outcome  AUTHORIZED: bounded large-context operation with compaction, restart and aggregate budget continuity in a separately identified
                              treatment.
   Required falsifiers        Compare uninterrupted and restarted semantic state; force repeated compaction; interrupt pending effects; change identity; revoke
                              authority; exhaust budgets. Prove no lost obligations, authority widening, fabricated evidence or budget reset.
  ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
   Packet                     Greenfield and multi-file oracle completeness
   Authorization and outcome  AUTHORIZED: exterior verification of the exact submitted candidate with meaningful coverage of required behavior. Extend existing work
                              instead of duplicating T-131 repairs.
   Required falsifiers        Reject empty/stub solutions, vacuous discovery, test tampering, stale verification, omitted required files, unauthorized additions and
                              candidate substitution. Include valid positive controls.
  ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
   Packet                     Planner→worker→verifier convergence
   Authorization and outcome  CONDITIONALLY AUTHORIZED: dispatch after the relevant workspace, continuation and oracle contracts are independently accepted. Use
                              existing topology lowering and the same runtime.
   Required falsifiers        Competing candidates, stale bases, worker failure, restart, budget exhaustion and verifier rejection must not produce unauthorized
                              merge or completion. Verify the final combined tree independently.

  These admissions do not approve the remaining FH-1 schemas, CAS algorithms, campaign machinery, learned routing or swarm experiments. New public-schema details
  still require an explicit seam decision.

  ## 5. Safe parallelism and acceptance assignments

  The immediate queue remains:

  - A: T-131.8, then eligible independent reviews.
  - B: T-130/T-135/T-131.6/T-140 reviews and acceptance reconciliation; then T-131.3 → T-131.4 → T-131.7 after release.
  - C: T-133 non-probe → T-132 → T-137 → hermetic T-51 readiness.
  - Senior: task truth, leases, handoffs, documentation transfer and packet dispatch.

  C retains session/context ownership until explicit release; probe dependencies remain binding. C owns justfile/CI changes under T-132. The Senior serializes board
  updates. Future packets may start only on genuinely available, disjoint surfaces.

  Leadership can accept batches, provided the reviewer did not author or materially supply the repair and independently reproduces the relevant falsifiers. General
  architecture authority is not automatic disqualification; directing the material repair is.

  B remains the eligible reviewer for assigned A/C work; A for assigned B/C work where independent. An integrated claim involving all available reviewers requires a
  qualified uninvolved acceptor. No such additional person is presently evidenced as appointed. Leadership owns that appointment; the Senior records the gap instead
  of inventing a signature.

  ## 6. Documentation transfer and authorization boundary

  The Senior shall:

  1. Put normative rulings in spec.md, engineering guidance in technical.md, live dependencies/leases in tasks.md, stable acceptance outcomes in milestones.md, and
     capability inventory in backlog.md.

  2. Update existing architecture/reference documents for accepted durable knowledge, distinguishing historical acceptance from current compatibility.
  3. Preserve subject-bound receipt references and digests before compacting completed history.
  4. Separate semantic changes from mechanical consolidation.
  5. Regenerate indexes and binding pins last and verify their actual subject binding.

  External curator, sealed-store, corpus, live-route, resource and reviewer requirements remain explicit evidence/authority gaps.

  Zero paid/provider calls. T-26 remains UNFROZEN. T-27 remains unauthorized. MS-CONTROL remains OPEN. D-6 remains F1–F7, with no capability packet becoming an
  eighth predicate.
