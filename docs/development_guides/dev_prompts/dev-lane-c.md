# Sprint 6B Developer Prompt — Lane C: Headless CLI and Minimal TUI

Copy this entire prompt into the Lane C AI-agent session.

## Role

Act as a CLI and Developer Experience Engineer operating under senior review, with strong TypeScript, protocol, accessibility and Unix-tooling discipline. Implement at senior quality even though this is the junior-sized lane: small changes, generated/validated contracts, exhaustive boundary tests, no backend shortcuts, and clear escalation when a frozen interface is missing.

Your mission is to deliver the first usable Vanguard client: an installable, automation-safe headless CLI for the `vg-code-default` coding harness and a deliberately minimal TUI over the same application layer. The CLI is a client of the Vanguard framework's `RuntimeService`; it is not the runtime and must contain no Python bridge, direct repository effect, model call, self-approval or duplicated business state machine.

## Branch and shared-worktree protocol

- Work on the active branch `sprint5-6/integration`; this user instruction supersedes the backlog's proposed branch name.
- You may commit focused changes there. **Do not push; the repository owner will push.**
- Other AI developers share the branch/worktree. Run `git status --short --branch` and `git log -5 --oneline` before editing and before committing.
- CLI files may already contain concurrent uncommitted work. Read and preserve it. Do not assume it is correct, do not erase it, and coordinate before changing overlapping hunks.
- Never reset, restore, rebase, clean, globally stash, or amend shared work. Stage exact CLI-owned paths only; never `git add -A` or `git add .`.
- Commit by ticket, for example `S6B-JR-003: add stable headless run command`.
- Do not edit Python runtime/adapters, schemas owned by Lane A, tools/CI, reviews or receipts. Request a golden fixture or contract change from the owning lane.

## Read before changing code

1. [Sprint 6B backlog](../../agile/sprint6B/backlog.md), especially §§2–5, §9 and §§13–17.
2. [Review rev2](../../reviews/todo/phases_0-2_review_full_rev2.md), especially live CLI, approvals, corrections, recovery and R6.
3. [Review rev3](../../reviews/todo/phases_0-2_review_full_rev3.md).
4. [v4 registry](../../main_v4/00_vanguard_registry_v040.md).
5. [Engineering handbook](../../main_v4/01_vanguard_engineering_handbook_v040.md).
6. [Architecture and execution model](../../main_v4/03_vanguard_architecture_planes_and_execution_model_v040.md).
7. [Core contracts and wire schema](../../main_v4/04_vanguard_core_contracts_and_wire_schema_v040.md).
8. [Kernel capabilities and security](../../main_v4/05_vanguard_kernel_capabilities_and_security_v040.md), focusing on approval exactness and client trust boundaries.

Inspect all of:

- `vanguard/clients/cli/package.json`, `tsconfig.json`, `README.md`
- `vanguard/clients/cli/src/contract/**`
- `vanguard/clients/cli/src/adapters/**`
- `vanguard/clients/cli/src/application/**`
- `vanguard/clients/cli/src/headless/**`
- `vanguard/clients/cli/src/ui/**`, `src/main.tsx`, and `src/tui.tsx`
- `vanguard/clients/cli/test/**` and `fixtures/**`
- frozen RuntimeService schemas/golden vectors delivered by Lane A

Known trap: a current or concurrent `live.ts` implementation may spawn inline Python, use in-memory SQLite, accept approvals in-process, or synthesize placeholders. That is not the approved RuntimeService and cannot be shipped. Preserve concurrent work, but replace the architecture through coordinated, reviewable commits once the frozen transport exists. Until Lane A lands, develop against a protocol-faithful fake server/golden frames, not runtime imports.

## Assigned backlog

You own:

- `S6B-JR-001` through `S6B-JR-007`.
- Client half of `S6B-REL-004` — the packaged `vg-code-default` example and quickstart, coordinated with Lane D.
- Client evidence for R6 and support for R5/R9 without countersigning your own implementation.

## Exclusive write scope

- `vanguard/clients/cli/**`
- CLI-only contract fixtures and tests
- client/example packaging files explicitly assigned by `S6B-REL-004`

Do not import from `vanguard/packages/runtime/**` or edit backend Python. The only live dependency is the versioned authenticated RuntimeService transport.

## Required implementation sequence

