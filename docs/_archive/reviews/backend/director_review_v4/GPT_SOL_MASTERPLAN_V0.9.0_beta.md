# GPT Solution Masterplan — Vanguard/AETHER v0.9.0 Beta

Status: locked execution prompt  
Scope: M-1 through M-9 delivery; M-10 plan only  
Lanes: Dev A implementation and producer evidence; Dev B independent verification  

The SWE-bench Verified target of 85%+ and SWE-bench Pro target of 65%+ are qualification thresholds, not claims. They may be reported as achieved only after official, pinned, contamination-controlled evaluation.

# Prompt 1 — Dev A: Backend Delivery, Coding Harness, M-1–M-9

## Role

Act as Lane A Staff/Principal Engineer, Principal Software Architect, Senior AI Agents Specialist, and backend release engineer for Vanguard/AETHER.

Own implementation, integration, producer evidence, backend packaging, coding-agent capability, codebase-explanation capability, and M-9 qualification.

Dev B owns independent verification, acceptance envelopes, and release authorization.

## Mission

Preserve M-1 through M-3.

Complete every reachable backend implementation and producer-evidence requirement for M-4 through M-8.

Begin M-9 product implementation only after its formal authorization gate is met.

After authorization, deliver and qualify Vanguard 0.9.0b1 from installed artifacts.

After M-9 qualification, inspect M-10 and produce an exact implementation plan only.

Do not implement or claim M-10 release features.

Build a general coding-agent harness capable of:

1. Repository exploration.
2. Codebase explanation.
3. Bug localization.
4. Multi-file implementation.
5. Test selection.
6. Patch generation.
7. Patch verification.
8. Recovery after interruption.
9. Long-horizon execution.
10. Planner/executor/reviewer execution.
11. Fork/read/merge execution.
12. Artifact-preserving context compaction.
13. Budget-aware model escalation.
14. Typed retry.
15. Exact evidence and telemetry capture.

Qualification targets:

- SWE-bench Verified: >=85% measured pass rate.
- SWE-bench Pro: >=65% measured pass rate.

Never claim either target from architecture, mechanism tests, synthetic fixtures, small smoke samples, private-task tuning, or model reputation.

If a target is missed, identify the exact failure distribution, implement general fixes, rerun the same preregistered qualification, and report the remaining gap honestly.

## Operating mode

Work autonomously.

Do not ask for routine approval or reviewers.

Do not stop after producing a plan.

Inspect, implement, test, falsify, and prepare producer evidence.

Continue until all reachable work is complete, an external prerequisite is genuinely required, or M-9 is fully qualified and only M-10 planning remains.

When externally blocked:

1. Prove the blocker with a typed diagnostic.
2. Complete every local prerequisite.
3. Emit the exact artifact the external owner must supply.
4. Continue with other reachable work.
5. Never simulate missing external state.

## Authoritative scope

Focus exclusively on backend and evidence surfaces:

- `vanguard/packages/domain/**`
- `vanguard/packages/ports/**`
- `vanguard/packages/kernel/**`
- `vanguard/packages/agency/**`
- `vanguard/packages/runtime/**`
- `vanguard/packages/adapters/**`
- `vanguard/packages/apps/**` only as a backend runtime-client boundary
- `vanguard/packages/agency/manifests/**`
- `schemas/**`
- migrations and package resources
- `benchmarks/**`
- backend portions of `tools/runners/**`
- backend portions of `tools/linters/**`
- backend qualification tooling
- `test/**`
- `pyproject.toml`
- `vanguard/__init__.py`
- existing canonical documentation files

## Prohibited scope

Do not edit frontend clients or TypeScript, React, or Ink code.

Never modify, move, delete, reformat, import, execute, package, or depend on:

`tools/006_LLM_INT_MACHINE/**`

That directory is a separate research engine. It may be read only for conceptual ideas. Any borrowed idea must become an isolated Vanguard-native treatment with a preregistered falsifier and evidence.

Do not create a second runtime.

Do not create a topology-specific execution engine.

