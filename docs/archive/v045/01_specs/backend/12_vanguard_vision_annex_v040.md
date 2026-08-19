---
id: VG-12
file: 12_vanguard_vision_annex_v040.md
title: "Vanguard v4.0 — Vision Annex"
version: 4.0.0
status: NON-NORMATIVE
authority_scope: none — this document states no contract
supersedes: none
superseded_by: none
budget_words: 1000
owners: [Project Lead]
last_reviewed: 2026-08-14
---

> # NON-NORMATIVE
> **Not a specification. No ticket may cite this document.** Nothing here constrains an implementation, and nothing here may be quoted in a design review as a reason to build anything.

# Vanguard — Vision Annex

## 0. Why this document exists as a quarantine

The analogies below are useful for explaining the system to people. They are also how the pre-v4 corpus went wrong: metaphor leaked into specifications, acquired the grammar of requirements, and produced two lineages that each believed they were describing the same architecture.

The failure was not that the metaphors were bad. It was that **a metaphor in a specification is unfalsifiable**, and an unfalsifiable statement in a normative document cannot be adjudicated when two people read it differently.

So they live here, behind a header, where they can do their job — communication — and nothing else.

---

## 1. The project in one sentence

A system that measurably improves its own harness under an evaluator it cannot game, in a domain where verification is cheap enough to run constantly.

That sentence is deliberately narrower than the ambition. The ambition is competence expansion in general; the claim is the coding case, because the coding case is the one that can be falsified this year.

---

## 2. Analogies, and precisely where each breaks

Every analogy is offered with its failure point, because an analogy without one is how metaphor becomes specification.

**The organism.** Primitives are cells, operators are proteins, methods are organs, and the competence graph is the genome — immutable, expressed selectively by context. *Breaks at:* biology has no verifier. Nothing in an organism plays the role of an external judge, and that judge is the load-bearing component here.

**The laboratory.** The runtime is an instrument; episodes are trials; the measurement apparatus is the calibration rig. *Breaks at:* laboratory instruments do not modify themselves between trials. Ours proposes its own successor, which is why the release pipeline exists.

**The operating system.** Planes are rings, capabilities are file descriptors, the broker is the syscall boundary. *Breaks at:* an operating system's processes do not argue with it in natural language, and the most dangerous input to this system arrives as content rather than as a call. The phrase "cognitive operating system" is rejected as architectural language for exactly this reason (`10 [REJ-09]`).

**The apprentice.** The system accumulates competence, is corrected, and eventually works unsupervised in narrow domains. *Breaks at:* an apprentice generalises from few examples and knows when they are out of their depth. Calibrated abstention is a research problem here, not a default.

---

## 3. The long horizon

If the coding case pays — if a competence artifact the designers did not author measurably transfers, survives a model change, and survives adversarial ablation — then the interesting question is not *"can we make a better coding agent."* It is whether the same machinery works in a domain where verification is expensive.

Nothing in the current design answers that. `07 §8` describes the experiment that would begin to.

**The honest framing:** this project is a bet that the evaluator problem is the bottleneck, and that a system built so the evaluator can never be gamed is worth more than a system built to score well on today's benchmarks. That bet may lose. If it loses cleanly — if the transfer experiment runs and produces nothing that clears its controls — that is a publishable result about methodology, and a better outcome than an unfalsifiable success.

---

## 4. What is deliberately not said here

No timelines. No capability predictions. No claims about general intelligence. The system earns each name before it prints it on the kernel, and this annex is not a place to spend that credit early.
