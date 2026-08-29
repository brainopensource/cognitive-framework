---
id: product.frontend.platform
class: product
authority: proposal
canonical_for:
  - frontend-platform-requirements
  - shared-client-substrate-requirements
  - cross-client-contract-standards
status: proposed
owner: product-architecture
version: "0.1.0"
last_verified: 2026-08-29
future_canonical_owner: docs/product/frontend/PRD_FRONTEND_PLATFORM.md
subordinate_to:
  - ../../SPEC.md
  - ../../01_law/RUNTIME.md
  - ../../01_law/SECURITY.md
---

# Product Requirements Document: AETHER Frontend Platform & Shared Client Substrate

## 1. Executive Summary & Product Thesis

The **AETHER Frontend Platform** defines the foundational requirements, shared contracts, state models, design tokens, security boundaries, and performance service-level agreements (SLAs) for all user-facing client applications in the AETHER / ELECTROWEAK ecosystem.

### 1.1 Core Thesis

> **One authoritative backend runtime, one shared TypeScript client substrate, multiple specialized renderers.**

The AETHER architecture is fundamentally event-native and Python-first. The backend Python Trusted Computing Base (TCB) remains the sole authoritative source of truth for execution, policy enforcement, budget attenuation, causal lineage, and durable event recording. Frontend clients are strictly **intention dispatchers and projection engines**. They MUST NOT become secondary execution engines, policy verifiers, or ad-hoc state stores.

### 1.2 The Composition Hierarchy

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
| **Client Workspace Structure** | Tri-furcated packages (`@vanguard/client-core`, `@vanguard/cli`, `@vanguard/studio`) with fragmented build scripts and local relative links. | Unified Bun monorepo workspace under `vanguard/clients/` with clear package separation. | Restructure workspace packages into pure shared modules and lightweight renderer shells. |
| **Terminal Rendering** | `@vanguard/cli` uses React 18 + Ink (`ink@^5.1.0`), resulting in full-tree VDOM diffs and high token streaming overhead. | `@aether/tui` uses OpenTUI + SolidJS on Bun for fine-grained cell-buffer reactive rendering. | Replace Ink and React VDOM in terminal with fine-grained reactive terminal primitives. |
| **Desktop / GUI Substrate** | `@vanguard/studio` is an exploratory React 18 SPA with 22 custom views and a custom Node/esbuild server script. | `@aether/desktop` is a minimalist SolidJS application packaged via Tauri 2 with a thin Rust native layer. | Migrate from React DOM to SolidJS + Tauri 2; eliminate Electron-style bloat. |
| **Gateway & Transports** | `studio_gateway.py` contains mock pilot simulations (`_pilot_run_simulation`) and inconsistent route aliases. | Strict `RuntimeService` transport bridge over SQLite WAL events, supporting the 45-route API catalog. | Eliminate synthetic simulation loops; enforce strictly ledger-backed streaming. |
| **Wire & Contract Validation** | Manual parsing in `client-core/src/contract/parse.ts` mirroring `schemas/v4/`. | Generated TypeScript types and validation readers compiled directly from canonical JSON schemas. | Establish automated JSON Schema to TypeScript code generation pipeline. |

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

### 4.1 Monorepo Package Matrix

The shared substrate MUST be partitioned into single-responsibility, framework-agnostic TypeScript packages:

1. **`@aether/contracts`**: Pure TypeScript type definitions, error codes, and validation readers generated from canonical JSON schemas (`schemas/v4/` and `schemas/mhf/`).
2. **`@aether/client`**: Transport abstractions (AF_UNIX UDS NDJSON client, HTTP/SSE client), cursor-resumption state machines, and the unified `RuntimeClient` protocol.
3. **`@aether/projections`**: Pure, deterministic reducer functions that fold canonical event streams into view models (`RunSnapshot`, `TraceGraph`, `EvidenceGrid`, `ApprovalState`).
4. **`@aether/state`**: Framework-agnostic state containers, reactive signals/stores, cache managers, and command dispatch controllers.
5. **`@aether/design-tokens`**: Semantic design token definitions (color palettes, elevation surfaces, spacing, typography, motion curves).
6. **`@aether/ui-web`**: Reusable SolidJS web components shared between Desktop and Lab (DiffViewer, MessageList, ArtifactCard, ApprovalModal).
7. **`@aether/ui-tui`**: Reusable OpenTUI terminal presentation primitives for the interactive TUI.
8. **`@aether/testkit`**: Deterministic test doubles, fake transports, golden event fixtures, and contract validation suites.