Do not bypass `Runtime.run_composed`.

Do not bypass `Runtime.execute_harness` where it is the public harness boundary.

Do not weaken evidence falsifiers, security boundaries, capability attenuation, evaluator isolation, containment checks, exact-subject requirements, clean-subject requirements, fail-closed behavior, or independent acceptance.

Do not overwrite historical evidence bundles or alter historical outcomes.

Do not mark a failed or undeterminable predecessor as passed.

Do not edit milestone acceptance claims.

Do not perform Git commands or execute scripts that invoke Git.

Treat commits, tags, clean trees, remote resolution, and publication as explicit external release-owner prerequisites.

## Documentation authority

Authority order:

1. `VISION.md`
2. `docs/SPEC.md`
3. `docs/01_law/**`
4. accepted ADRs
5. `docs/03_execution/milestones.md`
6. `docs/03_execution/backlog.md`
7. `docs/03_execution/sprint_active.md`
8. `docs/03_execution/sprint_upcoming.md`
9. advisory planning material
10. archived reviews

Archived material cannot authorize implementation or close a milestone.

## Read first, completely, in order

1. `AGENTS.md`
2. `README.md`
3. `VISION.md`
4. `docs/SPEC.md`
5. `docs/01_law/RUNTIME.md`
6. `docs/01_law/DISPATCH.md`
7. `docs/01_law/EXTENSIBILITY.md`
8. `docs/01_law/EVIDENCE.md`
9. `docs/01_law/MEASUREMENT.md`
10. `docs/01_law/SECURITY.md`
11. `docs/02_decisions/INDEX.md`
12. accepted ADR-0094 through ADR-0103
13. later accepted ADRs governing M-4 through M-10
14. `docs/03_execution/milestones.md`
15. `docs/03_execution/backlog.md`
16. `docs/03_execution/sprint_active.md`
17. `docs/03_execution/sprint_upcoming.md`
18. `TODO_PROMPT.md` as advisory only
19. `GLM_masterplan_review.md` as advisory only
20. `docs/_archive/reviews/backend/director_review_v3/guidelines.md` as non-authorizing review material

Read every selected file completely. Do not rely on summaries when the source exists.

## Repository rules

Use `rg` and `rg --files` for discovery.

Use `apply_patch` for edits.

Preserve unrelated dirty-tree changes.

Do not use destructive cleanup.

Do not create scratch Markdown files.

Keep temporary reports outside the repository.

Maintain the dependency direction:

`domain <- ports <- kernel <- agency <- runtime -> adapters`

Adapters must not import kernel or agency.

Domain and kernel must remain application-domain blind.

Keep the kernel within its enforced TCB LOC budget.

Use Python >=3.10 syntax and strict type annotations.

Normal tests must be hermetic and provider keys must remain unset.

## First action: current-subject audit

Before changing code:

1. Identify Python executable and version.
2. Identify package name and canonical version.
3. Identify installed/editable package state without Git.
4. Inventory milestone evidence and acceptance envelopes.
5. Identify active sprint authorization.
6. Run the complete Python suite.
7. Run safe architecture/security checks.
8. Run M-4 through M-8 builders, runners, and verifiers that do not invoke Git or publish.
9. Classify every result.

Classifications:

- mechanism test
- integration test
- evidence build
- producer verification
- independent acceptance
- external prerequisite

Checks include full suite, boundaries, TCB, domain blindness, isolation, execution truth, event coverage, stale paths, test/fixture hygiene, package resources, installed-wheel behavior, recovery, cold replay, non-Git secrets scan, and non-Git evidence structure validation.

Do not change code until every failure has an exact command, exact path and line where possible, typed cause, owning subsystem, milestone impact, and classification.

## M-1 through M-3 continuous preservation

Preserve:

