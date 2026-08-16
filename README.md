# Vanguard General Task Solver (GTS)

> **A verifiable, modular meta-harness runtime that accumulates machine competence under an exterior judge it cannot game.**

---

## 1. Architectural Blueprint & Six-Plane Separation

Vanguard is structured around six distinct planes with strict OS and process-level isolation:

```text
Interaction  ── CLI · TUI · Inspector · Web Surface
     │  authenticated requests, event subscriptions
Cognition    ── Episodes · Operators · Context Compaction
     │  proposals
Control      ── Broker · Policy Kernel · Attenuation · Leases
     │  scoped capability grants
Workload     ── Sandboxed Environment Adapters (Git, FS, Shell, LSP)
     │  receipts
Evidence     ── Exterior Evaluators · Claims · Invalidation Probes
     │  unreachable verdicts
Evolution    ── Distillation · Attestation · Promotion Pointers
     └──────── signed activation pointer ──▶ Cognition
```

Every capability in the system reduces to one universal invariant protocol:
```text
observe → propose → authorise → effect → receipt → evaluate
```

---

## 2. Physical Repository Tree

```text
Aether-D-System/
├── .github/
│   └── workflows/ci.yml             # CI testing, boundary checks & PR requirement gates
├── cv13/                            # Onboarding packet & verification keys
├── docs/
│   ├── development_guides/          # Sprint briefings & leadership guidelines
│   ├── reviews/                     # Historical design reviews & AI guidelines
│   ├── agile/                       # Sprint records, Active MVP Contract, archaeology
│   │   ├── sprint0/
│   │   │   ├── active-mvp-contract.json
│   │   │   ├── system-architecture-icd.md
│   │   │   ├── verification-threat-evaluation-plan.md
│   │   │   └── schema-archaeology/
│   │   └── sprint6B/                # Current Beta-closure backlog (RELEASE NO-GO)
│   └── main_v4/                     # Normative Vanguard v4 specification corpus
│       ├── 00..12 Normative Specs
│       └── 13_C_gts_mvp_plan.md
├── schemas/
│   └── v4/                          # Canonical JSON Schema reader/writer profiles
├── test/
│   └── broken/                      # Defective mock counterparts for must-fail tests
├── tools/                           # Automated CI linters, boundary, & contract checkers
└── vanguard/
    └── packages/                    # Physical package boundaries (enforced by CI)
        ├── domain/                  # Pure values, wire contracts, and state reducers
        ├── ports/                   # Abstract interfaces (ModelPort, LedgerPort, etc.)
        │   └── fakes/               # In-memory deterministic test doubles
        ├── kernel/                  # Capability attenuation, budget leases, & dispatch
        ├── agency/                  # Episode recursion, context compiler, & operators
        ├── runtime/                 # Composition root & daemon lifecycle
        │   └── governance/          # Durable state machines, approvals, & releases
        └── adapters/                # Concrete environment implementations (Git, Model, CLI)
```

---

## 3. Package Dependency Lattice & CI Rules

Dependency direction is strictly enforced in CI (`tools/check_boundaries.py`):

$$\text{domain} \longleftarrow \text{ports} \longleftarrow \text{kernel} \longleftarrow \text{agency} \longleftarrow \text{runtime} \longrightarrow \text{adapters}$$

* **`domain`**: Imports nothing. Pure business logic, canonical serialization, and state reducers.
* **`ports`**: Imports `domain` only. Pure abstract interfaces.
* **`kernel`**: Imports `domain` and `ports`. Capability verification and budget leases.
* **`agency`**: Imports `domain`, `ports`, and `kernel`. Cognitive episode coordination.
* **`adapters`**: Imports `domain` and `ports`. Zero knowledge of kernel or cognition.
* **`runtime`**: Injects concrete adapters into ports at composition root.

---

## 4. MVP Roadmap: Waves to Lightweight Coding Agent

