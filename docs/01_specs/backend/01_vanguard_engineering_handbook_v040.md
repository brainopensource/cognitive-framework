---
id: VG-01
file: 01_vanguard_engineering_handbook_v040.md
title: "Vanguard v4.0 — Engineering Handbook"
version: 4.0.0
status: LIVING
authority_scope: >
  Mental models; SOLID and DRY as practised in this codebase; the shape of a
  change; the testing taxonomy; the review checklist; ADR format; repository
  layout and dependency direction; the glossary.
supersedes: none (v4 is the first version of this document)
superseded_by: none
budget_words: 4000
owners: [Tech Lead]
last_reviewed: 2026-08-14
---

# Vanguard v4.0 — Engineering Handbook

> **Who this is for.** An engineer who has read `02` and `03` and is about to write code. It states nothing normative — every rule here belongs to another document — but it is where you learn *how to work* in this tree.

---

## 1. Nine mental models

Internalise these and most design questions answer themselves.

### M1 — The episode is the program

There is no workflow engine, no topology language, no graph validator. There is a loop that observes, proposes, gets authorised, acts, and reduces. If you find yourself declaring a shape for the work **before** the work runs, you are building the thing `03 §2` rejected.

### M2 — Everything pluggable is one of exactly four things

Observation source, cognitive operator, effect adapter, evaluator. A proposal to add a fifth is a design review, not a pull request. If your new capability does not fit, either it is one of the four wearing a disguise, or the taxonomy is wrong — and the second is a conversation, not a commit.

### M3 — The broker grants; the sandbox contains

Two distinct boundaries, and confusing them is the most common serious error in this domain. The broker decides *whether* an effect is permitted. The perimeter decides *what an attacker can reach when the broker was wrong*. A logical mediator in the host language is not containment. See `05 §6.1` before writing anything near this.

### M4 — Content carries provenance; provenance constrains authority

Untrusted content may **inform** work — reading a repository is the whole point — but may never **authorise** a capability-widening action.

> **The trap:** this control is easy to implement in a way that looks correct and does nothing. It has happened twice. Read `05 §5.2` before touching anything near it.

### M5 — The verifier is outside everything

Nothing the system can modify may judge the system. If you find yourself writing code that lets an agent path reach the verifier, its image, or its injected inputs, **stop** — you have found a bug in your design, not a limitation to work around.

### M6 — A gate that cannot fail is not a gate

Every check, invariant and test: if it has never been observed failing against a broken implementation, you do not know it works. This is why `test/broken/` exists in the tree rather than as a comment.

**Its twin, and the newer half:** a requirement that cannot be satisfied is not a requirement. Before writing a test, ask whether the thing being demanded is physically possible. *"A dying process emits a terminal event"* passed review, had a test, and was satisfiable only against a graceful-shutdown mock.

### M7 — Competence is the persistent object

Not the conversation, not the prompt, not a snapshot of ability. An immutable graph of artifacts with an evidence graph saying where each holds and what would refute it. When you are tempted to store something, ask which store it belongs in (`06 §2`) and what would invalidate it.

### M8 — One document is normative per contract

If you find the same rule stated in two places, that is a defect, not redundancy. Delete the copy; do not reconcile the wordings. The registry (`00 §1`) resolves ownership.

### M9 — Minimise what must be simultaneously correct before the first signal

Premature formalisation is indistinguishable from rigor at the moment of the decision, and distinguishable only in hindsight, by how long the first feedback signal took to arrive. Ask of every plan: **how many things must be simultaneously correct before anything tells us we are wrong?** Collapse that number rather than lowering the ceiling.

**The standing exception:** the kernel, verifier and capability boundary stay at full rigor. They are the only thing between *self-improving* and *self-deceiving*, and deferring them costs more than building them.

### M10 — Polyglot plugins outside the TCB (The Narrow Waist Wire Law)

