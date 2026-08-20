# Wave 2 — Converge Without a Third Tree (absorb `layer0/`, one runtime identity)

**Outcome:** One runtime authority. The useful `layer0/` contracts (wire codec, SPI Protocols,
lifecycle FSM, compose digest **shape**) live on the packages path; the duplicated
kernel/scheduler/mocks are deleted after a behavioral parity gate; `root.py` is split in place.
**Entry:** Wave 1 exit green (the trust spine must be real before the fork that fakes it is deleted,
or the deletion "fixes" F1 by hiding it instead of by proof).
**Exit (M-2):** F-16 duplication detector green; `layer0/` contains nothing the packages path does
not provide; zero imports of `layer0.*` anywhere under `vanguard/`; suites of record green.

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
| 2.2-A | Parity gate: for events/fold and compose-digest shape, run the layer0 suite's behavioral assertions against the packages implementations (adapter tests, not a port of the layer0 code) | `test/layer0/` assertions → `test/contracts/` | Every layer0 behavior worth keeping has a packages twin test; a written parity note in the PR | TECH-LEAD (decide per-assertion keep/kill) |
| 2.2-B | Delete: `layer0/kernel/`, `layer0/scheduler/` (F1 dies here **after** Wave 1 made fabrication impossible on the canonical path), `layer0/events/` MemoryLedger, remaining `layer0/spi`, `layer0/compose`, `layer0/registry` once 2.1/3.1 have absorbed them; retire the v4 envelope write path | repo-wide | `layer0/` gone or empty; CI has no `test/layer0` step; `test/README.md` updated | READY (after 2.2-A) |
| 2.2-C | Split `root.py` **in place** along its existing class seams: `runtime/compose.py` (`Runtime.compose` + manifest artifacts), `runtime/session.py` (`HarnessSession`, `SessionPorts`, swappable policy), `runtime/ledger_emitter.py` (done in 1.2), `runtime/wiring.py` (port bridges, environment/sandbox effectors); `root.py` remains a thin composition facade | `runtime/root.py` | No behavior change: `test/runtime` green unmodified; no module > ~500 LOC; boundary checker green | READY (seams named; internal layout DEV-LOCAL) |
| 2.2-D | Extend `check_domain_blindness.py` to `vanguard/packages/{domain,kernel}/` if Wave 0 did not already (F-18); extend `check_boundaries.py` rows for the new modules | `tools/` | F-18 green; boundary lattice enforced on the split modules | READY |

**Escalate to Director if:** parity work reveals a layer0 behavior that packages *cannot* express
(none is known — that would be ADR-0069's reversal evidence), or the split wants a new top-level
package.
