The primary goal of the AETHER / Vanguard framework is to build an industrial-grade, state-of-the-art (SOTA) substrate for autonomous AI coding agents capable 
of solving complex, multi-file software engineering challenges over long execution horizons without human hand-holding.

Unlike brittle agent wrappers that collapse after a few turns or fabricate test passes, Vanguard treats an agent not as a loose prompt loop, but as a pure     
projection over an immutable, event-sourced causality ledger. Its architectural mission is governed by five foundational pillars:

1. Long-Horizon Cognitive Resilience: Empower agents to sustain 40 to 120+ continuous turns of exploration, reasoning, and debugging without context           
dissipation or catastrophic forgetting, backed by structured compaction and crash-safe ledger resumption.
2. Fail-Closed Trust Spine: Confine execution within a bounded, domain-blind microkernel (TCB ≤ 1,438 LOC, audited by tests and linters — not a machine-checked proof) with monotonic capability attenuation and Ed25519
cryptographic approvals, preventing unauthorized environmental escape or lease violations.
3. Token-Bounded Repository Intelligence (LDA): Replace blind, context-exhausting grepping with a SQLite-WAL AST fact graph. Demonstrated: recall@5 of 1.0 for BM25/PPR on a six-file fixture (hybrid 0.875); a real-repo `lda plan` call on the order of seconds; sub-50ms is the delta-index measurement, not universal retrieval.
4. Anti-Tampering & Orthogonal Settlement: Strictly decouple run termination from task disposition. Victory is never self-declared by the model; it is granted 
solely by exterior, tamper-proof test oracles with zero tolerance for vacuous stubs or assertion tampering.
5. Atomic Multi-File Manipulation: Equip agents with two-phase commit (2PC) transactional editing and dynamic dependency tracking to safely architect new      
systems from scratch or navigate multi-million-line legacy codebases.

Ultimately, Vanguard transforms AI agents from probabilistic conversational tools into rigorous, verifiable, and self-correcting software engineers that deliver systems whose behavior is demonstrated under test — not assumed proven.

One general substrate — kernel, ports, budgets, evidence ledger, one episode loop — on which many agents are composed, with coding as the first pack rather than the point. The kernel is domain-blind by invariant (I-7), which is why formal-sat and code-explain sit beside code-default without a second runtime.

The distinguishing bet is truth before capability. Most harnesses optimize pass rate and treat honesty as a reporting layer. Aether inverts that: MS-TRUTH precedes MS-CONTROL in the reliability ordering because an agent that can claim completion it didn't earn makes every subsequent measurement meaningless. Hence the machinery that looks like overhead — exterior verification, tamper shields, candidate identity, fail-closed admission, the false-completion veto that runs independently of pass rate. The goal is an agent whose "done" is checkable by someone who doesn't trust it.

On that foundation, the product target: a coding agent that handles real multi-file greenfield and brownfield work over long horizons — localize, change, verify, recover, resume, report — under a finite budget it accounts for honestly. Then planner/worker topologies on the same substrate, not a second loop bolted on.

And SOTA is a measurement, not a claim. That's what the whole control apparatus is for: D-6's F1–F7, thirty fresh tasks, a Wilson lower bound, zero observed false completions. The framework is built so that when you eventually say "this is state of the art," the sentence is backed by a protocol someone hostile could reproduce.

The strategic risk is the mirror of the strength: the discipline that makes claims trustworthy also slows capability, and a perfectly honest agent nobody wants is still a failure.

The main goal of AETHER/Vanguard is to build a trustworthy, general-purpose substrate for autonomous AI agents, with a state-of-the-art coding harness as its first demanding product proof. Agents should be able to understand large repositories, plan complex work, edit multiple files atomically, use tools safely,
recover from errors, compact context, resume long sessions, and collaborate as planners, workers, reviewers, and specialists—all through the same core primitives
rather than separate ad hoc agent systems.

Success is not merely producing plausible code or passing convenient tests. Every outcome must be attributable to the exact task, workspace candidate,
composition, model usage, authorization, and exterior verification evidence. Capabilities must remain bounded by explicit authority and resource budgets, fail
closed when identity or infrastructure is uncertain, and preserve durable state across crashes and restarts.

