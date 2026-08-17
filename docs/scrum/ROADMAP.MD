# Vanguard Roadmap (Navigator)

Status: `NAVIGATOR`  
Last updated: 2026-08-17  
Authority: `docs/main_v4/` is normative for product and wire.

---

## 1. Active Boards

- **Frontend Active Board (Lanes FE-1, FE-2, FE-3):** [`docs/scrum/roadmap_frontend.md`](roadmap_frontend.md)
- **Backend Active Board (Sprints 07–10):** [`docs/scrum/roadmap_backend.md`](roadmap_backend.md)

---

## 2. Binding Frontend Architecture Law

- **Start here:** [`development_guides/frontend_implementer_playbook.md`](development_guides/frontend_implementer_playbook.md)
- [`development_guides/frontend_senior_review_and_two_lanes.md`](development_guides/frontend_senior_review_and_two_lanes.md) (Locked D1–D6)
- [`development_guides/cli_tui_architecture.md`](development_guides/cli_tui_architecture.md) (Hexagonal client, `@vanguard/client-core`)
- [`development_guides/tui_product_surface.md`](development_guides/tui_product_surface.md) (Claude-class Ink chrome)
- [`development_guides/gui_ide_slots.md`](development_guides/gui_ide_slots.md) (Slot-based standalone GUI)
- [`sprints_front/README.md`](sprints_front/README.md) (kits) · Wave 2 prompts: [`sprints_front/wave2_implementer_prompts.md`](sprints_front/wave2_implementer_prompts.md)

---

## 3. High-Level Strategy

- **Phase 1:** Ink TUI CLI (`vg` under `vanguard/clients/cli/**`) + core logic extracted into `@vanguard/client-core`.
- **Phase 2:** Standalone GUI IDE application (`vanguard-gui/**` / `apps/desktop/`).
- **Voided:** VS Code extension (`vanguard-ide/**`, FE-B1–B8) and Code-OSS fork.
