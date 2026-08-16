# Sprint 4 executable backlog

Sprint goal: Increment A no-model trust spine; disposables gone; real OpenRouter and Git adapters exist but unused by the gate.

| Ticket | Assignee | Scope | Contract | Depends | Evidence |
|---|---|---|---|---|---|
| `S4-SA-001` | Senior A | Finish episode: recursion depth, cancellation, scripted no-model trajectory | `REQ-TRUST-001` | S3-INT | Denial, attenuation, budget, atomicity, recovery, secrets |
| `S4-DC-001` | Dev C | OpenRouter ModelPort adapter + cassette; secrets as references | `REQ-PORT-006` | S3-DC-001 | Tests skip when key unset; never imported by trust-spine |
| `S4-SB-001` | Senior B | Worker perimeter probes; unverified blocks publish | `REQ-SEC-001` | S3-DC-003 | Mount/egress/syscall report |
| `S4-DD-001` | Dev D | Permanent Git EnvironmentAdapter; typed tools as effects | `REQ-PORT-003` | S3-DD-001 | New file in preview; not copied from `slice/` |
| `S4-GATE-001` | Senior A | Trust-spine CI with key unset; delete `spike/` and `slice/` | `REQ-TRUST-001`, `REQ-ARCH-002` | SA-001, SB-001 | `MF-S4-001`; findings notes remain |
