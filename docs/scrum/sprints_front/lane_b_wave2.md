# Lane FE-B · Wave 2 — live + editor integration

**Write scope:** `vanguard-ide/**`  
**DoD default:** `cd vanguard-ide && npm run typecheck && npm run build`

---

## FE-B5 — Live socket bridge

**Delta:** same vg.4 frames and path resolution as CLI (`--socket-path` / `VANGUARD_RUNTIME_SOCKET` / `/tmp/vanguard-runtime.sock`). Shared vendored transport.

**Depends:** FE-B2. Integrates against the real daemon (not FE-A TUI).

**DoD:** live stream from daemon; typecheck + build.

---

## FE-B6 — Editor context sync

**Delta:** active editor, selection, git state folded into `StartRun` **`brief`** (existing payload). Any new field is a Joint note (D6).

**Depends:** FE-B5.

**DoD:** payload shape unchanged except `brief` contents.

---

## FE-B7 — E2E matrix

**Delta:** tests per `docs/front_v4/007_testing.md`: unit → VG-04 golden vectors → replay E2E → live E2E.

**Depends:** FE-B5.

**DoD:** documented commands in `vanguard-ide/package.json` scripts.

---

## FE-B8 — `.vsix` packaging

**Delta:** produce `.vsix`; short note for Open-VSX / private distribution. No MSI/notarization.

**Depends:** FE-B1.

**DoD:** `npm run build` produces `.vsix`.