Ultimately, AETHER should let senior humans delegate difficult engineering outcomes—not micromanage individual actions—while retaining reliable evidence of what
happened, why it happened, what changed, what was verified, and whether the result is safe to accept. The framework should support increasingly capable agent
organizations without duplicating execution loops, weakening containment, or sacrificing measurement integrity.






# WORK SUGGESTED V1

At current a217a9ef, Vanguard has a strong mechanism base but is not an accepted MVP. The key distinction is:

   Delivery level                  Meaning                                                                                      Current state
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Engineering MVP                 Public coding CLI safely localizes, changes, verifies, resumes, and reports under bounded    Incomplete
                                   authority
  ──────────────────────────────  ───────────────────────────────────────────────────────────────────────────────────────────  ─────────────────────────────────────
   Qualified coding-harness MVP    MS-CONTROL: evidence-backed product qualification on 30 frozen tasks                         Open; external prerequisites absent
  ──────────────────────────────  ───────────────────────────────────────────────────────────────────────────────────────────  ─────────────────────────────────────
   Framework MVP                   M-8: governed durable memory with held-out lift and rollback                                 Blocked
  ──────────────────────────────  ───────────────────────────────────────────────────────────────────────────────────────────  ─────────────────────────────────────
   Beta / final release            M-9 / M-10                                                                                   Unauthorized
  ──────────────────────────────  ───────────────────────────────────────────────────────────────────────────────────────────  ─────────────────────────────────────
   Reproducible SOTA claim         MS-SOTA: official protocol and comparator superiority                                        Post-release horizon

  ## Current project state

   Area / goal               Done / mechanism present                           Remaining required work                            Owner / dependency
  ━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Trust foundation          M-0–M-3C, M-4, M-5a are done; kernel is            Preserve boundaries and evidence discipline        All
                             1386/1438 LOC
  ────────────────────────  ─────────────────────────────────────────────────  ─────────────────────────────────────────────────  ──────────────────────────────────
   Truth spine               MS-INSTRUMENT and MS-RESUME closed; anti-          Exact-subject product convergence, T-89/T-92/L0    Principal
                             tamper/completion mechanisms exist                 evidence, T-04 successor obligation
  ────────────────────────  ─────────────────────────────────────────────────  ─────────────────────────────────────────────────  ──────────────────────────────────
   LDA intelligence          LDA 2.0 healthy; README/skill workflow updated     Resolve global documentation-health debt before    Governance
                                                                                release gate
  ────────────────────────  ─────────────────────────────────────────────────  ─────────────────────────────────────────────────  ──────────────────────────────────
   Multi-file change         Atomic transaction and caller-awareness            Exact-subject evidence and independent             Principal
                             mechanisms exist                                   acceptance for MS-CHANGE
  ────────────────────────  ─────────────────────────────────────────────────  ─────────────────────────────────────────────────  ──────────────────────────────────
   Context / retrieval       One compiler and L5 retrieval mechanisms exist     Exact-subject evidence and independent             Principal
                                                                                acceptance for MS-SEE
  ────────────────────────  ─────────────────────────────────────────────────  ─────────────────────────────────────────────────  ──────────────────────────────────
   T-141 child workspaces    R1 hardening committed: immutable retention/       Real child-local adapters, base/grant/budget       Principal / A
                             fencing durability improved                        revalidation, verified combined-tree
                                                                                publication, safe recovery, then production
                                                                                activation
  ────────────────────────  ─────────────────────────────────────────────────  ─────────────────────────────────────────────────  ──────────────────────────────────
   T-131.3 / T-131.4         Completion qualification and stop-after-           Implement and prove exterior-bound completion      B
                             admission contracts defined                        and no next effect after accepted completion
  ────────────────────────  ─────────────────────────────────────────────────  ─────────────────────────────────────────────────  ──────────────────────────────────
   T-131.7 / T-142           Historical resume mechanism exists                 Real runtime continuation: repeated compaction,    B
                                                                                fresh-process resume, pending effect
                                                                                reconciliation, revocation, exhaustion
  ────────────────────────  ─────────────────────────────────────────────────  ─────────────────────────────────────────────────  ──────────────────────────────────
   T-131.8                   Cascade-accounting code/tests landed               Reconcile two-commit receipt; independent          B / Leadership
                                                                                acceptance
  ────────────────────────  ─────────────────────────────────────────────────  ─────────────────────────────────────────────────  ──────────────────────────────────
   T-133                     Quarantine correction exists in prior work         One clean SHA-bound packet and acceptance          C
  ────────────────────────  ─────────────────────────────────────────────────  ─────────────────────────────────────────────────  ──────────────────────────────────
   T-132                     Gate-discovery implementation exists               Fix current two test_collection_integrity          C
                                                                                failures; commit and accept truthful gate
                                                                                behavior
  ────────────────────────  ─────────────────────────────────────────────────  ─────────────────────────────────────────────────  ──────────────────────────────────
   T-137                     Approval-path diagnostic exists                    Clean SHA-bound attribution packet; no             C
                                                                                unauthorized repair
  ────────────────────────  ─────────────────────────────────────────────────  ─────────────────────────────────────────────────  ──────────────────────────────────
   T-143                     Candidate-bound oracle checks exist                Clean SHA-bound packet and independent             C
                                                                                acceptance
  ────────────────────────  ─────────────────────────────────────────────────  ─────────────────────────────────────────────────  ──────────────────────────────────
   Product CLI MVP           entrypoint.execute → Runtime → HarnessSession      End-to-end exact-subject CLI proof after T-141/    Principal
                             exists                                             T-131/T-143 integration
  ────────────────────────  ─────────────────────────────────────────────────  ─────────────────────────────────────────────────  ──────────────────────────────────
   Validation gates          Boundaries pass; LDA healthy                       Repair known collection-gate failures plus         Principal + canonical doc owners
                                                                                path-hygiene / broken-link / frontmatter debt
                                                                                before final verification
  ────────────────────────  ─────────────────────────────────────────────────  ─────────────────────────────────────────────────  ──────────────────────────────────
   T-51 corpus               Quarantine mechanics exist                         Independent curator, sealed store, 30 fresh        External authority
                                                                                holdout identities and receipts
  ────────────────────────  ─────────────────────────────────────────────────  ─────────────────────────────────────────────────  ──────────────────────────────────
   T-26 / T-27 control       Preregistration/control mechanisms exist           Accept T-51, freeze exact subject, explicitly      Leadership + external authority
                                                                                authorize run/resources, execute/publish 30
                                                                                outcomes
  ────────────────────────  ─────────────────────────────────────────────────  ─────────────────────────────────────────────────  ──────────────────────────────────
   M-8 framework MVP         Memory mechanisms present                          Empirical runner repair, held-out lift ≥0.05,      Memory owner
                                                                                promotion separation, rollback receipts
  ────────────────────────  ─────────────────────────────────────────────────  ─────────────────────────────────────────────────  ──────────────────────────────────
   M-9 / M-10 release        Not authorized                                     M-8 evidence, install/offline workflows,           Release owner
                                                                                migration, restore, security/performance/soak,
                                                                                signed release envelope
  ────────────────────────  ─────────────────────────────────────────────────  ─────────────────────────────────────────────────  ──────────────────────────────────
   T-144 topology demo       Design contract exists                             Wait for accepted T-141/T-142/T-143; capability    Later
                                                                                demo only
  ────────────────────────  ─────────────────────────────────────────────────  ─────────────────────────────────────────────────  ──────────────────────────────────
   SOTA claim                Protocol design exists                             Official evaluation, frozen comparator/resource    Post-MVP
                                                                                envelope, reproducible superiority evidence

  ## Critical delivery order

   Order    Work                                                                                      Can run in parallel with
  ━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
       0    Fix T-132’s two active collection-gate failures; assign documentation-gate cleanup        T-141, T-131.7
  ───────  ────────────────────────────────────────────────────────────────────────────────────────  ─────────────────────────────────────────
       1    Finish T-141 production activation safely                                                 C’s packet cleanup, B continuation work
  ───────  ────────────────────────────────────────────────────────────────────────────────────────  ─────────────────────────────────────────
       2    C lands T-133 → T-132 → T-137 → T-143 as four clean packets                               B: T-131.3 → T-131.4 → T-131.7 → T-142
  ───────  ────────────────────────────────────────────────────────────────────────────────────────  ─────────────────────────────────────────
       3    Bind/accept prior evidence: T-131.6, T-131.8, T-130/T-135, T-140, T-75/76, T-78, T-83b    Product integration
  ───────  ────────────────────────────────────────────────────────────────────────────────────────  ─────────────────────────────────────────
       4    Run exact-subject public CLI integration and final local gates                            After 1–3
  ───────  ────────────────────────────────────────────────────────────────────────────────────────  ─────────────────────────────────────────
       5    Obtain curator/store/resources; complete T-51 → T-26b → T-26 → T-27                       Requires external authority
  ───────  ────────────────────────────────────────────────────────────────────────────────────────  ─────────────────────────────────────────
       6    Close MS-CONTROL; then M-8, M-9, M-10                                                     Requires successful qualification
  ───────  ────────────────────────────────────────────────────────────────────────────────────────  ─────────────────────────────────────────
       7    Official/SOTA evaluation and planner-worker topology expansion                            Post-control / post-release

  The immediate project target should be the Engineering MVP plus MS-CONTROL readiness—not T-144, campaigns, or SOTA claims. The canonical source for this roadmap
  remains docs/execution/main/tasks.md and docs/execution/main/milestones.md.



