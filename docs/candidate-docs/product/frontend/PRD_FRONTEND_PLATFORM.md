---
id: product.frontend.platform
class: product
authority: proposal
canonical_for:
  - frontend-platform-product-requirements
  - shared-client-substrate-product-requirements
status: proposed
owner: product-architecture
version: "0.1.0"
last_verified: 2026-08-29
future_canonical_owner: docs/product/frontend/PRD_FRONTEND_PLATFORM.md
subordinate_to:
  - ../../../SPEC.md
  - ../../../01_law/RUNTIME.md
  - ../../../01_law/SECURITY.md
---

# Product Requirements Document: AETHER Frontend Platform & Shared Client Substrate

## 1. Executive Summary & Product Thesis

The **AETHER Frontend Platform** defines the foundational requirements, shared client substrate capabilities, state models, design token expectations, security boundaries, and provisional performance targets for all user-facing client applications in the AETHER / ELECTROWEAK ecosystem.

### 1.1 Core Thesis

> **One authoritative backend runtime, one shared TypeScript client substrate, multiple specialized renderers.**

The AETHER architecture is fundamentally event-native and Python-first. The backend Python Trusted Computing Base (TCB) remains the sole authoritative source of truth for execution, policy enforcement, budget attenuation, causal lineage, and durable event recording. Frontend clients are strictly **intention dispatchers and projection engines**. They MUST NOT duplicate or replace backend execution, policy evaluation, or ledger authority.

### 1.2 The Conceptual Composition Hierarchy

```text
                               ┌─────────────────────────────────────────┐
                               │       AETHER RUNTIME (PYTHON TCB)       │
                               │   Observe ──► Decide ──► Authorize ──►  │
                               │        Execute ──► Record (Ledger)      │
                               └────────────────────┬────────────────────┘
                                                    │ UDS NDJSON / HTTP SSE
                               ┌────────────────────▼────────────────────┐
                               │   SHARED CLIENT SUBSTRATE (TS / BUN)    │
                               │  @aether/contracts   @aether/client     │
                               │  @aether/projections @aether/state      │
                               │         @aether/design-tokens           │
                               └────────────────────┬────────────────────┘
                                                    │
                 ┌──────────────────┬───────────────┴───────────────┬──────────────────┐
                 │                  │                               │                  │
        ┌────────▼────────┐┌────────▼────────┐             ┌────────▼────────┐┌────────▼────────┐
        │   AETHER CLI    ││   AETHER TUI    │             │ AETHER DESKTOP  ││   AETHER LAB    │
        │ (Headless / Bun)││(Solid+OpenTUI)  │             │ (Tauri 2+Solid) ││ (Solid Web/App) │
        └─────────────────┘└─────────────────┘             └─────────────────┘└─────────────────┘
```

---

## 2. AS_BUILT vs. TARGET State Assessment

| Dimension | AS_BUILT (Repository Evidence) | TARGET (Electroweak Baseline) | Strategic Gap & Action |
|---|---|---|---|
| **Client Workspace Structure** | Tri-furcated packages (`@vanguard/client-core`, `@vanguard/cli`, `@vanguard/studio`) with fragmented build scripts and local relative links. | Unified Bun monorepo workspace under `vanguard/clients/` with explicit package separation. | Restructure workspace packages into pure shared semantic modules and lightweight renderer shells. |
| **Terminal Rendering** | `@vanguard/cli` uses React 18 + Ink (`ink@^5.1.0`), which relies on React VDOM reconciliation over terminal cells. | `@aether/tui` uses OpenTUI + SolidJS on Bun for fine-grained cell-buffer reactive rendering. | Replace Ink and React VDOM in terminal with fine-grained reactive terminal primitives to address streaming latency concerns. |
| **Desktop / GUI Substrate** | `@vanguard/studio` is an exploratory React 18 SPA with 22 custom views and a custom Node/esbuild server script. | `@aether/desktop` is a minimalist SolidJS application packaged via Tauri 2 with a thin Rust native layer. | Migrate from React DOM to SolidJS + Tauri 2; eliminate Node.js runtime overhead on user systems. |
| **Gateway & Transports** | `studio_gateway.py` contains exploratory pilot simulations (`_pilot_run_simulation`) and legacy route aliases. | Strict `RuntimeService` transport bridge over SQLite WAL events, supporting canonical runtime operations. | Eliminate synthetic simulation loops; enforce strictly ledger-backed streaming. |
| **Wire & Contract Validation** | Manual parsing in `client-core/src/contract/parse.ts` mirroring `schemas/v4/`. | Generated TypeScript types and validation readers compiled directly from canonical JSON schemas. | Establish automated JSON Schema to TypeScript code generation pipeline to prevent contract drift. |