- one canonical Runtime
- `Runtime.run_composed` as sole activated runtime path
- S0 through S12 dispatch
- JCS canonical identity
- exact digest semantics
- additive budgets: `usd_micros`, `millis`, `tokens`, `bytes`
- componentwise reservation and settlement
- structural depth and turn ceilings
- monotonic capability attenuation
- D_H, D_R, D_X identity separation
- one project-ledger writer
- strictly monotonic WAL sequencing
- event-sourced state
- fresh-process continuation
- cold reconstruction
- fail-closed profiles
- exterior evaluator isolation
- signed execution truth
- installed package-resource resolution
- no checkout-relative resources
- hexagonal dependency direction

After each implementation area, rerun focused kernel, budget, attenuation, event-store, recovery, evaluator, composition, profile, and package-resource tests.

## M-4: useful real-model coding proof

Expected current successor:

`docs/03_execution/evidence/M-4-rf95-candidate-07.json`

Treat Dev B's result as authoritative only if producer signature, acceptance signature, acceptance subject, registered keys, materials, cold reconstruction, and board state all verify.

Do not modify candidate-05 or earlier bundles.

Required RF-95 content:

- exact externally supplied subject
- runtime and execution identity
- execution profile
- requested and returned model identity
- provider identity and pricing snapshot
- complete trajectory
- SQLite WAL
- artifacts
- workspace patch
- exterior verifier
- terminal receipt
- cold reconstruction
- canonical Ed25519 producer signature

Producer identity: `dev-a-evidence-1`.

Do not create reviewer acceptance.

Pseudocode:

```python
materials = resolve_existing_rf95_materials()
assert historical_bundles_unchanged()
subject = require_external_exact_subject()

run = Runtime.execute_profiled(
    manifest=canonical_coding_manifest,
    task=rf95_task,
    profile_id="product",
    model=pinned_model,
    store=file_backed_sqlite_wal,
    blobs=durable_cas,
)

assert run.used_Runtime_run_composed
assert run.patch_is_real
assert exterior_verifier(run).passed
assert run.trajectory.complete
assert cold_reconstruct(run.wal).state_digest == run.state_digest

bundle = build_evidence(
    immutable_label=next_label,
    subject=subject,
    runtime_identity=run.runtime_identity,
    execution_identity=run.D_R,
    trajectory=run.trajectory,
    wal=run.wal,
    artifacts=run.artifacts,
    patch=run.patch,
    verifier=run.verifier,
    cold_reconstruction=run.cold_reconstruction,
)

producer_sign(bundle, key_id="dev-a-evidence-1")
verify_locally_without_accepting(bundle)
```

## M-5A: convergence successor baseline

Required external object: `CONVERGENCE-BASE-v1`.

The release owner must publish an annotated remote tag over an approved clean successor subject. Do not create or simulate it.

Require annotated tag-object SHA, commit SHA, tree digest, exact source manifest, event-schema digests, reducer identities, runtime identity, protected subtree digests, contamination exclusions, and `raw-sha256`.

Reject missing, lightweight, local-only, or remotely unresolvable tags.

```python
tag = resolve_external_remote_annotated_tag("CONVERGENCE-BASE-v1")

if tag.missing or tag.lightweight or not tag.remote_resolvable:
    fail_closed("CANDIDATE_NOT_A_BASELINE")

pins = {
    "tag_object_sha": tag.object_sha,
    "commit_sha": tag.commit_sha,
    "tree_digest": compute_external_tree_digest(tag.commit_sha),
    "source_manifest_digest": digest(source_manifest),
    "schema_manifest_digest": digest(schema_manifest),
    "reducer_identity_digest": digest(reducer_identities),
    "runtime_identity_digest": runtime_identity(),
    "protected_subtree_digests": protected_digests,
    "digest_scheme": "raw-sha256",
}

assert contamination_check(pins).passed
emit_producer_baseline_candidate(pins)
```

## M-5B: fresh generality successor

Begin only after `CONVERGENCE-BASE-v1` resolves.

Do not use M-5A-BASE-v2 as control.

Exercise positive, negative, malformed, incomplete, range-boundary, serialization-permutation, equivalent-input, and cold-replay vectors through `Runtime.execute_harness`.

Bind RF-86 and RF-98 comparisons to the approved baseline and use `raw-sha256` for every material.

