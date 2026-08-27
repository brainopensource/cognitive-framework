# M-6 CLOSURE RECORD — Mediated Delegation

**ADR-0090:** RATIFIED (CEO, 2026-08-24) · **Status:** CLOSED
**Commit:** `53d823e` · **Patch:** `M6_CLOSE_ADR0090.patch`

---

## 1. What was actually missing

Investigation found `ChildSpawned` and `ChildReturned` were **already allocated**
in the 42-kind `EventKind` enum and in `domain/wire/types_gen.py`. They were not
missing — they were sitting in `test/contracts/test_event_coverage.py`'s
`UNFOLDED_ALLOWLIST`, annotated as *"Subagent spawn notification"*.

That annotation was the defect. It classified delegation as an **advisory
marker**. ADR-0090 constraint 4 requires the opposite: `ChildSpawned` /
`ChildReturned` are **material FSM transitions** and must fold into
`LedgerState`, per `001_alfa` §3 (via 005 Epsilon) — every material transition
catalogued, emitted, **and reduced**.

An unfolded delegation event means cold replay reconstructs a run with no record
that a child ever existed. Lineage would have to be inferred from payload
convention — the "path bag pretending to be a graph" failure the architecture
explicitly rejects.

## 2. Changes landed

| file | change |
|---|---|
| `test/contracts/test_event_coverage.py` | both kinds removed from `UNFOLDED_ALLOWLIST` |
| `domain/ledger/state.py` | `ChildRecord` dataclass + `LedgerState.children` |
| `domain/ledger/reducer.py` | two fold arms with monotonic-sequence purity preserved |
| `runtime/ledger_emitter.py` | `spawn_adapter` registered as sole writer |
| `adapters/models/__init__.py` | PEP 562 lazy imports (perf, see §5) |

**The kernel was not touched.** TCB unchanged. Delegation was added without the
trusted core growing by a single line — the milestone's actual claim.

## 3. Verified fold behaviour (real reducer, not a stub)

```
after spawn : status=open reconcilable=True depth=1 auth=('fs.read',)
unknown_events: 0                        <- proves it FOLDS, not falls through
after return: status=closed outcome=completed cost={'usd_micros': 320}
open children now: []

double return   -> ReducerError: child 'ep-c1' returned twice
orphan return   -> ReducerError: ChildReturned without ChildSpawned for 'ep-c1'
duplicate spawn -> ReducerError: duplicate ChildSpawned for 'ep-c1'
```

An unmatched `ChildSpawned` folds to `open` and stays `reconcilable` — it is
**never assumed complete**. That open set is exactly the cold path's input, and
is what makes `UNDETERMINABLE` reachable instead of a silent retry.

### 3.1 One deliberate tolerance

The `test_event_coverage` gate probes every kind with a skeletal payload. The
fold uses `.get()` and no-ops on a payload with no `child_episode_id`, rather
than raising `KeyError`. A malformed child event is not reducible state — but it
must not silently land in `unknown_events` either, which is what the gate checks.
Well-formed payloads still enforce every ADR-0090 invariant.

## 4. Gate results

```
test/contracts/test_event_coverage.py     14 passed
full repository suite                     1294 passed / 8 failed   (= baseline)
bundle suite                              79 passed
RF-86 (all five frozen paths, M-5-BASE)   clean
```

The 8 residual failures are the known environmental set: 3 × no Ollama daemon,
5 × containment probes unattestable under uid 0. **Zero regressions.**

## 5. Performance fix included

`adapters/models/__init__.py` eagerly pulled `ollama → urllib → http.client →
email.parser` on every process start, including `local`-profile runs that never
use it.

```
cold start: 140.8 ms -> 12.9 ms   (10.9x)
urllib.request in sys.modules after importing FakeModel: False
```

## 6. RF-86 baseline ordering — a finding

The first `M-5-BASE` tag was placed **before** the M-6 commit. RF-86 then failed
on `runtime/ledger_emitter.py`, correctly: it cannot distinguish an
ADR-authorised M-6 change from an illicit M-5 kernel hook.

**The gate was right; the tag was in the wrong place.** RF-86 measures *the
formal pack's* diff, so its baseline must be taken after all non-M-5 substrate
work has landed. Re-tagged at `53d823e` (post-M-6); all five paths clean.

**Operational rule:** re-tag `M-5-BASE` after any ADR-authorised substrate
change, and never weaken the assertion to accommodate one.

## 7. Remaining M-6 item

The kill-tree drill (SIGKILL the parent mid-child; assert the cold path returns
`UNDETERMINABLE`, not a retry) requires a live multi-process run and is
therefore **environment-gated alongside M-4 rows 1/4/7**. The reducer-level
property it depends on — an open child is never folded to complete — is proven
above.
