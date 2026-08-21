 # ROLE
 
 Act as the collective leadership body — the **Leadership 7**:
 
    1. Engineering Director
    2. Chief Technology Officer (CTO)
    3. Chief Information Officer (CIO)
    4. Principal Staff Engineer
    5. Principal Systems Architect
    6. Tech Lead
    7. PhD AI Specialist (Cognitive Systems & Reinforcement Learning)

### Context & Reading:
Read the master briefing in `docs/00_overview/SYSTEM_OVERVIEW.md`. It provides the complete codebase
map, verified test evidence, the Clean Triad, the 3 Planes of Responsibility (Decision, State,
Evidence), and catalogues all active ADRs, reviews (`docs/07_reviews/`), and research papers
(`docs/06_references/`).

### Your Task:
Conduct an executive review of the system and formulate the phased technical plan for the upcoming
versions (**v0.6.1**, **v0.6.2**, **v0.6.3** leading to **v0.X.0** decide how many versions we need).

1. **Review Open Decision Points & Trade-offs:**
     - Evolving `harness.yaml` from fixed slots to a dynamic **Named Component Graph**.
     - Populating per-turn model token costs and fingerprints into `trajectory.py` (NOVA-1) to un-
hollow the training dataset.
     - Formalizing the "Absent-vs-Forged" guardrail model for non-coding packs.
     - Mediating `agent.spawn` as a capability verb (Design in Waves 1–4, implementation post-M-4).
     - Final absorption sequence of `layer0/registry` and `layer0/compose` into
`vanguard/packages/runtime/`.

2. **Produce the Phased Milestone Plan:**
     - Define the exact goals, entry/exit gates, and scope boundaries for each release (**v0.6.1**,
**v0.6.2**, **v0.6.3**, **v0.7.0**, **v0.8.0** you decide how many).
     - Incrementally harden the foundational architecture before unlocking higher-order emergence (M-5
through M-10).
     - Formalize decisions into a list of proposed append-only ADRs (`0077+`) and specify which
documents and wave plans will be updated.





























# Wave 2B - Decision Lock 

# ROLE

Act as the collective leadership body — the Leadership 7:

  1. Engineering Director
  2. Chief Technology Officer (CTO)
  3. Chief Information Officer (CIO)
  4. Principal Staff Engineer
  5. Principal Systems Architect
  6. Tech Lead
  7. PhD AI Specialist (Cognitive Systems & Reinforcement Learning)
  ──────
## ⚠️ MANDATORY PRE-REQUISITE: Research & Forensic Code Verification

  Before making any determinations or formulating the roadmap, you must strictly ground your decisions
  in rigorous external literature and verified codebase evidence:

  1. Active Web / Internet Research: Perform web searches on frontier multi-agent architectures,
  capability-based sandboxing, active inference in LLM agent loops, verifiable execution provenance DAGs,
  and reinforcement learning over trajectory graphs to incorporate industry-leading SOTA.
  2. Internal Research Literature (docs/06_references/): Thoroughly review our foundational research (e.
  g., RESEARCH_k3_harness-suggestion.md, RESEARCH_THEORETICAL_SYNTHESIS.md,
  RESEARCH_harness_agentic_coding_builder_research_and_framework.md, etc.) to understand the
  mathematical and cognitive rationale behind the A-B-C-D operating model.
  3. Principal Staff Engineering Reviews (docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/): Audit all
  principal reviews (including 002_V060_FOUNDATION_ROADMAP_AND_GAP_REGISTER.md,
  005_V061_SUBSTRATE_GENERALITY_REVIEW.md, 006_V061_aether-substrate-briefing.md) to evaluate existing
  gap registers, falsifiers, and substrate generality blueprints.
  4. Forensic Code Verification (vanguard/packages/): Cross-reference all claims against the living code
  on disk—inspecting the TCB Kernel (kernel/), the Event Store & Runtime (runtime/), the Exterior
  Sandbox/Evaluator (adapters/), Ports (ports/), and Domain Contracts (domain/) to ensure every proposal
  respects verified invariants and the Clean Triad.
  ──────

# Context & Primary Briefing:

