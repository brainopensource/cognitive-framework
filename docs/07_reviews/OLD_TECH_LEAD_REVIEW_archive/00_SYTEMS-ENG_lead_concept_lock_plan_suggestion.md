VANGUARD / AETHER v0.6 — PRINCIPAL SYSTEMS VERIFICATION & INVARIANTS CONCEPT LOCK REVIEW
Document: `00_SYTEMS-ENG_lead_concept_lock_plan_suggestion.md`  
Role: Principal Systems Verification & Invariants Engineer / Distributed State Machine Specialist / Formal Systems Safety Architect  
Engagement: ANALYSIS-ONLY  
Target: Vanguard / AETHER Substrate v0.6 Concept Lock  
Date: 2026-08-20  
Modification rule: No production code, SPEC, ADR, annex, roadmap, milestone, backlog, sprint, CI, or existing review was modified. This report is the sole artifact produced.
Evidence convention
This fifth review is independent in analysis, but it operates over the supplied evidence corpus rather than a live repository checkout. The corpus includes `SPEC.md`, the v0.6 execution/refactor proposals, the Concept Lock BETA, the Principal Architect review, Independent Tech Lead review, AI Agentic Systems review, and the larger technical synthesis. The Tech Lead and AI reviews contain explicit command output and `file:line` findings from the live tree; those observations are treated here as reported as-built evidence, not as commands re-executed by this reviewer.
Accordingly:
`[FACT]` means directly stated by the normative SPEC or explicitly evidenced in the supplied review corpus with source/command detail.
`[INFERENCE]` means a reasoned consequence of those facts.
`[INVARIANT PROOF]` means a conditional proof: the guarantee follows if all enumerated premises are enforced.
`[COUNTEREXAMPLE / HAZARD]` means a concrete execution or crash sequence that violates a claimed invariant.
`[VERIFICATION RECOMMENDATION]` means a lock/gate/schema rule needed to make a claim provable.
`[UNKNOWN / EXPERIMENT REQUIRED]` means the evidence corpus is insufficient to prove the property.
The central question is not whether the proposed design is elegant. It is whether a hostile scheduler, crash, race, malformed selector, duplicated refund, stale verdict, mutable in-process plugin, or replay boundary can make the substrate assert a state that is false while its own tests remain green.
---
1. Executive Summary & Verification Verdict
1.1 Verdict
SYSTEMS VERIFICATION VERDICT: CONDITIONAL ACCEPT FOR CONCEPT LOCK; NO-GO FOR CLAIMED MATHEMATICAL GUARANTEES AS CURRENTLY STATED.
The architectural direction is defensible: one Python-first single-node substrate, SQLite WAL, a narrow S0–S12 effect mediation spine, an exterior signed evaluator, declarative harness identity, recursive spawning under attenuation, and sequential execution until concurrency can be proven. The supplied evidence also shows that the mature `vanguard/packages/` tree already contains several of the correct mechanisms: a WAL-backed event store, a real exterior evaluator, rootless sandboxing, a real recursive `spawn()`, parent grant/lease lineage, and a much larger behavioral test base.
However, the stronger claims in the proposed v0.6 thesis are not yet mathematically established. Several are false or under-specified if read literally:
`[FACT]` The CI-gated `layer0/` path has been reported to use an in-memory ledger, fabricate a passing verdict, discard the harness capability ceiling, contain a weaker duplicate selector algebra, omit material lineage, and run a replay-parity test that folds the same event list twice. Those are direct counterexamples to the claim that the new substrate already enforces replay truth, exterior evaluation, and capability confinement.
`[INFERENCE]` `state = fold(events)` is necessary but not sufficient. A perfectly deterministic fold over forged or semantically synthetic events reconstructs fiction deterministically.
`[INFERENCE]` `Capabilities(child) ⊆ Capabilities(parent)` is not a proof until there is exactly one selector partial order, fail-closed defaults, complete mediation of all privileged effects, and no alias/symlink/shell path that creates effective authority outside the represented selector.
`[COUNTEREXAMPLE / HAZARD]` The six-dimensional `Reservation = {usd_micros, millis, tokens, bytes, turns, depth}` does not form one homogeneous additive conservation algebra. `depth` is an ordinal/path ceiling, not a fungible quantity to be summed across siblings; wall-clock `millis` is also not additive under parallel execution unless it is explicitly defined as charged compute time. A proof written as `Σ B_child ⪯ B_parent` over all six dimensions is therefore mathematically unsound.
`[INFERENCE]` Bernstein independence over read/write selectors is sound only if selectors are a conservative over-approximation of the actual resource footprint. Dynamic shell commands, symlink/hardlink aliases, environment reads, git index state, network endpoints, mutable service state, and hidden runtime dependencies can make static sets incomplete. Unknown footprint must therefore mean conflict, not independence.
`[INFERENCE]` An Ed25519 signature proves origin/integrity of a verdict, not validity of the oracle. In addition, a valid signed verdict is replayable unless the signed statement is bound to the exact evaluation request, subject digest, oracle version, execution/experiment identity, and a one-time request identifier.
`[COUNTEREXAMPLE / HAZARD]` “The ledger is authoritative” does not imply “the orchestrator cannot forge authoritative state.” If an orchestrator can directly append `CapabilityGranted`, `BudgetReleased`, `VerdictRecorded`, or other privileged event kinds, it can manufacture authoritative history that replays perfectly. Event-kind writer authority must be enforced at the ledger append boundary.
1.2 What is safe to lock now
`[VERIFICATION RECOMMENDATION]` The v0.6 Concept Lock should lock semantics and proof obligations, not claims of already-proven implementation:
one canonical event writer/ordering rule per consistency unit;
pure/total reducers and deterministic cold replay;
durable intent before external effect;
explicit recovery of undeterminable effects;
one capability/selector algebra with fail-closed attenuation;
additive resource conservation separated from structural limits such as depth/deadline;
point-of-effect revocation semantics;
event-kind authority matrix;
exterior verdict request binding and anti-replay;
sequential execution until selector soundness and race tests pass;
full composition/execution/experiment identity.
1.3 What must not be claimed yet
`[VERIFICATION RECOMMENDATION]` Do not claim any of the following as established properties of the current implementation:
mathematically proven replay parity;
exactly-once external effects;
fully monotonic capability confinement under all tool aliases;
six-dimensional additive budget conservation;
safe concurrent dispatch;
absolute revocation of in-flight effects;
non-subvertible evaluation in the epistemic sense;
orchestrator inability to forge ledger truth without enforced writer scoping.
The correct v0.6 statement is narrower and stronger: the design defines falsifiable invariants and refuses to enable behavior that cannot yet satisfy them.
---
2. Systems Verification Mandate & Independence Statement
This review is the fifth lane after:
Principal Staff Engineer;
Independent Tech Lead;
Principal Architect;
AI Agentic Systems Specialist;
Principal Systems Verification & Invariants Engineer — this report.
The prior lanes strongly converge on Python-first convergence, recursive agency, an exterior evaluator, a wire-first plugin boundary, event-derived state, and sequential execution before concurrency. This review does not reopen those decisions for aesthetic reasons. It tests whether their formal safety claims actually follow from the proposed mechanisms.
The review therefore uses a different unit of analysis. Instead of asking “which architecture is best?”, it asks:
What is the linearization point of an authority-changing operation?
What survives SIGKILL at each instruction boundary?
Which state transitions are legal and who may emit them?
Can a child acquire effective privilege not representable as a syntactic subset?
Can two idempotent-looking cleanup paths refund the same reservation twice?
Is the stated budget relation even an algebra under the chosen dimensions?
Does a selector describe all hidden reads/writes an effect can perform?
Does revocation mean termination, prevention of new dispatch, or both?
What exactly is signed by the evaluator, and can the signature be replayed?
Can a coordination process forge the authoritative log while still satisfying replay parity?
`[INFERENCE]` The highest-risk failure mode in Vanguard is not a loud crash. It is a self-consistent false history: the system records an event that is structurally valid, the hash chain is valid, replay succeeds, and yet the event did not represent the external reality, authority decision, budget settlement, or evaluation that the event claims. The reported hard-coded `verdict: "pass"` is the canonical example.
---
3. Core Substrate Invariant Checklist (Pass / Fail / At-Risk)
Invariant	Current evidence verdict	Systems assessment
1. Deterministic State Folding — `State_t = fold(E_1..E_t)` across crash/reboot	FAIL / AT-RISK	Packages reportedly has a real SQLite WAL store; `layer0` reportedly uses memory-only storage, drops committed budget in fold, and has tautological replay parity. Target is provable, current corpus does not prove it.
2. Strict Monotonic Capability Attenuation — `C_child ⊆ C_parent`	FAIL on reported layer0 path; AT-RISK globally	Real attenuation exists in packages, but the new compiler reportedly drops capability ceilings, empty ceilings fail open, and a second weaker selector algebra exists.
3. Strict Budget Conservation	AT-RISK	Parent lease lineage exists, but a formal refund/concurrent settlement proof is absent, and the 6-D vector mixes additive and non-additive dimensions.
4. Sound Selector Independence — Bernstein conditions	AT-RISK, execution currently safe only because sequential	Algebra exists, but static completeness of footprints is not proven. Concurrency should remain disabled.
5. Non-Subvertible Evaluation	FAIL on reported layer0 path; PARTIAL PASS in packages	Packages reportedly has UID-separated Ed25519 evaluator. Layer0 reportedly fabricates `pass`. Signature authenticity still does not prove oracle validity or replay binding.
6. Safe Revocation Semantics	AT-RISK	Cascading grant revoke is reported, but in-flight process/network semantics and the linearization point are not fully locked.
7. Separation of Truth — orchestrator cannot forge ledger truth	FAIL AS A FORMAL CLAIM unless writer scoping exists	“Ledger is truth” is insufficient if policy/orchestrator code can append privileged event kinds directly. Writer authority must be enforced by kind.
8. CAS Referential Integrity	AT-RISK	SPEC requires `write→fsync→emit(digest)`; directory fsync/read verification/GC and atomic relation to SQLite require explicit semantics.
9. Crash-Safe Effect Dispatch	PARTIALLY DEFINED	Intent-before-effect is correct. Exactly-once is impossible for arbitrary external effects; reconciliation/idempotency semantics must be the contract.
10. Identity/Attribution Completeness	FAIL on reported layer0 path	Prior reviews report missing/dropped lineage and incomplete harness digest. This invalidates scientific attribution and multi-agent reconstruction.
Checklist conclusion
`[INFERENCE]` The substrate is not ready to be described as “formally verified.” It is ready to be described as verification-oriented, provided the Concept Lock records the exact invariants below and refuses feature activation before their falsifiers pass.
---
4. Formal Analysis of State Machine & Ledger Semantics
4.1 Required state model
Define a consistency unit `p` (the proposed `project_id`) with authoritative event stream:
[
L_p = \langle e_{p,1}, e_{p,2}, \ldots, e_{p,n} \rangle
]
and reducer:
[
\delta : \Sigma \times E \rightarrow \Sigma
]
The authoritative state is:
[
S_{p,n} = \operatorname{fold}(\delta, S_{p,0}, L_p)
]
For deterministic state replay, the following are all necessary:
Totality: every reachable event kind is handled, or explicitly rejected as schema/version incompatible.
Purity: reducers perform no I/O, clock reads, RNG calls, environment reads, model calls, or mutation outside the returned state.
Determinism: equal input state + equal canonical event bytes produce equal output state.
Completeness: every fact that can change authoritative state is represented by an event.
Order determinism: the ledger exposes one unambiguous commit order inside the chosen consistency unit.
Durability: once an event is reported committed, a crash/reboot does not erase it.
Writer legality: only the authority assigned to an event class may create that event.
Semantic truthfulness: payloads are derived from real decision/effect/evaluator outputs, not constants that merely satisfy schema/gates.
`[INVARIANT PROOF]` If (1)–(8) hold, cold folding of the committed stream yields one authoritative state for that stream. This proves state reconstruction, not real-world re-execution equivalence.
4.2 The ledger is not made truthful by hashing
`[COUNTEREXAMPLE / HAZARD]` Suppose the scheduler appends:
```text
VerdictRecorded(subject=X, pass=true, signature="synthetic")
```
and the reducer deterministically incorporates it. The hash chain is valid; SQLite durability is valid; replay parity is valid. Yet the history is false because no exterior evaluator produced the verdict.
Therefore:
[
\text{HashIntegrity} \not\Rightarrow \text{SemanticTruth}
]
and:
[
\text{ReplayParity} \not\Rightarrow \text{Correctness}
]
`[VERIFICATION RECOMMENDATION]` Every authority-bearing event kind needs a construction rule and a writer owner. The event store must not expose a generic “append any valid event” capability to untrusted coordination policy.
4.3 Event-kind authority matrix
At minimum:
Event class	Sole authority allowed to originate it
Proposal / reflection	planner boundary via scheduler
Capability grant/attenuation/revoke	kernel grant authority
Budget reserve/commit/release/exhaust	kernel governor
Effect intent/start/terminal/reconcile	kernel effect mediator / reconciler
VerdictRecorded	verified evaluator gateway only after signature + request binding
ApprovalResolved	approval authority
Plugin lifecycle	registry supervisor
Run/episode lifecycle	scheduler mechanism, not arbitrary orchestrator policy
Promotion	separate governance/promotion authority, deferred
`[VERIFICATION RECOMMENDATION]` Enforce this at the append API using typed writer capabilities or separate writer interfaces. A policy plugin may request a transition; it must not directly manufacture the resulting authoritative event.
4.4 Sequence and hash-chain linearization
For each `project_id`, event `n` should satisfy:
[
seq_n = seq_{n-1} + 1
]
[
prev_digest_n = digest_{n-1}
]
[
digest_n = H(JCS(envelope_n \setminus digest_n))
]
`[INVARIANT PROOF]` On single-node SQLite, if the next sequence/head is read and the new row inserted within the same `BEGIN IMMEDIATE` transaction, and a uniqueness constraint exists on `(project_id, seq)`, then concurrent writers serialize at the SQLite writer lock. If the transaction also verifies `prev_digest == current_head`, two committed events cannot legally share the same predecessor within that project stream.
`[COUNTEREXAMPLE / HAZARD]` A process-local `_seq` / `_prev` cache not reconstructed from durable storage can fork after restart or under multiple writer objects. Prior reviews report exactly this risk in the `layer0` envelope factory.
`[VERIFICATION RECOMMENDATION]` The durable store, not an in-memory envelope factory, owns the authoritative chain head.
---
5. Crash Recovery, WAL Guarantees & Outbox Atomic Boundaries
5.1 Correct effect transaction boundary
The fundamental safety rule is already directionally correct:
```text
Durable intent commit
    BEFORE
external effect dispatch
```
A safe single-node sequence is:
validate request/grant/policy/budget;
atomically reserve budget and append the durable effect intent in SQLite;
commit the transaction under WAL + `synchronous=FULL`;
only after successful commit, dispatch the external effect;
capture a receipt or classify the effect as undeterminable;
append terminal effect event + budget settlement atomically;
expose completion to the caller only after terminal commit.
`[INVARIANT PROOF]` If no external effect is dispatched before step 3 commits, then a crash before the durable intent cannot create an invisible external effect.
5.2 Crash matrix
Crash point	Durable state	External reality	Required recovery behavior
Before reservation/intent transaction	nothing	nothing	restart command safely
During uncommitted SQLite transaction	rollback	nothing	restart command safely
After intent commit, before dispatch	open intent	effect not started	reconcile/probe; may dispatch if policy can prove not executed
During dispatch, before receipt observed	open intent	unknown	mark `undeterminable`; reconcile, do not blindly retry
Effect completed externally, before terminal ledger commit	open intent	effect may have happened	reconcile by idempotency/probe; terminal event derived from reality
Terminal event + settlement transaction in progress	either old or new DB state	effect already happened	transaction rollback/commit yields one durable settlement state
After terminal commit, before caller sees response	terminal committed	happened	command retry must return prior terminal result via idempotency key
`[VERIFICATION RECOMMENDATION]` The event name `EffectStarted` must be normatively defined as “durable dispatch intent committed”, not proof that an OS process or remote operation has actually started. If actual-start evidence matters, represent it separately.
5.3 Outbox semantics
For commands/events that trigger local asynchronous dispatch, use an outbox row in the same SQLite transaction as the authoritative intent/reservation. The dispatcher reads only committed outbox rows.
However:
`[INFERENCE]` An outbox does not make arbitrary external effects exactly-once. If the remote side does not support idempotency or querying, a crash after the remote side-effect but before local acknowledgement leaves irreducible uncertainty.
Therefore the correct invariant is:
> Every external effect is either terminally recorded, explicitly `undeterminable`, or reconciled; no undeterminable effect is silently retried as if nothing happened.
5.4 Idempotency boundary
Every command-derived effect should have a stable idempotency key bound to:
```text
(project_id, command_id/effect_request_digest, target adapter identity)
```
The ledger must reject two logically distinct terminal settlements for the same key.
`[VERIFICATION RECOMMENDATION]` For adapters that can guarantee external idempotency, pass the same key across retries. For adapters that cannot, reconciliation must precede retry.
5.5 WAL scope
`[FACT]` The normative design requires SQLite WAL + `FULL` synchronization. This is suitable for the stated single-node target.
`[INFERENCE]` The durability claim remains scoped to the SQLite database and the host/storage threat model. It does not atomically include an independent filesystem CAS, remote provider, or subprocess side effect. Those boundaries need ordered protocols, not a fictitious cross-system transaction.
---
6. Deterministic Replay vs Non-Deterministic Re-Execution
6.1 Three distinct claims
The project must keep these claims separate:
A. State replay
[
ReplayState(L_p) = fold(L_p)
]
This must be deterministic.
B. Schedule/fixture replay
Given recorded clock/RNG/model/tool inputs and a recorded schedule:
[
ReplayFixture(inputs, schedule) \rightarrow same\ canonical\ trajectory
]
This may be required for controlled fixtures.
C. Live re-execution
Calling a remote LLM, network API, wall clock, or nondeterministic tool again does not need to produce the same bytes.
`[VERIFICATION RECOMMENDATION]` Never define replay by re-calling the outside world. Replay consumes recorded facts from the ledger/CAS/cassettes.
6.2 Nondeterminism capture rule
Any nondeterministic value that influences authoritative state must be one of:
an event payload;
a referenced CAS blob whose digest is in the event;
a deterministic derivation of prior events;
a recorded cassette keyed to immutable identity.
Examples:
wall-clock time used for lease expiration → emit/record the expiration decision or injected clock value;
RNG used for routing → record the chosen value/seed and algorithm identity;
model output → store exact bytes/digest/receipt, not re-infer on replay;
external API response → receipt/blob digest;
scheduler interleaving → recorded order if schedule replay is a requirement.
6.3 Replay-parity gate
`[FACT]` Prior reviews report that the current `layer0` replay-parity test folds one list twice and therefore proves almost nothing.
A valid gate must:
execute a real fixture through the production path;
maintain live state via normal production projections;
close/discard all live in-memory state;
open a cold reader from the durable ledger;
rebuild state from sequence zero;
structurally diff at least grants, budget, approvals, episode/run lifecycle, plugin routing, lineage, and terminal effects;
fail on any mismatch.
`[VERIFICATION RECOMMENDATION]` Mutation-test this gate: delete a reducer update for `BudgetCommitted`; replay parity must fail.
---
7. CAS Blob Storage vs Ledger Event Boundary Audit
7.1 Authority split
The correct boundary is:
```text
Ledger = authoritative facts, identity, causal references, authority, settlements
CAS    = immutable content bytes referenced by digest
```
A large blob should not become authoritative merely because it exists in CAS. Its use becomes authoritative only when a ledger event references its digest under a defined event type.
7.2 Safe CAS write protocol
For a local filesystem CAS:
compute content digest over exact bytes;
write to a temporary file in the target filesystem;
`fsync()` the file;
atomically rename to the digest path;
`fsync()` the containing directory where required by the durability model;
optionally read/verify digest for critical evidence;
only then commit the ledger event referencing the digest.
`[INVARIANT PROOF]` With this order, a crash can leave an orphan blob with no ledger reference, which is safe and GC-able. It must not leave a committed event referencing bytes that were never durable.
7.3 SQLite + CAS are not one ACID transaction
`[COUNTEREXAMPLE / HAZARD]` If the ledger event commits first and the CAS write fails, authoritative history references missing evidence.
`[VERIFICATION RECOMMENDATION]` Prefer “blob first, ledger reference second.” Accept orphan blobs as the cost of not having a distributed transaction between SQLite and the filesystem.
7.4 CAS integrity requirements
digest is computed over bytes, not path or metadata alone;
digest is verified on read for critical signed/evaluation evidence;
immutable digest paths are never overwritten;
GC is reachability/retention based and cannot race a not-yet-committed reference without a grace period;
signed verdict evidence should bind the digest of any external evidence bundle it relies upon.
---
8. Formal Capability Attenuation Algebra & Privilege Confinement
8.1 Capability model
A capability should be modeled as a finite set of grants:
[
C = {g_1, g_2, \ldots, g_n}
]
where each grant is at least:
[
g = (verb, selector, constraints, expiry/lease, provenance)
]
Define `covers(g_parent, g_child)` as the canonical authority partial order. Then:
[
C_{child} \preceq C_{parent}
]
means:
[
\forall g_c \in C_{child}, \exists g_p \in C_{parent}: covers(g_p,g_c)
]
A simple syntactic set inclusion is insufficient because two different selector encodings can denote overlapping or identical authority.
8.2 Conditional attenuation proof
`[INVARIANT PROOF]` Monotonic attenuation follows by induction down a spawn tree if all of the following hold:
Root capabilities are issued only by the kernel authority.
Child issuance is exclusively `child = attenuate(parent_effective, request)`.
`attenuate()` returns either a subset under one canonical selector algebra or denial; there is no permissive fallback.
Empty/absent child capability declarations mean no capability, not “unrestricted.”
All privileged effects pass through the same point-of-effect grant verification (S8 or equivalent).
Tool aliases are resolved to the canonical privileged verb before grant checking.
Plugins/toolkits cannot directly access privileged resources outside the kernel-mediated sandbox/effect path.
Revocation is checked at the point of effect, not only at proposal time.
Then no child can acquire a grant outside the transitive closure of its ancestors' effective grants.
8.3 Reported counterexamples in the current path
`[FACT]` The supplied Tech Lead and AI reviews report four fail-open steps in the `layer0` harness ceiling path: the compiler does not parse the declared capabilities, the computed intersection is discarded, an empty registry ceiling permits all capabilities, and `spi/ceiling.py` treats an empty capability set as allowed.
`[FACT]` Those reviews also report a second, weaker selector implementation based on lexical prefix rules, distinct from the mature selector algebra.
`[COUNTEREXAMPLE / HAZARD]` Under those facts, the implication:
[
DeclaredCeiling(H) \Rightarrow EffectiveCeiling(H)
]
is false. A manifest may declare a restricted authority while the compiled runtime behaves as if there were no restriction.
8.4 Selector canonicalization and filesystem alias hazards
File selectors are especially dangerous because path strings are not resource identities. A valid confinement design must account for:
`..` traversal and normalization;
Unicode normalization where relevant;
symlinks created or swapped after authorization;
hard links exposing the same inode under another path;
bind mounts / namespace remapping;
case sensitivity differences;
rename races;
current working directory as an implicit input;
shell glob expansion after authorization.
`[VERIFICATION RECOMMENDATION]` In the coding sandbox, make `/workspace` a namespace boundary and authorize paths relative to a trusted root. Do not claim that lexical prefix comparison alone proves filesystem confinement.
8.5 Tool aliasing and shell escalation
`[COUNTEREXAMPLE / HAZARD]` A narrow verb can become broad authority if it internally delegates to a general shell. Example:
```text
Capability: test.run(selector=/workspace/tests)
Implementation: /bin/sh -c <model-controlled string>
```
The declared verb looks narrow, but effective authority is `proc.exec` plus whatever filesystem/network authority the shell process has.
`[VERIFICATION RECOMMENDATION]` Capability review applies to transitive effect authority, not method names. If a toolkit invokes a general process executor, the outer capability and sandbox must conservatively reflect that authority.
8.6 `None` / unbounded semantics
Prior AI review evidence reports a hole where an unbounded child dimension may pass beneath a bounded parent because `None` is interpreted permissively.
`[VERIFICATION RECOMMENDATION]` The partial order must define top/bottom explicitly. Recommended rule:
`None` as “unbounded” is `TOP`, never covered by a finite parent bound;
absence of permission is `BOTTOM`, never `TOP`;
comparison must be total over every schema-valid selector/constraint pair and fail closed on unknown kinds.
---
9. Resource Accounting, Budget Conservation & Refund Lineage
9.1 The current six-dimensional vector is not one algebra
The proposed reservation is:
[
B = \langle usd_micros, millis, tokens, bytes, turns, depth \rangle
]
The architectural intention is good: every agent/subagent consumes bounded resources. The formalization needs correction.
`[COUNTEREXAMPLE / HAZARD]` `depth` is not a fungible resource. If a parent has `max_depth = 2`, it may validly spawn many siblings at depth 1 without the sum of sibling depths representing consumed root depth. Conversely, a child at the same maximum depth as the parent may be invalid even when a numeric sum appears within budget. Therefore:
[
\sum_i depth_i \le depth_{parent}
]
is not the right invariant.
`[COUNTEREXAMPLE / HAZARD]` `millis` is ambiguous under concurrency. If it means wall-clock elapsed time, two children running for 700 ms concurrently consume 700 ms of parent latency, not 1,400 ms. If it means charged compute milliseconds, additive summation may be valid. The unit must be defined before any conservation proof.
9.2 Split the resource algebra
`[VERIFICATION RECOMMENDATION]` Separate at least two classes:
A. Additive conserved resources
[
A = \langle usd_micros, tokens, bytes, turns, compute_millis \rangle
]
for which sibling reservations can satisfy:
[
Committed + OpenReserved \preceq Limit
]
component-wise.
B. Structural / monotone constraints
Examples:
```text
max_depth
deadline / expires_at
max_concurrency
scope/capability ceiling
```
These obey inheritance/ordering rules, not additive conservation:
[
child.depth = parent.depth + 1 \le root.max_depth
]
[
child.deadline \le parent.deadline
]
This distinction removes a false proof while preserving the intent of the six-dimensional governor.
9.3 Correct conservation state
For each additive dimension `d` of a parent lease `P`:
[
remaining_d(P) = limit_d(P) - committed_d(P) - \sum_{r \in OpenChildren(P)} reserved_d(r)
]
A child reservation is legal iff:
[
request_d \le remaining_d(P) \quad \forall d \in A
]
9.4 Atomic reserve proof
`[INVARIANT PROOF]` If parent state is read, the sufficiency check is performed, `BudgetReserved(child)` is appended, and the parent's outstanding reservation set is updated in one `BEGIN IMMEDIATE` transaction, then two concurrent spawns cannot both reserve the same remaining additive budget on a single SQLite database. SQLite's single writer serialization creates the reservation linearization point.
9.5 Refund/settlement state machine
A lease/reservation should have a monotonic lifecycle such as:
```text
OPEN
  ├─> COMMITTED/PARTIALLY_COMMITTED -> CLOSED
  ├─> RELEASED -> CLOSED
  └─> EXHAUSTED -> CLOSED
```
The exact schema may differ, but settlement must be idempotent and terminal.
`[COUNTEREXAMPLE / HAZARD]` Mutable “remaining budget” updated by `remaining += refund` is vulnerable to duplicate cleanup paths:
child returns and refunds unused budget;
cancellation handler runs concurrently and refunds again;
parent receives more remaining budget than its original limit.
`[VERIFICATION RECOMMENDATION]` Derive remaining budget from immutable reservation/settlement events, or enforce a unique terminal settlement per lease ID. Never make “credit back” a free-standing increment operation.
9.6 Refund lineage
Every settlement needs:
```text
lease_id
parent_lease_id
reservation_digest
settled_amount
consumed_amount
terminal_reason
idempotency_key
```
and the reducer must verify:
[
0 \preceq consumed \preceq reserved
]
unless a separately specified overrun rule permits debit beyond reservation. If overruns are permitted, they must reduce the ancestor's remaining budget and cannot silently create credit.
9.7 Spawn atomicity
`[VERIFICATION RECOMMENDATION]` A successful spawn should not durably create a child identity without its budget/authority lineage. The logical transaction should atomically establish:
child principal identity;
parent principal linkage;
child capability grant/attenuation record;
child resource reservation;
`ChildSpawned` causal event.
If these live in one SQLite authority store, they can share one transaction. If not, the system needs an explicit intermediate `SPAWN_PENDING` state and recovery rules.
---
10. Concurrency Isolation, Selector Algebra & Bernstein Conditions
10.1 Bernstein conditions are necessary, not sufficient by themselves
For actions `i` and `j`, the classic non-interference conditions are:
[
W_i \cap R_j = \varnothing
]
[
R_i \cap W_j = \varnothing
]
[
W_i \cap W_j = \varnothing
]
If these sets are complete and sound, the actions do not conflict through represented resources.
The missing premise is the difficult one:
> `R` and `W` must conservatively over-approximate every resource the effect can actually read or mutate.
10.2 Hidden resource examples
A command that appears to write only `/workspace/a.py` may also read or write:
current working directory;
environment variables;
`.git/index`, `.git/HEAD`, git locks;
compiler/test caches;
temp directories;
local ports;
shared package caches;
remote network APIs;
credentials or OS keyrings;
process-global state;
a model provider quota/account;
an evaluator request queue.
`[COUNTEREXAMPLE / HAZARD]` Two effects with disjoint filesystem selectors can still conflict on `.git/index`, a package cache, an external API record, or a shared process-global registry.
10.3 Selector soundness rule
`[VERIFICATION RECOMMENDATION]` Each resource kind needs its own overlap semantics. A generic lexical selector comparator is insufficient.
Examples:
filesystem selector → namespace/path/inode-oriented conservative overlap;
network selector → protocol/host/port/path/account scope;
process selector → executable + sandbox/workspace + inherited environment authority;
model selector → provider/model/account/quota identity where resource interference matters;
repository selector → workspace + git metadata scope;
database selector → DB/table/key/range semantics if introduced.
Unknown selector kind or dynamic target means conflict.
10.4 Planner declarations are hypotheses
`independence_groups` emitted by a planner are not proof. They are hints.
The scheduler/kernel must recompute or validate independence from trusted request selectors before parallel activation.
`[VERIFICATION RECOMMENDATION]` Treat a planner-provided group as:
```text
claim: "these effects are intended to be independent"
```
not:
```text
authority: "run these effects concurrently"
```
10.5 Future parallel execution fallback
For resources where static independence cannot be proven, use one of:
conservative sequential execution;
pessimistic all-or-none leases;
isolated overlay/MVCC execution with conflict detection before commit;
optimistic execution only for effects that can be deterministically rolled back or whose commit is gated on a conflict-free merge;
explicit commutative operation types with proven merge semantics.
For irreversible external effects, optimistic rollback is not a general solution.
10.6 v0.6 conclusion
`[INVARIANT PROOF]` With `MAX_CONCURRENCY = 1`, scheduler-level effect races are excluded by construction, assuming plugins do not create untracked parallel privileged work internally.
`[VERIFICATION RECOMMENDATION]` Keep parallel dispatch disabled until selector soundness, race injection, budget cancellation, and deterministic schedule replay gates all pass. The current Concept Lock's “semantics now, execution later” stance is correct.
---
11. Lease Allocation, Deadlock Prevention & Revocation Semantics
11.1 Lease acquisition
Future concurrency should avoid a blocking “hold one lock while waiting for another” design.
`[VERIFICATION RECOMMENDATION]` For a proposal needing multiple resource leases:
canonicalize all required selectors;
sort them by a deterministic total ordering;
attempt all-or-none acquisition in one scheduler/SQLite transaction where possible;
on conflict, acquire none and requeue/reject;
never retain a partial set while waiting.
`[INVARIANT PROOF]` All-or-none acquisition without wait-holding removes the circular-wait condition for those scheduler leases and therefore prevents deadlock in that mechanism.
11.2 Lease expiry
Lease expiry is a state transition influenced by time. To preserve replay:
wall-clock reads come from an injected clock;
the expiration decision is evented (`LeaseExpired` or equivalent) or represented by an authoritative terminal event;
cold state replay does not compare stored timestamps with the current wall clock and invent new historical expirations.
11.3 Revocation linearization point
The realistic safety property is:
[
Revoke(grant) \Rightarrow NoNewPrivilegedDispatch(grant)
]
after the revocation event commits and becomes effective in the kernel's authoritative grant state.
This is stronger and more implementable than “revocation instantly undoes every in-flight effect.”
11.4 Point-of-effect check
`[VERIFICATION RECOMMENDATION]` The grant must be checked immediately before crossing the external effect boundary, after policy and reservation decisions. A proposal authorized earlier is not sufficient if revocation can occur between proposal and dispatch.
A useful ordering is:
```text
policy/descriptor checks
→ point-of-effect grant status check
→ durable intent commit
→ external dispatch
```
If revocation and dispatch can race in future concurrency, their linearization order must be decided by the same authority transaction/lease protocol.
11.5 In-flight effects after revoke
After revocation commits:
new privileged dispatch using the grant → reject;
lease renewal → reject;
local subprocess already running → best-effort terminate according to policy, then record actual result;
remote request already sent → cannot be un-sent; reconcile/record completion or indeterminacy;
filesystem mutation already committed → cannot be erased by pretending it did not occur; compensate/rollback through explicit semantics if available.
`[COUNTEREXAMPLE / HAZARD]` Treating `CapabilityRevoked` as retroactively invalidating already-observed effects would corrupt history. Revocation changes future authority; it does not rewrite the past.
11.6 Cancellation versus revocation
Cancellation and authority revocation are separate:
cancellation: stop pursuing a run/episode/task;
revocation: remove a principal's permission to perform a class of privileged effects.
A cancelled agent may still need a narrow cleanup capability; a revoked capability may occur while the episode continues with other permissions. Do not collapse the two state machines.
---
12. Process Isolation Tiers (In-Process vs Subprocess vs Container)
12.1 `in_process`
`[INFERENCE]` Python in-process execution is not a security isolation boundary. Static import lint and audit hooks are useful controls/observability, not containment against malicious code.
An in-process plugin can potentially:
mutate globals;
monkeypatch imported modules;
inspect process memory/object graphs;
access inherited environment variables and file descriptors;
bypass a logical RPC façade if it has direct Python object references;
interfere with asyncio tasks;
alter registries or caches.
`[VERIFICATION RECOMMENDATION]` Classify `in_process` as TCB extension privilege: first-party, reviewed, signed/frozen build only. Do not describe it as sandboxed.
12.2 `subprocess`
Subprocess is a meaningful memory/process boundary but rlimits alone do not provide strong filesystem/network confinement.
Minimum hardening for normal untrusted-ish plugins should include, where available:
fresh process via exec-style launch;
explicit minimal environment, not inherited wholesale;
`close_fds` / no secret file descriptors;
UDS permissions and peer identity checks;
`no_new_privs`;
resource limits;
seccomp or equivalent policy on Linux;
filesystem allowlist / namespace when authority warrants it;
wall-clock deadline and kill/reap path;
structured protocol parser with maximum message sizes.
12.3 `container` / rootless workspace sandbox
For model/user-authored code or broad `proc.exec`/`patch.apply` effects, rootless container/bubblewrap-style isolation is the correct default boundary:
separate mount/user/PID/network namespaces;
read-only base;
workspace overlay;
network default deny;
explicit writable paths;
no evaluator key/socket visibility.
12.4 `wasm`
WASM may become useful for portable pure-compute plugins but is not required for the v0.6 invariant set. It should remain a measured/deferred isolation option.
12.5 Evaluator isolation is a different boundary
The exterior evaluator is not just another plugin tier. Its signing identity and oracle implementation are part of the evidence authority. Agent-side manifests must not be able to replace its signer, mount its key, or select an arbitrary executable as the authoritative judge.
---
13. External Evaluator Security Boundary & Oracle Non-Subvertibility
13.1 What Ed25519 proves
A valid Ed25519 signature can prove:
the signed bytes were produced by a holder of the private key;
the signed bytes were not modified after signing.
It does not prove:
the oracle is correct;
the oracle tests the intended property;
the task was not leaked;
the result is fresh;
the verdict applies to this run rather than another;
the evaluator host/OS/root administrator was uncompromised.
Therefore “tamper-proof” must be scoped to a threat model.
13.2 Required signed statement
`[VERIFICATION RECOMMENDATION]` A `SignedVerdict` should bind at least:
```text
schema/version
evaluation_request_id
subject_digest
project/run/episode identity as appropriate
harness/execution identity required by the protocol
oracle_digest + oracle_version
evaluator_key_id
verdict payload / score / metrics
evidence_bundle_digest (if any)
issued_at or evaluator sequence
protocol/preregistration id where applicable
signature
```
The verification path must prove:
signature valid under an approved evaluator key;
key not revoked/expired under policy;
`evaluation_request_id` exists and is outstanding;
subject digest exactly matches the request;
oracle identity matches the preregistered/authorized oracle;
request has not already consumed a verdict unless the protocol explicitly permits multiple verdicts;
verdict is then read and used by the scheduler/gate.
13.3 Replay attack
`[COUNTEREXAMPLE / HAZARD]` If the signature covers only `{oracle, pass=true}`, an attacker can replay a valid pass from task A onto task B.
Even if the signature covers a subject blob, reuse may remain possible across experiment cells if the request/protocol identity is not bound.
`[INVARIANT PROOF]` Binding a one-time `evaluation_request_id` and immutable `subject_digest` into the signed payload, then atomically marking that request resolved, prevents a previously consumed verdict from being accepted as a new resolution for a different request.
13.4 Exteriority threat model
The defensible v0.6 threat model is approximately:
untrusted: model outputs, agent policy, normal plugins, user/model-authored code;
constrained: toolkit processes and sandbox cells;
trusted/TCB-adjacent: kernel/ledger authority, evaluator daemon + signing key, host OS/admin boundary.
Do not claim protection against a fully compromised host root unless remote attestation/HSM-class mechanisms are later introduced.
13.5 Operational evaluator versus experimental judge
This review identifies a critical distinction.
If an `IEvaluationGate` verdict is fed back into the running agent to drive `RETRY`, `ESCALATE`, or repair, that oracle is part of the execution environment. The agent is effectively optimizing against its feedback.
For scientific claims, a final holdout evaluator should be conceptually separate:
```text
Operational verification oracle
    → may influence trajectory
    → identity belongs in execution identity D_R

Confirmatory / holdout experiment oracle
    → must not influence candidate behavior before terminal submission
    → identity belongs in experiment identity D_X
```
`[COUNTEREXAMPLE / HAZARD]` Using the same oracle both as iterative training/control feedback and as the sole final benchmark judge invites Goodhart/overfitting even if the oracle is cryptographically exterior.
---
14. Goodhart Vulnerability Audit in Test Gates & Mutation Scores
14.1 Reported current false-confidence patterns
The supplied Tech Lead/AI evidence identifies several cases where a gate validates structure rather than behavior:
hard-coded `verdict: "pass"` on the CI-gated path;
event coverage satisfied lexically;
replay parity folding one list twice;
capability/grant path not exercised because a test verb is advisory;
generated types stale while codegen `--check` is not in CI;
declared isolation tier not necessarily matching executed isolation;
only a small fraction of the mature behavioral suite used by living CI.
`[INFERENCE]` These are not unrelated bugs. They demonstrate the same systemic failure mode:
[
ProxyGreen \land PropertyFalse
]
14.2 Verification gate design rule
For each critical invariant, ask:
> What is the laziest incorrect implementation that could still pass this gate?
Then commit that implementation as a planted negative or mutation target and require the gate to fail.
Examples:
Property	Planted defect that must be detected
Exterior verdict	replace evaluator response with constant pass
Replay	drop `BudgetCommitted` reducer update
Attenuation	interpret empty ceiling as allow-all
Selector safety	replace canonical overlap with lexical prefix
Budget	settle same lease twice
Revocation	remove S8 revoked check
Writer authority	let scheduler append `CapabilityGranted` directly
CAS integrity	ledger-reference blob before durable rename/fsync
Codegen truth	hand-edit generated type to diverge from schema
14.3 Mutation score
A global mutation percentage is useful but can itself be Goodharted.
`[VERIFICATION RECOMMENDATION]` For the TCB:
every mutant that weakens an authority invariant must die or have a documented equivalent-mutant waiver;
overall mutation score can remain a secondary metric;
invariant-targeted mutant classes are the primary gate.
14.4 Oracle Goodhart
Cryptographic signing eliminates trivial label forgery. It does not eliminate weak tests, benchmark leakage, memorization, selection bias, or oracle incompleteness.
For promotion-grade claims, require:
preregistered confirmatory protocol;
sealed/holdout tasks where feasible;
oracle version/digest frozen in the experiment identity;
mutation/adversarial tests of the oracle itself;
contamination checks;
multiple evidence channels for high-value claims;
statistical power/MDE, not arbitrary task counts;
rollback exercise for any promotion mechanism.
---
15. Identity Triad Verification (Harness vs Execution vs Experiment Identity)
15.1 Harness identity `D_H`
`D_H` answers: What logical composition was built?
Recommended shape:
[
D_H = H(JCS(ResolvedManifest) \parallel Merkle(PluginArtifacts, Assets, Prompts, Policies))
]
It must change when any behavior-affecting composition input changes, including:
plugin bytes;
plugin configuration;
system prompt assets;
capability ceiling;
approval policy;
tool schemas;
context/planner configuration;
resolved model route configuration where it is part of the harness definition.
`[FACT]` Prior AI/Tech reviews report that the current `layer0` compiler drops capability/system-prompt/approval-policy data from the effective frozen harness path. If true, current `D_H` is not a complete experimental treatment identity.
15.2 Execution identity `D_R`
`D_R` answers: What runtime conditions actually executed the harness?
Recommended shape:
[
D_R = H(D_H \parallel substrate_build \parallel runtime_env \parallel model_identity \parallel sampling \parallel sandbox/tool_runtime)
]
Include as needed:
substrate/kernel revision digest;
Python/interpreter/dependency lock;
sandbox/container image digest;
model provider + immutable model ID where available;
sampling parameters/seed;
relevant environment/config flags;
operational evaluator/oracle identity if its feedback influences the trajectory;
adapter/plugin execution versions not already fully captured by `D_H`.
15.3 Experiment identity `D_X`
`D_X` answers: What confirmatory experimental cell produced the claim?
Recommended shape:
[
D_X = H(D_R \parallel task/dataset_digest \parallel protocol_digest \parallel holdout_oracle_digest \parallel preregistration_id)
]
This separation resolves a tension present in prior proposals about whether oracle identity belongs in execution or experiment identity:
an oracle used interactively during execution belongs in `D_R` because changing it can change behavior;
a terminal independent holdout judge belongs in `D_X` because it defines the measurement cell.
15.4 Identity invariants
`[VERIFICATION RECOMMENDATION]`
One-byte change in any included immutable artifact changes the relevant digest.
Mutable aliases (`latest`, provider model aliases, moving policy files) are resolved to an immutable recorded identity before execution where possible.
Every trajectory carries `D_H`, `D_R`, and the task/run identifiers needed to derive or reference `D_X`.
Signed verdicts bind to the subject and experiment protocol identity, not just a human-readable run name.
No A/B result is considered attributable if treatment-affecting fields are absent from identity.
---
16. Python-First Runtime Hazards & GIL/Asyncio State Leakages
Python-first is a reasonable v0.6 implementation choice. It does not weaken any invariant if the architecture refuses to treat Python runtime properties as synchronization/security guarantees.
16.1 The GIL is not an invariant mechanism
`[COUNTEREXAMPLE / HAZARD]` The GIL does not make compound authority operations atomic. Code can yield or release the GIL around I/O, SQLite calls, subprocess operations, cryptography, or C extensions. Multiple processes are unaffected by the GIL entirely.
Never rely on:
```text
"Python has a GIL, therefore this reservation/grant/sequence update cannot race."
```
Use SQLite transactions, explicit locks, or immutable event-derived state for authority transitions.
16.2 Asyncio cancellation windows
Important cancellation windows include:
```text
reserve budget
await ...
append intent
await ...
dispatch subprocess
await receipt
settle reservation
```
`[COUNTEREXAMPLE / HAZARD]` If cancellation occurs after reservation but before a `finally`/terminal settlement path, a lease can remain open forever. If cancellation occurs after external dispatch but before the receipt is persisted, the effect becomes undeterminable.
`[VERIFICATION RECOMMENDATION]`
minimize `await` points inside authority-critical sections;
shield the SQLite commit that establishes an intent/settlement from task cancellation once begun;
use `try/finally` only as liveness hygiene, not as the sole accounting guarantee;
on restart, detect open reservations/intents from durable state;
cancellation itself becomes a typed/evented terminal reason.
16.3 Hidden mutable globals
Registry state, current principal, current run, current grant, active harness, or budget must not exist only as process-global mutable variables.
Prefer:
immutable/frozen request context passed explicitly;
frozen registries after composition;
explicit IDs instead of ambient “current” objects;
no security decision based solely on `contextvars` or thread-local state;
projections reconstructible from the ledger.
`[COUNTEREXAMPLE / HAZARD]` An in-process plugin that can mutate a global registry or monkeypatch the selector/grant function can bypass logical RPC boundaries while every ledger event remains syntactically valid.
16.4 Fork and SQLite
`[VERIFICATION RECOMMENDATION]` Do not inherit active SQLite connections across forked plugin/sandbox workers. Spawn/exec child processes with their own explicit resources; keep the authority database connection in the owning runtime process.
16.5 File descriptors and environment inheritance
Subprocess plugins should not inherit evaluator sockets, signing-key handles, database connections, secret-bearing file descriptors, or the complete parent environment by default.
`[VERIFICATION RECOMMENDATION]` Explicit allowlists for environment and FDs are part of capability confinement even when the capability algebra itself is correct.
16.6 Async concurrency and event order
If multiple asyncio tasks may propose concurrently in a future version, the durable ledger transaction, not task scheduling order, determines authoritative event order. Do not let an in-memory `seq += 1` create event identity before the SQLite transaction establishes the actual predecessor.
16.7 Python object aliasing
Frozen dataclasses prevent direct field assignment but do not automatically make nested mutable objects immutable. `dict`/`list` values inside “frozen” containers can still mutate unless canonical immutable types/copies are enforced.
`[VERIFICATION RECOMMENDATION]` Identity-bearing payloads should be canonicalized from immutable JSON-compatible structures before hashing/signing; mutable aliases must not remain reachable after digest computation.
---
17. Five-Way Review Comparison Matrix (PSE vs TL vs Arch vs AI vs Systems)
The Principal Staff Engineer lane is represented here through the supplied Concept Lock BETA and the other reviews' explicit summaries of `principal_engineer_proposal.md`, because that source was not independently re-executed in this fifth lane.
Topic	Principal Staff Engineer	Independent Tech Lead	Principal Architect	AI Specialist	Systems Verification — this report
Runtime direction	One recursive Python substrate; Concept Lock BETA makes `vanguard/packages/` canonical until convergence	Strongly favors packages as production truth; layer0 absorb/delete, no third runtime	Python selective convergence/strangler, preserve mature packages mechanisms	Agrees: packages has real agentic mechanisms; layer0 is interface/walking skeleton	Concur. Runtime language is not the safety issue; single canonical authority implementation is.
State authority	Decision plane vs ledger state plane; `State=fold(Events)`	Concur, but shows replay gates and layer0 fold are false confidence	Ledger + pure reducers authoritative	Concur; state lineage/trajectory missing	Strengthen: ledger truth requires writer-kind authority and semantic construction rules. Replay of forged events is still false.
WAL / durability	SQLite WAL retained	Shows packages has real WAL; layer0 memory sink is regression	Preserve SQLite WAL store	Concur	Concur + formalize crash matrix/outbox. No exactly-once claim for arbitrary external effects.
Recursive agency	`Agent = Principal + HarnessInstance`, spawn attenuation	Real spawn exists in packages; mock in layer0	Locks recursive primitive	Strongly endorses, asks heterogeneous harness parameter and typed denial	Concur + require atomic spawn authority/budget/identity transaction.
Capability attenuation	Child subset of parent	Finds dropped/fail-open ceiling and duplicate selector algebra	Locks attenuation lattice	Same, plus model/tool composition implications	Strengthen: one canonical partial order, fail-closed unknowns, transitive effect authority, alias/symlink/shell hazards, evented writer owner.
Budget model	Six-dimensional reservation, child ≤ parent	Notes parent lease lineage; does not fully formalize dimensional algebra	Locks 6-D governor	Treats budget conservation as recursion governor	Modify materially: split additive conserved resources from structural constraints. `depth` is not additive; wall-time semantics must be defined.
Concurrency	Semantics now, sequential v0.6	Sequential until real behavioral gates; criticizes false confidence	Two-phase concurrency; later selector proofs	Concur; selectors already provide intended predicate	Concur + strengthen: Bernstein only if selector footprint is conservative and complete. Unknown/dynamic = conflict.
Revocation	Lock semantics; no new dispatch after revoke	Prior synthesis explicitly recommends realistic `NoNewPrivilegedDispatch`	Mentions ephemeral leases/revocation hooks	Explicitly recommends point-of-effect semantics	Concur + formal linearization: revoke committed before point-of-effect prevents new dispatch; in-flight effects are best-effort terminate/reconcile, never retroactively erased.
Evaluator	Exterior signed judge, scheduler must use real verdict	Exposes hard-coded pass and gate weakness	Exterior UID-separated Ed25519 daemon	Treats exteriority as anti-reward-hacking moat	Strengthen: signed verdict must bind request+subject+oracle+protocol and be anti-replay. Authenticity ≠ oracle validity. Separate operational oracle from holdout judge.
Plugin boundary	Wire-first JSON-RPC/UDS, five SPIs	Accepts genuine broker value but demands behavioral coverage	Strongly wire-first	Strongly plugin-first, mechanism below line	Concur: `in_process` is TCB extension, not sandbox; subprocess/container boundaries need explicit FD/env/secret confinement.
Identity	`D_H/D_R/D_X` trinity	Calls envelope identity an irreversible lock decision	Locks triple digest	Makes identity/trajectory one of four AI-load-bearing obligations	Refine: operational oracle influencing behavior belongs in `D_R`; independent holdout oracle belongs in `D_X`.
Goodhart / gates	CI subject of record must become production lattice	Strongest adversarial gate audit; proves lexical/tautological gates	Calls for behavioral matrix	Adds trajectory/scientific attribution angle	Concur + require invariant mutants/planted negatives and writer-forgery tests.
Rust/distribution	Deferred behind evidence	Reject now	Reject third runtime, defer Rust	Defer; not AI-load-bearing	Concur. Neither Rust nor consensus fixes semantic falsehood, budget algebra, or writer authority.
17.1 Main points of new disagreement/correction
This systems lane introduces four material refinements beyond the apparent four-way consensus:
The budget vector requires two algebras, not one. Additive conservation cannot be applied literally to `depth`, and `millis` must be semantically classified.
Ledger authority requires writer scoping. “Orchestrator decides, ledger proves” is insufficient if the orchestrator can append proof events directly.
Evaluator integrity requires anti-replay request binding and oracle-role separation. A signed exterior evaluator can still be Goodharted if it is both the iterative feedback source and the final experimental judge.
Selector independence requires footprint completeness. Bernstein equations over incomplete selector sets are a false proof.
These are Concept Lock concerns because they define what future code is allowed to claim.
---
18. Counterexamples & Failure Mode Scenarios
FM-1 — Self-consistent forged verdict
Sequence
scheduler requests evaluation;
ignores response;
appends `VerdictRecorded(pass=true)` itself;
reducer folds it;
replay parity passes.
Violation: evaluator exteriority and semantic truth.  
Reported analogue: hard-coded `pass` in layer0.  
Required defense: event-kind writer authority + signed request-bound verdict verification + test that injected `fail` changes run outcome.
FM-2 — Hash-chain fork from process-local head
Sequence
two writer objects read `_prev = H42` from local memory;
each creates event seq 43 with `prev_digest=H42`;
both attempt persistence without one transactional DB-owned head check;
two branches exist or one is silently lost.
Violation: unique causal order.  
Defense: DB transaction owns chain head; unique `(project_id, seq)` + expected predecessor check.
FM-3 — Invisible effect after pre-commit dispatch
Sequence
process launches external tool;
tool mutates filesystem;
process SIGKILLs before intent event commits.
Violation: “everything that changes authoritative/external state is observable.”  
Defense: durable intent commit before dispatch.
FM-4 — Blind retry of undeterminable effect
Sequence
intent commits;
remote API performs non-idempotent action;
client dies before receipt;
reboot sees open intent;
runtime retries automatically.
Violation: duplicate external side effect.  
Defense: `undeterminable` state + probe/idempotency/reconciliation before retry.
FM-5 — CAS reference to non-durable bytes
Sequence
ledger event referencing digest D commits;
blob write/rename was not durable;
power loss;
replay finds event but CAS object D is missing.
Violation: evidence referential integrity.  
Defense: durable blob first, event reference second; orphan blobs are acceptable.
FM-6 — Child privilege escalation through empty ceiling
Sequence
parent/harness declares limited or empty capability ceiling;
compiler drops ceiling;
registry interprets empty set as unrestricted;
plugin requests `proc.exec`;
downstream check permits because “allowed is empty.”
Violation: monotonic attenuation.  
Defense: absence = no authority; compiled ceiling included in `D_H`; one canonical comparator.
FM-7 — Selector escape via transitive shell
Sequence
capability authorizes narrow verb `test.run`;
toolkit calls `/bin/sh -c` with model-controlled command;
shell writes outside intended test resource within its sandbox-visible namespace.
Violation: effective authority exceeds syntactic verb/selector.  
Defense: transitive effect classification + sandbox boundary + no broad shell behind narrow capability without corresponding authority.
FM-8 — Symlink race after authorization
Sequence
selector authorizes `/workspace/out/report.txt`;
attacker replaces `out` with symlink to another writable mount after check;
tool opens path after substitution.
Violation: filesystem selector confinement.  
Defense: namespace isolation plus race-resistant root-relative open/validation semantics; do not rely on lexical prefix.
FM-9 — Double refund
Sequence
child lease R reserves 100 tokens;
normal return path releases 40 unused;
concurrent cancellation/recovery handler also releases 40;
parent mutable `remaining += 40` runs twice.
Violation: budget conservation.  
Defense: one terminal settlement per lease ID; derive balance from events.
FM-10 — False six-dimensional conservation proof
Sequence
root has `max_depth=2`;
it spawns ten independent children at depth 1;
a proof sums sibling `depth=1` values and rejects after two children, even though the path-depth constraint is still satisfied.
Violation: model correctness — false denial from wrong algebra.  
Inverse hazard: treating `depth=None`/unbounded as covered by a finite parent can permit true escalation.  
Defense: depth is a structural path constraint, not additive budget.
FM-11 — Revocation race at effect boundary
Sequence
request passes grant check;
another task commits `CapabilityRevoked`;
first task dispatches external process without re-check/serialization.
Violation: `Revoke ⇒ NoNewPrivilegedDispatch`.  
Defense: define point-of-effect linearization with grant status and dispatch intent in one serialized authority transition.
FM-12 — Signed verdict replay
Sequence
evaluator signs `pass` for subject A;
attacker reuses signed bytes to resolve request B because verifier checks key/signature but not request/subject binding;
B passes.
Violation: evidence integrity.  
Defense: sign `evaluation_request_id + subject_digest + oracle_digest + protocol`; one-time resolution.
FM-13 — Orchestrator forges state while preserving replay
Sequence
orchestrator cannot obtain a capability through kernel policy;
orchestrator directly appends `CapabilityGranted` to generic event store;
reducers fold it;
later dispatch sees the grant as authoritative;
replay reconstructs the forged grant exactly.
Violation: separation of control policy and authority.  
Defense: kind-scoped append authority; orchestrator requests, kernel emits.
FM-14 — Async cancellation leaks reservation
Sequence
budget is reserved;
coroutine awaits RPC;
cancellation raises before settlement event;
process continues but lease remains open; parent starves indefinitely.
Violation: liveness/accounting closure.  
Defense: durable open-lease recovery + cancellation terminal semantics + idempotent release/reconcile.
FM-15 — In-process plugin mutates authority implementation
Sequence
in-process plugin imports selector/grant module;
monkeypatches comparator or registry mapping;
privileged request is now approved;
event stream shows apparently valid authorization.
Violation: isolation/authority independence.  
Defense: in-process is TCB-only; untrusted plugins run out of process; authority objects never passed by reference.
FM-16 — Operational oracle becomes the benchmark target
Sequence
same oracle gives repair feedback every turn;
planner learns/optimizes behavior specifically to that oracle;
final “independent” score uses the same oracle/version;
benchmark improves while general behavior may not.
Violation: experimental validity, not cryptographic integrity.  
Defense: holdout/confirmatory oracle separated from operational feedback and frozen into `D_X`.
---
19. P0 Invariants to Lock Immediately (Zero-Tolerance)
The items below are semantics/proof obligations, not a roadmap and not permission to implement concurrency or new infrastructure.
P0-SV-1 — Authoritative event writer matrix
LOCK: Every authority-bearing event kind has exactly one authorized emitter class; the append boundary enforces it. Generic coordination policy cannot append grant/budget/verdict/effect-settlement events directly.
Falsifier: a test obtains the orchestrator writer interface and successfully appends `CapabilityGranted` or `VerdictRecorded` without the owning authority.
P0-SV-2 — State replay contract
LOCK: Authoritative state is a pure, total deterministic fold of durable events; cold replay from disk structurally equals live authoritative projections for the defined state set.
Falsifier: delete/alter a budget/grant reducer and replay parity stays green.
P0-SV-3 — Durable intent before external effect
LOCK: No privileged external effect dispatch occurs until its authority/reservation/intent transaction is durably committed.
Falsifier: kill injection observes an external mutation with no durable intent.
P0-SV-4 — Undeterminable/reconciliation semantics
LOCK: Open durable effect intents after crash become explicit `undeterminable`/reconciliation work; they are never blindly retried.
Falsifier: a crash after remote execution but before local receipt causes automatic duplicate execution without probe/idempotency.
P0-SV-5 — One canonical capability/selector algebra
LOCK: Exactly one canonical `covers/overlap` semantics governs both harness/plugin ceilings and kernel grants. Unknown/unparseable selectors fail closed. Empty capability set means no authority.
Falsifier: `ceiling.py`-style lexical comparison or empty-allow behavior can authorize a request the canonical kernel selector rejects.
P0-SV-6 — Monotonic spawn authority
LOCK: Successful spawn atomically establishes child identity, parent linkage, attenuated capabilities, and resource lineage. Child authority can only be derived from parent effective authority.
Falsifier: property/fuzz test produces a child whose effective privileged effect set is wider than its parent.
P0-SV-7 — Split resource algebra
LOCK: Additive conserved quantities are separated from structural limits. `depth` is a monotone path constraint, not an additive budget component. Time semantics distinguish charged compute from deadline/wall time.
Falsifier: the specification still asserts `Σ depth_child ≤ depth_parent` as the meaning of recursion safety, or permits unbounded child depth under bounded parent.
P0-SV-8 — Idempotent reservation settlement
LOCK: Every reservation/lease has one monotonic terminal settlement; parent remaining balance is derived from immutable reservation/settlement facts or protected by equivalent uniqueness constraints.
Falsifier: concurrent return/cancel/recovery can credit the same unused reservation twice.
P0-SV-9 — Revocation point-of-effect semantics
LOCK: Once revocation commits before an effect's point-of-effect linearization, no new privileged dispatch under that grant may start. Already in-flight external effects are terminated best-effort or reconciled; history is not rewritten.
Falsifier: a committed revoke can be followed by a newly started privileged process using the revoked grant without an earlier linearization record.
P0-SV-10 — Sequential execution until independence is proven
LOCK: v0.6 executes privileged effects sequentially (`MAX_CONCURRENCY=1`) even if read/write/independence semantics are recorded.
Falsifier: two privileged effects can be live concurrently before the future concurrency gate is explicitly passed.
P0-SV-11 — Selector completeness rule
LOCK: Planner-declared independence is non-authoritative. Unknown/dynamic resource footprint means conflict. Each selector kind has trusted overlap semantics.
Falsifier: an “unknown” selector pair is treated as independent by default.
P0-SV-12 — Signed verdict request binding and anti-replay
LOCK: `SignedVerdict` binds immutable evaluation request ID, subject digest, oracle identity/version, and protocol/experiment identity as applicable; verifier rejects reused/mismatched verdicts.
Falsifier: a valid verdict from run A is accepted to resolve run B.
P0-SV-13 — Evaluator role separation for science
LOCK: If an oracle's feedback can influence the running agent, that oracle is part of execution identity. Confirmatory claims require an independent/frozen terminal evaluation protocol that did not feed the candidate during the measured trajectory.
Falsifier: a promotion claim is based solely on the same oracle that guided every repair decision, with no independent holdout/protocol.
P0-SV-14 — CAS durable-reference ordering
LOCK: Ledger events cannot reference a blob until the blob is content-addressed and durable under the defined local CAS protocol.
Falsifier: power-loss injection produces a committed event whose required blob digest cannot be read.
P0-SV-15 — Identity completeness
LOCK: `D_H`, `D_R`, and `D_X` have non-overlapping normative meanings; every treatment-affecting immutable input belongs to one of them and is captured before the result is used scientifically.
Falsifier: changing prompt/capability/policy/model/runtime/oracle in a way that changes behavior can leave all relevant identity digests unchanged.
P0-SV-16 — In-process classification
LOCK: `in_process` is a trusted TCB-extension mode, not a sandbox. Untrusted/model-authored code never relies on Python audit hooks as the sole containment boundary.
Falsifier: an untrusted plugin is classified isolated while sharing Python memory/object authority with the kernel.
---
20. P1 Structural Enforcements (Lock or Defer)
These are important but need not expand the v0.6 critical path beyond the P0 semantics.
Item	Decision	Systems rationale
P1-1 Canonical all-or-none lease acquisition	LOCK SEMANTICS NOW; implement with concurrency	Prevents future scheduler deadlock and partial-resource hold.
P1-2 Resource-kind selector registry	LOCK interface now; expand kinds as domains require	Each resource type needs sound overlap logic. Avoid a universal lexical comparator.
P1-3 Event schema version/upgrade policy	LOCK NOW	Reducer determinism across historical ledgers requires explicit version semantics.
P1-4 Directory fsync + CAS read verification	LOCK durability model now	Avoid claiming stronger blob durability than implemented.
P1-5 Cross-process emitter authentication	LOCK owner semantics; mechanism may be local capability handles initially	Full per-event signatures inside one trusted process are unnecessary, but writer identities must not be forgeable by policy plugins.
P1-6 Separate holdout evaluator process/key	LOCK scientific role now; implementation can be lab-side	Product evaluator and confirmatory judge have different epistemic roles.
P1-7 Invariant mutation suite	LOCK gate requirement now	Critical controls need targeted mutants, not just aggregate score.
P1-8 Full process sandbox hardening (advanced seccomp, attestation)	DEFER DELIBERATELY	Stronger hardening can evolve after basic subprocess/container boundaries are real.
P1-9 WASM isolation	DEFER DELIBERATELY	No effect on core formal invariants if current trust tiers are correctly enforced.
P1-10 Distributed consensus / Raft / global ordering	DEFER / REJECT for v0.6	SQLite single-node consistency is sufficient. Distribution would add failure modes without closing current semantic holes.
P1-11 Vector clocks / CRDTs / Merkle DAG state	DEFER	Not needed while project-local ledger commits are serialized and execution is single-node.
P1-12 Rust rewrite	DEFER behind measured gate	Language migration does not solve false event semantics or authority algebra.
P1-13 Remote attestation/HSM	DEFER	Needed only if threat model expands to hostile host/operator.
P1-14 Optimistic concurrency + rollback	DEFER	Only after selectors, isolation, deterministic merge, and irreversible-effect rules are proven.
P1-15 Hot-swap mid-episode	DEFER / forbid for v0.6 experiments	Mid-run treatment changes complicate identity and causal attribution; freeze composition per episode.
P1 conclusion
The architecture should remain intentionally boring at the infrastructure layer: one process for the trusted scheduler/kernel/ledger if desired, one SQLite DB, local CAS, subprocess/container cells, and exterior evaluator. Formal separation does not require premature physical distribution.
---
21. Falsification Criteria for Systems Invariants
A systems invariant is not locked until there is a test that would fail if the invariant were false. The following suite is the minimum falsification portfolio.
F-STATE-1 — Cold replay parity
Experiment: Run a production-path fixture, persist to SQLite, destroy process memory, cold-open DB, fold from zero, diff full authoritative state.  
Must fail if: any authority-bearing reducer update is removed or made order-dependent.
F-STATE-2 — Reducer purity/property test
Experiment: For canonical event sequence `L`, run fold repeatedly under randomized process state/environment and verify identical canonical state digest.  
Must fail if: reducer reads clock/RNG/environment/global mutable state.
F-CRASH-1 — Killpoint matrix
Inject SIGKILL/power-loss-equivalent boundaries:
```text
before intent tx
inside tx
after intent commit
before dispatch
after dispatch before receipt
after receipt before terminal commit
after terminal commit before caller response
```
Pass condition: no invisible effect; every ambiguous effect is reconcilable/undeterminable; no duplicate settlement.
F-CAS-1 — Blob durability fault injection
Kill between temp write, fsync, rename, directory fsync, and ledger commit.  
Pass condition: no committed required reference points to missing bytes.
F-CAP-1 — Attenuation property fuzzing
Generate parent grants and child requests across every selector kind, including malformed/unknown cases.  
Pass condition: every successful child effect is covered by some parent grant; unknowns deny.
F-CAP-2 — Alias/symlink adversarial suite
Include traversal, symlink swap, hardlink, bind-mount-visible aliases, case/unicode variants, and shell indirection.  
Pass condition: no effective resource access outside parent scope.
F-CAP-3 — Empty/unbounded boundary suite
Pass condition: empty means no permission; unbounded child cannot fit under finite parent; finite child may fit under unbounded parent if that state is allowed by policy.
F-BUDGET-1 — Concurrent reserve race
Start many child reservation attempts against the same small parent budget.  
Pass condition: committed + open reserved never exceeds root additive limit at any prefix of the ledger.
F-BUDGET-2 — Double-settlement race
Race normal return, cancellation, timeout, crash recovery, and explicit release for one lease.  
Pass condition: exactly one terminal settlement semantics; no double credit.
F-BUDGET-3 — Structural limit tests
Test depth and deadline separately from additive budgets.  
Pass condition: many siblings do not “consume” depth; no child path exceeds max depth; child deadline cannot outlive parent deadline.
F-REVOKE-1 — Linearization race
Race revoke commit against dispatch start over thousands of schedules.  
Pass condition: every dispatch can be classified as linearized-before-revoke or rejected-after-revoke; no unclassifiable newly started privileged effect.
F-CONC-1 — Sequentiality assertion (v0.6)
Instrument active privileged effect count.  
Pass condition: maximum active count is 1 in v0.6.
F-CONC-2 — Future selector race oracle
When concurrency is eventually enabled, randomize interleavings for supposedly independent pairs. Compare against both serial orders and actual resource diffs.  
Pass condition: result is observationally equivalent where independence was asserted, or the pair is rejected as conflicting.
F-EVAL-1 — Verdict truth propagation
Inject evaluator `FAIL`.  
Pass condition: scheduler cannot record/pass the run as if verdict were `PASS`.
F-EVAL-2 — Signature tamper
Flip one byte in signed subject/verdict/oracle identity.  
Pass condition: reject.
F-EVAL-3 — Replay/misbinding
Reuse valid verdict from request A against request B or same subject under different oracle/protocol.  
Pass condition: reject.
F-AUTH-1 — Unauthorized event append
Give orchestrator/policy code only its intended writer interface. Attempt to append kernel/evaluator event kinds.  
Pass condition: impossible by type/capability/runtime enforcement.
F-AUTH-2 — Forged sequence precondition
Attempt invalid transitions such as `BudgetReleased` for nonexistent reservation, `EffectCompleted` without intent, `CapabilityRevoked` for unknown grant, duplicate terminal verdict resolution.  
Pass condition: reject or quarantine as corrupt input; never silently fold as valid authority state.
F-ISOLATION-1 — In-process trust classification
Attempt monkeypatch/global mutation from a normal plugin.  
Pass condition: normal plugin is not in-process; trusted in-process extension is explicitly part of TCB and tested as such.
F-ISOLATION-2 — Secret/socket reachability
From plugin and workspace cells, attempt to open evaluator signing key path/FD/socket and authority DB handles.  
Pass condition: unavailable except through the allowed evaluation request protocol.
F-ID-1 — Digest sensitivity
Mutate one behavior-affecting input at a time: prompt, plugin byte, capability ceiling, policy, tool schema, model ID, sampling, runtime build, oracle protocol.  
Pass condition: exactly the appropriate identity layer (`D_H`, `D_R`, or `D_X`) changes.
F-GOODHART-1 — Planted lazy implementation portfolio
For every P0 gate, maintain a minimal incorrect implementation known to satisfy the old proxy.  
Pass condition: current gate suite rejects every planted defect.
F-RECOVERY-1 — Reboot reconstruction only from durable facts
Delete all caches, projections, in-memory orchestrator state, and temporary scheduling indexes.  
Pass condition: system reconstructs the same authoritative state and identifies outstanding reconciliation work from ledger/CAS alone.
---
22. Final Systems Verification Verdict & Signing Statement
22.1 Final verdict
CONDITIONAL CONCEPT-LOCK ACCEPTANCE.
The Vanguard / AETHER v0.6 architectural direction is viable for a Python-first, single-node, SQLite-WAL substrate. No distributed consensus system is required to make the core invariants rigorous. The core problems are local and tractable: transaction boundaries, authority ownership, event truthfulness, canonical attenuation, resource accounting, anti-replay evidence binding, and conservative concurrency semantics.
The current evidence does not support the stronger statement that the seven foundational claims are already mathematically guaranteed in the implementation. In particular:
deterministic fold is undercut by reported non-durable/partial `layer0` semantics and a weak parity gate;
capability monotonicity is contradicted by the reported fail-open ceiling path;
budget conservation is not formally correct until additive resources are separated from depth/deadline constraints;
selector independence remains a future proof obligation, not a present guarantee;
exterior signed evaluation is real in the mature packages path but reportedly fabricated in the CI-gated layer0 path, and signatures alone do not protect oracle validity;
revocation must be defined as prevention of new dispatch plus explicit handling of in-flight effects;
ledger authority does not prevent orchestrator forgery unless privileged event writers are scoped and enforced.
22.2 System-level lock recommendation
The Concept Lock should be approved only if it records P0-SV-1 through P0-SV-16 as zero-tolerance invariants or equivalent normative rules, with particular emphasis on these four corrections:
Event truth requires an enforced writer authority matrix.
Resource conservation requires separate additive and structural algebras.
Signed verdicts require request/subject/protocol binding and independent confirmatory evaluation semantics.
Bernstein independence is valid only over trusted, conservative resource footprints; unknown means conflict.
If these are locked, the single-node architecture has a credible path to proof without Rust, Raft, gRPC, a distributed database, or a larger kernel.
If they are not locked, the substrate remains vulnerable to the project's demonstrated worst failure mode: a system that records and replays a clean, cryptographically consistent history of something that did not actually happen or was not actually authorized.
22.3 Signing statement
Reviewer: Principal Systems Verification & Invariants Engineer  
Review class: Independent fifth-lane adversarial systems assessment  
Scope: state machines, WAL/crash semantics, capability attenuation, resource conservation, selector/concurrency safety, revocation, evaluator integrity, authority separation, and falsification criteria  
Evidence basis: supplied project corpus and prior live-tree evidence reports; no live repository commands were re-executed in this lane  
Code changes: none  
Normative document changes: none  
Final status: CONDITIONAL ACCEPT — CONCEPT DIRECTION SOUND; FORMAL GUARANTEES NOT YET PROVEN; P0 CORRECTIONS REQUIRED BEFORE CLAIMING INVARIANT CLOSURE.