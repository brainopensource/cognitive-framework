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

Three folders. Law, roles, and how we work — in that order of authority.

| Folder | Holds | Authority |
|---|---|---|
| [`main/`](main/) | The five canonical execution documents | **Normative.** Wins every conflict. |
| [`guidelines/`](guidelines/) | Standing instructions per role | Advisory; the *ask*, never the law |
| [`management/`](management/) | How we develop with several AI agents | Advisory; process, not content |

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

Role-scoped and long-lived. They change when a mandate changes, not when work
changes. Rulings made under a charter are transferred into `main/` by the Senior.

## `management/` — how we work

| Document | Answers | Read when |
|---|---|---|
| [`development_philosophy.md`](management/development_philosophy.md) | Why the process is shaped this way | Once, then on process change |
| [`work_packet_protocol.md`](management/work_packet_protocol.md) | How a work slice is compiled and handed off | Compiling or receiving an assignment |
| [`roles_and_authority.md`](management/roles_and_authority.md) | Who decides what, and what escalates | When unsure whether to escalate |
| [`state_of_play.md`](management/state_of_play.md) | What is live right now | Start of every session |
| [`methodology_sources.md`](management/methodology_sources.md) | What we borrow from BMAD, Spec Kit, Agent Skills — and what we refuse | Evaluating an external methodology |

## The three planes

```text
CANONICAL TRUTH          durable, slow-changing, authoritative
docs/execution/main/     spec · technical · tasks · milestones · backlog
        |
        |  compiled down into one bounded slice
        v
ACTIVE ORCHESTRATION     disposable, regenerated, never cited as authority
docs/execution/management/   work packets · state of play
docs/execution/guidelines/   standing role instructions
        |
        |  produces
        v
EVIDENCE                 machine-readable receipts, commands, digests, costs
        |
        |  durable conclusions promoted back up
        v
CANONICAL TRUTH
```

A work packet is **generated, disposable and non-canonical**. When a packet and a
canonical document disagree, the canonical document wins and the packet is
regenerated. A packet is never the place to record a decision.

## Where a new agent starts

1. [`management/state_of_play.md`](management/state_of_play.md) — what is live.
2. Your own row in [`main/tasks.md`](main/tasks.md) — objective, lease, falsifier,
   stop condition.
3. A clause in [`main/spec.md`](main/spec.md) **only when your row cites one.**

A row that cannot be started without reading all five documents is a malformed
row. Report it rather than reading around it.

## Boundaries

- No sixth canonical document. Additional planes are generated and disposable.
- Law lives in [`main/spec.md`](main/spec.md); work lives in
  [`main/tasks.md`](main/tasks.md). Neither is restated elsewhere.
- Raw logs and receipts are not pasted into these documents. Conclusions are
  promoted; evidence stays in its own artifacts.
