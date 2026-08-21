# Wave 4 — Foundation E2E (the stop condition)

**Outcome:** One verified real coding-agent path through the production substrate, leaving
trustworthy state and evidence behind. This is the foundation MVP and the architectural
integration test in one. **After this gate: stop.** Extra packs, concurrency, multi-agent policy,
lab promotion, and Meta-Harness are all post-foundation programmes (`002` §2).
**Entry:** Waves 1–3 exit gates green.
**Exit (M-4):** the nine-row table below is true **on one uninterrupted run**, reproduced in CI
nightly (live-model row may substitute the recorded cassette of that same run in per-PR CI).

## Sprint 4.1 — One real run

The task: compile `packs/code-default/harness.yaml`, point it at a small fixture repository with a
failing test, and let the agent make it pass.

| Required (from `002` §3 Wave 4) | Proof on the run's artifacts |
|---|---|
| Real model | Tier-1 Ollama route answered; `model_routes_used` + fingerprint in the trajectory |
| Authorized effect | `patch.apply` receipt carries `grant_digest` + `lease_id`; ADVISORY-only run fails the gate |
| Filesystem change | The fixture repo's test goes green; artifact digest in the receipt |
| Sandbox | The patch/test execution happened in the bwrap cell (containment report attached) |
| Exterior signed eval | `VerdictRecorded` with bound `SignedVerdict`, appended by the gateway |
| WAL ledger | The run's events are on disk in the packages store; no MemoryLedger anywhere |
| Cold replay | `replay-parity` reconstructs the run's terminal state from that WAL file |
| Trajectory | `mhf.trajectory/1` validates against the schema, turns populated, verdict embedded |
| One runtime authority | `layer0/` deleted; duplication detector green; one scheduler |

| # | Task | Readiness |
|---|---|---|
| 4.1-A | Fixture repository + preregistered oracle (restores the F-20 oracle-registry artifact at its canonical home, `packs/code-default/oracles/`) | READY |
| 4.1-B | E2E harness test wiring the nine rows into one asserted run (`test/integration/` — made importable in Wave 0) | READY |
| 4.1-C | Cassette recording of the green run for deterministic per-PR CI replay (K-12: S1–S8 still execute) | READY |
| 4.1-D | Run report: attach ledger digest, `D_H`/`D_R`, trajectory, containment report as the milestone's evidence bundle | DEV-LOCAL |

**Escalate to Director:** any temptation to widen scope to make the run pass (new event kind, new
SPI, kernel change, concurrency). The correct response to a gap found here is a small fix in the
owning wave's surface, not a new mechanism.

**After the gate:** tag the release cut (version bump from `0.4.5b1` is a Director decision at
that point), then open the post-foundation programme from `002` §2's deferred table.
