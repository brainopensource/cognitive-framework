---
id: execution.readme
class: navigation
authority: current-decision-navigation
canonical_for:
  - execution-navigation
status: living
owner: repository-governance
version: "0.1.0"
last_verified: 2026-09-12
---

# Execution

Three folders, four information layers. Canonical law, durable operating policy,
ephemeral work packets, and retained evidence stay distinct.

| Folder | Holds | Authority |
|---|---|---|
| [`main/`](main/) | The five canonical execution documents | **Normative.** Wins every conflict. |
| [`guidelines/`](guidelines/) | Reviewed role and dispatch prompt templates | Advisory; the *ask*, never the law |
| [`management/`](management/) | Durable multi-agent operating method and a descriptive snapshot | Advisory; process, never task authority |

## `main/` — canonical truth

| Document | Answers |
|---|---|
| [`spec.md`](main/spec.md) | What must be true — normative clauses, invariants, delta contracts |
| [`technical.md`](main/technical.md) | How — algorithms, recipes, operational handbook |
| [`tasks.md`](main/tasks.md) | What is authorized and what is done — flat work tree, leases, receipts |
| [`milestones.md`](main/milestones.md) | What is accepted — TARGET gates and dispositions |
| [`backlog.md`](main/backlog.md) | What is next — package lifecycle |

These five remain the only canonical execution documents. Nothing outside `main/`
creates law, a task row, or a status.

## `guidelines/` — who is asked to do what

| Document | Role |
|---|---|
| [Director charter](guidelines/task_instructions_and_prompts_DIRECTOR.md) | Architecture, invariants, public contracts, sequencing, genuine forks |
| [Developer instructions](guidelines/task_instructions_and_prompts_DEVS.md) | Senior Manager plus Developers A/B/C — assignments, leases, review routing, management loop |

The standing portions are role-scoped and durable. A current-assignment overlay
is a descriptive cache and MUST bind the task-board blob from which it was
compiled. Rulings made under a charter are transferred into `main/` by the Senior.

## `management/` — how we work

| Document | Answers | Read when |
|---|---|---|
| [`development_philosophy.md`](management/development_philosophy.md) | Why the process is shaped this way | Once, then on process change |
| [`work_packet_protocol.md`](management/work_packet_protocol.md) | How a work slice is compiled and handed off | Compiling or receiving an assignment |
| [`roles_and_authority.md`](management/roles_and_authority.md) | Who decides what, and what escalates | When unsure whether to escalate |
| [`state_of_play.md`](management/state_of_play.md) | What is live right now | Start of every session |
| [`methodology_sources.md`](management/methodology_sources.md) | What we borrow from BMAD, Spec Kit, Agent Skills — and what we refuse | Evaluating an external methodology |

## The four layers

```text
1. CANONICAL AUTHORITY   main/{spec,tasks,milestones,technical,backlog}.md
        |                durable law, authorization and accepted state
        v
2. OPERATING POLICY      management/ + guidelines/
        |                durable but advisory roles, methods and prompt templates
        v
3. ACTIVE WORK PACKET    compiled into agent context or an ephemeral store
        |                generated, subject-bound, disposable and never committed
        v
4. EVIDENCE              receipts, commands, digests, timings and costs
        |                retained outside the packet; conclusions promoted upward
        +----------------------------------------------------> 1
```

Management documents and prompt templates are not disposable: they are reviewed
operating policy. A work packet is **generated, disposable and non-canonical**.
When a packet and a canonical document disagree, the canonical document wins and
the packet is regenerated. A packet is never the place to record a decision.

## Where a new agent starts

1. Verify repository HEAD and LDA identity. Stale generated context is rejected.
2. Read [`management/state_of_play.md`](management/state_of_play.md) only if its
   recorded task-board blob matches the current `main/tasks.md` blob.
3. Read your own row in [`main/tasks.md`](main/tasks.md) — objective, lease,
   falsifier and stop condition.
4. Admit the generated packet for that row: verify subject, prerequisites, lease
   collisions and cited clause digests before the first write and after resume.
5. Read a clause in [`main/spec.md`](main/spec.md) **only when the row cites one.**

A row that cannot be started without reading all five documents is a malformed
row. Report it rather than reading around it.

## Boundaries

- No sixth canonical document. Operating-policy support is durable and advisory;
  only active work packets are generated and disposable.
- The files listed in this README are the complete permitted execution-support
  inventory. New management or guideline files require a CEO-approved structural
  change; scratch plans, reviews and session summaries remain forbidden.
- Law lives in [`main/spec.md`](main/spec.md); work lives in
  [`main/tasks.md`](main/tasks.md). Neither is restated elsewhere.
- `state_of_play.md` is a fail-closed cache, not a second status board. If stale,
  skip it and derive current state from `tasks.md`.
- Work packets never live under `docs/` and are never committed.
- Raw logs and receipts are not pasted into these documents. Conclusions are
  promoted; evidence stays in its own artifacts.
- A documentation topology move is isolated from semantic edits. Its receipt
  compares old and new blobs after normalized link-depth rewrites; a commit that
  mixes new law, task changes and path migration cannot claim “content untouched.”

## Document lifecycle

- `living` means an owned document is in the active working set and has a defined
  verification cadence; it does not merely mean “not deleted.”
- `reference` is useful context that is not required for routine work.
- `historical` preserves evidence and cannot authorize current work.
- `proposal` is the single spelling for unaccepted design. `proposed` is legacy
  vocabulary to be normalized without changing the proposal's substance.
- A descriptive finding receives evidence, a captured subject, an owner and a
  disposition deadline. It is then promoted, rejected or removed; it cannot age
  into a shadow backlog.
