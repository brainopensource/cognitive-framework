---
id: execution.management.work_packet
class: standard
authority: advisory
canonical_for:
  - work-packet-protocol
status: living
owner: repository-governance
version: "0.1.0"
last_verified: 2026-09-12
---

# Work packet protocol

A work packet is the compiled slice handed to one developer for one assignment.
It is **generated, bounded and disposable**. It is never authority: when a packet
disagrees with a canonical document, the canonical document wins and the packet
is regenerated.

Packets are delivered in agent context or a runtime-provided ephemeral artifact
store. They are never committed and never placed under `docs/`. Retained evidence
may bind a packet digest, but retaining the packet body would create a stale
parallel task board.

## Why packets rather than more documents

The five canonical documents are a *state* representation — they answer "what is
the case." A developer needs a *process* representation — "what am I doing, with
what authority, and how will we know it worked." Compiling the second from the
first keeps one source of truth while giving each agent a small, clean context.

## Required fields

A packet is malformed if any field is absent. `n/a` is a valid value; silence is
not.

| Field | Content |
|---|---|
| Packet identity | Stable packet ID, compilation timestamp and digest of the canonical inputs |
| Task ID and outcome | The row it implements, and the observable end state |
| Base HEAD and index identity | Exact SHA and LDA identity; both must be fresh at admission |
| Authority bindings | Task-board blob plus IDs and content digests of cited normative clauses |
| Accepted prerequisites | Which `requires:` edges are satisfied, and by which receipt |
| Owner and reviewer | Named, and the reviewer must not be the author |
| Exclusive write lease | Exact paths this packet may modify |
| Read-only surfaces | Paths it may read but not touch |
| Governing clauses | Stable clause IDs and bounded excerpts; line ranges are navigation hints, not identity |
| Known evidence | Current failing signature, prior attempts, relevant receipts |
| Implementation authority | What may be decided alone (see philosophy §2) |
| Required falsifiers | Positive **and** adversarial, with the expected red control |
| Budget | Turns, wall-clock, repair cycles, provider calls and USD |
| Non-goals | What this packet explicitly does not do |
| Stop and escalation conditions | What ends the session, and what returns to whom |
| Handoff receipt schema | The exact shape of the evidence to return |

**Size target: roughly 2,000–4,000 tokens.** This is a starting hypothesis, not a
rule. For each packet record compiled tokens, developer clarification turns,
recompilations, elapsed lead time and review defects. Adjust only from those
measurements. A packet that cannot fit is usually a task row that should be split.

## The falsifier field is the load-bearing one

Every packet names both a positive falsifier (the behaviour must work) and an
adversarial one (the failure must be caught), and states the **red control**:
the specific defect that must make the falsifier fail before the fix lands.

A packet whose falsifier has no retained negative-control provenance is
unverified, whatever its final exit code says. The control may be the actual
defect, a deterministic adversarial fixture or an isolated mutation; never damage
the shared candidate merely to manufacture a red result.

## Lifecycle

```text
compile   canonical law + task row + LDA retrieval -> packet + input digest
admit     check HEAD, index, input digests, prerequisites and lease collisions
execute   developer works inside lease and authority until a stop condition
resume    repeat admission before any new write; stale packets are regenerated
receipt   evidence binds packet digest: commands, exits, counts, durations, digests
verify    independent reviewer reruns the named falsifiers on the exact subject
promote   durable conclusions into canonical documents; raw logs stay outside
discard   the packet; regenerate from current truth when work resumes
```

Discarding is deliberate. A retained packet becomes a stale second source of
truth, which is the failure this protocol exists to prevent.

Admission fails closed when HEAD or the task-board blob changed, a cited clause
digest changed, a prerequisite receipt was superseded, the index is stale, the
tree is dirty contrary to the task contract, or a lease collides. A documentation-
only commit does not silently preserve admission: the compiler either proves its
inputs unchanged or regenerates the packet cheaply.

## Receipt requirements

A handoff is rejected without: packet digest, exact subject, exact commands, exit
codes, test counts, durations, changed files, candidate digest, reviewer identity,
negative-control provenance and resource settlement. Evidence is written only to
the task's already-authorized ledger or artifact destination; a packet cannot
invent a new evidence store. Self-reported prose, or a source string quoted as
proof that code runs, is not evidence. An unexecuted command is `not_run`, never
`passed`.

## Implementation vehicle

Packets should eventually be compiled by a repository skill rather than by hand,
so the format cannot drift. Start with two and add more only when a real gap
appears:

1. **`work-packet-compiler`** — assembles a packet from the task row, the cited
   clauses and LDA retrieval.
2. **`handoff-verifier`** — validates a returned receipt against the packet:
   changed files inside lease, falsifiers actually run, digests consistent.

Candidates for later, deliberately deferred until the first two have run:
`lease-admission`, `evidence-recorder`, `decision-escalator`,
`context-checkpoint`, `independent-review`, `as-built-promoter`.

Building eight skills before running one is the failure mode this list is
arranged to avoid.

## Third-party skills

Vendored, version-pinned, audited and hermetically tested before receiving write
or execution authority. A skill's instructions are executable influence over an
agent, not inert documentation.