# WORK SUGGESTED V2

# AETHER / Vanguard — Delivery Roadmap and SOTA Proposal

  North star: A general-purpose agent substrate whose first demanding product is a coding agent that can localize, change, verify, recover, resume and report across
  complex repositories under finite authority and budgets.

  At inspected HEAD 95a9ba38, the repository has substantial mechanisms and historical evidence, but this inspection does not establish an accepted engineering MVP.
  Earlier receipts retain their original subjects.

  Immediate objective: deliver the Engineering MVP and establish MS-CONTROL readiness. SOTA is a subsequent comparative measurement.

  ## 1. Define the delivery levels

   Delivery level                  What it establishes                                                             Current disposition
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Engineering MVP                 Public CLI performs useful multi-file work with safe mutation, truthful         Incomplete
                                   completion and durable recovery
  ──────────────────────────────  ──────────────────────────────────────────────────────────────────────────────  ──────────────────────────────────────────────────
   Qualified coding-harness MVP    MS-CONTROL’s preregistered, independently reviewed product qualification        Open; evidence and external prerequisites remain
  ──────────────────────────────  ──────────────────────────────────────────────────────────────────────────────  ──────────────────────────────────────────────────
   Framework MVP                   M-8 governed memory, measured held-out benefit, separated promotion and         Not established
                                   rollback
  ──────────────────────────────  ──────────────────────────────────────────────────────────────────────────────  ──────────────────────────────────────────────────
   Beta / final release            M-9/M-10 installation, operational reliability and release evidence             Gated
  ──────────────────────────────  ──────────────────────────────────────────────────────────────────────────────  ──────────────────────────────────────────────────
   Reproducible SOTA claim         Superiority against named comparators under a disclosed, reproducible           Proposed evaluation horizon
                                   protocol

  Two distinctions must remain explicit:

  - Thirty-task qualification is a product gate, not sufficient evidence of general SOTA superiority.
  - A staged multi-file change is not automatically an atomic transaction. Crash and concurrent-reader behavior must demonstrate the claimed publication semantics;
    calling it “2PC” supplies no guarantee.

  ## 2. Current state and next outcomes

  Ownership below is the proposed execution split. Accepted state remains governed by the canonical runway.

   Area                         Evidence/mechanism available                     Next required outcome                            Owner
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Trust foundation             Domain-blind kernel, attenuation, budgets,       Preserve invariants and revalidate the final     All
                                signed approval mechanisms                       integration subject
  ───────────────────────────  ───────────────────────────────────────────────  ───────────────────────────────────────────────  ───────────────────────────────────
   Repository intelligence      LDA navigation and incremental indexing          Measure retrieval accuracy, latency and          A + tooling owner
                                                                                 context cost on representative repositories
  ───────────────────────────  ───────────────────────────────────────────────  ───────────────────────────────────────────────  ───────────────────────────────────
   T-141 workspaces             R1 candidate-integrity hardening; production     Child-local effect adapters, safe publication    A / Principal
                                refusal                                          and recovery through real spawning
  ───────────────────────────  ───────────────────────────────────────────────  ───────────────────────────────────────────────  ───────────────────────────────────
   T-131.3/4 completion         Admission and stopping mechanisms/falsifiers     Exact exterior-bound completion; no              B
                                                                                 subsequent model or effect dispatch
  ───────────────────────────  ───────────────────────────────────────────────  ───────────────────────────────────────────────  ───────────────────────────────────
   T-131.7/T-142 continuity     Durable fold and historical resume evidence      Actual-runtime repeated compaction, restart,     B
                                                                                 pending-effect reconciliation, revocation and
                                                                                 exhaustion
  ───────────────────────────  ───────────────────────────────────────────────  ───────────────────────────────────────────────  ───────────────────────────────────
   T-131.8 accounting           Cascade-accounting implementation across two     Preserve history; bind combined evidence and     B + Leadership
                                commits                                          independent disposition
  ───────────────────────────  ───────────────────────────────────────────────  ───────────────────────────────────────────────  ───────────────────────────────────
   T-133 quarantine             Implementation work exists                       Exact packet proving all relevant entrypoints    C
                                                                                 enforce exposure rules
  ───────────────────────────  ───────────────────────────────────────────────  ───────────────────────────────────────────────  ───────────────────────────────────
   T-132 collection             Discovery and gate work exists                   Current focused results; deliberate failures     C
                                                                                 remain visible
  ───────────────────────────  ───────────────────────────────────────────────  ───────────────────────────────────────────────  ───────────────────────────────────
   T-137 approval               Diagnostic attribution exists                    Separate product reachability from session-      C
                                                                                 only success; independently accepted
                                                                                 attribution
  ───────────────────────────  ───────────────────────────────────────────────  ───────────────────────────────────────────────  ───────────────────────────────────
   T-143 oracle completeness    Candidate-bound checks and reported positive     Exact-subject independent verification,          C, accepted by A
                                controls                                         including oracle integrity
  ───────────────────────────  ───────────────────────────────────────────────  ───────────────────────────────────────────────  ───────────────────────────────────
   CLI product integration      Public runtime route exists                      Reproducible greenfield and brownfield           Principal
                                                                                 journeys on one integration subject
  ───────────────────────────  ───────────────────────────────────────────────  ───────────────────────────────────────────────  ───────────────────────────────────
   Validation                   Focused evidence exists; prior global            Repair current blocking failures without         Canonical owners
                                failures recorded                                exclusions or weakened assertions
  ───────────────────────────  ───────────────────────────────────────────────  ───────────────────────────────────────────────  ───────────────────────────────────
   Control qualification        Protocol and gating machinery exist              Curator, sealed store, fresh task identities,    Leadership + external authorities
                                                                                 resources and independent receipts
  ───────────────────────────  ───────────────────────────────────────────────  ───────────────────────────────────────────────  ───────────────────────────────────
   Governed memory              Storage/retrieval mechanisms exist               Authorized persistence, revocation, held-out     Memory owner
                                                                                 lift and rollback
  ───────────────────────────  ───────────────────────────────────────────────  ───────────────────────────────────────────────  ───────────────────────────────────
   T-144                        Target design exists                             Accepted applicable foundations, then bounded    Later
                                                                                 capability demonstration

  Do not carry forward “two current failures,” a historical TCB count, or a previous green gate without rerunning it on the intended subject.

  ## 3. SOTA proposal: what to optimize

  The competitive proposition should be reliably completed engineering work per unit of cost, elapsed time and human intervention.

  ### A. One strong controller first

  Make the single-controller CLI effective before adding agent organizations:

  - Maintain explicit objectives, constraints, unresolved failures and evidence references.
  - Retrieve code and dependencies when needed.
  - Perform bounded changes followed by meaningful verification.
  - Detect repeated failure and change strategy within existing authority.
  - Stop honestly when evidence or resources are insufficient.

  Long-running harness research supports incremental work, recoverable progress and explicit verification rather than relying on a large prompt alone. Adopt those
  techniques through Vanguard’s existing ledger and compiler. Anthropic: long-running harnesses

  ### B. Context quality over context volume

  Treat 40, 80 and 120+ turns as proposed qualification treatments, not success metrics themselves.

  Measure:

  - Preservation of obligations and constraints after compaction.
  - First resumed model context after process death.
  - Repeated retrieval and redundant tool calls.
  - Tokens and latency per useful observation.
  - Correct handling of changed files and stale index facts.

  Keep exact identities and obligations in durable structured state; use summaries for replaceable explanatory context. This follows the distinction between durable
  state and selective working context in current context-engineering practice. Anthropic: context engineering

  ### C. Verified publication as the trust boundary

  The proposed production change path is:

  Observe base → isolate execution → retain candidate → stage combined tree → exterior verification → revalidate authority/base/fence → publish → record settlement

  Required properties:

  - The verified combined tree is exactly the published tree.
  - A changed base, candidate, composition or relevant oracle invalidates affected evidence.
  - A worker’s successful termination grants no merge authority.
  - Recovery reconciles recorded effects; it never interprets retention as permission to publish.
  - Child execution cannot write parent data, sibling data or supervisor control records.

  Choose publication mechanics that prove these properties. Avoid a custom transaction system unless the existing filesystem and runtime mechanisms cannot satisfy
  them.

  ### D. Prove the harness contribution

  Use two distinct comparison tracks:

   Comparison                    Hold constant                                            Question answered
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Harness comparison            Model, tasks, budget, tools and execution environment    Does Vanguard improve delivery?
  ────────────────────────────  ───────────────────────────────────────────────────────  ───────────────────────────────────────
   Complete-system comparison    Task protocol and disclosed resource limits              Is the delivered product competitive?

  Add development-set ablations for LDA, compaction, memory and delegation. Preserve holdout isolation.

  A standardized minimal harness is a useful comparator; SWE-bench’s bash-only view explicitly uses a common mini-SWE-agent environment. SWE-bench leaderboard

  ### E. Use a benchmark portfolio

  Proposed portfolio:

  1. Fresh private multi-file tasks: primary product qualification.
  2. Public issue-resolution benchmark: external comparability.
  3. Greenfield feature tasks: requirements and oracle completeness.
  4. Long-horizon recovery tasks: interruption, changing context and pending effects.
  5. Adversarial integrity tasks: false completion, tampering, stale verification and authority violations.

  Audit task validity and contamination before selecting the final protocol. Recent benchmark audits show why a familiar benchmark name alone is insufficient
  assurance. OpenAI: coding-evaluation signal and noise

  ## 4. Critical delivery sequence

   Stage                                 Deliverable                                 Exit evidence                               Parallel work
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   0 — Establish one delivery subject    Explicit adoption of dirty work; packet     Exact file ownership, subjects and          A/B/C targeted diagnosis
                                         boundaries; current failure inventory       baseline commands
  ────────────────────────────────────  ──────────────────────────────────────────  ──────────────────────────────────────────  ────────────────────────────────────
   1 — Complete T-141                    Safe child execution and verified           Real-spawn positive case plus escape,       B continuity; C integrity
                                         publication                                 drift, race, revocation, crash and
                                                                                     rejection falsifiers
  ────────────────────────────────────  ──────────────────────────────────────────  ──────────────────────────────────────────  ────────────────────────────────────
   2 — Complete continuity and truth     T-131.3/4/7, T-142, T-133/132/137/143       Runtime-path evidence and separate          Disjoint file leases
                                                                                     packet dispositions
  ────────────────────────────────────  ──────────────────────────────────────────  ──────────────────────────────────────────  ────────────────────────────────────
   3 — Integrate the product             Public CLI greenfield and brownfield        Exact-subject change, verification,         Documentation/gate repairs
                                         journeys                                    resume and bounded-budget receipts
  ────────────────────────────────────  ──────────────────────────────────────────  ──────────────────────────────────────────  ────────────────────────────────────
   4 — Close Engineering MVP             Installable, usable, reproducible local     just check, just verify, independent        External qualification preparation
                                         product                                     integration disposition
  ────────────────────────────────────  ──────────────────────────────────────────  ──────────────────────────────────────────  ────────────────────────────────────
   5 — Qualify MS-CONTROL                T-51 → T-26b → T-26 → T-27                  Explicit authorization and complete         Only separately authorized work
                                                                                     preregistered reporting
  ────────────────────────────────────  ──────────────────────────────────────────  ──────────────────────────────────────────  ────────────────────────────────────
   6 — Demonstrate extensions            T-144 capability demonstration; governed    Independent capability and memory           Disjoint accepted foundations
                                         memory toward M-8                           evidence
  ────────────────────────────────────  ──────────────────────────────────────────  ──────────────────────────────────────────  ────────────────────────────────────
   7 — Release and compare               M-9/M-10 gates; separately authorized       Release envelope and reproducible           No retroactive tuning of holdouts
                                         external evaluation                         comparator results

  T-144 need not wait for final release: its existing dependency is accepted applicable T-141/T-142/T-143 foundations and released integration scope. It remains a
  capability demonstration and must not displace engineering-MVP closure.

  ## 5. Engineering MVP acceptance checklist

   Dimension          Required evidence
  ━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Useful delivery    Nontrivial greenfield and brownfield multi-file tasks through the public CLI
  ─────────────────  ───────────────────────────────────────────────────────────────────────────────────────
   Isolation          Actual child effects cannot reach parent/sibling/control state
  ─────────────────  ───────────────────────────────────────────────────────────────────────────────────────
   Publication        Exact verified tree published under current authority and base
  ─────────────────  ───────────────────────────────────────────────────────────────────────────────────────
   Completion         Missing, stale, vacuous or substituted verification cannot produce success
  ─────────────────  ───────────────────────────────────────────────────────────────────────────────────────
   Continuation       Repeated compaction and fresh-process resume preserve obligations and identities
  ─────────────────  ───────────────────────────────────────────────────────────────────────────────────────
   Effects            Settled effects do not replay; uncertain effects remain unresolved until reconciled
  ─────────────────  ───────────────────────────────────────────────────────────────────────────────────────
   Resources          Model/tool consumption remains bounded across fallback and restart
  ─────────────────  ───────────────────────────────────────────────────────────────────────────────────────
   Operations         Installation, failure diagnostics, cancellation and recovery work as documented
  ─────────────────  ───────────────────────────────────────────────────────────────────────────────────────
   Evidence           Exact subjects, commands, results, limitations and eligible dispositions are retained

  Zero observed false completions is a mandatory veto condition; it is not proof that the underlying failure probability is zero.

  ## 6. Delivery rules that protect speed

  - A: finish T-141; independently accept eligible C packets.
  - B: finish completion/continuity/accounting; independently accept eligible A packets.
  - C: finish integrity/oracle packets; independently accept eligible B packets.
  - Leadership: resolve cross-file conflicts and architectural decisions, assemble the final delivery subject, and obtain external authority.
  - Anyone who materially repairs a claim becomes its author and transfers acceptance.
  - Reserve acceptance and integration capacity alongside implementation capacity.
  - Keep one complete vertical slice ahead of new abstractions.
  - Evaluate performance improvements on development tasks; promote only measured improvements.
  - Do not let unrelated documentation cleanup expand into an architectural rewrite.

  Recommended immediate commitment: finish one trustworthy CLI delivery-and-resume path, activate T-141 safely, close current integrity packets, and produce an
  independently reviewable Engineering MVP subject. Then qualify capability under the existing control protocol.

  This is a chat-only proposal, not a task-state change or authorization for paid evaluation. Canonical authority remains docs/execution/main/
  {tasks,spec,milestones,technical,backlog}.md.


