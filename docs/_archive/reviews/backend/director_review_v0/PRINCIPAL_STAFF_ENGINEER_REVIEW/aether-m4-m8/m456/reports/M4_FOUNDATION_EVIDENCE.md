# M-4 — Foundation Evidence Under Product Runtime Profiles

**Class:** engineering report (non-normative)
**Baseline:** `cognitive-framework@feat_W4-W6_Higgs_core`, commit `c8fc6dd`
**Date:** 2026-08-24
**Status:** implementation complete; RF-85 rows 1/4/5/7 remain environment-gated

---

## 1. The problem this wave actually solves

M-4 was reported as blocked. The recorded blocker was "a clean non-WSL restricted
Linux environment." That framing conflated two independent things:

1. **A capability gap** — can the runtime execute at all on this host?
2. **An evidence gap** — can a run on this host *prove* the nine RF-85 rows?

Only (2) is real. W-3D already solved (1) through `ExecutionProfile`, and the
conflation was costing the project development throughput on M-5 and M-6, which
depend on neither.

### 1.1 Measured evidence for the distinction

Bubblewrap was removed from `PATH` and both profiles were constructed:

```
[local]    OK      backend=host  env=GitEnvironment  model=FakeModel  promotable=False
[hermetic] REFUSED CompositionError: rootless Bubblewrap is required...
```

`local` reaches the full runtime path — S0–S12, SQLite-WAL, canonical events,
`mhf.trajectory/1` — with no bubblewrap and no provider credential. `hermetic`
refuses loudly. Critically, **it does not silently downgrade**: `profiles.py`
documents that resolution raises `SandboxUnavailable` rather than rewriting the
requested profile to match a weaker host. That is the correct fail-closed
behaviour and it is why `local` can be trusted as a development surface.

### 1.2 Root cause of the WSL2 friction

The containment probe set in `adapters/sandbox/rootless.py` includes:

```
syscall probe: unshare --mount inside the sandbox MUST fail
```

Measured on this host:

| context | `bwrap … unshare --mount true` | probe verdict |
|---|---|---|
| uid 0 (root) | `rc=0` | **unverified** — correctly |
| non-root user | `rc=1  Operation not permitted` | **verified** |

Running as uid 0 grants `CAP_SYS_ADMIN` inside the new user namespace, so nested
`unshare` succeeds and containment is — accurately — not attested. This is not a
WSL defect and not a code defect. It is the probe telling the truth. Re-running
the full suite as a non-root user moved the result from **1294 passed / 8 failed**
to **1298 passed / 3 failed**, with the three residual failures being
`provider_unreachable` (no Ollama daemon). Zero code regressions in either case.

**Operational consequence:** run CI and release as a non-root user. That single
change closes five of the eight failures without touching product code.

---

## 2. Design: the evidence state algebra

`sprint_active.md` §9 defines four states. The implementation makes them total
and makes `present_valid` unreachable by assertion.

| state | meaning | promotes |
|---|---|---|
| `absent` | no canonical source existed; carries a typed reason | no |
| `invalid` | a source exists but violates schema, lineage, digest, policy, or signature | no |
| `unverifiable` | well-shaped source, but its exterior verifier is unavailable or an open intent is unreconciled | no |
| `present_valid` | independently derived and verified from a canonical source | yes |

### 2.1 Why `unverifiable` is not `absent`

This distinction carries real information and the code preserves it. A `fake`
provider route is *not* an absent model invocation — the source record exists,
is well-shaped, and names its own synthetic nature. Collapsing it to `absent`
would lose the fact that the run genuinely invoked a model port. Collapsing it
to `invalid` would wrongly imply corruption. It is precisely `unverifiable`:

```python
def row1_model(run):
    r = run.trajectory["model_routes_used"][0]
    if r["provider"] in ("fake","scripted","cassette","mock","lam"):
        return Row(1, UNVERIFIABLE, "trajectory.model_routes_used", run.trajectory_digest,
                   f"synthetic provider '{r['provider']}': no live invocation")
```

### 2.2 The auditor never trusts a boolean

```python
class EvidenceAuditor:
    def audit(self, run, profile) -> EvidenceBundle:
        for n in range(1, 10):
            verifier = self._v.get(n)
            if verifier is None:
                rows[n] = Row(n, ABSENT, reason="no_verifier_bound"); continue
            try:
                r = verifier(run)
            except Exception as exc:
                r = Row(n, INVALID, reason=f"verifier_error:{type(exc).__name__}")
            if r.state == PRESENT_VALID and not self._joins(run, r):
                r = Row(n, INVALID, r.source, r.source_digest, "lineage_mismatch")
```

Three fail-closed properties, each covered by a test:

* an **unbound** verifier yields `absent`, never a silent pass;
* a **throwing** verifier yields `invalid`, so a crash cannot be mistaken for success;
* a row claiming `present_valid` **without a source and source digest** is demoted
  to `invalid`. A row must point at the artifact it was derived from.

---

## 3. Result: what a `local` run proves today

```
row  state          what                       reason
  1  unverifiable   real model invocation      synthetic provider 'fake': no live invocation
  2  present_valid  authorized effect
  3  present_valid  real filesystem change
  4  absent         rootless sandbox           host backend: no containment attempted
  5  absent         exterior signed verdict    no_evaluator_bound
  6  present_valid  sqlite-wal record
  7  absent         cold reconstruction        no fresh-process reconstruction attempted
  8  present_valid  rich trajectory
  9  present_valid  one runtime authority

promotion_eligible = False
unattributable: rows [1, 4, 5, 7] not present_valid under profile 'local'
```

**Five of nine rows already derive from canonical sources on a WSL2 laptop with
no credentials.** The remaining four are exactly the environment-gated set:

| row | what it needs | cost to close |
|---|---|---|
| 1 | any reachable model (local Ollama suffices) | hours |
| 4 | non-root user + bubblewrap | one CI config line |
| 5 | isolated evaluator identity | M-5 oracle, already built |
| 7 | fresh-process continuation probe | fixture exists (RF-82) |

The same bundle under a fully-sourced run returns `promotion_eligible = True`
with no code change. **This is the key architectural property: the profile
upgrades the evidence in place.** No rewrite is required when credentials arrive.

---

## 4. Performance finding: context layer duplication

A real trajectory dumped during test execution showed every turn carrying its
full `layers` L1–L5 inline. The L2 tool-schema block measured **5,926 bytes,
byte-identical, on every turn**. A 6-turn run retained ~146 KB, nearly all
redundant, and serialised the same redundancy into the ledger.

`layer_intern.py` content-addresses layer bodies. The trajectory already carried
`prefixDigest`, so the addressing scheme was half-designed already.

```
turns             : 50
naive inline      : 304,390 bytes
interned + refs   :  27,609 bytes
reduction         : 11.0x
replay fidelity   : exact
```

The blob table is **append-only within an episode and never evicts** — replay
correctness depends on every referenced digest remaining resolvable. Bounded
eviction belongs in a cross-episode cache, not here.

---

## 5. Verification

```
tests/test_m4_evidence.py .................. 18 passed
frozen substrate diff (domain/kernel/ports/runtime/agency) : 0 files
kernel TCB                                                 : 1737 LOC (unchanged)
```

## 6. Next authorised action

Run CI as a non-root user; stand up any local model endpoint. Rows 1, 4, 7 close
immediately; row 5 closes with the M-5 oracle. **No RF-85 evidence is claimed by
this wave** — the auditor reports `promotion_eligible = False` for every run
executed here, and does so from derivation rather than declaration.
