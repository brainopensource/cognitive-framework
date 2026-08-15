# Field inventory — T0 output

Status: `EMPTY TEMPLATE — populate from BUG-01..03 and NONCODE-01`  
Owner: Tech Lead  
Independent reconstruction owner: unassigned

## Trace register and human baseline

| Trace | Repository/base | Issue | Shape | Recorders | Reconstructor | Elapsed ms | Hands-on ms | Reconstruction state |
|---|---|---|---|---|---|---:|---:|---|
| `BUG-01` | TBD | TBD | single-file | TBD | TBD | — | — | not started |
| `BUG-02` | TBD | TBD | multi-file | TBD | TBD | — | — | not started |
| `BUG-03` | TBD | TBD | test-reactive | TBD | TBD | — | — | not started |
| `NONCODE-01` | TBD | TBD | reconciliation/log triage | TBD | TBD | — | — | not started |

## Field evidence

Add one row per distinct semantic field. Do not merge two fields merely because their names look similar.

| Candidate field | Needed by traces | Why reconstruction needs it | VG-04 field/rule | Fillable at capture? | Referenced during reconstruction? | Class | Disposition | Owner |
|---|---|---|---|---|---|---|---|---|
| example: `environmentSnapshot` | BUG-01 | distinguishes observation state from later effect state | VG-04 EventEnvelope | yes | TBD | candidate-universal | pending evidence | Tech Lead |

Class is exactly `universal`, `domain`, or `speculative`. Disposition is `enter-v0.1`, `defer`, `amend-vg04`, or `reject`, and requires Tech Lead approval.

## VG-04 fields unfillable at capture time

| VG-04 field/rule | Trace and step | Why unfillable | Proposed source/default | Risk if retained | Decision/ADR |
|---|---|---|---|---|---|
| TBD | TBD | TBD | TBD | TBD | pending |

## Fields never referenced during reconstruction

| Field | Present in traces | Reconstruction count | Why it may be speculative | Disposition |
|---|---:|---:|---|---|
| TBD | 0 | 0 | TBD | pending |

## Missing fields discovered by reconstruction

| Gap ID | Trace/step | Reconstructor question | Candidate field | Universal/domain hypothesis | Schema owner decision |
|---|---|---|---|---|---|
| GAP-001 | TBD | TBD | TBD | TBD | pending |

## Sign-off

- [ ] Three real coding bugs traced.
- [ ] One non-coding task traced.
- [ ] Independent reconstruction completed without interviews before gap capture.
- [ ] Every VG-04 field classified as evidenced, unfillable, or never referenced.
- [ ] Every missing field has a gap ID.
- [ ] Human elapsed and hands-on baselines recorded.
- [ ] Tech Lead approved v0.1 dispositions.
