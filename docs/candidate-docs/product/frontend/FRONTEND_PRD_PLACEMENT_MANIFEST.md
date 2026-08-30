---
id: frontend-prd-placement-manifest
class: meta
authority: proposal
canonical_for:
  - frontend-prd-manifest
  - frontend-documentation-placement-map
status: proposed
owner: product-architecture
version: "0.1.0"
last_verified: 2026-08-29
future_canonical_owner: docs/product/frontend/FRONTEND_PRD_PLACEMENT_MANIFEST.md
subordinate_to:
  - ../../../SPEC.md
---

# AETHER Frontend PRD Placement & Knowledge Ownership Manifest

## 1. Overview & Documentation Authority Rules

This manifest registers the set of proposed Product Requirements Documents (PRDs) for the **AETHER — ELECTROWEAK** frontend ecosystem.

All documents in this directory represent **Product Requirements (WHAT and WHY)**. They strictly adhere to the invariant:

> **One durable fact → one canonical owner → all other documents reference it.**

PRDs establish user needs, functional requirements, provisional performance targets, and product boundaries. They intentionally **do not** own detailed low-level software architecture, exact API schemas, architectural decision records (ADRs), or sprint execution tasks.

---

## 2. Proposed PRD Placement & Canonical Ownership Map

| Document Title | Canonical ID | Staging Path (Current) | Future Canonical Owner | Truth Plane | Candidate Architecture Owner | Candidate Reference Owner | Candidate ADR Owner | Candidate Execution Owner |
|---|---|---|---|---|---|---|---|---|
| **Frontend Platform PRD** | `product.frontend.platform` | `docs/candidate-docs/product/frontend/PRD_FRONTEND_PLATFORM.md` | `docs/product/frontend/PRD_FRONTEND_PLATFORM.md` | Product Requirements | `docs/architecture/frontend/platform-architecture.md` | `docs/reference/frontend/client-sdk.md` | `docs/decisions/frontend/0107-frontend-stack-ratification.md` | `docs/execution/frontend/roadmap.md` |
| **AETHER CLI PRD** | `product.frontend.cli` | `docs/candidate-docs/product/frontend/PRD_AETHER_CLI.md` | `docs/product/frontend/PRD_AETHER_CLI.md` | Product Requirements | `docs/architecture/frontend/cli-architecture.md` | `docs/reference/frontend/cli-commands.md` | `docs/decisions/frontend/0108-cli-headless-posix-standard.md` | `docs/execution/frontend/cli-backlog.md` |
| **AETHER TUI PRD** | `product.frontend.tui` | `docs/candidate-docs/product/frontend/PRD_AETHER_TUI.md` | `docs/product/frontend/PRD_AETHER_TUI.md` | Product Requirements | `docs/architecture/frontend/tui-opentui-architecture.md` | `docs/reference/frontend/tui-keybindings.md` | `docs/decisions/frontend/0109-opentui-solid-selection.md` | `docs/execution/frontend/tui-backlog.md` |
| **AETHER Desktop PRD** | `product.frontend.desktop` | `docs/candidate-docs/product/frontend/PRD_AETHER_DESKTOP.md` | `docs/product/frontend/PRD_AETHER_DESKTOP.md` | Product Requirements | `docs/architecture/frontend/desktop-tauri-boundary.md` | `docs/reference/frontend/tauri-ipc-contract.md` | `docs/decisions/frontend/0110-tauri2-rust-boundary.md` | `docs/execution/frontend/desktop-backlog.md` |
| **AETHER Lab PRD** | `product.frontend.lab` | `docs/candidate-docs/product/frontend/PRD_AETHER_LAB.md` | `docs/product/frontend/PRD_AETHER_LAB.md` | Product Requirements | `docs/architecture/frontend/lab-inspection-architecture.md` | `docs/reference/frontend/lab-workbenches.md` | `docs/decisions/frontend/0111-lab-minimal-companion-scope.md` | `docs/execution/frontend/lab-backlog.md` |

---

## 3. Candidate Future Documents Register

The following topics represent candidate technical architecture, formal interface references, architectural decision records (ADRs), and sprint execution plans that are expected to be authored in subsequent governance phases according to the repository knowledge ownership model:

```text
Candidate Future Documentation Topics:
├── docs/architecture/frontend/
│   ├── platform-architecture.md            # Monorepo topology, package boundaries & build pipelines
│   ├── state-and-projection-algebra.md     # Specification of event folds, snapshots & selectors
│   ├── desktop-tauri-boundary.md           # IPC interface, sidecar lifecycle & security sandbox
│   └── tui-opentui-architecture.md         # OpenTUI reactive cell diffing & ANSI terminal drivers
│
├── docs/reference/frontend/
│   ├── client-sdk.md                       # API reference for @aether/client
│   ├── runtime-wire-protocol.md            # UDS and HTTP/SSE message specification
│   ├── design-tokens.md                    # Design token dictionary, elevation levels & schemas
│   └── tauri-ipc-contract.md               # IPC message definitions for Rust/WebView boundary
│
├── docs/decisions/frontend/
│   ├── 0107-frontend-stack-ratification.md # ADR locking SolidJS, OpenTUI, Bun, and Tauri 2
│   ├── 0108-cli-headless-posix-standard.md # ADR establishing CLI exit code and NDJSON contracts
│   ├── 0109-opentui-solid-selection.md     # ADR approving replacement of React/Ink with OpenTUI+SolidJS
│   ├── 0110-tauri2-rust-boundary.md        # ADR defining the non-domain boundary for Rust code
│   └── 0111-lab-minimal-companion-scope.md # ADR bounding Lab scope to zero unique state infrastructure
│
└── docs/execution/frontend/
    ├── frontend-migration-roadmap.md       # Phased migration roadmap
    ├── sprint_active_frontend.md           # Active frontend delivery board
    └── verification-matrix.md              # Test matrix & automated acceptance gates
```

---

## 4. Governance & Cutover Policy

1. **Staging Status**: Documents in `docs/candidate-docs/product/frontend/` remain in proposal status (`status: proposed`) as TARGET planning artifacts.
2. **Promotion Rule**: These documents are proposed staging artifacts. Their future canonical promotion is subject to documentation reconstruction, ownership validation, TARGET reconciliation, independent review, and governance ratification.
3. **Anti-Sprawl Enforcement**: No temporary scratch files or unauthorized architecture specifications may be created outside the canonical documentation structure.
