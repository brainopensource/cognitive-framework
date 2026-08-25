---
id: active-sprint-board
class: execution
authority: execution
canonical_for:
  - active-sprint-tasks
  - current-milestone-gates
status: living
owner: tech-lead
version: "0.7.0"
last_verified: 2026-08-25
supersedes: []
superseded_by: null
---

# Active Sprint Board — Product M-4 and M-5 Preparation

[`README.md`](../../README.md) is navigation; [`SPEC.md`](../SPEC.md) and
[`01_law/`](../01_law/) are law; accepted ADRs record decisions. This is the sole living work board.

## 1. Current Decision

ADR-0094 separates product viability from optional adversarial assurance:

- **M-4 / RF-95 is active:** prove a useful coding agent through the canonical runtime with a live
  model, real tools, durable WAL, and fresh-process reconstruction.
- **RF-85 is retained but non-blocking:** the original nine-row hermetic/isolated-evaluator audit is
  an optional assurance certification and currently claims zero completed evidence rows.
- **M7-01 may run in parallel:** measurement only; no scheduler or concurrency.
- **M-5 remains locked until RF-95 closes.** Preparation may define the pack, task, oracle, and RED
  tests, but may not change the frozen substrate or claim generality.
- M-6 implementation, M-7 implementation, M-8, and later horizons remain locked.

The repository baseline on 2026-08-25 is 1,327 Python tests passing with three skips. Architecture,
TCB, secrets, domain-blindness, isolation, event coverage, RF-ID, duplication, RF-86, link, and stale
path gates pass. Node is installed but locked workspace dependencies still require `npm ci` before
TypeScript gates are qualified.

## 2. Architectural Boundary

The product-first pivot does not authorize a rewrite. These boundaries remain mandatory:

```text
clients/products -> runtime -> agency -> kernel
                         |          |
                    adapters <- ports <- domain
```

- Clients own UX, commands, streaming display, approvals, and session selection.
- Packs own coding/formal/research prompts, tools, policies, and domain semantics.
- Runtime owns composition, adapter bootstrap, profiles, lifecycle, sessions, persistence, and replay.
- Agency owns the domain-neutral sequential turn mechanism and context lifecycle.
- Kernel owns only generic effect authority, budgets, selectors, and provenance.
- Adapters implement models, workspace tools, stores, evaluators, indexes, sandboxing, and protocols.
- The append-only ledger and immutable artifacts are canonical; indexes, caches, maps, and summaries
  are rebuildable projections.

Security mechanisms may be optional by profile, but no profile may disguise its assurance level in
`D_R`. `product` may use host execution and no evaluator. `hermetic` keeps the existing containment,
preregistration, signature, and promotion rules. No coding or formal semantics enter the kernel.

## 3. Active Lane A — Finish M-4 / RF-95

### M4-01 — Product execution profile and durable bootstrap

**State: IMPLEMENTED; verification pending full suite.**

- Add explicit `product` profile: in-place host workspace, explicit approval policy, SQLite-WAL,
  optional evaluator, recorded/non-promotional assurance.
- Make the bootstrap honor `persistence_mode=sqlite-wal` with a file-backed store by default.
- Default the generic CLI entrypoint to `product`; keep `local`, `sandboxed`, and `hermetic` explicit.
- RF-95 guards that product use does not require containment/evaluator infrastructure and never
  silently falls back to memory persistence.

### M4-02 — Make the coding CLI operable

Build the shortest useful vertical slice rather than more framework abstractions:

1. Install Node dependencies and qualify CLI typecheck/tests.
2. Expose provider/model, workspace, run id, event-store path, turn/effect/token budgets, and approval
   mode through the existing client request contract.
3. Stream model/tool/receipt/terminal events from the existing runtime event fan-out.
4. Present reviewable diffs and approval prompts; do not duplicate authority logic in TypeScript.
5. Add `vg resume <run-id>` over the existing WAL/reconstruction path.

Exit: a developer can start, observe, approve, interrupt, and resume a product coding session from
the CLI without constructing Python objects manually.

### M4-03 — Close tool-loop gaps

