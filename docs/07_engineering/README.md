---
status: living
id: engineering-index
class: how-to
authority: descriptive
canonical_for:
  - engineering-guides-index
source_of_truth:
  - docs/SPEC.md
  - AGENTS.md
derived_from:
  - tools/
  - test/
applies_to:
  - v0.6.1
implementation_status: AS_BUILT
owner: lead-documentation-engineer
version: "0.6.1"
last_verified: 2026-08-23
supersedes: []
superseded_by: null
---

# Autonomous Engineering & Contributor Guides

> **Classification:** How-To & Operational Engineering Reference.  
> **Authority:** Non-normative. Operational instructions for extending and verifying the substrate.

---

## Contributor Guides

Begin every change with the active task and the minimum context bundle. Use `development.md` for the
daily loop, then select only the specialized guide required by the boundary being changed.

| Guide | Scope & Focus |
|---|---|
| [`development.md`](development.md) | Setup, environment, dependencies, and daily developer workflow |
| [`testing_and_falsifiers.md`](testing_and_falsifiers.md) | Test pyramid, writing red falsifiers, hermetic cassette tests |
| [`security_and_tcb.md`](security_and_tcb.md) | TCB LOC budget enforcement ($\le 1438$ LOC), domain blindness, secrets scanning |
| [`adding_an_adapter.md`](adding_an_adapter.md) | Step-by-step guide to writing a model, evaluator, or storage adapter |
| [`adding_a_pack.md`](adding_a_pack.md) | Step-by-step guide to creating a new domain pack (e.g. Math/Deductive Verification) |
| [`documentation.md`](documentation.md) | Documentation anti-sprawl rules, frontmatter schema, and CI validation |
| [`context_bundles.md`](context_bundles.md) | Subsystem context bundle index & measured token budgets for AI agents |
