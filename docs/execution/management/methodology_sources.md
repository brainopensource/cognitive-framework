---
id: execution.management.methodology_sources
class: reference
authority: advisory
canonical_for:
  - external-methodology-adoption
status: living
owner: repository-governance
version: "0.1.0"
last_verified: 2026-09-12
---

# External methodology sources

What we borrow, and what we refuse. The standing rule: **Vanguard remains the
authority. An external methodology contributes workflow ideas, never a second
source of truth.**

The danger is never the idea. It is the artifact set that arrives with it —
parallel briefs, plans, stories and status systems that duplicate documents we
already have and then drift out of agreement with them.

## Adoption test

Before adopting anything external, answer all four:

1. Does it duplicate an artifact we already maintain? If yes, take the idea, not
   the artifact.
2. Does it introduce a second place where status or authority lives? If yes,
   refuse it.
3. Can it be expressed as a generated, disposable packet rather than a durable
   document? Prefer that form.
4. If it executes — a skill, a hook, a command — can it be vendored,
   version-pinned and hermetically tested before it gets write authority?

## BMAD

**Borrow, do not install.**

Useful: adaptive planning depth matched to task size; role-specific handoffs;
separation of developer and reviewer; retrospective and convergence loops;
distinct workflows for small changes versus architectural ones.

Refuse: its artifact set. Vanguard already has stronger normative contracts,
execution law, evidence accounting, leases and falsifiers than a generic BMAD
installation expects. Installing it wholesale would create parallel product
briefs, architecture documents, stories and status tracking.

## GitHub Spec Kit

**Borrow the workflow mechanics, not the artifacts.**

Its Spec → Plan → Tasks → Implement flow closely mirrors what the five execution
documents already provide, so direct installation would duplicate `spec.md`,
`technical.md` and `tasks.md`.

Worth taking:

- an explicit **clarify gate** before leasing ambiguous work;
- **cross-artifact analysis** that surfaces contradictions between spec, task and
  implementation — this is the mechanism that would have caught our stale oracle
  and our narrow gate;
- task-specific **checklists**;
- **convergence** of a packet before dispatch.

The resulting packet stays non-canonical and disposable.

## Agent Skills

**Adopt the format. Audit every skill.**

The format fits the context problem directly: a small entry point that loads
scripts, references and assets progressively, only when relevant. That is exactly
how packet compilation should work.

Build repository-specific skills rather than installing generic ones. Start with
two — `work-packet-compiler` and `handoff-verifier` — and add more only when a
real gap appears. The full candidate list is in
[`work_packet_protocol.md`](work_packet_protocol.md); it is deliberately deferred,
because building eight skills before running one is the predictable failure.

Third-party skills are vendored, audited, version-pinned and hermetically tested
before receiving write or execution authority. A skill's instructions are
executable influence over an agent, not inert documentation — treat an untrusted
skill the way you would treat an untrusted dependency with shell access.

## Standing refusal

No external methodology becomes a governance system alongside this one. If a
proposal cannot be expressed as (a) a workflow idea applied to our own artifacts,
or (b) a generated disposable packet, or (c) an audited skill, it is declined.
