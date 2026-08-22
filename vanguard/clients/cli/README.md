# `vg` CLI / TUI

Ink client for the RuntimeService daemon. Architecture: [`docs/SPEC.md`](../../../docs/SPEC.md) · Decisions: [`docs/05_adr/INDEX.md`](../../../docs/05_adr/INDEX.md).

Requires Node ≥ 20. Do not import `vanguard/packages`.

## Install

```bash
# channel 1
bash install.sh
# channel 2
npm install -g .
```

## Flags

`vg --help` lists: `--headless --feed --scenario --demo --replay --run-id --resume --checkpoint-every --repo --prompt --brief --model --manifest --decision --socket-path --yes|-y --help`.

Socket path: `--socket-path` → `VANGUARD_RUNTIME_SOCKET` → `/tmp/vanguard-runtime.sock`.

## Examples

```bash
npm install
npm run typecheck && npm test
vg run --demo --headless
vg run . --headless --prompt "fix the test" --manifest ./manifest.json
vg daemon status
vg --help
```

`--demo` replays `fixtures/sessions/` and labels `source: mock`. It does not open the daemon socket.
