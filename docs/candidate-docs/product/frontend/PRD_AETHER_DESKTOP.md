---
id: product.frontend.desktop
class: product
authority: proposal
canonical_for:
  - aether-desktop-product-requirements
status: proposed
owner: product-architecture
version: "0.1.0"
last_verified: 2026-08-29
future_canonical_owner: docs/product/frontend/PRD_AETHER_DESKTOP.md
subordinate_to:
  - product.frontend.platform
  - ../../../SPEC.md
  - ../../../01_law/SECURITY.md
---

# Product Requirements Document: AETHER Desktop (Consumer/Developer Workspace)

## 1. Executive Summary & Product Thesis

**AETHER Desktop** is the minimalist, native desktop client for the AETHER substrate. It is designed to provide software engineers, researchers, and creators with a streamlined conversational workspace that conceals backend complexity by default while offering progressive disclosure into agent reasoning, tool activity, diffs, and verification receipts.

### 1.1 Core Thesis

> **Frictionless conversational simplicity for everyday tasks; deep forensic visibility for engineers. Desktop is an elegant daily workspace, not a bloated telemetry dashboard.**

AETHER Desktop adheres strictly to a clean conversational layout while delivering agentic capabilities: workspace-scoped filesystem operations, real-time code diff inspection, cryptographic action approvals, and content-addressed artifact previews.

---

## 2. AS_BUILT vs. TARGET State Assessment

| Dimension | AS_BUILT (Repository Evidence) | TARGET (Electroweak Baseline) | Strategic Gap & Action |
|---|---|---|---|
| **Packaging & Native Shell** | Browser-only prototype (`vanguard/clients/studio/`) served over custom Node server. | Native desktop application packaged with **Tauri 2** (WebKit on macOS/Linux, WebView2 on Windows). | Package frontend with Tauri 2; eliminate Node.js runtime dependency on user machines. |
| **UI Framework & Footprint** | React 18 with custom CSS in Studio (runtime overhead not yet formally benchmarked). | **SolidJS** + **Vite** on **Bun**, utilizing fine-grained reactive primitives and semantic tokens. | Migrate UI components to SolidJS for targeted low memory usage and responsive rendering. |
| **UX & Layout Model** | Sprawling dashboard with 22 disparate engineering views (`StudioApp.tsx`). | Minimalist conversation-first desktop layout with progressive disclosure cards and slide-out drawers. | Refactor into clean two-pane layout: conversation sidebar + active chat/evidence transcript. |
| **Key & Secret Storage** | In-memory web signer with non-persistent session keys (`WebCryptoSigner`). | Native OS Keychain integration (macOS Keychain, Windows Credential Manager, Secret Service API). | Implement secure keychain storage via thin Tauri Rust bridge. |

---

## 3. Technology Stack & Native Boundaries

### 3.1 Proposed Architectural Hierarchy

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        SOLIDJS + VITE FRONTEND                         │
│   @aether/ui-web ──► @aether/state ──► @aether/client (TypeScript)      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Validated Native IPC
┌───────────────────────────────────▼────────────────────────────────────┐
│                       THIN TAURI 2 RUST LAYER                          │
│   Process Lifecycle │ Secure Keychain │ Native Windows │ Dialogs       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Loopback UDS / HTTP SSE
┌───────────────────────────────────▼────────────────────────────────────┐
│                    AETHER RUNTIME SERVICE (PYTHON)                     │
└────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Native Boundary Requirements

- **Desktop IPC Boundary**: Desktop MUST communicate with native platform integrations through a versioned, validated native IPC boundary. *Note: Exact IPC message schemas and serialization formats belong to future frontend reference documentation (`docs/reference/frontend/tauri-ipc-contract.md`).*
- **Approved Rust Responsibilities**:
  - Managing the Python runtime sidecar lifecycle (spawn, health check, graceful shutdown).
  - Interfacing with OS Keychains for storing Ed25519 signing keys.
  - Native file system dialogs (folder picker for workspace selection).
  - Native window framing, tray icon, and system notifications.
- **Strictly Forbidden Rust Responsibilities**:
  - MUST NOT implement agent logic, turn execution, or prompt assembly.
  - MUST NOT maintain event projections, reducers, or conversation histories.
  - MUST NOT parse domain contracts or execute business rules.

---

## 4. UX Model & Information Architecture

```text
┌──────────────────┬─────────────────────────────────────────────────────────────┐
│ ⊞ AETHER         │  Agent: Coding Agent (v0.9.1) ▾   Workspace: /Coding/Aether │
├──────────────────┼─────────────────────────────────────────────────────────────┤
│ ⊕ New Chat       │                                                             │
│ 🔍 Search chats   │  [User]                                                     │
│                  │  Analyze and resolve the memory leak in TableWorld adapter. │
│ TODAY            │                                                             │
│ • TableWorld Mem │  [AETHER]                                                   │
│ • Auth Race Fix  │  Investigating memory allocation in TableWorld bindings...  │
│ • Benchmark S33  │                                                             │
│                  │  ┌────────────────────────────────────────────────────────┐ │
│ YESTERDAY        │  │ ▸ Read 6 files (table.py, bindings.py, ...)            │ │
│ • M-7 Topology   │  │ ▾ Applied patch to vanguard/adapters/bindings/table.py │ │
│ • Doc Synthesis  │  │   [View Inline Diff]                                   │ │
│                  │  │ ▸ Ran 18 tests · 18 passed                             │ │
│ ⚙ Settings       │  └────────────────────────────────────────────────────────┘ │
│ 👤 Developer     │  Identified unreleased row handles during batch scan.       │
│                  │  Fixed via RAII context manager.                            │
│                  │                                                             │
│                  │  ┌────────────────────────────────────────────────────────┐ │
│                  │  │ Message AETHER...                                    ▲ │ │
│                  │  └────────────────────────────────────────────────────────┘ │
└──────────────────┴─────────────────────────────────────────────────────────────┘
```

