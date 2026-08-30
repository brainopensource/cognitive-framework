# Block F — Legacy Loss Audit

## Scope and method

- Reconstruction HEAD: `d8abc8c35e9022029a5badc4ef4027fa181ab1d8`
- AS_BUILT analysis subject: `9fd444674bf3a97f2673ff36a5f5928ef046c574`
- Documentation-like sources inventoried: **375**
- Claim units reviewed: **5487**
- Candidate architecture and ownership were frozen before legacy comparison; legacy paths did not define the taxonomy.
- `docs/candidate-docs/product/frontend/` was excluded as unrelated user-owned work and was not modified or absorbed.
- Concurrent/user-owned changes were recorded and excluded: `package-lock.json, package.json, vanguard/clients/cli/src/commands/agent.ts, vanguard/clients/cli/src/commands/artifact.ts, vanguard/clients/cli/src/commands/event.ts, vanguard/clients/cli/src/commands/index.ts, vanguard/clients/cli/src/composition/parse-cli.ts, vanguard/clients/cli/src/main.tsx, vanguard/clients/cli/src/output.ts, vanguard/clients/client-core/src/contract/types.ts, vanguard/clients/client/src/signers/operator-signer.ts, vanguard/clients/client/src/signers/web-signer.ts, vanguard/clients/client/src/transports/http.ts, vanguard/clients/client/src/transports/socket.ts, vanguard/clients/client/tsconfig.json, vanguard/clients/cli/src/commands/approve.ts, vanguard/clients/cli/src/commands/daemon.ts, vanguard/clients/cli/src/commands/doctor.ts, vanguard/clients/cli/src/commands/run.ts, vanguard/clients/cli/src/commands/workflow.ts, vanguard/clients/cli/test/cli-vertical-slice.test.ts, vanguard/clients/client/src/index.ts, vanguard/clients/client/test/, vanguard/clients/projections/`.

## Classification counts

- `ALREADY_CAPTURED`: 697
- `CURRENT_DECISION`: 947
- `CURRENT_REQUIREMENT`: 136
- `FUTURE_REQUIREMENT`: 76
- `THEORY`: 963
- `OBSOLETE`: 2340
- `CONTRADICTED_BY_CODE`: 321
- `UNRESOLVED`: 7

- Unique claims absorbed: **1**
- Critical unresolved knowledge-loss findings: **0**

## Knowledge recovered

- The stable backlog contract is now represented by a concise linked statement in `execution.active`; mutable package tables remain owned by the active authority.
- Accepted decision provenance, current normative requirements, and future execution requirements remain linkable without copying historical prose.

## Obsolete and contradicted material

- Superseded reviews, proposals, status narratives, and speculative benchmark plans remain in place and are recorded in `legacy-obsolete.jsonl`.
- Historical layer/layout assertions that conflict with the verified Python package lattice are explicit `CONTRADICTED_BY_CODE` findings; they do not cancel TARGET requirements.

## Block F gate

`BLOCK F EXIT GATE: PASS`

The duplicate accepted-labelled ADR-0106, its unindexed measurement authorization, and the related execution-status conflicts remain explicitly unresolved for Block H.
