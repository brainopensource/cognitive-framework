---
id: execution.management.philosophy
class: standard
authority: advisory
canonical_for:
  - multi-agent-development-philosophy
status: living
owner: repository-governance
version: "0.1.0"
last_verified: 2026-09-12
---

# Development philosophy

Why this process is shaped the way it is. Advisory, not normative: it explains
the reasoning behind rules that live in [`spec.md`](../main/spec.md), so that an
agent can extend them correctly rather than only obey them.

## 1. The problem this solves

Human engineers share an enormous amount of implicit state — what was tried last
week, what felt fragile, which code everyone quietly avoids. They rebuild it
cheaply through conversation, so their documents only need to carry the durable
part.

AI agents carry none of it. Every session starts cold. So state that human teams
keep in their heads must either be reconstructed each session — expensive, and
the origin of most hallucination — or be written down. Our documents therefore do
a job that human documents have never had to do.

Two failure modes follow, and both come from the same root:

- **Micromanagement.** Leadership re-specifies everything because the developer
  cannot be trusted to have the context. Leadership becomes an expensive project
  manager; the developer becomes a typist.
- **Drift.** The developer is given freedom but no durable record of *why* the
  boundaries sit where they do, so locally reasonable choices violate a
  constraint decided three sessions ago that nobody wrote down.

The cure for both is the same and it is not "more documentation."

## 2. Write boundaries, not decisions

A decision is *"REPAIR both oracles."* It handles one situation.

A boundary is *"you may rebind digests after independent red/green proof; never
without."* It handles forty situations nobody anticipated.

Leadership's output should be mostly boundaries. A developer who knows the
boundary continues through surprises; a developer who only has an instruction
stops at the first one and waits — which is exactly the interruption that
destroys long autonomous sessions.

[RUN-04](../main/spec.md) already has the right shape: what a developer MAY
decide alone, and what MUST return. Every work packet needs its own local version
of that, scoped to the slice.

## 3. The test for whether the process works

> Can a developer work for two weeks, make a hundred decisions, and have the
> eventual review find nothing that should have been escalated?

If yes, the system works. If no, you are back to micromanagement regardless of
how good the documents look. Everything in this folder exists to make that
sentence true.

## 4. Asynchronous review requires verifiable work

Review every two weeks instead of every minute requires exactly one property:
**work must be verifiable without the reviewer having been present when it
happened.** Three things provide it.

**Falsifiers that red.** A passing test proves an agent wrote code that satisfies
a test it also wrote. A test proven to *fail* on the real defect and pass after
the fix proves something happened. At a fortnightly cadence the red control is
the only thing standing between a reviewer and two weeks of confident nonsense.
This is why deterministic red controls are demanded everywhere, including on
gates themselves: a gate proven only green says nothing about the defect that
escaped it.

**Exact-subject identity.** A receipt bound to a SHA, a digest, and literal
commands can be re-verified later by someone who was not there. Prose cannot.
A shared HEAD moving underneath a receipt invalidating it is correct behaviour,
not a coupling defect — the fix is to make packets cheap to regenerate, never to
loosen subject binding.

**Resumable handoffs.** Every session ends with state, blockers and next action —
not a narrative of what happened, which the next agent does not need.

## 5. Context is not merely costly, it is harmful

An agent given five documents when it needs one paragraph does not just waste
tokens. It pattern-matches against irrelevant material and produces plausible
work addressing the wrong constraint.

So the working set must be small and explicit. `status: living` must mean *"an
agent must read this if the work touches its area"*, not *"not deleted"*. A
document unchanged for six weeks while the code moved is `reference`, whatever
its header says.

The corollary: a task row carries its contract inline — objective, falsifier,
what you may decide alone, stop condition — and cites normative text only when
the developer genuinely needs it. An agent that must read `spec.md` to *start*
has been handed a failed row.

## 6. Two AI reviewers are structurally weak

A human architect reviewing a human developer brings independent judgment. Two
instances of similar models share failure modes: they find the same arguments
convincing and miss the same gaps. An approval from a peer model is weaker
evidence than it appears.

This is why falsifier discipline matters more here than in a human team. A test
that reds on the actual defect is independent of both agents' judgment; a review
that says "this looks correct" is not. It is also why the CEO reading actual
diffs and red controls periodically is not micromanagement — it is the only
genuinely independent check in the loop, and it should be spent on evidence
rather than on prose summaries.

## 7. Findings need a home before they become decisions

Every expensive surprise in this project so far was known-but-homeless: true,
discoverable, recorded nowhere, surviving only in a chat transcript until it
cost a day. Observations that are not yet decisions must have a place to sit.
That place is [`state_of_play.md`](state_of_play.md), and the section that earns
its existence is *Found, not yet decided*.

## 8. What we refuse

- No sixth canonical document. Additional planes are generated and disposable.
- No second source of truth. An external methodology may contribute workflow
  ideas; it may not contribute authority. See
  [`methodology_sources.md`](methodology_sources.md).
- No append-only session log. Unreadable in three weeks, and an unread document
  is worse than none because it gets cited as if read. Git history is the append
  log; the working document is rewritten and stays short.
- No weakening of a falsifier to make a session end cleanly. Narrow a noisy
  check and prove it still reds; never delete it.