---

## 3. Product Ecosystem & Surface Boundaries

The frontend platform supports four distinct product surfaces, each tailored to specific operational profiles while sharing identical semantic state:

```text
┌─────────────────┬─────────────────┬─────────────────────────────────────────────────────────────┐
│ Product Surface │ Primary Runtime │ Target Personas & Primary Use Cases                         │
├─────────────────┼─────────────────┼─────────────────────────────────────────────────────────────┤
│ **CLI**         │ Bun / TS        │ CI pipelines, DevOps, automated shell scripting, batch runs.│
│ **TUI**         │ Bun / SolidTUI  │ Software engineers, terminal power users, deep-focus coding.│
│ **Desktop**     │ Tauri 2 / Solid │ General developers, researchers, daily conversational tasks.│
│ **Lab**         │ Solid / Web     │ Core systems engineers, benchmark evaluators, kernel audits.│
└─────────────────┴─────────────────┴─────────────────────────────────────────────────────────────┘
```

---

## 4. Shared Client Substrate Requirements

### 4.1 Proposed Monorepo Package Matrix (Candidate Architecture)

The shared substrate is proposed to be partitioned into single-responsibility, framework-agnostic TypeScript packages:

1. **`@aether/contracts`**: Pure TypeScript type definitions, error codes, and validation readers generated from canonical JSON schemas (`schemas/v4/` and `schemas/mhf/`).
2. **`@aether/client`**: Transport abstractions (AF_UNIX UDS NDJSON client, HTTP/SSE client), cursor-resumption state machines, and the unified `RuntimeClient` protocol.
3. **`@aether/projections`**: Pure, deterministic reducer functions that fold canonical event streams into view models (`RunSnapshot`, `TraceGraph`, `EvidenceGrid`, `ApprovalState`).
4. **`@aether/state`**: Framework-agnostic state containers, reactive signals/stores, cache managers, and command dispatch controllers.
5. **`@aether/design-tokens`**: Semantic design token definitions (color palettes, elevation surfaces, spacing, typography, motion curves).
6. **`@aether/ui-web`**: Reusable SolidJS web components shared between Desktop and Lab (DiffViewer, MessageList, ArtifactCard, ApprovalModal).
7. **`@aether/ui-tui`**: Reusable OpenTUI terminal presentation primitives for the interactive TUI.
8. **`@aether/testkit`**: Deterministic test doubles, fake transports, golden event fixtures, and contract validation suites.

*Note: Detailed package configurations, dependencies, and build pipelines belong to future frontend architecture documentation (`docs/architecture/frontend/platform-architecture.md`).*

---

## 5. DRY Architecture & Renderer Seams

### 5.1 The Semantic Boundary Invariant

> **DRY applies to semantics, state machines, and projections; DRY MUST NOT force false component sharing across incompatible rendering targets.**

- **Shared Semantics Across All Clients**:
  - Event parsing, validation, and normalization logic.
  - Causal trace graph generation and fold algorithms.
  - Cryptographically authenticated approval transaction workflows.
  - Command serialization and CAS precondition checks (`expectedSeq`).
  - Capability discovery negotiation.
- **Isolated Per Renderer Target**:
  - Terminal ANSI formatting, terminal cell buffers, and keypress interpreters (`ui-tui`).
  - DOM structures, CSS classes, WebGL canvases, and mouse/touch handlers (`ui-web`).

---

## 6. Shared Design System & Semantic Tokens

All visual products MUST embody the unified aesthetic of AETHER: calm, dense, precise, and evidence-focused.

### 6.1 Token Dimensions & Requirements

- **Product Requirement**: All AETHER interactive surfaces (Desktop, Lab, TUI) MUST share a coherent semantic visual language, including consistent surface elevation hierarchies, 4px/8px spacing grids, monospace formatting for code and cryptographic hashes, and uniform status signaling (proof/pass, hold/review, fail/denied, active flow).
- **Renderer Mapping**:
  - Web applications (Desktop/Lab) consume design tokens via typed TypeScript token constants and CSS Custom Properties.
  - Terminal applications (TUI) consume semantic color mappings translated into 24-bit TrueColor ANSI codes (with automatic 256-color and 16-color fallbacks).

