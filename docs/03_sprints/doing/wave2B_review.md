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