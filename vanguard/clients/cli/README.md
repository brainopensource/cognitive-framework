# `vg` CLI / TUI

Ink client for the RuntimeService daemon. Architecture: [`docs/scrum/development_guides/cli_tui_architecture.md`](../../../docs/scrum/development_guides/cli_tui_architecture.md). Lane lock: [`docs/scrum/development_guides/frontend_senior_review_and_two_lanes.md`](../../../docs/scrum/development_guides/frontend_senior_review_and_two_lanes.md).

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
