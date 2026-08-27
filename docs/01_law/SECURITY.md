---
id: normative-security-law
class: law
authority: normative
canonical_for:
  - security-law-routing
  - isolation-and-tcb-law
status: living
owner: principal-systems-architect
version: "0.8.0"
last_verified: 2026-08-25
read_when:
  - changing-capabilities
  - changing-isolation-or-tcb
do_not_read_when:
  - changing-only-model-routing
subordinate_to: ../../VISION.md
supersedes: []
superseded_by: null
---

# Security law

This is the task-sized entry point for security work. The complete normative text is preserved in
[`DISPATCH.md`](DISPATCH.md): its sections on the TCB, mutability, grants, attenuation, provenance,
the workload perimeter, architecture tests, and threat model are authoritative and are not duplicated
here.

> **Authority.** Normative, but subordinate to [`VISION.md`](../../VISION.md) (Law Zero, `ADR-0095`).
>
> **AETHER is not primarily a security or certification project.** Security mechanisms here are
> reusable substrate capabilities, available as optional profiles. They do not gate normal
> development, and RF-85 hermetic certification blocks no milestone (`ADR-0094`). What remains
> non-negotiable is *honesty*, not *mandatory containment*: profile identity in `D_R`, no false
> promotion claims, and fail-closed behaviour when a stronger assurance profile is explicitly
> requested and cannot be provided.

## Read map

| Concern | Detailed clause | Implementation evidence |
|---|---|---|
| TCB declaration and budget | [`DISPATCH.md §1`](DISPATCH.md#1-the-trusted-computing-base) | `check_tcb_budget.py` |
| S0–S12 reference monitor | [`DISPATCH.md §2`](DISPATCH.md#2-the-dispatch-sequence) | `test/kernel/` |
| Capability grants and attenuation | [`DISPATCH.md §§3–4`](DISPATCH.md#3-grants) | capability contract tests |
| Provenance authority predicate | [`DISPATCH.md §5`](DISPATCH.md#5-provenance-and-the-authority-predicate) | provenance tests |
| Rootless workload boundary | [`DISPATCH.md §6`](DISPATCH.md#6-the-workload-perimeter) | `check_isolation_policy.py` |
| Threat model and fail-closed controls | [`DISPATCH.md §§8–10`](DISPATCH.md#9-threat-model) | named falsifiers F-* |

## Binding reminders

- The model is untrusted content, not an authority principal.
- A host-language mediator, parser, or human process is not a containment boundary.
- Unknown capability relations, unbounded child budgets, unsigned approvals, and unverifiable
  evidence fail closed.
- Adapters and plugins consume ports and wire contracts; they never import the kernel or agency.
- Persistent memory is an authority boundary from M-8 onward. Every read, write, invalidation,
  ranking candidate, and artifact dereference MUST verify action, canonical selector, tenant,
  project, validity interval, and revocation at use time. Authorization filters precede ranking;
  denial MUST NOT disclose record existence. Legal hold dominates garbage collection (ADR-0100).
