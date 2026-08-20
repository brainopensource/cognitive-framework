# layer0/

Copy-fork to **absorb**, not the v0.6 destination (`ADR-0069`). Production truth is `vanguard/packages/`.

| Dir | Keep / promote | Do not treat as production |
|---|---|---|
| `spi/` | JSON-RPC, Protocols, generated types | — |
| `registry/` | lifecycle / broker | — |
| `compose/` | digest shape | fail-open capability parse |
| `scheduler/` | sequential driver idea | **F1** unsigned `verdict: "pass"` in `scheduler/driver.py` |
| `events/` | envelope / fold ideas | `MemoryLedger` (`events/store.py`) |
| `kernel/` | — | diverging port; packages kernel is the oracle |

Tests: `test/layer0/` (currently living-CI gated). Green here is **not** I-2 / I-4.

Do not delete this tree until Wave 2 parity. Do not add a third runtime. See [`../README.md`](../README.md).
