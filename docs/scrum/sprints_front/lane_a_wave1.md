# Lane FE-A · Wave 1 — hygiene and protocol truth

**Write scope:** `vanguard/clients/cli/**`  
**Do not touch:** `vanguard-ide/**` · `vanguard/packages/**` · `docs/main_v4/**`  
**DoD default:** `cd vanguard/clients/cli && npm run typecheck && npm test`

---

## FE-A1 — Delete dead scaffold; wire signer

**Delta:** remove `src/commands.ts`, `src/runtime.ts`, `src/mock-runtime.ts`. Wire `src/adapters/signer.ts` into the approval path (needed for signed approvals). Update imports in `main.tsx` / composition.

- [x] Grep: no remaining imports of deleted modules
- [x] Signer is constructed in composition and used on approve
- [x] `npm run typecheck && npm test`

**DoD:** typecheck + tests green; grep shows no imports of deleted files.

---

## FE-A2 — Split live transports; parse frames

**Delta:** `src/adapters/live.ts` — `FeedTransport` / `SocketTransport` behind a transport interface. Remove `isFeedMode()` branches. Type `frame` via `parse` (CT-03); no `any` casts on the socket.

- [ ] Existing tests green **without modification**
- [ ] No `isFeedMode` in src

**DoD:** existing tests green without modification.

---

## FE-A3 — RFC-8785 JCS + key persistence

**Delta:** `src/adapters/signer.ts` — add a `canonicalize` (RFC 8785) dependency; persist keys at `~/.vanguard/keys` mode 0600.

- [ ] Round-trip test vs Python `OperatorSigner` golden vector (read-only backend vectors)
- [ ] No PEM in logs

**DoD:** new signer test + `npm test`.

---

## FE-A4 — TUI restructure

**Delta:** move presentation to `src/tui/{components,screens,hooks,theme}/`; `src/composition/` for wiring. Extract `useVanguardRun` from `RunTui` / `live-screen.tsx`. Fix `ApprovalModal` misleading props.

- [ ] Boundary test extended to new paths (no UI imports in application)
- [ ] `ui.test.ts` (or relocated equivalent) passes

**DoD:** boundary test + UI tests pass.

**Depends:** FE-A1.

---

## FE-A5 — Reconnect / backoff / timeouts

**Delta:** live `SocketTransport` — configurable timeouts, reconnect with backoff, resume via `afterSeq`.

- [ ] New tests with a fake socket (no real daemon)

**DoD:** new tests + existing suite green.

**Depends:** FE-A2.
