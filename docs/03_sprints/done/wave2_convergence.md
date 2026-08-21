# Wave 2 — Converge Without a Third Tree (absorb `layer0/`, one runtime identity)

**Outcome:** One runtime authority. The useful `layer0/` contracts (wire codec, SPI Protocols,
lifecycle FSM, compose digest **shape**) live on the packages path; the duplicated
kernel/scheduler/mocks are deleted after a behavioral parity gate; `root.py` is split in place.
**Entry:** Wave 1 exit green (the trust spine must be real before the fork that fakes it is deleted,
or the deletion "fixes" F1 by hiding it instead of by proof).
**Exit (M-2):** F-16 duplication detector green; zero imports of `layer0.*` anywhere under
`vanguard/`; suites of record green; every surface the 2.2-A triage marked KILL is gone.
**Amended at 2.2-A:** "`layer0/` contains nothing the packages path does not provide" is *not* an
M-2 gate. `layer0/registry/` and `layer0/compose/` have no packages equivalent and are Wave-3
material (M-3's exit gate is the plugin lifecycle walk they implement), so `layer0/` survives Wave 2
in reduced form and is deleted at the 3.1 exit.

**Direction (ADR-0069, ADR-0076):** absorb *into* packages. Never "fix" a layer0 module in place —
if it is worth fixing, it is worth moving; if not worth moving, it is deleted at parity.

---

## Sprint 2.1 — Absorb the wire and the contracts

| # | Task | Where | Acceptance evidence | Readiness |
|---|---|---|---|---|
| 2.1-A | Move the wire codec: `layer0/spi/jsonrpc.py` → `vanguard/packages/domain/wire/jsonrpc.py` (pure stdlib, fits domain); update the 6 importing adapter files | `adapters/{sandbox/toolkit,evaluators/gate,models/planner,context/window,stores/memory_engine}.py` | `grep -rn "from layer0" vanguard/` empty for jsonrpc; boundary checker green | READY |
| 2.1-B | Move generated types + Result: codegen targets `vanguard/packages/domain/wire/types_gen.py`; `layer0/spi/types_gen.py` becomes a re-export shim until 2.2 deletes it | `tools/codegen/generate_types.py` | `--check` green against the new target; no hand-written mirror types anywhere (I-1/A-4) | READY |
| 2.1-C | Move SPI Protocols (`IPlanner`, `IMemoryEngine`, `IToolkit`, `IContextManager`, `IEvaluationGate`) → `vanguard/packages/ports/spi.py`; Protocols stay client conveniences of the wire (ADR-0072) | `layer0/spi/*.py` → `ports/` | Contract tests in `test/contracts` cover the five; no sixth SPI (ADR-M0-03) | READY |
| 2.1-D | Ceiling delegates to the domain algebra: reimplement `ceiling_allows` on `parse_selector`/`decide`; **fail-closed** (`not capabilities` ⇒ deny `execute`); land beside the toolkit host in adapters | `layer0/spi/ceiling.py` → `adapters/sandbox/` | F-07 negative fixture (the old `return True` branch) fails against it; F-16: `_selector_subset` deleted | READY (decision made, ADR-0076 §2) |
| 2.1-E | `tools/check_duplication.py`: detector for second selector algebra / second canonicalisation / second envelope writer (Wave 0 stub hardened here) | `tools/` | Detector red on a planted duplicate fixture in `test/broken/fixtures/` | DEV-LOCAL (detection heuristics) |

## Sprint 2.2 — Parity, deletion, and the root split

| # | Task | Where | Acceptance evidence | Readiness |
|---|---|---|---|---|
| 2.2-A | Parity gate: for events/fold and compose-digest shape, run the layer0 suite's behavioral assertions against the packages implementations (adapter tests, not a port of the layer0 code) | `test/layer0/` assertions → `test/contracts/` | Every layer0 behavior worth keeping has a packages twin test; a written parity note in the PR | **DONE — triage below; 2.2-A GREEN, deletion authorized** |

### 2.2-A keep/kill (Tech Lead, settled)

25 assertions across 10 modules. KEEP = packages needs an equivalent before deletion.

| layer0 behavior | Call | Justification |
|---|---|---|
| `events/selectors.py` (450 LOC) | **KILL** | Bodies are **byte-identical** to `domain/selectors/resource_selector.py` (verified by diff). Pure duplicate, no behavioral triage needed. |
| `events/canonical.py` JCS + digest | **KILL** | Byte-identical to `domain/canonicalisation/jcs.py` apart from whitespace. |
| `canonical.chain_digest` formula | **KILL** | layer0 chains `digest({prev, envelope})`; the emitter chains `digest(envelope)` with `prev_digest` *inside* the envelope. Same chaining property, and the packages form covers the field actually persisted. Not weaker. |
| `events/fold.py` lifecycle + grants | **KILL** | `domain/ledger/reducer.py` is a strict superset (grants, revocations, leases, debits, approvals, effects, FSM, `unknown_events`). |
| `events/fold.py` **branch resume** | **KEEP — absorbed** | SPEC §1.3 ("fold to `seq=N` + resume with a divergent `branch_id`"). `LedgerState` had no `branch_id`, so trunk and branch folded to the same digest. Landed: `state.py`, `reducer.py`, twin in `test/runtime/test_ledger_truth.py::BranchResume`. |
| `events/blob.py` fsync-before-emit | **SPLIT** | The *emit* half is **KILL** — a blob store is not a ledger writer (ADR-0076 §6). The *durability* half is **KEEP — absorbed**: `FileBlobStore` wrote straight to the final path, so a torn write left a blob whose bytes did not hash to its own address. Now staged + fsync + `os.replace`, with a twin in `test/runtime/test_blob_and_index_ports.py`. |
| `kernel/budget.py` 6-dim `Reservation` (`turns`, `depth` held and summed) | **KILL — contradicted** | ADR-0074 §2 / F-10 / the M-1 1.3-C ruling: depth and turns are structural ceilings, not conserved costs. Enforcement already lives in the right places (`Constraints.max_depth`, `task.max_turns`). |
| …but the *hazard* it leaves | **KEEP — absorbed** | `Governor.reserve` is duck-typed on `as_map()`, and the generated wire `Reservation` (`domain/wire/types_gen.py`, canonical since 2.1-B) is structurally interchangeable while carrying `depth`/`turns`. Repointing a caller from the layer0 governor to the packages one would have **silently** restored sibling-depth summing. `ADDITIVE_DIMENSIONS` now names the conserved set and `reserve()` refuses anything else; falsifier in `test/falsifiers`. |
| `kernel/{dispatch,attenuation,grants,policy,classifier,model,provenance}.py` | **KILL** | `vanguard/packages/kernel/` is the canonical TCB and the subject of record. The 3 pre-existing `test/layer0/kernel/test_dispatch.py` errors are fork drift against regenerated types — do not repair. |
| `scheduler/driver.py` unsigned `"pass"` (F1) | **KILL** | Fabrication is impossible on the canonical path since M-1 (`runtime/evaluator_gateway.py` is the sole `VerdictRecorded` writer). Deleting the file *is* the fix. |
| `scheduler/driver.py` trajectory + spawn spans | **KILL** | `agency/episode/engine.py` + `runtime/trajectory.py` (1.3-D) supersede it; spawn attenuation is covered by F-09. |
| `spi/jsonrpc.py` | **KILL — absorbed now** | Still a full second copy after 2.1-A moved the canonical one to `domain/wire/`; the detector does not check this surface, so it was invisible. Reduced to a re-export shim, matching what 2.1-A did for `result.py` and `types_gen.py`. A `JsonRpcError` raised in a cell and one caught in a packages adapter are now the same class. |
| `spi/{result,types_gen,ceiling}.py` | **KILL** | Already re-export shims (2.1-A/B/D). Deletion is a mechanical import rewrite, not a parity question. |
| `spi/interfaces.py`, `spi/fakes.py` | **KILL** | Protocols moved to `ports/spi.py` (2.1-C); fakes are layer0-suite-local. |
| `events/{emitter,envelope,store}.py` incl. `MemoryLedger` | **KEEP — deferred, not absorbed** | `layer0/registry/` depends on the emitter, and `MemoryLedger` is used by `test/adapters`, `test/registry`. Dies **with** the registry at 3.1, not in 2.2-B. Needs a packages test double then. |
| `registry/` (broker, lifecycle, validator, worker, sandbox, isolation, grants) | **KEEP — Wave 3 material** | There is **no** plugin lifecycle in `vanguard/packages/` at all, and M-3's exit gate is the DISCOVERED→…→RETIRED walk. 2.2-B's own text already gates this on 3.1. Not deletable in Wave 2. |
| `compose/compiler.py` (plugin-slot compose) | **KEEP — Wave 3 material** | Packages compose is artifact-graph based; it has no plugin-slot/SPI-binding/model-route resolution. Live consumer: `packs/code-default/load.py`, hence `test/packs`. Its thrown-away `intersect_ceilings` result (fail-open) is **KILL** and must not be carried into the packages twin. |
| `events/taxonomy.py` | **KEEP — deferred** | `tools/check_event_coverage.py` reads `EMITTER_SITES`; retarget at `domain/ledger/events.EVENT_KINDS` when the tool is rewired (E-COV is not a CI step today). |
| `registry/test_lifecycle`, `replay/test_parity`, `compose/test_compiler`, `spi/test_interfaces` assertions | **KEEP with their subjects** | They assert the KEEP-deferred surfaces above; they move when those move, in 3.1. |

**Deletion scope this authorizes (once the blocker clears):** `layer0/kernel/`, `layer0/scheduler/`,
`layer0/events/{selectors,canonical,fold,blob}.py`, `layer0/spi/{interfaces,fakes}.py`, and the
`layer0/spi/` shims once their importers are rewritten. **Retained until 3.1:** `layer0/registry/`,
`layer0/compose/`, `layer0/events/{emitter,envelope,store,taxonomy}.py`. `layer0/` therefore does
**not** disappear in Wave 2 — M-2's "`layer0/` removed" gate moves to the 3.1 exit.
| 2.2-B | Delete: `layer0/kernel/`, `layer0/scheduler/` (F1 dies here **after** Wave 1 made fabrication impossible on the canonical path — M-1 repointed falsifier F-03 onto `runtime/evaluator_gateway.py`, so the surviving `payload={"verdict": "pass"}` in `layer0/scheduler/driver.py` is carried here as the deletion's own acceptance evidence and must not outlive 2.2-B), `layer0/events/` MemoryLedger, remaining `layer0/spi`, `layer0/compose`, `layer0/registry` once 2.1/3.1 have absorbed them; retire the v4 envelope write path | repo-wide | `layer0/` gone or empty; CI has no `test/layer0` step; `test/README.md` updated | READY (after 2.2-A) |
| 2.2-C | Split `root.py` **in place** along its existing class seams: `runtime/compose.py` (`Runtime.compose` + manifest artifacts), `runtime/session.py` (`HarnessSession`, `SessionPorts`, swappable policy), `runtime/ledger_emitter.py` (done in 1.2), `runtime/wiring.py` (port bridges, environment/sandbox effectors); `root.py` remains a thin composition facade | `runtime/root.py` | No behavior change: `test/runtime` green unmodified; no module > ~500 LOC; boundary checker green | READY (seams named; internal layout DEV-LOCAL) |
| 2.2-D | Extend `check_domain_blindness.py` to `vanguard/packages/{domain,kernel}/` if Wave 0 did not already (F-18); extend `check_boundaries.py` rows for the new modules | `tools/` | F-18 green; boundary lattice enforced on the split modules | READY |

**Escalate to Director if:** parity work reveals a layer0 behavior that packages *cannot* express
(none is known — that would be ADR-0069's reversal evidence), or the split wants a new top-level
package.