Read the master briefing in docs/00_overview/SYSTEM_OVERVIEW.md. It provides the complete codebase
map, verified test evidence, the Clean Triad, the 3 Planes of Responsibility (Decision, State,
Evidence), and catalogues all active ADRs, reviews, and research assets.
──────
## Your Task:

Conduct an executive review of the system and formulate the phased technical plan for the upcoming
versions (v0.6.1, v0.6.2, v0.6.3 leading to v0.X.0 — determine the exact version milestones needed).

1. Review Open Decision Points & Trade-offs:
     • Evolving harness.yaml from fixed slots into a dynamic Named Component Graph (enabling debate,
     tree-search, reflection loops, and swarms without kernel modifications).
     • Populating per-turn model token costs and fingerprints into trajectory.py (NOVA-1) to un-hollow
     the training dataset.
     • Formalizing the "Absent-vs-Forged" guardrail model for non-coding packs.
     • Mediating agent.spawn as a capability verb (Design in Waves 1–4, implementation post-M-4).
     • Final absorption sequence of layer0/registry and layer0/compose into vanguard/packages/runtime/.
2. Produce the Phased Milestone Plan:
     • Define exact goals, entry/exit gates, and scope boundaries for each release (v0.6.1, v0.6.2, v0.
     6.3, v0.7.0, v0.8.0, etc.).
     • Incrementally harden the foundational architecture before unlocking higher-order emergence (M-5
     through M-10).
     • Formalize decisions into a list of proposed append-only ADRs (0077+) and specify which documents
     and wave plans will be updated.





























# PROMPT 3 — Comprehensive Single-File Architectural Mandate & Meta-Framework Proposal

# ROLE

Act as the collective leadership body — the **Leadership 7**:

  1. Engineering Director (Authority, Governance, Stop Lines)
  2. Chief Technology Officer (CTO - Moat, SOTA Alignment & Macro Strategy)
  3. Chief Information Officer (CIO - Auditability, Traceability & Security)
  4. Principal Staff Engineer (Gap Register & Substrate Generality)
  5. Principal Systems Architect (Boundary Lattice & TCB Invariants)
  6. Tech Lead (Sprint Execution & Zero-Guesswork Dev Bridge)
  7. PhD AI Specialist (Cognitive Systems, Active Inference & Reinforcement Learning)

──────

## ⚠️ MANDATORY PRE-REQUISITE: SOTA Research & Forensic Code Verification

Before making any determinations or formulating the technical roadmap, you must strictly ground your decisions in rigorous external literature and verified codebase evidence:

1. **Active Web / Internet Research:** Perform search queries on frontier multi-agent architectures (2025–2026 SOTA), capability-based sandboxing, active inference in LLM agent loops (VFE minimization), verifiable execution provenance DAGs, and reinforcement learning over trajectory graphs (ASTRA, DPO) to incorporate industry-leading paradigms.
2. **Internal Research Literature (`docs/06_references/`):** Thoroughly review our foundational research (e.g., `RESEARCH_k3_harness-suggestion.md`, `RESEARCH_THEORETICAL_SYNTHESIS.md`, `RESEARCH_harness_agentic_coding_builder_research_and_framework.md`, etc.) to understand the mathematical and cognitive rationale behind the A-B-C-D operating model.
3. **Principal Staff Engineering Reviews (`docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/`):** Audit all principal reviews (including `002_V060_FOUNDATION_ROADMAP_AND_GAP_REGISTER.md`, `005_V061_SUBSTRATE_GENERALITY_REVIEW.md`, `006_V061_aether-substrate-briefing.md`) to evaluate existing gap registers, falsifiers, and substrate generality blueprints.
4. **Forensic Code Verification (`vanguard/packages/`):** Cross-reference all claims against the living code on disk—inspecting the TCB Kernel (`kernel/`), the Event Store & Runtime (`runtime/`), the Exterior Sandbox/Evaluator (`adapters/`), Ports (`ports/`), and Domain Contracts (`domain/`) to ensure every proposal respects verified invariants and the Clean Triad.

──────

# Context & Primary Briefing:

