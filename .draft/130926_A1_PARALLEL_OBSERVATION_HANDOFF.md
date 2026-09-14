---
id: draft.a1.parallel-observation.130926
class: handoff
authority: dev-a-implementation
status: draft
owner: dev-a
date: 2026-09-13
branch: feat/aether-framework-electroweak-canonical-agents
subject: A1 — parallel observation as a causal partial order
falsifier: test/falsifiers/test_parallel_observation.py
---

# A1 — parallel observation, landed behind a composition opt-in

## What changed

| File | Delta |
|---|---|
| `agency/episode/observation.py` | **new, pure.** `ObservationRequest`, parsing, `settlement_levels` (Kahn ranking), `batch_descriptor`, `MAX_PARALLEL_OBSERVATIONS = 16` |
| `agency/episode/state.py` | `ProposalKind.OBSERVE`; `Proposal.observations`; the observe parse branch; batch-aware `descriptor` |
| `agency/episode/engine.py` | `observation_sinks` seam; batch settlement branch; `_batch_refusal`, `_settle_batch`, `_observation_request`, `_emit_batch_denied`, `_emit_batch_settled`; phase gate generalised over batch members |
| `adapters/models/invocation.py` | N tool calls translate to an observe proposal instead of failing `instrument_error`; a completion may not travel beside another action |
| `test/adapters/test_model_invocation.py` | the multi-action check **narrowed, not removed** — see below |
| `test/falsifiers/test_parallel_observation.py` | **new**, 31 assertions, 8 mutation proofs |

Kernel delta zero. TCB closure unchanged (`agency/` is not in it — verified
against `check_tcb_budget.py --v2`). No manifest and no pack file touched.

## The four non-negotiables, and where each one lives

**Read-only only.** `_batch_refusal` refuses a batch carrying any verb whose
sink class is not `observation`. The classification is the *manifest's own*,
carried by `SinkRegistry` — the engine holds no list of safe verbs, so adding a
domain still costs zero lines here (`C-01`, `ADR-0060`). An unregistered verb
fails closed as privileged, so absence of a declaration is not evidence of
safety. `patch.apply`, `proc.exec`, `finish` and `spawn` are untouched: they
stay single and serialised, and `RUN-10` is not weakened in any direction.

**Per-request causal identity.** Every member goes through `Kernel.dispatch`
on its own. Ten reads produce ten `EffectStarted`, ten grants, ten receipts and
ten distinct descriptor digests. Nothing is collapsed. The turn's own receipt
digest is a *vector* over the members (keyed by declaration position, not by
provider id) so no-progress detection still sees a repeat, and
`EpisodeStateChanged/observation_batch` records the settled order with the
kernel's own `descriptorDigest` per row — which is what joins each row to its
`EffectStarted`/`EffectCompleted` pair on a cold read.

**One reservation per sub-request.** `_reservation_of` is shared with the
single-action path, so a read inside a batch reserves, commits and releases
against the governor exactly as the same read issued alone. Ten reads produce
ten reserve/commit pairs.

**Failure is per request.** A failing member settles as a failure and the rest
of its level still runs. Only a failure path that ends the *run* — budget,
cancellation, suspended approval — stops the batch, and what already settled
stays settled.

## Two things worth arguing with

**Settlement is sequential, deliberately.** A level is a set of mutually
independent requests; executing it concurrently is a permitted optimisation
that changes no receipt. It is not taken. The economics being bought back are
*turn* economics — one model round trip instead of ten — and a run that
reorders under load stops being reconstructable from its own ledger. The order
recorded is causal (`dependsOn` plus derived level), so the optimisation stays
available without a second ledger format.

**One `ProposalProduced` per turn, batch or not.** `Session.turns_consumed`
counts these. Emitting one per member would have made a ten-read batch cost ten
turns of budget and given back nothing. The per-request identity lives in the
kernel's events, where it belongs.

## The narrowed check (rule 1, declared)

`test_translate_multiple_actions_fails` asserted that any multi-call proposal
fails. It now reads `test_translate_multiple_actions_never_collapses_to_one`.

The defect it was written against — several calls becoming one effect with the
rest silently dropped, so the model believes it issued reads it never issued —
**still reds**: a multi-call proposal may not translate to a single `effect`,
and every call must survive into the result. What moved is the disposition of
the survivors and *where* read-only membership is decided: not in the
translator, which would be a second place a domain has to be registered, but in
the episode against the manifest's own sink declarations.

This is also strictly less harsh than what it replaced. The old path returned
`Result.fail`, which the engine reduces to `INSTRUMENT_ERROR` and a terminated
run. A refused batch is now a recorded `AuthorizationDenied` plus typed
feedback the next turn can act on.

## Mutation proofs (rule 2 — re-run these)

Each guard reverted in place; falsifier red; restored; green.

| # | Revert | Red |
|---|---|---|
| M1 | read-only membership always empty | 3 |
| M2 | undeclared sinks no longer fail closed | 1 |
| M3 | batch descriptor keyed on provider ids | 2 |
| M4 | settlement ignores `dependsOn` | 4 |
| M5 | batch aborts on the first failing member | 4 |
| M6 | batch ceiling removed | 1 |
| M7 | attenuated-child scope refusal removed | 1 |
| M8 | phase gate no longer sees batch members | 1 |

Driver: `scratchpad/mutate.py` (reproduced in the session transcript). Baseline
and restored runs both green at 31/31.

## Handoff to Dev C — one line, `session.py`

`session.py` is C's lease this sprint, so this is a named wiring request, not a
concurrent patch. At the `EpisodeEngine(...)` construction (currently
`vanguard/packages/runtime/session.py:1611`, closing at `:1631`), add one
keyword argument:

```python
                completion_allowed_tools=self._completion_allowed_tools,
                observation_sinks=harness.sinks)
```

`harness.sinks` is already in scope at that call site and is the registry
`compose.py` builds from the manifest's `sink:` declarations. Nothing else is
required; the seam defaults to `None`, which refuses every batch, so the
capability is inert until that line exists.

## Reserved for ratification — not done, on purpose (A5)

`vg-code-default/read-tool.json` currently instructs the model:
*"Single action; do not emit parallel calls."* Until that sentence changes, a
well-behaved model will not emit a batch even after C lands the wiring.

Changing it changes the prompt bytes of **`vg-code-balanced`**, the arm the
board is about to freeze. That is a composition delta, and by A5 it is mine to
ratify rather than something to slip in beside a mechanism change. It is
deliberately a separate, single, reviewable commit — pending my own sign-off on
whether A1 activates inside the measured arm or lands beside it the way A2
does. Do not let it drift in with the wiring.

## Not mine, found in passing

- `check_path_hygiene.py` is **red on `main`** for
  `docs/research/AI/aux_cli_multi_profiles.md` (16 machine-local `/home/...`
  paths). Pre-existing at `HEAD`. B6 / CI truth.
- Three `test/runtime` errors are **pre-existing at `HEAD`**, all one defect:
  `session.py::_append_verification_record` calls `self.ledger.emit_kind`, and
  `HarnessSession` has no `ledger` attribute on that path
  (`test_approval_reentry_feedback` ×2, `test_rf85_release_admission` ×1).
  Nothing in A1 touches it. C's file, B5's gate — and a good example of why
  `just verify` not discovering `test/runtime` is a problem.
