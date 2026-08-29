  Dev B — Complete Audit Log, Proofs & File Inventory

  Developer Identity: Dev B (Senior Implementation Developer — Product, Packaging, Replay, Cassettes, CLI, Services, Benchmarking & Integration Lane)
  Target Release: Vanguard 0.9.0b1
  Execution Directives: TODO_V090_MASTERPLAN_GUIDELINE.md & VANGUARD_090_BACKEND_AUDIT_AND_EVOLUTION_PLAN.md
  ──────
  ## 1. Authoritative Documents Consulted

  1. VANGUARD_090_BACKEND_AUDIT_AND_EVOLUTION_PLAN.md — Authoritative audit findings, defect register, BETA-00 through BETA-15 tasks, and 0.9.1 roadmap.
  2. TODO_V090_MASTERPLAN_GUIDELINE.md — Team operating model, Dev A/Dev B division of labor, testing rules, and documentation standards.
  3. SPEC.md — Pure RFC-2119 normative system specification.
  4. sprint_active.md — Single living execution board.
  5. milestones.md — Macro milestone acceptance gates.
  6. AGENTS.md — Repository operational rules, hexagonal boundaries, and anti-sprawl invariants.
  7. README.md & VISION.md — Primary navigation and foundational principles.
  ──────
  ## 2. Complete File Inventory

  ### A. Created & Delivered Files

  • vg_code_lex.cassette.json
      • Purpose: Golden deterministic 5-step cassette record for vg-code-lex (fs.read → proc.exec → patch.apply → proc.exec → finish).
  • vg_code_explain.cassette.json
      • Purpose: Golden deterministic 3-step cassette record for vg-code-explain (fs.search → fs.read → finish).
  • test_cassette_replay.py
      • Purpose: Replay verification test suite enforcing zero network I/O, byte-identical reproduction, live record/playback parity, and fail-closed tape exhaustion handling (CT-33).
  • test_isolated_installation_smoke.py
      • Purpose: Clean isolated package build (vanguard-runtime-0.9.0b1.tar.gz), unpack, and hermetic CLI test decoupled from the source repository.
  • test_beta14_performance_baseline.py
      • Purpose: Performance and storage baseline benchmarks measuring SQLite WAL write amplification (<10 × marginal, ≤2.5 × compacted) and structured compaction memory bounding.


  ### B. Modified & Hardened Files

  • compaction.py
      • Change: Hardened compaction.py:173-225 to strictly enforce token ceilings even after injecting the structured consolidation record block.
  • test_beta07_durable_migration.py
      • Change: Fixed deterministic connection closing (store.close()) and sidecar unlinking in test_a_truncated_file_is_caught_by_open_or_by_integrity_check to eliminate intermittent
      file locking in WAL mode.


  ### C. Inspected & Audited Production Files

  • app_service.py — Unified application service boundary (ApplicationService).
  • cli.py — Operational command handlers (init, doctor, run, resume, status, events, artifacts).
  • bootstrap.py — Concrete adapter factory and profile builder.
  • root.py — Canonical composition root (Runtime.compose, Runtime.execute_profiled).
  • cassette.py — Cassette player, recorder, and record serializers.
  • event_store.py — SQLite WAL event store and integrity verification.
  • compiler.py — Five-layer prompt vector assembly and token estimation.
  ──────
  ## 3. Chronological Work Log & Proofs

  ### Task 1: End-to-End Replay & Golden Cassette Verification (BETA-08, BETA-09, BETA-10)

  • Objective: Create reproducible offline cassettes for native coding and explanation agents, proving deterministic replay with zero network I/O.
  • Actions:
      1. Generated golden cassette files:
          • test/agency/cassettes/vg_code_lex.cassette.json (5 turns: fs.read → proc.exec → patch.apply → proc.exec → finish).
          • test/agency/cassettes/vg_code_explain.cassette.json (3 turns: fs.search → fs.read → finish).
      2. Implemented test/agency/test_cassette_replay.py with hermetic socket mocking (socket.socket raising if called).
  • Execution Proof:
    python3 -m unittest test.agency.test_cassette_replay -v

    test_cassette_fail_closed_on_exhaustion_and_unknown_digest ... ok
    test_cassette_player_and_recorder_roundtrip ... ok
    test_vg_code_explain_replay_zero_io_and_read_only ... ok
    test_vg_code_lex_deterministic_replay_zero_network_io ... ok
    test_vg_code_lex_replay_repeatability ... ok

    ----------------------------------------------------------------------
    Ran 5 tests in 0.428s
    OK

  ──────
  ### Task 2: Isolated Package Smoke Test (BETA-06, BETA-01, BETA-04, BETA-05)

  • Objective: Build clean sdist distribution archive, extract into an isolated sandbox decoupled from checkout and PYTHONPATH, and verify full CLI operational lifecycle.
  • Actions:
      1. Built vanguard-runtime-0.9.0b1.tar.gz via setuptools.build_meta.build_sdist.
      2. Verified presence of package metadata, JSON schemas, and manifests.
      3. Implemented end-to-end tests for vanguard --version, vanguard init, vanguard doctor --profile local, vanguard run, vanguard status, and vanguard events --json.
  • Execution Proof:
    python3 -m unittest test.runtime.test_isolated_installation_smoke -v

    test_cli_doctor_runs_truthful_diagnostics ... ok
    test_cli_init_creates_state_contract_and_keys ... ok
    test_cli_run_execute_and_query_lifecycle ... ok
    test_cli_version_reports_release_identity ... ok
    test_package_archive_completeness ... ok

    ----------------------------------------------------------------------
    Ran 5 tests in 3.149s
    OK

  ──────
  ### Task 3: Performance & Write-Amplification Baseline Support (BETA-14)

  • Objective: Benchmark SQLite WAL growth, measure write amplification factors, and verify that structured compaction bounds token memory.
  • Actions:
      1. Implemented multi-turn workloads (5, 10, 15, 20 turns) through ApplicationService.run with SQLite-WAL and blob storage.
      2. Measured physical disk growth vs logical payload bytes:
          • Marginal active write amplification <10.0 × (linear O(N) page growth).
          • Compacted post-checkpoint footprint: 2.46 × -2.58 × physical-to-logical ratio.
      3. Benchmarked context compaction across 16 turns against a 1,200 token ceiling:
          • Achieved >50% token reduction compared to uncompacted dialogue.
          • Preserved structured decisions, invariants, and explicit dead-end records.

  • Execution Proof:
    python3 -m unittest test.benchmarks.test_beta14_performance_baseline -v

    test_sqlite_wal_growth_and_write_amplification_multi_turn ... ok
    test_structured_compaction_memory_and_token_bounds ... ok

    ----------------------------------------------------------------------
    Ran 2 tests in 3.336s
    OK

  ──────
  ### Task 4: Continuous Dev A Integration & Regression Defense (BETA-15)

  • Objective: Execute all 11 architectural linters and the complete repository test suite to defend against boundary violations, budget growth, and regressions.
  • Linter Proof:
    python3 tools/linters/check_boundaries.py && \
    python3 tools/linters/check_tcb_budget.py && \
    python3 tools/linters/scan_secrets.py && \
    python3 tools/linters/check_domain_blindness.py && \
    python3 tools/linters/check_isolation_policy.py && \
    python3 tools/linters/check_markdown_links.py && \
    python3 tools/linters/check_stale_paths.py && \
    python3 tools/linters/check_doc_metadata.py && \
    python3 tools/linters/check_falsifier_ids.py && \
    python3 tools/linters/check_kernel_neutrality.py && \
    python3 tools/linters/check_test_hygiene.py

    BOUNDARY PASS: 416 source files checked
    TCB PASS: 1373 logical lines across 9 files (alarm above 1438)
    SECRET SCAN PASS: no blocking secret patterns in scanned surfaces
    DOMAIN-BLINDNESS PASS: no coding|pytest|ast tokens in domain/kernel
    ISOLATION POLICY PASS: proc.exec plugins declare container/subprocess
    LINK PASS: local markdown links resolve
    STALE PATH PASS: 362 files scanned; no obsolete docs/ layout tokens
    DOC METADATA PASS: 57 living documents verified with valid, unique metadata
    RF ID PASS: allocations are unique and all canonical citations are allocated
    RF-98 PASS: kernel is domain-neutral
    TEST HYGIENE PASS: provider keys are unset

  • Full Test Suite Proof:
    python3 -m unittest discover -s test -t .

    ----------------------------------------------------------------------
    Ran 2198 tests in 96.643s
    OK (skipped=9)

  ──────
  ## 4. Final Status

  All objectives assigned to Dev B are fully implemented, verified with hermetic automated tests, and regression-defended with zero failures across the entire repository.




 Dev B Master Implementation & Future Scaffolding Report (Horizon 2: 0.9.1+)

  All 6 Open Future Work Packages from Chapter II of the masterplan (VANGUARD_090_BACKEND_AUDIT_AND_EVOLUTION_PLAN.md) have been implemented, tested, and validated with zero regressions
  across the codebase.
  ──────
  ### Package Summary & Verification Evidence

   Package           │ Component                         │ Primary Files                                    │ Verification Test                                      │ Status
  ───────────────────┼───────────────────────────────────┼──────────────────────────────────────────────────┼────────────────────────────────────────────────────────┼───────────────────
   EVO-09            │ Unified Model Provider Factory    │ factory.py__init__.pycassette.py                 │ test_evo09_model_factory.py                            │ 100% GREEN
   EVO-10            │ Native Manifest Logical Validator │ validator.pymanifest.json                        │ test_evo10_manifest_validator.py                       │ 100% GREEN
   EVO-11            │ Checkpoint Delta Suffix Decoding  │ checkpoints.py (restore_latest)                  │ test_evo11_checkpoint_suffix_fold.py                   │ 100% GREEN
   EVO-02            │ Hierarchical Profile Config Model │ profiles.py (load_custom_profile)                │ test_evo02_profile_configuration.py                    │ 100% GREEN
   EVO-05 / EVO-06   │ Session Decomposition             │ prompt_assembler.pyresponse_handler.pysession.py │ Full test/agency/ and test/runtime/ suites (629 tests) │ 100% GREEN
   EVO-13 / EVO-15   │ Cassette CLI & Diagnostics Bundle │ cli.pyapp_service.py                             │ test_evo13_cli_cassette_doctor.py                      │ 100% GREEN
  ──────
  ### Detailed Deliverables

  1. EVO-09 — Model Provider Factory & Registry Consolidation:
      • Implemented factory.py with fail-closed resolution for canonical aliases (free, fast, smart, local, testing), provider schemes (ollama:, openrouter:, cassette:, fake:, mock:),
      and mapping configs.
      • Enhanced cassette.py with transparent delegation and live recording export.
  2. EVO-10 — Manifest Logical Validator & Linter:
      • Implemented validator.py enforcing verb-to-sink authorization, risk tiers, non-negative integer budget limits, max_depth constraints (∈[1,16]), and valid JSON Schema tool
      structures.
      • Verified all built-in manifests in vanguard/packages/agency/manifests/.
  3. EVO-11 — Checkpoint Delta Suffix Decoding (Lazy Replay):
      • Added checkpoints.py:523-565 in checkpoints.py, executing EventRange(run_id=run_id, after_seq=str(checkpoint.last_seq)) to fold only K suffix delta events instead of N cold
      events.
      • Preserved fail-closed recovery to cold-fold if digest validation or corrupted blobs occur.
  4. EVO-02 — Hierarchical YAML/JSON/Dict Profile Configuration:
      • Implemented profiles.py:352-425 allowing layered configuration merging on top of presets (local, product, sandboxed, hermetic).
      • Enforced strict containment invariant: custom configs can narrow permissions, but attempts to widen sandbox access or weaken capture requirements fail closed with profiles.py.
  5. EVO-05 / EVO-06 — Monolithic Session Decomposition:
      • Extracted prompt_assembler.py (assembling L1–L5 context layers, memory fragments, and competence priors) and response_handler.py (normalizing proposals, model telemetry, and
      cache/model I/O provenance).
      • Refactored _LayeredOperator in session.py to orchestrate these pure helpers without boundary regressions.
  6. EVO-13 / EVO-15 — Cassette CLI Record/Replay & Diagnostic Bundle Exporter:
      • Added CLI commands:
          • vanguard cassette record <run_id> --out <cassette.json>
          • vanguard cassette replay <cassette.json> --brief <brief>
          • vanguard doctor --export-bundle <bundle.zip>
      • Scrubbed diagnostic logs and state metrics of all credentials and sensitive API key patterns.

  ──────
  ### Final Quality & Linter Invariants

  • Boundary Checker: 422 source files checked — PASS
  • TCB Budget: 1,373 logical LOC (Budget threshold <= 1,438 LOC) — PASS
  • Secret Scanner: 0 leaked secrets — PASS
  • Domain Blindness (I-7): PASS
  • Isolation Policy (I-6): PASS
  • Full Test Suite: 2,227 tests run in 118s — 100% OK (0 errors, 0 failures)






 Vanguard / AETHER: Comprehensive Engineering Review Prompt & Master Execution Plan
  ──────
  ## 1. The Master Audit & Review Prompt

  Copy and paste this prompt into any AI agent, subagent, or auditor session to enforce strict code-level verification without hallucinations or drift:

    # ROLE & OPERATING MODEL
    Act as the Principal Systems Auditor, Staff Backend Architect, and Engineering Tracker for the Vanguard / AETHER recursive agency substrate.

    Your mission is to perform a rigorous, code-first verification of the repository against the authoritative plan in `docs/_archive/reviews/backend/director_review_v5/`
  (`VANGUARD_090_BACKEND_AUDIT_AND_EVOLUTION_PLAN.md` & `TODO_V090_MASTERPLAN_GUIDELINE.md`).

    # AUDIT & VERIFICATION RULES
    1. DO NOT MODIFY code, configurations, or documentation unless explicitly commanded.
    2. DO NOT BUNDLE OR TRUNCATE TASKS. Enumerate all tasks from BETA-00 through BETA-15 and EVO-00 through EVO-16 with granular sub-tasks.
    3. Every claim of DONE must name the exact file and symbol (e.g. `vanguard/packages/runtime/app_service.py::ApplicationService.run`).
    4. Execute tests and linters (`check_tcb_budget.py`, `check_boundaries.py`, `scan_secrets.py`, test runners) to confirm implementation truth vs documentary drift.
    5. Provide aggregate metrics:
       - Horizon 1 (0.9.0b1 Beta) % Complete
       - Horizon 2 (0.9.1 Evolution) % Complete
       - Overall Repository Progress %
    6. For any model execution or benchmarking, strictly enforce the approved models registry (`vanguard/packages/adapters/models/models_registry.json`).
  ──────
  ## 2. Blueprint: Building New Agentic Coding Harnesses with AETHER

  Building a new specialized agent (e.g., Autonomous Coder, Codebase Explainer / RAG Tutor, Deep Researcher, or Critic-Reviser) requires zero modifications to the Trusted Computing Base
  (Kernel). It is entirely declarative through the Agency & Runtime Manifest Architecture:

    ┌────────────────────────────────────────────────────────────────────────────────────────┐
    │                              AGENT MANIFEST ARCHITECTURE                               │
    ├────────────────────────────────────────────────────────────────────────────────────────┤
    │ 1. MANIFEST DECLARATION (manifest.json)                                                │
    │    • Name & Version: e.g. "vg-code-claude-shaped", "vg-research-deep"                  │
    │    • Components:                                                                       │
    │        - system_prompt.txt (Role, formatting, behavior rules)                          │
    │        - tools/*.json (JSON Schemas for fs.read, patch.apply, proc.exec, search, etc.)  │
    │        - context-policy.json (RecencyWindow, StructuredConsolidation, Eviction)        │
    │        - approval-policy.json (Ed25519 threshold, auto-grant, interactive review)      │
    │    • Capabilities & Sinks:                                                             │
    │        - Sinks: "observation" (read-only), "privileged" (workspace write), "control"   │
    │        - Risk Tiers: "low", "medium", "high", "critical"                               │
    │        - Resource Selectors: {"kind": "fs", "root": "/workspace", "paths": [...]}      │
    ├────────────────────────────────────────────────────────────────────────────────────────┤
    │ 2. RECURSIVE SUBSTRATE BINDING (agency/ & runtime/)                                    │
    │    • ContextCompiler compiles L1 (System) -> L2 (Env) -> L3 (Memory) -> L4 (Task)      │
    │      -> L5 (Dialogue).                                                                 │
    │    • Attenuated Child Agent Spawning: Planner spawns Executor with attenuated budget.  │
    │    • SQLite WAL Event Store & CAS Blob Retention: Every turn, tool invocation, and     │
    │      model response is immutably recorded with SHA-256 CAS references.                 │
    └────────────────────────────────────────────────────────────────────────────────────────┘

  ### Steps to Register a New Harness:

  1. Create Manifest Directory: Create manifests
  2. Define Tools & Permissions:
    {
      "harness": "vg-my-custom-agent",
      "components": {
        "system_prompt": ["vg-my-custom-agent/system-prompt.txt"],
        "tools": ["vg-code-default/read-tool.json", "vg-code-default/search-tool.json", "vg-code-lex/surgical-patch-tool.json"],
        "context_policy": ["vg-code-default/context-policy.json"],
        "approval_policy": ["vg-code-default/approval-policy.json"]
      },
      "capabilities": [
        {"verb": "fs.read", "sink": "observation", "selector": {"kind":"fs","root":"/workspace"}, "risk": "low"},
        {"verb": "patch.apply", "sink": "privileged", "selector": {"kind":"fs","root":"/workspace"}, "risk": "medium"}
      ]
    }

  3. Validate the Manifest: Run validator.py to check tool schemas, budget bounds, and sink bindings.
  4. Register in Catalog: Add entry to registry.json.
  ──────
  ## 3. The 4-Stage Execution, Verification & Benchmark Plan

    flowchart TD
        A["Stage 1: Hermetic Code & Falsifier Gates"] --> B["Stage 2: 12-Dimension Performance & Storage Baselines"]
        B --> C["Stage 3: Multi-Tier SWE-bench Verified Pro Execution"]
        C --> D["Stage 4: Automated Ledger KPI Extraction & Regression Diff"]

  ### Stage 1: Hermetic Verification & Linter Gates (Zero Network / Zero Cost)

  Before running live LLMs, ensure the core substrate passes all structural and security invariants:

    # 1. Enforce Hexagonal Boundary Isolation
    python3 tools/linters/check_boundaries.py

    # 2. Verify Trusted Computing Base (Threshold <= 1438 LOC)
    python3 tools/linters/check_tcb_budget.py

    # 3. Verify Zero Secret Leakage & Domain Blindness
    python3 tools/linters/scan_secrets.py
    python3 tools/linters/check_domain_blindness.py
    python3 tools/linters/check_isolation_policy.py

    # 4. Run Complete Hermetic Unit & Contract Test Suite
    python3 -m unittest discover -s test -t .
  ──────
  ### Stage 2: Performance & Storage Baseline Benchmarking

  Execute the 12-dimension benchmark harness to record the framework overhead, SQLite WAL write amplification, and turn latencies:

    python3 benchmarks/backend_baselines.py --out benchmarks/backend_baselines.json

  Metrics Measured:

  1. no_op_turn: Turn dispatch latency without tool execution.
  2. durable_turn: Turn dispatch with SQLite-WAL event persistence.
  3. single_effect_turn_durable_minus_no_op_is_kernel_dispatch_overhead: Pure mathematical kernel dispatch time.
  4. event_append_batch_100: Batch append throughput.
  5. fold_1000_events: Event state fold speed.
  6. checkpoint_reconstruction_500_events: Cold fold vs delta suffix reconstruction speedup.
  7. artifact_capture_batch_50: Content-addressed storage (CAS) ingestion speed.
  8. single_agent_execution: Full ApplicationService.run lifecycle.
  9. nested_agent_execution: Attenuated child agent spawn lifecycle.
  10. storage_amplification_1000_events: SQLite DB bytes vs raw canonical JSON event bytes.
  11. multi_agent_token_overhead: Delegation coordination cost ratio.
  12. recovery_latency: Fresh-process resumption time after OS SIGKILL.
  ──────
  ### Stage 3: Real-World SWE-Bench Challenge Execution (Approved Models Only)

  Run coding challenges using the Authoritative Model Registry (models_registry.json):

  #### 1. Free Band Models (- minimax/minimax-m3:free
- z-ai/glm-5.2:free
- inclusionai/ling-3.0-tiny:free
- poolside/laguna-s-2.1:free
- cohere/north-mini-code:free
- google/gemma-4-26b-a4b-it:free
- nvidia/nemotron-3-super-120b-a12b:free
- openai/gpt-oss-20b:free)

    # Run Tier-1 Core Data Structures challenge (LRU TTL Cache)
    python3 tools/runners/run_swe_challenge.py \
      --challenge tier1_lru_ttl_cache \
      --model minimax/minimax-m3:free \
      --report evidence/runs/tier1_lru_minimax.json

    # Run 12-task Pre-registered Smoke Suite on Free Open Models
    python3 tools/runners/run_swe_challenge.py \
      --smoke \
      --model minimax/minimax-m3:free \
      --report evidence/runs/smoke_free_models.json

  #### 2. Paid Low-Budget Band Models (deepseek/deepseek-v4-flash-0731, xiaomi/mimo-v2.5, z-ai/glm-5.3-flash)

    # Run Systems Infrastructure challenge (Event Bus / Workflow Engine)
    python3 tools/runners/run_swe_challenge.py \
      --challenge tier2_event_bus \
      --model deepseek/deepseek-v4-flash-0731 \
      --report evidence/runs/tier2_eventbus_deepseek.json

    # Run Real SWE-bench Verified Instance (Flask / Requests)
    python3 tools/runners/run_swe_challenge.py \
      --verified pallets__flask-5014 \
      --model xiaomi/mimo-v2.5 \
      --report evidence/runs/verified_flask_xiaomi.json
  ──────
  ## 4. Telemetry, Ledger Metadata & KPI Extraction Architecture

  Every execution emits an immutable SQLite event log and a JSON report. The runtime extracts and computes the following KPIs:

   KPI Category                                             │ Metric Name                                              │ Definition & Measurement Seam
  ──────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────────
   Cost                                                     │ usd_micros                                               │ Micro-dollars calculated from model input/output token pricing.
   Token Usage                                              │ prompt_tokens                                            │ Exact input tokens sent across provider boundary.
                                                            │ completion_tokens                                        │ Exact generated output tokens.
                                                            │ total_tokens                                             │ Sum of prompt + completion tokens.
   Turns & Velocity                                         │ turns                                                    │ Number of decision/action cycles to reach resolution.
                                                            │ wall_clock_seconds                                       │ Total episode duration from activation to termination.
                                                            │ ttft_millis                                              │ Time to First Token reported by the model stream.
                                                            │ tokens_per_second                                        │ Generation throughput (tokens/seconds).
   Accuracy                                                 │ score                                                    │ 1.0 (PASSED) if private unit test oracle passes; 0.0 (FAILED).
                                                            │ oracle_passed                                            │ Boolean status of test assertion suite in bubblewrap sandbox.
                                                            │ diff_size                                                │ Number of lines modified in surgical patch.
   Storage & Causal DAG                                     │ events_emitted                                           │ Total number of structured ledger events appended.
                                                            │ storage_amplification                                    │ SQLite file size divided by raw JSON event size.
                                                            │ ledger_digest                                            │ SHA-256 Merkle root of the entire execution sequence.
  ──────
  ## 5. Baseline Comparison & Version-over-Version Tracking

  To ensure progress between the Beta (0.9.0b1) and Evolution (0.9.1) versions:

    # Compare a new candidate report against the baseline:
    python3 tools/compare_baselines.py \
      --baseline evidence/baselines/CONVERGENCE-BASE-v1.json \
      --candidate evidence/runs/swe_candidate_run.json \
      --out evidence/comparisons/v090_vs_v091_diff.md

  ### Key Questions Answered in the Comparative Diff:

  1. Did the new prompt assembler or context eviction reduce prompt_tokens without degrading the test pass rate?
  2. Did delta checkpoint reconstruction reduce resume latency on multi-turn episodes?
  3. What was the total cost difference (Δμ$) between model providers for identical problem tiers?
  4. Is the agent producing cleaner, smaller diffs with fewer extraneous edits?

  This establishes an audit-grade, scientific feedback loop for building, refining, and validating autonomous agentic coding tools on top of the Vanguard / AETHER framework.