## M-6: accepted recursion preservation

Audit:

- `vanguard/packages/runtime/root.py`
- `vanguard/packages/runtime/child_runtime.py`
- `vanguard/packages/runtime/delegation.py`
- `vanguard/packages/runtime/session.py`
- `vanguard/packages/runtime/ledger_emitter.py`
- `vanguard/packages/agency/episode/engine.py`
- `vanguard/packages/agency/episode/state.py`
- `vanguard/packages/ports/child_runtime.py`

Preserve public Runtime use, shared `agent.spawn`, deterministic child identity, durable spawn intent, attenuated scopes, monotonic limits, conserved budgets, persisted cost reconstruction, one WAL, no blind retry, undeterminable open-child recovery, truthful cancellation/kill-tree, and strict boundary isolation.

## M-6.5: controller seam

Preserve authority-free between-turn execution, controller-off parity, no capability/budget mutation, checkpoint freshness, bounded directives, deterministic no-op fallback, profile-scoped enablement, and rollback.

Verify corrected evidence has a registered producer key, canonical signature, `raw-sha256`, resolvable report, portable references, explicit disposition, and matching independent acceptance.

Do not reinterpret the historical undeterminable bundle.

## M-7: real multi-role topology execution

Audit runtime, topology, child runtime, delegation, session, ledger emitter, agency topology/episode modules, child-runtime port, stores, manifests, fixtures, falsifiers, and proof runner.

Use one sequential reference loop, one public `agent.spawn` path, ledger refolding between roles, deterministic order, authorized CAS readiness, one child per role, no retry of settled roles, and undeterminable recovery for open children.

```python
while not topology_settled:
    state = cold_fold(project_ledger)

    ready = canonical_sort(
        role
        for role in topology.roles
        if predecessors_settled(role, state)
        and required_artifacts_authorized(role, state, cas)
        and not role_settled(role, state)
    )

    if not ready:
        return typed_blocked_or_failed_state(state)

    role = ready[0]

    request = ChildRequest(
        parent_episode=root_episode,
        idempotency_key=H(topology.digest, role.id, attempt_identity(role, state)),
        capabilities=attenuate(root_capabilities, role.declared_requirements),
        resources=authorized_predecessor_artifacts(role, state),
        budget=reserve_componentwise(parent_remaining_budget(state), role_budget(role)),
        depth=parent_depth + 1,
        turn_limit=min(parent_turn_limit, role.turn_limit),
    )

    append_spawn_intent(project_ledger, request)
    result = public_child_runtime.spawn(request)
    append_role_settlement(project_ledger, result)
    state = cold_fold(project_ledger)
```

Required forms: direct, planner/executor/reviewer, fork/read/merge, every valid fixture, and a production-safe shipped composition.

Planner must emit a durable artifact. Executor and reviewer must consume only authorized digest references. Merge receives only declared predecessor artifacts. Missing, corrupt, or unauthorized artifacts fail closed. Topology never grants authority. Root alone receives configured spawn authority.

Add falsifiers for real role work, readiness, ordering, exactly-once children, sequential non-overlap, attenuation, budgets, artifacts, root-only spawn, crash points, replay, cold reconstruction, topology-off parity, and abandoned effect-free children.

Do not switch release qualification to host-dev. If WSL cannot qualify rootless containment, run mechanism tests explicitly in host-dev and release proof on a qualifying Linux host.

## M-8: durable memory and governed learning

Audit durable scoped memory, migrations, CAS, index transactions, authorization-before-ranking, tenant/category isolation, expiry, revocation, retention, legal hold, GC, degraded states, backup/restore, corruption quarantine, provenance, durable composition CAS, authority separation, signed rollback, restoration, replay protection, and no self-promotion.

Production must never silently select `InMemoryMemoryPort`.

```python
authorized_scope = authorize_before_ranking(principal, request, memory_policy)
if not authorized_scope:
    return typed_denial()

candidates = durable_memory.fetch(authorized_scope)
visible = filter_expired_revoked_and_retained(candidates)
ranked = rank(visible, query)
return attach_provenance(ranked, memory_policy.digest, authorized_scope.receipt)
```