Read the master briefing in `docs/00_overview/SYSTEM_OVERVIEW.md`. It provides the complete codebase map, verified test evidence, the Clean Triad, the 3 Planes of Responsibility (Decision, State, Evidence), and catalogues all active ADRs, reviews, and research assets.

──────

## Strict Output Constraint: Single Comprehensive Document

> **MANDATORY INSTRUCTION:** Do **NOT** edit any existing specification files, ADRs, or codebase source files. Instead, produce **ONE SINGLE COMPREHENSIVE REPORT** in the repository root called `007_zeta_review_full_opus_proposal.md`.

──────

## Your Task:

Conduct an exhaustive executive review of the system and formulate the definitive technical proposal and phased implementation plan for evolving AETHER from a coding substrate into a **general task-solving swarm meta-framework** across versions (**v0.6.1**, **v0.6.2**, **v0.6.3**, **v0.7.0**, **v0.8.0**, **v0.9.0**, **v1.0.0**).

In your single document (save in the root your final report), you must detail with extreme technical depth and mathematical rigor:

1. **Executive Rulings & Strategic Paradigm Shift:**
   - The consensus and mandates of the Leadership 7.
   - SOTA 2026 alignment (Harness Engineering, Stigmergic Swarms via State Plane vs. $O(N^2)$ chatter, Separability Thesis, A-B-C-D Foundation).

2. **Adjudication of All Open Architectural Tensions (T-1 through T-9):**
   - Evolving `harness.yaml` into a dynamic **Named Component Graph** (enabling debate, tree-search, critic loops, and swarms without engine changes).
   - Eliminating the hollow trajectory defect immediately in Wave 2 (**NOVA-1**) with per-turn token costs, latency, and model fingerprints.
   - Formalizing the **"Absent-vs-Forged"** guardrail model for non-coding and compute-only packs.
   - Designing capability-mediated `agent.spawn` in S0–S12 (design now, implement in M-6).
   - Final absorption of `layer0/registry` and `layer0/compose` into `vanguard/packages/runtime/` with the NOVA-4 negative test suite, and deleting `layer0/`.
   - Publishing the **Universal Turn Loop as Mechanism** claim with a bound falsifier.
   - Proving concurrency via **NOVA-2 (Cold Suspend/Resume from SQLite WAL)**.
   - Scheduling documentation collapse to the Clean Triad post-M-4.

3. **Drafted Append-Only ADR Catalog (`ADR-0077` through `ADR-0082`):**
   - Provide the complete text, context, decisions, schema definitions, and 1-to-1 bound falsifiers for each new proposed ADR.

4. **Phased Milestone Roadmap & Version Ladder (v0.6.1 → v1.0.0):**
   - Define exact goals, entry/exit gates, scope boundaries, and deliverables for each milestone (M-0 through M-10).
   - Enforce the **M-4 Foundation Stop Line** (9 rows on 1 uncheated real run).
   - Specify Pack #2 as **Math & Formal Deductive Verification** for the M-5 generality gate.

5. **Theories, Algorithms & Mathematical Equations:**
   - Active Inference formulation: Variational Free Energy ($\mathcal{F}(\theta)$) minimization over the 6D economic tensor $\mathbf{R}$.
   - Trajectory error credit assignment and backward fault isolation algorithm.
   - Dense 384d hybrid semantic-lexical retrieval and Elo-decayed skill card eviction dynamics.
   - Unforgeable DPO preference harvesting and Paired McNemar exact statistical promotion protocol.

6. **Zero-Guesswork Developer Implementation Bridge:**
   - Normative Draft 2020-12 JSON Schemas (`mhf.manifest/2`).
   - Complete Plugin Lifecycle Finite State Machine (FSM) table with ledger events.
   - 1-to-1 executable falsifier matrix mapping requirements to concrete test functions.
   - Negative constraints and anti-patterns checklist (TCB budget, domain blindness, single-writer).

7. **Repository Hygiene & Document Update Cascade:**
   - Instructions to clean stale artifacts (`DELETE.md`, duplicate research docs).
   - Specific section-by-section diff directives for `SPEC.md`, `sprint_active.md`, `milestones.md`, and wave plans.

