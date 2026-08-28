# M-6 — Mediated Delegation (`agent.spawn` as an ordinary effect)

**Class:** engineering report (non-normative)
**Governing sources:** `001_alfa` §4/§5, `Higgs_update_concepts.md` L909–913, `milestones.md` M-6
**Falsifiers:** RF-55–RF-59 (attenuation), RF-26 (recovery)

---

## 1. The architectural decision

There are two ways to build delegation. Only one survives the project's laws.

**Rejected — spawn as a kernel primitive.** Add `EpisodeEngine.spawn()` as a
privileged internal call. Simple, fast, and fatal: the kernel would need to know
what an agent *is*, authority attenuation would live inside the TCB, and the
kernel budget (≤1438 LOC, currently 1737 measured across the package) would
absorb parent/child lifecycle logic. `Higgs_update_concepts.md` L155 names this
directly — new kernel code is justified only for **new authority semantics**, and
delegation introduces none.

**Adopted — spawn as a generic descriptor.** `agent.spawn` is an ordinary
requested effect. The kernel authorises it exactly as it authorises
`patch.apply`: descriptor, grant, reservation, S8a durable intent, settlement.
Only a **runtime adapter** interprets the authorised intent as child creation.

```
parent proposes agent.spawn
  → S0..S7  normal authorisation (grant, budget reservation, approval)
  → S8a     EffectStarted  ← DURABLE INTENT written BEFORE any child exists
  → runtime SpawnAdapter reads authorised intent → creates child
  → ChildSpawned / ChildReturned
  → S9..S12 settlement, cost folded into parent
```

**The kernel never learns what spawning is.** That is the whole design.

---

## 2. The attenuation algebra

This function is the entire security story of M-6. It is pure, has no I/O, and
no kernel dependency — which is what makes it exhaustively testable.

```python
def attenuate(parent, req_authority, share, child_id) -> AgentContext:
    # 1. request must ALREADY be within the parent hull.
    req = frozenset(req_authority)
    if escaped := req - parent.authority:
        raise AttenuationError(f"requested authority outside parent hull: {sorted(escaped)}")
    authority = req & parent.authority

    # 2. budget: subtract from parent. Never mint.
    for k in share:
        if k not in BUDGET_KEYS:              raise AttenuationError(f"unknown dimension {k!r}")
        if share[k] > parent.budget.get(k,0): raise AttenuationError(f"child {k} exceeds parent")

    # 3. depth / cycles / storms
    if parent.depth + 1 > MAX_DEPTH:          raise AttenuationError("max depth exceeded")
    if child_id in parent.lineage:            raise AttenuationError("delegation cycle")
    if parent.budget.get("spawns",0) <= 0:    raise AttenuationError("spawn quota exhausted")

    return AgentContext(child_id, authority, dict(share),
                        parent.depth+1, parent.lineage + (parent.episode_id,))
```

### 2.1 A real defect found during implementation — worth recording

The first version read:

```python
authority = frozenset(req_authority) & parent.authority
if authority - parent.authority:                     # DEAD CODE
    raise AttenuationError("child authority escaped parent hull")
```

**After intersecting, `authority - parent.authority` is always empty.** The guard
could never fire. The code was not *unsafe* — the intersection did bound the
child correctly — but it silently narrowed a request instead of rejecting it. A
caller asking for `proc.exec` would receive a child without it and never learn.

The fix inverts the order: check membership **before** intersecting, and deny.

**Design principle extracted:** *silent narrowing is a failure mode, not a safety
feature.* It satisfies the letter of monotonic attenuation while hiding caller
bugs. In an authority system, "you asked for something you cannot have" must be
an error, not a shrug. This class of bug — a guard that cannot fire because an
earlier operation already established its invariant — is easy to review past and
is why each denial has its own test rather than one aggregate assertion.

### 2.2 Denial matrix (all verified)

```
happy path       -> ['fs.read']
widen authority  -> DENIED (requested authority outside parent hull: ['proc.exec'])
mint budget      -> DENIED (child usd_micros exceeds parent remaining)
cycle            -> DENIED (delegation cycle)
depth            -> DENIED (max delegation depth exceeded)
spawn storm      -> DENIED (spawn quota exhausted)
bad dimension    -> DENIED (unknown budget dimension 'gpu_hours')
```

`spawns` is a **budget dimension**, not a separate counter. It attenuates and
settles through the same typed machinery as tokens and micros, so spawn-storm
protection is not a bolted-on rate limiter — it is budget exhaustion, and it
recovers correctly across restarts for free.

---

## 3. Recovery: the case that corrupts naive implementations

The dangerous window is between the S8a durable intent and the child's actual
existence. A crash there leaves an intent whose outcome is genuinely unknown.

```python
def reconcile_cold(self, intent) -> str:
    match self._probe(intent.child_id):
        case "FOUND":  return OCCURRED         # adopt existing child
        case "ABSENT": return DID_NOT_OCCUR    # safe to retry
        case _:        return UNDETERMINABLE   # F-22 -- never guess, never retry
```

The third branch is where most delegation systems quietly corrupt themselves.
The tempting behaviours — assume failure and retry (duplicate child, duplicated
spend), or assume success and continue (phantom lineage) — are both wrong.
`sprint_active.md` §9 already fixes the rule: an unreconciled cold intent
returns F-22 and **cannot execute or claim occurrence** until exterior
reconciliation. The implementation returns `UNDETERMINABLE` and blocks that
effect only, rather than failing the whole run.

### 3.1 Idempotency guard

```python
if prior := self._ledger.settled(intent.idempotency_key):
    return prior                      # a settled physical effect is never repeated
```

Verified: replaying the same intent leaves `engine.runs == 1`. This is the M-4
row-7 property (`no settled effect repeated`) holding for delegation
specifically, which is why M-6 sits behind M-4 in the ladder — the recovery
semantics must be proven for simple effects before they are trusted for
recursive ones.

---

## 4. Sequential execution (I-11) is preserved

`SpawnAdapter` calls the **same** `EpisodeEngine`, synchronously:

```python
result = self._engine.run(child)      # SAME engine. sequential (I-11).
```

M-6 introduces delegation, **not concurrency**. Concurrency is M-7 and requires
its own measurement ADR plus an explicit Director lift of I-11. A parent blocks
on its child. This is slower and it is correct: exactly-once settlement cannot be
proven while runs race, and M-7 exists precisely to measure whether the trade is
worth making. Building the two together would make both unfalsifiable.

---

## 5. Verification

```
tests/test_m6_delegation.py ......... 9 passed
  RF-55..59 attenuation   6
  RF-26     recovery      3

frozen substrate diff : 0 files
kernel TCB            : 1737 LOC (unchanged — spawn added zero kernel code)
```

The last line is the milestone's real claim: **delegation was added without the
trusted core growing by a single line.**

---

## 6. Integration checklist (remaining)

1. Register `agent.spawn` in the pack capability table with `sink: "privileged"`.
2. Bind `SpawnAdapter` in `runtime/wiring.py` as an intent interpreter — **not**
   in `kernel/`.
3. Allocate `ChildSpawned` / `ChildReturned` in the event roster with a single
   legal writer, plus reducer and conformance vectors. Per `sprint_active.md` §2,
   a new event kind requires allocation, writer proof, schema, and coverage —
   this is the one place M-6 touches frozen surfaces and needs a successor ADR.
4. Fold child cost into the parent trajectory as a nested invocation.
5. Add a kill-tree drill: SIGKILL the parent mid-child and assert the cold path
   returns `UNDETERMINABLE`, not a retry.

Item 3 is the only Director-escalation item in M-6.
