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