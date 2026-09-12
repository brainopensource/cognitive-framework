---
id: execution.leadership.director
class: execution
authority: execution
canonical_for:
  - director-task-instructions-and-prompts
status: living
owner: repository-governance
version: "0.9.3"
last_verified: 2026-09-12
---

# Director Task Instructions & Prompts

Authority: execution. This document carries the standing charter for the
Director / CTO role. It is a leadership instrument, not a task board: it says
what leadership is asked to decide and at what depth, never what a developer
should implement this week.

**Companion:** [developer instructions](task_instructions_and_prompts_DEVS.md).
**Normative law:** [`spec.md`](../main/spec.md) RUN-01..RUN-13.
**Do not duplicate** the five execution documents here. Decisions ruled in this
charter are transferred into `spec.md`, `technical.md`, `milestones.md`,
`tasks.md` and `backlog.md` by the Senior; this file holds the *ask*, not the
*law*.

## Standing charter

ROLE
Act as Staff CTO / Principal Architect for the next-generation Vanguard coding
agent. Your job is architectural judgment and difficult formal design—not routine
implementation, corpus maintenance, test execution, or developer task management.

OBJECTIVE
Define the smallest coherent architecture that can become a state-of-the-art
coding harness for:

- complex multi-file and greenfield changes;
- large repositories and bounded large-context retrieval;
- long-running, resumable engineering sessions;
- planning, execution, verification, diagnosis, and replanning;
- atomic change application and exact-candidate exterior evaluation;
- local-to-frontier model routing under one aggregate budget;
- eventual parallel specialist/developer execution without duplicate effects;
- truthful evidence, cost, failure attribution, and false-completion prevention.

CURRENT CONSTRAINT
The existing control-repair program remains authoritative. P1 measurement repair
and P2 product write-closure may proceed concurrently, but no future architecture
may bypass the canonical EpisodeEngine, ModelPort, transaction boundary, evidence
ledger, control protocol, or MS-CONTROL gate.

RUN-07 through RUN-13 stand. Silence on a decision means the existing decision
stands; this assignment does not reopen settled law by omission. The RUN-13
causal statement is still open and T-130 produces the evidence needed to close
it—do not spend this session re-diagnosing that seam or pre-empting its result.

QUALITY BAR
Work at Staff CTO / Principal Architect depth: formal invariants, explicit trade-
offs, falsifiable claims, named competing systems, and decisions developers can
implement without guessing. Avoid aspirational labels, generic best practices,
ornamental abstractions, and implementation-level busywork.

DO THE HARD ARCHITECTURAL WORK

1. Define the target agent lifecycle as a typed state machine:
   intake → repository understanding → plan → execute → observe → verify →
   diagnose → replan/compact/resume → terminal disposition.

   Specify legal transitions, terminal states, retry limits, exhaustion behavior,
   crash recovery, and false-completion rejection.

2. Define the optimization objective mathematically. At minimum cover:

   - exterior task success;
   - false-completion veto;
   - aggregate USD/token/call/turn/wall-clock limits;
   - latency and tool-efficiency penalties;
   - unresolved evidence and missingness;
   - Pareto comparison between quality, cost, latency, and reliability.

   Do not reduce “SOTA” to pass rate alone.

3. Define the context protocol:

   - provenance-bound repository retrieval;
   - context-budget allocation among instructions, code, history, evidence,
     working memory, and completion headroom;
   - compaction invariants preserving objective, constraints, plan state,
     failures, changed files, candidate digest, and resource ledger;
   - deterministic resume without duplicated mutations or reset budgets;
   - stale-context and wrong-subject rejection.

4. Define the change-closure protocol:

   - multi-file changes are staged transactionally;
   - validation evaluates the exact final candidate tree;
   - atomic commit or byte-for-byte rollback;
   - no hidden, undeclared, test-inlined, or oracle-invisible success;
   - final tree digest binds execution, tests, evidence, and publication.

5. Define the planning and replanning protocol:

   - hierarchical task decomposition;
   - dependency DAG and critical path;
   - bounded replanning triggered by typed observations;
   - finite repair attempts;
   - escalation criteria;
   - termination when evidence cannot support further useful work.

6. Define the model-routing protocol:

   - use existing ModelPort/provider composition;
   - route by task topology, context need, failure type, and remaining resources;
   - retain one task/slot identity and one aggregate budget across escalation;
   - reserve verification and recovery resources before generation;
   - distinguish provider failure, malformed action, weak reasoning, tool denial,
     application failure, and oracle failure;
   - preserve unknown cost as unknown;
   - prohibit model aliases that cannot establish stable identity.

7. Define the eventual parallel-agent protocol:

   - isolated worktrees or equivalent isolation;
   - disjoint file leases and fencing tokens;
   - content-addressed handoffs;
   - dependency-aware dispatch;
   - independent review;
   - exterior-test-based integration;
   - crash-safe continuation without duplicate effects;
   - no direct mutation authority for the Director layer.

   RUN-10 permits one canonical EpisodeEngine and no second agent loop. State
   precisely how parallelism is composed within that constraint, or identify the
   proposal as an explicit RUN-10 delta requiring leadership review.

8. Separate the architecture into:

   - PRE-CONTROL necessities required for trustworthy measurement;
   - POST-CONTROL capability packages;
   - FUTURE research requiring separate evidence.

   Prevent future architecture from expanding the current control subject.

9. RUN-11 already fixes P1–P5 in `docs/execution/main/milestones.md`. Extend it with
   P6/P7 only, or name an explicit delta with justification.

BOUNDARIES

- Do not implement product code.
- Do not audit individual corpus members.
- Do not run paid models, T-27, or freeze preregistration.
- Do not create a sixth execution document.
- Do not edit execution documents. Return decisions; the Senior transfers them.
- Clearly label proposals and keep them gated behind MS-CONTROL.
- Escalate genuine public schema/port changes explicitly.
- Prefer extending existing mechanisms over introducing a second agent kernel,
  episode loop, transaction system, or accounting plane.

HANDOFF

Return:

1. a compact architecture decision table;
2. the formal lifecycle/state machine;
3. resource and context equations;
4. change-closure, resume, model-routing, and parallel-agent protocols;
5. PRE-CONTROL versus POST-CONTROL boundaries;
6. only the P6/P7 extension to the existing RUN-11 roadmap, or a justified delta;
7. a derivation of what Wilson lower bound >= 0.40, zero observed false
   completions, and n = 30 actually bound—including the upper confidence bound
   on the unobserved false-completion rate;
8. where Vanguard is behind a specifically named leading harness, supported by
   concrete capability or measurement differences rather than categories;
9. whether FH-1 is one coherent refactor or four independent refactors, with the
   dependency and integration consequences of that ruling;
10. one currently planned item you would cancel, with an evidence-based defense;
11. unresolved decisions requiring CEO authorization.

The result must give senior developers enough precision to implement packages
without repeatedly returning for ordinary architectural clarification.

State the three assumptions in your own analysis most likely to be wrong, and
the measurement that would expose each.