```
┌────────────────────────────────────────────────────────────────────────┐
│ WAVE 1: FOUNDATION & CONTRACTS (Sprint 0 – Sprint 1)                   │
│ • Sprint 0: Governance, ICD, CI boundaries, schema archaeology         │
│ • Sprint 1: Wire contracts (T1), provider probe in spike/ (T0a)        │
├────────────────────────────────────────────────────────────────────────┤
│ WAVE 2: KERNEL, LEDGER & ENGINE (Sprint 2 – Sprint 5)                  │
│ • Sprint 2: Disposable E2E slice (T0b), ledger store (T3), kernel (T2) │
│ • Sprint 3: Dispatch mediation, crash recovery, cassette replay (T3.8) │
│ • Sprint 4: Episode recursion (T4), process engine, S4 deletion gate   │
│ • Sprint 5: Exterior evaluator isolation & double probe (T5)           │
├────────────────────────────────────────────────────────────────────────┤
│ WAVE 3: TYPED CODING AGENT & BENCHMARKS (Sprint 6 – Sprint 9)          │
│ • Sprint 6: Git adapter, typed tools (read/search/patch/test), CLI TUI │
│             👉 DELIVERS: Production-grade lightweight Coding Agent     │
│ • Sprint 7: Competitor harness manifests (Claude-Code, OpenCode)       │
│ • Sprint 8: Paired McNemar runner, A/A floor, generality test (T9)     │
│ • Sprint 9: Final MVP Gate Review & Release                            │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Verification & Quality Gates

Run these commands locally to verify full compliance:

```bash
# 1. Check architectural boundary imports & cycles
python3 tools/check_boundaries.py

# 2. Check 12/12 mechanical acceptance rules
python3 tools/cv_checks.py

# 3. Check Active MVP Contract coverage
python3 tools/check_active_mvp_contract.py

# 4. Verify that must-fail tests catch broken implementations
python3 tools/run_broken_tests.py
```


## Openrouter Guidelines

- **OpenRouter**:
  - `base_url`: `https://openrouter.ai/api/v1`
  - `api_key_env`: `"OPENROUTER_API_KEY"` on `ModelRoute` (the engine reads the env var)
  - **Verified Free Models**:
    1. `openrouter/free`
    2. `inclusionai/ling-3.0-tiny:free`
    3. `poolside/laguna-s-2.1:free`
    4. `cohere/north-mini-code:free`
    5. `google/gemma-4-26b-a4b-it:free`
    6. `nvidia/nemotron-3-super-120b-a12b:free`
    7. `openai/gpt-oss-20b:free`
  - **Verified Low-Cost Paid Models**:
    8. `deepseek/deepseek-v4-flash`
    9. `xiaomi/mimo-v2.5`
  - **Frontier Cloud Models**: `z-ai/glm-5.2`, `openai/gpt-5.6-luna`, `deepseek/deepseek-v4-pro`, `minimax/minimax-m3`
- **DeepSeek API**:
  - `base_url`: `https://api.deepseek.com/v1`
  - `model`: `deepseek-reasoner` or `deepseek-coder` on `ModelRoute`
  - `api_key_env`: `"DEEPSEEK_API_KEY"`
- **OpenAI**:
  - `base_url`: `https://api.openai.com/v1`
  - `model`: `gpt-4o` on `ModelRoute`
  - `api_key_env`: `"OPENAI_API_KEY"`

## Ollama Guidelines

  - **Tier 1 models**:
    1. `llama3.2:3b`
    2. `qwen2.5:1.5b`
  - **Tier 2 models**:
    3. `qwen3.6:27b`
    4. `deepseek-r1:14b`


# SUGGESTIONS (UNDER BUDGET OF 0.5 US$)

test with these 3 openrouter free models, nvidia/nemotron-3-super-120b-a12b:free, nvidia/nemotron-3.5-lightning:free and cohere/north-
  mini-code:free to see how they fit in our tiers from 1 to 5.

  then test with these 3 openrouter medium models openai/gpt-5.6-luna, deepseek/deepseek-v4-flash-0731 and xiaomi/mimo-v2.5;

   google/gemini-3.7-flash deepseek/deepseek-v4-pro-0813 z-ai/glm-5.2 and then finally with these 3 top openrouter models
  

## Milestones — MVP Beta

This section maps what Vanguard v0.4.1 currently provides, what the framework builder can generate, and how
task complexity maps from Tier 1 (simple fixes) to Tier 5 (frontier autonomous refactoring).

---

### 1) What vg-code-default Provides Today

In the `vg-code-default` harness we currently provide:

