# kernel

Capabilities, grants, attenuation, policy, budgets, dispatch and provenance.
May import `domain` and `ports` only.

This is the Trusted Computing Base. Every effect passes through
`Kernel.dispatch` and there is no second path (`05 §2.1`, `ICD §3`, `AT-01`).

| Module | Owns | Rules |
|---|---|---|
| `model.py` | Request, span, outcome, event and failure-path values | `05 §2.3`, `CT-10` |
| `ports.py` | The interfaces the kernel depends on | `01 §2` (DIP, Liskov, ISP) |
| `provenance.py` | The authority predicate and monotone span accumulation | `K-28`..`K-33` |
| `classifier.py` | Capability-widening classification; the sink registry | `K-08`, `K-32`, `ICD §3` |
| `attenuation.py` | Child-grant narrowing, monotone-decreasing | `K-23`..`K-27`, `K-48` |
| `grants.py` | Issuance, point-of-effect verification, revocation | `K-18`..`K-21`, `K-49`, `CT-51` |
| `budget.py` | Reserve, commit, release; overruns debited | `K-07`, `CT-06`, `CT-07` |
| `policy.py` | S5 AUTHORIZE — the decision, and only the decision | `F-06`..`F-10`, `K-17` |
| `dispatch.py` | S0..S12 in order | `K-04`..`K-08`, `K-47` |

## Verification

```bash
python3 -m unittest discover -s test
python3 tools/check_boundaries.py
python3 tools/run_broken_tests.py      # includes MF-KRN-001..011
```

The must-fail counterparts live in `test/broken/fixtures/kernel/scenario.py`.
Each plants one defect at one seam and leaves the rest of the kernel real:

* `MF-KRN-001` — the widening classifier as a constant. No constant satisfies
  both a within-authority scenario and an escalation scenario.
* `MF-KRN-002` — justifying spans reset between turns, which makes the
  untrusted branch unreachable dead code. Against the defect the widening
  request completes, and the effect executes.
* `MF-KRN-003` — a grant that binds no descriptor, and a verifier that
  compares none. Against the defect a substituted call rides an approved grant.
* `MF-KRN-004..007` — widening attenuation, permissive grant verification,
  emission before release, and a clamped budget overrun.
* `MF-KRN-008..010` — a privileged sink weakened to `pure`, an effect with no
  durable intent, and dispatch occurring before intent durability.
* `MF-KRN-011` — unreviewed policy-kernel growth beyond the measured alarm.

## Integration boundary

Kernel role protocols are owned by `vanguard/packages/ports/kernel.py`.
Approval suspension is represented by its token and failure path; the resume
driver belongs to `runtime` and lands with the S4 process engine.