The microkernel and state ledger are minimal, deterministic, and language-neutral in their wire representation. Domain computation (Tree-sitter indexing, browser automation, microVM sandboxes, vector engines) or plugins in Rust, Go, TypeScript/Node, or Python must execute strictly outside the TCB, communicating across port boundaries via standard wire contracts (stdio, JSON-RPC, IPC, Unix domain sockets). The TCB never imports an external plugin runtime.

### M11 — The Generality Falsification Invariant

The core loop and microkernel must remain 100% agnostic to task domains. Coding is merely a configuration manifest (`vg-code-default`). Adding a research, legal, medical, or robotics task must require zero lines of code modified in `vanguard/packages/kernel/` or `vanguard/packages/agency/episode/`.

---

## 2. SOLID, concretely, here

SOLID stated abstractly is unfalsifiable. Here is what each means in *this* codebase, with the specific violation to watch for.

**Single responsibility** — a module has one reason to change; the layer lattice (`03 §4`) is this at package scale.

| Good | Violation |
|---|---|
| The assembler builds a prompt. It does not fetch, dispatch or decide | An assembler calling an observation source directly instead of receiving blocks |
| The governor accounts for budget and holds no opinion about policy | A governor denying based on effect class — that is policy's job |
| A tool executes one effect | A "smart edit" tool that reads, decides and writes |

*The smell:* you cannot name the module's job in one clause without "and".

**Open/closed** — adding a capability is a registry entry plus a configuration line. The loop, the dispatcher and the schemas do not change.

> *The violation to catch in review:* a change adding web search that also touches the loop. That is the abstraction leaking, and it is exactly the check that keeps `02 [C-02]` honest.

**Liskov substitution** — every implementation of a port is interchangeable **including in its failure behaviour**. This is where it usually breaks and where it matters most.

| Port | Substitutability contract |
|---|---|
| `ModelProvider` | Never throws for a provider-side failure; returns an instrument error. A provider that throws on a rate limit is not substitutable, and inconclusive handling silently breaks |
| `EvaluatorPort` | Never throws. Cannot verify implies inconclusive, **never** a pass |
| `SandboxRunner` | The containment report reflects reality. A runner claiming containment it lacks is not substitutable — it is lying |
| `EnvironmentAdapter` | Returns a typed result for every outcome, including denial |

*The rule:* the type signature is the easy half of a contract. **The failure mode is the half that breaks substitution.**

**Interface segregation** — ports are small and role-specific. Ten narrow interfaces, not one runtime god-object. *The violation:* a workspace that also stores blobs "because it already has filesystem access" — now every workspace implementation must implement blob storage, and the two evolve together forever.

**Dependency inversion** — kernel and cognition depend on ports, never on adapters. Only the composition root knows concrete implementations, and it knows them for exactly one function call. This is what makes `02 [C-03]` true: swapping an implementation language touches one adapter file. Enforced mechanically by the boundary gate and by `05 [AT-01]`/`[AT-06]`, never by discipline.

### 2.1 DRY, and where it turns into a trap

DRY applies to **knowledge**, not to text that happens to look similar.

| Genuinely DRY | Harmful "DRY" |
|---|---|
| Provenance labels declared once per source class | A shared base class three unrelated tools inherit for two helper methods |
| Canonicalisation implemented once per language, driven by shared vectors | Merging `read` and `glob` because both touch the filesystem |
| One definition of the patch: the environment's own diff | A generic effect handler with a kind switch — that is the dispatcher, and it already exists |

**The clearest historical win:** a lookup table that shadowed the type system, requiring a test to check the shadow against the original. Two representations of one fact. The fix was deleting the table, not testing it harder.

---

## 3. The shape of a change

```
1. UNDERSTAND    Which layer? Which document says what the behaviour should be?
2. WRITE THE TEST FIRST   ...and watch it fail. If it passes, you misunderstood.
3. SMALLEST CHANGE        Make the test pass. Nothing else.
4. CHECK THE BOUNDARY     Did you touch a layer you did not intend to?
5. ADR?                   Would this decision otherwise be tribal knowledge?
6. COMMIT                 The message says WHY. The diff says what.
```

**Step 2 is not negotiable.** A test written *after* the implementation is written against the implementation's assumptions, so it validates that the code does what the code does. **Watching a test fail first is the only evidence that it tests anything.**

