# Sprint 9 · Lane A — Control Plane (support lane)

**Owner:** Senior A · **Refinement:** **REFINED AND OPEN (2026-08-16)** · **Commit prefix:** `[lane-a]`

Lane A supports the instrument this sprint; it does not lead it. Lane C leads.

## ▶ YOUR S9 FIRST TASK: `S9-A-01` — **BLOCKED BY `S8-A-01`**

`RunResult` is produced by `HarnessSession.run()`, which does not exist until you land `S8-A-01`.
Adding the instrument's fields to today's shape means adding them twice. Land `S8-A-01` first.

**DoD command when unblocked:** `python3 -m unittest discover -s test/runtime -t .` — green with the
new fields asserted.

**Authorised to start NOW, in parallel with Sprint 8 (prep for `S9-A-03`):** audit `Recording`
against Phase 4 `V5-A` and write down which digests a benchmarked run must carry to be replayable —
tool-schema, context-compiler, manifest, composition. Prose, no code. If it finds a gap, that gap is
an `L-1` corpus-format decision needing an ADR, and finding it now is worth far more than finding it
mid-instrument.

`S9-A-02` is **BLOCKED BY `S9-A-01`** — integer-telemetry discipline applies to the fields A-01 adds.

- [ ] **S9-A-01** — surface the fields the instrument needs on `RunResult`: `gene_digests`,
      composition digest, per-arm instrument-error reason, turn/token/cost integers
- [ ] **S9-A-02** — integer telemetry discipline: integer microseconds, integer token counts,
      integer USD micros. **No floats as truth** (`S6B-MD-009`)
- [ ] **S9-A-03** — ensure `Recording` carries enough for replay of a benchmarked run; note any gap
      against Phase 4 `V5-A` (tool-schema / context-compiler / manifest digests)
- [ ] **S9-A-04** — capacity to support Lane C on ledger queries for the paired runner

**Stop condition:** if the instrument needs a field the event envelope does not carry, that is an
`L-1` corpus-format decision requiring an ADR — **stop**, do not add it inline.