```python
generated = generator.propose(candidate)
evaluation = isolated_evaluator.evaluate(generated, held_out_split=sealed_split)

if not evaluation.passed:
    reject(generated)

decision = promoter.decide(generated, signed_evaluation=evaluation)

if not verify_promoter_signature(decision):
    fail_closed()

if generator.identity in {evaluator.identity, promoter.identity}:
    fail_closed()

activate_by_digest(decision.candidate_digest)
persist_activation_receipt(decision)
```

M-8 requires an exact clean subject, complete runner output, durable materials, backup/restore and corruption proof, signed producer bundle, and independent acceptance over its exact digest. Mechanism tests alone do not close M-8.

## M-9 authorization gate

Do not activate M-9 product implementation until Dev B reports:

1. M-8 producer bundle verifies passed.
2. M-8 independent acceptance verifies passed.
3. Acceptance subject equals M-8 bundle digest.
4. Active sprint board explicitly authorizes M-9.

## M-9: operational beta

Once authorized, deliver `0.9.0b1`.

Primary surfaces include `pyproject.toml`, `vanguard/__init__.py`, runtime CLI/service/wiring/compose/bootstrap/configuration/plugins/registry, adapters, packaged schemas/manifests/migrations, backend installer/uninstaller, qualification tooling, and Python tests.

Requirements:

- one version source
- isolated reproducible wheel and sdist builds
- normalized content-manifest comparison
- empty-environment installation
- execution outside checkout
- no PYTHONPATH
- packaged resources
- explicit state directory
- clean initialization
- safe uninstall preserving data by default
- offline-after-install adapters
- CLI/service configuration and composition parity
- start, stop, resume, inspect events/artifacts
- durable episode identity
- distinct health/readiness
- typed, redacted diagnostics
- no in-memory fallback

Plugin lifecycle requires discovery, schema validation, digest/signature verification, compatibility, explicit activation, authority ceiling, health/readiness, shutdown, upgrade, rollback, disable/remove, and quarantine.

```python
candidate = discover_plugin(path)
verified = verify_plugin(
    manifest=candidate.manifest,
    schema=plugin_schema,
    digest=candidate.content_digest,
    signature=candidate.signature,
    runtime_compatibility=current_runtime,
)

if not verified:
    quarantine(candidate)
    return typed_plugin_failure("verification_failed")

requested_scope = parse_scope(candidate.manifest)
effective_scope = attenuate(configured_plugin_ceiling, requested_scope)

if requires_unavailable_authority(candidate, effective_scope):
    fail_closed("plugin_authority_unavailable")

service = activate_through_runtime_bootstrap(candidate, effective_scope)
if service is None:
    fail_closed("activation_without_service")

persist_plugin_activation_receipt(candidate.content_digest, effective_scope, service.identity)
```

Qualification includes double builds, clean installs, offline coding/formal/topology workflows, memory provenance, kill/resume, event/artifact inspection, full plugin lifecycle, backup/restore, safe uninstall, health/readiness/diagnostics, full suite, mandatory linters, producer beta evidence, and Dev B verification.

## SWE-bench coding harness

Use only the Vanguard runtime path:

`benchmark task -> canonical manifest -> Runtime composition -> Runtime.run_composed -> mediated tools -> durable ledger -> exterior evaluator -> evidence report`

Capture immutable task/repository/container/dependency/test/model/provider/pricing identities plus tokens, cost, latency, retries, patch, changed files, tool calls, replay, contamination, split, and preset.

Presets: direct, planner/executor/reviewer, fork/read/merge.

Capabilities: repository/symbol maps, file retrieval, test discovery/selection, static analysis, dependency tracing, localization, patching, regression verification, bounded repair, typed retry, context compaction, artifact preservation, and model escalation.

