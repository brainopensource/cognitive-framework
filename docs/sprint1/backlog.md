# Sprint 1 executable backlog

Sprint goal: produce evidence-ready v0.1 schema candidates and the disposable provider notes without merging or locking ahead of T0 human closure.

| Ticket | Assignee | Scope | Contract rows | Depends on | Acceptance evidence | Merge state |
|---|---|---|---|---|---|---|
| `S1-D1-001` | Dev 1 | T1.1 canonicalisation and 40+ triples | `REQ-SCHEMA-001` | none | two-reader golden vector report | blocked until T0 human close |
| `S1-D1-002` | Dev 1 | T1.2 primitives | `REQ-SCHEMA-002` | D1-001 | valid/invalid primitive vectors | blocked |
| `S1-D1-003` | Dev 1 | T1.3 VG-04 selector algebra | `REQ-SCHEMA-003` | D1-002 | property and must-fail selector suite | blocked |
| `S1-D2-001` | Dev 2 | T1.4 EffectDescriptor candidate | `REQ-SCHEMA-004` | D1-001, D1-003 | normalisation and cwd vectors | blocked |
| `S1-D2-002` | Dev 2 | T1.5 CapabilityGrant candidate | `REQ-SCHEMA-005` | D2-001 | missing-binding must-fail vectors | blocked |
| `S1-D2-003` | Dev 2 | T1.6 Receipt candidate | `REQ-SCHEMA-006` | D2-001, D2-002 | outcome/resource/uncertainty vectors | blocked |
| `S1-D3-001` | Dev 3 | T1.7 EventEnvelope candidate | `REQ-SCHEMA-007` | D1-002 | scope-conditional vectors | blocked |
| `S1-D3-002` | Dev 3 | T1.8 Artifact candidate | `REQ-SCHEMA-008` | D1-001, D1-002 | extensibility and immutability vectors | blocked |
| `S1-D3-003` | Dev 3 | T1.9 EvidenceClaim preservation | `REQ-SCHEMA-009` | D3-002 | invalidation must-fail vectors | blocked |
| `S1-D4-001` | Dev 4 | T0a disposable provider API probe | backlog-only `[B]` | boundary gate | `provider-notes.md`; no imported code | local-only; delete S4 |
| `S1-D4-002` | Dev 4 | T1.10 CorrectionRecord candidate | `REQ-SCHEMA-010` | D1-002, D3-001 | reason/scope vectors | blocked |
| `S1-D4-003` | Dev 4 | T1.11 Recording candidate | `REQ-SCHEMA-011` | D1-001, provider notes | completeness/digest vectors | blocked |
| `S1-D4-004` | Dev 4 | T1.12 Process contracts | `REQ-SCHEMA-012` | D3-001, D3-002 | finite-state and restart-resume property | blocked |
| `S1-LEAD-001` | Tech Lead | adjudicate four T0 candidate additions | all T1 rows | independent reconstruction | ADR/schema-review disposition | required before lock |
| `S1-GATE-001` | Independent engineer | reconstruct all four traces without author interview | backlog-only `[B]` | packet handoff | signed reconstruction or new GAP rows | required before lock |
| `S1-GATE-002` | Dev 1 + Dev 2 | prospectively time one manual reproduction each and record hands-on/elapsed time | backlog-only `[B]` | selected reproducible cases | two timed trace receipts | required for human baseline |
| `S1-PL-001` | Project Lead | verify branch protection and create baseline tag | `REQ-GOV-005` | real Git host/metadata | host setting evidence + annotated tag | external blocker |

Definition of done for a schema ticket: normative JSON Schema change, generated reader profile, shared valid/invalid vectors, semantic note, named test receipt, contract row updated to `covered`, and no draft schema used for durable recording.
