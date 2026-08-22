---
id: normative-annex-kernel
class: law
authority: normative
canonical_for:
  - kernel-capabilities-security-annex
  - s0-s12-dispatch-contract
status: living
owner: principal-systems-architect
version: "0.6.1"
last_verified: 2026-08-21
title: "Kernel, Capabilities & Security"
source: 01_specs/backend/05_vanguard_kernel_capabilities_and_security_v040.md (VG-05; git history, 4f9f8b1)
amendments: [ADR-M0-08 (K-40 inverted), ADR-M0-09 (alarm set F-21a+F-24), "SA-1..SA-6 pipeline text struck (D-34, honoured non-build)", ADR-0069 (production lattice is vanguard/packages/; layer0/ is not an M1 destination rewrite), ADR-0074 (typed budget; writer authority; complete D_H)]
supersedes: []
superseded_by: null
---

# Annex: Kernel, Capabilities & Security

> Kept nearly verbatim from VG-05 per the archived `01_SPECS_MIGRATION_MATRIX.md` §1.8 (git history,
> `4f9f8b1` — `docs/07_reviews/ARCHIVE.md`) — this
> is the crown jewel, the normative twin of `vanguard/packages/kernel/dispatch.py`. RFC-2119
> language (MUST/SHALL/SHOULD) is normative here, same as `docs/SPEC.md`. Amendments are ADRs only
> (front-matter); S0–S12 body is unchanged. **v0.6 (`ADR-0069`):** the production implementation of
> this annex is `vanguard/packages/kernel/`, not a destination rewrite into `layer0/`.


# Vanguard v4.0 — Kernel, Capabilities & Security

> **Standing exception.** Compression applies everywhere in this set except here. The kernel, the verifier boundary and the capability algebra are the only things standing between *self-improving* and *self-deceiving*. Nothing in this document is shortened to meet a budget; if it does not fit, something else gives way.

---

## 0. Audit stance

This document is written to be attacked. Every claim states its enforcing boundary, every control names the test that proves it can fail, and every residual risk is stated rather than absorbed into a guarantee.

**The governing rule, from which most of this document follows:**

> **`K-01`.** A guarantee may not exceed the boundary that actually enforces it.

A logical mediator in the host language is not a containment boundary. A parser is not a perimeter. A policy enforced by human attention is not a mechanism. Each of those was claimed as a security property by a predecessor of this design, and each was false in a way that a reader of the document could not detect.

Non-claims are owned by `02 §3` and are not restated. The two that matter most here: **the model is not trusted**, and **a malicious operator at the console is out of scope**. The threat model is untrusted *content*, not an untrusted *principal*.

**Assurance method.** Four independent kinds, none substituting for another: architecture tests proving paths do not exist (§8); must-fail tests proving each control can fail (`08 §5`); fault injection against the recovery paths; and adversarial audit of the verifier by someone who did not write it, mandatory before any training run.

---

## 1. The trusted computing base

### 1.1 The policy kernel and the declared transitive TCB

The auditable size ceiling applies to the **policy kernel** — dispatch, policy evaluation, grant issuance and verification, attenuation, the governor, and the provenance predicate. It does **not** apply to the trusted computing base, which is larger and must be declared rather than hidden:

operating-system kernel or hypervisor; container or micro-VM runtime; the supervisor; the policy configuration and its parser; the secret broker; the ledger and event store; the build and release controller; the evaluator runtime and its images; every transitive dependency loaded into a privileged process; and the identity, key and signing system.

> **`K-02`.** The project does not count the operating system against its internal size budget. It declares the dependency, its version, its hardening posture, its update cadence and its threat assumption. **Concealing a dependency does not remove it from the TCB.**

A ceiling on the policy kernel is a tripwire, not a guarantee. A TCB that grows without bound stops being auditable long before it stops being correct, so `AT-08` makes growth an explicit decision rather than a gradual slide.

