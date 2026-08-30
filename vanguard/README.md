# vanguard/

Production code for AETHER / Vanguard. Lattice: `packages/` (Python) + `clients/` (TypeScript).

```text
packages/   domain ← ports ← kernel ← agency ← runtime → adapters
            apps/ is a lattice slot (empty of coding modules today)
clients/    cli (`vg`) · client-core
```

This is the **sole canonical runtime** (`ADR-0069`); the former Layer-0 copy-fork is retired.

Entry points: `packages/runtime/root.py` (composition), `packages/agency/episode/engine.py` (`EpisodeEngine` / `spawn()`), `clients/cli/src/main.tsx` (`vg`), evaluator `packages/adapters/evaluators/daemon.py`.

Current milestone authorization is recorded only in
[`docs/execution/active.md`](../docs/execution/active.md). Map: [`../README.md`](../README.md).
