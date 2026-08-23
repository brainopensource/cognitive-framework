---
id: normative-security-law
class: law
authority: normative
canonical_for:
  - security-law-routing
  - isolation-and-tcb-law
status: living
owner: principal-systems-architect
version: "0.6.1"
last_verified: 2026-08-23
read_when:
  - changing-capabilities
  - changing-isolation-or-tcb
do_not_read_when:
  - changing-only-model-routing
supersedes: []
superseded_by: null
---

# Security law

This is the task-sized entry point for security work. The complete normative text is preserved in
[`DISPATCH.md`](DISPATCH.md): its sections on the TCB, mutability, grants, attenuation, provenance,
the workload perimeter, architecture tests, and threat model are authoritative and are not duplicated
here.

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
