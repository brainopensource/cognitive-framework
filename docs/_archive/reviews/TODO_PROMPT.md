# AETHER M‑8 Beta — Final Execution Plan

  Target file: docs/_archive/reviews/TODO_PROMPT.md

  This plan is not yet written to disk because Plan Mode forbids repository mutation.

  ## 1. Current report adjudication

  Dev A and Dev B reports are not independently accepted yet.

  The concurrent-session conflict is a P0 issue: Dev A changed schemas/client-core while Dev B changed service.py, inbox.py, and
  studio_gateway.py. Their work must first be reconciled against one final tree. Do not trust test counts or reports until the resulting combined
  diff is reviewed.

  Confirmed or likely remaining gaps:

  - RuntimeService.execute_command must actually call contract validation.
  - HTTP ExplainArtifact and RecordCorrection routes are still absent.
  - The default gateway must use a persistent SQLite-WAL store.
  - The canonical runtime must execute real Runtime.execute_profiled, not merely accept a runner callback.
  - Service state and events must not have two competing truths.
  - Cross-language protocol vectors are not yet genuinely shared.
  - Studio still contains direct fetch/EventSource integration and demo data.
  - UDS daemon installation/entrypoint is incomplete.
  - Independent M‑4/M‑6/M‑6.5 acceptance is still missing.
  - WP‑B1/M‑5b remains undeterminable until CONVERGENCE-BASE-v1 exists remotely.
  - M‑7 is not complete runtime integration.
  - M‑8 remains prototype-only.

  Dev A’s schema findings are partly obsolete because the current tree already contains the discriminated schema, ListRuns, GetCapabilities, and
  canonical error vocabulary. Reconcile the final source before making duplicate changes.

  ## 2. Immediate P0 — reconcile concurrent work

  1. Freeze edits to overlapping files.
  2. Establish one reviewed source commit.
  3. Compare the Dev A and Dev B diffs file-by-file.
  4. Preserve the strongest implementation without blind cherry-picks.
  5. Confirm no lost changes in:
      - schemas/v4/runtime-service.schema.json;
      - vanguard/packages/runtime/service/service.py;
      - vanguard/packages/runtime/service/inbox.py;
      - vanguard/packages/runtime/service/studio_gateway.py;
      - vanguard/packages/runtime/service/server.py;
      - vanguard/clients/client-core/src/*.

  6. Assign ownership:
      - Dev A: schema, client-core, CLI/TUI/Studio.
      - Dev B: RuntimeService, stores, UDS, HTTP/SSE.

  7. No developer may edit the other lane’s owned files without explicit review.

  ## 3. P1 — freeze one protocol

  Canonical protocol: vg.4 command, receipt, event, and error frames.

  Required work:

  - Keep the strict discriminated frame schema.
  - Keep the 11-command union and run-scope rules.
  - Wire validate_frame_envelope() and validate_command() into service ingress.
  - Reject malformed frames before idempotency or ledger access.
  - Use one error vocabulary:
    invalid_request, unauthenticated, permission_denied, not_found, conflict, incompatible_version, frame_too_large, rate_limited, not_available,
    internal.

  - Preserve transport_interrupted as client-local only.
  - Preserve server error code and retryability in UDS and HTTP clients.
  - Use one signed ApprovalDecision shape everywhere.
  - Remove conflicting unused command-envelope APIs only after all imports are migrated.
  - Add deprecation notes or a beta-breaking-version note if public exports are removed.
  - Create one shared golden-vector corpus consumed by Python and TypeScript tests.
  - Do not add a runtime schema dependency to client-core; validate with existing lightweight parsers and vectors.

  Required negative vectors:

  - unknown frame type;
  - wrong version;
  - missing frame ID;
  - command with forbidden runId;
  - command missing required runId;
  - unknown command field;
  - unknown payload field;
  - invalid approval signature shape;
  - unknown error code;
  - receipt containing both success and error fields;
  - event frame containing receipt data.

  ## 4. P2 — make RuntimeService real and durable

  Owner: Dev B.

  Implement:

  - Persistent SQLite-WAL configuration required by the gateway.
  - Separate command idempotency storage from event truth.
  - Exactly one canonical event store.
  - Atomic sequence allocation and append.
  - Atomic notification after successful append.
  - Durable run listing and status projection.
  - Real Checkpoint persistence.
  - Real Resume continuation from a checkpoint.
  - Cancellation that interrupts execution and records terminal facts.
  - Failure handling that never converts exceptions into completed.
  - CAS using expectedSeq, returning canonical conflict.
  - GetCapabilities derived from actual feature availability.
  - Explicit partial, disabled, and unavailable capability states.
  - No silent fallback from durable store to :memory:.
  - No direct ledger writes from HTTP handlers.

  The run worker must invoke the canonical path:

  Runtime.execute_profiled(
      manifest_path,
      task_context,
      profile_id=...,
      model=...,
      store=canonical_sqlite_store,
      ...
  )

  The worker must persist:

  - run start;
  - every canonical event;
  - approval requests/resolutions;
  - checkpoint;
  - cancellation;
  - completion or failure;
  - final run digest and event sequence.

  ## 5. P3 — complete UDS and HTTP/SSE

  Owner: Dev B.

  ### UDS

  Implement and verify:

  - NDJSON framing;
  - 1 MiB frame limit;
  - secure 0600 socket;
  - request validation;
  - response correlation with inReplyTo;
  - canonical error frames;
  - command idempotency;
  - stream cursor resume;
  - duplicate suppression;
  - sequence-gap detection;
  - clean disconnect and reconnect;
  - graceful daemon shutdown;
  - installed daemon entrypoint.

  ### HTTP/SSE

  Implement the beta route registry. Every route must map to a validated command or read projection.

  Required groups:

  - health;
  - capabilities;
  - run launch/list/get;
  - cancel;
  - checkpoint;
  - resume;
  - event stream;
  - artifact explanation;
  - correction recording;
  - approval resolution;
  - composition inspection;
  - agent projection and lineage;
  - topology inspection;
  - skill/evaluation status;
  - governance audit.

  Every route must define:

  - method and path;
  - request/response schema;
  - command mapping;
  - authorization;
  - idempotency;
  - CAS behavior;
  - error mapping;
  - redaction;
  - capability behavior.

  SSE requirements:

  - afterSeq;
  - Last-Event-ID;
  - keepalive frames;
  - WAL replay before live subscription;
  - strict increasing sequence;
  - explicit gap response;
  - reconnect without event loss;
  - terminal close after completed/failed/cancelled run.

  ## 6. P4 — finish client-core, CLI, TUI, and Studio

  Owner: Dev A.

  Implement:

  - Complete HttpRuntimeClient.
  - Implement getRun, cancel, checkpoint, resume, artifact explanation, correction recording, approval resolution.
  - Return actual CommandReceipt values.
  - Parse canonical receipt errors.
  - Preserve all server error codes.
  - Use one approval-signing implementation for UDS and HTTP.
  - Add list-runs and capability APIs to client-core if required by CLI/Studio; update all fake, replay, scenario, and live implementations
    together.

  - Ensure LiveRuntimeClient and HttpRuntimeClient have equivalent behavior.
  - Make CLI commands use client-core only.
  - Make TUI consume live projections and cursor-resumable streams.
  - Replace Studio direct fetch and EventSource calls with HttpRuntimeClient.
  - Keep demo fixtures behind an explicit demo mode.
  - Never silently replace a failed live connection with demo data.
  - Render capability-disabled features as disabled, not successful.
  - Add visible reconnect, gap, approval, cancellation, checkpoint, resume, and error states.

  ## 7. P5 — frontend-backed vertical slice

  Both developers integrate one complete path:

  CLI/TUI/Studio
  → client-core
  → HTTP/SSE or UDS
  → RuntimeService
  → Runtime.execute_profiled
  → SQLite-WAL
  → replayable event stream

  Acceptance scenario:

  1. Start a run from CLI.
  2. Attach from TUI.
  3. Observe the same events in Studio.
  4. Receive an approval request.
  5. Sign and resolve it.
  6. Checkpoint the run.
  7. Disconnect the client.
  8. Reconnect from the last cursor.
  9. Resume the run.
  10. Inspect an artifact.
  11. Record a correction.
  12. Reconstruct the final state in a fresh process.
  13. Confirm all three surfaces show equivalent state.

  ## 8. P6 — close M‑4 through M‑6.5

  Leadership, not the producing developer, must:

  - independently review M‑4;
  - independently review M‑6;
  - independently review M‑6.5;
  - issue separate signed acceptance or negative envelopes;
  - resolve WP‑B1 evidence truthfully;
  - create CONVERGENCE-BASE-v1 only after ADR‑0102 prerequisites;
  - verify the annotated tag remotely;
  - update boards only from receipts.

  No test result, merge, or producer envelope closes a milestone.

  ## 9. P7 — complete M‑7

  Owner order: Dev A, then Dev B.

  Dev A:

  - Consume topology artifacts through the public runtime.
  - Validate authority-free topology extensions.
  - Lower them to ordinary runtime plans.
  - Execute direct, planner/executor/reviewer, and fork/read/merge patterns.
  - Keep the sequential scheduler as default.
  - Use ordinary M‑6 delegation.
  - Add correlated monotonic telemetry outside the ledger.
  - Prove disabled topology parity.

  Dev B:

  - Execute M7‑01.
  - Measure selector disjointness, sink safety, causal completeness, timing completeness, contention, and recovery.
  - Treat unknown information conservatively as non-parallelizable.
  - Produce signed M7‑01 evidence.
  - Ratify ADR‑0099 as:
      - bounded read concurrency, or
      - SEQUENTIAL_CONFIRMED.

  No concurrency feature is accepted from library presence alone.

  ## 10. P8 — complete M‑8

  ### Dev A: durable memory

  Implement ADR‑0100:

  - verified AuthorizedMemoryContext;
  - issuer, subject, action, selector, tenant, project, purpose;
  - expiry and revocation epoch;
  - verification receipt;
  - authorization at use time;
  - knowledge, experience, project-memory, and skill categories;
  - SQLite-WAL metadata/index storage;
  - CAS blob storage;
  - blob-first, metadata-second, causal-fact-third writes;
  - append, supersede, invalidate;
  - authorization before ranking;
  - retrieval provenance;
  - tenant/project/category isolation;
  - retention and quarantine;
  - legal hold;
  - restore;
  - garbage collection;
  - WAL safety checks.

  ### Dev B: governed learning

  Implement:

  - sealed development, held-out, adversarial, and transfer workloads;
  - generator/evaluator/promoter separation;
  - immutable composition candidates;
  - signed evaluation evidence;
  - held-out lift;
  - regression budgets;
  - durable CAS promotion registry;
  - concurrent promotion conflict handling;
  - signed promotion receipts;
  - runtime-visible promotion;
  - real injected-regression rollback;
  - restart/crash recovery;
  - rejection of presence-only gains.

  M‑8 closes only after durable memory, measured learning, promotion, rollback, security evidence, replay evidence, and independent acceptance.

  ## 11. Documentation cleanup

  Keep canonical:

  - VISION.md;
  - docs/SPEC.md;
  - accepted ADRs;
  - docs/03_execution/milestones.md;
  - docs/03_execution/backlog.md;
  - docs/03_execution/sprint_active.md;
  - docs/03_execution/sprint_upcoming.md.

  Update canonical execution documents to reflect:

  - actual evidence states;
  - the integration packages;
  - current ownership;
  - current dependencies;
  - M‑7 and M‑8 progress;
  - M‑9/M‑10 remaining unauthorized.

  Update descriptive README and architecture/contract pages that still describe older M‑4/M‑6 states.

  Mark these as historical, advisory, and non-authorizing:

  - director development plan;
  - director convergence plan;
  - masterplan todo;
  - sprint_doing reports;
  - Higgs concept review;
  - old M‑4/M‑5/M‑6/M‑7/M‑8 reports.

  Do not delete historical evidence until provenance has been extracted and the repository retention decision is explicit.

  ## 12. Verification order

  After reconciliation and implementation:

  1. documentation/status consistency;
  2. schema and code-generation checks;
  3. boundary and domain-blindness checks;
  4. TCB budget;
  5. isolation and secret scanning;
  6. Python contract vectors;
  7. TypeScript contract vectors;
  8. RuntimeService command tests;
  9. SQLite-WAL restart/replay/CAS tests;
  10. qualified Linux UDS tests;
  11. HTTP route tests;
  12. SSE reconnect/gap tests;
  13. client-core tests;
  14. CLI/TUI tests;
  15. Studio browser tests;
  16. approval signature tests;
  17. M‑7 falsifiers;
  18. M‑8 security and rollback falsifiers;
  19. full suite;
  20. independent evidence review.

  ## 13. Beta definition of done

  The M‑8 beta is releasable only when:

  - M‑4 through M‑8 have truthful evidence states;
  - mandatory accepted milestones have independent receipts;
  - one persistent runtime service uses one WAL event ledger;
  - CLI, TUI, and Studio operate against the same backend;
  - UDS and HTTP/SSE share the same contracts;
  - approvals are cryptographically verified;
  - reconnect and replay are lossless;
  - checkpoint/resume are real;
  - M‑7 topology execution is integrated and measured;
  - M‑8 memory is durable and authorization-checked;
  - promotion is signed, CAS-protected, and reversible;
  - no Kernel/domain authority semantics were added;
  - M‑9/M‑10 remain out of scope and unauthorized.

# SUGGESTED: VANGUARD STANDALONE CLI v1.0 PRODUCTION BLUEPRINT

### 1. Title & Executive Scope
**Vanguard Standalone CLI v1.0 Production Blueprint**
Complete architectural specification for the standalone `vanguard` binary and CLI distribution. This document establishes the foundational design, security boundaries, storage mechanisms, and operational matrix for deploying Vanguard as a globally accessible, zero-configuration cognitive engine.

### 2. Chapter 1: Global Distribution & Standalone Binary Architecture
- **Entrypoint configuration in `pyproject.toml`**: The python package mandates a definitive console script binding:
  ```toml
  [project.scripts]
  vanguard = "vanguard.packages.runtime.cli:main"
  ```
- **Standalone curl installer specification (`install_vanguard.sh`)**: We expose a frictionless bootstrap mechanic that fetches and evaluates a signed release:
  ```bash
  curl -fsSL https://raw.githubusercontent.com/brainopensource/cognitive-framework/main/install_vanguard.sh | bash
  ```
  This installer is responsible for detailing virtual environment creation in `~/.vanguard/venv`, automated symlinking to `~/.local/bin/vanguard`, dependency locking, and global environment detection to seamlessly adapt to diverse topologies.
- **NPM TypeScript CLI bridge packaging (`@vanguard/cli`)**: A lightweight Node wrapper published to npm, enabling seamless cross-ecosystem ingestion while delegating underlying execution to the Python backend.

### 3. Chapter 2: Zero-Config Project Discovery & AST Symbol Indexing
- **Workspace root heuristic detection**: The CLI context automatically resolves its operational boundary by searching upwards for standard repository markers: `.git`, `pyproject.toml`, `package.json`, `Cargo.toml`, or `go.mod`.
- **Automatic `.vanguard/` layout creation**: The system scaffolds an ephemeral/durable state repository within the resolved root, initializing `.vanguard/events.sqlite3`, `.vanguard/blobs/`, and `.vanguard/grants/`.
- **Incremental AST symbol extraction**: A non-blocking daemon utilizing `resource_selector.py` combined with tree-sitter bindings. This pipeline incrementally builds rich symbol maps without requiring manual configuration, surfacing in-context references for autonomous execution.

### 4. Chapter 3: Autonomous Cognitive Turn Engine & Command Dispatch
- **Direct invocation**: Commands traverse the canonical boundary by directly calling `Runtime.execute_profiled` using an injected `TaskContext`, eliminating HTTP overhead for local tasks.
- **Real CLI usage patterns**: The CLI surface is optimized for both targeted interventions and deep exploratory iterations. Example usage:
  ```bash
  # Quick single-turn fix
  vanguard "Fix the ValueError in blueprints.py"

  # Autonomous multi-file sprint planning and implementation
  vanguard sprint "Implement user authentication endpoints with JWT in FastAPI"

  # Security and invariant audit
  vanguard review --strict

  # Regression oracle verification
  vanguard test --oracle
  ```
- **The 4 core tools**: Interaction within the execution loop is strictly mediated through these canonical interfaces: `fs.read`, `fs.search`, `patch.apply`, and `proc.exec`.

### 5. Chapter 4: Fail-Closed TCB Security, Bounded Budgets & SQLite-WAL Durability
- **13-stage Kernel S0–S12 pipeline description**: Every instruction traverses a rigorous pipeline (S0 Observe $\to$ S1 Authenticate $\to$ S2 Authorize $\to$ S3 Reserve $\to$ ... $\to$ S11 Audit $\to$ S12 Settle).
- **Sandbox chroot traversal protection**: A hardened security boundary that guarantees a fail-closed response if any capability or artifact path resolves outside the designated workspace root.
- **Cryptographic Ed25519 `OperatorSigner` autonomous grant lifecycle**: Session capabilities and automated tasks rely on tightly scoped cryptographic tokens issued via an operator key pair.
- **Immutable SQLite Write-Ahead Log (`events.sqlite3`) and SHA-256 CAS blob storage**: The system leverages WAL mode for concurrent, acid-compliant transaction recording, coupled with SHA-256 CAS blob storage for verifiable artifact retrieval.

### 6. Chapter 5: Release Qualification Ladder & Verification Matrix
- **Gate progression from M-4 through M-8**: Systematic maturation of the system spanning foundational features (M-4), topologies (M-5), recursive delegation (M-6), harness capabilities (M-7), and governed memory (M-8).
- **Falsifier requirements**: Strict verification tests (RF-95, RF-100 to RF-117) validating systemic invariants prior to any production release.
- **Real-world SWE-bench Verified qualification matrix**: Empirical benchmarking confirming autonomous SWE task efficacy on standard, independently maintained datasets.

### 7. Compact ASCII TODO Matrix

| ID     | Subsystem  | Target Task Specification                           | Gate    |
|--------|------------|-----------------------------------------------------|---------|
| CLI-01 | Dist       | Wire `pyproject.toml` script entrypoint             | M-4     |
| CLI-02 | Dist       | Implement and publish `install_vanguard.sh`         | M-4     |
| CLI-03 | Dist       | Scaffold `@vanguard/cli` NPM bridge                 | M-4     |
| CLI-04 | Index      | Workspace heuristic root detection logic            | M-4     |
| CLI-05 | Index      | Automatic `.vanguard/` state scaffolding            | M-4     |
| CLI-06 | Index      | `resource_selector.py` + tree-sitter AST indexer    | M-5     |
| CLI-07 | Exec       | Map CLI inputs to `Runtime.execute_profiled`        | M-4     |
| CLI-08 | Exec       | Build parsers for standard usage patterns           | M-4     |
| CLI-09 | Sec        | Instrument and audit S0-S12 pipeline                | M-6     |
| CLI-10 | Sec        | Enforce chroot bounds and budget fail-closed paths  | M-6     |
| CLI-11 | Sec        | Inject Ed25519 `OperatorSigner` token lifecycles    | M-6     |
| CLI-12 | Store      | SQLite-WAL configuration + CAS blobs integration    | M-4     |
| CLI-13 | Release    | Achieve SWE-bench Verified zero-shot milestones     | M-7/M-8 |

### 8. Concluding One-Phrase Summary
Vanguard Standalone CLI v1.0 delivers a zero-config, globally distributed, securely bounded autonomous cognitive engine directly into any developer's local workspace.



# WAVES MASTERPLAN

