# Sprint 6 Developer Packet Index — Beta Product Assembly & Dogfood Milestone

**Authority:** [ADR-0057](file:///home/rocha/Coding/Aether-D-System/docs/v4/09_vanguard_decision_register_v040.md#L165), [ADR-0058](file:///home/rocha/Coding/Aether-D-System/docs/v4/09_vanguard_decision_register_v040.md#L177), [ADR-0059](file:///home/rocha/Coding/Aether-D-System/docs/v4/09_vanguard_decision_register_v040.md#L178), [ADR-0060](file:///home/rocha/Coding/Aether-D-System/docs/v4/09_vanguard_decision_register_v040.md#L179), [ADR-0061](file:///home/rocha/Coding/Aether-D-System/docs/v4/09_vanguard_decision_register_v040.md#L180)  
**Branch:** `sprint5-6/integration`  
**Status:** BLOCKED — PENDING SPRINT 5 MERGE TO MAIN

Sprint 6 delivers the **Beta MVP Product Milestone**: one composable framework running the frozen [`vg-code-default`](file:///home/rocha/Coding/Aether-D-System/vanguard/packages/agency/manifests/vg-code-default/) coding harness, backed by real OpenRouter inference, descriptor-bound human approvals, and an interactive Ink TUI.

Implementation starts strictly after Sprint 5 (`REQ-CTX-001` and `REQ-EVAL-001`) lands on disk.

---

## Developer Allocation Matrix

| Developer / Role | Lane | Wave Prompt | Packet | Cx | Target Contract |
|---|---|---|---|---|---|
| **Lead Architect / Tech Lead** | Lane SA | [`../development/dev_prompts_blocked/lane-a.md`](../development/dev_prompts_blocked/lane-a.md) | [`sa-packet.md`](sa-packet.md) | 5 GATE | `REQ-DOG-001` |
| **Senior Developer B** | Lane SB | [`../development/dev_prompts_blocked/lane-b.md`](../development/dev_prompts_blocked/lane-b.md) | [`sb-packet.md`](sb-packet.md) | 4 GATE | `REQ-APP-001` |
| **Senior Developer C** | Lane DC | [`../development/dev_prompts_blocked/lane-c.md`](../development/dev_prompts_blocked/lane-c.md) | [`dc-packet.md`](dc-packet.md) | 3 FAST | `REQ-BENCH-001` |
| **Mid Developer D** | Lane DD | [`../development/dev_prompts_blocked/lane-d.md`](../development/dev_prompts_blocked/lane-d.md) | [`dd-packet.md`](dd-packet.md) | 3 FAST | `REQ-CLI-002` |

---

## Required Reading for Sprint 6

1. [GTS-13C Ch. 10 MVP Questions Gate Q1+Q2](file:///home/rocha/Coding/Aether-D-System/docs/v4/13_C_gts_mvp_program_and_engineering_plan.md)
2. [CLI / TUI Architecture Specification](file:///home/rocha/Coding/Aether-D-System/docs/development/cli_tui_architecture.md)
3. [Decision Register ADR-0057 (Beta Scope)](file:///home/rocha/Coding/Aether-D-System/docs/v4/09_vanguard_decision_register_v040.md#L165)
4. [Master Phase Review Chapter 2](file:///home/rocha/Coding/Aether-D-System/docs/review/todo/phases_review.md)
5. Assigned developer packet (`sa-packet.md`, `sb-packet.md`, `dc-packet.md`, `dd-packet.md`).
