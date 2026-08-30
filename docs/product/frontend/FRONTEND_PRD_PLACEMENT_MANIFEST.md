---
id: frontend-prd-placement-manifest
class: meta
authority: proposal
canonical_for:
  - frontend-prd-manifest
  - frontend-documentation-placement-map
status: proposed
owner: product-architecture
version: "0.2.0"
last_verified: 2026-08-29
future_canonical_owner: docs/product/frontend/FRONTEND_PRD_PLACEMENT_MANIFEST.md
subordinate_to:
  - ../../SPEC.md
---

# AETHER Frontend PRD Placement & Knowledge Ownership Manifest

## 1. Overview & Documentation Authority Rules

This manifest registers the set of proposed Product Requirements Documents (PRDs) for the **AETHER — ELECTROWEAK** frontend ecosystem.

All documents in this directory represent **Product Requirements (WHAT and WHY)**. They strictly adhere to the invariant:

> **One durable fact → one canonical owner → all other documents reference it.**

PRDs establish user needs, functional requirements, provisional performance targets, and product boundaries. They intentionally **do not** own detailed low-level software architecture, exact API schemas, architectural decision records (ADRs), or sprint execution tasks.

---

## 2. Proposed PRD Placement & Canonical Ownership Map

| Document Title | Canonical ID | Staging Path (Current) | Future Canonical Owner | Truth Plane | Candidate Architecture Owner | Candidate Reference Owner | Candidate ADR Owner (Unassigned ID) | Candidate Execution Owner |
|---|---|---|---|---|---|---|---|---|
| **Frontend Platform PRD** | `product.frontend.platform` | `candidate-docs/product/frontend/PRD_FRONTEND_PLATFORM.md` | `docs/product/frontend/PRD_FRONTEND_PLATFORM.md` | Product Requirements | `docs/architecture/frontend/platform-architecture.md` | `docs/reference/frontend/client-sdk.md` | `docs/decisions/frontend/adr-candidate-frontend-stack.md` | `docs/execution/frontend/roadmap.md` |
| **AETHER CLI PRD** | `product.frontend.cli` | `candidate-docs/product/frontend/PRD_AETHER_CLI.md` | `docs/product/frontend/PRD_AETHER_CLI.md` | Product Requirements | `docs/architecture/frontend/cli-architecture.md` | `docs/reference/frontend/cli-commands.md` | `docs/decisions/frontend/adr-candidate-cli-exit-contract.md` | `docs/execution/frontend/cli-backlog.md` |
| **AETHER TUI PRD** | `product.frontend.tui` | `candidate-docs/product/frontend/PRD_AETHER_TUI.md` | `docs/product/frontend/PRD_AETHER_TUI.md` | Product Requirements | `docs/architecture/frontend/tui-opentui-architecture.md` | `docs/reference/frontend/tui-keybindings.md` | `docs/decisions/frontend/adr-candidate-opentui-solid.md` | `docs/execution/frontend/tui-backlog.md` |
| **AETHER Desktop PRD** | `product.frontend.desktop` | `candidate-docs/product/frontend/PRD_AETHER_DESKTOP.md` | `docs/product/frontend/PRD_AETHER_DESKTOP.md` | Product Requirements | `docs/architecture/frontend/desktop-tauri-boundary.md` | `docs/reference/frontend/tauri-ipc-contract.md` | `docs/decisions/frontend/adr-candidate-tauri2-rust-boundary.md` | `docs/execution/frontend/desktop-backlog.md` |
| **AETHER Lab PRD** | `product.frontend.lab` | `candidate-docs/product/frontend/PRD_AETHER_LAB.md` | `docs/product/frontend/PRD_AETHER_LAB.md` | Product Requirements | `docs/architecture/frontend/lab-inspection-architecture.md` | `docs/reference/frontend/lab-workbenches.md` | `docs/decisions/frontend/adr-candidate-lab-minimal-scope.md` | `docs/execution/frontend/lab-backlog.md` |

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
├── docs/decisions/frontend/ (Decision Status: Candidate / Unassigned ADR Numbers)
│   ├── adr-candidate-frontend-stack.md     # Candidate ADR evaluating SolidJS, OpenTUI, Bun, and Tauri 2
│   ├── adr-candidate-cli-exit-contract.md  # Candidate ADR establishing CLI exit code and NDJSON contracts
│   ├── adr-candidate-opentui-solid.md      # Candidate ADR evaluating replacement of React/Ink with OpenTUI+SolidJS
│   ├── adr-candidate-tauri2-rust-boundary.md # Candidate ADR defining the non-domain boundary for Rust code
│   └── adr-candidate-lab-minimal-scope.md  # Candidate ADR bounding Lab scope to zero unique state infrastructure
│
└── docs/execution/frontend/
    ├── frontend-migration-roadmap.md       # Phased migration roadmap
    ├── sprint_active_frontend.md           # Active frontend delivery board
    └── verification-matrix.md              # Test matrix & automated acceptance gates
```

---

## 4. Governance & Cutover Policy

1. **Staging Status**: Documents in `candidate-docs/product/frontend/` remain in proposal status (`status: proposed`) as TARGET planning artifacts.
2. **Promotion Rule**: These documents are proposed staging artifacts. Their future canonical promotion is subject to documentation reconstruction, ownership validation, TARGET reconciliation, independent review, and governance ratification.
3. **Anti-Sprawl Enforcement**: No temporary scratch files or unauthorized architecture specifications may be created outside the canonical documentation structure.