```python
attempt = run_once(model=current_model)
if attempt.passed:
    settle(attempt)

failure = classify(attempt)
if failure.kind in RETRYABLE_TYPED_FAILURES and retry_budget_available(failure):
    preserve(attempt.artifacts)
    retry_with_targeted_context(failure)
else:
    settle_without_retry(attempt)
```

Do not use `openrouter/free` as comparative identity. Pin a specific route and record the returned identity.

Permitted requested routes:

- `minimax/minimax-m3:free`
- `z-ai/glm-5.2:free`
- `deepseek/deepseek-v4-flash-0731`

Rate limits remain visible instrument errors.

Paid limit: at most 100 paid calls and $0.40 aggregate; fail closed before either limit.

Evaluation stages:

1. Harness qualification with deterministic tasks and no score claim.
2. Preregistered 10–15 task public smoke set for debugging.
3. Larger fixed public development qualification.
4. Official SWE-bench Verified, target >=85%.
5. SWE-bench Pro, target >=65%.

If targets are missed, preserve reports, classify every failure, separate harness/model/environment/task/localization/patch/test/context/budget failures, implement general fixes, add non-benchmark regressions, rerun matched conditions, and preserve negative runs.

## Codebase-explainer generality proof

Create a held-out explanation benchmark covering architecture, responsibilities, call/data/capability/event paths, persistence/recovery, security boundaries, bug localization, impact analysis, test selection, extension points, and doc/code contradiction detection.

Require exact paths, symbols, evidence references, calibrated uncertainty, and no invented code.

Score path/symbol/call/dependency/security/citation accuracy and unsupported-claim rate with an exterior evaluator.

Falsify renamed modules, missing symbols, misleading docstrings, stale paths, duplicate names, unreachable code, port/adapter confusion, runtime/kernel confusion, historical/current evidence confusion, incomplete trees, and contradictory docs.

Generality requires coding, formal, topology, explanation, and the same runtime/evidence system.

## Evidence rules

Every producer bundle binds immutable label, exact subject, runtime/execution identities, manifest, model/provider, profile, ledger, trajectory, artifacts, patch, verifier, cold reconstruction, digest scheme, producer identity, and canonical signature.

Producer evidence is not acceptance. Mechanism tests are not acceptance.

## M-10 plan only

After M-9 qualification, produce a locked implementation plan covering migration graph, downgrade refusal, backup/restore under load, corruption/interrupted migration recovery, fault injection, bounded soak, performance/security qualification, reproducible release artifacts, exact-subject signed release envelope, external commit/tag/publication gates, rollback, and incident response.

Do not implement M-10.

## Final verification and report

Run complete Python, runtime, agency, recursion, topology, memory, registry, recovery, package, CLI/service, plugin, benchmark, explainer, boundary, TCB, blindness, isolation, truth, coverage, stale-path, hygiene, package-resource, installed-wheel, and empty-environment checks.

Report package/Python versions, exact changed backend paths, test counts, typed failures, M-1–M-9 state, artifact identities, benchmark results, explainer results, evidence, independent gates, external prerequisites, M-10 plan only, and confirmation that frontend and `tools/006_LLM_INT_MACHINE/**` were untouched.

# Prompt 2 — Dev B: Independent Truth Audit and Acceptance

## Role and mission

Act as Lane B Principal Verification Engineer, Independent Evidence Auditor, Senior Security Engineer, AI Evaluation Scientist, and release gatekeeper.

Remain independent from Lane A.

Do not implement Lane A product features, repair producer evidence in place, or create producer signatures.

Verify claims, run falsifiers, issue independent acceptance envelopes, reject invalid claims, and authorize progression only when law permits.

Continuously preserve M-1 through M-3 and M-6 falsification.

Verify every M-4 through M-9 producer artifact, coding/explainer generality treatment, and SWE-bench measurement.

Authorize M-9 only after the exact M-8 gate is satisfied.

After M-9, audit the M-10 plan without authorizing implementation.

## Authority and reading

Use the same authority order and complete reading list specified for Dev A.

## Scope and prohibitions

Inspect producer bundles, acceptances, keys, signatures, materials, subjects, manifests, identities, trajectories, WALs, artifacts, patches, verifiers, reconstructions, packages, benchmark reports, installed behavior, and boards.

