# PRIMARY GOAL: THE SOTA AGENTIC SUBSTRATE

The primary goal of the AETHER / Vanguard framework is to build an industrial-grade, state-of-the-art (SOTA) substrate for autonomous AI coding agents capable of solving complex, multi-file software engineering challenges over long execution horizons without human hand-holding.

Unlike brittle agent wrappers that collapse after a few turns or fabricate test passes, Vanguard treats an agent not as a loose prompt loop, but as a pure projection over an immutable, event-sourced causality ledger. Its architectural mission is governed by five foundational pillars:

1. **Long-Horizon Cognitive Resilience**: Empower agents to sustain 40 to 120+ continuous turns of exploration, reasoning, and debugging without context dissipation or catastrophic forgetting, backed by structured compaction and crash-safe ledger resumption.
2. **Fail-Closed Trust Spine**: Confine execution within a bounded, domain-blind microkernel (TCB ≤ 1,438 LOC, audited by tests and linters — not a machine-checked proof) with monotonic capability attenuation and Ed25519 cryptographic approvals, preventing unauthorized environmental escape or lease violations.
3. **Token-Bounded Repository Intelligence (LDA)**: Replace blind, context-exhausting grepping with a SQLite-WAL AST fact graph. Demonstrated: recall@5 of 1.0 for BM25/PPR on a six-file fixture (hybrid 0.875); a real-repo `lda plan` call on the order of seconds; sub-50ms is the delta-index measurement, not universal retrieval.
4. **Anti-Tampering & Orthogonal Settlement**: Strictly decouple run termination from task disposition. Victory is never self-declared by the model; it is granted solely by exterior, tamper-proof test oracles with zero tolerance for vacuous stubs or assertion tampering.
5. **Atomic Multi-File Manipulation**: Equip agents with two-phase commit (2PC) transactional editing and dynamic dependency tracking to safely architect new systems from scratch or navigate multi-million-line legacy codebases.

Ultimately, Vanguard transforms AI agents from probabilistic conversational tools into rigorous, verifiable, and self-correcting software engineers that deliver systems whose behavior is demonstrated under test — not assumed proven.

One general substrate — kernel, ports, budgets, evidence ledger, one episode loop — on which many agents are composed, with coding as the first pack rather than the point. The kernel is domain-blind by invariant (I-7), which is why formal-sat and code-explain sit beside code-default without a second runtime.

The distinguishing bet is truth before capability. Most harnesses optimize pass rate and treat honesty as a reporting layer. Aether inverts that: MS-TRUTH precedes MS-CONTROL in the reliability ordering because an agent that can claim completion it didn't earn makes every subsequent measurement meaningless. Hence the machinery that looks like overhead — exterior verification, tamper shields, candidate identity, fail-closed admission, the false-completion veto that runs independently of pass rate. The goal is an agent whose "done" is checkable by someone who doesn't trust it.

On that foundation, the product target: a coding agent that handles real multi-file greenfield and brownfield work over long horizons — localize, change, verify, recover, resume, report — under a finite budget it accounts for honestly. Then planner/worker topologies on the same substrate, not a second loop bolted on.

And SOTA is a measurement, not a claim. That's what the whole control apparatus is for: D-6's F1–F7, thirty fresh tasks, a Wilson lower bound, zero observed false completions. The framework is built so that when you eventually say "this is state of the art," the sentence is backed by a protocol someone hostile could reproduce.

The strategic risk is the mirror of the strength: the discipline that makes claims trustworthy also slows capability, and a perfectly honest agent nobody wants is still a failure.

The main goal of AETHER/Vanguard is to build a trustworthy, general-purpose substrate for autonomous AI agents, with a state-of-the-art coding harness as its first demanding product proof. Agents should be able to understand large repositories, plan complex work, edit multiple files atomically, use tools safely, recover from errors, compact context, resume long sessions, and collaborate as planners, workers, reviewers, and specialists—all through the same core primitives rather than separate ad hoc agent systems.

Success is not merely producing plausible code or passing convenient tests. Every outcome must be attributable to the exact task, workspace candidate, composition, model usage, authorization, and exterior verification evidence. Capabilities must remain bounded by explicit authority and resource budgets, fail closed when identity or infrastructure is uncertain, and preserve durable state across crashes and restarts.

