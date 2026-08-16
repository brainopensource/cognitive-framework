# Sprint 3 executable backlog

Sprint goal: port activation bundles plus a cassette episode slice and a model-free process engine, all talking to the existing kernel and ledger.

| Ticket | Assignee | Scope | Contract | Depends | Evidence | Merge |
|---|---|---|---|---|---|---|
| `S3-DC-001` | Dev C | ModelPort interface + fake/cassette + suite | `REQ-PORT-002` | none | instrument_error fixture | FAST |
| `S3-DC-002` | Dev C | EvaluatorPort interface + fake + agency isolation | `REQ-PORT-004` | DC-001 | architecture must-fail | FAST |
| `S3-DC-003` | Dev C | SandboxRunner interface + unverified-blocks-publish fake | `REQ-PORT-005` | none | publication blocked | FAST |
| `S3-DD-001` | Dev D | EnvironmentAdapter fake + argv test + new-file preview | `REQ-PORT-003` | none | slice-findings absorbed | FAST |
| `S3-DD-002` | Dev D | `vg-code-default` manifest; `vg-shell-only` stays undeletable | `REQ-HARN-001` | DD-001 | freeze-at-composition | FAST |
| `S3-SA-001` | Senior A | Episode loop depth-1, cassette model, terminals, no self-eval | `REQ-EXEC-001` | DC-001 | cassette turn through `Kernel.dispatch` | GATE |
| `S3-SB-001` | Senior B | Process engine restart-resume, no model | `REQ-EXEC-002` | none | interrupted instance reconstitutes | GATE |
| `S3-INT-001` | Senior A | Same ledger: one episode turn + one process resume | `REQ-EXEC-001`, `REQ-EXEC-002` | SA-001, SB-001, DC-* | architecture tests still forbid agency→adapters and governance→model | GATE |

Out: OpenRouter live (`S4-DC`), Git real adapter (`S4-DD`), containment probes (`S4-SB`), `TEST-TRUST-001` (`S4-SA`).