**[AMENDED] TCB metric.** The original LOC-number tripwire (the specific line-count ceiling) is struck from this annex's normative prose — the audit's AP-8 finding is that a LOC ceiling is a Goodharted metric (rewards density over clarity in exactly the code that must be clearest). The TCB **concept** in this section (§1.1's declared transitive TCB) stays. The replacement metric triple — mutation-testing score on kernel+reducers, percentage of declared controls with production call-site proofs, and event-kind emission coverage (E-COV) — is M1 CI and does not exist yet; pretending it does would repeat the audit's own complaint. Until M1 lands it, `tools/check_tcb_budget.py`'s LOC gate remains the **living** size gate (this dual state — annex describes the future metric, the old gate still runs — is intentional, not an oversight; see ADR-M0-05).

### 1.2 Mutability classes

The boundary is enforced at the dispatcher, not by governance. A policy is routed around by a motivated optimiser and forgotten by a tired human, and it cannot be checked at runtime by the thing it constrains.

| Class | Contents | Initial policy |
|---|---|---|
| `R0` root | Update root, signing policy, capability algebra | Human plus threshold. **No automation** |
| `R1` TCB | Policy kernel, broker, evaluator gate | Automatic candidate; human promotion |
| `R2` runtime | Episode engine, stores, adapters | Candidate plus CI plus canary; explicit approval |
| `R3` cognition | Prompts, operators, methods, routing | Promotion delegable to evidence policy |
| `R4` content | Memories, indexes, episodic data | Automatic write with quarantine and retention |

> **`K-03`.** At composition the dispatcher builds a **closed** adapter table. Any effect request whose normalised target resolves into `R0` or `R1` is rejected before policy rules are evaluated. The rejection is not configurable, because the check precedes the rule engine that could otherwise grant an exception.

### 1.3 The security claim, stated once

> **S1.** For any agent A executing under Vanguard, and any sequence of model outputs — including adversarial ones, including outputs induced by untrusted content in A's context — A cannot:
> **(a)** perform an effect outside its granted actions **and resources**;
> **(b)** cause a child to hold authority outside the parent's;
> **(c)** modify the verifier, its image, its inputs, or the measurement protocol;
> **(d)** exceed its limits without the overrun being debited and recorded;
> **(e)** cause untrusted content to authorise a capability-widening effect;
> **(f)** promote a claim to active competence without independent evidence;
> **(g)** reach the runtime, its configuration, its keys or its update path.

Clause **(a)** says *and resources* deliberately. A verb-only formulation of this claim is satisfiable by a system in which a "read-only" child reads the evaluator bundle, the policy configuration and the signing keys — all read-class, all permitted (`04 §5.1`). Clause **(g)** is new and is the clause that makes self-modification safe to discuss at all.

Sections 2 through 9 exist to make S1 checkable. §9 enumerates the attacks against each clause.

---

## 2. The dispatch sequence

### 2.1 The only path

The dispatch sequence is the single execution path for all effects. However, two distinct principals invoke it across well-defined boundaries:

1. **`Principal::Episode`** (ingress from the agent loop): submits action proposals (`observe`, `fs.patch`, `proc.test`). Subject to grant verification, selector attenuation, and budget reservation.
2. **`Principal::EvidencePlane`** (ingress from the evaluator daemon, a separate OS process identity): submits evaluation executions triggered solely upon observing a terminal ledger event. The episode holds zero capability to invoke or request this path (`03 §3/§6.1`).

The dispatcher pipeline S0–S12 is identical and strictly mediated; the distinction resides in caller authority and provenance. There is no second path, and `AT-01` proves it.

```
 S0  ENTER      EffectRequest { action, resource, args, principal, depth,
                                justifyingSpans, runId, parentLease }
 S1  PARSE      validate against the contract schema
 S2  RESOLVE    action → adapter                    ◄── BEFORE any lease
 S3  DESCRIBE   descriptor = digest(canonical(name, normalisedArgs))
 S4  CLASSIFY   widensCapability := classifier(request)   ◄── not a constant
 S5  AUTHORIZE  decision := policy.authorize(AuthorityRequest)
 S6  GRANT      grant := issue(descriptor, principal, resources, ttl)
 S7  RESERVE    lease := governor.reserve(runId, resources, parentLease)
 ┌── try ──────────────────────────────────────────────────────────────┐
 │ S8  VERIFY   assert the grant binds THIS descriptor and is unexpired │
 │              ◄── at the point of effect, not at issuance             │
 │ S8a INTENT   durably append EffectStarted{descriptor, grantId,       │
 │              idempotencyKey} and FSYNC   ◄── BEFORE the effect       │
 │ S9  DISPATCH adapter.execute(...)                                    │
 │ S10 COMMIT   governor.commit(lease, actual)                          │
 └── finally ──────────────────────────────────────────────────────────┘
 S11 RELEASE    governor.release(lease)             ◄── every path, always
 S12 EMIT       outcome events                      ◄── after release
```

### 2.2 Ordering rules

Each rule below corresponds to a defect that actually shipped in the prototype. None is stylistic.

| # | Rule | Defect prevented |
|---|---|---|
| `K-04` | **S2 precedes S7.** Adapter resolution before lease acquisition | With lookup between reservation and the guarded block, an unknown action raises while holding a lease that is never released and never committed — permanently subtracted from the run ceiling. Unreachable with a closed table; reachable the moment a new action class is added |
| `K-05` | **S8 is inside the guarded block, after S7.** The grant is verified at the point of effect | A resumed run, a mutated request or a stale decision cannot ride an earlier grant |
| `K-06` | **S11 precedes S12.** Release before emit, including on the exception path | If the emit itself raises, the lease is already back. A leaked lease is worse than a lost event |
| `K-07` | **S10 debits reality, including overruns.** Refund is reserved minus actual, **retained when negative** | Clamping the refund at zero means an overrun is never debited and the ceiling never moves |
| `K-08` | **S4 is a classifier call**, computed per request | A hardcoded value makes the predicate appear to fail closed on all tool use, masking that the classifier does not exist |
| `K-47` | **S8a precedes S9, and the intent record is durable before the effect begins.** Emission is therefore split: intent before, outcome at S12 | A crash between dispatch and emit otherwise leaves **no record that the effect was attempted**. The recovery controller has nothing to reconcile against, so an executed external effect becomes *invisible* rather than *undeterminable* — which silently defeats `F-22`, `02 [C-11]` and hypothesis H3. A single trailing emit point is the most plausible-looking version of this defect, and it was present in the first draft of this document |

### 2.3 Failure paths

Every exit is enumerated. **An exit not in this table is a defect**, and `AT-09` checks that the set is exhaustive.

| # | Stage | Condition | Lease | Emitted | Returned |
|---|---|---|---|---|---|
| `F-01` | S1 | Schema validation fails | never opened | `EffectRejected{schema}` | contract error |
| `F-02` | S2 | Unknown action | **never opened** (`K-04`) | `EffectRejected{unknown_action}` | composition error |
| `F-03` | S2 | Adapter present but unhealthy | never opened | `EffectRejected{adapter_unavailable}` | instrument error |
| `F-04` | S3 | Arguments not canonicalisable | never opened | `EffectRejected{descriptor}` | contract error |
| `F-05` | S4 | Classifier raises | never opened | `EffectRejected{classifier_error}` | **fail closed** — treated as widening |
| `F-06` | S5 | Decision is reject | never opened | `AuthorizationDenied{reject}` | denied |
| `F-07` | S5 | Approval required, benchmark mode | never opened | `AuthorizationDenied{ask_fail_closed}` | denied |
| `F-08` | S5 | Approval required, interactive mode | never opened | `ApprovalRequested` | **suspend** (§2.5) |
| `F-09` | S5 | Authority predicate violated | never opened | `AuthorizationDenied{untrusted_justifying}` | denied |
| `F-10` | S5 | Request exceeds parent scope | never opened | `AuthorizationDenied{scope_escalation}` | denied, **alertable** |
| `F-11` | S6 | Grant issuance fails | never opened | `EffectRejected{grant_issue}` | kernel error |
| `F-12` | S7 | Budget denied on any dimension | denied | `BudgetReleased{denied}` | budget exhausted |
| `F-13` | S7 | Parent lease already closed | denied | `BudgetReleased{parent_closed}` | budget exhausted |
| `F-14` | S8 | Grant does not bind this descriptor | released | `EffectRejected{grant_mismatch}` | kernel error |
| `F-15` | S8 | Grant expired | released | `EffectRejected{grant_expired}` | kernel error |
| `F-16` | S8 | Grant already consumed | released | `EffectRejected{grant_replay}` | kernel error |
| `F-17` | S8 | Grant authenticator invalid across a process boundary | released | `EffectRejected{grant_forged}` | kernel error, **alertable** |
| `F-18` | S9 | Adapter raises | released | `EffectCompleted{error}` | error |
| `F-19` | S9 | Timeout | released | `EffectCompleted{timeout}` | timeout |
| `F-20` | S9 | Cancelled | released | `EffectCompleted{cancelled}` | cancellation |
| `F-21` | S9 | Perimeter unavailable or crashed | released | `EffectCompleted{error}` | **instrument error** |
| `F-21a` | S8a | Intent append fails | released | `KernelAlarm{intent_append_failed}` | kernel error — **the effect never starts** |
| `F-22` | S9 | External effect occurrence undeterminable | released | `EffectReconciled{unknown}` | **uncertainty preserved** |
| `F-23` | S10 | Commit fails | released | `BudgetReleased` | kernel error |
| `F-24` | S11 | Release itself fails | **leaked — alarm** | `KernelAlarm{lease_leak}` | kernel error |
| `F-25` | S12 | Emit fails | already released (`K-06`) | `EffectReconciled{unknown}` | **transactional outbox: intent record exists from S8a; recovery scanner reconciles to `undeterminable`** |

**On `F-05`.** A classifier that raises is treated as widening. Failing open here would mean that an exception in the classifier disables the authority predicate — the single most attractive target in the entire kernel.

**On `F-22`.** This path did not exist in either predecessor. Without it, an implementation must resolve an undeterminable external effect to success or failure, which is manufacturing evidence. It is the enforcement point for `02 [C-11]`.

**On `F-24`.** A release failure is unrecoverable by definition and raises a kernel alarm. **It must page, not log.**

**[AMENDED — ADR-M0-09] Alarm set = `{F-21a, F-24}`.** The original text ("F-24 is the only kernel alarm") is corrected: `F-21a` (intent-append failure, S8a) also raises `KernelAlarm`. A crash between durable intent-append and effect dispatch is exactly the undeterminable-effect case `K-47` exists to make visible rather than silent — it MUST page an operator, not just log (drift D-18).

**On `F-25`.** An emission failure at S12 does not re-execute the effect. Because the intent record was durably written at S8a before execution, the transaction is enqueued to the outbox, and the recovery scanner reconciles the outcome to `undeterminable` rather than silently dropping the event.

### 2.4 Idempotence and replay

| # | Rule |
|---|---|
| `K-09` | S1–S8 are pure given the request and kernel state. Re-execution yields the same decision or a replay rejection |
| `K-10` | S9 is **not** idempotent. Replaying a dispatch is a correctness violation, prevented by single-use grants |
| `K-11` | On resume, prior grants are **not** honoured. A resumed run re-authorises from S1 |
| `K-12` | Recorded replay bypasses S9 only; **S1–S8 execute normally** |

`K-12` is an assurance property, not a convenience: it means the security path is exercised by every replayed test in the suite, not only by tests written against the kernel.

### 2.5 Suspension

Approval in interactive mode suspends **before** the lease is opened (`F-08`). Re-entry is at S1 with the same request.

| # | Rule | Rationale |
|---|---|---|
| `K-13` | No lease is held across a suspension | A suspension may last hours; a held lease would block the run's budget |
| `K-14` | Re-entry is at S1, never at S6 | An approval authorises a *request*; it does not bypass authorisation |
| `K-15` | The suspension token binds the descriptor | An approval cannot be transplanted onto a different call |
| `K-16` | Tokens expire, and expiry resolves as denied | Fails closed |
| `K-17` | In benchmark mode, approval never suspends (`F-07`) | A run that blocks for a human has unbounded wall-clock **and** a human contributing to the measured outcome |

---

## 3. Grants

Grant structure is owned by `04 §5.2`. The kernel's obligations:

| # | Rule |
|---|---|
| `K-18` | A grant carries `descriptorDigest` (`04 [CT-51]`) and authorises **exactly that call**. S8 compares the descriptor recomputed at S3 against it; any mismatch is `F-14`. A grant without the field cannot be issued |
| `K-19` | A grant is single-use whenever the effect has no safe idempotency key |
| `K-20` | A grant crossing a process boundary carries a message authentication code or signature over its full contents. An in-process grant may be an opaque reference |
| `K-21` | Long-running operations renew lease and grant explicitly. **There is no universal fixed time-to-live** — a thirty-second default silently breaks every legitimate long operation and teaches operators to widen it globally |
| `K-22` | Granting subprocess execution grants execution **inside an already-limited environment**. It does not imply syscall interception, and no document may describe it as though it does |

The receipt for an execution effect records what actually bounded it: image or root-filesystem digest, normalised argument vector and working directory, environment variable **keys but never secret values**, mounts, network policy, resource limits, redacted output references, exit or cancellation or timeout, and the containment runtime in force.

---

## 4. Attenuation

A child grant is valid only when its actions are a subset of the parent's, its resources are a subset of the parent's, and its constraints never increase time, uses, bytes, budget, risk or resource surface.

| # | Rule |
|---|---|
| `K-23` | Attenuation narrows. It is idempotent, and the result is a subset of both the parent and the request |
| `K-48` | Resource inclusion is decided by the per-kind relation in `04 §5.3.1`. It is total on the defined pairs and **denies every undefined pair**, including all cross-kind comparisons. A checker returning "unknown" fails closed | 
| `K-24` | Depth is a budget dimension; a child's depth is the parent's plus one, bounded |
| `K-25` | An out-of-scope request is **denied**, recording both what was requested and what was grantable |
| `K-26` | **There is no silent intersection.** Narrowing an over-broad request without saying so is prohibited |
| `K-27` | Denial for scope escalation emits `AuthorizationDenied` as an **alertable** event (`F-10`), never a log line |
| `K-49` | Revocation is immediate, applies to descendants transitively, and emits `CapabilityRevoked`. A revocation leaving no event is indistinguishable from a grant never issued |

> **Why `K-26` is a security rule and not an ergonomic one.** A child repeatedly requesting authority beyond its parent is the single strongest intrusion signal a system of this shape produces. Silent intersection is a design that discards that signal by construction, and it does so while appearing more helpful.

---

## 5. Provenance and the authority predicate

Clause S1(e). This is where the most instructive failure in the project's history lives.

### 5.1 The predicate

> **Untrusted content may inform work; it may never authorise it.**

A violation occurs when a request widens capability **and** any span justifying it carries an untrusted label. Evaluated at S5; violation is `F-09`.

| # | Rule |
|---|---|
| `K-28` | Labels never improve. No operation produces a label lower than its inputs |
| `K-29` | Model output that consumed any untrusted span is untrusted-derived at minimum |
| `K-30` | A tool or environment result is untrusted-external **at construction**, never at consumption |
| `K-31` | Labels are declared **per source class**, never at a call site |

**On `K-31`.** In the prototype, repository content and test tracebacks were labelled as agent-originated because ten call sites across three files each made that judgement independently. Moving the declaration to the source class fixed it structurally: one declaration, no judgement at the point of use. The type-level guard in `04 §3.2` completes it — the assembler accepts context blocks only, so laundering by string concatenation is impossible by type signature.

### 5.2 The two operands, both of which have failed silently

The most important subsection in this document, because the failure mode is a control that is **documented, tested, and inert**.

**First operand — capability widening must be a classifier output.** The prototype hardcoded it to *true* for every subprocess call. The predicate therefore appeared to fail closed on all tool use; every design document in that tree recorded the resulting deadlock as *a property of the taint model*. It was a constant standing in for a classifier that did not exist.

> **`K-32`.** Capability widening is *true* when the request would grant an effect the principal does not already hold, or would escalate outside the perimeter; *false* when the request lies fully within the principal's declared actions and resources and escalates nothing.

Running the test suite under an already-held execution capability escalates nothing and classifies false. An attempt at privilege elevation, egress outside the allowlist, or a write outside the granted resource selector classifies true. **The corresponding must-fail test must fail against a hardcoded value.**

**Second operand — justifying spans must accumulate monotonically.** Tool output is untrusted at birth and is fed back to the model. From the second round onward it can steer a tool call. If the kernel reuses the initial span set, the predicate evaluates over a set that **cannot contain an untrusted span by construction** — the untrusted branch is unreachable dead code. That is exactly what happened. The invariant existed, had a test, and did nothing.

> **`K-33`.** Justifying spans at turn *n* are the union of the spans at turn *n−1*, the spans of the model reply at *n−1*, and the spans of the results at *n−1*. Monotone, never reset within a run. A child operator starts a fresh accumulation, and its **return value** enters the parent's accumulation as untrusted-derived at minimum.

The corresponding must-fail test must fail against a reset: by the second round the span set contains a result span, and the authority branch is demonstrably reachable.

### 5.3 What provenance does not do

It does not prevent untrusted content from **influencing** model output — that is the point, since untrusted content is supposed to inform work. It does not track laundering within a single model reply; the mitigation is that the whole block is already labelled untrusted-derived. It is not a defence against a compromised model. And it does **not establish causation**: you cannot determine from outside a model what justified its action. For sensitive effects the mechanism is intent binding — the effect binds to a brief, a purpose digest and an approval — not inference from attention.

---

## 6. The workload perimeter

### 6.1 The perimeter is the boundary

Restated because it is the most commonly misunderstood point in the design: **the shell classifier is not a security boundary.** It classifies for policy and for the widening computation. What contains an attacker is the perimeter.

| # | Requirement |
|---|---|
| `K-34` | Separate process, mount, IPC and network namespaces; unprivileged user |
| `K-35` | **Only** the granted resource surface is writable. No host mounts, no privileged pseudo-filesystems, no container-control sockets |
| `K-36` | Network denied by default; egress only to an explicit allowlist, **enforced outside the sandboxed process** |
| `K-37` | CPU, memory, process-count and wall-clock limits derived from the lease where dimensionally possible |
| `K-38` | Cancellation kills the **process group**, not the direct child |
| `K-39` | A syscall filter denying process tracing, mounting, key operations, kernel program loading and namespace creation |
| `K-40` | **[AMENDED — ADR-M0-08]** The evaluator runs as a **separate identity outside** the worker's perimeter (UID 10002 daemon over UDS), not co-located inside it. The worker MUST NOT be able to read the evaluator's mount, keys, or signing material |
| `K-41` | The perimeter supervisor is a small, independently auditable, statically linked binary |

**On `K-40` (amended).** The original text called for an asymmetric perimeter with the evaluator *inside* the worker's containment and network denied unconditionally, reasoning that co-location with a stricter policy was safer than a second identity. As-built inverted this: the evaluator runs as a wholly separate OS identity, outside the worker's perimeter, with an unreadability probe proving the worker cannot see it (drift D-32). This is *stronger* isolation for `CL-1` — the judge is not merely policy-restricted inside the candidate's blast radius, it is architecturally unreachable. **`K-40` as originally written (same-perimeter evaluator) MUST NOT be restored.**

### 6.2 Containment is reported, never asserted

A boolean claims a property the runtime cannot verify at that granularity. The perimeter returns a **containment report**: runtime and version, namespace configuration, syscall profile, network enforcement point, writable mounts, exposed sockets, resource limits, the startup probes that were actually run, and the attestation time.

| # | Rule |
|---|---|
| `K-42` | Containment is **verified at startup by probing** — attempt a denied syscall, attempt a denied egress — never inferred from configuration |
| `K-43` | A runtime that cannot verify containment reports that it cannot |
| `K-44` | Where containment is unverified, the publication path **refuses to emit a number**, and the claim records the fact |
| `K-45` | The containment report is part of the instrument tuple. **Two results with differing containment are not comparable** |
| `K-46` | Degrading to an uncontained runtime is permitted for local development and must be visible in every artifact it touches |

> An instrument that reports containment it does not have produces numbers that are worse than no numbers, because they are trusted.

---

## 7. Self-modification

Clause S1(g). The distinction that makes recursive self-improvement discussable without being reckless: **the agent may fabricate its successor; it may not replace its own brain while using it.**

| # | Rule |
|---|---|
**[AMENDED — ADR-M0-10 / drift D-34] `SA-1`…`SA-6` pipeline text struck.** The original release-pipeline detail (candidate artifacts, build/test attestation, canary promotion, tested rollback) described a self-update mechanism that was never built and is explicitly refused going forward (`docs/SPEC.md` §9, honour table: no self-updating release pipeline). D-34 tags this `[NEUTRAL]` — honoured non-build, not a gap. What survives as normative, unconditionally:

**In-place self-modification is prohibited outright.** No model-controlled principal holds a capability reaching the live runtime's files, configuration, keys, or process. A process that rewrites its own running components cannot verify the result with the components it just rewrote, and the failure is not detectable from inside. This is a pure prohibition — there is no companion release pipeline to describe, and none is planned.

**When the optimiser proposes a core change**, which it will: reject the change, record the proposal with its rationale, and escalate it to a human as a design proposal. The *pattern* of repeated proposals is valuable signal about where the core actually limits the system — arguably one of the more interesting outputs the system produces — and it is never a reason to relax the boundary.

---

## 8. Architecture tests

These prove that **paths do not exist**, which is stronger than proving they are not taken.

| # | Assertion | Prevents |
|---|---|---|
| `AT-01` | No module outside the kernel imports an adapter, except the composition root | A second dispatch path |
| `AT-02` | No cognition or adapter module imports the laboratory or the evaluator gate | An agent constructing its own judge |
| `AT-03` | No client module holds an adapter handle or imports the kernel | An inspector that can act |
| `AT-04` | Every observation source declares a static provenance label | Per-call-site provenance judgement |
| `AT-05` | No tool declares a commutativity claim | Commutativity is a property of the resource, not the verb |
| `AT-06` | No kernel or contract module imports cognition, adapters, clients or laboratory | TCB inversion |
| `AT-07` | Every path in the TCB list is covered by a review rule requiring human approval | Silent TCB drift |
| `AT-08` | The policy kernel is within its declared size ceiling | Unauditable growth |
| `AT-09` | Every action class has a case in the dispatcher's table, and every dispatch exit appears in §2.3 | A silently unhandled path |
| `AT-10` | No cast on data crossing a process boundary | Unparsed external data acquiring a type |
| `AT-11` | Every plane that the current phase declares process-separated runs under a **distinct** OS identity and mount namespace, verified at startup against the phase's declared topology (`03 §12`). In Phase 0 that is controller, worker and evaluator; the updater has no runtime component | Plane separation existing only in the documentation |
| `AT-12` | No capability resolves to a path owned by the verifier, the policy configuration, the key store or the updater | Clause S1(c) and S1(g) becoming aspirational |

`AT-11` reads its expectation from the declared phase topology rather than hard-coding four identities, so it is a test that can actually run — and fail — in every phase, rather than one that is aspirational until Phase 1. `AT-11` and `AT-12` are cross-process identity tests and are new in v4. Both predecessors described plane separation and tested only import graphs — which proves nothing about two modules that happen to share a process, a uid and a mount table.

---

## 9. Threat model

### 9.1 Attacker capabilities

**In scope:** control of content in the repository under work, in web or protocol responses, and in dependencies the agent reads; inducing arbitrary model output through any of those; influencing which trajectories enter the corpus through task content.

**Out of scope:** modifying operator configuration; modifying kernel code; a kernel-level container escape; adversarial write access to the blob store. These are untrusted-principal or platform-exploit scenarios, mitigated operationally.

### 9.2 Assets

| # | Asset | Consequence of compromise |
|---|---|---|
| A1 | The verifier | Every number and every trained model becomes worthless. **Catastrophic** |
| A2 | The host system | Standard remote-execution consequences |
| A3 | The principal's authority | Privilege escalation within the run |
| A4 | The budget ledger | Unbounded spend |
| A5 | Competence and memory | Self-reinforcing corruption of all future runs |
| A6 | The training corpus | Poisoned weights — persistent and hard to detect |
| A7 | The release pipeline | Attacker-authored successor promoted with valid attestation |

### 9.3 Attack trees

| # | Attack | Controls | Residual risk |
|---|---|---|---|
| `T-01` | Prompt injection to capability escalation (A2, A3) | `K-30`, `K-32`, `K-33`, `K-34`–`K-41` | An attacker can cause the agent to do anything it was **already permitted** to do. Accepted; bounded by minimal per-principal authority and by the perimeter, not by the predicate |
| `T-02` | Reward hacking to verifier compromise (A1, A6) | Unreachability, the double probe, containment honesty, `AT-02`, `AT-12` | Requires adversarial audit before any training run. Exploiting the judge is the shortest path to reward, and the optimiser will find it without malice |
| `T-03` | Tool escape (A2) | `K-34`–`K-41` | The classifier is deliberately **not** load-bearing. A security argument depending on parsing shell correctly would be a weak one |
| `T-04` | Budget evasion (A4) | `K-04`, `K-07`, `K-13`, `K-24`, `K-25` | A single in-flight call may overrun before commit. Enforcement is eventually exact, never instantaneously exact |
| `T-05` | Memory poisoning (A5, A6) | Four-stage claim pipeline and adversarial ablation (`06 §3`), `K-30` | A record from a genuinely passing run can still encode a bad generalisation. Mitigation is statistical, not architectural |
| `T-06` | Corpus poisoning (A6) | The verifier as sole admission gate; split discipline; containment and modification checks | Contamination discovered late is expensive; the per-instance membership check exists for this |
| `T-07` | **Release-pipeline compromise (A7)** | `SA-3`–`SA-6`, hermetic build, attestation over inputs, signed canary, tested rollback | An attacker who controls the build host controls the successor. This is why `R0` and `R1` have no autonomous path |
| `T-08` | **Recovery-path forgery (A1, A4)** | Recovery controller outside the failed process; reconciliation by idempotency key; `F-22` | An adversary who can forge a heartbeat can keep a dead run apparently alive. Heartbeats are authenticated on the same channel as grants |

`T-07` and `T-08` are new in v4. Neither predecessor modelled the release pipeline or the recovery path as attack surfaces, despite both being components with authority over the live system.

---

## 10. Audit checklist

For a reviewer with one day. Each line has a mechanical answer; an answer that requires a narrative is a finding.

1. Enumerate every path from a model output to an effect. Is it exactly the sequence in §2.1? Does `AT-01` prove it?
2. Is capability widening a classifier call, and does a must-fail test fail against a constant?
3. Do justifying spans accumulate monotonically, and does a must-fail test fail against a reset?
4. Take a granted capability. Name the resource selector. Can it reach the verifier, the policy configuration, the key store or the updater? `AT-12` must answer no.
5. Does an over-broad request produce a denial and an alertable event, or a quiet narrowing?
6. Is containment probed at startup, and does an unverified perimeter block publication?
7. Kill the worker. Who writes the terminal record? Is an undeterminable external effect recorded as undeterminable?
8. Show a grant crossing a process boundary. Is it authenticated?
9. Do the four planes run under distinct identities at runtime, or only in the diagram?
10. For every control in this document, name its must-fail test. **A control without one is not a control.**

> **Outstanding obligation.** The rule-to-test map does not yet exist: `08 §5` owns the must-fail suite and is unwritten. Until `CI-9` passes, every rule in this document is *asserted and unproven*, which is a weaker position than this document's tone implies. No rule here may be cited as an established control before its test exists.