---

## 5. DRY Architecture & Renderer Seams

### 5.1 The Semantic Boundary Invariant

> **DRY applies to semantics, state machines, and projections; DRY MUST NOT force false component sharing across incompatible rendering targets.**

- **Shared Across All Clients**:
  - Event parsing, validation, and normalization logic.
  - Causal trace graph generation and fold algorithms.
  - Ed25519 cryptographic approval transaction workflows.
  - Command serialization and CAS precondition checks (`expectedSeq`).
  - Capability discovery negotiation.
- **Isolated Per Renderer Target**:
  - Terminal ANSI formatting, terminal cell buffers, and keypress interpreters (`ui-tui`).
  - DOM structures, CSS classes, WebGL canvases, and mouse/touch handlers (`ui-web`).

---

## 6. Shared Design System & Semantic Tokens

All visual products MUST embody the unified aesthetic of AETHER: calm, dense, precise, and evidence-focused.

### 6.1 Token Dimensions (`@aether/design-tokens`)

```text
┌─────────────────┬───────────────────────────────────────────────────────────────────────────┐
│ Token Category  │ Semantic Scales & Values                                                  │
├─────────────────┼───────────────────────────────────────────────────────────────────────────┤
│ **Surfaces**    │ Canvas (Base), Surface (Panels), Raised (Cards), Overlay (Dialogs/Popovers│
│ **Borders**     │ Subtle (`rgba(255,255,255,0.06)`), Medium (`0.12`), Strong (`0.24`)       │
│ **Typography**  │ Sans (UI copy, humanist), Mono (Code, hashes, tokens, sequences, metrics) │
│ **Spacing**     │ 4px base grid: `space-1` (4px), `space-2` (8px), `space-4` (16px), etc.   │
│ **Radii**       │ `radius-sm` (4px), `radius-md` (8px), `radius-lg` (12px)                  │
│ **Signals**     │ Success (Proof/Pass), Warning (Hold/Review), Danger (Fail), Accent (Flow)│
└─────────────────┴───────────────────────────────────────────────────────────────────────────┘
```

- **Web Applications (Desktop/Lab)**: Consume design tokens via typed TypeScript token constants and CSS Custom Properties.
- **Terminal Applications (TUI)**: Consume semantic color mappings translated into 24-bit TrueColor ANSI codes (with automatic 256-color and 16-color fallbacks).

---

## 7. Public Runtime Dependency & Boundary Constraints

### 7.1 Forbidden Dependency Paths

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

### 10.1 Approval Flow Protocol

1. **Challenge Issuance**: Runtime emits `ApprovalRequested` containing an `approvalId`, `action`, `argsDigest`, `descriptorDigest`, `normalizedDiff`, and `expiresAt` timestamp.
2. **Presentation**: Frontend renders the challenge with exact syntax-highlighted diffs and parameter breakdowns.
3. **Cryptographic Signing**:
   - The client signs canonical RFC 8785 JSON bytes of the `ApprovalDecision` using an Ed25519 private key.
   - Private keys MUST be stored securely (WebCrypto non-exportable keys, OS Keychain, or hardware tokens) and NEVER transmitted over the wire.
4. **Resolution Submission**: Client dispatches `ResolveApproval` containing the 128-character hex Ed25519 signature and the CAS precondition `expectedSeq`.
5. **Settlement**: Runtime validates the signature against registered trust roots and emits `ApprovalResolved`.