*Note: The exhaustive design token catalog and exact CSS custom property definitions belong to future reference documentation (`docs/reference/frontend/design-tokens.md`).*

---

## 7. Public Runtime Dependency & Boundary Constraints

### 7.1 Boundary Constraints

Frontend code MUST strictly adhere to hexagonal boundary rules:

- **FORBIDDEN**: Frontend importing Python kernel modules or adapters directly.
- **FORBIDDEN**: Frontend executing raw SQL queries against backend SQLite databases.
- **FORBIDDEN**: Frontend relying on unverified in-memory simulation event loops in production modes.
- **FORBIDDEN**: Frontend re-implementing budget algebra, policy gates, or agent spawning logic.

### 7.2 Approved Communication Paths

```text
[Frontend Application]
        │
        ▼
[@aether/client (RuntimeClient)]
        │  (UDS NDJSON Frames / HTTP JSON + SSE Stream)
        ▼
[AETHER RuntimeService Gateway]
        │
        ▼
[AETHER Runtime / LedgerEmitter / SqliteEventStore]
```

---

## 8. Event-Derived State Model

### 8.1 Tripartite State Separation

The frontend MUST maintain a strict separation across three distinct categories of state:

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│ 1. AUTHORITATIVE REMOTE FACTS                                                                │
│    Derived strictly from the immutable event ledger (EventEnvelope) and BlobStore references.│
│    Immutable, append-only, reproducible via deterministic cold replay.                       │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│ 2. REBUILDABLE CLIENT CACHE                                                                  │
│    Projection snapshots, search indexes, layout caches, and stream sequence cursors.         │
│    Keyed by `(runId, asOfSeq)` and safely discardable/rebuildable on demand.                 │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│ 3. EPHEMERAL PRESENTATION STATE                                                              │
│    Active tab, sidebar open/collapsed state, draft input text, scroll offsets, pane sizes.   │
│    Local to the current UI process; zero authority over execution truth.                     │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 9. Session & Conversation Abstraction

### 9.1 Product Abstraction Mapping

A "Conversation" is a product-level container that maps user-facing interactions to underlying kernel executions:

```text
Conversation (Product Layer)
  ├── Conversation ID (UUIDv7)
  ├── Selected Agent / Workflow Descriptor
  ├── User Prompts & Agent Turn Projections
  ├── Canonical Run References (`runId`, `episodeId`)
  ├── Content-Addressed Artifact References (`digest`)
  └── Ephemeral Interaction Metadata (drafts, timestamps)
```

The frontend maps a user prompt to a `StartRun` or `Resume` command dispatched to `RuntimeService`. The resulting sequence of `EventEnvelope` items is projected into turn cards, tool spans, and diff views.

---

## 10. Cryptographic Approval & Governance Requirements

Mutating or privileged actions (file writes, shell execution, network calls, workspace patches) require operator approval under governed execution profiles.

### 10.1 Approval Flow Protocol Requirements

1. **Challenge Presentation**: Frontend renders the challenge with exact syntax-highlighted diffs and parameter breakdowns.
2. **Cryptographic Signing**:
   - The client signs canonical RFC 8785 JSON bytes of the approval decision using an authenticated, versioned operator key.
   - Private keys MUST be stored securely (WebCrypto non-exportable keys, OS Keychain, or hardware tokens) and NEVER transmitted over the wire.
3. **Resolution Submission**: Client dispatches `ResolveApproval` containing the cryptographically signed decision and the CAS precondition `expectedSeq`.
4. **Settlement**: Runtime validates the signature against registered trust roots and emits `ApprovalResolved`.

*Note: Exact wire encodings, signature algorithms, and key registration schemas belong to future reference documentation (`docs/reference/frontend/client-sdk.md`).*

---

## 11. Security, Content Isolation & Sandboxing

### 11.1 Threat Model & Defenses

- **Untrusted Model Outputs**: All model text and external tool results MUST be treated as untrusted. Direct HTML injection (`innerHTML`) is strictly prohibited. Markdown rendering MUST sanitize HTML tags and enforce safe URI schemes (`http:`, `https:`).
- **Workspace Access Isolation**: WebViews MUST NOT have unrestricted direct access to arbitrary local files. Workspace file reads MUST be mediated through audited runtime endpoints.
- **Local Origin Hardening**: Local HTTP gateways MUST bind to `127.0.0.1`, reject non-loopback bindings without explicit authentication tokens, and validate `Origin` and `Host` headers. Wildcard CORS (`*`) is strictly forbidden on mutating routes.

