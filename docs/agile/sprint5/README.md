# Sprint 5 Developer Packet Index — The Judge & Context Substrate

**Authority:** [ADR-0058](file:///home/rocha/Coding/Aether-D-System/docs/v4/09_vanguard_decision_register_v040.md#L177), [ADR-0059](file:///home/rocha/Coding/Aether-D-System/docs/v4/09_vanguard_decision_register_v040.md#L178), [ADR-0060](file:///home/rocha/Coding/Aether-D-System/docs/v4/09_vanguard_decision_register_v040.md#L179), [ADR-0061](file:///home/rocha/Coding/Aether-D-System/docs/v4/09_vanguard_decision_register_v040.md#L180)  
**Branch:** `sprint5-6/integration`  
**Status:** ACTIVE IMPLEMENTATION

Sprint 5 builds the **two missing pillars of trust**: the **Isolated Exterior Evaluator Daemon** (so the judge cannot be captured or tampered with) and the **Prefix-Stable Context Compiler** (for KV-cache reuse and cognitive grounding).

Give each developer their specific wave prompt (`docs/development/dev_prompts/lane-a.md` … `lane-d.md`) and assigned packet below.

---

## Developer Allocation Matrix

| Developer / Role | Lane | Wave Prompt | Packet | Cx | Target Contract |
|---|---|---|---|---|---|
| **Lead Architect / Tech Lead** | Lane SA | [`../development/dev_prompts/lane-a.md`](../development/dev_prompts/lane-a.md) | [`sa-packet.md`](sa-packet.md) | 4 GATE | `REQ-CTX-001` |
| **Senior Developer B** | Lane SB | [`../development/dev_prompts/lane-b.md`](../development/dev_prompts/lane-b.md) | [`sb-packet.md`](sb-packet.md) | 4 GATE | `REQ-EVAL-001` |
| **Senior Developer C** | Lane DC | [`../development/dev_prompts/lane-c.md`](../development/dev_prompts/lane-c.md) | [`dc-packet.md`](dc-packet.md) | 3 FAST | `REQ-PORT-006`, `REQ-SLICE-001` |
| **Mid Developer D** | Lane DD | [`../development/dev_prompts/lane-d.md`](../development/dev_prompts/lane-d.md) | [`dd-packet.md`](dd-packet.md) | 2 FAST | `REQ-CLI-001` |

---

## Required Reading for Sprint 5

1. [Decision Register §11 (`ADR-0058..0061`)](file:///home/rocha/Coding/Aether-D-System/docs/v4/09_vanguard_decision_register_v040.md)
2. [Engineering Handbook §1 Mental Models M1–M11](file:///home/rocha/Coding/Aether-D-System/docs/v4/01_vanguard_engineering_handbook_v040.md)
3. [Active MVP Contract Phase 2 Rows (`REQ-CTX-001`, `REQ-EVAL-001`)](file:///home/rocha/Coding/Aether-D-System/docs/sprint0/active-mvp-contract.json)
4. [Master Phase Review Chapter 2](file:///home/rocha/Coding/Aether-D-System/docs/review/todo/phases_review.md)
5. Assigned developer packet (`sa-packet.md`, `sb-packet.md`, `dc-packet.md`, `dd-packet.md`).
