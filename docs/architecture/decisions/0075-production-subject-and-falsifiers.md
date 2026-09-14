---
id: adr-0075-production-subject-and-falsifiers
adr: "0075"
class: decision
authority: binding-decision
canonical_for:
  - decision-0075-production-subject-and-falsifiers
status: living
owner: engineering-director
version: "1.0"
last_verified: 2026-09-13
decision_status: accepted
---

# ADR-0075 — Production subject and named falsifiers

This is a bounded restoration of the accepted 2026-08-20 director decision from Git `a694ba8f2d2b6f7148e45b64de4e10226aeec725:docs/02_decisions/0075-director-review-v060-approved-wave0-authorized.md`.
It approved the v0.6 concept lock and authorized historical Wave 0 to align CI with the canonical production lattice and named falsifiers, rather than accepting a competing legacy implementation as product truth.
Its F-18 extended domain-blindness enforcement to production domain/kernel, F-19 required honest test collection, F-20 required restoring or explicitly retiring the missing oracle registry, and F-21 treated translator lifting failures as real behavioral findings rather than silently relabeling them legacy.
The durable rule is that production source, executable falsifiers and attributed baseline evidence decide implementation status; excluded tests, missing artifacts and fabricated passes cannot establish acceptance.
Current routing references are [domain-blindness enforcement](../../../tools/linters/check_domain_blindness.py), [named falsifiers](../../../test/falsifiers/test_falsifiers.py) and [the restored oracle registry](../../../test/fixtures/preregistered_oracles.json), not a claim that the original review's counts are current.
Historical concept-lock scheduling, retired paths and the then-current baseline remain provenance, with later accepted runway decisions controlling present readiness; reversal requires a successor decision supported by a named substantive contradiction.
