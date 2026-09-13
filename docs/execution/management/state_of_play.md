---
id: execution.management.state_of_play
class: execution
authority: descriptive
canonical_for:
  - current-orchestration-state
status: living
owner: repository-governance
version: "0.1.0"
last_verified: 2026-09-12
---

# State of play

Descriptive cache only. [Tasks](../main/tasks.md) owns leases and acceptance;
[spec DIR-1](../main/spec.md#dir-1-wave-1-rulings-and-replacement-corpus-quarantine)
owns Wave 1 decisions. No statement here grants authority.

**Snapshot binding:** inspected HEAD
`63d12d839ff334befa2ae64a07e5c80ed35ecb82`, branch
`feat/aether-framework-electroweak-canonical-agents`. The five requested local
commits are present; initial worktree was clean. This handoff relocates the
diagnostic tooling and synchronizes docs/knowledge, without product-code changes.

| Live working-file binding | Git blob |
|---|---|
| `main/tasks.md` | `4fa0d207fb2a3f2f29d8124a4e8e036759b5f569` |
| `main/spec.md` | `add9939a3c72e1616fbe3538f08c9392a93ce1aa` |
| `main/milestones.md` | `d010465eea63bf44898fb36ab7d734388da50f15` |
| `main/technical.md` | `77f741673923da5cdd62040883c6e464ffaf847a` |

Verify with `git hash-object docs/execution/main/{tasks,spec,milestones,technical}.md`.
Any mismatch invalidates this snapshot; derive state from the board. The director
charter's older current-assignment blob binding is stale; its standing role and
the explicit phase-transition dispatch informed this handoff.

## Live dispatch

| Owner | Row | State / dependency |
|---|---|---|
| A | T-134 | ACCEPTED component; session.py transferred to B |
| B | T-136 | ACCEPTED; canonical baseline pin unchanged |
| B | T-135 | READY; session.py and its named companion lease |
| A | T-131.6 | READY; candidate/evidence identity lease excludes B's files |
| C | T-133 | REOPENED; correction READY, acceptance explicitly withheld |
| C | T-132 | READY; justfile, collection-integrity test and CI files transferred |
| C | T-137 | READY; synthetic approval probe only, zero provider calls/USD |
| C + curator | T-51 | REOPENED/BLOCKED: T-133 reacceptance, independent curator and external sealed store |

C serializes its rows; A and B may start disjoint READY leases concurrently.
T-131 rows 4/6/7 remain outside the narrow T-134 acceptance. T-130's valid
instrument retains both controls and NOT_REPRODUCED on three write fixtures.
The moved `tools/diagnostics/write_landing_probe.py` still enters the shipped
product route; no benchmark adapter-import permission was added. Its terminal
instrument errors are not completion qualification. No historical write-failure
repair site or public port/schema change is attributed. T-26b waits for T-51;
T-26 remains UNFROZEN, T-27 unauthorized, RUN-12 zero provider calls/USD.

## Evidence and decisions

The isolated Python 3.12 review slice passed 123 tests in 10.428s (runner 11.241s),
covering baseline, carriers, event/schema vectors, row-7 replay, quarantine and
the moved write probe. The first system-Python attempt lacked cryptography and
was superseded by this correctly provisioned run. `just check` passed in 5.414s;
boundary, execution-truth and local-link checks also passed. These component
receipts do not accept the control instrument or a fresh corpus.

Independent synthetic counterexamples allow missing/unknown task IDs and accept
forged evaluation authority plus a FROZEN flag, copying both source and oracle
into the solver directory. Inventory is 7 required guards / 14 observed-unleased
/ 1 declarative, not 22 guarded paths. T-133 cannot be signed off on green helper
tests. Q-01 remains binding; old oracle repairs remain forbidden under RUN-08.
Replacement remains exactly 30 with strata 10/11/5/1/3. No holdout was exercised.
The former domain.md/system_composition.md paths no longer exist; current mapped
owners schemas.md, events.md, causal-state.md and runtime-execution.md were updated.

## Explicit outstanding boundaries

- No write-landing repair site attributed; Director rules after T-137 evidence.
- Private curator/store provisioning and actual fresh corpus availability are not
  established; metadata checks alone cannot close T-51.
- Accepted public schema scope is limited to DIR-D1's two kind/payload additions;
  no other port, preset, terminal-enum, threshold or paid authority is granted.
- External signed padded baseline pins, if found, require a migration decision.
- P6/P7 remain proposals behind control and T-129; no implementation lease.
- Existing documentation-size debt is not a reason to widen ceilings silently;
  no ceiling change or broad historical-document rewrite is included here.
