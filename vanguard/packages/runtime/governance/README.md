# runtime/governance

Finite, declared, durable approval/release processes. Statically restricted to `domain`, `ports` and `kernel`; no model or agency dependency.

## State reduction

`ProcessDefinition` is declared data: a finite state set and at most one edge
for each `(state, event kind)` pair. `ProcessEngine` begins at `initialState`,
consumes ordered governance events addressed by `payload.processId`, and records
only declared transitions in `ProcessInstance.history`.

An `ApprovalRequested` event suspends the instance. Only the matching approved
`ApprovalResolved` event can release the suspension and take a declared edge;
other process events cannot advance it. `resume()` reads the governance ledger
and performs the same pure reduction from the beginning. It never replays an
Episode and this package has no model or agency dependency.
