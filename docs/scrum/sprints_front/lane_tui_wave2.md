# Lane FE-2 · Wave 2 — Claude-class Ink chrome (FE-2-8)

**Write scope:** `vanguard/clients/cli/**` (presentation: `src/tui/**`, `src/composition/**`, `src/headless/**`, tests, `install.sh`).  
**Do not touch:** `vanguard/clients/client-core/**` internals (import paths OK) · `vanguard-gui/**` · `vanguard/packages/**`  
**Depends:** Wave 1 FE-2-1…FE-2-7 `[DONE]` (40/40 CLI tests). This sprint is **FE-2-8 only** plus tests. FE-2-9 resume is Wave 3.  
**DoD default:** `cd vanguard/clients/cli && npm run typecheck && npm test`  
**Also:** `vg --help` still lists flags; `ui.test.ts` passes; `NO_COLOR=1` still prints `source: mock` as text.

Binding layout: `docs/scrum/development_guides/tui_product_surface.md`.

Copy-paste implementer prompt: [`wave2_implementer_prompts.md`](wave2_implementer_prompts.md) §FE-2.

---

## FE-2-8 — SOTA chrome

Replace the single stacked `RunTui` column with the binding regions:

```text
┌─ vg · source · seq · budget ─────────────────────────┐
│ transcript (windowed)      │ detail / approval / why │
├────────────────────────────┴─────────────────────────┤
│ prompt bar  (brief)     hints: ctrl+c cancel · ?     │
└──────────────────────────────────────────────────────┘
```

| Atom | Rule |
|---|---|
| Status | `sourceLabel`, last `payload.kind`, tokens/cost from `BudgetCommitted`, last `seq` if known. Replay/demo never look live. |
| Transcript | Window a slice of `RunViewModel` (use `windowTranscript` from core if exported; else local clamp). Do not mount one Ink node per historical thought. |
| Detail | Selected tool/effect **or** approval modal **or** why stub (`explainArtifact` → surface `not_available`, no fiction). |
| Prompt | Type + Enter feeds `StartRun.brief` **only when no approval modal**. Empty Enter = local `invalid_request` (do not call daemon). |
| Focus | Explicit mode: `prompt` \| `approval` \| `correct` \| `help`. `y`/`n`/`c` **must not fire while typing a brief**. |
| Keys | `ctrl+c` / Esc (when not in prompt text) → `requestCancel`. `?` help (text, not color-only). `q` quits. |
| Approval | Keep P0-4 `submitInteractiveApproval` (OperatorSigner, no empty-digest success). Optimistic UI = `requested` until `ApprovalResolved`. |

**DoD:** `ui.test.ts` covers focus-mode key routing, window clamp, empty-Enter, `ctrl+c` maps to cancel (fake client). Existing 40 tests stay green.

**Out of this sprint:** FE-2-9 resume chrome, new verbs, `/mcp`, parallel sessions.
