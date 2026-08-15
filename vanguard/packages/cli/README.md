# `vg` CLI / TUI (T6.4 scaffold)

This package provides the operator surface before the real runtime is available. It uses a deterministic `MockRuntime` behind the same `RuntimePort` that the runtime composition root will implement later.

```bash
npm install
npm run vg -- run . --headless --run-id demo
npm run vg -- run .
npm run vg -- trace demo --headless
npm run vg -- why typed-tools --headless
```

The headless mode emits one JSON object per line for integration tests. The TUI shows the same event stream and supports `c` to cancel and `q` to quit. Checkpoints are emitted every two steps by default; use `--checkpoint-every N`. `--resume RUN_ID` exercises the resume path in the mock adapter.

Integration boundary: replace `MockRuntime` construction in `src/main.tsx` with the runtime client/daemon adapter. Commands and TUI should continue to consume only `RuntimePort` and `RuntimeEvent`.
