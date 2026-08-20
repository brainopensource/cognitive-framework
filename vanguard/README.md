# vanguard/

Production code for AETHER / Vanguard. Lattice: `packages/` (Python) + `clients/` (TypeScript).

```text
packages/   domain ← ports ← kernel ← agency ← runtime → adapters
            apps/ is a lattice slot (empty of coding modules today)
clients/    cli (`vg`) · client-core
```

This is the **canonical runtime** (`ADR-0069`). `../layer0/` is a fork to absorb, not a replacement.

Entry points: `packages/runtime/root.py` (composition), `packages/agency/episode/engine.py` (`EpisodeEngine` / `spawn()`), `clients/cli/src/main.tsx` (`vg`), evaluator `packages/adapters/evaluators/daemon.py`.

Do not start Wave 0–4 implementation until Director **APPROVED**. Map: [`../README.md`](../README.md).
