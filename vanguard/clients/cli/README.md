# `aether` / `vg` CLI / TUI

Requires Node ≥ 20. Architecture & Spec: [`docs/execution/spec.md`](../../../docs/execution/spec.md).

## Install

From the repository root (writes `aether` and `vg` into `~/.local/bin`):

```bash
just install-cli
# or
bash vanguard/clients/cli/install.sh
```

Then, from any directory:

```bash
aether
aether run /path/to/repo
aether --help
```

`npm link --workspace @vanguard/cli` also works, but the symlink lives in the current Node version's bin and disappears if you switch nvm versions.

## Flags

`aether --help` lists: `--headless --feed --scenario --demo --replay --run-id --resume --checkpoint-every --repo --prompt --brief --model --manifest --decision --socket-path --yes|-y --help`.

Socket path: `--socket-path` → `AETHER_RUNTIME_SOCK` → `/tmp/vanguard-runtime.sock`.

## Examples

```bash
npm install
npm run typecheck && npm test
aether
vg run --demo --headless
vg run . --headless --prompt "fix the test"
vg daemon status
```

`--demo` replays `fixtures/sessions/` and labels `source: mock`. It does not open the daemon socket.
