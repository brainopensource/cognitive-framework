# SPEC_M5A — Event-Derived Agent: Substrate Change Window (D-09…D-15)

Authority: ADR-0097 §3 (decided change set), ADR-0096 §6.2bis (window assignment), milestones
§M-5a, RF-96/97/99/100(computation). Executed as **one window** governed by **ADR-0098** (drafted
in SPRINT_UPCOMING; this spec is its technical annex). `M-5-BASE` re-tags exactly once at exit.

Entry conditions: M-4 CLOSED (RF-95 evidence accepted); ADR-0098 accepted; append/fold benchmark
baseline frozen. Exit: §9 gates green → tag `M-5-BASE`.

---

## 1. Scope of the window (and nothing else)

D-09 envelope `mhf.event/2` · D-10 vocabulary unification/deprecation · D-11 execution contracts ·
D-12 AgentView + five semantic kinds · D-13 checkpointed fold · D-14 RF-97 tooling gate switch ·
D-15 re-tag. Explicitly out: any M-6 spawn mediation, topology, scheduler, memory work.

## 2. Files

| Action | Path |
|---|---|
| modify | `schemas/mhf/event_envelope.schema.json` (→ defines `mhf.event/2`; retains `/1` in `oneOf` for readers) |
| regen | `vanguard/packages/domain/wire/types_gen.py` (codegen; adds folded kinds; adds provenance fields) |
| modify | `vanguard/packages/domain/ledger/events.py` (delete `_V4_ONLY_KINDS`; add `DEPRECATED_KINDS`; version-dispatch parser) |
| modify | `vanguard/packages/runtime/ledger_emitter.py` (write `/2`; populate authority fields; reject deprecated kinds; new kind ownership rows) |
| modify | `vanguard/packages/domain/ledger/reducer.py` (+5 kind handlers; checkpoint-aware `reconstruct_state`) |
| create | `vanguard/packages/domain/execution/{__init__,operation,lineage,scope}.py` |
| create | `vanguard/packages/domain/ledger/agent_view.py` |
| create | `vanguard/packages/runtime/ledger/checkpoints.py` |
| create | `schemas/mhf/{goal_declared,plan_revised,strategy_changed,progress_assessed,context_compacted,checkpoint}.schema.json` payload schemas |
| modify | `tools/linters/check_tcb_budget.py` (v2 per D-14) |
| create | `test/falsifiers/test_rf96_cold_reconstruction.py`, `test_rf97_tcb_budget_v2.py`, `test_rf99_authority_provenance.py` |
| modify | `docs/05_contracts/events.md` (kind table + deprecated register), `docs/01_law/RUNTIME.md` §15 gap-closure note |

## 3. Envelope `mhf.event/2` (D-09, RF-99)

New typed fields (names camelCase on wire, snake_case in `EventEnvelope`):

| field | type | req | semantics | validation |
|---|---|---|---|---|
| `authoritySource` | str enum-open: `capability` \| `approval` \| `policy` \| `system` \| `recovery` | ✓ | authority basis for the recorded operation (0096 §6.1) | non-empty |
| `policyVersion` | str | ✓ | governing policy/deterministic rule identity | non-empty; `"none"` allowed for pure observations |
| `approvalReference` | str \| null | ✓ (nullable) | `ApprovalResolved.eventId` when approval materially authorized | null ⇔ semantically inapplicable; never fabricated |
| `capabilityGrant` | str \| null | ✓ (nullable) | grant id (kernel `Grant`) under which the effect proceeded | populated for every kernel-dispatched effect event |

Population rules by writer role: kernel-role events populate `capabilityGrant` from the dispatched
grant and `authoritySource="capability"` (or `"approval"` when a suspension resolved);
approval-role → `authoritySource="approval"`, `approvalReference=self`; recovery-role →
`"recovery"`; session/orchestrator observations → `"policy"` with the active policy version from
`FrozenComposition`. `LedgerEmitter.__init__` gains `authority_defaults: Mapping[str, str]`;
`RoleScopedEmitter` enforces role-consistent values (test: forging `authoritySource="capability"`
from orchestrator role → `WriterAuthorityError`).

**Migration (dual-read/single-write).** `parse_event_envelope` dispatches on `schema_version`:
`/1` legacy read (fields default: `authoritySource="unrecorded"`, `policyVersion="unrecorded"`,
nulls) — the defaults are *reader-side projections*, never written. Emitter writes only `/2` after
cutover commit. `prev_digest` chain: each event's digest covers its own canonical form; the chain
crosses the boundary without recomputation. Falsifier: mixed-chain fresh-process replay parity test
(`test_rf99_…::test_mixed_version_chain_replays`). Rollback: emitter version flag (`WIRE_VERSION`)
can be reverted pre-tag; post-tag rollback = new ADR.

## 4. Vocabulary unification + deprecation (D-10)

Schema `kind` enum gains the 8 live V4 kinds: `ActivationChanged, ArtifactCreated,
CanaryPromoted→NO — dead`, correction: gains **`ActivationChanged, ArtifactCreated,
CompetencePriorRecorded, ConflictDetected, EffectPreviewed, EpisodeStateChanged,
EvidenceClaimProduced, ObservationProduced`** plus the 5 new M-5a kinds (§5). Codegen regenerates
`EventKind`. `domain/ledger/events.py`:

