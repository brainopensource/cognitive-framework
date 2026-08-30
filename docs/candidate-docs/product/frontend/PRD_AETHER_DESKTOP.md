---
id: product.frontend.desktop
class: product
authority: proposal
canonical_for:
  - aether-desktop-product-requirements
status: proposed
owner: product-architecture
version: "0.2.0"
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
| **Key & Secret Storage** | In-memory web signer with non-persistent session keys (`WebCryptoSigner`). | Native OS Keychain integration (macOS Keychain, Windows Credential Manager, Secret Service API). | Implement secure keychain storage and restricted envelope validation via thin Tauri Rust bridge. |

---

## 3. Technology Stack & Operating Modes

### 3.1 Dual Operating Modes

AETHER Desktop MUST support two distinct runtime connectivity profiles:

1. **Managed Local Runtime Mode (Default Desktop Distribution)**:
   - Desktop spawns and manages the lifecycle of a bundled, version-matched `RuntimeService` sidecar process.
   - Enforces single-instance locks (`aether.lock`), monitors process liveness via periodic `/api/v1/health` probes, and triggers graceful shutdown (`SIGINT` + CAS settlement) when the application window closes.
   - Rotates local sidecar log files under `~/.aether/logs/desktop/`.
2. **External Runtime Mode (Power User & Remote Profile)**:
   - Desktop connects to an independently running `RuntimeService` daemon over loopback AF_UNIX UDS or authenticated HTTP/SSE.
   - Performs a capability and protocol handshake (`/api/v1/capabilities`) upon connection to ensure wire version compatibility.

### 3.2 Proposed Architectural Hierarchy

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        SOLIDJS + VITE FRONTEND                         │
│   @aether/ui-web ──► @aether/state ──► @aether/client (TypeScript)      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Validated Native IPC
┌───────────────────────────────────▼────────────────────────────────────┐
│                       THIN TAURI 2 RUST LAYER                          │
│   Process Lifecycle │ Secure Keychain │ Envelope Validator │ Dialogs   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Loopback UDS / HTTP SSE
┌───────────────────────────────────▼────────────────────────────────────┐
│                    AETHER RUNTIME SERVICE (PYTHON)                     │
└────────────────────────────────────────────────────────────────────────┘
```

### 3.3 Native Boundary & Security Invariants

- **Desktop IPC Boundary**: Desktop MUST communicate with native platform integrations through a versioned, validated native IPC boundary.
- **Approved Rust Responsibilities**:
  - Managing Python runtime sidecar process lifecycle and health probes.
  - Interfacing with OS Keychains to hold Ed25519 signing keys.
  - **Restricted Signing Envelope Validation**: Validating that signing requests adhere to the canonical approval schema (verifying action, digests, and expiration) before signing, preventing an untrusted WebView from acting as an arbitrary byte-signing oracle.
  - Native file system dialogs (workspace directory selection), window framing, tray icons, and system notifications.
- **Strictly Forbidden Rust Responsibilities**:
  - MUST NOT implement agent logic, turn execution, or prompt assembly.
  - MUST NOT maintain event projections, reducers, or conversation histories.
  - MUST NOT parse AETHER execution/domain contracts (except the narrowly scoped, versioned approval-signing envelope required by the native security boundary) or execute business rules.

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
   - Search bar for full-text query across local conversation indexes.
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

When the agent attempts a governed effect:

1. A modal dialog interrupts the stream with a clear description of the requested effect.
2. Displays the exact normalized diff or command line arguments and challenge digest.
3. Provides an "Approve & Apply" button that cryptographically signs the challenge with the local Ed25519 key via the native security bridge.
4. Provides a "Reject" button allowing the user to provide corrective feedback directly to the agent.

---

## 6. Accessibility Requirements

- **Standard Compliance**: Target WCAG 2.2 Level AA compliance.
- **Full Keyboard Navigation**: Complete navigation of conversations, messages, diffs, and approval modals via keyboard with visible focus indicators.
- **Screen Reader Support**: Semantic HTML landmark roles (`nav`, `main`, `region`), ARIA live regions for streaming token announcements, and accessible names on all icon buttons.
- **Visual Ergonomics**: Support high-contrast dark/light themes; never convey critical status by color alone; honor OS `prefers-reduced-motion`.

---

## 7. Provisional Performance & Packaging Budgets

Performance budgets are partitioned between the native application shell and the complete managed distribution:

| Metric Dimension | Provisional Engineering Target | Scope / Context |
|---|---|---|
| **Cold Startup Latency (P95)** | $<1.2\text{ s}$ (Application Shell Ready) | Time from icon click to interactive UI on reference hardware. |
| **Idle Memory (Application Shell)** | $<60\text{ MB}$ RAM | Combined Tauri native process + WebView memory. |
| **Idle Memory (Managed Distribution)**| $<180\text{ MB}$ RAM | Total memory including bundled Python runtime sidecar. |
| **Streaming Frame Rate** | Consistent 60 fps | Scrolling and rendering during high-speed token arrival. |
| **Installer Size (Shell Only)** | $<25\text{ MB}$ download | Standalone client package connecting to external runtime. |
| **Installer Size (Managed Bundle)** | $<150\text{ MB}$ download | Complete package including embedded Python runtime and wheels. |

---

## 8. Security & Sandboxing Architecture

- **WebView Sandboxing**: WebViews MUST operate with strict CSP (`default-src 'self'`). Inline script execution is disabled.
- **Sanitized Markdown Rendering**: Strip arbitrary HTML tags (`<script>`, `<iframe>`, remote `<img>`) to prevent XSS and pixel-tracking leaks.
- **External Link Mediation**: All external hyperlinks MUST open in the default operating system browser, never inside the application WebView.
- **Host & Origin Validation**: Loopback HTTP endpoints MUST enforce `Host` header allowlisting (`127.0.0.1`, `localhost`) to prevent DNS-rebinding attacks.
- **Key Isolation**: Ed25519 private keys MUST be marked non-exportable in OS Keychains where supported.

---

## 9. Non-Goals & Out-of-Scope Boundaries

- **NON-GOAL 1**: Embedding a full terminal emulator or xterm.js instance inside Desktop.
- **NON-GOAL 2**: Providing an integrated software development environment (IDE) with language servers and debuggers.
- **NON-GOAL 3**: Supporting multi-tenant cloud collaboration features within the local-first desktop shell.

---

## 10. Candidate Future Documents & Ownership References

- **Candidate Architecture Owner**: `docs/architecture/frontend/desktop-tauri-boundary.md`
- **Candidate Reference Owner**: `docs/reference/frontend/tauri-ipc-contract.md`
- **Candidate Decisions Owner**: `docs/decisions/frontend/adr-candidate-tauri2-rust-boundary.md`
- **Candidate Execution Owner**: `docs/execution/frontend/desktop-backlog.md`
