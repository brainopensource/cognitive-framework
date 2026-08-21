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

   Act as the collective leadership body — the Leadership 7:

  1. Engineering Director
  2. Chief Technology Officer (CTO)
  3. Chief Information Officer (CIO)
  4. Principal Staff Engineer
  5. Principal Systems Architect
  6. Tech Lead
  7. PhD AI Specialist (Cognitive Systems & Reinforcement Learning)
  ──────
  ### ⚠️ MANDATORY PRE-REQUISITE: Research & Forensic Code Verification

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
  ### Context & Primary Briefing:

  Read the master briefing in docs/00_overview/SYSTEM_OVERVIEW.md. It provides the complete codebase
  map, verified test evidence, the Clean Triad, the 3 Planes of Responsibility (Decision, State,
  Evidence), and catalogues all active ADRs, reviews, and research assets.
  ──────
  ### Your Task:

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