**Commit messages** carry three things — what layer, why, and what proves it:

```
kernel: release lease before emitting on the exception path

If the emit raises while the lease is held, the lease leaks and the run
ceiling is permanently reduced. Ordering rule 05 [K-06].

Test: kernel/test/dispatch.leak.test.ts — fails against test/broken/emit-first.ts
```

If you cannot write the "why", you may not yet understand the change.

---

## 4. Testing taxonomy

Seven kinds, each answering a different question. Confusing them is why suites get slow and prove little.

| Kind | Answers | Speed |
|---|---|---|
| Unit | Does this function do what it says? | ms |
| Property | Does this algebraic law hold for arbitrary inputs? | ms |
| Vector | Do the implementations agree byte-for-byte? | ms |
| Must-fail | Can this control actually fail? | ms |
| Fault injection | Does every failure path in `05 §2.3` behave as specified? | ms |
| Cassette | Does the harness still behave as on this recorded real interaction? | seconds |
| Live canary | Do real models emit what our parsers expect? | slow, costs money |

### 4.1 Mock, cassette, live

The most important idea in this section, and it generalises well beyond this project.

> **A mock built by reading your own consumer code proves the harness is self-consistent. It cannot prove the harness agrees with a real endpoint.** Any parser assumption a real model would violate is precisely the shape the mock was taught to avoid.

A predecessor shipped a tool loop missing both the assistant tool-call message and the call identifier on results — a hard requirement of every compatible endpoint. It survived review because *that path had only ever run against mocks returning no tool calls.*

| Path | Answers | Cannot answer |
|---|---|---|
| Mock | Given a known output, does the harness do the right thing? | Whether a real model would emit that output |
| Cassette | Does behaviour still match this recorded interaction? | Anything about a prompt that just changed |
| Live canary | Do real models emit what our parsers expect? | Anything cheap, fast or deterministic |

**Canary rules:** asserts **wire shape, never task outcome**; pre-merge only; deselected from the inner loop. A task failure in a canary is not a gate failure — it is a model having a bad day.

### 4.2 The satisfiability check

Before writing a test, ask whether the requirement is physically achievable. If the only implementation that passes is a mock of the failure mode, the requirement is wrong. Fix the requirement, then write the test.

### 4.3 What not to test

Schema libraries doing what they do; getters, constructors and trivial delegation; adapter internals the port contract already pins. **A test that has never failed and cannot fail is a maintenance cost with no benefit.** Delete it.

---

## 5. Practices

| Practice | Why it saves time |
|---|---|
| Parse at the boundary, never cast | External data acquires its type by parsing. One cast becomes six hours debugging a field that was never there |
| Fail at composition, not at first use | An unknown name should crash at startup, not in turn fourteen of a paid run |
| Make illegal states unrepresentable | The assembler taking context blocks and not strings makes provenance laundering a type error rather than a review catch |
| Trajectory over logging | You already emit structured events. `vg trace <runId>` beats adding a print statement and re-running |
| Cassettes for the inner loop | Deterministic, free, fast. Re-record when prompts change, not before |

**When you are stuck:** re-read the document that owns the contract before rewriting code. Most confusion in this tree is a contract question wearing an implementation costume.

**Working agreements.** Trunk-based with short-lived branches; every fix ships with a test proven to fail against pre-fix code; kernel changes get a second pair of eyes; an ADR when a decision would otherwise be tribal knowledge; **no status document** — the ticket table in `08 §3` is the status; and weekly, thirty minutes, three questions: what merged, what is blocked, **has anything changed our mind about `02`–`07`?** The third matters most.

---

## 6. Review checklist

| # | Check |
|---|---|
| 1 | Does the change touch only the layer it should? |
| 2 | Is there a test, and was it watched failing first? |
| 3 | Does a new capability touch the loop or the dispatcher? If so, why? |
| 4 | Does any new external data acquire its type by cast rather than parse? |
| 5 | Does any new failure path leave a lease held? |
| 6 | Does a new source declare its provenance label at the class, not the call site? |
| 7 | **Are there special cases?** A conditional naming one environment, one provider or one task type is the generality constraint (`02 §8`) failing quietly |
| 8 | If a rule changed, does its entry in the rule-to-test map still hold? |

