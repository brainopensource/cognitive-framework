# Lane FE-1 · Wave 2 — core product API (selectors, graph, stream)

**Write scope:** `vanguard/clients/client-core/**` only. CLI re-export shims may be updated **import paths only**.  
**Do not touch:** Ink/TUI chrome · `vanguard-gui/**` · `vanguard/packages/**` · pack JSON  
**Depends:** Wave 1 FE-1-1…FE-1-4 `[DONE]`  
**DoD default:** `cd vanguard/clients/client-core && npm run typecheck && npm test`  
**Also:** `cd vanguard/clients/cli && npm run typecheck && npm test` must stay green (40 tests as of Wave 1 close).

This package **is** the GUI/TUI SDK. No React DOM, no Ink, no Tauri, no Monaco, no xyflow.

Copy-paste implementer prompt: [`wave2_implementer_prompts.md`](wave2_implementer_prompts.md) §FE-1.

---

## FE-1-5 — Public API freeze & hygiene

- Barrel `@vanguard/client-core` is the supported import. Keep existing `exports` subpaths so CLI shims do not break.
- Move `import` declarations to the top of `src/application/commands.ts` (today `jsonLine` precedes `import type`).
- Rename conceptually: `CliOptions` remains exported (do not break FE-2) but add `HeadlessRunOptions` as an alias documented as the headless DTO. Do not add Ink flags to the live wire.
- `jsonLine` stays a tiny encoder; no CSI, no pretty-print.

**DoD:** core tests include an export-surface test (barrel exports `RuntimeClient`, `reduceRunView`, `OperatorSigner`, `ReplayRuntimeClient`, `toTraceGraph`, `windowTranscript`).

---

## FE-1-6 — Status selectors + windowed transcript

Pure projections over `RunViewModel` + optional `lastSeq` / `source`:

- `selectStatusBar({ view, source, lastSeq, lastKind })` → `{ source, seq, tokens, costMicros, kind }`
- `windowTranscript(view, cursor: number, height: number)` → bounded rows for Ink/React virtualization (no DOM). Height default 16. Cursor clamps to `[0, max(0, n-height)]`.
- Do **not** re-reduce the ledger inside selectors.

**DoD:** unit tests: empty view, overflow clamp, unknown kinds ignored, `seq` remains string.

---

## FE-1-7 — `toTraceGraph(envelopes)`

`EventEnvelope[] → { nodes, edges }` where `node.id = eventId`, `node.kind = payload.kind`, `node.seq = seq` (string). Edges: `parentEventId → eventId` when present; otherwise sequential by `seq` **only within the same `runId`**. Unknown kinds are opaque nodes. No xyflow types.

**DoD:** golden test on `vanguard/clients/cli/fixtures/sessions/successful-episode.jsonl` (read-only). Graph node count equals parsed envelope count.

---

## FE-1-8 — Stream subscription helper

`subscribeRun(client, cursor, handlers, signal?: AbortSignal)` owns **one** `for await` loop. Handlers: `onItem(StreamItem)`, `onError(ClientFailure)`, `onDone()`. Abort stops the loop; do not throw across the port.

**DoD:** fake async iterable test; abort mid-stream; duplicate `eventId` not the helper’s job (adapter already dedupes).