Exercise `vg-code-default` against a small existing repository and fix only defects exposed by the
run. The minimum product tool surface is `fs.read`, `fs.search`, `patch.apply`, and allowlisted
`proc.exec`. Improve prompts, schemas, receipts, diff ergonomics, and context compaction in the pack,
clients, or adapters—not the kernel.

Exit: the agent inspects before editing, applies a valid change, runs the preregistered verification
command, reacts to failure, and stops after success within declared budgets.

### M4-04 — Execute RF-95

Freeze a non-trivial coding task and verifier before the run. Execute exactly one candidate with:

- a live non-fake/non-cassette provider;
- `vg-code-default` through canonical compose/activate/`Runtime.run_composed`;
- the `product` profile bound into `D_R`;
- at least one repository observation, file mutation, and verification process effect;
- a non-empty before/after diff and passing verifier receipt;
- file-backed SQLite-WAL and complete terminal trajectory;
- a fresh process reopening the ledger and reconstructing the same terminal state.

No alternate driver, stitched trace, manual event repair, or post-hoc task change qualifies. An
independent reviewer confirms the evidence and the Engineering Director closes M-4. RF-85 is not
implicitly satisfied.

## 4. Active Lane B — M7-01 Measurement

ADR-0092 authorizes a sequential effect-log measurement in parallel with M-4. Construct effect
references from actual `EffectStarted` records with resolved resources—not static manifests. Capture
selector, sink, idempotency key, wall/model/tool timing, and cache-hit rate over a fixed-seed workload.

Allowed: capture, analysis, deterministic fixtures, reproducible runner. Forbidden: scheduler,
concurrency, claim TTL, leasing protocol, worker pool, or topology engine. Below 30% useful
independence, the default decision is to cancel M-7. At or above 30%, a successor ADR is still needed.

## 5. M-5 Preparation — Formal Pack #2

Preparation starts now; implementation starts only after RF-95 closes.

### M5-P1 — Choose the falsification task

Use a deterministic, materially non-coding domain. Preferred first slice: structured arithmetic or
SMT witness production with an independent checker. The task must require model reasoning and tool
use, produce a typed witness, and admit a deterministic pass/fail oracle.

### M5-P2 — Freeze the pack boundary

The new pack may add:

- `packs/formal-default/` manifest, prompts, schemas, and policies;
- formal environment and checker/evaluator adapters behind existing ports;
- typed witness artifacts and pack-owned fixtures;
- client selection and result rendering.

It may not change semantics under `vanguard/packages/{domain,ports,kernel,runtime,agency/episode}`
during the RF-86 proof interval. If it cannot be expressed through the existing ports and composition,
M-5 fails and returns an abstraction finding; RF-86 is never weakened.

### M5-P3 — RED contract before implementation

Before opening M-5, add tests proving that code and formal packs:

- compose through the same API and activation lifecycle;
- use the same episode mechanism, effect dispatch, budgets, WAL, and trajectory contracts;
- differ only in pack/adapters/artifacts/client presentation;
- produce independently checkable domain outputs;
- leave all RF-86 frozen paths unchanged.

### M5 exit

One real formal task produces a valid witness through the unchanged substrate and deterministic
checker. A failure requiring substrate semantics is valuable falsification evidence, not permission
to patch the kernel until the claim passes.

## 6. Explicit Non-Scope

- Do not implement `agent.spawn` before M-5 closes.
- Do not implement concurrency or topologies from M7-01 data without a successor ADR.
- Do not build advanced memory, broad MCP support, swarms, learned skills, or metacognition now.
- Do not delete RF-85 assurance code merely because it is no longer the product gate.
- Do not add conceptual mirror packages or a second execution authority.

## 7. Verification

```bash
python3 -m unittest discover -s test -t .
bash ci/rf86_gate.sh M-5-BASE
python3 tools/linters/check_boundaries.py
python3 tools/linters/check_tcb_budget.py
python3 tools/linters/scan_secrets.py
python3 tools/linters/check_domain_blindness.py
python3 tools/linters/check_isolation_policy.py
python3 tools/linters/check_event_coverage.py
python3 tools/linters/check_falsifier_ids.py
python3 tools/linters/check_duplication.py --enforce
python3 tools/linters/check_markdown_links.py
python3 tools/linters/check_stale_paths.py
npm ci
npm run typecheck --workspaces --if-present
npm test --workspaces --if-present
```
