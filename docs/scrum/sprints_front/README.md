# Frontend sprint delta kits

Status: `BINDING for FE lanes` under `frontend_senior_review_and_two_lanes.md`  
Numbering: **FE-1-n** (Core), **FE-2-n** (TUI), **FE-3-n** (GUI)

| Kit | Lane | Contents |
|---|---|---|
| `lane_core_wave1.md` | **FE-1 (Core)** | FE-1-1 … FE-1-4 (extract `@vanguard/client-core`) |
| `lane_a_wave1.md` | **FE-2 (TUI Wave 1)** | FE-2-1 … FE-2-2 (core re-export, TUI tree) |
| `lane_a_wave2.md` | **FE-2 (TUI Wave 2)** | FE-2-3 … FE-2-9 (demo, approvals, headless, SOTA chrome, resume) |
| `lane_gui_wave1.md` | **FE-3 (GUI Wave 1)** | FE-3-1 … FE-3-6 (GUI scaffold, client-core import, replay, slot stubs) |

Also: `frontend_implementer_playbook.md` (start here), `tui_product_surface.md` (FE-2), `gui_ide_slots.md` (FE-3).

*Note: `sprints_front/sprint1`–`sprint4` and `lane_b_wave*.md` are VOID.*

---

## Lane Rules & Write Scopes

1. **FE-1 (Core):** Writes `vanguard/clients/client-core/**` (or `vanguard/clients/cli/packages/core/`). Must not touch UI chrome or daemon Python.
2. **FE-2 (TUI):** Writes `vanguard/clients/cli/**` presentation only. Imports `@vanguard/client-core`.
3. **FE-3 (GUI):** Writes `vanguard-gui/**` (or `apps/desktop/`). Imports `@vanguard/client-core`.
4. **Backend frozen:** Backend trees stay frozen. Joint notes J1–J5 are requests, not FE PRs.

---

## Default DoD Commands

```bash
# FE-1 (Client Core)
cd vanguard/clients/client-core && npm run typecheck && npm test

# FE-2 (CLI TUI)
cd vanguard/clients/cli && npm run typecheck && npm test

# FE-3 (Standalone GUI)
cd vanguard-gui && npm run typecheck && npm run dev
```

Boundary verification:

```bash
# Expect no imports of vanguard/packages in any frontend client
grep -rn "vanguard/packages" vanguard/clients/ vanguard-gui/src || true
```