Item 7 is the one reviewers skip. A special case is how the coding track captures the general abstraction, and it always arrives disguised as pragmatism.

---

## 7. ADR format

Decision, context, alternative rejected, **reversal condition**, status. The reversal condition is what converts a decision from dogma into a hypothesis with an expiry.

**State the losing alternative fairly enough that its advocate would recognise it.** A register recording only winners cannot support a reversal, because the reader has no idea what to reconsider.

Write one when a competent engineer arriving in six months would be surprised and unable to reconstruct why. Not for every choice — a register of everything is a register nobody reads. Entries live in `09`; deferrals and rejections in `10`.

---

## 8. Repository layout

```
vanguard/
├── packages/
│   ├── wire-schema/       schemas, semantic rules, vectors, reader profiles
│   ├── domain/            pure types and reducers, no I/O
│   ├── ports/             interfaces only
│   ├── policy-kernel/     capabilities, grants, budgets, dispatch
│   ├── controller/        episode lifecycle and recovery
│   ├── agency/            the loop, context assembly, playbooks
│   ├── adapters/
│   │   ├── environments/  git, tableworld
│   │   ├── operators/     model, deterministic
│   │   ├── evaluators/    coding, tableworld
│   │   └── stores/        event store, blob store, export
│   ├── runtime/           composition root and daemon
│   └── cli/               vg run, vg trace
├── lab/                   offline; consumes exports only
├── schemas/v4/            normative artifacts and golden vectors
├── docs/
│   ├── v4/                the document set + generated rule-test map
│   └── adr/               append-only from day one
├── test/broken/           deliberately broken implementations
└── tools/                 wordcount, audit, reader-profile, rule-test-map
```

**Dependency direction is enforced, not documented** (`03 §4`): domain ← ports ← kernel ← agency ← runtime → adapters, cli → runtime. `lab/` imports nothing and is imported by nothing.

---

## 9. Glossary

| Term | Meaning |
|---|---|
| **Episode** | The unit of execution: task, snapshot, activation set, budget, policy |
| **Effect** | Anything that changes state outside the process, or reads from outside it |
| **Descriptor** | The canonical digest of a call; input to loop detection, policy caching and grant binding |
| **Grant** | A scoped, expiring authorisation binding a principal, actions, resources and a purpose |
| **Attenuation** | Deriving a child authority that is a subset of its parent's |
| **Lease** | A reservation against a budget dimension, released on every path |
| **Provenance** | Six orthogonal axes describing where content came from and what it may do |
| **Context block** | The only type admissible into context assembly |
| **Operator** | A versioned artifact producing a proposal; data, not control flow |
| **Playbook** | Methodology as data, with a rigidity dial |
| **Competence artifact** | An immutable, content-addressed node in the competence graph |
| **Evidence claim** | A scoped assertion with validity, uncertainty and invalidation conditions |
| **Activation set** | The artifacts valid for the current context |
| **Instrument tuple** | The complete configuration that produced a result |
| **A/A floor** | The variance of a configuration compared against itself |
| **Containment report** | What the perimeter actually enforced, probed rather than asserted |
| **Inconclusive** | The instrument did not work. Never a task verdict |
| **Candidate** | A proposed successor artifact with no operational authority |

---

## 10. Ten rules, if you remember nothing else

1. One path from a proposal to an effect. Never a second.
2. Untrusted content informs; it never authorises.
3. The verifier is outside everything you can change.
4. A gate that cannot fail is not a gate.
5. A requirement that cannot be satisfied is not a requirement.
6. Parse at the boundary; never cast.
7. Fail at composition, not at first use.
8. Release the lease on every path, including the one you did not plan for.
9. If a rule appears in two documents, delete one.
10. If it needs a special case, the abstraction is wrong — or you are about to lose the general system to the coding track.