---

## 12. Performance Philosophy & Provisional Budgets

Performance is treated as an architectural requirement. The following figures represent **provisional engineering budgets (proposed TARGET thresholds)** that must be validated and ratified through automated benchmark suites in CI:

| Metric Dimension | Provisional Engineering Target | Evaluation Scope / Context |
|---|---|---|
| **Cold Startup Latency** | $<15\text{ ms}$ (CLI), $<40\text{ ms}$ (TUI), $<1.2\text{ s}$ (Desktop) | Proposed target from binary launch to interactive ready state. |
| **Keystroke / Input Latency** | $<12\text{ ms}$ (TUI), $<16\text{ ms}$ (Desktop) | Proposed target from physical keypress to visible buffer update. |
| **Stream Processing Overhead** | $>1,000\text{ events/sec}$ with $<5\%$ CPU utilization | Proposed target for main thread ingestion and projection fold rate. |
| **Main-Thread Long Tasks** | Zero tasks $>50\text{ ms}$ during continuous streaming | Target threshold to prevent UI frame dropping. |
| **Memory Footprint (Idle)** | $<35\text{ MB}$ (CLI), $<45\text{ MB}$ (TUI), $<60\text{ MB}$ (Desktop) | Target resident memory consumption on reference systems. |
| **Memory Footprint (100k events)**| $<200\text{ MB}$ total client heap | Bounded cache target enforced via virtualized rendering. |

*Note: These provisional targets do not represent empirical facts until formal benchmark evidence is established.*

---

## 13. Testing Strategy & Deterministic Fixtures

### 13.1 Universal Fixture Parity

All client applications MUST be validated against a shared suite of golden event fixtures (`schemas/v4/vectors/`):

1. **Contract Parity Tests**: Verify that TypeScript parsers and Python backend serializers produce byte-identical canonical JSON representations.
2. **Projection Fold Tests**: Ensure that replaying a recorded trajectory (`successful-episode.jsonl`) produces bit-for-bit identical `RunSnapshot` and `EvidenceGrid` models across all renderers.
3. **Cryptographic Signing Tests**: Cross-verify signature generation and verification between TypeScript client signers and backend approval authorities.
4. **Disconnection & Reconnection Tests**: Verify that clients handle network interruptions, simulate cursor gaps, and resume event tailing without duplicate or lost events.

---

## 14. Cross-Client Acceptance Scenario

To achieve product acceptance, the platform MUST support the following end-to-end multi-client workflow:

```text
1. Operator launches AETHER Desktop and opens local repository workspace.
2. Operator creates a conversation, selects "Coding Agent", and prompts: "Fix auth race condition".
3. Desktop dispatches `StartRun` -> Python Runtime initiates execution.
4. Runtime emits `ApprovalRequested` for modifying authentication middleware.
5. Operator inspects unified diff in Desktop and cryptographically signs approval.
6. Patch is applied, tests execute, and episode completes with `satisfied` verdict.
7. Operator closes Desktop, opens terminal, and launches AETHER TUI.
8. TUI attaches to the same run ID, reconstructs identical event history and artifacts.
9. Operator runs `aether run inspect <run-id> --json` via CLI and receives valid JSON matching the TUI/Desktop state.
```

---

## 15. Non-Goals & Out-of-Scope Boundaries

- **NON-GOAL 1**: Creating a browser-side Python execution engine or WebAssembly kernel.
- **NON-GOAL 2**: Supporting arbitrary third-party plugin execution inside the frontend process.
- **NON-GOAL 3**: Implementing ad-hoc, unversioned REST CRUD endpoints that bypass the canonical RuntimeService API catalog.
- **NON-GOAL 4**: Introducing heavy, multi-megabyte visualization or dashboard frameworks into minimal client surfaces.

---

## 16. Candidate Future Documents & Ownership References

This PRD establishes high-level product requirements. Detailed architectural designs, interface specifications, decision records, and sprint backlogs are deferred to their candidate future owners:

- **Candidate Architecture Owner**: `docs/architecture/frontend/platform-architecture.md`
- **Candidate Reference Owner**: `docs/reference/frontend/client-sdk.md`
- **Candidate Decisions Owner**: `docs/decisions/frontend/0107-frontend-stack-ratification.md`
- **Candidate Execution Owner**: `docs/execution/frontend/roadmap.md`
