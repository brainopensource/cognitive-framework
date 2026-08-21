now before proceeding, lets review our docs structure and organization approach and metodology. I have a proposal but feel free to use any metodology or theory you want to review our docs structure

We want to overhaul and elevate our repository's documentation architecture to match state-of-the-art (SOTA), world-class engineering standards
  (drawing from proven methodologies like the Diátaxis framework, RFC/IETF normative specifications, Michael Nygard ADRs, C4 architectural modeling, and
  Contract-First / Executable Specification design).

    Could you please analyze our current documentation and design a clean, layered, anti-sprawl documentation structure and governance methodology?

    Specifically, please provide:

    ---

    ### 1. The Core SOTA Thesis
    * In a single, crisp phrase, what should our documentation architecture embody to be truly SOTA?

    ---

    ### 2. Multi-Tiered Information Architecture & Progressive Disclosure
    How should we partition our documentation into clear layers of depth so that contributors (both engineers and AI coding assistants) only consume the
  exact level of context they need without cognitive overload? Please address:

    * **Layer 0 (Navigation & Orientation):** System map, 10,000-ft mental model, quick-start, and contributor operational contracts.
    * **Layer 1 (The Law & Normative Contracts):** Pure RFC-2119 (`MUST`/`SHALL`) specifications, data contracts, wire schemas, formal state machines, and
  algorithmic pseudocode—strictly decoupled from task progress or timelines.
    * **Layer 2 (Architecture & Systems Topology):** Component diagrams, hexagonal boundary flows (`domain → ports → kernel → agency → runtime →
  adapters`), and interaction sequences.
    * **Layer 3 (The Decisions — ADRs):** Append-only Architecture Decision Records (Context, Decision, Trade-offs, Reversal Criteria, and 1-to-1 bound
  test falsifiers).
    * **Layer 4 (Execution & Active Delivery):** Living single-board sprint management, task ownership, definition of done, and objective milestone gates.
    * **Layer 5 (Development & Engineering Standards):** Coding conventions, TCB budgets, security invariants, linter enforcement, and PR review
  checklists.
    * **Layer 6 (Retained Research & Provenance):** Retained research, external benchmarks, and non-authoritative proposal archives (with clear non-
  normative banners).

    ---

    ### 3. Proposed Folder Tree & File Responsibility Matrix
    * Provide a clean, proposed folder tree for `docs/` and root configuration files.
    * Provide an explanatory matrix for each folder/file defining:
      1. Its primary purpose and authority tier.
      2. Its target audience / when it should be read.
      3. Its update lifecycle (e.g., immutable, append-only, living single-source, or archived).

    ---

    ### 4. Anti-Drift, Anti-Coupling & AI-Resilience Guardrails
    When developers and AI agents jump straight into coding from high-level summaries or ambiguous task tickets, it often leads to architectural drift,
  coupled abstractions, ignored invariants, and hallucinated interfaces.
    * How will your proposed documentation model enforce strict "design-by-contract" and "falsifier-first" workflows (e.g., requiring red test contracts
  before production code)?
    * How can automated tooling (CI linters, boundary checkers, schema validators, broken-link checkers) continuously verify that code conforms to
  documentation law?

    ---

    ### 5. Lean Governance & Anti-Sprawl Protocol
    * What rules and invariants must we establish to ensure documentation never sprawls into duplicate backlogs, stale scratchpads, or competing
  specifications?
    * What is the exact lifecycle protocol for deprecating and archiving superseded proposals and completed sprint notes?

    ---

    Please present your response with a clear folder tree diagram, comparison tables, and concrete examples of how each tier interacts.