You may strengthen independent falsifiers, verifier tests, evidence contracts, acceptance gates, contamination tests, benchmark integrity, package verification, and acceptance envelopes.

Do not fix Lane A runtime defects. Reproduce, minimize, classify, preserve, and report them with exact owning paths.

Do not edit frontend code or `tools/006_LLM_INT_MACHINE/**`.

Do not bypass the canonical runtime, weaken falsifiers, overwrite evidence, reinterpret undeterminable outcomes, accept self-review, accept wrong-subject envelopes, or run Git commands/scripts.

## Independence model

Producer and reviewer identities and registered keys must be distinct.

Acceptance must target the producer bundle digest and carry reviewer identity, key ID, role, outcome, reason, signature, timestamp, and policy identity.

Report mechanical key separation separately from organizational operator independence.

## First action

Without Git:

1. Identify versions.
2. Enumerate bundles, envelopes, and registered keys.
3. Validate schemas and signatures.
4. Resolve materials and digests.
5. Match acceptance subjects.
6. Check supersession.
7. Run full suite and independent falsifiers.
8. Run safe architecture/security checks.
9. Compare results to the active board.
10. Produce a dependency ledger.

Classify each observation as mechanism, integration, producer evidence, producer verification, independent acceptance, or external prerequisite.

## Evidence verification pseudocode

```python
bundle = parse(bundle_path)

assert schema_valid(bundle)
assert immutable_label(bundle)
assert registered_producer(bundle.producer)
assert canonical_signature_format(bundle.signature)
assert verify_signature(bundle)
assert supported_digest_scheme(bundle.materials)
assert all_materials_resolve(bundle.materials)
assert all_material_digests_match(bundle.materials)
assert source_subject_exact(bundle)
assert runtime_identity_present(bundle)
assert execution_identity_present(bundle)
assert trajectory_valid(bundle)
assert wal_valid(bundle)
assert artifacts_valid(bundle)
assert patch_valid_if_claimed(bundle)
assert verifier_valid(bundle)
assert cold_reconstruction_matches(bundle)
assert claim_is_receipt_derived(bundle)
```

```python
acceptance = parse(acceptance_path)

assert acceptance.subject == [bundle.digest]
assert acceptance.reviewer.role == "reviewer"
assert acceptance.reviewer.identity != bundle.producer.identity
assert registered_reviewer(acceptance.reviewer)
assert verify_signature(acceptance)
```

Never accept an envelope pointing to a run ID, commit, milestone name, different bundle, predecessor, or undeterminable subject as passed.

## Milestone audits

M-1 through M-3: verify dispatch, canonical identity, budgets, limits, attenuation, identity separation, ledger/WAL, replay, profiles, evaluator isolation, execution truth, resources, and boundaries after every Lane A change.

M-4: verify candidate-07 producer/acceptance signatures, exact subject, real provider execution, returned identity, pricing, turns/tokens/cost, real patch, exterior tests, file-backed WAL, trajectory, artifacts, reconstruction, terminal digest, and supersession. Separate mechanical and organizational independence.

M-5A: require annotated remote tag, tag object, commit, tree, remote resolution, manifests, reducers, runtime, protected digests, exclusions, and raw-sha256. Missing/lightweight means `CANDIDATE_NOT_A_BASELINE`.

M-5B: require successor evidence bound to `CONVERGENCE-BASE-v1`, all vectors through the canonical harness, fail-closed malformed/unauthorized behavior, raw-sha256, and correct RF-86/RF-98 control.

M-6: preserve order10 and continuously verify depth, identity, intent, attenuation, budgets, WAL, replay, undeterminable recovery, kill-tree, cancellation, and boundary isolation.

M-6.5: require registered key, canonical signature, report, raw-sha256, portable references, explicit disposition, exact acceptance subject, and registered reviewer. A valid negative result may close a disposition study if law allows.

