# Sprint 9 · Lane A — Control Plane (support lane)

**Owner:** Senior A · **Refinement:** PLANNED, NOT REFINED

Lane A supports the instrument this sprint; it does not lead it.

- [ ] **S9-A-01** — surface the fields the instrument needs on `RunResult`: `gene_digests`,
      composition digest, per-arm instrument-error reason, turn/token/cost integers
- [ ] **S9-A-02** — integer telemetry discipline: integer microseconds, integer token counts,
      integer USD micros. **No floats as truth** (`S6B-MD-009`)
- [ ] **S9-A-03** — ensure `Recording` carries enough for replay of a benchmarked run; note any gap
      against Phase 4 `V5-A` (tool-schema / context-compiler / manifest digests)
- [ ] **S9-A-04** — capacity to support Lane C on ledger queries for the paired runner

**Stop condition:** if the instrument needs a field the event envelope does not carry, that is an
`L-1` corpus-format decision requiring an ADR — **stop**, do not add it inline.