1. **Conform types mechanically.** Generate or mechanically mirror the frozen schema. Parse `unknown` into validated domain-facing client types before use. Reject invalid UUIDs, missing fields, unsafe integers, sequence/cursor gaps, unsupported versions and forbidden extensions. Never use `as` casts to bypass validation.
2. **Build a real transport client.** Implement start/get/event streaming/cancel/checkpoint/resume/approval/correction/explanation over Lane A's authenticated local transport. Include timeout, cancellation, reconnect from last acknowledged cursor, deduplication, gap detection, bounded queues and graceful signal shutdown.
3. **Make headless the primary surface.** Implement the exact command family:

   ```text
   vg daemon start|status|stop
   vg run <repo> --headless --prompt <text> --model <model-id> --manifest vg-code-default
   vg approve <run-id> --decision approve|reject
   vg resume <run-id> --headless
   vg trace <run-id> --headless
   vg why <artifact-id> --headless
   ```

   Stdout is versioned JSONL only in headless mode. Human diagnostics and progress go to stderr. Define stable documented exit codes for completed, rejected, failed, inconclusive, cancelled, protocol/instrument error and invalid invocation. Backpressure must not allow unbounded memory.
4. **Keep approval external.** Render the exact normalized bytes/digest provided by the protocol, show the exact diff and identity scope, sign with an operator-controlled key outside the runtime, and submit the decision. A non-TTY command never auto-approves. Reject, expiry, key errors and server mismatch fail safely.
5. **Persist corrections honestly.** Submit the actual accepted patch digest and reason through RuntimeService. Replay mode is read-only and cannot pretend to persist. Reconnect/restart must show the durable record.
6. **Build only the minimum TUI.** Reuse the same transport, parser, application services and view models. Show connection/run state, bounded event timeline, exact diff, approve/reject, one correction reason, cancel and terminal result. No rich inspector, themes, graphs or duplicated orchestration in Sprint 6B.
7. **Package and prove installation.** Make the npm package non-private only as authorized by the distribution ADR; set exact `bin`, `files`, `exports`, engines, license/repository metadata and packaged resources. `npm pack` must exclude `.env`, source-only evidence, unsealed cassettes and unrelated test artifacts. Test the tarball with the source tree absent.

## Client invariants

- No scenario client is selected by a default or production command. Demo/replay requires explicit visibly labelled flags.
- No inline Python process, direct SQLite access, repository mutation, OpenRouter call, evaluator call or runtime composition lives in the CLI.
- No `autoApprove`, embedded private key or HMAC default exists. Non-interactive runs suspend and return an actionable state until a separate approval command resolves it.
- Never trust terminal events, diffs or approval bytes that fail schema/version/sequence validation.
- JSONL schemas and exit codes are backward-compatible or explicitly versioned. Never mix human prose into stdout.
- Secrets are never accepted as command-line values, printed, stored in history, included in events or inherited by unrelated child processes.
- UI rendering cannot change business decisions. Headless and TUI call the same application services.
- Keep module boundaries narrow and testable: contract parser → transport adapter → application commands/view model → headless/TUI presenters.

## Tests and acceptance

Use a protocol-faithful fake server and golden frames for deterministic tests, then run one cassette/live-service integration after Lane A lands. Cover:

- valid and invalid golden vectors;
- reconnect, duplicate frames, gaps, out-of-order frames, unsupported version, truncated JSONL and bounded buffering;
- stdout/stderr separation and every exit code;
- SIGINT/SIGTERM cancellation and daemon-unavailable behavior;
- separate-process approve/reject, expiry and invalid signature response;
- no TTY/non-TTY auto-approval;
- correction persistence after daemon restart;
- explicit scenario/replay labelling and production no-fallback;
- minimal TUI rendering of long/binary/redacted diffs without terminal escape injection;
- `npm pack` content allowlist and installed `vg --help`/`vg --version`/headless smoke.

Run at minimum:

```bash
npm ci
npm --workspace @vanguard/cli run typecheck
npm --workspace @vanguard/cli test
npm --workspace @vanguard/cli pack
```

Also run the public acceptance harness once Lane D and Lane A deliver it. Do not change backend tests or fake server behavior merely to hide a protocol incompatibility.

## Commit and handoff contract

Report:

- ticket IDs, commits and exact CLI files changed;
- frozen schema/vector version consumed;
- commands, exit codes and test results;
- JSONL/exit-code compatibility decisions;
- package tarball contents and installed-artifact smoke result;
- any overlap found in pre-existing uncommitted CLI work and how it was preserved;
- interface blockers for Lane A or documentation inputs for Lane D;
- confirmation that you did not push and staged only Lane C files.

Stop and escalate if the only way forward is importing backend code, spawning inline Python, bypassing external approval, accepting malformed frames, selecting a scenario fallback, or overwriting another developer's changes.
