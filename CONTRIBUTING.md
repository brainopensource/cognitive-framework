# Contributing to Vanguard

**Non-normative.** This is onboarding, not law. The normative documents are `docs/SPEC.md`,
`docs/04_annex/*`, and `docs/05_adr/*`. If anything here disagrees with those, they win and this file is
wrong — open a PR fixing this file, don't cite it as a requirement.

Extracted from the archived engineering handbook (`docs/archive/v045/01_specs/backend/01_vanguard_engineering_handbook_v040.md`,
VG-01) — the still-true operational mental models, condensed. The SOLID/DRY essays, "shape of a change"
prose, and glossary in the original are superseded by this document's brevity and by `docs/SPEC.md`
itself; they are not carried forward.

## Mental models worth internalising

- **The episode is the program.** There is no workflow engine, no topology language, no graph
  validator — there is a loop that observes, proposes, gets authorised, acts, and reduces. If you find
  yourself declaring a shape for the work *before* the work runs, you are building the thing
  `docs/SPEC.md` §1.1 (loop-over-DAG inversion) rejects.
- **The broker grants; the sandbox contains.** Two distinct boundaries. The kernel decides *whether* an
  effect is permitted. The perimeter decides *what an attacker can reach when the kernel was wrong*. A
  logical mediator in the host language is not containment — see `docs/04_annex/KERNEL.md` §6 before
  writing anything near this.
- **Content informs, never authorises.** Untrusted content may inform work; it must never authorise a
  capability-widening effect. This has failed silently twice in this project's history (see
  `docs/04_annex/KERNEL.md` §5.2) — read that section before touching provenance code.
- **The verifier is outside everything.** No cognition or adapter module may import the evaluator gate
  or reason about its internals. If your change needs the evaluator's logic to be visible from agent
  code, the design is wrong, not the import lint.
- **A gate that cannot fail is not a gate.** Every control needs a must-fail counterpart proving it can
  actually deny. A green suite over unwired code is worse than no control — it manufactures false
  assurance.
- **One document is normative per contract.** If you're about to write a second source of truth for
  something `docs/SPEC.md` already owns, stop — extend the section, don't fork it.
- **Minimise what must be simultaneously correct.** Layer 0 has an LOC target for exactly this reason —
  correctness argument size, not code golf.
- **Polyglot plugins live outside the trusted computing base.** The wire schema (JSON Schema + JCS) *is*
  the narrow waist between languages; there is no other legitimate cross-language coupling.
- **Adding a domain must not touch the core.** `grep -rE "coding|pytest|ast" layer0/` is expected to
  return nothing, always. If your PR breaks that grep, the code is in the wrong package.

## Testing taxonomy (kept intact from VG-01 §4)

Three kinds, and the distinction matters when you're deciding what a new test should be:

- **Mock** — no I/O, no clock, no randomness; deterministic by construction. Fast, runs on every commit.
- **Cassette** — a recorded real interaction (model call, network response) replayed deterministically.
  Proves the code handles a real shape of response without needing a live credential in CI.
- **Live** — an actual external call. Rare, gated, and never a prerequisite for a merge unless the PR
  explicitly says so.

**Satisfiability check:** before writing a test asserting a property, ask whether the property is
actually reachable given the test's own setup. A test that can only ever pass (or can only ever be
vacuously satisfied) is not testing anything — this is how historical ADR-0028's span-reset defect
shipped with a green suite.

## Where things live

Read `docs/SPEC.md` §1 for the target Layer-0 lattice and the current (as-built) seven-package lattice
(`domain, ports, kernel, agency, runtime, adapters, apps`) enforced by `tools/check_boundaries.py`.
Manifest authoring (harness.yaml, plugin.yaml) is specified in `docs/SPEC.md` §2. Measurement rules
(paired designs, McNemar, the A/A floor) are in `docs/04_annex/MEASUREMENT.md` — read it before proposing
any A/B claim.