# WORK SUGGESTED V3: THE SYNTHESIS (FOUNDATIONAL RIGOR + HIGH-VELOCITY VERIFICATION)

Neither V1 nor V2 is sufficient on its own:
- **V1's flaw**: Decoupled from execution velocity; collapses into bureaucratic ticket auditing and administrative gridlock before proving real utility.
- **V2's flaw**: Over-corrects toward immediate single-agent delivery, risking architectural myopia and under-specifying the substrate invariants needed for multi-agent delegation, shared ledgers, and formal SOTA qualification.

**V3 is the dual-stage architecture**: Build the industrial, frontier PhD-grade substrate from Day Zero (hexagonal ports, monotonic attenuation, event-sourced causality ledger, LDA SQLite-WAL fact graphs, plugin interfaces, tamper-proof exterior verification), while establishing a single autonomous controller as the **first uncompromising client of that full substrate**.

---

## 1. Core Principles of V3

1. **Substrate-First Invariants from Day Zero**:
   - Strictly uphold hexagonal isolation (`domain ← ports ← kernel ← agency ← runtime → adapters`).
   - Monotonic capability attenuation, cryptographic approvals, and the TCB limit ($\le 1438$ LOC) are non-negotiable.
   - Design ports, events, and leasing so multi-agent topologies (planner/worker/verifier) plug directly into the causality ledger without rewriting the execution loop.