M-7: separately verify parsing/lowering, real effects, and production-safe evidence. Require all topologies, order, exactly-once, readiness, sequentiality, attenuation, root-only spawn, artifacts, corruption rejection, recovery, replay, and parity. Reject host-dev as release containment. Require a qualifying Linux environment when WSL cannot attest rootless containment.

M-8: verify all canonical markers and inspect production wiring for in-memory/fail-open paths. Test authorization-before-ranking, isolation, lifecycle, legal hold, GC, corruption, backup/restore, provenance, contamination, authority separation, promotion/rollback signatures, replay rejection, and restoration.

M-8 authorization requires a passed producer bundle, passed independent acceptance, exact digest subject, exact clean subject, and board authorization.

Required M-9 authorization message:

> M-8 producer bundle verifies passed. M-8 independent acceptance verifies passed. Acceptance subject equals the M-8 bundle digest. The active sprint board authorizes M-9. Lane A may begin M-9 implementation.

M-9: audit exact wheel/sdist identities, normalized manifests, empty installs outside checkout without PYTHONPATH, packaged resources, state, uninstall behavior, CLI/service parity, health/readiness, diagnostics, plugins, recovery, memory, and exact installed-artifact evidence.

## SWE-bench measurement audit

Targets are Verified >=85% and Pro >=65%, but do not authorize claims.

Require preregistered benchmark/task/repository/container/dependency/evaluator/model/provider/call/cost/retry/escalation/preset/contamination/seed/scoring identities.

Reject adaptive task selection, removed failures, unrecorded route changes, hidden-test/oracle leakage, task-specific harness branches, excess retries/cost, environment drift, manual patch repair, or overwritten reports.

Smoke sets are debugging evidence, not official scores. Report uncertainty.

Official reports include eligible/excluded instances, typed failure categories, cost/latency/token/retry/repository distributions, and confidence intervals.

Competitor comparisons require matched tasks, containers, evaluators, models, budgets, and retry policies or official leaderboard-compatible methodology.

## Codebase-explainer audit

Verify preregistration, held-out status, no answer leakage, real cited paths/symbols/call paths, dependency direction, security boundaries, citation resolution, calibrated abstention, and unsupported-claim rate.

Generality requires evidence across coding, formal workload, topology, durable memory, and explanation.

## Contamination audit

Hash task/source/evaluator/model-visible context, search for hidden tests, oracle output, task IDs, expected patches, task-specific retries, and verify held-out tasks were not used for development.

Quarantine and invalidate contaminated reports while preserving them.

## Failure taxonomy

Use typed causes including mechanism/integration/evidence/signature/key/subject/material/digest/source/dirty/contamination/containment/evaluator/provider/pricing/environment/package/recovery/authorization/tag/publication failures.

Never report only “failed.”

## Lane A defect format

Report ID, milestone, severity, classification, reproduction command, expected, observed, path, symbol, first failing event, typed cause, security/evidence impact, required correction, regression test, and retest result.

## M-10 plan audit

After M-9, require an exact migration matrix, downgrade refusal, backup/restore under load, interrupted migration, corruption and power/disk/process/evaluator/provider/plugin faults, bounded soak, performance/security thresholds, reproducible artifacts, exact release envelope, external gates, rollback, and incident response.

Reject implementation claims or vague success criteria.

## Final independent report

Produce:

`Milestone | Mechanism | Producer Evidence | Independent Acceptance | External Gate | Verdict`

Report versions, test/linter results, bundle/signature/subject/supersession results, M-1–M-9 status, M-9 artifact identities, SWE smoke and official scores only when valid, explainer scores, contamination, typed failures, Lane A defects, external prerequisites, M-10 plan audit, and untouched frontend/research-engine confirmation.

## Definition of independent acceptance

A milestone is accepted only when its mechanism satisfies law, producer evidence is valid, materials resolve, subject is exact, signatures verify, acceptance targets the bundle digest, reviewer is registered/distinct, falsifiers pass, external prerequisites resolve, and the active board authorizes transition.

Anything less remains failed, undeterminable, blocked, or mechanism-only.

Never convert uncertainty into success.
