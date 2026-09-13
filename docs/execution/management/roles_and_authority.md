---
id: execution.management.roles
class: standard
authority: advisory
canonical_for:
  - multi-agent-roles-and-authority
status: living
owner: repository-governance
version: "0.1.0"
last_verified: 2026-09-12
---

# Roles and authority

Who decides what. The purpose of this document is to make interruption rare:
each role holds enough standing authority to continue without asking.

## The roles

| Role | Owns | Never does |
|---|---|---|
| **CEO** | Outcomes, priorities, risk tolerance, spending | Routine technical decisions |
| **Director / CTO** | Architecture, invariants, public contracts, sequencing, statistical meaning, genuine forks | Task rows, leases, status maintenance, approving edits |
| **Senior Engineering Manager** | Packet compilation, leases, coordination, ordinary review, integration, task truth | Inventing architecture |
| **Developers A/B/C** | Implementation inside a disjoint lease and accepted authority | Widening a lease to fit a plan |
| **Independent reviewer** | Rerunning falsifiers and accepting or rejecting the exact subject | Reviewing their own implementation |

## The coupling failure

Most lost time comes from one role doing another's job. The observed pattern:
the Director doing architecture *and* task routing *and* review *and* status
maintenance *and* permission granting, while the developer waits on decisions an
accepted lease already implied.

Separating them is the whole point:

- The Director does not approve every edit.
- The developer does not invent architecture.
- Strategic review and ordinary code review are **different gates**. Conflating
  them is what turns a fortnightly cadence back into a daily one.
- The developer has authority to repair within the diagnosed component. A role
  accountable for an outcome without standing authority to reach it will
  escalate constantly, correctly, and fatally to the cadence.

## Escalation triggers — the complete list

A developer with a READY row and a valid lease continues without review until
exactly one of these occurs:

1. a public interface or schema must change;
2. the assigned architectural invariant cannot be preserved;
3. authority or budget must expand;
4. another lease must be touched;
5. a required falsifier would have to be weakened;
6. three bounded repair cycles fail.

Everything else belongs to the developer and the Senior.

**The value of this list is entirely in what it excludes.** Each addition costs a
fortnight of autonomy, so additions are a CEO decision and should be rare.

## Escalations reserved to the CEO

- public port or schema changes;
- control thresholds or holdout-policy changes;
- product identity or preset changes;
- additional paid authority;
- an architectural fork the Director could not resolve;
- a developer blocked after three bounded repair cycles.

## Review independence

Independence is evaluated for the exact change and subject, not granted by a role
label. Concretely:

- an author never accepts their own implementation;
- a reviewer who designed, directed or supplied the material repair is not
  independent of that repair;
- reviewing an earlier subject does not by itself destroy independence for a new
  subject, but the earlier receipt cannot be reused as acceptance;
- model diversity is useful but insufficient: acceptance combines authorship
  separation with evidence from an independently rerunnable falsifier;
- when available reviewers share likely model failure modes, adversarial and
  mutation controls carry more weight than review prose. See
  [`development_philosophy.md`](development_philosophy.md) §6.

The Senior records the independence basis in the handoff: author, reviewer,
subject, contribution to the repair, and which evidence the reviewer reproduced.

## Parallelism is capped by lease surface, not by agent count

Two agents editing one file costs a day; everything else costs minutes. So the
binding constraint on how many agents can work at once is how cleanly ownership
divides.

When one stream owns several unrelated surfaces, its work serializes no matter
how many agents exist. Redrawing ownership is therefore a capacity decision, and
it belongs to the CEO with the Senior — not to whoever is holding the bottleneck.

Adding another agent without a disjoint lease creates coordination, not capacity.
Before dispatch, the Senior publishes the lease graph and identifies its critical
path. Parallel work is admitted only where write surfaces and acceptance authority
are both disjoint.
