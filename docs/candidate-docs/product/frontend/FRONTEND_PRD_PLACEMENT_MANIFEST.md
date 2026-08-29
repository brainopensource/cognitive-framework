---
id: frontend-prd-placement-manifest
class: meta
authority: governance
canonical_for:
  - frontend-prd-manifest
  - frontend-documentation-placement-map
status: proposed
owner: product-architecture
version: "1.0.0"
last_verified: 2026-08-29
future_canonical_owner: docs/product/frontend/FRONTEND_PRD_PLACEMENT_MANIFEST.md
subordinate_to:
  - ../../SPEC.md
---

# AETHER Frontend PRD Placement & Knowledge Ownership Manifest

## 1. Overview & Documentation Authority Rules

This manifest registers the authoritative set of Product Requirements Documents (PRDs) for the **AETHER — ELECTROWEAK** frontend ecosystem. 

All documents in this directory represent **Product Requirements (WHAT and WHY)**. They strictly adhere to the invariant:

> **One durable fact → one canonical owner → all other documents reference it.**

PRDs establish user needs, functional requirements, non-functional performance budgets, and product boundaries. They intentionally **do not** own detailed low-level software architecture, exact API schemas, architectural decision records (ADRs), or sprint execution tasks.

---

## 2. PRD Placement & Canonical Ownership Map

| Document Title | Canonical ID | Staging Path (Current) | Future Canonical Owner | Truth Plane | Future Architecture Owner | Future Reference Owner | Future ADR Owner | Future Execution Owner |
|---|---|---|---|---|---|---|---|---|
| **Frontend Platform PRD** | `product.frontend.platform` | `candidate-docs/product/frontend/PRD_FRONTEND_PLATFORM.md` | `docs/product/frontend/PRD_FRONTEND_PLATFORM.md` | Product Requirements | `docs/architecture/frontend/platform-architecture.md` | `docs/reference/frontend/client-sdk.md` | `docs/decisions/frontend/0107-frontend-stack-ratification.md` | `docs/execution/frontend/roadmap.md` |
| **AETHER CLI PRD** | `product.frontend.cli` | `candidate-docs/product/frontend/PRD_AETHER_CLI.md` | `docs/product/frontend/PRD_AETHER_CLI.md` | Product Requirements | `docs/architecture/frontend/cli-architecture.md` | `docs/reference/frontend/cli-commands.md` | `docs/decisions/frontend/0108-cli-headless-posix-standard.md` | `docs/execution/frontend/cli-backlog.md` |
| **AETHER TUI PRD** | `product.frontend.tui` | `candidate-docs/product/frontend/PRD_AETHER_TUI.md` | `docs/product/frontend/PRD_AETHER_TUI.md` | Product Requirements | `docs/architecture/frontend/tui-opentui-architecture.md` | `docs/reference/frontend/tui-keybindings.md` | `docs/decisions/frontend/0109-opentui-solid-selection.md` | `docs/execution/frontend/tui-backlog.md` |
| **AETHER Desktop PRD** | `product.frontend.desktop` | `candidate-docs/product/frontend/PRD_AETHER_DESKTOP.md` | `docs/product/frontend/PRD_AETHER_DESKTOP.md` | Product Requirements | `docs/architecture/frontend/desktop-tauri-boundary.md` | `docs/reference/frontend/tauri-ipc-contract.md` | `docs/decisions/frontend/0110-tauri2-rust-boundary.md` | `docs/execution/frontend/desktop-backlog.md` |
| **AETHER Lab PRD** | `product.frontend.lab` | `candidate-docs/product/frontend/PRD_AETHER_LAB.md` | `docs/product/frontend/PRD_AETHER_LAB.md` | Product Requirements | `docs/architecture/frontend/lab-inspection-architecture.md` | `docs/reference/frontend/lab-workbenches.md` | `docs/decisions/frontend/0111-lab-minimal-companion-scope.md` | `docs/execution/frontend/lab-backlog.md` |

---

## 3. Deferred Documentation Register

The following documents represent necessary technical architecture, formal interface references, architectural decision records (ADRs), and sprint execution plans that MUST be authored in subsequent governance phases according to the knowledge ownership model:

```text
Deferred Documentation Taxonomy:
├── docs/architecture/frontend/
│   ├── platform-architecture.md            # Monorepo topology, package boundaries & build pipelines
│   ├── state-and-projection-algebra.md     # Mathematical specification of event folds, snapshots & selectors
│   ├── desktop-tauri-boundary.md           # Formal IPC interface, sidecar lifecycle & security sandbox
│   └── tui-opentui-architecture.md         # OpenTUI reactive cell diffing & ANSI terminal drivers
│
├── docs/reference/frontend/
│   ├── client-sdk.md                       # Complete API reference for @aether/client
│   ├── runtime-wire-protocol.md            # vg.4 UDS and HTTP/SSE 45-route message specification
│   ├── design-tokens.md                    # Complete token dictionary, elevation levels & theme schemas
│   └── tauri-ipc-contract.md               # JSON-RPC IPC message definitions for Rust/WebView boundary
│
├── docs/decisions/frontend/
│   ├── 0107-frontend-stack-ratification.md # Formal ADR locking SolidJS, OpenTUI, Bun, and Tauri 2
│   ├── 0108-cli-headless-posix-standard.md # ADR establishing CLI exit code and NDJSON contracts
│   ├── 0109-opentui-solid-selection.md     # ADR approving replacement of React/Ink with OpenTUI+SolidJS
│   ├── 0110-tauri2-rust-boundary.md        # ADR defining the strict non-domain boundary for Rust code
│   └── 0111-lab-minimal-companion-scope.md # ADR bounding Lab scope to zero unique state infrastructure
│
└── docs/execution/frontend/
    ├── frontend-migration-roadmap.md       # Phased migration roadmap (F0 Contract Freeze -> F12 Release)
    ├── sprint_active_frontend.md           # Active frontend delivery board (Lane A / Lane B tasks)
    └── verification-matrix.md              # Test matrix & automated cross-client acceptance gates
```

---

## 4. Governance & Cutover Policy

1. **Staging Isolation**: Documents in `candidate-docs/product/frontend/` remain in proposal status (`status: proposed`) until formally ratified by repository leadership.
2. **Zero Sprawl Rule**: No additional temporary design documents or scratchpads may be created outside this manifest.
3. **Cutover Execution**: When the global repository documentation reconstruction occurs, these files will be copied directly to their `future_canonical_owner` paths under `docs/product/frontend/` without alteration of their canonical IDs or semantic substance.
