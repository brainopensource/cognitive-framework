# Lane FE-B · Wave 1 — scaffold against replay

**Write scope:** `vanguard-ide/**` only  
**Does not depend on FE-A wave completion** — only frozen `vanguard/clients/cli/src/contract/` + `fixtures/*.jsonl`  
**DoD default:** `cd vanguard-ide && npm run typecheck && npm run build`

---

## FE-B1 — Extension scaffold

**Delta:** new `vanguard-ide/` (TypeScript, `vscode` engine, esbuild). CI-free local build.

Contributes: sidebar webview view, commands, CodeLens provider stub.

**DoD:** `npm run typecheck && npm run build`.

---

## FE-B2 — Vendor the client contract

**Delta:** copy `contract/types.ts` + `contract/parse.ts` + a `RuntimeClient`-shaped port into `vanguard-ide/src/contract/`. Single source of truth remains the FE-A repo path; vendoring is a documented build step (no runtime monorepo import).

Replay adapter against `vanguard/clients/cli/fixtures/*.jsonl`.

**DoD:** replay loads a fixture without a daemon.

---

## FE-B3 — Webview run stream

**Delta:** thoughts / tools / budget view. Port reducer pattern from `vanguard/clients/cli/src/application/run-view.ts` via vendored package or copy. Design tokens from `docs/front_v4/004_ui_ux.md`.

**Depends:** FE-B1, FE-B2.

**DoD:** webview renders from replay fixture without a daemon.

---

## FE-B4 — Approval UX

**Delta:** diff view + `[Approve & Sign]` / `[Reject]` CodeLens + Ed25519 signing (port of FE-A3 signer semantics).

**Depends:** FE-B3; signer bytes compatible with FE-A3.

**DoD:** approve/reject on a replay `ApprovalRequested` envelope.