- **Headless & TUI Coding CLI (`vg`)**: Autonomous or interactive CLI driven by a line-delimited JSON-RPC wire protocol.
- **Typed sandboxed effect verbs (5)**:
  - `fs.read` — Scoped file reading inside a Bubblewrap container.
  - `fs.search` — Pattern matching and regex workspace searching.
  - `fs.write` — Atomic file writes with path sanitization.
  - `patch.apply` / `fs.patch` — Descriptor-bound unified-diff application with human signoff.
  - `proc.exec` — Containerized test execution (`pytest`, `unittest`, `npm test`) in isolated namespaces.
- **Prefix-stable context memory (L1–L5)**: Byte-stable system prompts and tool schemas (L1–L3) for KV-cache reuse; mid-run observations are admitted only into L5.
- **Asymmetric human approval (Ed25519)**: Operator signs the exact normalized diff before any state mutation.
- **Durable ledger recovery & idempotency**: SQLite WAL ledger records every EffectIntent and Receipt; on restart it resumes at the next legal transition without re-querying the model.
- **Exterior UID 10002 verification**: Results evaluated by an out-of-process test daemon with double probes (immutable oracle, non-polluting workspace).

---

### 2) What the Framework Builder Can Create (Harness Manifests)

The Vanguard engine is domain-agnostic (ADR-0060). New harnesses can be declared by adding a manifest directory, for example:

```text
my-custom-harness/
├── manifest.json         # capability declarations, risk levels, budget ceilings, evaluator IDs
├── system-prompt.txt     # specialized system persona / brief
├── tool-schemas/         # JSON Schemas for custom tools
├── budget-policy.json    # USD micros, wall-clock, token, and byte ceilings
└── context-policy.json   # compaction and layer-retention rules
```

Decoupled extension primitives include:

- **Custom tool schemas & verbs** — Bind domain verbs (e.g. `db.query`, `web.fetch`, `docker.build`, `ast.analyze`, `git.rebase`) to sandboxed adapter factories.
- **Domain-specific risk & approval policies** — Assign risk levels (low/medium/high/critical) per verb to trigger human approval, external key verification, or auto-grants.
- **Custom model providers & routing** — Target local models (Ollama), deterministic offline mocks (LAM), or cloud providers (OpenRouter, OpenAI, Anthropic) behind a single `ModelPort`.
- **Pluggable exterior evaluators** — Swap unit-test evaluators for web regression checkers, AST linters, or formal-verification solvers (UID 10002).

---

### 3) Task Complexity Hierarchy & 5-Tier Model Escalation Ladder

Our architecture enforces a 5-tier model escalation ladder. Tiers 1–2 run exclusively on free local GPU models (Ollama). Tiers 3–5 escalate to cloud models (OpenRouter) as task complexity increases:

| Tier | Complexity & Scope | Assigned Models (In Escalation Order) | Platform | Example Tasks |
| :--- | :--- | :--- | :--- | :--- |
| **Tier 1** | Single-file syntactic & typo fixes | `qwen2.5:1.5b` → `llama3.2:3b` | **Local Ollama** ($0) | Fix syntax errors, update static text, single-function deduplication (< 5s) |
| **Tier 2** | Multi-file dependency repair | `deepseek-r1:14b` → `qwen3.6:27b` | **Local Ollama** ($0) | Fix off-by-one bugs, resolve circular imports, run unit tests and diffs |
| **Tier 3** | Subdirectory refactor & search | `openrouter/free` → `poolside/laguna-s-2.1:free` → `nvidia/nemotron-3.5-lightning:free` → `cohere/north-mini-code:free` → `qwen/qwen3.7-flash` | **Cloud OpenRouter** (Light) | Multi-file features, sha256 digests across packages using `list_dir` and `grep_file` |
| **Tier 4** | Subsystem refactoring & workflows | `google/gemma-4-26b-a4b-it` → `qwen/qwen3.6-35b-a3b` → `deepseek/deepseek-v4-flash-0731` | **Cloud OpenRouter** (Mid) | Resolve state machine transitions, multi-step approval workflows, async race conditions |
| **Tier 5** | Autonomous SOTA refactoring | `openai/gpt-5.6-luna` → `z-ai/glm-5.2` → `deepseek/deepseek-v4-pro-0813` → `google/gemini-3.7-flash` | **Cloud OpenRouter** (Frontier SOTA) | Complex compiler module extraction, Persistent Immutable AVL Trees, full repo rebalancing |