2. **One Strong Controller as the Sovereign Proof**:
   - The single-controller agent is not a toy prototype; it is the comprehensive testbed that exercises every layer of the substrate (AST navigation, transactional changes, sandbox execution, exterior oracle checks, session resumption).
   - If the substrate cannot safely power one autonomous agent through 80+ turns of complex refactoring, it will fail when scaled to multi-agent swarms.

3. **Subjugate Bureaucracy to Empirical Falsification**:
   - Stop managing synthetic paper tickets across five redundant runway documents.
   - Replace administrative busywork with executable test suites, deterministic boundary linters, and reproducible benchmark evaluations.

---

## 2. Two-Stage Unified Roadmap

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│                   STAGE 1: HARDENED SUBSTRATE & SINGLE CONTROLLER               │
│  - Event-sourced causality ledger + TCB microkernel intact                       │
│  - Token-bounded LDA AST fact graph (sub-50ms delta indexing)                   │
│  - Public CLI / CodingMaxFacade wired to real LLM inference                      │
│  - Atomic multi-file changes verified by exterior, tamper-proof test oracles     │
│  - Crash-safe session compaction and fresh-process resumption                   │
└────────────────────────────────────────┬─────────────────────────────────────────┘
                                         │ Validates substrate under fire
                                         ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│             STAGE 2: MULTI-AGENT RECURSIVE AGENCY & SOTA QUALIFICATION           │
│  - Subagent spawning via attenuated capability leases (T-141 child workspaces)   │
│  - Planner / Worker / Verifier / Specialist collaborative topologies (T-144)    │
│  - Governed memory layer with held-out benefit verification (M-8)               │
│  - Reproducible comparative SOTA evaluation on fresh, un-contaminated benchmarks │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Immediate Implementation Priorities

1. **Keep Day-Zero Invariants Pure**: Maintain the hexagonal boundaries, strict typing protocols in `ports/`, and the lean TCB core.
2. **Execute Live End-to-End**: Ensure `CodingMaxFacade` and `vg` run against real LLMs (local `llama-server` or cloud providers) without hitting mock cassettes or admission gate bottlenecks.
3. **Pave the Multi-Agent Way**: Ensure workspace leasing and capability descriptors are clean interfaces ready for recursive agency once the single-controller baseline achieves measurable stability.


