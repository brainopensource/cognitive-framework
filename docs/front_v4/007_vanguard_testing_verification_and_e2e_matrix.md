# Vanguard Frontend Testing, Verification & E2E Matrix

**Document ID:** `VG-FE-007`  
**Version:** `0.4.1-beta`  
**Status:** `Normative / Authoritative`  
**Owner:** `QA & Verification Lead`  
**Target:** `vanguard/clients/cli/test/`, `test/contracts/`

---

## 1. The Verification Pyramid for the Interaction Plane

To ensure rock-solid stability and zero regression, the frontend is tested across four rigorous layers:

```
                  ┌──────────────────────────────┐
                  │   Layer 4: Real E2E Harness  │ (Live Daemon + Docker Sandbox)
                  ├──────────────────────────────┤
                  │   Layer 3: Headless Mock E2E │ (Mock Daemon / Replay Fixtures)
                  ├──────────────────────────────┤
                  │   Layer 2: Contract Vectors  │ (Cross-Language Schema Parity)
                  ├──────────────────────────────┤
                  │   Layer 1: Unit & TUI Tests  │ (node --test, ink-testing-library)
                  └──────────────────────────────┘
```

---

## 2. Test Execution Commands

```bash
# 1. Typecheck and TypeScript compile
npm --workspace @vanguard/cli run typecheck

# 2. Run TypeScript Unit & Component Tests
npm --workspace @vanguard/cli test

# 3. Run Cross-Language Contract Conformance Tests
python3 -m unittest test.contracts.t1_wire_contracts -v

# 4. Run Headless E2E Simulation
npm --workspace @vanguard/cli run vg -- --headless --scenario test/fixtures/fix_typo.json
```

---

## 3. Layer 1: Unit & Component Testing (`ink-testing-library`)

Unit tests verify component layout, ANSI styling, and keyboard navigation without opening a real terminal:

```typescript
import { test, describe } from "node:test";
import * as assert from "node:assert";
import React from "react";
import { render } from "ink-testing-library";
import { ApprovalModal } from "../src/ui/ApprovalModal";

describe("ApprovalModal Component", () => {
  test("renders high risk warning and action descriptor", () => {
    const descriptor = {
      approval_id: "appr_123",
      action_descriptor: { command: "rm -rf test_dir" },
      nonce: "12345"
    };

    const { lastFrame } = render(
      React.createElement(ApprovalModal, {
        isOpen: true,
        descriptor,
        onAccept: () => {},
        onDeny: () => {}
      })
    );

    assert.ok(lastFrame()?.includes("OPERATOR APPROVAL REQUIRED"));
    assert.ok(lastFrame()?.includes("rm -rf test_dir"));
  });
});
```

---

## 4. Layer 2: Cross-Language Wire Conformance (`SC-7` / `ADR-0014`)

Every TypeScript validator must agree 100% with the Python backend on both valid and invalid vector fixtures:

| Vector Family | Verification Goal | Target |
| :--- | :--- | :--- |
| `valid_primitives` | Exact RFC 8785 byte agreement and SHA-256 digest match | `test/contracts/t1_dev1_primitives.py` |
| `wire_contracts` | Strict validation of all 11 `LedgerEvent` kinds | `test/contracts/t1_wire_contracts.py` |
| `unknown_fields` | Enforce rejection of unknown fields in authored config | `test/contracts/t1_config_schemas.py` |

---

## 5. Layer 3: Headless E2E Scenario Matrix

Automated scenarios run in CI using synthetic task files to guarantee agent flows complete deterministically:

| Scenario ID | Task Description | Expected Tool Trace | Expected Verdict |
| :--- | :--- | :--- | :--- |
| `SCEN-01` | Read file and fix one-line syntax error | `fs.read` $\to$ `fs.write` $\to$ `proc.exec` (test) | `success` (Turn 3) |
| `SCEN-02` | Refuse destructive command when operator denies | `proc.exec` (`rm -rf`) $\to$ `approval.requested` $\to$ `deny` | `cancelled` (Turn 2) |
| `SCEN-03` | Budget token limit enforcement | Infinite loop prompt $\to$ `turn.completed` $\times 10$ | `budget_exhausted` |
| `SCEN-04` | Daemon crash and auto-reconnection | Kill daemon mid-stream $\to$ Client reconnects $\to$ Stream resumes | `recovered` |
