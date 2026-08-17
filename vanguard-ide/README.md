# Vanguard IDE

VS Code extension for the Vanguard agent runtime. Provides a sidebar run stream, CodeLens approval UX, and live/replay socket bridge.

**Lane FE-B** — `vanguard-ide/` only. Does not modify `vanguard/clients/cli/**` or `vanguard/packages/**`.

## Build

```bash
cd vanguard-ide
npm install
npm run typecheck   # DoD gate
npm run build       # produces dist/ + .vsix
```

## Test matrix (FE-B7)

```bash
npm run test:unit     # reducers, parse, signer
npm run test:vectors  # VG-04 golden vectors
npm run test:replay   # replay E2E (no daemon required)
npm test              # all three
```

## Commands

| Command | Description |
|---|---|
| `Vanguard: Start Run` | Start a live run against the daemon |
| `Vanguard: Cancel Run` | Abort the active stream |
| `Vanguard: Replay Fixture (no daemon)` | Stream a `.jsonl` fixture without a daemon |
| `Vanguard: Show Daemon Status` | Connect-only probe (J2 — no Ping) |

## Wire contract

vg.4 NDJSON over Unix domain socket. Socket path resolution (D1, `docs/front_v4/003_wire_consumer.md`):
1. `vanguard.socketPath` VS Code setting
2. `VANGUARD_RUNTIME_SOCKET` env var
3. `/tmp/vanguard-runtime.sock`

## Vendoring (FE-B2)

`src/contract/types.ts`, `src/contract/parse.ts`, `src/adapters/replay.ts`, and `src/adapters/signer.ts`
are vendored copies of their FE-A originals in `vanguard/clients/cli/src/contract/` and `src/adapters/`.

**Single source of truth is FE-A.** To update, copy the changed file from the CLI tree and update the
`VENDORED from` comment. Do not import from the CLI tree at runtime (no monorepo runtime dependency).

## Distribution (FE-B8)

`npm run build` runs `scripts/bundle-vsix.js` which calls `vsce package`.

- **Open-VSX**: `npx vsce publish --packagePath vanguard-ide-*.vsix` or upload via [open-vsx.org](https://open-vsx.org)
- **Private**: share the `.vsix` file; users install with _Extensions: Install from VSIX…_

No MSI/notarization required (D3 — extension-first).

## Boundary check

```bash
grep -r "vanguard/packages" vanguard-ide/src || true  # expect no hits
```
