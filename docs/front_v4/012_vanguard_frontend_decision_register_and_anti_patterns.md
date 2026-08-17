# Vanguard Frontend Decision Register & Anti-Patterns

**Document ID:** `VG-FE-012`  
**Version:** `0.4.1-beta`  
**Status:** `Normative / Authoritative`  
**Owner:** `Tech Lead & Principal Architect`  
**Related Specs:** [`09_vanguard_decision_register_v040.md`](file:///home/rocha/Coding/Aether-D-System/docs/main_v4/09_vanguard_decision_register_v040.md), [`10_vanguard_deferred_and_rejected_register_v040.md`](file:///home/rocha/Coding/Aether-D-System/docs/main_v4/10_vanguard_deferred_and_rejected_register_v040.md)

---

## 1. Frontend Architectural Decision Records (ADRs)

| ADR ID | Decision | Context & Rationale | Reversal Condition |
| :--- | :--- | :--- | :--- |
| **`ADR-FE-001`** | **React + Ink for Terminal UI** | Ink provides declarative component composition, reactive state, and robust terminal flexbox layout without low-level ANSI cursor math. | Terminal rendering latency exceeds 16ms under standard load. |
| **`ADR-FE-002`** | **Decoupled Daemon/Client via UDS / NDJSON** | Keeps the UI crash-isolated from the long-running agent kernel; allows CLI and IDE to be peer clients over the same socket. | A benchmark mathematically proves in-process memory sharing is necessary for UI responsiveness. |
| **`ADR-FE-003`** | **Code-OSS / VSCodium Base for Vanguard IDE** | Code-OSS provides 100% standard VS Code extension and editor ecosystem without proprietary Microsoft telemetry or licensing locks. | Upstream Code-OSS introduces architectural changes that prevent secondary webview panel embedding. |
| **`ADR-FE-004`** | **Ed25519 Asymmetric Key Signing for Approvals** | Ensures the operator approval authority is physically held outside the Python runtime process memory space (`ADR-0062`). | A cryptographically superior hardware token standard supersedes Ed25519 with equivalent ergonomics. |
| **`ADR-FE-005`** | **Zero-Prerequisite Shell Installer (`curl \| sh`)** | Enables instant adoption without requiring users to manually manage Node, Python, or virtual environment versions. | A universal cross-platform package manager gains 100% developer market share. |

---

## 2. Forbidden Anti-Patterns (Strictly Rejected)

The following design patterns are strictly forbidden in the Vanguard frontend codebase:

```
❌ REJECTED ANTI-PATTERNS
├── 1. In-Process Kernel Import: UI code importing Python modules or direct C-bindings.
├── 2. Unbounded Memory Buffer: Storing entire infinite stream logs in React component state.
├── 3. Unsigned Capability Execution: Auto-granting high-risk shell commands without Ed25519 signature.
├── 4. Raw ANSI Cursor Escapes: Manually printing '\033[2K\r' instead of using Ink components.
└── 5. Cliché Visual Gimmicks: Purple-on-dark neon glow, pulsating biscuit badges, unaligned typefaces.
```

---

## 3. Pull Request Review & Merge Gate Checklist

Before approving any Frontend PR, the reviewer must verify:

- [ ] **Typecheck:** `npm --workspace @vanguard/cli run typecheck` passes with zero errors.
- [ ] **Unit Tests:** `npm --workspace @vanguard/cli test` passes with 100% green assertions.
- [ ] **Vector Conformance:** All schema changes match [`04_vanguard_core_contracts_and_wire_schema_v040.md`](file:///home/rocha/Coding/Aether-D-System/docs/main_v4/04_vanguard_core_contracts_and_wire_schema_v040.md) and pass Python vector tests.
- [ ] **Process Boundary:** No direct imports crossing the client/daemon boundary.
- [ ] **Operator Authority:** Approval resolution logic preserves canonical RFC 8785 byte signing.