### 4.1 Layout Regions

1. **Left Navigation Sidebar (Collapsible)**:
   - "New Chat" action button.
   - Historical conversation list grouped by date (Today, Yesterday, Last 7 Days, Older).
   - Search bar for full-text query across conversations and artifacts.
   - Settings launcher.
2. **Main Transcript Pane**:
   - Header with active Agent/Workflow selector and Workspace directory breadcrumb.
   - Chronological message history with Markdown, syntax highlighting, and progressive disclosure cards.
   - Message composer at the bottom with multi-line input and agent triggers.
3. **Slide-Out Forensic Drawer (Collapsible)**:
   - Opens on demand when the user clicks an activity card, diff link, or artifact reference.
   - Houses the Split-Pane Diff Viewer, Test Result Matrix, and Citation Views.

---

## 5. Functional Feature Modules

### 5.1 Conversational Transcript & Progressive Disclosure

- **Streaming Syntax Highlighting**: Syntax coloring of streaming code blocks without layout jumps.
- **Progressive Activity Cards**:
  - *File Read Card*: `▸ Read 8 files [0.12s]` -> expands to list of files and line counts.
  - *Patch Card*: `▾ Modified 2 files (+14, -3)` -> renders inline unified diff with syntax coloring.
  - *Verification Card*: `▸ Tests · 42 passed (100%) [0.85s]` -> expands to test suite summary.
  - *Research Card*: `▸ 14 citations analyzed` -> expands to source URLs and extracted claims.

### 5.2 Interactive Diff Viewer (`@aether/ui-web`)

- **Split & Unified Modes**: Toggle between side-by-side split view and unified patch view.
- **Line Change Navigation**: Jump between additions and deletions.
- **File Tree Navigation**: Filter multi-file diffs by directory or modification status.

### 5.3 Cryptographic Approval Modal

When the agent attempts a governed effect (e.g. disk write, shell command):

1. A modal dialog interrupts the stream with a clear description of the requested effect.
2. Displays the exact normalized diff or command line arguments.
3. Provides an "Approve & Apply" button that cryptographically signs the challenge with the local Ed25519 key stored in the OS Keychain.
4. Provides a "Reject" button allowing the user to provide corrective feedback directly to the agent.

---

## 6. Provisional Performance Targets

The following values represent **provisional engineering budgets (TARGET thresholds)** subject to verification via automated performance benchmarks:

- **Cold Startup Latency**: Provisional target of $<1.2\text{ s}$ from application icon click to interactive UI on reference hardware.
- **Memory Footprint (Idle)**: Provisional target of $<60\text{ MB}$ RAM total across native and WebView processes.
- **Memory Footprint (Active Streaming)**: Provisional target of $<120\text{ MB}$ RAM during high-speed token ingestion.
- **Scrolling Performance**: Target 60 fps rendering during continuous scrolling over long conversations using DOM virtualization.
- **Installer Package Size**: Target $<25\text{ MB}$ total download size across macOS (.dmg), Linux (.AppImage/.deb), and Windows (.msi).

---

## 7. Security & Sandboxing Requirements

- **WebView Sandboxing**: WebViews MUST operate with strict CSP (`default-src 'self'`). Inline script execution is disabled.
- **Zero Raw HTML Injection**: Markdown parser MUST sanitize arbitrary HTML tags to prevent XSS.
- **External Link Mediation**: All hyperlinks MUST open in the default external operating system browser, never inside the application WebView.
- **Key Isolation**: Ed25519 private keys MUST be marked non-exportable in OS Keychains where supported.

---

## 8. Non-Goals & Out-of-Scope Boundaries

- **NON-GOAL 1**: Embedding a full terminal emulator or xterm.js instance inside Desktop.
- **NON-GOAL 2**: Providing an integrated software development environment (IDE) with language servers and debuggers.
- **NON-GOAL 3**: Supporting multi-tenant cloud collaboration features within the local-first desktop shell.

---

## 9. Candidate Future Documents & Ownership References

- **Candidate Architecture Owner**: `docs/architecture/frontend/desktop-tauri-boundary.md`
- **Candidate Reference Owner**: `docs/reference/frontend/tauri-ipc-contract.md`
- **Candidate Decisions Owner**: `docs/decisions/frontend/0110-tauri2-rust-boundary.md`
- **Candidate Execution Owner**: `docs/execution/frontend/desktop-backlog.md`
