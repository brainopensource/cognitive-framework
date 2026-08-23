---
adr: 0073
title: "v0.6 Concept Lock vs defer: sequential execution; CI subject-of-record; Meta-Harness, distribution, WASM-default, graph DB, and Rust rewrite deferred"
status: accepted
source_section: "v0.6 Concept Lock"
---

# ADR-0073: v0.6 lock versus deliberate deferral

**Context.** Forensic discovery showed living CI certifying `test/layer0` + lexical gates while
the production kernel suite (`test/kernel`, 95 OK) is unwired, E-COV is a string grep, and SPEC
names a `replay-parity` CI job that does not exist. Roadmaps and the Full Refactor pull
Meta-Harness, distribution, WASM, and Rust into the same wave as substrate repair. That packing
is how dual runtimes and false gates survived.

**Decision.**

### Locked for v0.6 (semantics now; some wiring in the next *code* phase)

- Sequential execution. Independence groups may be declared; they MUST NOT run concurrently
  until I-11's measurement gate fires. ADR-0007 remains deferred. No vector clocks, NATS, or
  Kubernetes.
- The production lattice (`vanguard/packages/`) is the **CI subject of record**. E-COV lexical
  coverage is not I-2 proof. Fabricated verdicts, missing grants, capability/budget widening,
  fail-open ceilings, replay divergence, and sandbox failure require **negative behavioral
  tests**. Wiring CI is the first code-phase task; this ADR makes shipping without that wiring
  a spec violation, not an aesthetic nit.
- Envelope identity, `D_H`/`D_R`/`D_X`, spawn subset invariants, wire-first plugins, exterior
  evaluator, WAL ledger (ADRs 0069–0072).

### Deliberately deferred (not "forgotten"; normative authority: [`SPEC.md` §9](../SPEC.md#9-what-this-specification-refuses-to-build))

- Meta-Harness promotion loop, genome mutation, DPO harvest productionization, self-updating
  release pipeline (ADR-0019; SPEC §9 SA-1…SA-6)
- Heterogeneous subagent packs beyond the first coding path
- Controlled concurrency enablement
- Moving model gateway and sandbox behind the plugin wire (remain first-party ports)
- pytest as universal test runner (unittest remains)
- TypeScript plugin conformance suite
- WASM-default isolation, remote attestation, multi-host distribution
- Graph database / workflow DAG engine
- Competence-graph revival (DEF-02)
- Systems-language / Rust TCB rewrite (ADR-0006, DEF-05, ADR-0069)
- Third control-plane language

### Explicitly rejected as substrate architecture (normative authority: [`SPEC.md` §9](../SPEC.md#9-what-this-specification-refuses-to-build))

- Third runtime tree
- Swarm engine
- Byte-identical concurrent ledger as a general requirement
- Evaluator as a product plugin
- Mid-run FrozenHarness hot-swap

**Alternative considered (and rejected).**

- Implement CI rewire and F1 fix in the Concept Lock wave. Rejected: TODO and this lock are
  documentation-and-decision; mixing them recreates "docs claim done."
- Pull Meta-Harness into v0.6 because trajectories are specified. Rejected: I-9 requires a
  real trajectory record; it does not require a promotion controller.
- Enable concurrency now because selectors already exist on Proposal. Rejected: I-11; D-38.

**Evidence / bound test / links.** Forensic §§4, 17, 19 P0-10/P0-11/P0-12, §20 P1 registry;
`.github/workflows/ci.yml`; `tools/check_event_coverage.py`; ADR-0005; ADR-0006; ADR-0007;
ADR-0019. Bound test for CI subject-of-record: living workflow runs `test/kernel` plus
packages runtime/agency/adapters suites — code phase. `REQ-TRUST-001`.

**Reversal condition.** A newer ADR that names a measurement (p-value / latency / lost-event
rate) forcing concurrency, distribution, WASM-default, or a systems-language TCB component.
Roadmap enthusiasm is not reversal. Restoring lexical E-COV as the sole I-2 proof is not
available as reversal.

**Owner · status.** Principal Staff Engineer / Tech Lead · accepted · 2026-08-20 · accepted
