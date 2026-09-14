---
id: adr-0109-binding-decision-medium
adr: "0109"
class: decision
authority: binding-decision
canonical_for:
  - decision-0109-binding-decision-medium
status: living
owner: engineering-director
version: "1.0"
last_verified: 2026-09-13
decision_status: accepted
---

# ADR-0109 — D-4: restore the binding decision medium

`docs/architecture/decisions/` is the canonical home for accepted architectural decisions, their rationale, explicit supersession and reversal conditions; the execution spec keeps delta contracts and links to decisions, while milestones keep acceptance predicates and tasks keep readiness.
This directory and the four bounded restorations are explicitly authorized by the present director assignment despite the earlier general prohibition on new ADRs; that exception does not admit scratch reports or parallel planning documents.
[ADR-0047](0047-disposable-prototypes.md), [ADR-0060](0060-domain-generality.md), [ADR-0075](0075-production-subject-and-falsifiers.md) and [ADR-0092](0092-measurement-before-concurrency.md) restore decisions from identified Git objects, retaining their original meaning while separating historical scheduling from current authority.
Their restoration neither reopens historical milestones nor invents missing original text, and later accepted topic-specific decisions and constitutional invariants retain precedence.
The ADR-0047 citation in `test/contracts/test_evo09_model_factory.py` is misattributed: the historical decision concerns disposable prototype consumers, so the factory's actual behavioral contract remains its source, ports and registry until the owning senior corrects the citation without changing the restored ADR.
The ADR-0092 module `test/falsifiers/test_m7_topology_and_independence.py` is explicitly skipped after `lab/` withdrawal, so it is a historical reference rather than a live enforcement receipt.
Future architectural changes receive an identified decision here and reference it from the affected gate; restoring four cited decisions is the bounded scope, not a wholesale migration or an assertion that every remaining numbered citation has been repaired.
