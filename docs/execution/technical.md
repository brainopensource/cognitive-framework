---
id: execution.technical
canonical_id: execution.technical
class: execution
authority: execution
truth_plane: TARGET
status: living
owner: repository-governance
canonical_for:
  - execution-technical-handbook
version: "0.9.6"
purpose: Self-explaining engineering handbook for future work. Present-tense architecture stays in docs/architecture and docs/backend.
derived_from:
  - docs/reports/reviews/electroweak_v092/plans/DEVELOPMENT_FINAL_PLAN.md
  - docs/reports/reviews/electroweak_v092/plans/DEVELOPMENT_FINAL_PLAN_B.md
  - docs/reports/reviews/electroweak_v092/plans/DEVELOPMENT_FINAL_PLAN_v2.md
  - docs/reports/reviews/electroweak_v092/plans/PHASE-0_DEVELOPMENT_FINAL_PLAN.md
lock_head: "bf56eea9"
last_verified: 2026-09-12
relationships:
  - execution.milestones
  - execution.feature_spec
  - execution.tasks
  - execution.backlog
---

# Technical Specifications (Detailed)

> **Scope-breach record (2026-09-12).** The reconciliation that produced this file
> removed roughly 5,400 of 6,750 lines — far beyond the ~15% stop threshold the
> assignment set, which required halting for an explicit decision first. That
> decision was not obtained in advance. What was removed: duplicated plan-catalog
> imports ("From v2", "From B"), the §12–24 harness-mechanics narrative, and stale
> inventories — all of which survive in
> `docs/reports/reviews/electroweak_v092/`. What was retained: the near-term
> handbook and the complete FH-1 algorithms (`prepare_and_promote`,
> `commit_critical_section`, `reconcile_unknown_commit`, `export`,
> `restore_or_quarantine`, `recover_export`, `delegate`, `settle`,
> `reconcile_delegation`, `cancel`, `run_campaign`, `acquire_node_lease`,
> `dispatch_node`, `replan`) and the fault-injection index. Leadership should
> ratify or reverse this breach explicitly; a good outcome does not retroactively
> authorize bypassing a stop rule. **Ratified retrospectively on 2026-09-12** — see
> [milestones.md](milestones.md#ratified--technicalmd-consolidation-2026-09-12). The
> stop rule stays in force for future passes.


Developers SHALL use this file plus [`spec.md`](spec.md), [`tasks.md`](tasks.md), [`milestones.md`](milestones.md), and [`backlog.md`](backlog.md). The originating plan drafts now live under `docs/reports/reviews/electroweak_v092/plans/` and are historical reference, not guidance. Engineering autonomy inside a READY row is governed by [RUN-04](spec.md#run-1-leadership-execution-decision-2026-09-12): choose helpers, fixtures, wording and equivalent algorithms freely; return to leadership before adding a public port or schema, changing presets, widening scope or authority, disabling verification, or altering an acceptance threshold.

**Present vs future.** Source implements; accepted specification clauses constrain.
FH-1 is proposed detail, not HEAD architecture. This handbook is subordinate to
RUN-1; historical recipes do not authorize implementation.

**Navigation before coding.** `uv run lda identity --json` then `uv run lda doctor --json`. Then `python3 tools/docs_rag_v0.py --file <path>` for the file you will edit. Kernel stays domain-blind (I-7). AST preflight belongs in `adapters/environment/`, never `kernel/dispatch.py` S7/S8.

**Canonical task IDs** are `T-01`… in [`tasks.md`](tasks.md). v2 `SUB-*` / `TXN-*` are aliases in [`backlog.md`](backlog.md). Live kernel pipeline package `SUB-01` in the backlog is **not** v2 admission.

## Active control implementation guide (2026-09-12)

Use [RUN-1](spec.md#run-1-leadership-execution-decision-2026-09-12) and the
[active work table](tasks.md#active-autonomous-work-2026-09-12). Read only the
guidance for the admitted task. NT-1 recipes below are preservation references
for accepted historical work; they are not instructions to repeat T-98–T-111.

### Control boundary recipe

1. **T-26a:** Trace `benchmarks/ladder/control.py`, `metrics.py`, `evidence.py`
   and their callers. `require_frozen` currently checks status, a truthy subject,
   harness and worker count; it does not validate all fields named by its error
   message. Pure metrics compute fixture diagnostics; `canary_disposition` accepts
   a boolean frozen flag. Implement complete explicit record validation and a
   separate publication admission path using those modules. Keep fixture scoring
   pure. An empty supplied record must not fall back to the ambient checked-in file.
2. **T-51:** Enumerate candidate tasks through existing corpus code. Reject
   generated cache entries and reused development tasks. Bind the 30 task IDs,
   order, class counts, source and oracle digests. Record absent or unusable classes
   rather than constructing fake membership. Corpus preparation makes no model call.
3. **T-52:** Validate rows before computing the binary denominator. Join task IDs
   to the frozen membership, reject duplicates and subject/configuration mismatch,
   retain every scheduled slot, and separate missingness from binary failure.
   Derive counts from admitted rows, not caller claims. Use existing Wilson code;
   preserve actual or unknown cost. Apply the false-completion veto before a
   positive result can be published, including on rows excluded from pass rates.
4. **T-26b:** Use `benchmarks/agentic_harness_matrix_benchmark.py` through
   `benchmarks/product_path.py::execute_product` and `entrypoint.execute`.
   Its helper defaults to local/six turns: pass the frozen balanced/product
   identity and attenuation explicitly. `benchmarks/ladder_runner.py` is a
   different harness; its LiveBudget tests alone do not qualify the product arm.
   Wire the admitted publication boundary into the actual report caller. Use injected
   hermetic provider/evaluator fixtures to prove refusals at that caller and stop
   before an extra attempt/call. Budget post-accounting alone is not proof of a
   safe pre-dispatch reservation. Reconcile all applicable prerequisite receipts;
   do not create a second runtime to avoid an integration gap.
5. **T-26/T-27:** After prerequisite and independent candidate review, freeze the
   actual record with an explicit resource envelope. Existing L0 requirements
   remain; a local zero-paid-call route is usable only if its model and environment
   are eligible and authorized. Missing live resources block measurement, not the
   preceding engineering tasks. Publish all 30 slots or the early-stop evidence;
   never fill missing slots by retries. Independent acceptance closes MS-CONTROL.

Expected verification includes a complete valid fixture, malformed/empty manifests,
every altered identity, duplicate attempts, missing slots, false completion,
expired/exhausted resources, and correct diagnostics on replay data. Existing
test modules are starting points; no test result is claimed here. Focused failure
must expose the changed behavior; an ImportError is not a sufficient falsifier.
Run declared complete gates in the isolated environment for implementation
acceptance. The documentation-only planning review does not run those suites.

### Long-session handoff and bounded repair

Take a READY task and its lease; record the current subject and a pre-edit baseline.
Use the task's session envelope and preserve a recovery allowance. Implement the
smallest coherent slice, run its falsifier, and inspect the actual failure before
each repair. After three unsuccessful repair cycles or a command/session timeout,
stop with a resumable handoff; do not broaden tests or mutate unrelated files to
manufacture progress. Resume retains unresolved effects, ownership and budgets.
An accepted package permits ordinary private implementation choices without a
new leadership round. Public contracts, scope/authority, acceptance thresholds,
paid resources and destructive migrations stay at their declared decision boundary.

### Post-control depth and source compatibility

T-129 refines memory/skills first. Trace the bounded static `skill_index.py`,
`SkillLibrary` in `ports/memory.py`, the durable memory adapter, signed skill
evaluation, and `governance/learning.py`. Demonstrate composition wiring and
restart/revocation/rollback before claiming durable skill-library completion.
Do not use the in-memory `skill_lifecycle.CompositionRegistry` as durable storage.
Keep learning lift separate from mechanical catalog/retrieval acceptance.

Retain FH-1 invariant and fault-model detail as review input. Defer additional
algorithm expansion until a branch is selected. Before adopting its file map,
resolve the `runtime/memory.py` and `benchmarks/protocols.py` file/package collisions,
reuse `ports/blob_store.py`, and account for schema registration, event reducers and
composition bindings. A handwritten algorithm-to-file table proves none of these.
Campaign/MCTS/RTV expansion is deferred; voting never accepts a patch.

## Near-term implementation handbook (NT-1)

**Accepted historical scope; preservation guidance.** NT-1 on `2989d57d` is not
remaining implementation. The following recipes explain that scope and its
verification obligations when affected. Current work is selected above. Historical
source labels and directory assignments do not grant active leases.

### Baseline recipe and contributor isolation

T-98 creates an independent disposable repository, not a linked worktree sharing the contributor index. Capture source/index/corpus digests; redirect test databases before imports under unittest; remove provider credentials from child environments and deny network at the execution boundary. Build each temporary Git fixture with its own `.git` and verify its resolved root before any write/stage. A pytest-only `conftest` hook cannot establish safety for unittest. Copy/install declared dependencies in the isolated environment; do not quietly substitute a different test runner.

T-101 inventories collection and executes the complete suite only in that environment. Include every import error and baseline failure; compare exact source/index/corpus state afterward. The expected collection inventory must derive from current test modules and protected falsifier IDs, not the historical number 2,855. A count dropping without a recorded successor is a gate failure. A missing `just` executable requires execution of all recipe bodies, not a PASS for the subset available. Install/fix declared dependencies under C ownership; record failures without suppressing them.

Root tasks T-99/T-100 can proceed concurrently in independently isolated focused fixtures: A proves the terminal-projection defect; B defines pure value round trips. Their completion does not substitute for the full baseline gate. T-109 must incorporate every still-open failure identified by T-101. Deleting a duplicated implementation is preceded by caller, registry/resource and test-owner checks. Port required lab/security assertions; do not restore obsolete engines or discard falsifiers for a lower red count.

### Integration map and schema migration

| Reference primitive | Integrate into existing owner | Required adaptation |
|---|---|---|
| `MemoryView.capture/encode/decode`, `critical_state` | `domain/task_state.py`; runtime fold/checkpoints through A | Canonical byte snapshot, full SemanticTaskState retained; add lineage/reducer/cursor binding from NT-1.2. Reject stale/unknown identity before prompt use. |
| `Prefix.build`, `compile_packet` | `agency/context/compiler.py`, `layers.py`, `compaction.py`, `distiller.py` | Stable schema-list order; final serialized counting; bounded cardinality/body size; full action/result units; preserve critical state and artifact-bound omissions. Do not create `progressive.py` or a second compiler. |
| `PromptCodec` | Existing model request serializers under A | Real provider dialect and counter identity; supported cache controls; provider usage or explicit null. Local JSON-envelope counting is not evidence about a differently serialized remote request. |
| `Recovery`, `recover` | `agency/episode/protocol_recovery.py`, existing engine recovery branch | Merge fields and bounded history into ProtocolRecoveryState; use versioned readers; remove consultation from the near-term policy. Persist decisions and counters through runtime. |
| `stage`, `transact`, `delegate_readonly` | **[PROPOSAL] outside this iteration** | Do not activate CAS promotion, new topology or specialists. Existing patch/attenuation bug fixes stay on their current paths. |

Part 3 is design provenance, not an alternate normative import. Production must implement NT-1 schemas, including stricter lineage checks and the no-consult recovery action set. Use current JCS `canonical_bytes`/`digest_of`, not ordinary JSON formatting as a substitute for canonical identity. Validate booleans separately from integer counters. A frozen dataclass with mutable nested mappings is not an immutable snapshot: capture canonical bytes and reconstruct fresh mappings when needed.

Readers support existing accepted schema versions explicitly and reject unknown required versions. Never rewrite historical event identities. C owns registered schema/generator inputs; A owns emitter and reducer integration. Persist selection and recovery facts in registered `mhf.event/2` envelopes before external dispatch. If durable emission fails, stop the next request rather than proceed with unrecorded decision spend. Record policy/serializer/counter identity at composition, not inferred from class names alone.

### Reference context-selection algorithm

Implement this order in the existing compiler; no model call occurs during selection:

1. Verify snapshot lineage/cursor/reducer and current subject. Freeze L1–L3 and canonical tool ordering for the epoch. Validate capability-card prefix <=4096 characters.
2. Reserve output, safety and a recovery allowance from the model window. Refuse a nonpositive usable budget. Apply item/body bounds before invoking a tokenizer.
3. Render the exact objective/constraints, current plan/next action, modified resources, material failure, applicable verification, settled effects and remaining budgets. Retain the complete state as an authorized artifact; relevant dead ends enter source-bound evidence.
4. Remove stale evidence. Serialize through the selected provider codec and count that final request. Above 80% usable, compact toward 60%; both thresholds are versioned policy settings.
5. Elide lowest-priority evidence bodies, then old result bodies into artifact receipts. Drop lowest-priority evidence next, then oldest complete interactions. Keep the newest complete interaction. Recount after each change or use proven conservative incremental bounds plus a final exact/bounded recount.
6. Mandatory content may exceed the low watermark but never the hard ceiling. If still too large, return `CONTEXT_BUDGET_EXCEEDED` with no inference. Upstream may reduce an oversized result into a structured receipt; it cannot summarize away the original requirement.
7. Emit request/prefix/state/policy digests and omission reasons; then infer under the reserved budget. Actual cached reads/writes remain telemetry with explicit source/missingness, not a guarantee made by the compiler.

Keep passing-test evidence even when raw passing logs leave the prompt. Failure snippets alone are insufficient: retain argv/environment/subject identity, counts, exit status and output artifact references. Eviction is a presentation decision; it never erases ledger history or resets verification freshness. Tool outputs remain untrusted content, including text that asks to replace the goal.

### Reference deterministic recovery algorithm

The following pure policy kernel is an executable guide to NT-R01/R02. Integrate its semantics into the existing recovery class, not as another loop. The caller validates schema types, supplies normalized fingerprints, persists the returned decision and counters, and decrements the shared reservation. `history` includes the current attempt and excludes transport/poll-only records; each tuple is `(fingerprint, outcome, verified_progress_key)`.

```python
from dataclasses import dataclass
from typing import Literal, Sequence

Action = Literal["continue", "wait", "reground", "replan", "stop"]

@dataclass(frozen=True)
class CoreDecision:
    action: Action
    interventions: int
    transport_retries: int
    delay_ms: int
    reason: str

def decide_recovery(
    history: Sequence[tuple[str, str, str]], *, failure: str | None,
    interventions: int, transport_retries: int,
    remaining_turns: int, remaining_ms: int, jitter: float,
) -> CoreDecision:
    for value in (interventions, transport_retries, remaining_turns, remaining_ms):
        if type(value) is not int or value < 0:
            raise ValueError("invalid nonnegative counter")
    allowed = {None, "permission", "permanent", "budget", "transient",
               "protocol", "patch", "verification", "context", "tool"}
    if failure not in allowed or not 0 <= jitter <= 1:
        raise ValueError("invalid failure or jitter")
    if remaining_turns == 0 or remaining_ms == 0:
        return CoreDecision("stop", interventions, transport_retries, 0, "budget")
    if failure in {"permission", "permanent", "budget"}:
        return CoreDecision("stop", interventions, transport_retries, 0, failure)
    if failure == "transient":
        if transport_retries >= 3:
            return CoreDecision("stop", interventions, transport_retries, 0, "retry_limit")
        delay = int(min(8000, 500 * 2 ** transport_retries) * (0.5 + jitter / 2))
        if delay >= remaining_ms:
            return CoreDecision("stop", interventions, transport_retries, 0, "deadline")
        return CoreDecision("wait", interventions, transport_retries + 1, delay, "transient")
    window = tuple(history[-6:])
    if not window or any(len(item) != 3 or not all(item) for item in window):
        raise ValueError("semantic history requires complete identities")
    repeated = window.count(window[-1]) >= 3
    cycle = any(len(window) >= 2 * n and window[-n:] == window[-2*n:-n]
                for n in (2, 3))
    stagnant = len(window) == 6 and len({item[2] for item in window}) == 1
    if not (failure or repeated or cycle or stagnant):
        return CoreDecision("continue", interventions, transport_retries, 0, "progress")
    if interventions >= 2:
        return CoreDecision("stop", interventions, transport_retries, 0, "intervention_limit")
    action: Action = "reground" if interventions == 0 else "replan"
    return CoreDecision(action, interventions + 1, transport_retries, 0,
                        failure or "no_progress")
```

Keep at most twelve attempt records in durable recovery state. Distinct fresh evidence may justify repeated syntax/tests; changed prose/timestamps do not. Persist chosen jitter delay and deadline, not a random generator state. Pending-operation polling is handled before this policy: reconcile the existing handle under its original deadline, charge elapsed budget, and never create a second operation. Unknown external effects keep their reservation; no refund solely because a transport call raised.

Recovery does not change grants, tool authorization or the parent budget. Near-term exhaustion stops after reground/replan; Part 3's optional `consult` branch is not promoted. T-80 can later consume this detector to study different workspace/tool policies after MS-CONTROL. On stop, reconcile existing owned mutation/recovery work; report `RECOVERY_FAILED` if restoration cannot be proved. Do not claim that existing filesystem transactions already have crash-safe CAS promotion.

### Gate and handoff recipe

Pure contracts may land before baseline acceptance, but runtime enablement T-107 requires T-109. C accepts MS-BASELINE from complete integrated receipts; A binds context/recovery only after B's values/algorithms and A's provider codec are ready. B/T-77 then qualifies cache/receipt behavior without assuming a backend hit rate. A/T-110 runs a >=100-turn deterministic scenario with forced compaction, restart, stale verification and pending-operation exhaustion using a dedicated test profile. It MUST NOT enlarge balanced's product turn ceiling.

T-111 reruns all required gates on the final subject, reconciles MS-CONTEXT and hands a clean exact identity to T-26. Register policy, model, prompt, tool and serializer identity before live L0/L2 measurement; changed behavior invalidates an earlier freeze. Neither mock success nor a negative valid control result accepts a positive capability gate. C updates only the existing five execution files and generator-produced knowledge; production changes also update their mapped architecture owners.

### Remaining critical path: implementation runbook

Historical NT-1 path, completed on its accepted subject. Consult only for
preservation or a specifically admitted regression task; current sequencing is
the active control guide, not the checklist below.

The only near-term dependency path is:

```text
T-109 -> MS-BASELINE
MS-BASELINE + T-107 + T-77 -> T-110
T-109 + T-110 -> T-111 -> MS-CONTEXT
MS-CONTEXT -> T-26 control-freeze work may begin
```

T-77 may be implemented before T-109 because its accepted prerequisites are T-104/T-105. T-107 cannot be enabled before T-109. If A and B work concurrently, use isolated repositories or explicit disjoint file leases: A owns runtime integration and B owns context compiler/compaction. C alone edits execution status and generator inputs. Merge T-107 and T-77 before constructing T-110 so the preservation fixture exercises the actual integrated path.

#### Multi-day autonomous integration recipe

Use a multi-day batch to reduce coordination overhead without weakening acceptance.
The duration is planning metadata only; task ordering still comes exclusively from
`requires:` edges.

1. **C establishes the shared subject.** Start from T-107 candidate `cae7c98d`,
   integrate T-77 candidate `37813a65`, register `ContextSelectionRecorded` through
   canonical generator inputs, regenerate derived artifacts, and run the combined
   event/context/runtime gates. C publishes the clean integration SHA to both source
   owners. A branch-local receipt cannot substitute for this combined receipt.
2. **A and B work concurrently from that SHA.** A owns T-110 and any runtime,
   checkpoint, session, product-consumer or provider defects exposed by the fixture.
   B owns compiler, layer, compaction, receipt-distillation and recovery-policy
   defects. Each stream may make multiple coherent commits and run its own development
   loops without an intermediate governance decision. Never share a writable checkout
   or concurrently lease the same path.
3. **C prepares evidence in parallel.** C alone audits preset/catalog configuration,
   corpus manifests, Wilson/cost calculations, evidence-row validation, hypotheses,
   frozen-canary refusal and the L0 operator recipe for T-51/T-52/T-79/T-89/T-92–T-95.
   Preparation is hermetic. Keep the control record unfrozen and make no provider call.
   A supplies fixes to the product path; B does not edit C-owned benchmark assets.
4. **C serially converges.** Integrate A and B, route a consolidated defect list to the
   source owner when necessary, and rerun affected focused suites after each repair.
   Once executable changes stop, execute T-111 and the complete T-109 recipe on one
   clean subject, regenerate knowledge, reconcile all five execution files and prepare
   one Leadership package.
5. **Leadership decides once.** An independent reviewer evaluates the complete subject,
   receipts and missingness. Acceptance closes MS-CONTEXT and authorizes T-26 work.
   Rejection returns one consolidated defect inventory. Routine development failures
   and intermediate commits do not create governance gates.

Commit boundaries should preserve reviewability: keep schema/catalog integration,
T-110 behavior, B-owned context/recovery repairs, C-owned control-instrument readiness,
and final evidence reconciliation distinguishable. Do not combine an unrelated session
decomposition, terminal-outcome rewrite or context migration in one patch.

#### T-109 exact-subject baseline procedure

Use an isolated repository with independent `.git`, not a linked worktree that shares the contributor index. Redirect temporary directories, bytecode and test databases into the isolated root or temporary storage. Remove provider keys and block network. Begin from a clean committed subject.

```bash
git rev-parse HEAD
git status --porcelain
sha256sum justfile uv.lock package-lock.json
UV_CACHE_DIR=/tmp/aether-uv-cache uv run lda identity --json
UV_CACHE_DIR=/tmp/aether-uv-cache uv run lda doctor --json
UV_CACHE_DIR=/tmp/aether-uv-cache uv sync --frozen

UV_CACHE_DIR=/tmp/aether-uv-cache uv run python3 -m unittest \
  test.contracts.test_suite_nonmutation \
  test.contracts.test_collection_integrity \
  test.tools.test_check_test_hygiene -v

UV_CACHE_DIR=/tmp/aether-uv-cache uv run python3 \
  -m unittest discover -s test -t .

UV_CACHE_DIR=/tmp/aether-uv-cache uv run just check
UV_CACHE_DIR=/tmp/aether-uv-cache uv run just verify
npm run typecheck
npm --workspace @vanguard/cli test
git status --porcelain
```

The complete discovery command is authoritative. If it fails, preserve its output and run the smallest focused module needed to diagnose the failure. Fix the owning source or test fixture, commit a new candidate and restart the broad gate. A focused pass after a broad failure demonstrates localization only. It does not convert the broad receipt to green. Test counts are accepted only when collected equals passed plus failed plus errors plus skipped and executed equals passed plus failed plus errors.

Record exact commands, exit codes, environment versions, start/end times, output digests and protected pre/post state. Store large raw output in the existing evidence mechanism or an ephemeral CI artifact; do not create a Markdown report. Put only the concise accepted receipt in `tasks.md` and milestone disposition in `milestones.md`.

#### T-107 runtime binding sequence

The runtime integration uses the existing `Session`, `LedgerEmitter`, task-state fold and episode recovery objects. The core rule is write-before-use: any decision that authorizes external work becomes durable before that work occurs.

```python
def execute_next_turn(session, ledger, model, environment):
    events = ledger.read_verified(session.episode_id)
    state = fold_task_state(events, objective=session.objective)
    state = validate_reconstruction(
        state,
        subject=session.subject_digest,
        lineage=session.lineage_id,
        reducer=session.reducer_version,
        composition=session.composition_digest,
    )
    reconcile_open_intents_and_children(events, environment)

    epoch = bind_epoch_identity(
        prompt=session.system_prompt,
        tools=session.ordered_tool_schemas,
        context_policy=session.context_policy,
        model_route=session.model_route,
        serializer=session.prompt_codec.serializer_id,
        counter=session.prompt_codec.counter_id,
        recovery_policy=session.recovery_policy,
    )
    selection = session.context_compiler.compile(state, epoch=epoch)

    # Atomic gate: append failure means zero model calls.
    ledger.emit_registered(
        "ContextSelectionRecorded",
        payload=selection.identity_payload(),
    )
    proposal = model.infer(selection.final_serialized_request)

    outcome = session.dispatch_or_classify(proposal)
    recovery = session.recovery_policy.decide(state.recovery_state, outcome)

    # Atomic gate: append failure means zero wait/retry/next dispatch.
    ledger.emit_registered(
        recovery.registered_event_kind,
        payload={"recoveryState": recovery.state.to_dict()},
    )
    return apply_durable_recovery_action(recovery)
```

`identity_payload()` must include the fields required by `aether.prompt-selection/1`, final serialized token count and ordered omission reasons. Do not emit prompt bodies as general ledger metadata; retain authorized prompt bytes through the existing artifact boundary and bind them by digest.

The recovery carrier must be a kind admitted by the event schema. `runtime/task_state.py` currently recognizes compatibility spellings, but a reducer branch is not a registration. If T-107 chooses `RecoveryStateUpdated`, C first adds it to canonical schema/catalog generator input and test vectors. Otherwise extend the registered `EpisodeStateChanged` payload without weakening its existing consumers. In both cases `check_event_coverage.py` must prove every production-emittable kind is registered.

Fresh-process resume follows this pseudocode:

```python
def resume_without_replay(ledger, task, ports):
    events = ledger.verify_and_read(task.episode_id)
    state = fold_task_state(events, objective=task.brief)
    validate_schema_lineage_subject_and_policy(state, task)

    reconcile_open_intents(events, ports.environment)
    reconcile_open_children(events, ports.child_runtime)
    state = fold_task_state(ledger.verify_and_read(task.episode_id), objective=task.brief)

    assert every_settled_descriptor_is_unique(state.settled_effects)
    assert state.recovery_state.counters_are_monotonic()
    assert state.remaining_budgets.do_not_exceed_declared_ceiling()

    if state.pending_operation:
        return reconcile_under_original_deadline_and_reservation(state)
    return compile_next_turn(state)
```

Required fault-injection tests interrupt at each boundary:

| Boundary | Injected fault | Required observation |
|---|---|---|
| Before selection append | Ledger rejection | Zero model calls; explicit runtime failure. |
| After selection append, before inference | Process crash | Resume may infer once from the same validated selection identity. |
| Before recovery append | Ledger rejection | Zero waits, retries or subsequent effects. |
| After `EffectStarted`, before result | Process crash | Occurrence stays unknown until reconciliation; no blind replay/refund. |
| After effect settlement | Duplicate resume | Settled descriptor is not executed again. |
| During pending poll | Deadline expires | Explicit stop/recovery failure under the original reservation. |
| During reconstruction | Subject/policy/reducer mismatch | Fail closed before prompt compilation. |

#### T-77 provider-neutral cache and context procedure

T-77 changes selection and presentation; it does not add a cache authority. The provider adapter remains responsible for serialization and supported cache controls through T-105.

```python
def compile_cached_packet(view, policy, codec):
    prefix = freeze_l1_l3(
        system=view.system,
        capability_cards=view.capability_cards,
        ordered_tools=view.ordered_tools,
        environment=view.environment_contract,
    )
    assert len(prefix.capability_cards) <= 4096

    mandatory = render_critical_state(view.task_state)
    interactions = correlate_complete_tool_interactions(view.interactions)
    evidence = bound_bodies_and_create_artifact_receipts(view.evidence, policy)
    tail = render_complete_goal_echo(view.objective, view.constraints)

    candidate = assemble(prefix, mandatory, evidence, interactions, tail)
    while codec.count_final(candidate) > policy.low_target:
        if remove_stale_evidence(candidate):
            continue
        if elide_lowest_priority_body(candidate):
            continue
        if drop_lowest_priority_evidence(candidate):
            continue
        if drop_oldest_complete_interaction_except_newest(candidate):
            continue
        break

    request = codec.serialize_final(candidate)
    if codec.count_serialized(request) > policy.usable:
        raise ContextBudgetExceeded
    return request, selection_identity(candidate, request)
```

Compaction starts above the configured high watermark and targets the low watermark. Mandatory state may finish above low, but never above usable. Each omission has a stable item key and one NT-C04 reason. Successful verification is represented by command, environment, subject, collected/executed counts, exit status, freshness and output artifact even when its raw body is evicted. The newest interaction includes both action and result; never retain an orphan tool result or tool call.

Cache controls are applied only after route capability negotiation. Unsupported routes retain the original serialized messages. Cache observation distinguishes `0` from missing: zero means the provider reported no cached tokens; null means it did not report the metric. Admission always reserves worst-case uncached input.

#### T-110 deterministic 100-turn qualification fixture

Build one test fixture, not a parallel runtime. It uses a deterministic fake clock, scripted model, isolated durable event store and the production composition/session path. Its test-only budget must permit at least 100 turns while assertions prove the shipped preset files and declared ceilings are byte-identical before and after.

Recommended schedule:

| Turn range | Stimulus | Required assertion |
|---|---|---|
| 1-20 | Normal observations and effects | Objective, constraints, plan, next action and budgets accumulate monotonically. |
| 21-35 | Oversized tool/test bodies | Bodies become artifact receipts; newest complete interaction survives. |
| 36-45 | Stale evidence and misleading tool text | Stale evidence omitted; untrusted text cannot replace goal or expand grants. |
| 46 | Fresh-process restart | Reconstructed semantic vector equals uninterrupted control. |
| 47-65 | Repeated failures and two/three cycles | One reground, one replan, then bounded stop unless verified progress changes. |
| 66-75 | Pending operation and transient retry | One operation identity, persisted delay/deadline and original reservation. |
| 76 | Crash between intent and settlement | Unknown occurrence reconciled without duplicate execution. |
| 77-95 | Multiple compaction epochs | Prefix remains stable within epoch; behavior change requires a new epoch. |
| 96 | Second fresh-process restart | Counters, settlements, budgets, deadline and latest verification match control. |
| 97-100+ | Stale finish then fresh verification | Stale finish rejected; fresh applicable verification permits only its truthful disposition. |

Run the uninterrupted and resumed variants from the same scripted inputs. Canonically encode and compare the NT-1.7 semantic vector after each restart and at termination. Failure output names the first divergent field and the event prefix that produced it. Assert unique settled descriptors and model/effect call counts so state equality cannot hide duplicated work.

#### T-111 reconciliation and control handoff

T-111 performs no feature development. Freeze executable changes first, then run the preregistration/frozen-canary falsifiers and the entire T-109 recipe on the integrated clean candidate. Any changed prompt, tool schema, model route, serializer/counter, context policy, recovery policy, preset, lockfile, event schema or fixture corpus invalidates the earlier compatible receipt.

Review the five execution files as a single projection:

1. `spec.md` contains normative contracts and forbidden behavior, without status prose.
2. `technical.md` contains implementation algorithms, operational recipes and fault injection.
3. `tasks.md` contains checkboxes, exact dependencies, ownership and accepted receipts.
4. `backlog.md` contains package lifecycle, without becoming another task queue.
5. `milestones.md` contains stable outcomes and accepted/open dispositions, without implementation detail.

Regenerate knowledge through `just docs-knowledge`; never hand-edit generated output. Run `lda index --delta`, `lda drift --json`, `just docs-check`, `just check` and `just verify`. Zero stale paths are required for touched code/docs; broad pre-existing orphan/undocumented inventory is reported separately and cannot be silently called zero drift.

The accepted handoff records a clean candidate SHA and leaves T-26 `UNFROZEN`. Starting MS-CONTROL means auditing and completing applicable T-79/T-89/T-92-T-95 plus T-51/T-52, then creating the T-26 freeze and running T-27. It does not mean MS-CONTROL is closed, a paid run is authorized, or post-control T-80/T-96/CAS/specialist work may start.

### Near-term review and failure-routing rules

| Finding | Owning stream | Required action |
|---|---|---|
| Full discovery, dependency, runner or nonmutation failure | C, then source owner | Preserve receipt; classify exact failure; repair candidate; rerun complete gate. |
| Provider serialization/count/cache observation defect | A | Fix adapter/codec and adversarial serialization tests; preserve B compiler ownership. |
| Context selection, compaction or goal-echo defect | B | Fix existing compiler/compaction path; do not add a second compiler. |
| Recovery decision/cycle detection defect | B | Fix pure recovery/episode policy; preserve bounded action set. |
| Runtime event ordering, replay or checkpoint defect | A | Fix session/fold/checkpoint/emitter integration; keep one writer/store. |
| Event schema/catalog coverage defect | C inputs, A consumers | Register via generator inputs, regenerate and rerun event coverage. |
| Long-session fixture exposes product defect | Owning A/B source stream | Fix production path; the fixture remains a falsifier and is not weakened. |
| Documentation status contradicts receipts | C | Keep milestone open; reconcile all five files before handoff. |

Stop and return the task to review when a proposed change adds kernel LOC, a second compiler/retry loop/store, runtime subprocess execution, automatic authority expansion, an unregistered event, a silent skip, relaxed collection floor, larger public preset budget, inferred cache metric or a focused-test waiver. Those changes exceed NT-1 or violate its acceptance boundary.

**FACT STORE path:** `adapters/stores/event_store.py`.
**I-STATE.** Lock `66aa7a3c`: `domain/task_state.py` MISSING. Branch: LIVE `8637db55` (`SemanticTaskState`; fold in `runtime/task_state.py`). MS-RESUME `CLOSED`.
**MS-INSTRUMENT CLOSED** at `63b77116`.
**MS-RESUME CLOSED** at `8637db55`.
**T-14 WorkspaceEpoch LIVE** `587db91a`. **T-16/T-15/T-36/T-37/T-45 LIVE** (`33dc7c33`, `2a4cdaad`, `179f5616`, `81b7b572`, `c7995195`). **T-17 adapter 2PC LIVE** `5c9870f0`.
**T-04 / `ADMISSION_GATE_EXEMPT`:** the production exemption is removed. Do not weaken the gate to satisfy legacy bare-finish fixtures; retarget those fixtures as a separate successor.

## Post-control reference handbook (FH-1) [PROPOSAL]

The normative owner is [spec FH-1](spec.md#fh-1-post-control-backend-horizon-proposal); [tasks](tasks.md#context-post-control-horizon-fh-1-proposal) owns dependencies and prototype leaves. These algorithms refine [Part 3 §§5–6](../reports/reviews/aether_v093_review/part3_blueprints_and_interface_contracts.md). They are conditional reference algorithms, not executed production code. NT-1 compile/recover remains the near-term contract. The references' in-memory tests do not qualify disk durability or aggregate resource accounting.

**Clause binding.** Each algorithm below implements named spec clauses and is read against them, not instead of them: `prepare_and_promote` implements FH-C05–FH-C10, `export` implements FH-C11, `delegate`/`settle`/`reconcile_delegation` implement FH-D04–FH-D07, and `run_campaign`/`acquire_node_lease`/`replan` implement FH-D08–FH-D12. Every failure return names a code from the FH-1.8 matrix. Where an algorithm here and a spec clause could be read to differ, the spec clause governs and this handbook is wrong. Step numbering is a reading aid for review and for the Wave 4 task board; it is not an API.

### Placement and compatibility decisions

Reuse `domain` canonicalization/artifact values for tree/edit/check/delegation payloads; `ports/environment.py`, blob/event/evaluator ports and `ports/child_runtime.py` for effect seams; `adapters/environment/transaction.py` and `git.py` for capture/staging/export; existing stores for persistence; `runtime/ledger_emitter.py` and registered reducers for admission/projection; `runtime/delegation.py` and agency spawn for child lineage; code-pack planner/completion for domain phases. Benchmark scheduling/reporting belongs in `benchmarks/` and executable runners in `tools/`. Runtime never imports subprocess. The kernel remains unchanged.

Trace the selected product manifest through bindings before retiring any patch frontend or planner. `DriveUntilGreenPlanner` and `AstPatchToolkit` demonstration paths do not establish which implementation runs in a given product profile. T-103 hardens current editing; CAS adds a new qualified workspace profile with an explicit migration boundary. Convert supported frontends to a common edit set; reject unsupported syntax rather than invoking fuzzy fallbacks. Reference `SnapshotBlobs`, `CandidateVerifier`, `PromotionLedger` and `SpawnGateway` are responsibility labels to map onto existing contracts, not four automatic new public ports.

### Immutable trees and serializable promotion

Let `H` be SHA-256 over canonical bytes and `J` the existing JCS encoder. A file node is `(path, file, mode, H(bytes))`; a directory is `(path, directory, mode, null)`. Define `tree_id = H(J(sorted(nodes, key=path)))`. Including parents, empty directories and modes makes absence and executable changes observable. Manifest ordering is deterministic; physical filesystem case collisions are rejected at capture/materialization. Check blobs on read and bound entries/total bytes before allocation. Capture must detect concurrent changes, not hash a mixed-time tree.

The active branch is `(tree_id, generation) = fold(commit_events)`. Each successful compare-and-append increases generation, including rollback to an earlier tree. This prevents an old transaction from matching an A->B->A cycle. Linearization occurs at the durable commit event, not at candidate file writes. A pinned reader observes one immutable tree. Ordinary checkout export is intentionally weaker and has a distinct receipt.

```text
prepare_and_promote(request) -> Result[PromotionReceipt]

  # ---- Phase 0: identity (pure; domain/cas/promotion.py; no effect) --------
  0.1  value <- decode(request) as aether.promotion/1
         unknown or unsupported schema version      -> fail SCHEMA_UNSUPPORTED
  0.2  identity <- H(JCS(value without "receipts"))            # FH-C08, I(P)
  0.3  txn      <- value.transaction_id
  0.4  reject non-digest fields, negative generation, empty branch
         -> fail INVALID_REQUEST   # the existing PortFailure kind, not a new one

  # ---- Phase 1: idempotent replay (read-only fold; runtime) ---------------
  1.1  prior <- promotion_index.lookup(txn)     # projection of commit facts
  1.2  if prior is not NONE:
         if prior.identity != identity          -> fail TRANSACTION_IDENTITY_MISMATCH
         return prior.receipt                   # original generation; NO mutation
       # Replay is answered before any blob is read. A committed transaction
       # is never re-executed, even if the branch has advanced since.

  # ---- Phase 2: authority and baseline (runtime; no mutation yet) ---------
  2.1  grant <- verify_grant(value.grant, now)
         expired / revoked / wrong subject       -> fail DELEGATION_DENIED
  2.2  (head, generation) <- branch_head(value.branch)   # fold of mhf.event/2
  2.3  if value.expected_head != head           -> fail PROMOTION_CONFLICT
  2.4  if value.expected_generation != generation -> fail GENERATION_STALE
       # 2.3 and 2.4 are advisory here and authoritative in Phase 6. Checking
       # early saves the candidate build; checking ONLY here would be the
       # classic TOCTOU, which is why Phase 6 repeats both under the lock.

  # ---- Phase 3: candidate construction (domain + blob adapter) -----------
  3.1  baseline <- load_tree(value.expected_head)
         missing / corrupt blob                  -> fail BLOB_MISSING | BLOB_CORRUPT
  3.2  edits <- decode(value.edit_set) as aether.edit-set/1
  3.3  for each (p, x, r) in edits:                          # FH-C07, total
         if D(nu_baseline(p)) != x               -> fail PATCH_PREIMAGE_MISMATCH
       # Evaluated over ALL edits before any write. One mismatch rejects the
       # whole set; no partial application exists at any observable point.
  3.4  candidate <- baseline (+) edits
  3.5  assert admissible(candidate)  per FH-C06 P1-P7
                                     -> fail EDIT_SET_INCONSISTENT | TREE_*
  3.6  syntax_check(candidate) in packs/adapters, never in domain
                                                 -> fail SYNTAX_REJECTED
  3.7  tree_id <- H_tree(candidate)                          # FH-C05

  # ---- Phase 4: durable candidate (adapters/stores/blob_store.py) -------
  4.1  pin(operation_id, tree_id)          # pin-before-write; FH-C10 ordering
  4.2  for each new blob b in candidate: blob_store.put(b)
  4.3  fsync files, then fsync containing directories       # rename durability
  4.4  persist candidate manifest; verify read-back digest == tree_id
                                                 -> fail BLOB_CORRUPT
       # FAULT INJECTION POINT F1: kill between 4.2 and 4.4.
       # Recovery: pin survives, blobs are orphaned-but-pinned, no head moved.

  # ---- Phase 5: verification (adapters/tools; N-06 keeps this out of runtime)
  5.1  plan <- decode(value.check_plan) as aether.check-plan/1
  5.2  reserve verification + publication + recovery envelopes  # FH-D04
         insufficient                            -> fail ENVELOPE_OVERCOMMIT
  5.3  for each check c in plan.checks:
         receipt <- verifier.run(c, candidate)   # immutable source mount
         persist receipt durably before use
  5.4  if not promotable(candidate, plan, receipts)          # FH-C09
         -> fail CHECK_INCOMPLETE | VERIFIER_UNTRUSTED | VERIFICATION_STALE
       # FAULT INJECTION POINT F2: kill between 5.3 and 5.4.
       # Recovery: receipts are durable and candidate-bound; re-entry re-reads
       # them rather than re-running, and a receipt bound to another tree_id
       # is VERIFICATION_STALE rather than reusable.

  # ---- Phase 6: commit (single-writer critical section; runtime) ---------
  6.1  return commit_critical_section(txn, identity, value, tree_id, receipts)
```

The commit is one serialized section owned by the existing emitter. Nothing inside it performs I/O that can block indefinitely; every expensive step already happened in Phases 3-5.

```text
commit_critical_section(txn, identity, value, tree_id, receipts)
  # Entered under the SAME single-writer boundary that serializes mhf.event/2
  # appends. There is no second lock and no second head.

  6.1  prior <- promotion_index.lookup(txn)          # re-read inside the lock
       if prior is not NONE:
         if prior.identity != identity -> return TRANSACTION_IDENTITY_MISMATCH
         return prior.receipt                        # lost-reply winner
  6.2  (head, generation) <- branch_head(value.branch)
  6.3  if value.expected_head       != head        -> return PROMOTION_CONFLICT
  6.4  if value.expected_generation != generation  -> return GENERATION_STALE
  6.5  re-verify grant validity at commit time     -> return DELEGATION_DENIED
  6.6  re-verify blob presence for tree_id         -> return BLOB_MISSING
  6.7  re-verify promotable(...) against receipts  -> return CHECK_INCOMPLETE
  6.8  append CasPromoted fact:
         {txn, identity, branch, head_before: head, head_after: tree_id,
          generation_after: generation + 1, check_plan, receipts}
  6.9  update the head projection in the SAME storage transaction as 6.8
       # If projection and log can diverge, the projection is rebuilt from the
       # log on read and is never an independent authority (FH-C02).
  6.10 release the operation pin; retain the candidate pin as the live head
  6.11 return receipt{txn, head_after: tree_id, generation_after: generation+1}
       # FAULT INJECTION POINT F3: kill between 6.8 and 6.11 (reply lost).
       # Recovery: reconcile_unknown_commit below.
```

**Why every loser mutates nothing.** Steps 6.2-6.7 are re-evaluated inside the lock, so of `n` concurrent requests naming the same `(head, generation)`, exactly one reaches 6.8; the rest observe the advanced generation at 6.4 and return without having written anything since Phase 4 (which writes only content-addressed blobs, never a head).

**ABA immunity, operationally.** Generation is incremented at 6.8 on every commit including rollback, which is itself an ordinary forward promotion to a retained earlier tree. A request prepared at `(A, g)` that arrives after `A -> B -> A` observes `(A, g+2)` and fails at 6.4 with `GENERATION_STALE`, distinct from the `PROMOTION_CONFLICT` it would get from an ordinary race at 6.3. Callers use that distinction: `PROMOTION_CONFLICT` means rebase onto a different tree, `GENERATION_STALE` means the tree looks identical but history moved underneath and prior verification must still be re-run.

```text
reconcile_unknown_commit(txn, identity) -> Result[PromotionReceipt]
  # Runs when the commit reply was lost (F3), on retry or on restart.
  # It NEVER re-applies and NEVER refunds on a guess.
  R1  prior <- promotion_index.lookup(txn)       # authoritative fold, not cache
  R2  if prior is not NONE:
        if prior.identity != identity -> fail TRANSACTION_IDENTITY_MISMATCH
        return prior.receipt                     # it did commit; adopt it
  R3  if the log is readable and txn is absent:
        the commit did NOT occur -> safe to retry prepare_and_promote
  R4  if the log is unreadable or truncated:
        -> fail PROMOTION_UNKNOWN; hold reservations unsettled; do not retry
       # R4 is the honest branch. "Probably did not commit" is the assumption
       # that duplicates irreversible effects, so it is not available here.
```

The adapter's commit boundary must serialize competing appenders in a fresh-process test; a Python lock in one process is insufficient. Do not claim a new atomic event-store API exists before adapter qualification. Storage acknowledgement requires declared durability semantics, including directory synchronization where needed; fsync success is not a backup strategy. Fault-inject before/after blob persistence, verification receipt persistence, event commit and reply delivery. Orphan unpromoted blobs are collectible only after pending-operation pins expire under policy.

```text
export(candidate, destination, operation_id) -> Result[ExportDisposition]

  # Export publishes an immutable candidate onto a mutable host directory.
  # It is a SEPARATE disposition from promotion (FH-C11) and can fail
  # without invalidating a committed head.

  # ---- E0: ownership --------------------------------------------------
  E0.1  assert destination is a declared, owned export root
                                              -> fail EXPORT_UNOWNED
  E0.2  lock <- acquire_destination_lock(destination)
          held by another framework writer    -> fail EXPORT_CONFLICT
        # The lock binds framework writers only. An arbitrary external editor
        # is NOT excluded, which is exactly why E3.2 rechecks every path and
        # why no atomic host-checkout guarantee is offered.
  E0.3  baseline <- scan(destination)         # path -> (digest, mode, exists)
  E0.4  if baseline.identity != declared destination_baseline
                                              -> fail EXPORT_CONFLICT

  # ---- E1: plan and preimages (still no mutation) ----------------------
  E1.1  target  <- materialization_set(candidate)      # paths we will own
  E1.2  touched <- target UNION {p in baseline : p in candidate_scope}
  E1.3  preimages <- { p: (digest(p), mode(p), exists(p)) for p in touched }
        # Existence is recorded, not just content: restoring a file that the
        # export created means DELETING it, and that is only knowable from a
        # preimage that says "absent".
  E1.4  manifest <- H(JCS(preimages))

  # ---- E2: journal before effect ---------------------------------------
  E2.1  journal.write(operation_id, state=prepared,
                      candidate=H_tree(candidate),
                      destination_baseline=baseline.identity,
                      destination_identity=destination,
                      preimage_manifest=manifest,
                      completed_paths=[])
  E2.2  fsync journal file AND its directory
        # FAULT INJECTION POINT X1: kill after E2.2. Recovery finds `prepared`
        # with no completed paths and restores nothing, because nothing moved.

  # ---- E3: publish ------------------------------------------------------
  E3.1  journal.advance(operation_id, state=publishing)
  E3.2  for p in deterministic_order(target):
          observed <- scan_one(destination, p)
          if observed != preimages[p]:
            # Someone else wrote here between E1.3 and now.
            journal.advance(operation_id, state=restoring)
            return restore_or_quarantine(operation_id) with EXPORT_CONFLICT
          write_path(destination, p, candidate)     # temp file + atomic rename
          fsync file, then fsync parent directory
          journal.append_completed(operation_id, p)  # durable BEFORE next path
        # FAULT INJECTION POINT X2: kill inside the loop. `completed_paths` is
        # the resume cursor; recovery knows exactly which paths it owns.
  E3.3  for p in (touched \ target) where preimages[p].exists and p is deleted
            by the candidate: delete and record completed

  # ---- E4: verify and commit -------------------------------------------
  E4.1  final <- scan(destination restricted to touched)
  E4.2  if final != expected_postimage(candidate, touched)
          journal.advance(operation_id, state=restoring)
          return restore_or_quarantine(operation_id) with EXPORT_CONFLICT
  E4.3  journal.advance(operation_id, state=committed)
  E4.4  release lock; return EXPORTED{operation_id, paths=|target|}
```

```text
restore_or_quarantine(operation_id) -> ExportDisposition
  # Dirty-disk restoration. The rule is: restore ONLY what we wrote, and
  # never overwrite a third party's edit to prove our own cleanliness.

  J   <- journal.read(operation_id)
  for p in reverse(J.completed_paths):
    observed <- scan_one(J.destination, p)
    expected <- expected_postimage(J.candidate, p)   # what WE wrote
    pre      <- J.preimages[p]

    case observed == expected:                       # untouched since we wrote
        restore(p, pre)        # rewrite bytes+mode, or delete if pre.absent
    case observed == pre:                            # already back to preimage
        continue                                     # idempotent no-op
    case otherwise:                                  # externally modified
        record conflict(p); DO NOT WRITE
        # Restoring here would destroy someone else's work in the name of
        # cleanup. The honest outcome is quarantine, not a tidy directory.

  if conflicts is empty:
      verify each restored path against its preimage
        mismatch -> goto quarantine
      journal.advance(operation_id, state=restored)
      release lock
      return RESTORED{operation_id}                  # reports RECOVERY_FAILED=false

  quarantine:
      journal.advance(operation_id, state=quarantined,
                      conflicts=conflicts, evidence=scan_digests(conflicts))
      retain the lock marker and the journal; do NOT release for reuse
      return QUARANTINED{operation_id, conflicts}    # RECOVERY_FAILED
      # A quarantined destination is never silently reused. It requires an
      # operator decision under separate authority, and the framework reports
      # the export as failed while the promotion may still be committed.
```

```text
recover_export(operation_id)          # runs at startup, before new exports
  J <- journal.read(operation_id)
  switch J.state:
    prepared    -> nothing was written; discard journal; release lock
    publishing  -> restore_or_quarantine(operation_id)
    restoring   -> restore_or_quarantine(operation_id)     # idempotent re-entry
    committed   -> verify final state; already terminal; release lock
    restored    -> terminal; release lock
    quarantined -> terminal; stay quarantined; refuse new export to this root
  # Every branch is idempotent: running recover_export twice yields the same
  # state, because each case is driven by durable journal state plus observed
  # disk digests, never by in-memory progress.
```

**Separation of dispositions.** `export` returns `EXPORTED`, `RESTORED` or `QUARANTINED`. The promotion receipt from `prepare_and_promote` is unaffected by all three. A run that committed a head and quarantined its checkout reports both, truthfully, as a pair. Collapsing that pair into one status is the reporting defect FH-C11 exists to prevent.

A failure before branch promotion leaves the head unchanged. A post-promotion rollback uses a new expected-generation comparison. Export failure cannot erase a successful branch promotion. Mark/sweep retention roots include live heads, suspended branches, open transactions, accepted evidence and explicit user pins; use a consistent root snapshot or generation barrier so concurrent publication cannot race reclamation. Garbage collection remains grant-checked and bounded.

### Conserved delegation and durable campaigns

For each additive dimension `d`, require `spent_d + unsettled_d + sum(child_reserved_d) + recovery_reserved_d <= root_limit_d`; these are disjoint accounting categories, not double-counted costs. Use the existing governor/lease settlement path. Wall-clock deadlines and structural turn/depth ceilings are checked separately; parallel elapsed latency is not the sum of child runtimes. Unknown usage prevents claiming a fully measured cost and does not justify refunding a possibly spent reservation.

The five states of FH-D06 are not new machinery; they name durable points that
already exist in `runtime/delegation.py::SpawnAdapter.execute` plus the two
records DEL-01 adds. The mapping is exact:

| State | Today (`HEAD`) | DEL-01 delta |
|---|---|---|
| `RESERVED` | kernel `S7` `Governor.reserve` before the adapter runs | unchanged |
| `INTENT_RECORDED` | *absent* — `_already_settled(intent_key)` reads back only after `ChildSpawned` | durable intent record keyed by `call_id`, written before dispatch |
| `DISPATCHED` | `ChildSpawned` fact, emitted before `run_child` | unchanged |
| `RETURNED` | `ChildReturned` fact from `ChildRunResult` | adds bounded `aether.specialist-findings/1` validation |
| `SETTLED` | kernel `S11` commit/release against the parent lease | adds durable `aether.delegation-settlement/1` |

```text
delegate(parent, request) -> DelegationOutcome

  # ---- S->RESERVED ------------------------------------------------------
  D0.1  req <- decode(request) as aether.specialist-request/1
                                          -> deny SCHEMA_UNSUPPORTED
  D0.2  call_id <- req.call_id
        identity <- H(JCS({parent_lineage, call_id, canonical request}))
  D0.3  prior <- settlement_index.lookup(call_id)
        if prior is not NONE:
          if prior.identity != identity  -> deny TRANSACTION_IDENTITY_MISMATCH
          return prior.outcome           # idempotent; no second child
        # This is the existing `_already_settled` check, moved ahead of parse
        # so a retried spawn cannot re-run a subtree that already happened.
  D0.4  assert depth(child) = depth(parent) + 1 <= max_depth
                                          -> deny DELEGATION_DEPTH_EXCEEDED
  D0.5  granted <- attenuate(parent.scope, requested_scope)      # K-23/K-25
        not ok                            -> deny SCOPE_ESCALATION_DENIED
                                               (record requested AND grantable)
  D0.6  for d in {usd_micros, millis, tokens, bytes}:
          if req.budget[d] > remaining_d(parent) -> deny ENVELOPE_OVERCOMMIT
        lease <- Governor.reserve(run_id, Reservation(**req.budget),
                                  parent_lease_id=parent.lease_id)
        state := RESERVED
        # `remaining_d` is read through the existing callable, never a
        # snapshot: a sibling spawned three turns ago has already spent.

  # ---- RESERVED -> INTENT_RECORDED --------------------------------------
  D1.1  persist intent{call_id, identity, lease_id, reserved, granted scope,
                       deadline, parent_lineage, state: INTENT_RECORDED}
  D1.2  fsync before returning                           # durable-before-effect
        state := INTENT_RECORDED
        # FAULT INJECTION POINT D1: kill here. Recovery finds an intent with no
        # `ChildSpawned` and must PROVE non-dispatch (D-R2) before releasing.

  # ---- INTENT_RECORDED -> DISPATCHED ------------------------------------
  D2.1  plan <- ChildRunPlan(...)          # existing validated plan value
  D2.2  emit ChildSpawned(lineage)         # sole legal writer: SpawnAdapter
        state := DISPATCHED
  D2.3  result <- child_runtime.run_child(plan)
          raised exception -> result := ChildRunResult(outcome="undeterminable",
                                                       terminal="UNDETERMINABLE")
        # An exception does NOT mean nothing happened. The child may have
        # completed an irreversible effect before raising, so the occurrence is
        # UNDETERMINABLE, never DID_NOT_OCCUR (`F-22`).

  # ---- DISPATCHED -> RETURNED -------------------------------------------
  D3.1  assert isinstance(result, ChildRunResult)   # no handles, no transcripts
  D3.2  findings <- decode(result.result_digest) as aether.specialist-findings/1
        verify findings.request == identity
               findings.child_lineage == plan.child_episode_id
               findings.subject matches the parent's current subject
               every claim's evidence digest resolves
          any failure -> findings are DROPPED, not partially trusted;
                         the call still settles on observed cost
  D3.3  emit ChildReturned(result)
        state := RETURNED

  # ---- RETURNED -> SETTLED ----------------------------------------------
  D4.1  observed <- result.actual_cost        # may be partial; never negative
  D4.2  settled  <- settle(call_id, reserved, observed, outcome)   # below
  D4.3  persist aether.delegation-settlement/1{call_id, request: identity,
              state: SETTLED, reserved, observed, settled, deficit, reason}
  D4.4  kernel commits `settled` against the PARENT lease and releases the
        remainder (`S11`). There is exactly one accountant and it is not the
        adapter.
        state := SETTLED     # terminal, idempotent by call_id
  D4.5  findings are advisory input to a parent candidate only; they cannot
        satisfy a check plan or mark a campaign node PASSED (FH-D07).
```

```text
settle(call_id, reserved, observed, outcome) -> (settled, deficit, reason)
  case outcome == "completed" and observed is complete:
      settled := observed
      deficit := max(0, observed - reserved)      # overrun is recorded exactly
  case outcome in {"denied"} and dispatch provably never occurred:
      settled := 0                                 # the ONLY zero-settle case
  case outcome == "abandoned":
      settled := observed if observed is complete else reserved
  case outcome == "undeterminable" OR observed has any null dimension:
      settled := reserved                          # worst case, not zero
      reason  := "unknown_usage"
  # A timeout or an unknown outcome settles at RESERVED. Settling such a call
  # at zero asserts that no effect occurred, which the deadline never proved.
  if deficit > 0:
      charge deficit to recovery_d(parent) first; if exhausted,
      remaining_d(parent) < 0 and the parent is refused all further
      reservations (ENVELOPE_OVERCOMMIT). The overrun is never clamped.
```

```text
reconcile_delegation(call_id)        # startup and retry path
  I <- intent_store.lookup(call_id)
  D-R1  I absent, lease open      -> release lease; nothing was recorded
  D-R2  I.state == INTENT_RECORDED, no ChildSpawned in the log
                                  -> dispatch provably did not occur;
                                     settle 0 and release
  D-R3  I.state == INTENT_RECORDED, ChildSpawned present
                                  -> treat as DISPATCHED; go to D-R4
  D-R4  ChildSpawned present, no ChildReturned
                                  -> outcome UNKNOWN; keep the reservation
                                     HELD and UNSETTLED (CHILD_UNKNOWN);
                                     poll the child lineage; never refund
  D-R5  ChildReturned present, no settlement record
                                  -> replay D4.1-D4.4 (idempotent by call_id)
  D-R6  settlement record present -> terminal; a second settle attempt is
                                     refused as SETTLEMENT_UNRECONCILED
```

```text
cancel(parent, reason)
  C1  compute the descendant set from the canonical lineage chain, deepest first
  C2  for each descendant in that order:
        propagate a DEADLINE (not a kill): deliver deadline <- now
  C3  for each call in {DISPATCHED}:
        wait bounded; on expiry settle per `settle(...)` with outcome
        "undeterminable" -> settled := reserved
  C4  for each call in {RESERVED, INTENT_RECORDED} that satisfies D-R2:
        settle 0 and release
  C5  cancellation NEVER converts a descendant's settled spend back into
      available budget. The envelope shrinks monotonically; a cancel that
      replenished the allowance would make cancel-and-retry a budget exploit.
```

**Advisory read-only isolation.** The child receives an attenuated `Grant`, never the parent's `HmacAuthenticator` key or a live session handle — `ChildRunResult.__post_init__` already enforces the scalar-only contract that makes a leaked handle a construction error rather than a downstream surprise. The parent remains the sole writer of `ChildSpawned`/`ChildReturned` (`PRIVILEGED_KIND_OWNERS`), so a specialist has no path to append a fact of its own.

If reservation and intent cannot share one storage transaction, define a recoverable admission state machine: `reserved -> intent_recorded -> dispatched -> returned -> settled`. Each transition is idempotent; restart repairs an incomplete transition before dispatch. A reservation without recorded intent may be released only after proving dispatch never occurred. Cancellation propagates through the canonical lineage and reconciles outstanding effects. Do not construct a second governor or refund on arbitrary exceptions.

Campaign readiness is `ready(v) iff every dependency u has an accepted artifact matching v's required interface/version`. A terminal child without that evidence is not ready. The director records a bounded plan revision and uses the current runtime client; each worker has an explicit lease, task, artifact inputs and budget. On restart reconcile leased/running nodes before selecting ready nodes. Merging independent candidates produces a new tree whose whole check plan must run. A read-only specialist treatment and a parallel-mutating treatment are different experiments. Basic DAG fixtures may qualify mechanics without positive specialist lift; full Octopus and recursive tournament treatments remain behind M-OCT.

### Campaign execution and worker coordination (OCT-03)

The director is a runtime **client**. It owns no `EpisodeEngine`, no `Governor`
and no scheduler accounting of its own: every node is executed by dispatching
through the canonical delegation path, so exactly one engine exists per running
node, inside that node's own child lineage. The structural falsifier is direct —
`grep` the campaign client for an `EpisodeEngine` construction or a mutating
verb and the count must be zero (FH-D11).

```text
run_campaign(plan, director_identity) -> CampaignDisposition

  # ---- C0: plan admission (pure; domain) --------------------------------
  C0.1  G <- decode(plan) as aether.campaign-plan/1
                                        -> fail SCHEMA_UNSUPPORTED
  C0.2  assert every u in deps(v) is a node of G  -> fail CAMPAIGN_PLAN_INVALID
  C0.3  order <- kahn_topological_sort(G)
          returns fewer than |V| nodes  -> fail CAMPAIGN_PLAN_INVALID (cycle)
        # Acyclicity is proven once, at admission. A partially dispatched
        # cyclic plan is never observable.
  C0.4  assert budget(G) <= campaign envelope; grants(G) subset of director grant

  # ---- C1: restart reconciliation BEFORE any new dispatch ---------------
  C1.1  for v in V where lease(v).state == ACTIVE:
          reconcile_delegation(lease(v).operation_id)      # D-R1..D-R6
          # A node whose child outcome is unknown keeps its reservation and
          # stays RUNNING. It is NOT re-dispatched: that is how "resume at
          # K+1 with no duplicate effects" is actually achieved.
  C1.2  recompute dispositions as a fold of campaign facts, never from memory
  C1.3  propagate_blocked(G)                                # C4 below

  # ---- C2: traversal ----------------------------------------------------
  C2.1  while exists v with ready(v) or disposition(v) == RUNNING:
  C2.2    R <- { v : ready(v) }                             # FH-D09
            # ready(v) requires every u in deps(v) to be PASSED *and* to have a
            # schema-valid accepted artifact. Terminality alone is not enough.
  C2.3    if R is empty and nothing is RUNNING: break       # quiescent
  C2.4    for v in R (bounded by the declared parallelism ceiling):
              lease <- acquire_node_lease(v, director_identity)
              if lease is NONE: continue                    # another holder won
              inputs <- { u: artifact_digest(u) for u in deps(v) }
              dispatch_node(v, lease, inputs)
  C2.5    await at least one node transition; then loop

  # ---- C3: node completion ----------------------------------------------
  C3.1  on RETURNED(v, result):
          artifact <- resolve(result.result_digest)
          if not validates(artifact, output_schema(v)):
              record disposition(v) := FAILED, reason ARTIFACT_SCHEMA_INVALID
          else if not accepted_by_exterior_verification(artifact):
              record disposition(v) := FAILED, reason CHECK_INCOMPLETE
          else:
              record disposition(v) := PASSED, artifact(v) := artifact
          release lease(v) by appending its terminal state
        # Acceptance is the exterior verdict. A child's self-report, a role
        # vote and a tournament score are all inadmissible here.

  # ---- C4: monotone failure closure -------------------------------------
  C4.1  propagate_blocked(G):
          frontier <- { u : disposition(u) in {FAILED, BLOCKED, UNDETERMINABLE} }
          for w in reachable_from(frontier):
              if disposition(w) in {PENDING}:
                  disposition(w) := BLOCKED            # persisted, not inferred
        # Once BLOCKED, w is never ready under this plan version. A failed
        # dependency cannot be re-argued into readiness.

  # ---- C5: termination ---------------------------------------------------
  C5.1  every node holds a terminal disposition, or the envelope is exhausted
  C5.2  emit CampaignSettled{per-node dispositions, artifacts, replans, spend}
  C5.3  a campaign with any BLOCKED/FAILED/UNDETERMINABLE node reports exactly
        that. It never reports completion.
```

```text
acquire_node_lease(v, holder) -> Lease | NONE
  # Exclusivity comes from compare-and-append inside the SAME single-writer
  # boundary that serializes every other mhf.event/2 append. There is no
  # second lock service and no second ledger.
  L1  (current_token, current_state) <- lease_projection(v)
  L2  if current_state == ACTIVE and not expired(current_lease):
        return NONE                                  # NODE_LEASE_CONFLICT
  L3  next_token <- current_token + 1                # strictly increasing
  L4  append aether.campaign-lease/1{campaign_id, node_id: v,
            attempt: current_attempt + 1, fence_token: next_token,
            holder_identity: holder, state: ACTIVE, deadline, operation_id}
        compare-and-append fails (someone else advanced the token) -> return NONE
  L5  return the lease
  # FENCING: every later append for node v carries `fence_token` and is
  # refused unless it equals the node's current token. A director that was
  # partitioned, resumed elsewhere, or simply slow therefore CANNOT write a
  # disposition for a node that has been re-leased -- regardless of what it
  # believes about its own liveness. Expiry alone settles nothing; the child's
  # outcome is still reconciled by `operation_id` through D-R1..D-R6.
```

```text
dispatch_node(v, lease, inputs)
  N1  reserve the node envelope from the campaign envelope (FH-D04)
        insufficient -> disposition(v) := BLOCKED, reason ENVELOPE_OVERCOMMIT
  N2  build an aether.specialist-request/1 (or an ordinary task request) whose
      scope is attenuated from the director's grant and whose inputs are the
      dependency artifact DIGESTS -- never inline content
  N3  delegate(director, request)        # the SAME path as FH-D06; one engine
                                         # is constructed inside the child
  N4  disposition(v) := RUNNING; the lease's operation_id is the reconciliation
      key for C1.1
  # The director never calls an environment adapter, never opens a workspace
  # and never applies a patch. Edits happen only inside qualified child
  # episodes, through the existing execution path.
```

```text
replan(G, G_prime) -> Result[Plan]
  P1  assert objective_digest(G_prime) == objective_digest(G)
  P2  assert grants(G_prime) subset of grants(G)
  P3  assert budget_d(G_prime) <= budget_d(G) for every additive d
  P4  assert { v : disposition(v) == PASSED } and their artifacts are carried
      over byte-identically
  P5  assert replans(G) + 1 <= replan_allowance   -> fail REPLAN_EXHAUSTED
  P1-P3 violated                                   -> fail SCOPE_ESCALATION_DENIED
  P6  append the plan revision as a fact; the old plan version is retained
  # Replanning is how a campaign adapts. Silently enlarging the objective,
  # the authority or the budget is how a campaign escapes its authorization,
  # so each is a separate refusal with its own code.
```

**Merge is a candidate, not a vote.** Integrating independent node artifacts produces a NEW candidate tree whose complete check plan must run (FH-D02). Passing children, role agreement and tournament ranking are inputs to *which* candidate is built, never evidence that the combined tree is correct.

Memory promotion reuses the existing governed learning path: capture candidate lesson with subject/version/evidence, evaluate on a segregated development holdout, admit through a distinct promoter, and record supersession/rollback. Revocation invalidates materialized retrieval caches as well as future queries. Official evaluation holdouts never become training or adaptive selection data within that study.

### Measurement model and reference evaluation procedure

Freeze the evaluated system, not only the model name. Let `N` be the frozen eligible instance count, `R` verified resolutions, `U` undeterminable attempts and `C` total observed cost across all attempts. Report `R/N` with a Wilson interval; also report all disposition counts and the descriptive missingness bounds `[R/N, (R+U)/N]`. Those bounds are not a confidence interval. `C/R` is undefined when `R=0`; if cost is missing, report a known subtotal and missing count rather than a complete cost estimate. Infrastructure/dataset anomalies remain in the scheduling inventory; separately declared official denominators are reproduced exactly, with a reconciliation table.

For paired arms use `delta = mean(y_treatment - y_control)` on identical task IDs. Predeclare a repository-clustered bootstrap for uncertainty where tasks share repositories, trial handling for stochastic outputs, and multiplicity correction for several treatments. McNemar's discordant-pair analysis may supplement binary outcomes; it does not resolve missingness or repository dependence. Freeze sample size, useful effect `delta_min`, cost/latency ceilings and stopping policy after control measurements and before treatment evaluation. Default decision confidence is 95%; thresholds are study fields, not invented universal scores.

Promote a treatment only if the predeclared useful-lift predicate (`lower_bound(delta) > delta_min`) or a predeclared cost-saving/noninferiority alternative holds, mandatory invariants pass, and missingness rules permit inference. Choose the alternative before observing results. Zero observed false completion also needs its sample count and uncertainty; it is not proof of zero population risk. Do not repeatedly inspect ordinary confidence intervals and stop when positive; use fixed sampling or a preregistered sequential method.

```text
evaluate_frozen(manifest):
  validate all frozen identities, authorized budget and evaluator isolation
  for each scheduled instance/attempt:
    materialize pinned baseline; execute selected runtime arm
    seal prediction/patch artifact even when empty or invalid
    evaluate independently with a unique subject-bound run identity
    persist raw outputs and one canonical attempt disposition
  reconcile expected IDs with all received/missing outputs
  compute only declared per-corpus metrics and uncertainty
  produce evidence bundle; independent reviewer issues a disposition
```

Pin SWE-bench code/dataset/environment and export `instance_id`, `model_name_or_path`, `model_patch` predictions to its upstream evaluator. Its result cache uses run/instance identity, so changed predictions need a new run ID. Preserve raw reports and distinguish harness execution from resolution. See the [official evaluation guide](https://www.swebench.com/SWE-bench/guides/evaluation/) (checked 2026-09-07; revalidate at implementation freeze).

Pin Aider's polyglot corpus, runner and attempt/feedback protocol separately; report first-attempt and feedback-assisted results independently and identify the AETHER harness substitution. The [Aider benchmark documentation](https://aider.chat/docs/benchmarks.html) and [leaderboard methodology](https://aider.chat/docs/leaderboards/) are protocol sources, not evidence that this backend has achieved their scores (checked 2026-09-07). Do not hard-code leaderboard leaders into acceptance. For greenfield, freeze requirements, negative checks, clean-start/build conditions and evaluator independence; assess completeness/reproducibility separately from repository repair.

Official protocol reproduction, public submission and a SOTA claim have distinct receipts. Public submission requires its existing release/operator authority. Select comparator eligibility and a dated comparison snapshot before running the study; incomparable harness/resource settings forbid a direct superiority claim. Negative or inconclusive results close the reporting task while leaving the performance gate open. Release qualification still requires M-8/M-9/M-10 and complete preservation recipes on the final subject.

### T-129 preparation: owner decisions (2026-09-12; NOT admission)

Source inspected at `001911e3` with the working execution-doc delta. These are
placement decisions for a candidate implementation, not accepted new contracts,
working APIs or permission to execute. T-129 remains BLOCKED on accepted T-27.
Do not move the existing `runtime/memory.py` or `benchmarks/protocols.py`: although
a same-stem directory can coexist on disk, it risks ambiguous/shadowed Python
imports and would impose an unnecessary compatibility migration.

| Package | Reuse / extend existing owner | Selected new placement and boundary |
|---|---|---|
| CAS-01 | `ports/blob_store.py::BlobStorePort` and `adapters/stores/blob_store.py::FileBlobStore`; existing ledger/store/session owners below | `domain/cas/{tree,edit_set,promotion}.py`, `runtime/cas/{promote,commit}.py`, `adapters/cas/{workspace,export,retention}.py`. No second blob port/store and no second ledger. Existing environment transaction support is not durable workspace CAS; retain its public behavior. |
| DEL-01 | `runtime/delegation.py::SpawnAdapter`, its construction in `runtime/wiring.py`, and existing child execution; no second spawn adapter | `domain/delegation/{specialist,settlement}.py`; `runtime/delegation_recovery.py` is a helper called by the existing lifecycle, never another execution loop. Preserve existing child event folding in `domain/ledger/reducer.py`. |
| OCT-03 | Existing runtime application composition and episode dispatch; no direct construction of another EpisodeEngine | `domain/campaign/plan.py`, `runtime/campaign/director.py`. Director implementation requires qualified CAS and accepted delegation fault tests (T-118c), not merely recovery code. |
| MEM-01 | `ports/memory.py` authorization/provenance contracts; `adapters/stores/memory_engine.py` durable storage; `runtime/skill_index.py` static discovery and `runtime/governance/learning.py` durable promotion registry retain distinct responsibilities | `domain/memory/lesson.py`, `runtime/memory_admission.py`, `benchmarks/studies/memory_lift.py`. Admission composes existing authorization, not a replacement memory engine, skill catalog or promotion registry. Public wiring remains an admission obligation, not something proved by existing doubles. |
| EVAL-02 | `benchmarks/protocols.py::{EvaluatorAdapter,BenchmarkSubmission,BenchmarkReceipt}`, existing statistics and evaluator infrastructure | `benchmarks/evaluation_protocols/{evaluator_boundary,swebench_verified,aider_polyglot,greenfield_corpus}.py`; `domain/evaluation/manifest.py` contains only pure shared values, with no import from benchmarks. Retain protocol imports and receipt identity; no second evaluator authority. Studies remain in `benchmarks/studies/`; official/reporting orchestration remains in `benchmarks/ladder/`. |

All listed new package roots were absent on inspection (including same-stem
`.py` checks). This establishes placement, not package qualification. Candidate
verifier orchestration may live in `adapters/verification/runner.py`, but must
consume existing `adapters/evaluators/{client,gate,signing}.py` authority and
isolation rather than mint a competing signer or run processes in runtime.

**CAS gaps become explicit leaves.** T-114e owns schema-backed event registration,
generated wire types, writer-role authorization in `runtime/ledger_emitter.py`,
and workspace/generation/transaction projections in `domain/ledger/{state,reducer}.py`.
The event vocabulary in `domain/ledger/events.py` is derived from generated
types: adding a string to the emitter is not registration. Allocate new events
only through existing governance; preserve historical readers and golden vectors.
T-114f extends `ports/event_store.py` and both stores in
`adapters/stores/event_store.py` through the existing emitter. SQLite's present
`append()` uses `BEGIN IMMEDIATE`, but exposes no workspace expected-generation
predicate. Require the comparison, transaction-identity check and append to share
one durable atomic boundary; an in-process lock or caller-side precheck cannot
prove this. Exact signatures and migration version require post-gate contract
review; these are missing obligations, not APIs claimed to exist.

T-116d wires the selected coordinator through `runtime/{session,compose,wiring}.py`,
including restart/replay and export recovery; T-116c tests that real product path.
T-113a hardens FileBlobStore instead of duplicating it: current `get()` does not
rehash, `put()` trusts an existing path, temporary names are shared per target,
and directory-fsync errors are swallowed. Durable CAS needs explicit corruption,
concurrent-put and durability-failure tests, while retaining existing callers'
compatibility. Pin/GC policy belongs in `adapters/cas/retention.py`, not the port.

**Dependency disposition.** T-114b requires T-114d and T-114e; T-114c additionally
requires T-114f; T-116c additionally requires T-116d; T-120b requires T-118c.
Memory lift T-121c consumes evaluator boundary T-122b, not just manifest values.
Greenfield T-125a depends on T-122b independently of Verified/Aider; official
reconciliation T-126a joins T-123a, T-124a and T-125a explicitly. Shared emitter,
schema and composition leases are serialized, not assumed disjoint. The board's
`requires:` edges remain the operational authority after package admission.

### Algorithm-to-file map and fault-injection index (feeds Wave 4)

Proposed placement for review only. No row grants a lease or establishes a new
module/API. The preparation decisions above supersede earlier path placeholders;
T-129 must still admit the selected package before any row is executable.

| Algorithm | Owning file (new unless noted) | Layer rule |
|---|---|---|
| `H_tree`, `ent`, `order`, admissibility P1–P7 | `vanguard/packages/domain/cas/tree.py` | pure; no `os`, no `pathlib`, no clock |
| `nu_A`, `D`, `admissible`, `(+)` | `vanguard/packages/domain/cas/edit_set.py` | pure; rejects, never repairs |
| promotion value, `I(P)`, generation algebra | `vanguard/packages/domain/cas/promotion.py` | pure value + predicates |
| `prepare_and_promote` Phases 0–5 | `vanguard/packages/runtime/cas/promote.py` | composes; **no `import subprocess`** (N-06) |
| `commit_critical_section`, `reconcile_unknown_commit` | `vanguard/packages/runtime/cas/commit.py` | inside the existing emitter boundary |
| blob persistence and fsync | extend `vanguard/packages/adapters/stores/blob_store.py` | reuse `ports/blob_store.py::BlobStorePort`; pin/sweep belongs in `adapters/cas/retention.py` |
| capture / materialization | `vanguard/packages/adapters/cas/workspace.py` | the only filesystem reader for CAS |
| `export`, `restore_or_quarantine`, `recover_export` | `vanguard/packages/adapters/cas/export.py` | journal is adapter-owned; intent is runtime-owned |
| check execution | `vanguard/packages/adapters/verification/runner.py` or `tools/` | the only place a process is spawned |
| `delegate` D0–D4, `settle`, `reconcile_delegation`, `cancel` | extend `vanguard/packages/runtime/delegation.py` | extend `SpawnAdapter`; do not fork a second adapter |
| `aether.delegation-settlement/1` value | `vanguard/packages/domain/delegation/settlement.py` | pure; parent is sole writer |
| `run_campaign`, `acquire_node_lease`, `dispatch_node`, `replan` | `vanguard/packages/runtime/campaign/director.py` | runtime client; zero mutating verbs (FH-D11) |
| `aether.campaign-plan/1`, `aether.campaign-lease/1` values | `vanguard/packages/domain/campaign/plan.py` | pure; Kahn sort lives here |
| lesson values, revocation root `R_e` | `vanguard/packages/domain/memory/lesson.py` | pure; admission predicate is a function |

Kernel delta stays zero against the 1438 ceiling: none of these rows touch
`vanguard/packages/kernel/`. `Governor`, `Reservation`, `Lease`, `Scope`,
`attenuate` and `Grant` are consumed as they are.

**Proposed fault-injection index.** Each point is a candidate acceptance obligation
for its branch, subject to T-129 contract review; none is a current executed test.
The falsifier must kill the process at the named point and assert the stated
recovery, because an untested claim of crash or ABA immunity cannot satisfy
MS-CAS, MS-DELEGATION or MS-CAMPAIGN.

| Point | Kill site | Required post-restart assertion |
|---|---|---|
| `F1` | between blob write and manifest read-back (4.2–4.4) | head unmoved; blobs pinned, not orphaned; retry succeeds |
| `F2` | between receipt execution and sufficiency test (5.3–5.4) | receipts re-read, not re-run; a receipt bound to another `tree_id` reports `VERIFICATION_STALE` |
| `F3` | between commit append and reply (6.8–6.11) | `reconcile_unknown_commit` adopts the committed receipt; no second append; no refund |
| `X1` | after journal `prepared` fsync (E2.2) | nothing restored because nothing was written; lock released |
| `X2` | inside the publish loop (E3.2) | `completed_paths` drives restoration; externally modified paths are preserved and the destination quarantines |
| `D1` | after intent fsync, before `ChildSpawned` (D1.2) | `D-R2` proves non-dispatch before releasing; no orphan child |
| `D2` | after `ChildSpawned`, before `ChildReturned` | `D-R4` holds the reservation unsettled as `CHILD_UNKNOWN`; no refund, no re-dispatch |
| `C1` | after a node lease append, before dispatch | resume reconciles by `operation_id`; the node is not dispatched twice |
| `C2` | after node K passes, before node K+1 dispatch | resume starts at K+1; node K's artifact is reused, not recomputed |

**Concurrency falsifiers.** A single-process lock proves nothing about the
commit boundary. Each of these runs fresh OS processes: (a) `n` concurrent
promotions on one `(head, generation)` — exactly one commits, `n-1` return
`PROMOTION_CONFLICT` or `GENERATION_STALE` and no loser leaves a trace beyond
content-addressed blobs; (b) an `A -> B -> A` rollback cycle with a stale
request held across it — refused with `GENERATION_STALE`, never admitted;
(c) two directors racing one node lease — the superseded `fence_token` cannot
append a disposition; (d) a replayed `transaction_id` carrying different
fields — `TRANSACTION_IDENTITY_MISMATCH`, never the earlier receipt.

## 0. Epistemic legend

| Tag | Meaning |
|---|---|
| **FACT** | Observed in current source |
| **MECHANISM** | Code exists with tests; not a product claim |
| **INFERENCE** | Engineering conclusion from FACT + MECHANISM |
| **[PROPOSAL]** | Future work; keep the text; do not treat as HEAD |
| **ASPIRATION** | Competitive position; not a forecast |
| **CONTRADICTION** | Two authorities disagree; source wins |
| **MISSING** | Path does not exist at lock HEAD `66aa7a3c` |
| **SUPERSEDED** | Keep text, mark `[PROPOSAL]`, cite the better location |

Present docs to open while coding:

| Context | Read first |
|---|---|
| Kernel / TCB | `docs/architecture/boundaries.md`, `vanguard/packages/kernel/dispatch.py` |
| Turn loop | `docs/backend/architecture/agency.md`, `episode/engine.py`, `session.py` |
| Context | `compiler.py`, `layers.py`, `compaction.py` |
| Runtime / resume | `docs/backend/architecture/runtime-execution.md`, `app_service.py`, `task_state.py` |
| Index | `ports/index.py`, `adapters/stores/repo_index.py` |
| Packs | `packs/code-default/` |
| Memory | `docs/backend/architecture/memory-learning.md`, `ports/memory.py` |
| Eval | `docs/backend/architecture/assurance-evaluation.md` |

Wave-titled sections copied below are **capability recipes**, not a calendar.

## Electroweak v0.9.3 Wave 1–2 contract overlay

**Overlay scope and epistemic status.** This is the implementation handbook for
the authorized Electroweak Wave 1–2 contracts in [`spec.md`](spec.md) §EW-9.
Rows explicitly marked **FACT** are observed mechanisms at the 2026-09-05
checkpoint; rows marked `[PROPOSAL]` remain implementation recipes and MUST NOT
be read as HEAD. Authorization comes from `spec.md` §EW-9; this file carries
the recipe and handoff. The
older Wave 0–10 sections below remain historical capability recipes with their
existing titles. Do not renumber, retitle, or infer current scheduling from
them.

This historical EW-9 overlay stops at frozen control. NT-1 above now authorizes
T-77 context/cache hardening and T-106 core recovery before that freeze, plus
the explicitly listed baseline repairs. T-75/T-76, T-78/T-83b extensions,
T-80 workspace-policy treatments, OCT-03 and ARM-01 remain post-control.
DLG-01 live alias/provenance work (T-86/T-90) remains outside this iteration.

### FACT — W1 HAR-01 harness preconditions

No settlement result is useful until the product agent can call declared tools,
write through the mediated path, and explicitly finish. Apply these repairs in
the order below and keep their falsifiers executable:

| Work item | Recipe | Required falsifier |
|---|---|---|
| Capability-bound native profiles (T-69) | In `domain/models/profile.py`, add an explicit `ToolCallStyle.NATIVE` profile only for a production route whose provider-shape vector has verified native dispatch. Preserve `NATIVE -> JSON_SCHEMA -> FENCED_JSON -> TEXT_GRAMMAR` for unknown/unverified routes. Never stamp the registry globally. | Every native-declared route dispatches `patch.apply` and `finish` without degradation; an unverified route is never promoted. |
| Approval passthrough (T-70) | Replace the hardcoded unsealed threshold in `runtime/session.py` with the manifest's existing `components.approval_policy`; do not author a second policy artifact. | The product default honors `mode=assisted`, `threshold=standard`, and `escalate_on=[proc.exec]`; a missing/malformed component fails closed. |
| Finish declaration (T-71) | Add the flat `vg-code-default/finish-tool.json` component and register it for the default/fast/balanced/max product manifests. Use the already supported `ProposalKind.FINISH`; do not add another verb or execution path. | All four manifests resolve the component and can propose `finish`; undeclared or malformed finish remains rejected. |
| Streaming abort (T-70a) | First capture the OpenRouter SSE abort at the two non-retryable malformed/empty proposal call sites. Only after the regression fails may the retryable boundary be changed. | A malformed streamed chunk after completed effects enters bounded protocol recovery instead of discarding the episode. T-70a MUST NOT close as `no_defect` from the earlier hedge. |
| Orientation selectors | Extend the existing `proc://exec/allow/...` set only with the minimum read-only orientation verbs required to locate the workspace and inspect files; keep selector grammar and mediation unchanged. | A fresh agent can orient, while an undeclared executable remains denied. |
| `EffectStarted` singleton | Replay a ledger containing adjacent equal `descriptorDigest` and `leaseId` values before choosing the owner-side fix. The kernel is the sole authorized originator; do not spend TCB headroom speculatively. | One accepted effect produces exactly one `EffectStarted`. |
| Effect-budget binding | Reproduce the known reservation shape before choosing the runtime/kernel boundary. Additive resources and structural ceilings remain distinct. | A known reservation never emits `{}` or an unexplained `-1` settlement. |
| Completion-tool restriction | Re-verify autonomous no-approval re-entry, then bind `_completion_allowed_tools` inside the actual turn loop rather than only at outer engine construction if the defect remains. | The restriction applies on every autonomous iteration. |
| Workspace initialization | Re-verify the advertised `kind=git` environment, then make `vanguard init` establish resolvable workspace state and initialize Git when absent. | Fresh `vanguard init` reaches mediated `proc.exec` without ambient `AETHER_WORKSPACE_ROOT`. |
| Provider configuration | Remove the retired `ollama` route and resolve the literal `$FRONTIER` in the supported pack configuration. llama.cpp / llama-server remains the local inference standard. | Native-only route scan finds no retired alias or unresolved provider placeholder. |
| Workspace hygiene (T-74) | Route `PYTHONPYCACHEPREFIX` outside the workspace tree. Keep index exclusions separate from workspace-digest truth. | A Python effect creates no agent-authored `.pyc` path in the workspace digest. |
| Fenced-action recovery (T-82) | In the existing dialect/invocation pipeline, unwrap markdown-fenced JSON action blocks found in note payloads into candidate proposals. Do not execute raw text. Reject unsolicited `finish` when an invocation remains unparsed or no mutation occurred. | Fenced `patch.apply` recovers through validation; ambiguous or mutation-free finish fails closed. |
| Greenfield prompt and vacuity (T-81/T-83a) | Remove the product prompt conflict that says not to read/search and to write one file per turn. State the scaffold -> red oracle -> atomic 2PC sequence. Keep structural and behavioral evidence distinct; reject `pass` and `NotImplementedError` stubs with `VACUOUS_ORACLE_REJECTED`. | A stub may not produce a green settlement; the same fixture must be red before implementation and green after it. |

The kernel TCB remains **1386 logical LOC** for this overlay. A reproduced defect
that truly requires kernel work needs separate authorization, its complete
architecture package, and a fresh budget check; Wave 1 documentation does not
spend the headroom.

### W1 — TRUTH two-axis settlement and admission (landed mechanisms)

Implement the domain value by following the exact contract in the Synthesis of
Record §3.2; do not duplicate that module body here. The integration recipe is:

1. Add the pure `TaskDisposition` enum and immutable `SettlementReceipt` under
   `domain/evidence`, exporting the six named settlement symbols through the
   package surface. The wire schema is `aether.settlement/1`.
2. Enforce construction refusals for `passed` at zero executed tests, `passed`
   without bound oracle and verification subject, reasonless
   `undeterminable`, and evidence-bearing `not_run`. Make
   `disposition_to_outcome(not_run)` raise `DispositionError`.
3. Emit run termination only on existing `EpisodeCompleted` and emit the
   settlement receipt only on existing `VerdictRecorded`. Allocate no new
   ledger event kind. Keep `terminal_status` a plain string in the domain value
   so `domain` does not import `agency`.
4. Derive the benchmark disposition vocabulary from `TaskDisposition` and
   preserve missingness-marker precedence. Gate only through
   `satisfies_predicate`; never use `!= failed` as a positive test.
5. T-04's production exemption is removed and the RF-25 successor assertions
   are updated. Do not use legacy bare-finish fixtures as a reason to retain a
   permanent product-default bypass; those fixtures remain a separate successor
   obligation.
6. In `_admit_completion`, join mutation receipt, current postimage/epoch,
   relevant tests collected and executed, zero exit code, the existing
   IndexPort-enumerated tamper shield, and zero unresolved omissions/stale-index
   markers. Test implication/caller evidence is required only through the
   currently authorized Wave 1 surface. **T-83b is out of scope here by
   dependency, not by preference:** it wires `IndexPort.get_callers`, which has
   no adapter until `LdaRepoIndex` lands in T-75 (Wave 3). Where the Synthesis
   of Record §7 lists T-83b in the Wave 1 `session.py` cell it contradicts its
   own dependency graph; the dependency governs. Do not re-litigate this.

The axes are independent throughout. Oracle `PASS` never rewrites
`RunTermination` to `completed`, and `abandoned + passed` is a valid settlement.
The decisive contract tests are: `passed@0-tests` raises; reasonless
`undeterminable` raises; `not_run` with an envelope digest raises; outcome
projection of `not_run` raises; `EpisodeCompleted` contains no disposition; and
ledger replay preserves `terminal_status=abandoned` with
`disposition=passed`.

### FACT — W1 INS-01 and BRG-01 instrument integrity

INS-01 is an additive product-path repair. It does **not** reopen
`spec.md` §1 or `MS-INSTRUMENT`.

- Replace the literal CLI run identity with a generated UUID/ULID per new run.
  Only `--resume <id>` may continue an existing identity. Two invocations in
  one workspace must produce different ledgers.
- Carry actual `modelRoutes`, non-null token accounting, `verifiedStepIds`, and
  cost provenance from composition/application service into the product
  receipt. Do not fill missing telemetry with synthetic zeroes.
- Make benchmark execution call `runtime.entrypoint.execute`; a direct call to
  `Runtime.execute_profiled` is useful only when explicitly labeled as a
  different subject.
- In `tools/llama_cpp/cli.py`, use the accepted flash-attention flag; declare
  readiness only while the child is live, its PID matches, and `/props` binds
  the expected model identity. Stop only that verified child, never blanket
  `pkill`. In the MCP server, turn empty and max-token outputs into typed
  fail-closed errors.

Falsify with unique-run-identity, receipt-telemetry, product-path-subject,
bridge-lifecycle, and bridge-empty-output tests. Provider outage, HTTP failure,
or zero model calls settles as `not_run`, not task failure.

### `IN_PROGRESS` — W2 CMX-01 preset unification (T-79)

Unify the product path around the existing `packs/code-default/presets.json`
catalog; do not author replacement budget numbers:

| Preset | `usd_micros` | `millis` | `tokens` | `turns` |
|---|---:|---:|---:|---:|
| fast | 50,000 | 300,000 | 16,000 | 8 |
| balanced | 150,000 | 900,000 | 40,000 | 20 |
| max | 400,000 | 2,400,000 | 96,000 | 40 |

Make `CodingMaxFacade` select that catalog, expose the overlay from the pack
loader, give each product manifest its declared budget policy, and remove the
facade's universal `max_turns=40` default. Trace the selected ceiling through
`runtime/wiring.py` to `Governor` and assert it on `EpisodeStarted.budgetCeiling`.
`usd_micros`, `millis`, `tokens`, and `bytes` are additive reservation
dimensions; `turns` and `depth` are structural ceilings and are never summed.

Checkpoint (session stop): catalog resolution, distinct manifest policies,
cost/turn fields, declared `budgetCeiling` plus separate `budgetAttenuation`,
and removal of `max_turns` from the facade signature are in the working tree.
All 8 named T-79 tests pass. This is an implementation candidate, not accepted
work. Before freezing L0: repair the five boundary violations in
`benchmarks/ladder/evidence.py`, `benchmarks/ladder/l0_triad/runner.py`,
`benchmarks/product_path.py`, and `runtime/cli.py`; repair the four
related-surface failures (`test.apps.coding_max.test_coding_max_facade` ×2,
`test.falsifiers.test_rf90_generic_entrypoint` ×2); then run the touched-surface
gate on a clean subject. `just` is not installed — use the `justfile` recipe
bodies. Do not add Markdown under `docs/`; regenerate knowledge only into
`.generated/knowledge/` after package edits.

### `[PROPOSAL]` W2 — EXP-01 evidence ladder and frozen control

Build the instrument in increasing-cost rungs:

1. **L0 (T-92):** run `P0-FIB`, `P0-CSV`, and `P0-BUG` in fresh workspaces via
   the public CLI. This licenses only the Wave 1 smoke statement.
2. **L1 (T-93):** freeze four greenfield, four single-file bug, and four
   data/CLI tasks. Use them to find fixture/oracle defects; publish no pass rate
   and never reuse tuned L1 tasks as L2 evaluation.
3. **L2:** freeze the exact candidate SHA and a multi-class suite of at least 30
   tasks. Execute single-worker `vg-code-balanced` through the product path.
   Close `MS-CONTROL` only with Wilson LB >= 0.40 and false-completion rate 0.
4. **L3:** after `MS-CONTROL`, compare immutable manifest x model x preset arms
   with at least 30 tasks per arm and one declared dimension changed. License
   relative task-class claims only.

Freeze prompts, tools, fixtures, oracle, model, server flags, sampling, and
budgets on the first measured attempt; any change resets the rung. The harness
writes one append-only row per run with every field group from `spec.md` §EW-9.4,
including `n`, `suite_digest`, and the oracle/tamper digests, and refuses blanks. It also refuses
`pass_rate_pct` when observed rows are fewer than the frozen suite size.

Partition `LIVE-LOCAL`, `LIVE-HOSTED`, `LIVE-HISTORICAL`, `REPLAY`, `STATIC`,
and `UNDETERMINABLE`. Only current `LIVE-*` rows enter capability rates;
undeterminable rows require reasons and leave the denominator. Bind every
non-control run to the T-95 hypothesis registry with a control digest and one
varied dimension.

Publish false-completion rate, Wilson live oracle pass rate, valid first-call
rate, malformed/recovery rate, no-op rate, time to first valid action, turn
waste `W`, and token efficiency `kappa`. **False-completion rate must equal
zero.** It vetoes every pass-rate, lift, latency, token, and cost claim. Publish
the frozen control disposition even when it is negative or undeterminable.

### Historical EW-9 handoff (superseded for near-term ordering by NT-1)

T-79/T-89/T-92–T-95 have 31 named focused tests green and remain unchecked.
Execute the remaining work in this dependency order: **boundary repair ->
related-surface repair (CMX-04 facade + RF-90) -> touched-surface verification
-> T-97 (deferred this pass; TypeScript help/`-m`) -> live T-92/L0
disposition -> T-51/T-52 reconciliation -> T-26 freeze -> T-27**. Freeze no
paid subject before T-26; run L2 only as single-worker `vg-code-balanced` on
the exact clean SHA. T-95 is the hypothesis registry, not gate close. Closure
requires n >= 30, Wilson LB >= 0.40, false-completion rate 0, and a published
POSITIVE, NEGATIVE, UNDETERMINABLE, or INVALID disposition.

After `MS-CONTROL` closes, the remaining post-control rows are IDX-01
T-75/T-76, T-78/T-83b change closure, DLG-01 T-86/T-90, then the
preregistered treatments T-80/T-96 as their `requires:` edges permit. T-77
and core recovery are now pre-control under NT-1. OCT-03,
specialists, memory and campaign work remain blocked by their milestone gates;
do not infer authorization merely from mechanism presence.

---

## Retired planning source bodies

The duplicated v2/A/B planning bodies formerly below are retired from operational
use by the 2026-09-12 leadership decision. They mixed historical subject claims,
wave calendars, alternate algorithms and speculative APIs with current guidance.
No implementation obligation is dropped: active contracts remain in spec.md,
package outcomes in milestones/backlog, and retained task IDs in tasks.md.

The complete original text is recoverable with
`git show 001911e3:docs/execution/technical.md`. It is historical evidence only.
The following headings retain old fragment links; they contain no current
instructions, acceptance claims or file leases. Follow the active control guide
and admitted package contracts instead.

<details>
<summary>Historical section anchors (retired; non-operational)</summary>

## From v2 — architecture catalog and SOTA harness mechanics

## Locked triad roles

## Epistemic legend (applies to every later claim)

## Lock identity

## 1. Executive Synthesis & Strategic Complementarity

### 1.1 The Dual Mission of Vanguard / AETHER

### 1.2 Complementarity with Plan A + Plan B (MERGED is a historical sibling)

## 2. Pillar I: The Harness Builder Framework & Meta-Framework Primitives

### 2.1 The 16 Candidate Computational Substrate Primitives

### 2.2 "Agent as a Compiled Phenotype"

### 2.3 Event-Sourced Workflow Graph & Closed Node Kinds

### 2.4 Pure Artifact-Transform Algebra

## 3. Pillar II: SOTA Long-Horizon Agency & Context Economics (100+ Turns)

### 3.1 The 5 Root Problems of Context Economics

### 3.2 L1–L5 Prefix-Stable Context Architecture

### 3.3 Distillation at the Effect Boundary (`ResultDistiller`)

### 3.4 Recency-Inverted Salience & Pinned Working-Set Header

### 3.5 The Dead-Ends Algebra (`StructuredRecord.dead_ends`)

### 3.6 Repo-Scale Retrieval via Skeletonization, AST Callgraphs & Submodular Knapsack

## 4. Pillar III: Greenfield Multi-File Synthesis & Recoverable Transactions

### 4.1 The Greenfield Synthesis Challenge

### 4.2 Two-Phase Commit (2PC) Multi-File Transaction Protocol

### 4.3 In-Process 0.2ms AST Syntax Pre-Flight Gate

### 4.4 Speculative Branching & Git Checkpoint Rollbacks

## 5. Pillar IV: Autonomous Verification, Tamper-Resistance & Reproducers

### 5.1 Separation of Authority Invariant

### 5.2 The Cryptographic Test Tamper Shield (`TestTamperShield`)

### 5.3 Gated Dual-Loop Reproducer Protocol (Fail-to-Pass Enforcement)

### 5.4 Type-Aware Mutation Testing (EvalPlus / LLMorpheus)

## 6. Pillar V: Model Dialect Wrangling & Response Recovery

### 6.1 Provider Dialect Realities

### 6.2 Decoupled Protocol Recovery Pipeline

### 6.3 Bounded Protocol Recovery State Machine

## 7. Pillar VI: Outer-Loop Meta-Orchestration & Multi-Agent Topologies

### 7.1 The Director Layer (Program-Scale Orchestration)

### 7.2 The Meta-Conductor: Higher-Order Supervisory Loop

#### The Non-LLM `ProgressVector`

#### Closed Vocabulary of 8 Pathologies & Ordered Interventions

### 7.3 Dynamic Bifurcation Functional (HYDRA)

### 7.4 The 5 Specialized Heads & Living Horizon Planning

## 8. Pillar VII: Unified Package Inventory & Operational Runway Mapping

### 8.1 Unified Capability Package Inventory

## 9. Lattice Placement, Invariant Matrix & TCB Budget Accounting

### 9.1 Hexagonal Dependency Lattice Placement

### 9.2 Invariant Matrix

## 10. Conclusion & Next Operational Steps

## 11. Closed-loop controller vs chatbot (product loop)

### 11.1 The loop that everything else hangs on

## 12. CLI as the operator surface (not the brain)

## 13. Small orthogonal toolkit (the agent’s hands)

## 14. Reading and editing stack (where most harnesses die)

## 15. Context: rolling windows, compress, cache, progressive packets

## 16. Index modes: structural map / lexical / graph zoom / docs RAG

## 17. Four-tier memory (short-term vs long-term)

## 18. Skills: progressive disclosure vs `skill_lifecycle.py`

## 19. Loop engineering vs harness engineering

## 20. Meta-cognition (keep it small and powerless)

## 21. Long-session / brownfield fail-to-pass / greenfield oracle

### 21.1 Long sessions (hours, resume, many files)

### 21.2 Brownfield (bugfix / feature in a living tree)

### 21.3 Greenfield (new project, many files, empty src)

## 22. Other pieces that actually matter

## 23. One-picture architecture

## 24. Build order (so this does not become a graveyard of features)

## Appendix: Cross-link matrix (locked triad)

## From B — live inventory, gaps, formal model, lattice, workflows, file routing

## 3. Current implementation inventory

### 3.1 Substrate and control plane

### 3.2 Agency inner loop

### 3.3 Runtime session, state, resume

### 3.4 Packs, verification, change surface

### 3.5 Parallel engines, topology, memory

### 3.6 Models

### 3.7 What VISION already forbids (FACT)

## 4. Proven gaps

### 4.1 False-positive completion on the default path

### 4.2 Invented test counts (Forge)

### 4.3 Heuristic verification classification

### 4.4 Incomplete restart identity

### 4.5 Stale repository intelligence

### 4.6 Change-surface incompleteness

### 4.7 Insufficient long-run evidence

### 4.8 Benchmark membership errors

### 4.9 Multi-agent mechanisms without measured lift

### 4.10 Memory without held-out promotion on the product path

### 4.11 Orchestration proposals not implemented

### 4.12 FEATURE_SPEC vs source (CONTRADICTION table)

### 4.13 Draft reconciliation (do not copy blindly)

## 5. Formal agent model

### 5.1 Constrained POMDP

### 5.2 Event-sourced semantic task state

### 5.3 Progress potential

### 5.4 Context optimization

### 5.5 Retrieval value of information

### 5.6 Blast-radius closure

### 5.7 Verification confidence lattice

### 5.8 Strategy selection

### 5.9 Multi-agent bifurcation

### 5.10 Campaign reliability

### 5.11 Cost per signed pass

### 5.12 Iterative architectural erosion

### 5.13 Budget attenuation

### 5.14 Skill promotion lift

## 6. Target backend architecture

### 6.1 Inner loop (canonical)

### 6.2 Outer loop

### 6.3 Campaign projection

### 6.4 Content-addressed handoffs

### 6.5 Director policy

### 6.6 Typed verification

### 6.7 Repository epoch

### 6.8 Progressive context packet

### 6.9 One-writer workspace policy

### 6.10 Exterior evaluation

### 6.11 Operator control

### 6.12 Where FEATURE_SPEC modules belong (corrected)

## 7. Competency profiles

### 7.1 Senior Developer

### 7.2 Staff Engineer

### 7.3 Principal Architect

### 7.4 Tech Lead

### 7.5 Mapping to public benches (cautious)

## 8. Development waves

### Wave 0 — Truth baseline and benchmark integrity

### Wave 1 — Truthful task-aware completion

### Wave 2 — Durable semantic task state and restart parity

### Wave 3 — Progressive context and repository intelligence

### Wave 4 — Greenfield and brownfield change-surface closure

### Wave 5 — Strong single-agent qualification

### Wave 6 — Adaptive strategy and metacognition `[PROPOSAL]`

### Wave 7 — Specialist agents and topology treatments `[PROPOSAL]`

### Wave 8 — Durable outer-loop campaign director `[PROPOSAL]`

### Wave 9 — Governed memory, skills, and learning `[PROPOSAL]`

### Wave 10 — External benchmark and release qualification `[PROPOSAL]`

## Appendix: historical schedule (do not execute)

## 10. Greenfield workflow

## 11. Brownfield workflow

## 12. Research and explanation workflows

## 13. Model routing

## 14. Multi-agent policy

## 15. Memory and skills

## 16. Benchmark methodology

### 16.1 Task taxonomy (internal)

### 16.2 Official corpora (external; do not treat as interchangeable)

### 16.3 Statistics (mandatory)

### 16.4 What 60–90 means under this methodology

### 16.5 Why this session did not buy a data point

## 17. File-by-file routing

## From B — references, session appendix, algorithms, operator one-pager, tool inventory, product loop

## 20. References

### 20.1 Repository-relative

### 20.2 External

## 21. Session validation appendix

### 21.1 Navigation limitations (repeat)

### 21.2 Tests actually executed

### 21.3 Paid spend

### 21.4 Scope confirmation (to be re-checked after write)

## Appendix A — Algorithms (normative for implementers, still PROPOSAL)

### A.1 Completion admission (target)

### A.2 Turn compile (target)

### A.3 2PC write (target)

### A.4 Campaign step (target)

## Appendix B — Dependency graph (waves)

## Appendix C — Why Plan B is not Plan A copied

## Appendix D — Operator one-pager

## 22. Live tool/verb inventory (lock HEAD `66aa7a3c`)

## 23. Product target loop

## Appendix E — Cross-link matrix (locked triad)

## From A — what the code already provides (G-01…G-12)

## 2. What the code already provides

### 2.1 Foundation worth preserving

### 2.2 The current inner loop

### 2.3 Current public product boundary

### 2.4 Current gaps proven by source or artifacts

#### G-01: completion evidence can be overstated

#### G-02: verification classification is heuristic

#### G-03: task state is present but not yet the universal control state

#### G-04: resume does not yet prove exact cognitive parity

#### G-05: context is bounded but not yet task-adaptive enough

#### G-06: repository intelligence is a port, not yet a complete product loop

#### G-07: multi-file closure is not demonstrated at target scale

#### G-08: benchmark membership integrity failed

#### G-09: strong single-agent behavior is not qualified

#### G-10: topology mechanisms exceed their empirical proof

#### G-11: outer-loop orchestration is proposed, not implemented

#### G-12: memory mechanisms exceed learning evidence

## From A — formal model, target architecture, capability recipes (historical wave bodies)

## 5. Formal model

### 5.1 Partially observable engineering process

### 5.2 Semantic task state

### 5.3 Progress potential

### 5.4 Context allocation

### 5.5 Retrieval value of information

### 5.6 Blast-radius closure

### 5.7 Verification confidence

### 5.8 Strategy selection

### 5.9 Multi-agent bifurcation rule

### 5.10 Campaign reliability

### 5.11 Cost per signed pass

### 5.12 Long-horizon quality erosion

## 6. Target backend architecture

### 6.1 Architectural shape

### 6.2 Required new domain values

### 6.3 Required ports

### 6.4 Typed verification receipt

### 6.5 Progressive context packet

### 6.6 Durable campaign state

### 6.7 Content-addressed handoffs

### 6.8 Director semantics

### 6.9 Single-writer rule

## 7. Wave map

## 8. Wave 0 — Truth baseline and benchmark integrity

### 8.1 Objective

### 8.2 Work packages

#### W0-01: freeze subject identity

#### W0-02: repair task enumeration

#### W0-03: exact-subject runner

#### W0-04: missingness semantics

#### W0-05: baseline corpus

### 8.3 Likely files

### 8.4 Acceptance predicates

### 8.5 Exit gate

## 9. Wave 1 — Truthful task-aware completion

### 9.1 Objective

### 9.2 Required changes

### 9.3 Task classes

### 9.4 Per-class evidence

### 9.5 Likely files

### 9.6 Falsifiers

### 9.7 Exit gate

## 10. Wave 2 — Durable semantic task state and restart parity

### 10.1 Objective

### 10.2 Extend the existing projection

### 10.3 Resume identity

### 10.4 Restart invariants

### 10.5 Likely files

### 10.6 Falsifiers

### 10.7 Exit gate

## 11. Wave 3 — Progressive context and repository intelligence

### 11.1 Objective

### 11.2 Preserve current context strengths

### 11.3 Add phase-aware retrieval

### 11.4 Repository epoch

### 11.5 Omission ledger

### 11.6 LDA integration

### 11.7 Likely files

### 11.8 Falsifiers

### 11.9 Exit gate

## 12. Wave 4 — Greenfield and brownfield change-surface closure

### 12.1 Objective

### 12.2 Unified change graph

### 12.3 Brownfield workflow

### 12.4 Greenfield workflow

### 12.5 Transaction semantics

### 12.6 Test tamper resistance

### 12.7 Likely files

### 12.8 Exit gate

## 13. Wave 5 — Strong single-agent control

### 13.1 Objective

### 13.2 Why single-agent first

### 13.3 Control policy

### 13.4 Fast, balanced, and max

### 13.5 Qualification ladder

### 13.6 Exit gate

## 14. Wave 6 — Adaptive strategy and metacognition

### 14.1 Objective

### 14.2 Controller input

### 14.3 Allowed directives

### 14.4 Forbidden directives

### 14.5 Failure fingerprint

### 14.6 Experiments

### 14.7 Exit gate

## 15. Wave 7 — Specialist agents and topology treatments

### 15.1 Objective

### 15.2 Candidate roles

### 15.3 Topologies to test

### 15.4 Merge policies

### 15.5 Independence

### 15.6 Exit gate

## 16. Wave 8 — Durable outer-loop campaign director

### 16.1 Objective

### 16.2 Reuse before invention

### 16.3 Campaign plan

### 16.4 Rolling horizon

### 16.5 Director review boundary

### 16.6 Campaign dead ends

### 16.7 Likely module placement

### 16.8 Exit gate

## 17. Wave 9 — Governed memory, skills, and learning

### 17.1 Objective

### 17.2 Memory classes

### 17.3 Authorization-before-retrieval

### 17.4 Skill object

### 17.5 Skill utility

### 17.6 Counterfactual replay

### 17.7 Exit gate

## 18. Wave 10 — External benchmark and release program

### 18.1 Objective

### 18.2 Target calibration

### 18.3 Benchmark portfolio

### 18.4 Metrics

### 18.5 Statistical protocol

### 18.6 Sequential testing

### 18.7 Anti-overfitting controls

### 18.8 Release gate

## 19. Dependency graph and sprint sequencing

### 19.1 Critical DAG

### 19.2 Proposed sprint cadence

### 19.3 WIP policy

## From A — file ownership, prompts, models, security, verification, taxonomy, research agents

## 20. File ownership and expected change surface

### 20.1 Domain

### 20.2 Ports

### 20.3 Kernel

### 20.4 Agency

### 20.5 Runtime

### 20.6 Adapters

### 20.7 Apps and packs

### 20.8 Documentation synchronization after authorization

## 21. Agent prompt and policy architecture

### 21.1 Stable system core

### 21.2 Task policy fragments

### 21.3 Dynamic state

### 21.4 Tool ergonomics

### 21.5 Prompt evaluation

## 22. Model strategy

### 22.1 Model-neutral substrate

### 22.2 Routing tiers

### 22.3 Escalation

### 22.4 Provider failure

### 22.5 Routing experiments

## 23. Security, control, and operator semantics

### 23.1 Least authority

### 23.2 Budget attenuation

### 23.3 Human control points

### 23.4 TUI-ready backend events

## 24. Verification matrix

### 24.1 Unit level

### 24.2 Contract level

### 24.3 Integration level

### 24.4 End-to-end level

### 24.5 Adversarial level

## 25. Benchmark task taxonomy

### 25.1 Scope axis

### 25.2 Horizon axis

### 25.3 Work-type axis

### 25.4 Environment axis

### 25.5 Failure attribution axis

## 26. Research and explanation agents

### 26.1 Shared substrate

### 26.2 Research workflow

### 26.3 Explanation workflow

### 26.4 Research verification

## From A — per-task go/no-go checklists (renamed from sprint)

## 30. Go/no-go checklist for each sprint

### Before implementation

### During implementation

### Before review

### Before completion claim

## From A — bibliography, CLI, loop vs harness, four-tier memory, cross-link matrix

## 34. Internal references

### Constitutional and normative

### Current architecture and execution

### Draft and research inputs

### Direct source anchors

### Local empirical artifacts

## 35. External references

### Benchmarks and measurement

### Agent and harness architecture

### Context, memory, and learning

### Statistical and protocol standards

## 37. Operator / CLI surface (lock append)

## 38. Loop engineering vs harness engineering (lock append)

## 39. Four-tier memory (lock append)

## Appendix L: Cross-link matrix (locked triad)

## Lock-append alternate wording (keep; do not drop)

## 37. Operator / CLI surface (lock append)

## 38. Loop engineering vs harness engineering (lock append)

## 39. Four-tier memory (lock append)

## Appendix L: Cross-link matrix (locked triad)

## Planning snapshots (historical; not HEAD identity)

### A §1 evidence boundary

## 1. Evidence boundary and snapshot

### 1.1 Inspected subject

### 1.2 Navigation health

### 1.3 Commands executed during planning

### 1.4 Authority rule

### B §2 evidence boundary

## 2. Evidence boundary and snapshot

### 2.1 Identity (FACT)

### 2.2 Navigation health (FACT, degraded mode)

### 2.3 Commands run this session (FACT)

### 2.4 Tests run this session (FACT)

### 2.5 Benchmark artifacts inspected (FACT)

### 2.6 Paid cost this session (FACT)

### 2.7 Pre-existing dirty worktree (FACT)

### 2.8 How to read the rest of this document

</details>