> **Offline Mock Acceleration:** Once a successful trace is recorded for any tier, the **LAM Engine** (`tools/002_LLM_API_MOCK`) replays the exact multi-turn cascade offline in **< 20 ms for $0**.

---

### 4) Path to a "Claude Code" / "OpenCode" Competitor

To evolve `vg-code-default` into a frontier-grade harness (`vg-code-frontier`), add the following primitives:

1. **Interactive workspace map** (`repo.tree` / `ast.search`) — high-level semantic context indexing.
2. **Terminal shell co-pilot** (`proc.interactive`) — safe shell execution inside Bubblewrap with real-time stream parsing.
3. **Multi-file diff staging** (`patch.bundle`) — atomic multi-file transaction patches.
4. **Correction memory & self-improvement** — persist human corrections (RecordCorrection) into competence artifacts so the agent learns and avoids repeating the same mistakes.

---

### Original (preserved raw content)

The following is the original Milestones block preserved verbatim to ensure no content was removed during formatting.

```markdown
# MILESTONES MVP BETA

Here is the exact mapping of what our v0.4.1 codebase currently has, what the framework builder engine can
  create in a decoupled way, and how general + coding tasks map from Tier 1 (Simple Fixes) to Tier 5 (Frontier
  Autonomous Refactoring like Claude Code / OpenCode).
  ──────
  ## 1. What Features Our v0.4.1 Harness (vg-code-default) Has Today

  In our codebase (vg-code-default), the vg-code-default harness provides:

  1. Headless & TUI Coding CLI (vg): Autonomous or interactive CLI execution driven by line-delimited JSON-RPC
  wire protocol.
  2. 5 Typed Sandboxed Effect Verbs:
      • fs.read — Scoped file reading inside Bubblewrap container.
      • fs.search — Pattern matching & regex workspace searching.
      • fs.write — Atomic file write with path sanitization.
      • patch.apply / fs.patch — Descriptor-bound unified diff application with human signoff.
      • proc.exec — Containerized test execution (pytest, unittest, npm test) inside isolated namespaces.
  3. Prefix-Stable Context Memory (L1–L5): Maintains byte-stable system prompts & tool schemas (L1–L3) for zero-
  cost KV-cache reuse, admitting mid-run tool observations only into L5.
  4. Asymmetric Human Approval (Ed25519): Interactive signoff where the operator holds the private key and signs
  the exact normalized diff before any state-mutating patch application.
  5. Durable Ledger Recovery & Idempotency: SQLite WAL transaction log that records every EffectIntent and
  Receipt. On crash/restart, it resumes at the exact next legal transition without calling the LLM again.
  6. Exterior UID 10002 Verification: Evaluates results using an out-of-process test daemon with double probes
  (immutability of test oracle and non-pollution of workspace).
  ──────
  ## 2. What Features the Framework Builder Can Create for New Harnesses (Decoupled Decoupled Plugins)

  The Vanguard framework is 100% domain-agnostic (ADR-0060). The engine (kernel/ and agency/episode/) has zero
  hardcoded coding logic. You can build entirely new agentic harnesses simply by declaring a new manifest
  directory without touching core runtime code:

    my-custom-harness/
      ├── manifest.json         # Capability declarations, risk levels, budget ceilings, evaluator IDs
      ├── system-prompt.txt     # Specialized system persona / Brief
      ├── tool-schemas/         # JSON Schemas for custom tools
      ├── budget-policy.json    # USD micros, wall-clock, token, and byte ceilings
      └── context-policy.json   # Compaction and layer retention rules

  ### Decoupled Extension Primitives:

  • Custom Tool Schema & Verbs: Bind any domain verb (db.query, web.fetch, docker.build, ast.analyze, git.
  rebase) to a corresponding sandboxed adapter factory.
  • Domain-Specific Risk & Approval Policies: Assign risk levels (low, medium, high, critical) per verb to
  automatically trigger human approval, external key verification, or auto-grant.
  • Custom Model Providers & Routing: Target local models (Ollama), deterministic offline mocks (LAM), or cloud
  providers (OpenRouter, OpenAI, Anthropic) behind one invariant ModelPort.
  • Pluggable Exterior Evaluators: Swap out Python unit test evaluators for Web regression checkers, AST linter
  validators, or formal verification solvers under UID 10002.
  ──────
  ## 3. Task Complexity Hierarchy: Tier 1 to Tier 5 (Claude Code / OpenCode Competence)

   Task Tier │ Task Complexity Level          │ Features Utilized in Vanguard  │ Concrete Task Examples
  ───────────┼────────────────────────────────┼────────────────────────────────┼────────────────────────────────
    Tier 1   │ Single-File Syntactic & Typos  │ fs.read, fs.write,             │ • Fix syntax errors & broken
             │ (Simple)                       │ ContextCompiler L1–L5.         │ imports.• Update static text
             │                                │                                │ strings or docstrings.•
             │                                │                                │ Correct minor variable typos
             │                                │                                │ in a single function.
    Tier 2   │ Single-Unit Bug Fix & Test     │ fs.read, fs.search, proc.exec, │ • Off-by-one error repair in
             │ Repair (Intermediate)          │ patch.apply, Ed25519 approval. │ an algorithm.• Run unit test,
             │                                │                                │ observe failure output, apply
             │                                │                                │ diff, verify green test.• Fix
             │                                │                                │ failing API response parsing.
    Tier 3   │ Multi-File Feature             │ Unified Sandbox Worker         │ • Implement a new REST
             │ Implementation (Advanced)      │ (bwrap), Context L5 dialogue   │ endpoint across router,
             │                                │ memory, Multi-turn             │ controller, service, and DB
             │                                │ LAM/OpenRouter loop, Exterior  │ layers.• Add a new command to
             │                                │ Evaluator UID 10002.           │ the CLI client.• Refactor a
             │                                │                                │ module into sub-packages while
             │                                │                                │ keeping tests green.
    Tier 4   │ Subsystem Refactoring &        │ Durable SQLite Recovery,       │ • Resolve complex async race
             │ Diagnostic Repair (Frontier -  │ Ed25519 Descriptor Signing,    │ conditions across multiple
             │ Opus Class)                    │ Competence Prior Recording,    │ services.• Upgrade major
             │                                │ Multi-turn tool feedback       │ framework dependency (e.g.,
             │                                │ loops.                         │ Python 3.10 → 3.12 or React 17
             │                                │                                │ → 18).• Fix multi-file state
             │                                │                                │ leakage or memory leak
             │                                │                                │ reported by benchmarks.
    Tier 5   │ Autonomous Agentic Coding CLI  │ Full Vanguard Stack + vg-code- │ • Full Repository Exploration
             │ (Claude Code / OpenCode Goal)  │ default harness pack + Shell   │ & Blueprinting: Auto-discover
             │                                │ Execution Worker + Self-       │ workspace topology, run tests,
             │                                │ Correction & Distillation.     │ synthesize fix plan.•
             │                                │                                │ Autonomous Multi-Hypothesis
             │                                │                                │ Debugging: Branch workspace,
             │                                │                                │ execute experiments, pick
             │                                │                                │ optimal patch.• Interactive
             │                                │                                │ Human Co-Pilot: Present diffs,
             │                                │                                │ accept live corrections,
             │                                │                                │ update competence memory.
  ──────
  ## 4. Path to Building Our Own "Claude Code CLI / OpenCode"

  With Vanguard v0.4.1, we have built the secure, durable, sandboxed kernel and protocol foundation.

  To turn Vanguard into a full Claude Code / OpenCode CLI competitor, we simply add a higher-tier harness pack
  (vg-code-frontier) containing:

  1. Interactive Workspace Map Tool (repo.tree / ast.search): High-level semantic context indexing.
  2. Terminal Shell Co-Pilot Tool (proc.interactive): Safe shell execution inside Bubblewrap with real-time
  stream parsing.
  3. Multi-File Diff Staging (patch.bundle): Multi-file atomic transaction patches.
  4. Correction Memory & Self-Improvement: Persisting human feedback (RecordCorrection) into

    G
     C

  competence artifacts so the agent avoids repeating past user corrections.
```

