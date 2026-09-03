AETHER / Vanguard is a Python-first, recursive-agency substrate designed for mathematically rigorous, verifiable autonomous software engineering. Built around a strictly bounded Trusted
  Computing Base (≤1438 logical LOC) enforcing a 13-stage monotonic capability dispatch pipeline (S0–S12) and an append-only RFC 8785 JCS SQLite-WAL event ledger, Vanguard ensures that   
  autonomous agents cannot escape capability bounds, hallucinate unearned verification passes, or corrupt execution history. An existing example already running on this substrate is      
  Coding Max (apps/coding_max), invoked via the CLI command vg code (or vg code --preset balanced). Coding Max uses the default code pack (packs/code-default) on top of the EpisodeEngine 
  turn loop to autonomously ingest task briefs or failing test cases, localize fault paths through repository-intelligence graphs, apply atomic multi-file edits inside a rootless         
  Bubblewrap sandbox (bwrap), verify that new tests pass while regressions remain zero, and emit a cryptographically signed execution verdict alongside a unified diff patch.              
  ──────                                                                                                                                                                                   
  ## 1. Hexagonal Production Lattice (vanguard/packages/)                                                                                                                                  
                                                                                                                                                                                           
  The core framework strictly enforces unidirectional dependency flow:                                                                                                                     
                                                                                                                                                                                           
    domain ← ports ← kernel ← agency ← runtime → adapters                                                                                                                                  
             (apps/ is a client slot of runtime)                                                                                                                                           
                                                                                                                                                                                           
   Layer / Directory │ File Path │ Responsibilities & Architectural Constraints
  ───────────────────┼───────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
   Domain            │ domain    │ Pure data models, wire contracts, RFC 8785 JCS canonicalization, ledger reducers, resource selectors, and semantic task vectors (task_state.py). Stdlib
                     │           │ Python only; zero dependencies, zero I/O, zero network.
   Ports             │ ports     │ Abstract Python typing.Protocol declarations defining all hexagonal interfaces (kernel.py, model.py, sandbox.py, evaluator.py, event_store.py,
                     │           │ blob_store.py, index.py, and 5 SPI protocols in spi.py).
   Kernel (TCB)      │ kernel    │ The Trusted Computing Base (≤1438 LOC budget enforced by CI). Implements the 13-stage dispatch pipeline (S0–S12), monotonic budget attenuation,
                     │           │ capability grants, and execution provenance DAG. Strictly domain-blind; must never import domain, agency, runtime, or adapters.
   Agency            │ agency    │ Recursive turn engine. Houses EpisodeEngine, attenuated child agent spawning (spawn()), context compilers, admission gate enforcement, and manifest
                     │           │ loaders.
   Runtime           │ runtime   │ System lifecycle and wiring (compose.py, session.py, wiring.py, ledger_emitter.py), Ed25519 cryptographic approvals (governance/), and SQLite WAL event
                     │           │ storage.
   Adapters          │ adapters  │ Concrete I/O implementations: Model clients (OpenRouter, Ollama, Cassette, Fake), Bubblewrap sandbox worker, evaluator daemon/RPC, and SQLite stores.
                     │           │ Must NEVER import kernel or agency.
   Apps              │ apps      │ Thin application entry points (e.g., apps/coding_max). Coordinates CLI/API requests into ApplicationService compositions.
   Front             │ front     │ TypeScript/React/Ink client workspaces: CLI (vg), Desktop UI, TUI, Studio, and shared client contracts.
  ──────                                                                                                                                                                                   
  ## 2. Documentation Architecture & The 4 Execution Files                                                                                                                                 
                                                                                                                                                                                           
  Per AGENTS.md, repository documentation is strictly partitioned into distinct authority tiers:                                                                                           
                                                                                                                                                                                           
    VISION.md / AGENTS.md / docs/SPEC.md      # Constitutional Law & Operational Rules                                                                                                     
    docs/decisions.md                         # Foundational Architecture Decision Records (ADRs)                                                                                          
    docs/architecture/ & docs/backend/        # Invariant System Topography & Component Specs                                                                                              
    docs/theory/                              # Mathematical Reference Papers (LDA, SOTA Treatise)                                                                                         
    docs/execution/                           # The 4-File Operational Runway (milestones, backlog, FEATURE_SPEC, tasks)                                                                   
                                                                                                                                                                                           
  ### The Four Authoritative Runway Files in execution                                                                                                                                     
                                                                                                                                                                                           
  To eliminate split-brain authority and keep developers focused, the execution runway contains exactly four files:                                                                        
                                                                                                                                                                                           
  1. milestones.md [STABLE GATES]:                                                                                                                                                         
      • Contains formal, release-level acceptance predicates for M-0 through M-10 and Backend Finish Gates (W-092-F0 to W-092-F6).                                                         
      • Publishes the future M-OCT (Octopus Outer-Loop Meta-Orchestrator) horizon (W-OCT-1 to W-OCT-4: Mailbox protocol, CoordinationPlan DAG, Roadmap director, Swarm goal algebra) at a  
      conceptual gate level without premature pseudocode.                                                                                                                                  
  2. backlog.md [STABLE INVENTORY]:                                                                                                                                                        
      • Categorized inventory of all capability packages (SUB-* Kernel, MEM-* Memory, DEL-* Delegation, TLS-* Tooling, CMX-* Coding Max, and OCT-* Octopus Swarms).                        
      • Tracks package lifecycle state: PROPOSED, APPROVED, IN_PROGRESS, REVIEWING, DONE, BLOCKED, DEFERRED.                                                                               
  3. FEATURE_SPEC.md [ACTIVE DELTA SPEC] (The PRD / In-Flight Contract):                                                                                                                   
      • The authoritative typed delta contract for the active sprint ticket (W-092-F1 / CMX-09).                                                                                           
      • Defines the exact Pydantic/dataclass schemas (SemanticTaskState), Two-Phase Commit (2PC) FEATURE_SPEC.md:78-115, cryptographic FEATURE_SPEC.md:125-160, 4-tier                     
      FEATURE_SPEC.md:162-180, model dialect recovery matrices, CLI flags, and error codes.                                                                                                
  4. tasks.md [ACTIVE WORK DAG] (with active.md -> tasks.md backward-compatibility symlink):                                                                                               
      • The dynamic execution work graph for the active sprint.                                                                                                                            
      • Quarantines historical forensic autopsies, commit digests, and diagnostic clutter. Contains only active WIP lanes (Lane A / Lane B), current active sub-goals (T0–T7), blocker     
      matrices, and exact test falsifiers.                                                                                                                                                 
                                                                                                                                                                                           
  ──────                                                                                                                                                                                   
  ## 3. Repository-Intelligence Navigation Protocol (Using LDA)                                                                                                                            
                                                                                                                                                                                           
  Per SKILL.md, developers and AI agents must navigate the repository using token-bounded repository intelligence tools instead of dumping thousands of raw source lines into context.     
                                                                                                                                                                                           
  ### The Mandatory Starting Sequence                                                                                                                                                      
                                                                                                                                                                                           
    # Step 0 — Assert Index Health: Must return status: HEALTHY and index_healthy: true                                                                                                    
    uv run lda doctor --json                                                                                                                                                               
                                                                                                                                                                                           
    # Step 1 — Route the Task: Get token-bounded context packet for keywords or errors                                                                                                     
    uv run lda context "<task keywords or error signature>" --budget 4000                                                                                                                  
                                                                                                                                                                                           
    # Step 2 — Targeted Symbol Inspection: Read exact class/method signatures and docstrings                                                                                               
    uv run lda symbol <SymbolName> --exact                                                                                                                                                 
                                                                                                                                                                                           
    # Step 3 — Blast Radius & Impact Graph: Discover all callers before editing                                                                                                            
    uv run lda callers <SymbolName.method>                                                                                                                                                 
    uv run lda callees <SymbolName.method>                                                                                                                                                 
                                                                                                                                                                                           
    # Step 4 — Focused Test Selection: Find the exact unit tests covering a touched file                                                                                                   
    uv run lda tests <relative/path/to/modified_file.py>                                                                                                                                   
                                                                                                                                                                                           
    # Step 5 — Dense Structural Map (if exploring a new subsystem)                                                                                                                         
    uv run lda repomap --budget 2000 --focus <subsystem_path>                                                                                                                              
  ──────                                                                                                                                                                                   
  ## 4. End-to-End Developer Workflow: How to Implement Any Feature                                                                                                                        
                                                                                                                                                                                           
  Follow this standard procedure to develop, verify, and document any work in Vanguard:                                                                                                    
                                                                                                                                                                                           
    sequenceDiagram                                                                                                                                                                        
        autonumber                                                                                                                                                                         
        actor Dev as Developer / AI Agent                                                                                                                                                  
        participant Board as tasks.md & FEATURE_SPEC.md                                                                                                                                    
        participant LDA as LDA Repository Intelligence                                                                                                                                     
        participant Code as vanguard/packages/                                                                                                                                             
        participant Linters as Boundaries & TCB Linters                                                                                                                                    
        participant Tests as Test Falsifiers                                                                                                                                               
        participant Docs as Knowledge Base (.jsonl & index.db)                                                                                                                             
                                                                                                                                                                                           
        Dev->>Board: Read active sub-goal in tasks.md & schema in FEATURE_SPEC.md                                                                                                          
        Dev->>LDA: Inspect interfaces (lda symbol) & blast radius (lda callers)                                                                                                            
        Dev->>Tests: Write failing test falsifier first (TDD / Greenfield oracle)                                                                                                          
        Dev->>Code: Implement logic strictly following hexagonal boundaries                                                                                                                
        Dev->>Linters: Run check_boundaries.py & check_tcb_budget.py                                                                                                                       
        Dev->>Tests: Run focused test (lda tests <file>) + full module suite                                                                                                               
        Dev->>Board: Check off step in tasks.md ([x] Tn)                                                                                                                                   
        Dev->>Docs: Refresh knowledge (generate_knowledge_base.py & uv run lda index)                                                                                                      
                                                                                                                                                                                           
  ### Step-by-Step Execution Guide:                                                                                                                                                        
                                                                                                                                                                                           
  ### 1. Identify Your Active Goal & Invariant Constraints                                                                                                                                 
                                                                                                                                                                                           
  • Open tasks.md to locate the current in-progress task (e.g., T2: SemanticTaskState Vector).                                                                                             
  • Open FEATURE_SPEC.md to review the exact schemas, method signatures, and invariant rules governing that task.                                                                          
                                                                                                                                                                                           
  ### 2. Locate Relevant Code via LDA                                                                                                                                                      
                                                                                                                                                                                           
  • Do not browse arbitrary folders. Pin existing protocols and dependent types:                                                                                                           
    uv run lda symbol TaskContext --exact                                                                                                                                                  
    uv run lda callers TaskContext                                                                                                                                                         
                                                                                                                                                                                           
                                                                                                                                                                                           
  ### 3. Falsification-First (Write Failing Tests First)                                                                                                                                   
                                                                                                                                                                                           
  • Create or update the test falsifier in test/contracts/, test/kernel/, test/agency/, or test/runtime/.                                                                                  
  • Ensure the test fails on the pre-image before modifying production code.                                                                                                               
  • If implementing a greenfield task, follow the Synthetic Test Oracle Protocol defined in FEATURE_SPEC.md:117-123.                                                                       
                                                                                                                                                                                           
  ### 4. Implement Code within Hexagonal Boundaries                                                                                                                                        
                                                                                                                                                                                           
  • Write single-responsibility, type-annotated code.                                                                                                                                      
  • Keep dependencies strictly downward:                                                                                                                                                   
      • Stdlib only in domain/.                                                                                                                                                            
      • Protocols in ports/.                                                                                                                                                               
      • Kernel core ≤1438 LOC in kernel/.                                                                                                                                                  
      • Concrete drivers in adapters/ (never imported by agency or kernel).                                                                                                                
                                                                                                                                                                                           
                                                                                                                                                                                           
  ### 5. Run Verification & Boundary Linters                                                                                                                                               
                                                                                                                                                                                           
  Before committing or claiming completion, execute the repository validation gates:                                                                                                       
                                                                                                                                                                                           
    # 1. Check architectural boundary flows and TCB budget limit                                                                                                                           
    python3 tools/linters/check_boundaries.py                                                                                                                                              
    python3 tools/linters/check_tcb_budget.py
  
    # 2. Check domain blindness (I-7) and container isolation (I-6)
    python3 tools/linters/check_domain_blindness.py
    python3 tools/linters/check_isolation_policy.py
  
    # 3. Check markdown link integrity across all documentation
    python3 tools/linters/check_markdown_links.py
    python3 tools/linters/check_stale_paths.py
    python3 tools/linters/check_falsifier_ids.py
  
    # 4. Run Python unit and contract test suites using the virtual environment
    .venv/bin/python -m unittest discover -s test/kernel -t .
    .venv/bin/python -m unittest discover -s test/contracts -t .
    .venv/bin/python -m unittest discover -s test/agency -t .
    .venv/bin/python -m unittest discover -s test/packs -t .
    .venv/bin/python -m unittest discover -s test/runtime -t .
  
    # 5. Run TypeScript suite (if touching client code)
    npm test
  
  ### 6. Update the Active DAG & Rebuild Indexes
  
  • **Mark the step as complete in tasks.md**:
  Change - [ ] T2: Domain Semantic Task State Vector to - [x] T2: Domain Semantic Task State Vector.
  • Rebuild the Knowledge Layer & LDA Index:
    python3 tools/generate_knowledge_base.py
    uv run lda index
  
  • Atomic Promotion: When all tasks for the active ticket are verified and pass the milestone gate in milestones.md, promote the delta contracts from FEATURE_SPEC.md into canonical      
  docs/architecture/ and cycle the spec for the next backlog package.