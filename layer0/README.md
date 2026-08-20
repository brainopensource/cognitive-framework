# layer0/

Copy-fork to **absorb**, not the v0.6 destination (`ADR-0069`). Production truth is `vanguard/packages/`.

**2.2-B (Wave 2) deleted `kernel/`, `scheduler/` and `spi/` wholesale** — their useful contracts
were absorbed into packages first (wire codec → `domain/wire/jsonrpc.py`, generated types →
`domain/wire/types_gen.py`, SPI Result ADT → `domain/wire/result.py`, the five Protocols →
`ports/spi.py`, ceiling delegation → `adapters/sandbox/ceiling.py`), then the layer0 copies and
their re-export shims were removed. `scheduler/driver.py`'s unsigned `verdict: "pass"` (defect F1)
died with the file; F-03 was repointed onto `runtime/evaluator_gateway.py` at M-1 and never
depended on this tree.

| Dir | Status | Do not treat as production |
|---|---|---|
| `registry/` | **Kept — Wave-3 material.** No packages equivalent exists yet; imports `domain/wire/` and `adapters/sandbox/ceiling.py` directly (2.2-B) | — |
| `compose/` | **Kept — Wave-3 material.** Plugin-slot compiler; no packages equivalent yet. Its `intersect_ceilings` call computes and discards the result (fail-open) — do not carry that into the packages twin | fail-open capability parse |
| `events/` | **Kept in part.** `emitter.py`/`envelope.py`/`store.py`/`taxonomy.py` survive (registry/compose depend on them); `selectors.py`/`canonical.py`/`fold.py`/`blob.py` deleted at 2.2-B (byte-identical or strict-subset duplicates of `domain/`) | `MemoryLedger` (`events/store.py`) is a test double, not I-2/I-4 evidence |
| `kernel/` | **Deleted (2.2-B).** | — |
| `scheduler/` | **Deleted (2.2-B).** | — |
| `spi/` | **Deleted (2.2-B).** | — |

Tests: `test/layer0/` (advisory CI step, not the subject of record). Green here is **not** I-2 / I-4.

Do not delete the remaining tree until the Wave-3 registry/compose walk lands a packages twin.
Do not add a third runtime. See [`../README.md`](../README.md).