```python
DEPRECATED_KINDS = frozenset({
  "ObservationRequested","OperatorInvoked","OperatorSelected","CorrectionRecorded",
  "CandidateBuilt","CandidateAttested","CanaryPromoted","RollbackTriggered",
})
EVENT_KINDS = frozenset(k.value for k in _WireEventKind)          # schema is sole authority
READABLE_KINDS = EVENT_KINDS | DEPRECATED_KINDS                    # history tolerance
# parse_event_envelope: kind ∈ READABLE_KINDS
# LedgerEmitter._remember/append: kind ∈ DEPRECATED_KINDS → raise DeprecatedKindError
```

Reintroduction (expected consumer: M-8 promotion pipeline, ADR-0100) requires the full kind
package: ADR + INDEX allocation + writer role + reducer handler + payload schema + golden vector +
coverage test (ADR-0097 §3.2). `test_event_coverage.py` rewritten: asserts `EVENT_KINDS` derives
solely from schema; asserts every non-deprecated kind has reducer handling or an explicit
`REDUCER_NOOP_KINDS` entry with rationale.

## 5. Execution contracts (D-11) + semantic kinds (D-12 roster)

```python
# domain/execution/scope.py
@dataclass(frozen=True, slots=True)
class ExecutionScope:
    """The spatio-temporal boundary of a lineage. Authority view lives in kernel.attenuation.Scope;
    this value references it, never re-implements attenuation."""
    lineage_id: str
    budget: Mapping[str, int]          # 6D tensor keys: usd_micros, tokens, bytes, charged_millis, depth, turns
    max_depth: int; max_turns: int
    capability_grant: str | None       # kernel grant id (authority reference)
    terminal_conditions: tuple[str, ...]  # declarative, e.g. ("verified_done","budget_exhausted")
    def attenuated_for_child(self, *, budget_slice: Mapping[str,int], **narrowing) -> "ExecutionScope":
        """Child scope MUST be a strict narrowing; raises InvalidScopeAttenuation otherwise.
        Does NOT touch kernel grants — the caller attenuates authority via kernel.attenuate."""

# domain/execution/lineage.py
@dataclass(frozen=True, slots=True)
class LineageRef:
    lineage_id: str                    # == principal_id chain member today (compat note below)
    parent: str | None; root: str; depth: int

# domain/execution/operation.py
@dataclass(frozen=True, slots=True)
class OperationRecord:
    """Protocol shape only (ADR-0097 lock: no verb subclass hierarchy)."""
    operation_id: str; verb: str
    input_refs: tuple[str, ...]; output_refs: tuple[str, ...]   # artifact digests / event ids
    causation_id: str | None; lineage_id: str; scope_digest: str
    status: str                        # proposed|authorized|dispatched|observed|settled|committed|invalidated (0096 §4.2)
    resources: Mapping[str, int]
```

Compatibility mapping (documented in `05_contracts/events.md`): `lineage_id ≙ principal_id`,
`parent ≙ parent_principal_id`, nested episode ≙ `parent_episode_id` — the M-5a contracts *name*
the semantics the envelope already carries; no field duplication.

**Semantic kinds (writer role → payload → reducer effect):**

| Kind | Writer | Payload schema (key fields) | Reducer/AgentView effect |
|---|---|---|---|
| `GoalDeclared` | orchestrator | `mhf.goal/1` {goal, source, briefDigest} | sets `AgentView.goal` (latest wins; history kept) |
| `PlanRevised` | orchestrator | `mhf.plan/1` {revision:int, planDigest, planArtifact?, rationaleDigest} | appends plan version; revision 0 = creation |
| `StrategyChanged` | orchestrator | `mhf.strategy/1` {from, to, trigger, controllerId?} | sets `strategy`; increments `strategy_changes` |
| `ProgressAssessed` | orchestrator \| evaluator_gateway | `mhf.progress/1` {assessment ∈ advancing/stalled/regressing, signals{…}, basis[]} | appends to `progress_log` (M-6.5 input) |
| `ContextCompacted` | orchestrator | `mhf.context-compacted/1` ≙ CompactionRecord fields | supersedes `ClaimRecorded{compaction}` writer path (readers keep both) |

Kind-introduction criterion satisfied per milestone law: each changes the history we must
reconstruct (goal/plan/strategy/progress/context epoch are AgentView members).

## 6. AgentView (D-12)

