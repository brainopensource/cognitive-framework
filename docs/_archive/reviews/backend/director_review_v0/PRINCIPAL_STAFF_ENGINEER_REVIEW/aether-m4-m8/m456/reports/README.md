# AETHER M-4 → M-8 — Implementation Bundle (wave 2)

Against `cognitive-framework@feat_W4-W6_Higgs_core` (`c8fc6dd`), 2026-08-24.

## Reports
| file | scope |
|---|---|
| `M4_FOUNDATION_EVIDENCE.md` | nine-row evidence, state algebra, profile findings |
| `M5_GENERALITY_PROOF.md` | formal Pack #2, memo soundness, exterior oracle |
| `M6_MEDIATED_DELEGATION.md` | attenuation algebra, spawn adapter, recovery |
| `M7_M8_MEASUREMENT_AND_TOPOLOGY.md` | perf fixes, concurrency plan, topologies, SWE-bench strategy |
| `adr/0090-mediated-delegation-event-roster.md` | **closes M-6** — needs Director ratification |

## Foundation performance fixes (this wave)
One root cause, two axes: every turn re-carried and re-canonicalised
byte-identical layer bodies.

| axis | before | after | factor |
|---|---|---|---|
| RAM, 50 turns | 304,390 B | 27,609 B | **11.0×** |
| CPU, 200 turns | 135.3 ms | 11.4 ms | **11.9×** |
| cold start | 140.8 ms | 12.9 ms | **10.9×** |

* `runtime/context_store.py` — interning + digest memoisation (supersedes `layer_intern.py`)
* `adapters/models_init_lazy.py` — drop-in replacement for
  `vanguard/packages/adapters/models/__init__.py`; PEP 562 lazy imports.
  Verified on the real repo: suite unchanged at 1294 passed / 8 failed.

## Run
```bash
pip install -r requirements.txt
python3 -m pytest tests/ -q        # 79 passed
```

## Status
* **M-4** rows 2,3,6,8,9 derive under `local`; 1,4,5,7 environment-gated. No RF-85 claimed.
* **M-5** complete. `M-5-BASE` tagged at `53d823e`; `rf86_gate.sh` clean on all
  five frozen paths. Wire it into CI.
* **M-6** **CLOSED** — ADR-0090 ratified, folded, single-writer registered,
  landed as commit `53d823e`. See `M6_CLOSURE_RECORD.md` + `M6_CLOSE_ADR0090.patch`.
* **M-7** **UNBLOCKED** — `runtime/independence.py` built and tested. Needs the
  sequential baseline to feed it runtime effect instances (see M7_M8 §5.1).
* **M-8** not authorised. Do not start before M-7's baseline exists.

## Strategy note (see M7_M8 §3)
Scaffolding is worth ~4 points on SWE-bench Verified; model generation is worth
tens. AETHER will not out-score Codex CLI by harness alone. The defensible
differentiator is **attributability** — signed exterior verdicts bound to
preregistered oracles, replayable trajectories, per-row evidence states.
Compete on "you can verify our number."
