# Lane FE-1 · Wave 1 — extract `@vanguard/client-core`

**Write scope:** `vanguard/clients/client-core/**` (create). Re-export from `vanguard/clients/cli` so FE-2 stays green.  
**Do not touch:** Ink/TUI chrome · `vanguard-gui/**` · `vanguard/packages/**` · pack JSON  
**DoD default:** `cd vanguard/clients/client-core && npm run typecheck && npm test`  
**Also:** `cd vanguard/clients/cli && npm run typecheck && npm test` after re-exports.

This package **is** the GUI SDK. No React DOM, no Ink, no Tauri, no Monaco.

---

## FE-1-1 — Types, parse, Result

Move `contract/types.ts`, `contract/parse.ts` (daemon frames included). Package name `@vanguard/client-core`.

- [ ] CLI imports via `@vanguard/client-core` or `cli` re-export path
- [ ] Parse tests move with the code

**DoD:** core typecheck + tests; no `vanguard/packages` imports.

---

## FE-1-2 — Signer + RuntimeClient port

Move `OperatorSigner`, RFC-8785 `canonicalize`, key dir `~/.vanguard/keys` 0600, `RuntimeClient` interface.

**DoD:** JCS golden vector test in core.

---

## FE-1-3 — Reducers (view-models, zero UI)

Move `reduceRunView`, approval dispatch helpers, correction mapping. These are **pure functions** GUI will bind later (`envelopes → RunView`). Optional stub: `envelopes → TraceGraphNodes` (VG-04 kinds only; no xyflow).

**DoD:** reducer unit tests in core.

---

## FE-1-4 — Adapters

Move `LiveRuntimeClient`, `ReplayRuntimeClient`, `ScenarioRuntimeClient`, transports. CLI and GUI both import these.

**DoD:** CLI existing suite 100% green without rewriting tests except import paths if required.