```python
# domain/ledger/agent_view.py
@dataclass(frozen=True, slots=True)
class AgentView:
    lineage_id: str; goal: str | None
    plan_revisions: tuple[Mapping[str, Any], ...]     # ordered; last = current plan
    attempts: tuple[Mapping[str, Any], ...]           # proposal→settlement summaries (verb, outcome, idempotency_key)
    settled_effects: Mapping[str, str]                # idempotency_key → terminal status
    budget_consumed: Mapping[str, int]                # additive dims from Budget* events
    strategy: str | None; progress_log: tuple[Mapping[str, Any], ...]
    context_epoch: int                                # increments per ContextCompacted
    children: tuple[Mapping[str, Any], ...]           # ChildSpawned/Returned summaries
    terminal: str | None                              # RunTermination value or None
    covered_through: str                              # last folded eventId
    reducer_version: str

class AgentViewReducer(Protocol):
    def fold(self, checkpoint: "AgentViewCheckpoint | None",
             events: Iterable[EventEnvelope]) -> AgentView:
        """Deterministic under pinned reducer/schema versions; creates no facts; preserves
        lineage identity; tolerates READABLE deprecated kinds (no-op); raises ReducerError on
        kind outside READABLE_KINDS or non-monotonic seq within the lineage."""

def fold_agent_view(checkpoint, events) -> AgentView: ...   # canonical impl
```

**RF-96 falsifier** (`test_rf96_cold_reconstruction.py`): run a scripted episode (goal, plan,
2 revisions, 3 effects incl. one failure, strategy change, compaction, terminal) against
file-backed WAL in process A; kill; process B folds from disk only and must equal a recorded
golden AgentView (field-by-field), with **zero** access to process-A objects. A second case runs
`RecoveryScanner` first (interrupted mid-effect) and asserts the reconciled view.

## 7. Checkpointed fold (D-13)

`mhf.checkpoint/1` payload: {`projectionId` ("agent_view"|"ledger_state"), `reducerVersion`,
`schemaVersions`, `stateDigest`, `stateArtifact` (sha256 of JCS-serialized state in blob store,
role `checkpoint_state`), `coveredThroughEventId`, `coveredThroughSeq`}. Writer: new role
`checkpointer` (runtime-owned; `PRIVILEGED_KIND_OWNERS["CheckpointCreated"]={"checkpointer"}`).

```python
# runtime/ledger/checkpoints.py
class CheckpointManager:
    """deps: blob: BlobStorePort, emitter: RoleScopedEmitter("checkpointer"), store: EventStorePort,
    policy: CheckpointPolicy (interval by event-count/turns; pure)."""
    def maybe_checkpoint(self, view: AgentView) -> None: ...
    def load_latest(self, lineage_id: str) -> AgentViewCheckpoint | None:
        """Verify stateDigest against blob bytes; reducerVersion must match pins; any mismatch ⇒
        return None (fail-closed to cold fold) and emit KernelAlarm?—no: log via telemetry, never
        alarm (checkpoint invalidity is degradation, not authority violation)."""
def reconstruct_agent_view(store, blob, lineage_id) -> AgentView:
    # load_latest → fold(checkpoint, suffix)   else fold(None, full history)
```

Perf gate: `bench_append_fold` extended — checkpointed reconstruction ≤ 20% of cold-fold time on
the 10k-event fixture (target, not law; recorded in benchmark artifact).

## 8. RF-97 budget v2 (D-14)

`check_tcb_budget.py` v2 outputs JSON: `{closure:[modules], logical_loc:{...},
public_contracts:len(kernel.__all__), privileged_ops:#kernel-owned kinds, dependencies:{stdlib,domain,ports},
domain_concepts:0-gate (deny-list scan: fs/git/code/test/coding/research terms in kernel),
extension_knowledge:0-gate (import scan for adapters|packs|runtime), change_amplification:
reverse-import count of kernel symbols}`; CI gate fails on closure drift (new module in closure
without allowlist update + ADR reference) or any 0-gate violation. LOC alarm retained as one row.

## 9. Exit gates → `M-5-BASE`

1. All new/changed payload+envelope schemas have golden JCS vectors; codegen clean (A-4).
2. RF-96, RF-97, RF-99 falsifier tests green; RF-100 `reproducibility_current` computation added
   (reads run-close claim, recomputes, records as new claim; never overwrites).
3. Mixed-version chain fresh-process replay parity green; full suite green incl. sandbox envs.
4. Deprecation write-rejection + historical-read tests green; `_V4_ONLY_KINDS` deleted.
5. Bench: append/fold regression < 10% vs frozen M-4 baseline; checkpoint speedup recorded.
6. Docs: `events.md` kind table + deprecated register; `RUNTIME.md §15` gap marked closed.
7. Kernel semantic diff == 0 for the window (RF-98 pre-check) — the window changes substrate,
   never kernel; any kernel edit here fails the window by definition.
Then: tag `M-5-BASE`; record pin set; ADR-0098 status → implemented.

## 10. Sequence — cold reconstruction (target)

```mermaid
sequenceDiagram
  participant P as Fresh process
  participant CM as CheckpointManager
  participant B as BlobStore
  participant ES as EventStore(WAL)
  participant R as fold_agent_view
  P->>CM: load_latest(lineage)
  CM->>ES: read(CheckpointCreated latest)
  CM->>B: get(stateArtifact) & verify stateDigest/pins
  alt valid checkpoint
    CM-->>P: AgentViewCheckpoint
    P->>ES: read(suffix > coveredThroughSeq)
  else invalid/absent
    CM-->>P: None
    P->>ES: read(full lineage history)
  end
  P->>R: fold(checkpoint?, events)
  R-->>P: AgentView (== golden; RF-96)
```