Ultimately, AETHER should let senior humans delegate difficult engineering outcomes—not micromanage individual actions—while retaining reliable evidence of what happened, why it happened, what changed, what was verified, and whether the result is safe to accept. The framework should support increasingly capable agent organizations without duplicating execution loops, weakening containment, or sacrificing measurement integrity.

---

### SOTA Autonomous Coding Harnesses: The Meta-Framework Reality

To achieve true state-of-the-art autonomous software engineering (surpassing standalone agent loops like SWE-agent, Aider, Devin, or Hermes-style autonomous coding harnesses), an AI agent system must not be structured as a fragile prompt-and-eval loop. When faced with enterprise multi-file codebases, deep dependency trees, or long 100-turn debugging sessions, ad-hoc agent scripts inevitably collapse: context windows drown in irrelevant grep output, model edits break syntax silently, processes crash losing all working memory, and hallucinations cause agents to declare false victory on broken code.

In Vanguard / AETHER, autonomous coding agents operate within a **decoupled, event-sourced Meta-Framework** governed by six architectural tenets:

1. **The Agent as a Causal Projection (Not a Physical Object)**:
   Persistent in-memory `Agent` objects that hold state, memory, and tools in process memory are forbidden. Instead:
   $$\text{Agent} = \text{Identity} + \text{Policy} + \text{Event-Derived Projection} + \text{Execution Boundary}$$
   Every action, hypothesis, file observation, tool dispatch, test failure, and compaction is an immutable, append-only event (`mhf.event/2`) in a SQLite-WAL ledger. The working memory of the agent is a pure, deterministic fold over this causality stream. If an agent process dies, experiences rate-limiting, or restarts after a machine reboot, another process resumes the exact lineage with zero context amnesia (`RF-25`).

2. **Ontology of Atomic Primitives (Decoupled Language of Action)**:
   Instead of hardcoding domain workflows into the kernel, the substrate provides a minimal, orthogonal set of atomic primitives:
   - *Observation*: `fs.read`, `fs.search`, `repo.search_symbols`, `repo.get_callers`, `repo.get_dependencies`, `repo.get_tests`.
   - *Mutation*: `patch.apply` (preimage-bound transactional patch), `fs.write` (new file creation).
   - *Execution*: `proc.exec` (hermetic, sandboxed test execution).
   - *Governance & Coordination*: `task.revise` (plan adaptation), `agency.finish` (settlement request), `spawn` (attenuated child delegation).
   Complex behaviors—whether brownfield bug fixing, greenfield feature scaffolding, code audits, or formal verification—are simply different declarative compositions of these identical primitives.

3. **Hexagonal Lattice & Domain-Blind Microkernel (`domain ← ports ← kernel ← agency ← runtime → adapters`)**:
   The execution engine is strictly partitioned:
   - **`domain/`**: Zero-dependency pure Python contracts, event schemas, RFC 8785 JCS canonicalization, and task state models.
   - **`ports/`**: Strictly typed hexagonal protocols (`ModelPort`, `EventStorePort`, `SandboxPort`, `EvaluatorPort`).
   - **`kernel/`**: A domain-blind Trusted Computing Base ($\le 1,438$ LOC, currently 1,386 LOC) enforcing a 13-stage dispatch pipeline (S0–S12), monotonic budget attenuation, and fail-closed security.
   - **`agency/`**: The generic recursive turn loop (`EpisodeEngine`), admission gates, anti-stall recovery FSMs, and structured context compactor.
   - **`runtime/`**: Lifecycle composition, cryptographic Ed25519 approvals, and application services (`CodingMaxFacade`, `ApplicationService`).
   - **`adapters/`**: Pluggable backends: real LLMs (OpenRouter, llama.cpp / llama-server), rootless bubblewrap sandboxes (`bwrap`), and SQLite-WAL event stores.

4. **Token-Bounded Repository Intelligence (LDA 2.0)**:
   Frontier agents cannot afford blind string searches. LDA transforms the repository into an in-process SQLite-WAL AST graph. Through `lda plan`, an agent receives a token-bounded (e.g., 8,000 tokens) task bundle containing exact symbol line slices, 1-hop caller blast radius, affected documentation obligations, and relevance-ranked test falsifiers in ~2 seconds, with sub-50ms incremental AST synchronization on dirty files.

