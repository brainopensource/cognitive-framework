---
id: adr-0108-session-composition-and-analysis
adr: "0108"
class: decision
authority: binding-decision
canonical_for:
  - decision-0108-session-composition-and-analysis
status: living
owner: engineering-director
version: "1.0"
last_verified: 2026-09-13
decision_status: accepted
---

# ADR-0108 — D-2: session composition and analysis ownership

`HarnessSession` becomes an orchestrator consuming explicit, immutable collaborators assembled by `RuntimeBootstrap.build` and the existing wiring/`SessionPorts` boundary: index selection, revision handling and caller admission are injected dependencies, not lane-specific branches or a mutable global hook registry.
Each collaborator is supplied by its owning lane; bootstrap chooses implementations once for the composition identity, and callbacks that can emit events or perform effects remain behind authenticated dispatch and the sole writer rather than exposing arbitrary effectful hooks.
B makes one transitional session adaptation, C integrates the bootstrap assembly, and subsequent lane changes target their collaborators; the current exclusive-writer lease remains only during that bounded transition and no lane waits for wholesale decomposition of the 2,742-line file.
Python parsing and structural analysis leave `session.py` for the environment adapter's analysis boundary shared with `transaction.py`, whose preflight remains the owner of syntax validation before durable mutation under I-TXN.
Stub/vacuity detection is not transaction syntax validity: the adapter reports candidate-bound structural observations, the code pack/agency completion policy interprets them, and the exterior verifier still establishes behavioral success rather than allowing successful parsing to imply completion.
Completion-time analysis remains necessary for the exact submitted tree, including changes made outside the transaction path; reuse of preflight analysis is valid only for the same whole-candidate identity, and unreadable or unsupported analysis yields explicit unresolved evidence.
I-TXN owns all-or-nothing mutation and rollback, ADR-0060/I-7 own domain-neutral kernel/episode execution, and N-06 plus the hexagonal dependency direction keep process execution in adapters/tooling and policy outside adapters.
This ruling authorizes extraction within DIR-3, not a second loop, public plugin platform, change to containment, or new freeze prerequisite, and it claims no implementation has landed.
