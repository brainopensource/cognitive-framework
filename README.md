# Vanguard General Task Solver (GTS)

> **A SOTA verifiable, modular meta-harness runtime that accumulates machine competence under an exterior judge it cannot game.**

[![Vanguard Core Integrity](https://img.shields.io/badge/Vanguard-v0.4.5--beta-blue.svg)](docs/scrum/sprints/wave20/evidence/s20-g-03-release-claims.md)
[![Architecture](https://img.shields.io/badge/Architecture-Hexagonal_plane_separated-green.svg)](docs/main_v4/03_vanguard_architecture_planes_and_execution_model_v040.md)
[![Verification](https://img.shields.io/badge/Tests-488_passed-success.svg)](tools/run_active_contract_tests.py)
[![TCB Budget](https://img.shields.io/badge/TCB_LOC-1315%2F1438-brightgreen.svg)](tools/check_tcb_budget.py)

---

## 1. Executive Summary & Core Thesis

Vanguard is an agentic coding and general task solver framework built on a fundamental security and architectural thesis (`VG-02`):

> **When an agent solves a task, what solved it — model, scaffold, prompt, tools, context policy, retry — must be separable, and the judge must be unreachable from the judged.**

Vanguard enforces an invariant, deterministic turn lifecycle across all domains:
```text
observe ──▶ propose ──▶ authorize ──▶ effect ──▶ receipt ──▶ evaluate
```

---

## 2. Orders of Abstraction & Biological Framework Dictionary

Vanguard conceptualizes software architecture using a **Biological Hierarchy of Emergent Competence**.

> [!IMPORTANT]
> **Architectural Invariant (GTS-13C §3.6):** The biological vocabulary is **NOT an OOP class hierarchy** (we do *not* write `class Cell(Polymer)`). It is a conceptual taxonomy and an **emergent telemetry depth** logged in `lam.sqlite`. Build one recursive coordinator, and the biological hierarchy becomes an empirical finding in the ledger.

```text
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│ LEVEL 9: ENTITY / AGI SWARM       ──▶ Autonomous Multi-Agent Orchestration & Swarm Topology │
│ LEVEL 8: ORGANS & SYSTEMS         ──▶ Paired Measurement Lab (`lab harness bench`)          │
│ LEVEL 7: CELLS                    ──▶ Sandboxed Autonomous Agent Workspace & Lifecycle      │
│ LEVEL 6: ORGANELLES               ──▶ Exterior Signed Evaluator (UID 10002) & Double Probes │
│ LEVEL 5: GENES (DNA / RNA)        ──▶ Declarative Manifest Packs (`vg-code-*`, `AGENTS.md`)  │
│ LEVEL 4: PROTEINS & ENZYMES       ──▶ Context Compactor (L1–L5) & `ProposalTranslator`      │
│ LEVEL 3: LINEAR POLYMERS          ──▶ `EpisodeEngine` Depth-1 Multi-Turn Recursion Loop     │
│ LEVEL 2: MOLECULES                ──▶ Attenuation Kernel & Rootless Bubblewrap Sandbox       │
│ LEVEL 1: ATOMS                    ──▶ Abstract Ports (`ModelPort`) & Single Verbs (`fs.read`)│
│ LEVEL 0: SUB-ATOMIC PRIMITIVES    ──▶ Canonical Wire Value Objects, Hashes & Ed25519 Keys   │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Biological Dictionary: From Primitives to Emergent AGI

| Biological Tier | Biological Analogy | Vanguard Code Component & Realization | Emergent Competence |
|---|---|---|---|
| **0. Sub-Atomic** | Protons, Neutrons, Electrons (Pure energy/charge, no chemistry alone) | `domain/wire/contracts.py`: Canonical Value Objects, SHA-256 digests, Ed25519 asymmetric keys, JsonSchema contracts. | **Byte-Level Determinism** |
| **1. Atoms** | Carbon, Hydrogen, Oxygen (Periodic table elements with valency & affinity) | `ports/`: `ModelPort`, `LedgerPort`, `EvaluatorPort`; Single Verbs (`fs.read`, `fs.search`, `fs.write`, `patch.apply`, `proc.exec`). | **Capability Valency** |
| **2. Molecules** | Water, Glucose, Amino Acid Monomers (Atoms bound into functional units) | `kernel/dispatch.py`, `adapters/sandbox/rootless.py`: Attenuation Kernel, USD micro-budget leases, rootless Bubblewrap containerization. | **Sandboxed Isolation** |
| **3. Linear Polymers** | Unfolded Peptide Chains (Sequential monomers linked in series) | `agency/episode/engine.py`: `EpisodeEngine` depth-1 sequential multi-turn recursion (`observe → propose → authorize → effect → receipt → evaluate`). | **Multi-Turn Traceability** |
| **4. Functional Proteins** | Folded Enzymes & Molecular Motors (Folded polymers with active chemical catalytic function) | `agency/context/compiler.py`, `adapters/models/invocation.py`: L1–L5 Context Compactor, byte-stable system prompts, `ProposalTranslator`. | **Cognitive Pruning & Efficiency** |
| **5. Genes (DNA / RNA)** | Nucleic Acid Sequence Manuals (Instructions dictating protein assembly) | `agency/manifests/`: Pure-data JSON Manifests (`vg-code-claude-shaped`, `vg-code-opencode-shaped`), `AGENTS.md` / `CLAUDE.md` context discovery. | **Declarative Harness Alignment** |
| **6. Organelles** | Mitochondria, Ribosomes (Membrane-bound functional cellular machinery) | `adapters/evaluators/daemon.py`: Out-of-process signed Evaluator Daemon (UID `10002`) running sealed double probes. | **Un-gameable Verification** |
| **7. Cells** | Single-cell Organisms (Self-contained, bounded factory operating continuously under DNA instructions) | `runtime/root.py`, `runtime/coordination.py`: Autonomous Agent Workspace runtime executing episodes end-to-end. | **Autonomous Problem Solving** |
| **8. Organs & Systems** | Tissues, Muscular & Nervous Systems (Coordinated specialized cell groups) | `lab/`: Paired Measurement Laboratory (`lab harness bench`), McNemar A/A floor tracking against undeletable `vg-shell-only`. | **Empirical Benchmark Laboratory** |
| **9. Entity / AGI Swarm** | Conscious Macro-Organism (Harmonious coordination of trillions of specialized nanomachines) | `runtime/governance/`: Multi-Agent Competence Distillation (`O-01`), Cross-Agent Delegation, and Heterogeneous Swarm Orchestration. | **Emergent Machine AGI** |

---

## 3. Six-Plane Architectural Blueprint

Vanguard isolates responsibilities into six decoupled planes ([`03_vanguard_architecture_planes_and_execution_model_v040.md`](docs/main_v4/03_vanguard_architecture_planes_and_execution_model_v040.md)):

```text
Interaction  ──▶ CLI · TUI · Inspector · Web Surface
                     │ (authenticated RPC requests)
Cognition    ──▶ Episodes · Operators · Context Compaction (L1–L5)
                     │ (proposals)
Control      ──▶ Broker · Attenuation Kernel · Leases · Ed25519 Approvals
                     │ (scoped capability grants)
Workload     ──▶ Sandboxed Environment Adapters (Git, FS, Shell, LSP)
                     │ (execution receipts)
Evidence     ──▶ Exterior Evaluators (UID 10002) · Claims · Oracle Probes
                     │ (unreachable signed verdicts)
Evolution    ──▶ Distillation · Attestation · Promotion Pointers (O-01)
```

---

## 4. Repository Structure & Package Lattice

```text
Aether-D-System/
├── .github/workflows/ci.yml         # Boundary, TCB, secret scan, & test CI gates
├── benchmarkings/                   # Empirical benchmark suites & live zero-hint runners
├── containers/                      # OCI build files & manifest.json digests
│   ├── worker.Dockerfile            # Bubblewrap worker container (UID 10001)
│   ├── evaluator.Dockerfile         # Signed evaluator daemon container (UID 10002)
│   └── manifest.json                # Immutable release build SHA-256 digests
├── docs/
│   ├── main_v4/                     # Normative Vanguard v4 Specification Corpus (VG-00..12, GTS-13C)
│   ├── reviews/done/                # S7–S10 Master Architectural Roadmap
│   └── agile/sprint6B/              # Gate R0–R10 release evidence & dogfood log
├── tools/                           # Boundary check, TCB budget, secret scan, & dogfood tools
└── vanguard/packages/               # Physical package boundaries (enforced in CI)
    ├── domain/                      # Pure values, wire contracts, state reducers (Order 0)
    ├── ports/                       # Abstract interfaces & in-memory fakes (Order 1)
    ├── kernel/                      # Attenuation kernel, budget leases, dispatch (Order 2)
    ├── agency/                      # Context compiler, proposal translator, episode engine (Order 3)
    │   └── manifests/               # Data-only harness configurations (Order 4)
    ├── runtime/                     # Composition root & daemon lifecycle
    │   └── governance/              # Ed25519 approval flow & release signoff
    └── adapters/                    # Concrete adapters (Model, Sandbox, Evaluator) (Order 1/2/5)
```

### CI Architectural Boundary Lattice

Import direction is strictly unidirectional (`tools/check_boundaries.py`):

$$\text{domain} \longleftarrow \text{ports} \longleftarrow \text{kernel} \longleftarrow \text{agency} \longleftarrow \text{runtime} \longrightarrow \text{adapters}$$

- **`domain`**: Standard library only. Imports nothing else in the repository.
- **`ports`**: Imports `domain` only.
- **`kernel`**: Imports `domain` and `ports`.
- **`agency`**: Imports `domain`, `ports`, and `kernel`.
- **`adapters`**: Imports `domain` and `ports`. Zero direct imports of `kernel` or `agency`.
- **`runtime`**: Composition root injecting concrete adapters into abstract ports.

---

## 5. Master Roadmap & Sprint Overview

```text
┌──────────────────────────────────────────────────────────────────────────────────────┐
│ PHASE 1 & 2: FOUNDATION, KERNEL & BETA RELEASE (Sprint 0 – Sprint 6B) [COMPLETE]      │
│ • Sprint 0–1: Governance, ICD, CI boundaries, wire contracts (T1)                   │
│ • Sprint 2–5:  Ledger store, attenuation kernel (T2), Episode recursion (T4), UID 10002 │
│ • Sprint 6A-B: Rootless Bubblewrap worker, Ed25519 approval, Gate R9 Dogfood 3/3 PASS│
│                👉 DELIVERS: Vanguard MVP Beta v0.4.1-beta Release Candidate           │
├──────────────────────────────────────────────────────────────────────────────────────┤
│ PHASE 3: HARNESS RECONSTRUCTIONS, MEASUREMENT & RELEASE (Sprint 7 – Sprint 10)       │
│ • Sprint 7: Pure-data manifests (`vg-code-claude-shaped`, `vg-code-opencode-shaped`),  │
│             aliases.json translation, dynamic `AGENTS.md` context discovery          │
│ • Sprint 8: Laboratory bench (`lab harness bench`), paired A/A control against       │
│             `vg-shell-only`, verifier-deployment gap measurement                     │
│ • Sprint 9: TableWorld non-coding structured-data witness with zero kernel changes   │
│ • Sprint 10: Non-authoritative memory recall (L5), offline distillation (O-01),     │
│              and Phase 3 release gate dossier                                        │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Model Escalation & Routing Hierarchy

Vanguard abstracts models behind `ModelPort`. Local GPU models ($0) handle routine syntactic tasks, while cloud models (OpenRouter/OpenAI/Anthropic) handle high-tier refactoring:

# Openrouter Guidelines

    OpenRouter:
        base_url: https://openrouter.ai/api/v1
        api_key_env: "OPENROUTER_API_KEY" on ModelRoute (the engine reads the env var)
        Verified Free Models:
            openrouter/free
            inclusionai/ling-3.0-tiny:free
            poolside/laguna-s-2.1:free
            cohere/north-mini-code:free
            google/gemma-4-26b-a4b-it:free
            nvidia/nemotron-3-super-120b-a12b:free
            openai/gpt-oss-20b:free
        Verified Low-Cost Paid Models: 8. deepseek/deepseek-v4-flash 9. xiaomi/mimo-v2.5
        Frontier Cloud Models: z-ai/glm-5.2, openai/gpt-5.6-luna, deepseek/deepseek-v4-pro, minimax/minimax-m3
    DeepSeek API:
        base_url: https://api.deepseek.com/v1
        model: deepseek-reasoner or deepseek-coder on ModelRoute
        api_key_env: "DEEPSEEK_API_KEY"
    OpenAI:
        base_url: https://api.openai.com/v1
        model: gpt-4o on ModelRoute
        api_key_env: "OPENAI_API_KEY"

Ollama Guidelines

    Tier 1 models:
        llama3.2:3b
        qwen2.5:1.5b
    Tier 2 models: 3. qwen3.6:27b 4. deepseek-r1:14b


---

## 7. Verification & Release Verification Commands

Verify repository integrity, boundaries, TCB budget, and test suite locally:

```bash
# 1. Verify Backend Artifacts & OCI Image Manifests (--release)
python3 tools/check_backend_artifacts.py --release

# 2. Check Package Import Boundaries (115 source files)
python3 tools/check_boundaries.py

# 3. Check Kernel Trusted Computing Base (TCB) LOC Budget (Limit <= 1438 LOC)
python3 tools/check_tcb_budget.py

# 4. Check Secret Patterns Across Repository
python3 tools/scan_secrets.py

# 5. Run Sprint 6B Gate R9 Production Dogfood (3/3 PASS)
python3 tools/run_dogfood_r9.py

# 6. Execute Complete Unit Test Suite (488/488 Tests Green)
python3 -m unittest discover -s test -t .
```

---

## 8. Alignment Matrix with `docs/main_v4`

| Specification File | Purpose in Vanguard | Alignment Status |
|---|---|---|
| [`00_vanguard_registry_v040.md`](docs/main_v4/00_vanguard_registry_v040.md) | Document index, precedence rules (`PR-3`), & terminology | **Fully Aligned** |
| [`01_vanguard_engineering_handbook_v040.md`](docs/main_v4/01_vanguard_engineering_handbook_v040.md) | Engineering guidelines & architecture standards | **Fully Aligned** |
| [`02_vanguard_charter_claims_and_non_claims_v040.md`](docs/main_v4/02_vanguard_charter_claims_and_non_claims_v040.md) | Non-claims, separability thesis, & negative result validity | **Fully Aligned** |
| [`03_vanguard_architecture_planes_and_execution_model_v040.md`](docs/main_v4/03_vanguard_architecture_planes_and_execution_model_v040.md) | Six-plane separation & universal turn lifecycle | **Fully Aligned** |
| [`05_vanguard_kernel_capabilities_and_security_v040.md`](docs/main_v4/05_vanguard_kernel_capabilities_and_security_v040.md) | Capability attenuation, budget leases, & kernel security | **Fully Aligned** |
| [`09_vanguard_decision_register_v040.md`](docs/main_v4/09_vanguard_decision_register_v040.md) | Architectural Decision Records (ADRs) | **Fully Aligned** |
| [`13_C_gts_mvp_program_and_engineering_plan.md`](docs/main_v4/13_C_gts_mvp_program_and_engineering_plan.md) | GTS MVP program plan, sprint definitions, & Ch.10 gate questions | **Fully Aligned** |





Subatômico (Prótons, Nêutrons e Elétrons): Os tijolos de energia e carga elétrica pura. Sozinhos, não têm química.

Átomos (Carbono, Hidrogênio, Oxigênio...): Quando os prótons e elétrons se juntam, emergem os elementos da tabela periódica. Eles ganham propriedades como "afinidade" ou "repulsão" por outros átomos.

Moléculas (Aminoácidos, Água, Glicose): Átomos se ligam. Um átomo de carbono sozinho não faz nada, mas quando se junta com hidrogênio, nitrogênio e oxigênio na ordem certa, emerge um aminoácido (a célula da sua linha de montagem).

Polímeros - Linear: As moléculas pequenas (monômeros) se ligam em uma fita única e contínua. Aqui emerge a propriedade do dobramento e da forma tridimensional.

Polimero - Proteinas e Enzimas: O polímero se dobra e ganha uma função mecânica ou química. Agora ele é uma ferramenta ativa (a tesoura, o motor, a chave).

Polimero - Genes (DNA / RNA): São polímeros de outro tipo (ácidos nucleicos) que guardam a informação e a ordem exata para a fábrica de proteínas funcionar. O DNA é o "manual de instruções" da fábrica.

Organelas (Mitocôndrias, Ribossomos): São formadas quando membranas de gordura (lipídios) encapsulam grupos de proteínas funcionais para trabalharem juntas. A mitocôndria vira a usina de energia; o ribossomo vira a linha de montagem.

Células: A primeira unidade que consideramos "viva". É o fechamento da fábrica. Uma célula é uma cidade fechada onde bilhões de proteínas (polímeros dobrados) trabalham sem parar, seguindo as ordens do DNA, para manter a estrutura funcionando e se duplicando.

Órgãos (Músculo, Coração): Bilhões de células trabalhando juntas de forma coordenada.

Entity: Um sistema consciente feito de trilhões de nanomáquinas que sequer sabem que você existe, mas que trabalham em perfeita harmonia.