5. **Exterior, Tamper-Proof Verification (Anti-Hallucination & Anti-Tampering)**:
   In a production harness, victory is never self-declared by the LLM. The agent's `finish` proposal is merely a submission request. Acceptance is governed by independent exterior oracles executing against the exact workspace candidate. Any attempt by the model to delete tests, weaken assertions, or mock out failures triggers an immediate false-completion veto (`fc == 0`), failing closed.

6. **Fractal Multi-Agent Delegation Without Loop Duplication**:
   When scaling from a single autonomous worker to multi-agent topologies (planner, worker, verifier, specialist), the system does not bolt on a secondary orchestrator framework. Instead, child subagents are spawned as attenuated children on the **exact same substrate**. The parent grants a scoped lease, a bounded token budget, and an isolated candidate workspace. All subagents write into the same unified causality ledger, enabling complete multi-agent attribution, cross-verification, and conflict-free transactional merges.

---

# STEP 1: HARDENED TRUST SPINE & EMPIRICAL BASELINE (The Resilient Worker Core)

The foundational step establishes an uncompromising, reproducible single-controller execution path. Before building complex multi-agent swarms or claiming benchmark supremacy, the core worker engine must be proven under fire: executing live LLM turns, localizing defects, applying atomic edits, executing tests, and surviving real-world failures without crashing or hallucinating success.

## 1.1 Objectives & Deliverables
- **Live Model Execution via OpenRouter & llama.cpp**: Ensure `ApplicationService` and `CodingMaxFacade` operate seamlessly against frontier reasoning models (e.g., DeepSeek v4.1 Flash, GLM 5.3 Flash via OpenRouter) and local weights (`llama-server`) with zero reliance on mock cassettes or synthetic test doubles for product execution.
- **Model Adapter & Proposal Schema Parity**: Standardize proposal validation in `vanguard/packages/adapters/models/invocation.py` to recognize real-world provider usage metadata (`provider_usd_micros`, `usd_micros`, `resolved_model`, `model_fingerprint`), ensuring live provider responses translate cleanly into canonical domain proposals without instrument errors.
- **Autonomous Headless Approvals for Backend Work**: Provide operator-governed Ed25519 signature generation (`OperatorSigner`) for unattended script execution, allowing the agent to execute approved sandboxed commands (e.g., `python3 -m unittest`, `pytest`) without stalling on interactive prompts.
- **Git-Backed Workspace Integrity**: Enforce valid repository initialization and status enumeration for all workspace targets, ensuring snapshot digests and dirty-tree baselines can be computed reliably before and after mutations.
- **Anti-Stall & Cycle Recovery FSM**: Validate the loop recovery state machine in `vanguard/packages/agency/episode/protocol_recovery.py` to detect semantic repetition (e.g., 2–3 identical failed patch attempts or redundant reads) and dynamically guide the model toward alternate hypotheses or graceful surrender within finite turn ceilings.

## 1.2 Verification & Exit Gates
1. **Live Vertical Smoke Test**: A headless backend script runs `CodingMaxFacade.run()` against a live LLM on a real bug in an isolated git repository, successfully reads the code and test, generates a valid patch, runs tests, and terminates with a verified outcome.
2. **Boundary & TCB Invariant Pass**:
   ```bash
   python3 tools/linters/check_boundaries.py
   python3 tools/linters/check_tcb_budget.py   # Must remain <= 1438 LOC (currently 1386 LOC)
   python3 tools/linters/check_domain_blindness.py
   ```
3. **Zero False-Completion Guarantee**: The veto harness verifies that unverified or failing runs are projected strictly as `abstained`, `failed`, or `abandoned`—never relabeled as `completed`.

---

# STEP 2: VERIFIED WORKSPACE ISOLATION & CONTINUITY (Safe Transactions & Resumption)

Step 2 builds upon the working single controller to provide ironclad multi-file safety and long-horizon execution resilience. An autonomous coding agent operating on enterprise systems must never leave dirty, half-applied edits or corrupted repositories when interrupted, and must sustain long multi-turn sessions (40–120+ turns) across process crashes.

## 2.1 Objectives & Deliverables
- **Candidate Workspace Isolation (T-141)**:
  Child and worker mutations must execute in isolated candidate worktrees/directories (e.g., `/tmp/...` or virtual CAS staging trees) rather than the active checkout. The parent and sibling trees remain strictly read-only during worker execution.