---

## 11. Security, Content Isolation & Sandboxing

### 11.1 Threat Model & Defenses

- **Untrusted Model Outputs**: All model text and external tool results MUST be treated as potentially malicious. Direct HTML injection (`innerHTML`) is strictly prohibited. Markdown rendering MUST sanitize HTML tags and enforce safe URI schemes (`http:`, `https:`).
- **Workspace Access Isolation**: WebViews MUST NOT have direct access to arbitrary local files. Workspace file reads MUST be mediated through the runtime's audited `ExplainArtifact` or authorized workspace endpoints.
- **Local Origin Hardening**: Local HTTP gateways MUST bind to `127.0.0.1`, reject non-loopback bindings without explicit TLS/authentication tokens, and validate `Origin` and `Host` headers. Wildcard CORS (`*`) is strictly forbidden on mutating routes.

---

## 12. Performance Philosophy & SLA Budgets

Performance is an architectural invariant, not an afterthought.

| SLA Metric | Target Threshold | Scope / Context |
|---|---|---|
| **Cold Startup Latency** | $<15\text{ ms}$ (CLI), $<40\text{ ms}$ (TUI), $<1.2\text{ s}$ (Desktop) | From process invocation to interactive ready state. |
| **Keystroke / Input Latency** | $<12\text{ ms}$ (TUI), $<16\text{ ms}$ (Desktop) | From physical keypress to visible buffer update. |
| **Stream Processing Overhead** | $>1,000\text{ events/sec}$ with $<5\%$ CPU utilization | Main thread ingestion and projection fold rate. |
| **Main-Thread Long Tasks** | Zero tasks $>50\text{ ms}$ during continuous streaming | Prevents UI stuttering and frame dropping. |
| **Memory Footprint (Idle)** | $<35\text{ MB}$ (CLI), $<45\text{ MB}$ (TUI), $<60\text{ MB}$ (Desktop) | Resident memory consumption. |
| **Memory Footprint (100k events)**| $<200\text{ MB}$ total client heap | Enforced via virtualized rendering and bounded caches. |

---

## 13. Testing Strategy & Deterministic Fixtures

### 13.1 Universal Fixture Parity

All client applications MUST be validated against a shared suite of golden event fixtures (`schemas/v4/vectors/`):

1. **Contract Parity Tests**: Verify that TypeScript parsers and Python backend serializers produce byte-identical canonical JSON representations.
2. **Projection Fold Tests**: Ensure that replaying a recorded trajectory (`successful-episode.jsonl`) produces bit-for-bit identical `RunSnapshot` and `EvidenceGrid` models across all renderers.
3. **Cryptographic Signing Tests**: Cross-verify Ed25519 signature generation and verification between TypeScript `SignerPort` and Python `ApprovalAuthority`.
4. **Disconnection & Reconnection Tests**: Verify that clients handle network interruptions, simulate cursor gaps, and resume event tailing without duplicate or lost events.

---

## 14. Cross-Client Acceptance Scenario

To achieve production acceptance, the platform MUST support the following end-to-end multi-client workflow:

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
- **NON-GOAL 3**: Implementing ad-hoc, unversioned REST CRUD endpoints that bypass the canonical 45-route API catalog.
- **NON-GOAL 4**: Introducing heavy, multi-megabyte visualization or dashboard frameworks into minimal client surfaces.

---

## 16. Deferred Documentation & Canonical References

This PRD establishes high-level product requirements. Detailed architectural designs, interface specifications, decision records, and sprint backlogs are deferred to their canonical owners:

- **Future Architecture Owner**: `docs/architecture/frontend/platform-architecture.md`
- **Future Reference Owner**: `docs/reference/frontend/client-sdk.md`
- **Future Decisions Owner**: `docs/decisions/frontend/0107-frontend-stack-ratification.md`
- **Future Execution Owner**: `docs/execution/frontend/roadmap.md`