- **Two-Phase Commit (2PC) Multi-File Transactions**:
  Implement full preimage validation and atomic publication in `vanguard/packages/adapters/environment/transaction.py`:
  1. *Preflight*: Verify that all source files match expected preimage hashes and satisfy language syntax checks.
  2. *Isolated Staging*: Stage all file modifications in the candidate tree.
  3. *Exterior Verification*: Execute the test harness against the staged combined tree.
  4. *Atomic Commit*: Publish changes to the target repository only upon verified test passage.
  5. *Rollback Guarantee*: On test failure, timeout, or budget exhaustion, restore the baseline byte-for-byte and retain the failed attempt solely as an isolated evidence artifact.
- **Structured Context Compaction & Session Continuity (`RF-25` / T-142)**:
  As an episode approaches its token headroom ceiling (e.g., beyond turn 20 or 40), the structured context compactor folds historical turns into a durable `SemanticTaskState` (active goals, validated hypotheses, failed attempts, and caller maps) without losing critical constraints or unresolved obligations.
- **Fresh-Process Ledger Resumption**:
  Prove that a running session killed via `SIGKILL` or process crash can be cleanly resumed from its SQLite-WAL event store using `ApplicationService.resume(run_id=...)`, reconciling any pending effect intents (`EffectStarted` fsync) before issuing the next model turn.

## 2.2 Verification & Exit Gates
1. **Multi-File Rollback Falsifier**: A multi-file edit that introduces a syntax or test error is completely rolled back, leaving 0 uncommitted changes and matching the exact pre-run git SHA.
2. **Crash-Resume Invariant**: An episode terminated mid-run resumes in a fresh Python process, reconstitutes the `AgentView` from SQLite events, and continues execution without duplicating side-effects.
3. **Delta-Index AST Sync**:
   ```bash
   uv run lda index --delta   # Sub-50ms incremental reindex passes on all dirty files
   ```

---

# STEP 3: RECURSIVE MULTI-AGENT TOPOLOGIES & SOTA QUALIFICATION (The Meta-Framework in Action)

With a hardened worker core, safe transactional editing, and crash-resilient session continuity in place, Step 3 scales Vanguard into a true SOTA recursive-agency substrate and proves its superiority against established industry benchmarks.

## 3.1 Objectives & Deliverables
- **Attenuated Multi-Agent Topologies (T-144)**:
  Compose collaborative agent organizations using the unified `spawn()` primitive without introducing parallel runtime loops:
  - *Planner*: Synthesizes user briefs into structured dependency graphs, allocating sub-budgets and workspace leases.
  - *Worker*: Specialized single-controller coding agents executing bounded edits in isolated candidate workspaces.
  - *Verifier / Oracle*: Independent, read-only testing agents that execute hermetic falsifiers and inspect test coverage.
  - *Critic / Specialist*: Bounded advisory agents auditing security, documentation drift (`lda drift`), and architectural boundary compliance.
- **Governed Cross-Episode Memory (M-8 / `MEM-01`)**:
  Provide an authorized, governed memory store that captures durable engineering discoveries, architectural patterns, and reusable fixes across episodes, requiring empirical held-out lift ($\ge 0.05$) before promotion to prevent memory poisoning.
- **Official SOTA Benchmark Qualification (`MS-CONTROL` & SWE-bench)**:
  Subject the complete Vanguard harness to rigorous, reproducible qualification:
  1. *MS-CONTROL Canary*: Execute 30 frozen, pre-registered tasks with Wilson 95% confidence lower bound $\ge 0.40$ and zero observed false completions (`fc == 0`).
  2. *SWE-bench Verified Evaluation*: Run the standardized SWE-bench harness against official Docker evaluation environments, measuring:
     - Resolve rate (%) on held-out tasks.
     - Total inference cost (USD) per resolved task.
     - Token efficiency (tokens per useful observation / fix).
     - Clean rollback and non-contamination rates.
  3. *Harness vs. Model Ablation*: Quantify the exact contribution of Vanguard's substrate (LDA fact graphs, 2PC transactions, and structured compaction) holding the underlying LLM constant.

## 3.2 Verification & Exit Gates
1. **Multi-Agent Verification Receipt**: An end-to-end task is planned, delegated to two parallel isolated workers, verified by an exterior oracle, and atomically merged into the target workspace with complete ledger provenance.
2. **Reproducible SOTA Evidence Envelope**: A signed, cryptographic evidence envelope containing all SQLite event logs, model invocations, tool receipts, and benchmark scores is generated, providing reproducible proof of state-of-the-art autonomous software engineering.
