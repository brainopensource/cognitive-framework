#!/usr/bin/env python3
"""Generate reviewed Block B AS_BUILT evidence and Block C blueprint artifacts.

This helper is intentionally confined to ``tools/docs_alpha``.  It does not
inspect legacy documentation, mutate product sources, or create candidate
documentation.  The semantic records below are the reviewed architecture
synthesis; repository paths and the implementation-drift guard make that
synthesis falsifiable at the pinned Block A subject.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / ".generated" / "knowledge"
ANALYSIS_SHA = "9fd444674bf3a97f2673ff36a5f5928ef046c574"
BRANCH = "docs/convergenc-electroweak-v091"
STATUS = {"IMPLEMENTED", "PARTIAL", "PLANNED", "EXPERIMENTAL", "UNRESOLVED", "OBSOLETE", "CONTRADICTED"}
RELEVANT_PREFIXES = (
    "vanguard/packages/", "vanguard/clients/", "packs/", "schemas/", "containers/",
    "test/", ".github/workflows/", "ci/", "pyproject.toml", "package.json",
    "requirements.lock", "uv.lock", "pnpm-lock.yaml",
)


def git(*args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(ROOT), *args], check=True, text=True, capture_output=True
    ).stdout.strip()


def dump_json(name: str, value: Any) -> None:
    (OUT / name).write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def dump_jsonl(name: str, rows: Iterable[dict[str, Any]]) -> None:
    ordered = list(rows)
    (OUT / name).write_text(
        "".join(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n" for row in ordered),
        encoding="utf-8",
    )


def evidence(eid: str, kind: str, path: str, symbols: list[str], supports: list[str],
             tests: list[str] | None = None, notes: str = "") -> dict[str, Any]:
    return {
        "evidence_id": eid, "evidence_type": kind, "path": path, "symbols": symbols,
        "supports_claim_ids": supports, "supporting_tests": tests or [], "notes": notes,
        "analysis_subject_sha": ANALYSIS_SHA,
    }


def claim(cid: str, subsystem: str, observation: str, evidence_ids: list[str], text: str,
          status: str = "IMPLEMENTED", confidence: str = "high",
          contrary: str = "", caveats: list[str] | None = None) -> dict[str, Any]:
    assert status in STATUS
    return {
        "claim_id": cid, "subsystem": subsystem, "observation": observation,
        "evidence_ids": evidence_ids, "claim": text, "status": status,
        "confidence": confidence, "falsification_attempt": contrary,
        "unresolved_caveats": caveats or [], "analysis_subject_sha": ANALYSIS_SHA,
    }


def subsystem(sid: str, name: str, purpose: str, status: str, paths: list[str],
              symbols: list[str], responsibilities: list[str], non_responsibilities: list[str],
              state: dict[str, list[str]], interfaces: list[str], inbound: list[str],
              outbound: list[str], runtime: list[str], failure: list[str], trust: list[str],
              extension: list[str], evidence_ids: list[str], tests: list[str],
              uncertainty: list[str] | None = None, confidence: str = "high") -> dict[str, Any]:
    assert status in STATUS
    return {
        "subsystem_id": sid, "name": name, "purpose": purpose,
        "implementation_status": status, "confidence": confidence,
        "responsibilities": responsibilities, "non_responsibilities": non_responsibilities,
        "state_ownership": state, "implementation_paths": paths, "significant_symbols": symbols,
        "construction_and_bootstrap": runtime, "interfaces": interfaces,
        "inbound_dependencies": inbound, "outbound_dependencies": outbound,
        "runtime_behavior": runtime, "failure_recovery_semantics": failure,
        "trust_and_authority": trust, "extensibility": extension,
        "evidence_ids": evidence_ids, "supporting_tests": tests,
        "uncertainty": uncertainty or [], "analysis_subject_sha": ANALYSIS_SHA,
    }


def page(path: str, cid: str, doc_class: str, purpose: str, audience: list[str],
         facts: list[str], non: list[str], plane: str, evidence_ids: list[str],
         related: list[str], sections: list[str], size: str, diagrams: list[str],
         validation: list[str], phase: str, deferred: bool = False) -> dict[str, Any]:
    return {
        "path": path, "canonical_id": cid, "document_class": doc_class,
        "purpose": purpose, "audience": audience, "canonical_facts_owned": facts,
        "explicit_non_responsibilities": non, "truth_plane": plane,
        "evidence_basis": evidence_ids, "related_canonical_ids": related,
        "expected_sections": sections, "expected_size_scope": size,
        "diagrams": diagrams, "validation_requirements": validation,
        "production_phase": phase, "deferred_until_block_e": deferred,
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    current_head = git("rev-parse", "HEAD")
    current_branch = git("branch", "--show-current")
    changed = [line.split("\t")[-1] for line in git("diff", "--name-status", f"{ANALYSIS_SHA}..HEAD").splitlines() if line]
    relevant_drift = sorted(path for path in changed if path.startswith(RELEVANT_PREFIXES))
    if relevant_drift:
        raise SystemExit(f"implementation evidence drift after {ANALYSIS_SHA}: {relevant_drift}")

    evidence_rows = [
        evidence("E-B-001", "baseline", ".generated/knowledge/baseline.json", [], ["CLM-B-001"], notes="Block A pins the recorded reconstruction subject."),
        evidence("E-B-002", "manifest", "pyproject.toml", ["project.scripts"], ["CLM-B-002", "CLM-B-020"]),
        evidence("E-B-003", "manifest", "package.json", ["workspaces", "scripts"], ["CLM-B-003"]),
        evidence("E-B-004", "manifest", "vanguard/clients/cli/package.json", ["bin.vg", "scripts"], ["CLM-B-003"]),
        evidence("E-B-005", "manifest", "vanguard/clients/client-core/package.json", ["exports"], ["CLM-B-003", "CLM-B-022"]),
        evidence("E-B-006", "manifest", "vanguard/clients/studio/package.json", ["scripts", "dependencies"], ["CLM-B-003"]),
        evidence("E-B-007", "production-code", "vanguard/packages/domain/__init__.py", ["__all__"], ["CLM-B-004", "CLM-B-008"]),
        evidence("E-B-008", "production-code", "vanguard/packages/domain/ledger/events.py", ["EventEnvelope", "parse_event_envelope"], ["CLM-B-008", "CLM-B-009"], ["test/contracts/test_event_substrate_v2.py"]),
        evidence("E-B-009", "production-code", "vanguard/packages/domain/ledger/reducer.py", ["reduce_event", "reconstruct_state", "compute_state_digest"], ["CLM-B-009", "CLM-B-015"], ["test/test_ledger_properties.py"]),
        evidence("E-B-010", "production-code", "vanguard/packages/domain/ledger/agent_view.py", ["AgentView", "fold_agent_view"], ["CLM-B-010"], ["test/contracts/test_m5a_agent_view.py"]),
        evidence("E-B-011", "production-code", "vanguard/packages/ports/__init__.py", ["__all__"], ["CLM-B-004", "CLM-B-021"]),
        evidence("E-B-012", "production-code", "vanguard/packages/ports/spi.py", ["IPlanner", "IContextManager", "IToolkit", "IMemoryEngine", "IEvaluationGate"], ["CLM-B-021"], ["test/contracts/test_spi_protocols.py"]),
        evidence("E-B-013", "production-code", "vanguard/packages/kernel/dispatch.py", ["Kernel.dispatch", "DispatchResult", "SuspensionToken"], ["CLM-B-005", "CLM-B-011", "CLM-B-016"], ["test/kernel/test_dispatch.py"]),
        evidence("E-B-014", "production-code", "vanguard/packages/kernel/attenuation.py", ["attenuate", "Scope", "Constraints"], ["CLM-B-012"], ["test/kernel/test_attenuation.py"]),
        evidence("E-B-015", "production-code", "vanguard/packages/kernel/budget.py", ["Governor", "Reservation", "ADDITIVE_DIMENSIONS"], ["CLM-B-013"], ["test/kernel/test_grant_budget_events.py", "test/kernel/test_governor_concurrency.py"]),
        evidence("E-B-016", "linter", "tools/linters/check_tcb_budget.py", [], ["CLM-B-005", "CLM-B-027"], notes="2026-08-29 run: 1384 logical LOC, threshold 1438, PASS."),
        evidence("E-B-017", "linter", "tools/linters/check_boundaries.py", [], ["CLM-B-004", "CLM-B-026"], notes="2026-08-29 run: 453 source files, PASS."),
        evidence("E-B-018", "linter", "tools/linters/check_domain_blindness.py", [], ["CLM-B-006"], notes="2026-08-29 run: PASS for domain and kernel."),
        evidence("E-B-019", "production-code", "vanguard/packages/agency/episode/engine.py", ["EpisodeEngine.run", "EpisodeEngine.spawn"], ["CLM-B-007", "CLM-B-014"], ["test/agency/test_episode.py", "test/agency/test_episode_spawn.py"]),
        evidence("E-B-020", "production-code", "vanguard/packages/agency/context/compiler.py", ["ContextCompiler"], ["CLM-B-007"], ["test/agency/test_context_compiler.py"]),
        evidence("E-B-021", "production-code", "vanguard/packages/runtime/compose.py", ["Runtime.compose", "Harness", "TaskContext"], ["CLM-B-017", "CLM-B-021"], ["test/contracts/test_a1_canonical_composition.py"]),
        evidence("E-B-022", "production-code", "vanguard/packages/runtime/activation.py", ["plan_activation", "activate", "ActivationPlan"], ["CLM-B-017"], ["test/contracts/test_b2_lifecycle_integration.py"]),
        evidence("E-B-023", "production-code", "vanguard/packages/runtime/run_plan.py", ["RunPlan", "plan_run"], ["CLM-B-017"], ["test/runtime/test_release_identity.py"]),
        evidence("E-B-024", "production-code", "vanguard/packages/runtime/root.py", ["Runtime.execute_profiled", "Runtime.run_composed", "Runtime.execute_harness"], ["CLM-B-017", "CLM-B-018", "CLM-B-025"], ["test/runtime/test_composition_root.py", "test/falsifiers/test_rf94_single_runtime_authority.py"]),
        evidence("E-B-025", "production-code", "vanguard/packages/runtime/bootstrap.py", ["RuntimeBootstrap.build"], ["CLM-B-018", "CLM-B-020"], ["test/falsifiers/test_rf87_execution_profile_identity.py", "test/falsifiers/test_rf88_sandbox_fail_closed.py"]),
        evidence("E-B-026", "production-code", "vanguard/packages/runtime/session.py", ["HarnessSession", "HarnessSession.run", "HarnessSession.reconstruct"], ["CLM-B-007", "CLM-B-015", "CLM-B-017"], ["test/runtime/test_harness_session.py", "test/runtime/test_resume_from_ledger.py"]),
        evidence("E-B-027", "production-code", "vanguard/packages/runtime/ledger_emitter.py", ["LedgerEmitter", "RoleScopedEmitter", "PRIVILEGED_KIND_OWNERS"], ["CLM-B-008", "CLM-B-011"], ["test/kernel/test_event_kinds_writer.py"]),
        evidence("E-B-028", "production-code", "vanguard/packages/adapters/stores/event_store.py", ["SqliteEventStore", "InMemoryEventStore"], ["CLM-B-009", "CLM-B-015"], ["test/contracts/test_event_store_port.py", "test/contracts/test_b3_wal_recovery.py"]),
        evidence("E-B-029", "production-code", "vanguard/packages/runtime/ledger/recovery.py", ["RecoveryScanner", "replay_ledger_state"], ["CLM-B-015"], ["test/falsifiers/test_rf25_cold_continuation.py"]),
        evidence("E-B-030", "production-code", "vanguard/packages/runtime/checkpoints.py", ["CheckpointManager", "Reconstruction"], ["CLM-B-015"], ["test/falsifiers/test_rf96_checkpoint_reconstruction.py"]),
        evidence("E-B-031", "production-code", "vanguard/packages/adapters/stores/blob_store.py", ["FileBlobStore", "InMemoryBlobStore"], ["CLM-B-019"], ["test/runtime/test_blob_and_index_ports.py"]),
        evidence("E-B-032", "production-code", "vanguard/packages/runtime/delegation.py", ["SpawnAdapter", "derive_child_id", "prepare_spawn"], ["CLM-B-014"], ["test/falsifiers/test_rf101_rf112_canonical_recursion.py"]),
        evidence("E-B-033", "production-code", "vanguard/packages/runtime/child_runtime.py", ["RuntimeChildRunner.run_child"], ["CLM-B-014"], ["test/falsifiers/test_rf55_rf59_delegation_e2e.py"]),
        evidence("E-B-034", "production-code", "vanguard/packages/runtime/topology.py", ["parse_topology", "lower_topology", "RunPlanExtension"], ["CLM-B-023"], ["test/runtime/test_topology_lowering.py", "test/falsifiers/test_m7_topology_execution.py"]),
        evidence("E-B-035", "production-code", "vanguard/packages/runtime/workflow_scheduler.py", ["WorkflowScheduler.run"], ["CLM-B-024"], ["test/workflows/test_workflow_scheduler.py"]),
        evidence("E-B-036", "production-code", "vanguard/packages/runtime/staged_workflow.py", ["StagedWorkflowEngine.run_workflow"], ["CLM-B-024"], ["test/runtime/test_staged_workflow.py"]),
        evidence("E-B-037", "production-code", "vanguard/packages/ports/memory.py", ["MemoryBinding", "MemoryAuthorizationPort", "authorize_memory_action"], ["CLM-B-028"], ["test/security/test_m8_memory_fake_parity.py"]),
        evidence("E-B-038", "production-code", "vanguard/packages/adapters/stores/memory_engine.py", ["DurableMemoryPort"], ["CLM-B-028"], ["test/adapters/test_durable_memory_port.py", "test/security/test_m8_memory_falsifiers.py"]),
        evidence("E-B-039", "production-code", "vanguard/packages/runtime/governance/learning.py", ["CompositionRegistry", "CompositionPromotionService"], ["CLM-B-029"], ["test/runtime/test_governed_learning.py"]),
        evidence("E-B-040", "production-code", "vanguard/packages/adapters/evaluators/daemon.py", ["EvaluatorDaemon", "main"], ["CLM-B-030"], ["test/adapters/test_evaluator_daemon.py"]),
        evidence("E-B-041", "production-code", "vanguard/packages/runtime/evaluator_gateway.py", ["record_verdict"], ["CLM-B-030"], ["test/runtime/test_evaluation_service.py"]),
        evidence("E-B-042", "production-code", "vanguard/packages/runtime/app_service.py", ["ApplicationService"], ["CLM-B-020"], ["test/runtime/test_app_service_and_cli.py"]),
        evidence("E-B-043", "production-code", "vanguard/packages/runtime/cli.py", ["main", "build_parser"], ["CLM-B-002", "CLM-B-020"], ["test/runtime/test_app_service_and_cli.py"]),
        evidence("E-B-044", "production-code", "vanguard/packages/runtime/service/contract.py", ["COMMAND_RUN_SCOPE", "validate_command", "validate_frame_envelope"], ["CLM-B-022", "CLM-B-031"], ["test/contracts/test_runtime_service_contract_parity.py"]),
        evidence("E-B-045", "production-code", "vanguard/packages/runtime/service/service.py", ["RuntimeService", "RuntimeService._run_worker_thread"], ["CLM-B-022", "CLM-B-031"], ["test/runtime/test_runtime_service.py"]),
        evidence("E-B-046", "production-code", "vanguard/packages/runtime/service/server.py", ["RuntimeServer", "main"], ["CLM-B-002", "CLM-B-022"], ["test/runtime/test_runtime_service.py"]),
        evidence("E-B-047", "production-code", "vanguard/clients/cli/src/commands/index.ts", ["COMMANDS"], ["CLM-B-003", "CLM-B-020"], ["vanguard/clients/cli/test/commands.test.ts"]),
        evidence("E-B-048", "production-code", "vanguard/clients/client-core/src/adapters/live.ts", ["LiveRuntimeClient.startRun"], ["CLM-B-022", "CLM-B-031"], ["vanguard/clients/client-core/test/core.test.ts"]),
        evidence("E-B-049", "schema", "schemas/v4/runtime-service.schema.json", ["RuntimeServiceFrame"], ["CLM-B-022"], ["test/contracts/test_runtime_service_vectors.py"]),
        evidence("E-B-050", "schema", "schemas/mhf/manifest_v2.schema.json", ["mhf.manifest/2"], ["CLM-B-021"], ["test/contracts/test_manifest_v2_graph.py"]),
        evidence("E-B-051", "schema", "schemas/mhf/trajectory_v2.schema.json", ["mhf.trajectory/2"], ["CLM-B-019", "CLM-B-030"], ["test/contracts/test_trajectory_v2.py"]),
        evidence("E-B-052", "configuration", "vanguard/packages/runtime/profiles.py", ["PRESETS", "resolve_profile"], ["CLM-B-018", "CLM-B-031"], ["test/contracts/test_execution_profile_v2.py"]),
        evidence("E-B-053", "pack", "packs/code-default/harness.yaml", [], ["CLM-B-021"], ["test/packs/test_gates.py"]),
        evidence("E-B-054", "configuration", "vanguard/packages/agency/manifests/vg-code-default/manifest.json", [], ["CLM-B-021"], ["test/agency/test_manifest_loader.py"]),
        evidence("E-B-055", "production-code", "vanguard/packages/runtime/transform_runtime.py", ["TransformRuntime.execute"], ["CLM-B-024"], ["test/transforms/test_transform_runtime.py"]),
        evidence("E-B-056", "linter", "tools/linters/check_isolation_policy.py", [], ["CLM-B-006"], notes="2026-08-29 run: PASS."),
    ]

    claims = [
        claim("CLM-B-001", "SUB-B-00", "Block A recorded branch head SHA 9fd4446; later commits were diffed by evidence class.", ["E-B-001"], "All AS_BUILT claims describe one immutable analysis subject and current reconstruction commits did not alter implementation evidence.", contrary="Diffed production code, tests, schemas, config, manifests, clients, CI and public-interface surfaces from subject to current HEAD; found no changes."),
        claim("CLM-B-002", "SUB-B-11", "Four Python console scripts resolve to callable main functions.", ["E-B-002", "E-B-040", "E-B-043", "E-B-046"], "The installed Python entry points are vanguard, vanguard-evaluator, vanguard-daemon, and vanguard-studio.", contrary="Parsed project.scripts and inspected each target symbol."),
        claim("CLM-B-003", "SUB-B-11", "npm declares three client workspaces and vg as a binary.", ["E-B-003", "E-B-004", "E-B-005", "E-B-006", "E-B-047"], "The TypeScript surface consists of reusable client-core, the vg CLI/TUI, and Studio.", contrary="Parsed root/workspace manifests and command registry; searched for additional client package manifests."),
        claim("CLM-B-004", "SUB-B-01", "Package exports and import linter establish the lower-layer dependency lattice.", ["E-B-007", "E-B-011", "E-B-017"], "Production dependencies flow through domain, ports, kernel, agency and runtime; adapters implement outward ports and are composed by runtime.", contrary="Ran the boundary linter across 453 source files and searched imports rather than relying on directory names."),
        claim("CLM-B-005", "SUB-B-03", "Kernel.dispatch is the generic mediated-effect path and kernel is budgeted as TCB.", ["E-B-013", "E-B-016"], "Kernel owns effect admissibility, grants, generic budget accounting and dispatch settlement, not domain behavior.", contrary="Searched production for adapter execution and direct environment mutation paths; runtime adapters are constructed outside kernel, while effect proposals enter Kernel.dispatch."),
        claim("CLM-B-006", "SUB-B-03", "Domain/kernel blindness and sandbox policy linters pass.", ["E-B-018", "E-B-056"], "The trusted core contains no coding/tool-domain vocabulary and proc.exec plugins declare an isolation mechanism.", contrary="Executed both linters; noted the non-fatal missing historical layer0 scan target."),
        claim("CLM-B-007", "SUB-B-04", "EpisodeEngine drives proposals sequentially; HarnessSession wires model/context/kernel and approval re-entry.", ["E-B-019", "E-B-020", "E-B-026"], "Agency owns the generic bounded turn loop, while runtime session owns concrete wiring and lifecycle.", contrary="Inspected both engine.run and HarnessSession.run and searched for a second production turn engine."),
        claim("CLM-B-008", "SUB-B-05", "LedgerEmitter constructs digest-chained mhf.event/2 envelopes through role-scoped facades.", ["E-B-008", "E-B-027"], "Runtime has a single canonical event-envelope writer with privileged event-kind ownership checks.", contrary="Searched production for EventEnvelope construction and EventStore.append calls; service ingestion is a distinct external frame-to-canonical append boundary and is recorded separately."),
        claim("CLM-B-009", "SUB-B-05", "Reducers fold ordered envelopes; SQLite persists unique events under WAL with integrity operations.", ["E-B-008", "E-B-009", "E-B-028"], "Causal events are authoritative state; LedgerState and other views are derived projections.", contrary="Inspected reducer inputs and store read/append; searched for an authoritative mutable agent-state database."),
        claim("CLM-B-010", "SUB-B-05", "AgentView is a pure fold over lineage events.", ["E-B-010"], "Persisted agent semantic state is represented as an event-derived AgentView, not a durable Agent object.", contrary="Searched production for Agent classes and state stores; transient episode/session objects exist but continuation-critical state is reconstructed from events.", caveats=["Transient model dialogue and runtime objects exist during a process; the claim concerns durable semantic authority."]),
        claim("CLM-B-011", "SUB-B-03", "Kernel writes pre-effect intent before adapter execution and emits settlement after lease release.", ["E-B-013", "E-B-027"], "Privileged effects use ordered intent, dispatch, budget settlement and terminal event semantics.", contrary="Reviewed all guarded-block exits and kernel failure-path tests."),
        claim("CLM-B-012", "SUB-B-03", "attenuate rejects action/resource/constraint widening without intersection.", ["E-B-014"], "Child authority can only narrow monotonically and over-broad requests fail closed.", contrary="Checked action, selector, constraint, depth and network comparisons plus attenuation tests."),
        claim("CLM-B-013", "SUB-B-03", "Governor accounts exactly four additive dimensions and keeps depth/turns structural.", ["E-B-015"], "Budget authority conserves usd_micros, millis, tokens and bytes with thread-safe reserve/commit/release.", contrary="Inspected additive dimension roster, rejection of extra dimensions and concurrency tests."),
        claim("CLM-B-014", "SUB-B-07", "agent.spawn is dispatched as an effect; SpawnAdapter persists child facts and RuntimeChildRunner re-enters Runtime.run_composed.", ["E-B-019", "E-B-032", "E-B-033"], "Recursive delegation creates attenuated nested lineages without a second runtime.", contrary="Searched for child execution constructors and verified the runner callback is the public run_composed seam."),
        claim("CLM-B-015", "SUB-B-05", "Session detects prior ledger state, reconciles open effects/children and emits RunRecovered; checkpoints fall back to cold fold.", ["E-B-009", "E-B-026", "E-B-028", "E-B-029", "E-B-030"], "File-backed runs support process-independent continuation, replay, recovery and proof-aware checkpoint acceleration.", contrary="Inspected empty, existing, corrupt, open-intent and checkpoint-failure paths; ran recovery-focused tests."),
        claim("CLM-B-016", "SUB-B-03", "Adapter exceptions produce UNDETERMINABLE after durable intent rather than manufactured success/failure.", ["E-B-013"], "Unknown physical occurrence is preserved as an explicit failure semantic.", contrary="Inspected exception mapping, reconciliation event emission and failure-path tests."),
        claim("CLM-B-017", "SUB-B-06", "Canonical run construction is manifest composition, activation planning, run-plan identity, HarnessSession and EpisodeEngine.", ["E-B-021", "E-B-022", "E-B-023", "E-B-024", "E-B-026"], "Runtime owns the canonical compose → activate → run lifecycle and binds D_H/D_R-like digests into the run plan.", contrary="Traced product entry points to execute_profiled/run_composed and searched for alternate production composition roots."),
        claim("CLM-B-018", "SUB-B-06", "RuntimeBootstrap resolves profile to concrete model, store and environment; containment profiles fail when unavailable.", ["E-B-024", "E-B-025", "E-B-052"], "Profile resolution is the production adapter-construction seam and does not silently downgrade requested containment.", contrary="Inspected every profile branch and RF-87/RF-88 tests."),
        claim("CLM-B-019", "SUB-B-05", "Large captured values go to a content-addressed BlobStore and trajectory/2 binds evidence references.", ["E-B-031", "E-B-051"], "Artifacts are content-addressed durable bytes distinct from ledger facts and derived projections.", contrary="Inspected blob put/get digest verification and trajectory schema; did not infer retention beyond implemented capture policy."),
        claim("CLM-B-020", "SUB-B-11", "Python CLI uses ApplicationService; TS vg exposes code/daemon/query/TUI commands and direct stdin-json coding execution.", ["E-B-002", "E-B-025", "E-B-042", "E-B-043", "E-B-047"], "AETHER exposes multiple client transports over runtime services, with the runtime retaining authority.", status="PARTIAL", contrary="Mapped all console scripts, npm bin, TS command registry, ApplicationService calls, RuntimeService calls and direct generic entrypoint.", caveats=["The Python vanguard CLI and TypeScript vg CLI have overlapping but non-identical command vocabularies."]),
        claim("CLM-B-021", "SUB-B-10", "Manifest compiler binds components, artifacts, tool schemas, budgets, risks and bindings into a frozen harness.", ["E-B-012", "E-B-021", "E-B-050", "E-B-053", "E-B-054"], "Extensibility is manifest/pack/port/adapter based; domain packs supply task semantics outside kernel.", contrary="Traced packaged manifest and code-default pack through Runtime.compose and checked kernel imports for pack/domain semantics."),
        claim("CLM-B-022", "SUB-B-11", "vg.4 validates commands, persists an idempotency inbox, streams canonical events over a 0600 UDS and has TypeScript clients.", ["E-B-005", "E-B-044", "E-B-045", "E-B-046", "E-B-048", "E-B-049"], "RuntimeService is the durable command/query/stream API for live clients.", status="PARTIAL", contrary="Compared Python tables, JSON Schema and TS request construction; found the profile-default mismatch in CLM-B-031."),
        claim("CLM-B-023", "SUB-B-07", "mhf.topology/1 is parsed as authority-free routing data and lowered to sequential agent.spawn operations.", ["E-B-024", "E-B-034"], "The canonical runtime implements sequential multi-role topology by lowering roles into ordinary recursive lineages.", contrary="Inspected topology authority-field rejection, sequential scheduler, root integration and M-7 execution tests."),
        claim("CLM-B-024", "SUB-B-07", "WorkflowScheduler, StagedWorkflowEngine and TransformRuntime are importable and unit-tested but have no caller in the canonical runtime.", ["E-B-035", "E-B-036", "E-B-055"], "A separate mhf.topology/2 workflow DAG and staged workflow mechanism exist only as isolated partial surfaces at this SHA.", status="PARTIAL", confidence="high", contrary="Searched every production Python import/reference to WorkflowScheduler and StagedWorkflowEngine; found definitions only."),
        claim("CLM-B-025", "SUB-B-06", "Runtime.execute_harness remains callable but its own contract says it is retired from production paths.", ["E-B-024"], "execute_harness is an obsolete compatibility/evidence seam; execute_profiled is the product entrypoint.", status="OBSOLETE", contrary="Searched all production callers; none invoke execute_harness, while tests/evidence still do."),
        claim("CLM-B-026", "SUB-B-02", "Adapters import ports/domain and boundary linter detects forbidden higher-layer imports.", ["E-B-017"], "Ports define dependency inversion and adapters do not import kernel or agency.", contrary="Executed the boundary linter and reviewed port protocols."),
        claim("CLM-B-027", "SUB-B-03", "The measured kernel is 1384 logical LOC against a 1438 limit.", ["E-B-016"], "The TCB directory is within its enforced size ceiling at the analysis SHA.", contrary="Ran the repository linter rather than relying on documentation's older count."),
        claim("CLM-B-028", "SUB-B-08", "MemoryBinding authorizes operations before DurableMemoryPort recall/write and durable storage supports revocation, GC, backup and restore.", ["E-B-037", "E-B-038"], "Durable categorized memory is implemented behind authorization-aware ports and SQLite/blob storage.", contrary="Inspected authorization-before-recall paths and security/recovery tests."),
        claim("CLM-B-029", "SUB-B-08", "Governed composition promotion uses immutable digests and separated generator/evaluator/promoter identities.", ["E-B-039"], "Composition learning/promotion and rollback mechanisms are implemented as runtime governance services, not kernel semantics.", contrary="Inspected lifecycle state transitions and governed-learning tests; no claim of external acceptance is made."),
        claim("CLM-B-030", "SUB-B-09", "Evaluator daemon signs verdicts externally and evaluator gateway is the privileged VerdictRecorded writer.", ["E-B-040", "E-B-041", "E-B-051"], "Evaluation and evidence capture are exterior to the episode and feed signed results into the causal record.", contrary="Traced evaluator CLI, client/gate, signing and session terminal evaluation; searched for episode self-signing."),
        claim("CLM-B-031", "SUB-B-11", "LiveRuntimeClient.startRun omits profileId; RuntimeService defaults it to code-default; resolve_profile has no such preset or alias.", ["E-B-045", "E-B-048", "E-B-052"], "The live daemon StartRun path without an explicit profile is internally incompatible and fails at runtime bootstrap.", status="CONTRADICTED", contrary="Compared client payload, service default and complete preset/alias table; searched tests for an end-to-end default-profile launch and found none."),
    ]

    subsystems = [
        subsystem("SUB-B-01", "Domain contracts and projections", "Own pure values, canonicalization, event/artifact/workflow contracts and deterministic reducers.", "IMPLEMENTED", ["vanguard/packages/domain/"], ["EventEnvelope", "LedgerState", "AgentView", "FrozenComposition", "WorkflowSpec"], ["Canonical value construction", "Event and artifact contract values", "Pure state/progress/agent/workflow folds", "Selector and digest algebra"], ["I/O", "Adapter construction", "Effect authorization", "Runtime lifecycle"], {"authoritative": ["none; domain values are in-memory representations"], "derived": ["LedgerState", "AgentView", "ProgressView", "WorkflowState"], "transient": ["immutable value instances"], "persistent": ["none directly"]}, ["vanguard.packages.domain exports", "mhf.event readers", "manifest and selector parsers"], ["all higher Python layers"], ["Python stdlib only"], ["Parse values; fold ordered facts; emit deterministic values/digests"], ["Malformed input raises typed value/reducer errors", "Unknown events are preserved by ledger projections where supported"], ["No authority; provides relations used by authority owners"], ["New pure contracts, reducers and selectors"], ["E-B-007", "E-B-008", "E-B-009", "E-B-010"], ["test/test_ledger_properties.py", "test/contracts/test_event_substrate_v2.py"]),
        subsystem("SUB-B-02", "Ports and SPIs", "Define dependency-inversion protocols for kernel, model, environment, stores, evaluator, memory and plugins.", "IMPLEMENTED", ["vanguard/packages/ports/"], ["EventStorePort", "ModelPort", "EnvironmentAdapter", "ChildRuntimePort", "MemoryBinding", "IPlanner", "IToolkit"], ["Stable callable boundaries", "Typed result/failure vocabulary", "Five pack SPIs"], ["Concrete I/O", "Policy decisions", "Lifecycle composition"], {"authoritative": [], "derived": [], "transient": ["protocol values"], "persistent": []}, ["Python Protocols and dataclasses"], ["kernel", "agency", "runtime", "adapters"], ["domain"], ["Consumers call protocols; adapters satisfy them structurally"], ["PortFailure/Result and typed exceptions preserve failure at boundaries"], ["Ports carry no authority by themselves"], ["New adapters and test doubles"], ["E-B-011", "E-B-012", "E-B-017"], ["test/contracts/test_spi_protocols.py", "test/contracts/test_event_store_port.py"]),
        subsystem("SUB-B-03", "Kernel trusted core", "Mediate every generic effect through authorization, grants, typed resources and ordered settlement.", "IMPLEMENTED", ["vanguard/packages/kernel/"], ["Kernel", "Governor", "GrantIssuer", "attenuate", "StandardPolicy"], ["S1-S12 dispatch", "Capability attenuation", "Budget reserve/commit/release", "Generic policy and provenance"], ["Domain workflows", "Model selection", "Persistence implementation", "Evaluation", "Scheduling"], {"authoritative": ["live grants and Governor accounting during a run"], "derived": ["dispatch results and emitted facts"], "transient": ["leases", "suspension tokens"], "persistent": ["facts emitted via LedgerEmitter"]}, ["Kernel.dispatch", "Scope/Constraints", "DispatchResult"], ["agency", "runtime"], ["domain", "ports"], ["parse → resolve → describe → classify → authorize → grant → reserve → verify/intent → dispatch → commit → release → emit"], ["Fail closed before effect", "Adapter exception becomes UNDETERMINABLE", "Intent append failure prevents effect", "Lease release alarm is fatal"], ["Owns generic effect admissibility and resource authority"], ["Adapters remain injected behind EffectAdapter"], ["E-B-013", "E-B-014", "E-B-015", "E-B-016", "E-B-018"], ["test/kernel/test_dispatch.py", "test/kernel/test_attenuation.py"], confidence="high"),
        subsystem("SUB-B-04", "Agency turn engine and context", "Run the bounded sequential propose/dispatch/observe loop and compile model context.", "IMPLEMENTED", ["vanguard/packages/agency/"], ["EpisodeEngine", "Episode", "Turn", "ContextCompiler", "ProtocolRecoveryPolicy"], ["Sequential turn lifecycle", "Proposal parsing/recovery", "Context layering/compaction", "Generic spawn proposal dispatch"], ["Concrete adapters", "Exterior evaluation", "Canonical composition", "Durable store ownership"], {"authoritative": [], "derived": ["turn state from inputs"], "transient": ["episode object", "model dialogue/context bundle"], "persistent": ["events through injected sink"]}, ["EpisodeEngine.run", "EpisodeEngine.spawn", "ModelPort", "KernelPort-like dispatch"], ["runtime"], ["domain", "ports", "kernel"], ["observe/compile → model propose → parse/recover → dispatch/finish → emit terminal"], ["Malformed proposals use bounded protocol recovery", "Budget/turn exhaustion terminates", "Agency never grades itself"], ["No independent authority; effect proposals cross kernel"], ["Protocol decoders, context policies and model ports"], ["E-B-019", "E-B-020", "E-B-026"], ["test/agency/test_episode.py", "test/agency/test_protocol_recovery.py"]),
        subsystem("SUB-B-05", "Causal state, artifacts and persistence", "Persist causal facts and artifacts; reconstruct projections, recovery and checkpoints.", "IMPLEMENTED", ["vanguard/packages/domain/ledger/", "vanguard/packages/runtime/ledger_emitter.py", "vanguard/packages/runtime/ledger/", "vanguard/packages/runtime/checkpoints.py", "vanguard/packages/runtime/artifacts.py", "vanguard/packages/adapters/stores/"], ["LedgerEmitter", "SqliteEventStore", "FileBlobStore", "RecoveryScanner", "CheckpointManager"], ["Role-scoped event writing", "Digest chain and ordering", "SQLite-WAL durability", "Content-addressed artifacts", "Cold fold/checkpoint recovery"], ["Effect policy", "Model/tool choice", "Client presentation"], {"authoritative": ["ordered event envelopes", "content-addressed blob bytes"], "derived": ["LedgerState", "AgentView", "indexes", "checkpoints"], "transient": ["emitter chain cursor", "in-memory store option"], "persistent": ["SQLite events", "blob files"]}, ["EventStorePort", "BlobStorePort", "mhf.event/1|2 readers", "mhf.trajectory/2 writer"], ["kernel", "agency", "runtime", "services", "clients"], ["domain", "ports", "adapters"], ["event creation → role check → envelope/digest/sequence → store append → reducer/projection consumption"], ["Append failure is typed; pre-effect intent failure blocks dispatch", "Open intent/child is undeterminable", "Checkpoint failure falls back to full fold", "Backup/restore rechecks integrity"], ["Writer-role ownership enforced for privileged kinds"], ["Store ports, projection reducers, capture policies"], ["E-B-008", "E-B-009", "E-B-010", "E-B-027", "E-B-028", "E-B-029", "E-B-030", "E-B-031"], ["test/contracts/test_b3_wal_recovery.py", "test/falsifiers/test_rf25_cold_continuation.py"]),
        subsystem("SUB-B-06", "Runtime composition and session lifecycle", "Compile manifests, activate components, bind profiles/adapters and run one canonical session.", "IMPLEMENTED", ["vanguard/packages/runtime/compose.py", "vanguard/packages/runtime/activation.py", "vanguard/packages/runtime/run_plan.py", "vanguard/packages/runtime/bootstrap.py", "vanguard/packages/runtime/root.py", "vanguard/packages/runtime/session.py", "vanguard/packages/runtime/wiring.py"], ["Runtime.compose", "Runtime.execute_profiled", "Runtime.run_composed", "RuntimeBootstrap", "HarnessSession"], ["Composition and identity", "Adapter bootstrap", "Activation/retirement", "Approval suspension/re-entry", "Session lifecycle and result assembly"], ["Pure contract ownership", "Provider implementations", "Client UI"], {"authoritative": ["resolved RunPlan identity for a run"], "derived": ["RunResult", "trajectory", "telemetry"], "transient": ["HarnessSession", "activation handles", "adapter instances"], "persistent": ["delegated to event/blob stores"]}, ["Runtime.execute_profiled", "Runtime.run_composed", "TaskContext", "SessionPorts"], ["application service", "RuntimeService", "child runtime"], ["domain", "ports", "kernel", "agency", "adapters"], ["manifest → FrozenComposition → ActivationPlan → RunPlan → HarnessSession → EpisodeEngine → retirement"], ["Composition/activation fail before ready", "Requested unavailable containment fails closed", "Session recovers existing episode", "Reverse-order teardown records faults"], ["Owns construction, not the authority semantics enforced by kernel/evaluator"], ["BindingResolver, profiles, injected ports, manifests"], ["E-B-021", "E-B-022", "E-B-023", "E-B-024", "E-B-025", "E-B-026"], ["test/runtime/test_composition_root.py", "test/runtime/test_harness_session.py"], uncertainty=["execute_harness remains a tested obsolete public method and should be documented as compatibility-only."]),
        subsystem("SUB-B-07", "Delegation, topology and workflow mechanisms", "Represent and execute nested lineages and sequential topology routing; host isolated workflow experiments.", "PARTIAL", ["vanguard/packages/runtime/delegation.py", "vanguard/packages/runtime/child_runtime.py", "vanguard/packages/runtime/topology.py", "vanguard/packages/runtime/scheduler.py", "vanguard/packages/domain/workflows/", "vanguard/packages/runtime/workflow_scheduler.py", "vanguard/packages/runtime/staged_workflow.py", "vanguard/packages/runtime/transform_runtime.py"], ["SpawnAdapter", "RuntimeChildRunner", "lower_topology", "SequentialScheduler", "WorkflowScheduler", "StagedWorkflowEngine"], ["Mediated recursive child runs", "Authority-free topology lowering", "Sequential readiness", "Isolated artifact-transform workflow execution"], ["Concurrent scheduler", "Independent authority", "A second canonical runtime"], {"authoritative": ["child facts only after ledger append"], "derived": ["topology extensions", "workflow state"], "transient": ["workflow scheduler local event list"], "persistent": ["canonical child events/artifacts; workflow/2 events are not wired to canonical ledger"]}, ["agent.spawn effect", "mhf.topology/1", "mhf.topology/2 isolated values"], ["runtime session"], ["domain", "ports", "kernel/runtime seams"], ["parent proposal → kernel dispatch → SpawnAdapter intent → child run_composed → ChildReturned; topology/1 lowers roles to that path"], ["Open child becomes undeterminable", "Collision/budget/scope failures deny", "Workflow/2 suspends at cycle/node failures"], ["Topology carries no authority; child scope is attenuated"], ["ChildRuntimePort, topology data, transform registry, node executors"], ["E-B-032", "E-B-033", "E-B-034", "E-B-035", "E-B-036", "E-B-055"], ["test/falsifiers/test_rf101_rf112_canonical_recursion.py", "test/workflows/test_workflow_scheduler.py"], uncertainty=["mhf.topology/2 and staged workflow engines have no canonical runtime caller; they are not part of the primary execution path."]),
        subsystem("SUB-B-08", "Memory and governed learning", "Authorize, persist, retrieve and lifecycle-manage memory and immutable compositions.", "IMPLEMENTED", ["vanguard/packages/ports/memory.py", "vanguard/packages/runtime/memory.py", "vanguard/packages/adapters/stores/memory_engine.py", "vanguard/packages/runtime/governance/learning.py", "vanguard/packages/runtime/skill_*.py"], ["MemoryBinding", "DurableMemoryPort", "CompositionRegistry", "CompositionPromotionService"], ["Authorization-before-use", "Category isolation and provenance", "Revocation/retention/GC/backup", "Composition CAS promotion/rollback", "Skill evaluation lifecycle"], ["Kernel memory semantics", "Unmediated model authority", "External acceptance claims"], {"authoritative": ["memory SQLite rows/blob digests", "composition registry head"], "derived": ["search index", "retrieval results", "skill evaluation"], "transient": ["in-memory adapter"], "persistent": ["category SQLite/blob stores", "composition registry"]}, ["KnowledgePort/ExperiencePort/ProjectMemoryPort/SkillLibrary", "MemoryBinding"], ["HarnessSession", "governance services"], ["domain", "ports", "adapters"], ["authorize → validate → rank/dereference → return provenance; generate/evaluate/promote/rollback composition"], ["Missing/revoked authorization denies", "Index can rebuild", "Legal hold blocks GC", "CAS conflict rejects promotion"], ["Authorization port precedes memory access; promotion authorities are separated"], ["Category ports, storage adapters, scoring/evaluation policies"], ["E-B-037", "E-B-038", "E-B-039"], ["test/adapters/test_durable_memory_port.py", "test/runtime/test_governed_learning.py"]),
        subsystem("SUB-B-09", "Evaluation, evidence and assurance", "Capture trajectories and obtain exterior signed evaluation without episode self-grading.", "IMPLEMENTED", ["vanguard/packages/domain/evidence/", "vanguard/packages/runtime/evidence_capture.py", "vanguard/packages/runtime/trajectory.py", "vanguard/packages/runtime/evaluator_gateway.py", "vanguard/packages/adapters/evaluators/", "vanguard/packages/runtime/assurance.py", "vanguard/packages/runtime/reproducibility.py"], ["EvaluatorDaemon", "EvaluatorClient", "record_verdict", "assemble_trajectory", "AssurancePolicy"], ["Exterior verdict execution/signing", "Trajectory/evidence capture", "Assurance and reproducibility assessment", "Verdict ledgering"], ["Episode policy", "Kernel authority", "Milestone acceptance by mechanism presence"], {"authoritative": ["signed verdict bytes and causal evidence facts"], "derived": ["trajectory", "foundation bundle", "reproducibility assessment"], "transient": ["RPC client/server connection"], "persistent": ["ledger verdict/evidence events", "artifact blobs"]}, ["EvaluatorPort", "evaluator daemon CLI", "mhf.trajectory/2"], ["session", "release/evidence tooling"], ["domain", "ports", "adapters", "runtime state"], ["terminal run ref → exterior evaluator → signed verdict → gateway validation → VerdictRecorded → trajectory"], ["Absent evaluator stays absent", "Forged/unbound verdict fails", "Required capture failure is terminal where configured"], ["Evaluator signature is distinct authority; gateway alone writes verdict facts"], ["Evaluator adapters, capture policies, evidence sinks"], ["E-B-040", "E-B-041", "E-B-051"], ["test/adapters/test_evaluator_signing.py", "test/trust/test_spine.py"]),
        subsystem("SUB-B-10", "Packs, manifests and plugin lifecycle", "Supply task-domain composition, tools, policies and plugin activation outside the trusted core.", "IMPLEMENTED", ["packs/", "vanguard/packages/agency/manifests/", "vanguard/packages/runtime/registry/", "vanguard/packages/adapters/bindings/"], ["Runtime.compose", "ManifestRegistry", "Plugin lifecycle FSM", "BindingResolver"], ["Domain-specific harness data", "Tool and policy declarations", "Plugin validation/activation/retirement", "Binding factories"], ["Kernel changes", "Independent event writer", "Runtime authority"], {"authoritative": ["frozen composition identity for a run"], "derived": ["activation plan", "tool schemas", "skill cards"], "transient": ["activation handles"], "persistent": ["manifest/artifact files; lifecycle facts in ledger"]}, ["mhf.manifest/2", "pack harness.yaml/plugin.yaml", "five SPIs"], ["runtime composition", "application defaults"], ["domain", "ports", "runtime registry/adapters"], ["load/validate → compose/freeze → plan activation → materialize handles → quiesce/retire"], ["Unknown/unread components fail composition", "Activation failure tears down", "Plugin faults are recorded"], ["Plugins are untrusted; activation does not grant effect authority"], ["New packs, manifest components, bindings, SPIs"], ["E-B-012", "E-B-021", "E-B-050", "E-B-053", "E-B-054"], ["test/agency/test_manifest_loader.py", "test/runtime/test_plugin_full_lifecycle.py"]),
        subsystem("SUB-B-11", "Application, service and client surfaces", "Expose runtime commands, queries, event streams and visual clients without duplicating substrate authority.", "PARTIAL", ["vanguard/packages/runtime/app_service.py", "vanguard/packages/runtime/cli.py", "vanguard/packages/runtime/entrypoint.py", "vanguard/packages/runtime/service/", "vanguard/packages/runtime/studio/", "vanguard/clients/"], ["ApplicationService", "RuntimeService", "RuntimeServer", "StudioGatewayServer", "LiveRuntimeClient", "COMMANDS"], ["Python CLI", "TS vg CLI/TUI", "vg.4 command/query/stream service", "HTTP Studio gateway", "client-side projections"], ["Kernel decisions", "Canonical state mutation outside runtime", "Schema ownership outside reference contracts"], {"authoritative": ["none; commands delegate to runtime and views fold events"], "derived": ["RunSnapshot", "TUI/Studio stores", "diagnostics"], "transient": ["active run threads", "socket subscriptions"], "persistent": ["service idempotency inbox and canonical event store"]}, ["Python console scripts", "vg binary", "vg.4 UDS", "Studio HTTP gateway", "@vanguard/client-core exports"], ["operators and external clients"], ["runtime", "adapters", "schemas"], ["request → validate/idempotency/CAS → runtime execute_profiled → event stream/result projection"], ["Typed wire errors", "socket size/permission controls", "run thread records failed/cancelled", "default live StartRun profile mismatch currently fails bootstrap"], ["Clients hold no effect authority; signed approvals cross explicit service boundary"], ["Transport adapters, headless/replay/scenario clients, UI projections"], ["E-B-002", "E-B-003", "E-B-004", "E-B-005", "E-B-006", "E-B-042", "E-B-043", "E-B-044", "E-B-045", "E-B-046", "E-B-047", "E-B-048", "E-B-049", "E-B-052"], ["test/runtime/test_app_service_and_cli.py", "test/runtime/test_runtime_service.py", "vanguard/clients/cli/test/commands.test.ts"], uncertainty=["Python and TypeScript CLIs overlap without a single shared command registry.", "Default daemon StartRun payload/profile is incompatible."]),
        subsystem("SUB-B-12", "Schemas and generated wire contracts", "Own exact JSON wire shapes, compatibility readers and conformance vectors.", "IMPLEMENTED", ["schemas/", "vanguard/packages/domain/wire/", "vanguard/clients/client-core/src/contract/"], ["parse_wire", "types_gen", "runtime-service.schema.json", "parseDaemonLine"], ["JSON Schema contracts", "Golden/negative vectors", "Python/TypeScript readers", "Compatibility versions"], ["Proof that every schema behavior is used", "Runtime policy", "Tutorials"], {"authoritative": ["wire shape where tests bind schema/code parity"], "derived": ["generated Python types", "client types"], "transient": [], "persistent": ["schema/vector files"]}, ["mhf.* schemas", "vg.4 runtime-service", "v4 readers/vectors"], ["domain parsers", "runtime service", "clients", "tests"], ["jsonschema dependency and generated/handwritten readers"], ["schema/vector → parser validation → typed value → producer/consumer"], ["Unknown fields/versions fail closed where strict readers are used", "Compatibility readers preserve older rows"], ["Contracts carry data, not executable authority"], ["New schema versions require readers/vectors"], ["E-B-008", "E-B-044", "E-B-049", "E-B-050", "E-B-051"], ["test/contracts/test_schema_catalog_authority.py", "test/contracts/test_runtime_service_vectors.py"], uncertainty=["The inventory contains hundreds of schema vector files; Block B maps schema families and major producer/consumer paths, not each vector as an architectural subsystem."]),
    ]

    dependencies = [
        {"from": "SUB-B-02", "to": "SUB-B-01", "kind": "imports", "direction": "ports -> domain", "evidence_ids": ["E-B-017"]},
        {"from": "SUB-B-03", "to": "SUB-B-01", "kind": "imports", "direction": "kernel -> domain", "evidence_ids": ["E-B-013", "E-B-017"]},
        {"from": "SUB-B-03", "to": "SUB-B-02", "kind": "imports", "direction": "kernel -> ports", "evidence_ids": ["E-B-013", "E-B-017"]},
        {"from": "SUB-B-04", "to": "SUB-B-03", "kind": "dispatches-through", "direction": "agency -> kernel", "evidence_ids": ["E-B-019"]},
        {"from": "SUB-B-06", "to": "SUB-B-04", "kind": "constructs", "direction": "runtime -> agency", "evidence_ids": ["E-B-024", "E-B-026"]},
        {"from": "SUB-B-06", "to": "SUB-B-03", "kind": "wires", "direction": "runtime -> kernel", "evidence_ids": ["E-B-026"]},
        {"from": "SUB-B-06", "to": "SUB-B-05", "kind": "persists-via", "direction": "runtime -> causal-state", "evidence_ids": ["E-B-026", "E-B-027"]},
        {"from": "SUB-B-06", "to": "SUB-B-10", "kind": "composes", "direction": "runtime -> packs/manifests", "evidence_ids": ["E-B-021"]},
        {"from": "SUB-B-06", "to": "SUB-B-09", "kind": "evaluates-via", "direction": "runtime -> evaluation", "evidence_ids": ["E-B-041"]},
        {"from": "SUB-B-07", "to": "SUB-B-06", "kind": "re-enters", "direction": "child runtime -> canonical runtime", "evidence_ids": ["E-B-033"]},
        {"from": "SUB-B-08", "to": "SUB-B-02", "kind": "implements-ports", "direction": "memory adapters -> ports", "evidence_ids": ["E-B-037", "E-B-038"]},
        {"from": "SUB-B-10", "to": "SUB-B-02", "kind": "declares-spis", "direction": "packs -> ports", "evidence_ids": ["E-B-012", "E-B-053"]},
        {"from": "SUB-B-11", "to": "SUB-B-06", "kind": "invokes", "direction": "clients/services -> runtime", "evidence_ids": ["E-B-042", "E-B-045", "E-B-048"]},
        {"from": "SUB-B-11", "to": "SUB-B-12", "kind": "conforms-to", "direction": "clients/services -> schemas", "evidence_ids": ["E-B-044", "E-B-049"]},
        {"from": "SUB-B-05", "to": "SUB-B-02", "kind": "implements-ports", "direction": "stores -> ports", "evidence_ids": ["E-B-028", "E-B-031"]},
    ]
    for row in dependencies:
        row["analysis_subject_sha"] = ANALYSIS_SHA

    flows = [
        {"flow_id": "FLOW-B-001", "name": "Python product bootstrap", "status": "IMPLEMENTED", "steps": ["vanguard console script", "runtime.cli", "ApplicationService.run", "profile/model/state resolution", "Runtime.execute_profiled", "RuntimeBootstrap.build", "Runtime.run_composed", "ready session"], "evidence_ids": ["E-B-002", "E-B-042", "E-B-043", "E-B-024", "E-B-025"]},
        {"flow_id": "FLOW-B-002", "name": "Canonical request execution", "status": "IMPLEMENTED", "steps": ["manifest parse/compose", "activation plan", "run plan identity", "HarnessSession.begin_episode", "EpisodeEngine propose", "Kernel.dispatch", "adapter effect", "ledger/artifact capture", "exterior evaluation", "EpisodeCompleted/trajectory/result"] , "evidence_ids": ["E-B-021", "E-B-022", "E-B-023", "E-B-024", "E-B-026", "E-B-013", "E-B-027", "E-B-041"]},
        {"flow_id": "FLOW-B-003", "name": "Agent/episode lifecycle", "status": "IMPLEMENTED", "steps": ["TaskContext identity/scope", "EpisodeStarted", "event-derived prior state", "context compile", "sequential turns", "approval suspension/re-entry", "terminal outcome", "projection/reconstruction"] , "evidence_ids": ["E-B-019", "E-B-020", "E-B-026", "E-B-010"]},
        {"flow_id": "FLOW-B-004", "name": "Event lifecycle", "status": "IMPLEMENTED", "steps": ["role emits kernel/runtime fact", "writer ownership check", "mhf.event/2 envelope", "sequence + prev digest", "SQLite append", "read by range", "reducer/projection", "client stream"] , "evidence_ids": ["E-B-027", "E-B-008", "E-B-028", "E-B-009", "E-B-045"]},
        {"flow_id": "FLOW-B-005", "name": "Artifact lifecycle", "status": "IMPLEMENTED", "steps": ["authorized capture/transform", "sha256 addressing", "blob put", "ArtifactCreated/reference fact", "digest-verified get", "trajectory/topology provenance"] , "evidence_ids": ["E-B-031", "E-B-051", "E-B-055"]},
        {"flow_id": "FLOW-B-006", "name": "Cold recovery and resume", "status": "IMPLEMENTED", "steps": ["open file-backed store", "read ordered prior episode", "fold LedgerState", "reconcile open intents/children", "emit RunRecovered", "resume remaining turns", "checkpoint used only after pin/digest checks; otherwise cold fold"] , "evidence_ids": ["E-B-026", "E-B-028", "E-B-029", "E-B-030"]},
        {"flow_id": "FLOW-B-007", "name": "Recursive delegation", "status": "IMPLEMENTED", "steps": ["model proposes agent.spawn", "kernel authorizes/reserves", "SpawnAdapter derives/persists child identity", "RuntimeChildRunner attenuates and re-enters run_composed", "child events/artifacts", "ChildReturned", "parent consumes result"] , "evidence_ids": ["E-B-019", "E-B-032", "E-B-033"]},
        {"flow_id": "FLOW-B-008", "name": "Live service/client", "status": "PARTIAL", "steps": ["TS LiveRuntimeClient", "vg.4 UDS command", "frame validation/idempotency/CAS", "RuntimeService worker thread", "execute_profiled", "event subscription/result"], "evidence_ids": ["E-B-044", "E-B-045", "E-B-046", "E-B-048"], "caveat": "Default StartRun omits profileId and service supplies unsupported code-default."},
        {"flow_id": "FLOW-B-009", "name": "Memory and governed learning", "status": "IMPLEMENTED", "steps": ["scoped MemoryBinding authorization", "category storage", "authorization-before-ranking", "provenance-bearing retrieval", "candidate composition", "separate evaluation", "CAS promotion", "rollback"] , "evidence_ids": ["E-B-037", "E-B-038", "E-B-039"]},
        {"flow_id": "FLOW-B-010", "name": "Isolated workflow/2", "status": "PARTIAL", "steps": ["WorkflowSpec", "local reducer state", "sequential node selection", "TransformRuntime or injected executor", "local event list", "outcome"], "evidence_ids": ["E-B-035", "E-B-055"], "caveat": "No canonical runtime or LedgerEmitter integration."},
    ]
    for row in flows:
        row["analysis_subject_sha"] = ANALYSIS_SHA

    interfaces = [
        {"interface_id": "IF-B-001", "owner": "SUB-B-11", "kind": "python-console", "name": "vanguard", "target": "vanguard.packages.runtime.cli:main", "status": "IMPLEMENTED", "evidence_ids": ["E-B-002", "E-B-043"]},
        {"interface_id": "IF-B-002", "owner": "SUB-B-09", "kind": "python-console", "name": "vanguard-evaluator", "target": "vanguard.packages.adapters.evaluators.daemon:main", "status": "IMPLEMENTED", "evidence_ids": ["E-B-002", "E-B-040"]},
        {"interface_id": "IF-B-003", "owner": "SUB-B-11", "kind": "python-console", "name": "vanguard-daemon", "target": "vanguard.packages.runtime.service.server:main", "status": "IMPLEMENTED", "evidence_ids": ["E-B-002", "E-B-046"]},
        {"interface_id": "IF-B-004", "owner": "SUB-B-11", "kind": "python-console", "name": "vanguard-studio", "target": "vanguard.packages.runtime.service.studio_gateway:main", "status": "IMPLEMENTED", "evidence_ids": ["E-B-002"]},
        {"interface_id": "IF-B-005", "owner": "SUB-B-11", "kind": "npm-bin", "name": "vg", "target": "vanguard/clients/cli/src/main.tsx", "status": "IMPLEMENTED", "evidence_ids": ["E-B-004", "E-B-047"]},
        {"interface_id": "IF-B-006", "owner": "SUB-B-11", "kind": "cli-commands", "name": "vg command registry", "target": "run, code, explain, doctor, approve, resume, trace, why, daemon, init, agent, composition, event, artifact, schema, lineage", "status": "IMPLEMENTED", "evidence_ids": ["E-B-047"]},
        {"interface_id": "IF-B-007", "owner": "SUB-B-11", "kind": "cli-commands", "name": "vanguard backend CLI", "target": "init, doctor, cassette record/replay, run, resume, status, events, artifacts", "status": "IMPLEMENTED", "evidence_ids": ["E-B-043"]},
        {"interface_id": "IF-B-008", "owner": "SUB-B-11", "kind": "wire-service", "name": "RuntimeService vg.4", "target": "StartRun, GetRun, ListRuns, StreamEvents, Cancel, Checkpoint, Resume, ResolveApproval, RecordCorrection, ExplainArtifact, GetCapabilities", "status": "PARTIAL", "evidence_ids": ["E-B-044", "E-B-045", "E-B-049"], "caveat": "Default live StartRun profile is incompatible."},
        {"interface_id": "IF-B-009", "owner": "SUB-B-06", "kind": "python-api", "name": "Runtime.execute_profiled", "target": "canonical product compose/bootstrap/run", "status": "IMPLEMENTED", "evidence_ids": ["E-B-024", "E-B-025"]},
        {"interface_id": "IF-B-010", "owner": "SUB-B-06", "kind": "python-api", "name": "Runtime.run_composed", "target": "already-composed and child-run seam", "status": "IMPLEMENTED", "evidence_ids": ["E-B-024", "E-B-033"]},
        {"interface_id": "IF-B-011", "owner": "SUB-B-06", "kind": "python-api", "name": "Runtime.execute_harness", "target": "legacy compatibility/evidence path", "status": "OBSOLETE", "evidence_ids": ["E-B-024"]},
        {"interface_id": "IF-B-012", "owner": "SUB-B-02", "kind": "ports", "name": "core ports", "target": "model, environment, sandbox, evaluator, event/blob/index stores, child runtime, memory, determinism", "status": "IMPLEMENTED", "evidence_ids": ["E-B-011", "E-B-012", "E-B-037"]},
        {"interface_id": "IF-B-013", "owner": "SUB-B-10", "kind": "manifest", "name": "mhf.manifest/2", "target": "canonical composition graph", "status": "IMPLEMENTED", "evidence_ids": ["E-B-021", "E-B-050"]},
        {"interface_id": "IF-B-014", "owner": "SUB-B-05", "kind": "schema", "name": "mhf.event/1|2", "target": "causal event envelopes", "status": "IMPLEMENTED", "evidence_ids": ["E-B-008", "E-B-027"]},
        {"interface_id": "IF-B-015", "owner": "SUB-B-09", "kind": "schema", "name": "mhf.trajectory/1|2", "target": "run trajectory evidence", "status": "IMPLEMENTED", "evidence_ids": ["E-B-051"]},
        {"interface_id": "IF-B-016", "owner": "SUB-B-07", "kind": "schema", "name": "mhf.topology/1", "target": "authority-free topology lowering", "status": "IMPLEMENTED", "evidence_ids": ["E-B-034"]},
        {"interface_id": "IF-B-017", "owner": "SUB-B-07", "kind": "python-api", "name": "mhf.topology/2 WorkflowScheduler", "target": "isolated workflow DAG", "status": "PARTIAL", "evidence_ids": ["E-B-035"]},
        {"interface_id": "IF-B-018", "owner": "SUB-B-11", "kind": "npm-library", "name": "@vanguard/client-core", "target": "contracts, transports, signers, projections and use cases", "status": "IMPLEMENTED", "evidence_ids": ["E-B-005", "E-B-048"]},
        {"interface_id": "IF-B-019", "owner": "SUB-B-11", "kind": "browser-ui", "name": "@vanguard/studio", "target": "React event-projection studio", "status": "IMPLEMENTED", "evidence_ids": ["E-B-006"]},
        {"interface_id": "IF-B-020", "owner": "SUB-B-01", "kind": "python-package", "name": "vanguard.packages.domain", "target": "curated __all__", "status": "IMPLEMENTED", "evidence_ids": ["E-B-007"]},
        {"interface_id": "IF-B-021", "owner": "SUB-B-02", "kind": "python-package", "name": "vanguard.packages.ports", "target": "curated __all__ plus module protocols", "status": "IMPLEMENTED", "evidence_ids": ["E-B-011"]},
        {"interface_id": "IF-B-022", "owner": "SUB-B-03", "kind": "python-package", "name": "vanguard.packages.kernel", "target": "curated __all__", "status": "IMPLEMENTED", "evidence_ids": ["E-B-013"]},
        {"interface_id": "IF-B-023", "owner": "SUB-B-04", "kind": "python-package", "name": "vanguard.packages.agency", "target": "curated __all__", "status": "IMPLEMENTED", "evidence_ids": ["E-B-019"]},
        {"interface_id": "IF-B-024", "owner": "SUB-B-06", "kind": "python-namespace", "name": "vanguard.packages.runtime", "target": "module-level imports; no package __init__.py export surface", "status": "PARTIAL", "evidence_ids": ["E-B-024"], "caveat": "Public API stability is module-path based rather than curated at package root."},
    ]
    for row in interfaces:
        row["analysis_subject_sha"] = ANALYSIS_SHA

    invariants = [
        {"invariant_id": "INV-B-001", "statement": "Lower-layer dependency direction is enforced: domain <- ports <- kernel <- agency <- runtime, with adapters behind ports.", "scope": ["SUB-B-01", "SUB-B-02", "SUB-B-03", "SUB-B-04", "SUB-B-06"], "evidence_ids": ["E-B-017"], "validation": "check_boundaries.py PASS across 453 source files", "counterexample_search": "AST import scan performed by linter; no forbidden edge found.", "confidence": "high"},
        {"invariant_id": "INV-B-002", "statement": "Kernel/domain remain domain-blind and kernel stays within 1438 logical LOC.", "scope": ["SUB-B-01", "SUB-B-03"], "evidence_ids": ["E-B-016", "E-B-018"], "validation": "domain blindness PASS; TCB 1384/1438 PASS", "counterexample_search": "Scanned tokens/imports and counted every kernel file.", "confidence": "high"},
        {"invariant_id": "INV-B-003", "statement": "Privileged effects persist intent before physical dispatch and release leases before terminal emission.", "scope": ["SUB-B-03", "SUB-B-05"], "evidence_ids": ["E-B-013", "E-B-027"], "validation": "kernel dispatch tests PASS", "counterexample_search": "Reviewed every guarded exit and exception branch.", "confidence": "high"},
        {"invariant_id": "INV-B-004", "statement": "Child scopes never widen actions, resources, constraints, depth or network policy.", "scope": ["SUB-B-03", "SUB-B-07"], "evidence_ids": ["E-B-014", "E-B-032"], "validation": "attenuation and recursion falsifiers PASS", "counterexample_search": "Tested explicit widening and undefined selector relations.", "confidence": "high"},
        {"invariant_id": "INV-B-005", "statement": "Only usd_micros, millis, tokens and bytes are additive budgets; turns/depth are structural ceilings.", "scope": ["SUB-B-03", "SUB-B-07"], "evidence_ids": ["E-B-015"], "validation": "budget and governor concurrency tests PASS", "counterexample_search": "Governor rejects offered non-additive dimensions.", "confidence": "high"},
        {"invariant_id": "INV-B-006", "statement": "Causal state is reconstructed by folding durable ordered events; checkpoints are discardable verified caches.", "scope": ["SUB-B-05"], "evidence_ids": ["E-B-009", "E-B-028", "E-B-030"], "validation": "cold continuation/checkpoint tests PASS", "counterexample_search": "Corrupt/mismatched checkpoints fall back to cold fold.", "confidence": "high"},
        {"invariant_id": "INV-B-007", "statement": "Privileged event kinds have role-scoped writer ownership and new production envelopes use mhf.event/2.", "scope": ["SUB-B-05", "SUB-B-09"], "evidence_ids": ["E-B-027"], "validation": "event writer tests PASS", "counterexample_search": "Attempted wrong-role and deprecated-kind writes in tests.", "confidence": "high"},
        {"invariant_id": "INV-B-008", "statement": "Canonical runtime turns are sequential; topology/1 lowers to ordinary sequential spawn rather than granting authority.", "scope": ["SUB-B-04", "SUB-B-06", "SUB-B-07"], "evidence_ids": ["E-B-019", "E-B-024", "E-B-034"], "validation": "topology lowering/execution tests PASS", "counterexample_search": "Searched canonical runtime for concurrent scheduler activation; none found.", "confidence": "high"},
        {"invariant_id": "INV-B-009", "statement": "Exterior evaluator authority is separate from episode execution and alone writes signed verdict facts.", "scope": ["SUB-B-09"], "evidence_ids": ["E-B-040", "E-B-041"], "validation": "evaluator signing and trust-spine tests PASS", "counterexample_search": "Searched agency for evaluator signing/imports; none found.", "confidence": "high"},
        {"invariant_id": "INV-B-010", "statement": "Memory retrieval requires scoped authorization before ranking and dereference.", "scope": ["SUB-B-08"], "evidence_ids": ["E-B-037", "E-B-038"], "validation": "memory security falsifiers PASS", "counterexample_search": "Reviewed recall path and denied/revoked cases.", "confidence": "high"},
    ]
    for row in invariants:
        row["analysis_subject_sha"] = ANALYSIS_SHA

    unresolved = [
        {"unresolved_id": "UNR-B-001", "severity": "high", "subsystem": "SUB-B-11", "finding": "Default TypeScript live StartRun does not send profileId, while RuntimeService defaults to unsupported code-default.", "status": "CONTRADICTED", "evidence_ids": ["E-B-045", "E-B-048", "E-B-052"], "confidence": "high", "next_action": "Block D must document the defect; a separately authorized engineering packet should align client payload/service default and add a real daemon-launch contract test."},
        {"unresolved_id": "UNR-B-002", "severity": "medium", "subsystem": "SUB-B-07", "finding": "mhf.topology/2 WorkflowScheduler and StagedWorkflowEngine are isolated, tested mechanisms with no canonical runtime caller or canonical ledger writer.", "status": "PARTIAL", "evidence_ids": ["E-B-035", "E-B-036", "E-B-055"], "confidence": "high", "next_action": "Document as isolated partial surfaces; product authority must decide integration, retirement or continued experiment outside Blocks B/C."},
        {"unresolved_id": "UNR-B-003", "severity": "medium", "subsystem": "SUB-B-11", "finding": "Python vanguard and TypeScript vg expose overlapping, non-identical command sets and no shared command registry.", "status": "PARTIAL", "evidence_ids": ["E-B-043", "E-B-047"], "confidence": "high", "next_action": "Reference both exact surfaces and make no claim of command parity; future product ownership belongs to TARGET reconciliation."},
        {"unresolved_id": "UNR-B-004", "severity": "low", "subsystem": "SUB-B-06", "finding": "Runtime.execute_harness remains public and tested although explicitly retired from production callers.", "status": "OBSOLETE", "evidence_ids": ["E-B-024"], "confidence": "high", "next_action": "Document as compatibility/evidence-only and link product users to execute_profiled; removal needs separate engineering/evidence governance."},
        {"unresolved_id": "UNR-B-005", "severity": "low", "subsystem": "SUB-B-11", "finding": "runtime and adapters are namespace packages without curated package-root exports, so module paths act as de facto public surfaces.", "status": "UNRESOLVED", "evidence_ids": ["E-B-024"], "confidence": "medium", "next_action": "Block D should state supported entry points and avoid promising stability for every importable module."},
        {"unresolved_id": "UNR-B-006", "severity": "low", "subsystem": "SUB-B-12", "finding": "Hundreds of schema/vector files include compatibility and negative corpora; not every individual vector has a unique production producer/consumer.", "status": "UNRESOLVED", "evidence_ids": ["E-B-049", "E-B-050", "E-B-051"], "confidence": "high", "next_action": "Reference schema families and machine catalogs; do not create one documentation page per schema/vector."},
        {"unresolved_id": "UNR-B-007", "severity": "low", "subsystem": "SUB-B-00", "finding": "Root-level benchmark/status Markdown governance remains unclassified.", "status": "UNRESOLVED", "evidence_ids": ["E-B-001"], "confidence": "high", "next_action": "Carry to the later legacy loss audit; it does not affect AS_BUILT architecture."},
        {"unresolved_id": "UNR-B-008", "severity": "low", "subsystem": "SUB-B-11", "finding": "vanguard/packages/apps contains only an empty package marker.", "status": "PARTIAL", "evidence_ids": ["E-B-017"], "confidence": "high", "next_action": "Exclude from a standalone subsystem page; treat as a reserved client slot until implementation exists."},
    ]
    for row in unresolved:
        row["analysis_subject_sha"] = ANALYSIS_SHA

    root_coverage = [
        {"root": "vanguard/packages/domain", "assignment": "SUB-B-01", "disposition": "assigned"},
        {"root": "vanguard/packages/ports", "assignment": "SUB-B-02", "disposition": "assigned"},
        {"root": "vanguard/packages/kernel", "assignment": "SUB-B-03", "disposition": "assigned"},
        {"root": "vanguard/packages/agency", "assignment": "SUB-B-04 and SUB-B-10", "disposition": "assigned"},
        {"root": "vanguard/packages/runtime", "assignment": "SUB-B-05 through SUB-B-11 by responsibility", "disposition": "assigned"},
        {"root": "vanguard/packages/adapters", "assignment": "SUB-B-05, SUB-B-08, SUB-B-09 and binding implementations", "disposition": "assigned"},
        {"root": "vanguard/packages/apps", "assignment": "UNR-B-008", "disposition": "explicitly excluded: empty reserved slot"},
        {"root": "vanguard/clients", "assignment": "SUB-B-11", "disposition": "assigned"},
        {"root": "packs", "assignment": "SUB-B-10", "disposition": "assigned"},
        {"root": "schemas", "assignment": "SUB-B-12", "disposition": "assigned"},
        {"root": "containers", "assignment": "SUB-B-09 and adapter deployment evidence", "disposition": "assigned as deployment/isolation support, not a runtime subsystem"},
    ]

    block_b_gate = {
        "verdict": "PASS", "record": "BLOCK B EXIT GATE: PASS",
        "criteria": [
            {"criterion": i + 1, "passed": True, "evidence": text}
            for i, text in enumerate([
                "All significant production roots assigned or apps explicitly excluded.",
                "All four Python scripts, vg npm bin, public runtime APIs and service commands mapped.",
                "Bootstrap, primary execution, agent, event, artifact, recovery, delegation, service and memory flows traced.",
                "Twelve responsibility-based subsystem boundaries cite implementation and tests.",
                "Major public interfaces have one subsystem owner.",
                "Authoritative, derived, transient and persistent state identified per subsystem.",
                "Observed dependency direction recorded and boundary linter passes.",
                "Failure, undeterminacy, recovery, replay and checkpoint fallbacks represented.",
                "Ten invariants include evidence and counterexample searches.",
                "Block A entry-point/workspace gaps resolved; non-architectural legacy gap carried forward.",
                "No AS_BUILT claim uses historical documentation as evidence.",
                "TARGET observations are excluded from AS_BUILT claims.",
                "Material unsupported claims: zero.",
                "All unresolved findings have severity, evidence, confidence and next action.",
            ])
        ],
        "unsupported_material_claims": 0,
    }
    architecture = {
        "artifact": "AS_BUILT architecture reconstruction evidence",
        "analysis_subject_sha": ANALYSIS_SHA, "current_reconstruction_branch": current_branch,
        "current_reconstruction_head": current_head,
        "implementation_drift_check": {"changed_paths_since_subject": changed, "implementation_relevant_changes": relevant_drift, "result": "PASS"},
        "generation_review_context": {"block": "B", "method": "code-first targeted inspection plus deterministic manifests/AST/search and executable tests", "historical_documentation_used_as_implementation_evidence": False, "canonical_documentation_written": False},
        "architecture_summary": "A Python-first event-sourced agentic runtime composes manifest-defined packs into a bounded sequential EpisodeEngine. A small domain-blind kernel mediates effects and typed resources; runtime owns composition, lifecycle and the single ledger writer; adapters implement model, environment, sandbox, evaluator and store ports; recursive roles re-enter the same runtime; Python/TypeScript clients consume application/service boundaries.",
        "production_root_coverage": root_coverage,
        "subsystem_ids": [row["subsystem_id"] for row in subsystems],
        "major_flow_ids": [row["flow_id"] for row in flows],
        "major_invariant_ids": [row["invariant_id"] for row in invariants],
        "test_evidence": {"kernel": "97 passed", "agency": "121 passed", "contracts": "416 passed, 1 skipped", "focused_runtime_memory_workflow": "112 passed, 1 skipped", "architecture_linters": ["boundaries PASS", "TCB 1384/1438 PASS", "domain blindness PASS", "isolation PASS", "duplication PASS"]},
        "block_a_gap_disposition": {"gap-001": "resolved in interfaces IF-B-001..004", "gap-002": "resolved in IF-B-005..006, IF-B-018..019 and CLM-B-003", "gap-003": "resolved by running five architecture/security linters", "gap-004": "carried to UNR-B-007; later legacy loss audit", "gap-005": "not applicable until authored candidate metadata; Block C defines validation requirements"},
        "exit_gate": block_b_gate,
    }

    dump_json("as-built-architecture.json", architecture)
    dump_jsonl("as-built-subsystems.jsonl", subsystems)
    dump_jsonl("as-built-evidence-map.jsonl", evidence_rows)
    dump_jsonl("as-built-claims.jsonl", claims)
    dump_jsonl("as-built-dependencies.jsonl", dependencies)
    dump_jsonl("as-built-flows.jsonl", flows)
    dump_jsonl("as-built-interfaces.jsonl", interfaces)
    dump_jsonl("as-built-invariants.jsonl", invariants)
    dump_jsonl("as-built-unresolved.jsonl", unresolved)

    pages = [
        page("candidate-docs/README.md", "nav.home", "navigation", "Orient audiences and route them to canonical owners.", ["newcomer", "operator", "contributor"], ["documentation authority explanation", "audience reading paths", "canonical navigation"], ["architecture details", "commands", "requirements", "current status"], "AS_BUILT", ["CLM-B-001", "CLM-B-017", "CLM-B-020"], ["arch.system.overview", "guide.getting-started", "ref.commands", "spec.core"], ["What this evidence-backed candidate describes", "Choose a path", "Truth planes and status labels", "Canonical owner map"], "120-200 lines; navigation only", [], ["metadata", "links", "canonical IDs", "no duplicated durable facts"], "BLOCK_D"),
        page("candidate-docs/SPEC.md", "spec.core", "normative", "Own the compact normative product contract after TARGET reconciliation.", ["implementer", "architect", "reviewer"], ["normative requirements and invariant navigation"], ["AS_BUILT narrative", "tutorials", "current work"], "TARGET_DEPENDENT", [], ["arch.system.overview", "decision.index"], ["Deferred until Block E TARGET reconciliation"], "Deferred; scope set after authority reconciliation", [], ["normative authority traceability", "governance ratification"], "DEFERRED_TO_BLOCK_E", True),
        page("candidate-docs/architecture/overview.md", "arch.system.overview", "architecture", "Give the smallest complete AS_BUILT system map and dependency direction.", ["newcomer", "architect", "AI retriever"], ["system boundary", "subsystem responsibility map", "dependency direction", "primary flow index"], ["exact interfaces", "requirements", "procedures"], "AS_BUILT", ["CLM-B-004", "CLM-B-017", "CLM-B-020"], ["arch.runtime.execution", "arch.trust.kernel", "arch.state.causal"], ["Scope and SHA", "Subsystem map", "Dependency direction", "Primary flow", "Known partial/obsolete surfaces"], "250-400 lines", ["one derived subsystem/dependency diagram"], ["code evidence links", "status labels", "diagram parity"], "BLOCK_D"),
        page("candidate-docs/architecture/runtime-execution.md", "arch.runtime.execution", "architecture", "Own canonical composition, bootstrap, activation, session and failure lifecycle.", ["runtime developer", "operator", "architect"], ["compose/activate/run lifecycle", "profile bootstrap boundary", "session ownership", "recovery entry"], ["kernel internals", "event field catalog", "CLI syntax"], "AS_BUILT", ["CLM-B-007", "CLM-B-015", "CLM-B-017", "CLM-B-018", "CLM-B-025"], ["arch.trust.kernel", "arch.agency.turns", "ref.configuration", "ref.manifests"], ["Construction path", "Run identity", "Activation lifecycle", "Session/turn handoff", "Failure and teardown", "Compatibility seam"], "350-550 lines", ["one sequence diagram"], ["trace every step to symbol", "separate obsolete execute_harness"], "BLOCK_D"),
        page("candidate-docs/architecture/kernel.md", "arch.trust.kernel", "architecture", "Own trusted-core responsibilities, boundaries and dispatch behavior.", ["security reviewer", "kernel developer"], ["kernel responsibility boundary", "S1-S12 execution semantics", "capability/budget ownership", "failure semantics"], ["exact event fields", "adapter implementation", "normative law"], "AS_BUILT", ["CLM-B-005", "CLM-B-006", "CLM-B-011", "CLM-B-012", "CLM-B-013", "CLM-B-016", "CLM-B-027"], ["ref.events", "ref.ports", "arch.runtime.execution"], ["Boundary and TCB", "Dispatch sequence", "Capabilities", "Budgets", "Failure/undeterminacy", "Evidence and falsifiers"], "350-550 lines", ["S1-S12 sequence diagram"], ["TCB linter", "boundary linter", "kernel tests"], "BLOCK_D"),
        page("candidate-docs/architecture/agency.md", "arch.agency.turns", "architecture", "Own the generic episode/turn/context behavior.", ["agent-system developer", "pack author"], ["EpisodeEngine lifecycle", "proposal and recovery semantics", "context compilation", "runtime handoff"], ["specific agents/packs", "effect authorization", "model provider details"], "AS_BUILT", ["CLM-B-007", "CLM-B-010"], ["arch.runtime.execution", "arch.orchestration.delegation", "ref.ports"], ["Episode identity", "Sequential turn loop", "Context", "Proposal recovery", "Terminal outcomes"], "250-400 lines", ["turn state diagram"], ["agency tests", "no persistent-agent overclaim"], "BLOCK_D"),
        page("candidate-docs/architecture/causal-state.md", "arch.state.causal", "architecture", "Own events-as-state, projections, persistence, artifact and recovery relationships.", ["runtime developer", "data/recovery reviewer"], ["authoritative vs derived state", "event lifecycle", "artifact relationship", "cold replay/checkpoint semantics"], ["event field lookup", "schema catalog", "retention requirements"], "AS_BUILT", ["CLM-B-008", "CLM-B-009", "CLM-B-010", "CLM-B-015", "CLM-B-019"], ["ref.events", "ref.artifacts", "ref.schemas"], ["Truth model", "Event lifecycle", "Projection ownership", "Artifacts", "Replay/recovery", "Checkpoint proof"], "350-550 lines", ["event/artifact/projection relationship", "recovery sequence"], ["cold continuation tests", "store integrity evidence"], "BLOCK_D"),
        page("candidate-docs/architecture/composition-extensibility.md", "arch.composition.extensibility", "architecture", "Own how manifests, packs, plugins, bindings and adapters compose.", ["pack author", "adapter developer", "architect"], ["composition boundary", "plugin lifecycle", "pack responsibility", "extension taxonomy"], ["exact manifest fields", "step-by-step guides", "kernel policy"], "AS_BUILT", ["CLM-B-021", "CLM-B-026"], ["ref.manifests", "ref.ports", "guide.add-pack-tool", "guide.add-adapter-provider"], ["Extension model", "Composition compiler", "Activation lifecycle", "Packs/tools", "Adapters/providers", "Boundary constraints"], "300-450 lines", ["extension boundary diagram"], ["boundary tests", "manifest tests"], "BLOCK_D"),
        page("candidate-docs/architecture/delegation-topology.md", "arch.orchestration.delegation", "architecture", "Own recursive lineage and topology execution semantics, including isolated workflow drift.", ["agent-system developer", "architect"], ["spawn lifecycle", "child identity/scope/budget", "topology/1 lowering", "workflow/2 partial status"], ["target concurrency", "workflow redesign", "exact schemas"], "AS_BUILT", ["CLM-B-014", "CLM-B-023", "CLM-B-024"], ["arch.agency.turns", "ref.manifests", "theory.agent-substrate"], ["Delegation boundary", "Child lifecycle", "Topology/1", "Sequential scheduler", "Isolated workflow surfaces", "Recovery"], "350-550 lines", ["parent/child sequence", "topology lowering diagram"], ["recursion/topology tests", "PARTIAL labels"], "BLOCK_D"),
        page("candidate-docs/architecture/memory-learning.md", "arch.memory.learning", "architecture", "Own durable memory and governed composition-learning behavior.", ["memory developer", "security reviewer", "architect"], ["memory authority/data flow", "category persistence", "retrieval provenance", "promotion/rollback lifecycle"], ["exact port signatures", "TARGET claims", "operator tutorial"], "AS_BUILT", ["CLM-B-028", "CLM-B-029"], ["ref.artifacts", "ref.ports", "arch.assurance.evaluation"], ["Boundaries", "Authorization before retrieval", "Durability/lifecycle", "Skills", "Composition promotion", "Failure/rollback"], "300-500 lines", ["promotion state diagram"], ["memory security/recovery tests", "no acceptance overclaim"], "BLOCK_D"),
        page("candidate-docs/architecture/assurance-evaluation.md", "arch.assurance.evaluation", "architecture", "Own exterior evaluation, evidence capture and assurance relationships.", ["evaluator developer", "security reviewer", "researcher"], ["evaluation authority boundary", "trajectory/evidence flow", "assurance profile relationship", "absence/failure semantics"], ["schema fields", "milestone status", "normative promotion rules"], "AS_BUILT", ["CLM-B-030", "CLM-B-016", "CLM-B-019"], ["ref.events", "ref.schemas", "ref.configuration"], ["Evaluation boundary", "Signed verdict flow", "Capture and trajectories", "Assurance profiles", "Failure and missingness"], "300-450 lines", ["worker/evaluator/ledger trust diagram"], ["signing/trust tests", "status labels"], "BLOCK_D"),
        page("candidate-docs/architecture/application-interfaces.md", "arch.interfaces.clients", "architecture", "Own the relationship among ApplicationService, RuntimeService, Python/TS CLIs and Studio.", ["client developer", "operator", "architect"], ["application boundary responsibility", "transport relationships", "client projection ownership", "known interface drift"], ["command syntax", "wire fields", "UI guide"], "AS_BUILT", ["CLM-B-020", "CLM-B-022", "CLM-B-031"], ["ref.commands", "ref.runtime-service", "guide.operate-service"], ["Interface map", "Python CLI path", "TS vg paths", "RuntimeService", "Studio", "Known incompatibilities"], "300-450 lines", ["client/transport/runtime diagram"], ["interface tests", "CONTRADICTED default profile visible"], "BLOCK_D"),
        page("candidate-docs/reference/commands.md", "ref.commands", "reference", "Provide exact installed Python and TypeScript command surfaces.", ["operator", "automation author"], ["console scripts", "CLI commands/options/exit semantics", "command surface differences"], ["runtime architecture", "tutorial narrative"], "AS_BUILT", ["CLM-B-002", "CLM-B-003", "CLM-B-020"], ["guide.getting-started", "arch.interfaces.clients"], ["Installed entry points", "vanguard commands", "vg commands", "Exit/output modes", "Known differences"], "250-450 lines", [], ["parser/manifest parity", "CLI tests"], "BLOCK_D"),
        page("candidate-docs/reference/runtime-service.md", "ref.runtime-service", "reference", "Own exact vg.4 commands, frames, errors, sequencing and transport limits.", ["client developer", "service integrator"], ["vg.4 frame contract", "command payloads", "error vocabulary", "idempotency/CAS/stream semantics", "known profile defect"], ["CLI commands", "runtime internals", "approval rationale"], "AS_BUILT", ["CLM-B-022", "CLM-B-031"], ["ref.schemas", "arch.interfaces.clients"], ["Transport", "Frames", "Commands", "Errors", "Ordering/idempotency", "Failure caveats"], "350-600 lines", [], ["schema/Python/TS parity tests", "vector tests"], "BLOCK_D"),
        page("candidate-docs/reference/events.md", "ref.events", "reference", "Own event versions, kinds, envelope fields, writer roles and ordering semantics.", ["runtime developer", "client developer", "auditor"], ["event envelope contract", "event-kind roster link/catalog", "writer ownership", "sequence/digest semantics"], ["event lifecycle explanation", "state projection narrative"], "AS_BUILT", ["CLM-B-008", "CLM-B-009", "CLM-B-011"], ["arch.state.causal", "ref.schemas"], ["Versions", "Envelope", "Kinds and owners", "Ordering/digests", "Compatibility readers"], "350-600 lines", [], ["event coverage", "writer tests", "schema links"], "BLOCK_D"),
        page("candidate-docs/reference/schemas.md", "ref.schemas", "reference", "Route exact schema families to producers, consumers, generated readers and vectors.", ["integrator", "contract developer", "AI retriever"], ["schema family catalog", "producer/consumer map", "generation/vector relationships", "compatibility status"], ["copying every schema", "behavior claims from schema alone"], "AS_BUILT", ["CLM-B-008", "CLM-B-021", "CLM-B-022", "CLM-B-030"], ["ref.events", "ref.runtime-service", "ref.manifests"], ["Authority caveat", "MHF schemas", "vg.4 schemas", "v4 compatibility", "Readers/vectors", "Orphans/unknowns"], "250-450 lines plus generated links", [], ["schema catalog tests", "path resolution", "no behavior overclaim"], "BLOCK_D"),
        page("candidate-docs/reference/configuration.md", "ref.configuration", "reference", "Own execution profiles, environment keys, state paths and model/provider configuration.", ["operator", "deployment integrator"], ["profile presets/aliases", "configuration keys", "state/store locations", "provider selection inputs"], ["setup procedure", "architecture rationale", "secrets"], "AS_BUILT", ["CLM-B-018", "CLM-B-020", "CLM-B-031"], ["guide.getting-started", "arch.runtime.execution"], ["Profiles", "State and persistence", "Model/provider inputs", "Environment variables", "Containment behavior", "Known defaults"], "300-500 lines", [], ["config source links", "profile tests", "no credential values"], "BLOCK_D"),
        page("candidate-docs/reference/ports.md", "ref.ports", "reference", "Own exact port and SPI lookup with implementer mappings.", ["adapter developer", "pack author"], ["port signatures and owners", "five SPI contracts", "implementer/test-double map"], ["adapter procedure", "architecture narrative"], "AS_BUILT", ["CLM-B-004", "CLM-B-021", "CLM-B-026", "CLM-B-028"], ["guide.add-adapter-provider", "guide.add-pack-tool"], ["Core ports", "Memory/child ports", "Five SPIs", "Implementations", "Failure types"], "300-500 lines", [], ["protocol tests", "boundary linter"], "BLOCK_D"),
        page("candidate-docs/reference/manifests.md", "ref.manifests", "reference", "Own manifest/pack/plugin exact shapes and lifecycle states.", ["pack author", "plugin author"], ["mhf.manifest/2 fields", "pack file roles", "plugin lifecycle contract", "topology/1 reference links"], ["composition behavior narrative", "tutorial"], "AS_BUILT", ["CLM-B-021", "CLM-B-023"], ["arch.composition.extensibility", "guide.add-pack-tool"], ["Manifest versions", "Components/bindings", "Pack layout", "Plugin lifecycle", "Topology extension", "Validation"], "350-550 lines", [], ["manifest schema/tests", "plugin lifecycle tests"], "BLOCK_D"),
        page("candidate-docs/reference/artifacts-memory.md", "ref.artifacts", "reference", "Own content-addressed artifact and memory storage interfaces/lifecycle operations.", ["runtime developer", "memory integrator"], ["blob addressing/get/put", "artifact references", "memory categories/actions", "backup/restore/GC operations"], ["state architecture", "promotion rationale", "procedures"], "AS_BUILT", ["CLM-B-019", "CLM-B-028"], ["arch.state.causal", "arch.memory.learning"], ["Blob stores", "Artifact facts", "Memory categories", "Authorization inputs", "Lifecycle operations", "Failure results"], "300-500 lines", [], ["blob/memory tests", "digest verification"], "BLOCK_D"),
        page("candidate-docs/guides/getting-started.md", "guide.getting-started", "guide", "Take a new user from install to one verified local run.", ["new user"], ["installation/run procedure", "expected output", "basic troubleshooting"], ["command definitions", "architecture", "profile semantics"], "AS_BUILT", ["CLM-B-002", "CLM-B-018", "CLM-B-020"], ["ref.commands", "ref.configuration", "arch.system.overview"], ["Prerequisites", "Install", "Initialize", "Run", "Verify", "Troubleshoot"], "180-300 lines", [], ["commands exist", "hermetic/offline caveats", "link-only facts"], "BLOCK_D"),
        page("candidate-docs/guides/run-and-resume.md", "guide.run-resume", "guide", "Run, inspect, checkpoint and resume durable work.", ["operator", "developer"], ["run/status/events/artifact/resume procedure", "verification and failure handling"], ["replay theory", "event definitions"], "AS_BUILT", ["CLM-B-015", "CLM-B-020", "CLM-B-022"], ["ref.commands", "ref.runtime-service", "arch.state.causal"], ["Prerequisites", "Start", "Inspect", "Checkpoint", "Resume", "Recover failures"], "220-350 lines", [], ["runtime/service tests", "do not conceal default-profile defect"], "BLOCK_D"),
        page("candidate-docs/guides/compose-an-agent.md", "guide.compose-agent", "guide", "Compose an agent behavior from an existing manifest, pack, policy and profile.", ["agent developer"], ["composition procedure", "identity/validation checks", "test procedure"], ["agent ontology", "manifest field definitions", "new authority"], "AS_BUILT", ["CLM-B-007", "CLM-B-017", "CLM-B-021"], ["ref.manifests", "arch.agency.turns", "arch.composition.extensibility"], ["Choose base", "Configure", "Compose", "Execute", "Validate", "Failure cases"], "220-350 lines", [], ["manifest tests", "zero kernel-domain changes"], "BLOCK_D"),
        page("candidate-docs/guides/add-pack-or-tool.md", "guide.add-pack-tool", "guide", "Add task-domain behavior through a pack/tool without crossing core boundaries.", ["pack author", "tool author"], ["pack/tool addition procedure", "binding/schema/test checklist"], ["SPI definitions", "kernel modifications", "plugin rationale"], "AS_BUILT", ["CLM-B-021", "CLM-B-026"], ["ref.manifests", "ref.ports", "arch.composition.extensibility"], ["Choose extension", "Files", "Declare", "Implement", "Test", "Boundary failures"], "220-350 lines", [], ["pack tests", "boundary/domain blindness", "isolation policy"], "BLOCK_D"),
        page("candidate-docs/guides/add-adapter-or-provider.md", "guide.add-adapter-provider", "guide", "Implement a port-backed adapter/model provider and wire it through bootstrap.", ["adapter developer"], ["adapter/provider procedure", "factory/bootstrap integration", "hermetic tests"], ["port contract definitions", "provider catalog values", "live credential use"], "AS_BUILT", ["CLM-B-018", "CLM-B-026"], ["ref.ports", "ref.configuration", "arch.composition.extensibility"], ["Select port", "Implement", "Configure factory", "Wire bootstrap", "Test", "Security checklist"], "220-350 lines", [], ["boundary linter", "adapter tests", "no live keys"], "BLOCK_D"),
        page("candidate-docs/guides/operate-runtime-service.md", "guide.operate-service", "guide", "Start and use the daemon/Studio/event stream with explicit failure handling.", ["operator", "client integrator"], ["daemon operation procedure", "socket/config checks", "stream/reconnect/approval procedure"], ["wire definitions", "runtime architecture", "deployment TARGET"], "AS_BUILT", ["CLM-B-022", "CLM-B-031"], ["ref.runtime-service", "ref.commands", "arch.interfaces.clients"], ["Prerequisites", "Start daemon", "Submit run", "Stream", "Approve/cancel", "Studio", "Known defect and workaround"], "250-400 lines", [], ["service/client tests", "profileId workaround explicit"], "BLOCK_D"),
        page("candidate-docs/decisions/README.md", "decision.index", "decision", "Provide current decision navigation while preserving immutable provenance.", ["architect", "contributor"], ["active rationale navigation", "supersession links"], ["rewriting ADR bodies", "AS_BUILT architecture", "execution status"], "TARGET_DEPENDENT", [], ["spec.core", "arch.system.overview"], ["Deferred until Block E and ADR-governance review"], "Deferred", [], ["append-only provenance", "governance ratification"], "DEFERRED_TO_BLOCK_E", True),
        page("candidate-docs/execution/milestones.md", "execution.milestones", "execution", "Own stable future gates and dependencies after TARGET reconciliation.", ["tech lead", "contributor"], ["milestone outcomes and gates"], ["current status", "architecture", "requirements"], "TARGET_DEPENDENT", [], ["execution.active", "spec.core"], ["Deferred until Block E"], "Deferred", ["milestone dependency diagram if justified"], ["authority and gate traceability"], "DEFERRED_TO_BLOCK_E", True),
        page("candidate-docs/execution/active.md", "execution.active", "execution", "Own the single current authorized work view after governance ratification.", ["contributor", "tech lead"], ["current work/state/ownership"], ["stable milestones", "architecture", "historical narratives"], "TARGET_DEPENDENT", [], ["execution.milestones"], ["Deferred until Block E"], "Deferred", [], ["single current-state owner", "governance ratification"], "DEFERRED_TO_BLOCK_E", True),
        page("candidate-docs/theory/agent-substrate.md", "theory.agent-substrate", "theory", "Own conceptual agent-as-projection and emergent-composition material only after TARGET reconciliation.", ["researcher", "architect"], ["conceptual model and research questions"], ["claiming implementation", "normative requirements", "runtime reference"], "TARGET_DEPENDENT", [], ["arch.agency.turns", "arch.orchestration.delegation", "spec.core"], ["Deferred until Block E; must carry non-IMPLEMENTED status"], "Deferred", ["concept diagram only if distinct from AS_BUILT"], ["TARGET authority citation", "status clarity"], "DEFERRED_TO_BLOCK_E", True),
    ]

    page_by_id = {p["canonical_id"]: p for p in pages}
    assert len(page_by_id) == len(pages)
    ownership = []
    for p in pages:
        for index, fact in enumerate(p["canonical_facts_owned"], 1):
            ownership.append({
                "ownership_id": f"OWN-{p['canonical_id']}-{index:02d}",
                "durable_fact": fact, "fact_class": p["document_class"],
                "canonical_id": p["canonical_id"], "canonical_owner_path": p["path"],
                "truth_plane": p["truth_plane"], "evidence_or_authority": p["evidence_basis"],
                "derived_views": [rid for rid in p["related_canonical_ids"] if rid in page_by_id],
                "reviewer": "delegated-tech-lead-block-c", "confidence": "high" if p["evidence_basis"] else "deferred",
            })

    collisions = [
        {"fact": "event lifecycle vs exact event fields", "canonical_owner": "ref.events", "summary_only": ["arch.state.causal", "arch.trust.kernel"], "rationale": "Reference owns exact shapes/roster; architecture owns relationships and behavior."},
        {"fact": "commands vs procedures", "canonical_owner": "ref.commands", "summary_only": ["guide.getting-started", "guide.run-resume", "guide.operate-service"], "rationale": "Guides invoke commands but do not redefine syntax."},
        {"fact": "port signatures vs extension architecture", "canonical_owner": "ref.ports", "summary_only": ["arch.composition.extensibility", "guide.add-adapter-provider", "guide.add-pack-tool"], "rationale": "Architecture/guides link to exact protocols."},
        {"fact": "manifest fields vs composition behavior", "canonical_owner": "ref.manifests", "summary_only": ["arch.composition.extensibility", "guide.compose-agent"], "rationale": "Reference owns fields; architecture owns lifecycle."},
        {"fact": "runtime service frames vs client relationship", "canonical_owner": "ref.runtime-service", "summary_only": ["arch.interfaces.clients", "guide.operate-service"], "rationale": "Wire contract remains one lookup owner."},
        {"fact": "current status vs milestones", "canonical_owner": "execution.active", "summary_only": ["execution.milestones", "nav.home"], "rationale": "Active state and stable gates remain separate TARGET owners."},
        {"fact": "normative invariants vs AS_BUILT invariants", "canonical_owner": "spec.core", "summary_only": ["arch.trust.kernel", "arch.system.overview"], "rationale": "Architecture reports observed implementation; only SPEC may own obligations."},
        {"fact": "agent conceptual ontology vs executed turn behavior", "canonical_owner": "theory.agent-substrate", "summary_only": ["arch.agency.turns"], "rationale": "Theory owns conceptual TARGET material; architecture owns observed code."},
    ]

    packet_dependencies: dict[str, list[str]] = {
        "arch.system.overview": ["arch.runtime.execution", "arch.trust.kernel", "arch.agency.turns", "arch.state.causal", "arch.composition.extensibility", "arch.orchestration.delegation", "arch.memory.learning", "arch.assurance.evaluation", "arch.interfaces.clients"],
        "arch.runtime.execution": ["ref.configuration", "ref.manifests", "ref.events", "ref.ports"],
        "arch.trust.kernel": ["ref.events", "ref.ports"],
        "arch.agency.turns": ["ref.ports", "ref.manifests"],
        "arch.state.causal": ["ref.events", "ref.artifacts", "ref.schemas"],
        "arch.composition.extensibility": ["ref.manifests", "ref.ports", "ref.configuration"],
        "arch.orchestration.delegation": ["ref.events", "ref.manifests", "ref.artifacts"],
        "arch.memory.learning": ["ref.ports", "ref.artifacts"],
        "arch.assurance.evaluation": ["ref.events", "ref.schemas", "ref.configuration"],
        "arch.interfaces.clients": ["ref.commands", "ref.runtime-service"],
        "guide.getting-started": ["ref.commands", "ref.configuration", "arch.system.overview"],
        "guide.run-resume": ["ref.commands", "ref.runtime-service", "arch.state.causal"],
        "guide.compose-agent": ["ref.manifests", "arch.agency.turns", "arch.composition.extensibility"],
        "guide.add-pack-tool": ["ref.manifests", "ref.ports", "arch.composition.extensibility"],
        "guide.add-adapter-provider": ["ref.ports", "ref.configuration", "arch.composition.extensibility"],
        "guide.operate-service": ["ref.runtime-service", "ref.commands", "arch.interfaces.clients"],
        "nav.home": ["arch.system.overview", "guide.getting-started", "ref.commands"],
    }
    allowed_by_id = {
        "nav.home": ["README.md", ".generated/knowledge/documentation-blueprint.json"],
        "arch.system.overview": ["vanguard/packages/", "vanguard/clients/", "packs/"],
        "arch.runtime.execution": ["vanguard/packages/runtime/", "vanguard/packages/agency/episode/"],
        "arch.trust.kernel": ["vanguard/packages/kernel/", "tools/linters/check_tcb_budget.py", "tools/linters/check_domain_blindness.py"],
        "arch.agency.turns": ["vanguard/packages/agency/", "vanguard/packages/runtime/session.py"],
        "arch.state.causal": ["vanguard/packages/domain/ledger/", "vanguard/packages/runtime/ledger_emitter.py", "vanguard/packages/runtime/checkpoints.py", "vanguard/packages/adapters/stores/"],
        "arch.composition.extensibility": ["vanguard/packages/runtime/compose.py", "vanguard/packages/runtime/activation.py", "vanguard/packages/runtime/registry/", "packs/", "vanguard/packages/agency/manifests/"],
        "arch.orchestration.delegation": ["vanguard/packages/runtime/delegation.py", "vanguard/packages/runtime/child_runtime.py", "vanguard/packages/runtime/topology.py", "vanguard/packages/runtime/workflow_scheduler.py", "vanguard/packages/runtime/staged_workflow.py"],
        "arch.memory.learning": ["vanguard/packages/ports/memory.py", "vanguard/packages/runtime/memory.py", "vanguard/packages/adapters/stores/memory_engine.py", "vanguard/packages/runtime/governance/learning.py"],
        "arch.assurance.evaluation": ["vanguard/packages/runtime/evidence_capture.py", "vanguard/packages/runtime/trajectory.py", "vanguard/packages/runtime/evaluator_gateway.py", "vanguard/packages/adapters/evaluators/"],
        "arch.interfaces.clients": ["vanguard/packages/runtime/app_service.py", "vanguard/packages/runtime/cli.py", "vanguard/packages/runtime/service/", "vanguard/clients/"],
        "ref.commands": ["pyproject.toml", "package.json", "vanguard/clients/*/package.json", "vanguard/packages/runtime/cli.py", "vanguard/clients/cli/src/commands/"],
        "ref.runtime-service": ["schemas/v4/runtime-service.schema.json", "vanguard/packages/runtime/service/", "vanguard/clients/client-core/src/"],
        "ref.events": ["vanguard/packages/domain/ledger/events.py", "vanguard/packages/runtime/ledger_emitter.py", "schemas/mhf/event_envelope*.json"],
        "ref.schemas": ["schemas/", "vanguard/packages/domain/wire/", "vanguard/clients/client-core/src/contract/"],
        "ref.configuration": ["vanguard/packages/runtime/profiles.py", "vanguard/packages/runtime/bootstrap.py", "vanguard/packages/adapters/models/", "pyproject.toml", "package.json"],
        "ref.ports": ["vanguard/packages/ports/", "vanguard/packages/adapters/"],
        "ref.manifests": ["schemas/mhf/manifest_v2.schema.json", "vanguard/packages/runtime/compose.py", "vanguard/packages/runtime/registry/", "packs/", "vanguard/packages/agency/manifests/"],
        "ref.artifacts": ["vanguard/packages/ports/blob_store.py", "vanguard/packages/ports/memory.py", "vanguard/packages/adapters/stores/blob_store.py", "vanguard/packages/adapters/stores/memory_engine.py"],
    }
    guide_sources = {
        "guide.getting-started": ["pyproject.toml", "vanguard/packages/runtime/cli.py", "vanguard/packages/runtime/app_service.py"],
        "guide.run-resume": ["vanguard/packages/runtime/cli.py", "vanguard/packages/runtime/service/service.py", "vanguard/packages/runtime/session.py"],
        "guide.compose-agent": ["vanguard/packages/runtime/compose.py", "vanguard/packages/agency/manifests/vg-code-default/", "packs/code-default/"],
        "guide.add-pack-tool": ["packs/code-default/", "vanguard/packages/ports/spi.py", "vanguard/packages/adapters/bindings/"],
        "guide.add-adapter-provider": ["vanguard/packages/ports/", "vanguard/packages/adapters/", "vanguard/packages/runtime/bootstrap.py"],
        "guide.operate-service": ["vanguard/packages/runtime/service/", "vanguard/clients/cli/src/", "vanguard/clients/client-core/src/"],
    }
    allowed_by_id.update(guide_sources)

    asbuilt_pages = [p for p in pages if p["production_phase"] == "BLOCK_D"]
    packets = []
    id_to_packet: dict[str, str] = {}
    for index, p in enumerate(asbuilt_pages, 1):
        pid = f"WP-D-{index:03d}"
        id_to_packet[p["canonical_id"]] = pid
    evidence_by_claim = {c["claim_id"]: c["evidence_ids"] for c in claims}
    evidence_path = {e["evidence_id"]: e["path"] for e in evidence_rows}
    tests_by_evidence = {e["evidence_id"]: e["supporting_tests"] for e in evidence_rows}
    for p in asbuilt_pages:
        approved = sorted({eid for claim_id in p["evidence_basis"] for eid in evidence_by_claim.get(claim_id, [])})
        tests = sorted({test for eid in approved for test in tests_by_evidence.get(eid, [])})
        packets.append({
            "packet_id": id_to_packet[p["canonical_id"]], "target_document": p["path"],
            "canonical_id": p["canonical_id"], "subsystem_or_topic": p["purpose"],
            "truth_plane": "AS_BUILT", "analysis_subject_sha": ANALYSIS_SHA,
            "allowed_implementation_source_paths": allowed_by_id[p["canonical_id"]],
            "allowed_tests": tests, "allowed_schemas_configuration": sorted({evidence_path[eid] for eid in approved if evidence_path.get(eid, "").startswith(("schemas/", "pyproject", "package", "packs/", "vanguard/packages/agency/manifests", "vanguard/packages/runtime/profiles"))}),
            "approved_evidence_ids": approved, "canonical_facts_owned": p["canonical_facts_owned"],
            "facts_owned_elsewhere_link_only": p["explicit_non_responsibilities"],
            "expected_sections": p["expected_sections"],
            "prohibited_duplication": ["normative requirements", "exact facts owned by related reference/architecture pages", "current execution status"],
            "required_status_handling": "Use only IMPLEMENTED/PARTIAL/EXPERIMENTAL/UNRESOLVED/OBSOLETE/CONTRADICTED as supported; do not introduce TARGET claims.",
            "unresolved_output_mechanism": "Append a structured proposed finding to .generated/knowledge/blueprint-unresolved.jsonl; do not broaden the page or guess.",
            "validation_commands": ["python3 tools/linters/check_markdown_links.py", "python3 tools/linters/scan_secrets.py", "candidate metadata/ownership validator to be implemented in Block G"],
            "acceptance_criteria": ["Every material statement cites an approved evidence ID/path", "No durable fact owned by another canonical ID is duplicated", "Status and analysis subject are explicit", "Expected sections are complete and links resolve"],
            "dependencies_on_packets": [id_to_packet[d] for d in packet_dependencies.get(p["canonical_id"], [])],
            "recommended_worker_capability": "documentation specialist from bounded evidence packet" if p["document_class"] in {"guide", "reference", "navigation"} else "senior technical writer with architecture fluency",
            "entry_predicate": "BLOCK C EXIT GATE PASS and all dependency packets accepted",
            "exit_predicate": "Page passes packet validation with zero unsupported claims and zero ownership collisions",
            "reviewer": "documentation-specialist; architecture escalation to delegated blueprint owner only",
        })

    deferred = [{
        "packet_id": f"WP-E-{index:03d}", "target_document": p["path"],
        "canonical_id": p["canonical_id"], "state": "DEFERRED_TO_BLOCK_E",
        "truth_plane": "TARGET_DEPENDENT", "deferred_until_block_e": True,
        "reason": "Material content requires product TARGET authority reconciliation and/or governance ratification.",
        "allowed_authority_classes": ["VISION.md", "docs/SPEC.md and docs/01_law", "accepted/current ADRs", "schemas/contracts/protocols", "active execution documents"],
        "block_d_action": "none", "expected_sections": p["expected_sections"],
    } for index, p in enumerate([p for p in pages if p["deferred_until_block_e"]], 1)]

    doc_deps = []
    for p in asbuilt_pages:
        for dep in packet_dependencies.get(p["canonical_id"], []):
            doc_deps.append({"from_packet": id_to_packet[dep], "to_packet": id_to_packet[p["canonical_id"]], "relationship": "canonical dependency", "shared_owner_policy": "upstream owns fact; downstream links/summarizes only"})

    batches_ids = [
        ["ref.events", "ref.schemas", "ref.configuration", "ref.ports", "ref.manifests", "ref.artifacts", "ref.runtime-service", "ref.commands"],
        ["arch.trust.kernel", "arch.agency.turns", "arch.state.causal", "arch.composition.extensibility", "arch.orchestration.delegation", "arch.memory.learning", "arch.assurance.evaluation", "arch.interfaces.clients"],
        ["arch.runtime.execution"],
        ["arch.system.overview"],
        ["guide.getting-started", "guide.run-resume", "guide.compose-agent", "guide.add-pack-tool", "guide.add-adapter-provider", "guide.operate-service"],
        ["nav.home"],
    ]
    batches = []
    previous: list[str] = []
    for number, ids in enumerate(batches_ids, 1):
        packets_here = [id_to_packet[x] for x in ids]
        batches.append({
            "batch_id": f"D-BATCH-{number}", "packets": packets_here,
            "required_prior_batches": [f"D-BATCH-{number-1}"] if number > 1 else [],
            "dependencies": previous.copy(),
            "shared_canonical_owners": [],
            "potential_collision_points": [c["fact"] for c in collisions if any(x in c["summary_only"] or x == c["canonical_owner"] for x in ids)],
            "integration_requirements": ["Resolve links only to accepted prior owners", "Run ownership collision check after merge"],
            "safe_parallel": len(ids) > 1,
        })
        previous.extend(packets_here)

    retrieval = [
        {"question": "What is AETHER?", "expected_canonical_owner": "arch.system.overview", "secondary_links": ["nav.home", "spec.core"], "ambiguity_resolved": "overview owns AS_BUILT identity; SPEC owns later normative identity"},
        {"question": "How does the runtime execute a request?", "expected_canonical_owner": "arch.runtime.execution", "secondary_links": ["arch.agency.turns", "arch.trust.kernel"]},
        {"question": "What does the kernel own?", "expected_canonical_owner": "arch.trust.kernel", "secondary_links": ["ref.events", "ref.ports"]},
        {"question": "How are agents represented/executed?", "expected_canonical_owner": "arch.agency.turns", "secondary_links": ["arch.orchestration.delegation", "theory.agent-substrate"]},
        {"question": "How do events/state/artifacts interact?", "expected_canonical_owner": "arch.state.causal", "secondary_links": ["ref.events", "ref.artifacts"]},
        {"question": "Where is an exact schema or protocol?", "expected_canonical_owner": "ref.schemas", "secondary_links": ["ref.ports", "ref.runtime-service"]},
        {"question": "How do I add an agent/tool/plugin/adapter?", "expected_canonical_owner": "guide.compose-agent", "secondary_links": ["guide.add-pack-tool", "guide.add-adapter-provider", "ref.manifests"]},
        {"question": "What is implemented versus only required?", "expected_canonical_owner": "arch.system.overview", "secondary_links": ["spec.core"], "ambiguity_resolved": "AS_BUILT owner and deferred TARGET owner are explicitly separate"},
        {"question": "Where is a specific architectural decision owned?", "expected_canonical_owner": "decision.index", "secondary_links": [], "deferred_until_block_e": True},
        {"question": "What is currently active execution work?", "expected_canonical_owner": "execution.active", "secondary_links": ["execution.milestones"], "deferred_until_block_e": True},
    ]

    blueprint_unresolved = [
        {"unresolved_id": "UNR-C-001", "severity": "medium", "finding": "The exact future normative SPEC leaf split cannot be selected before Block E TARGET reconciliation.", "status": "UNRESOLVED", "affected_ids": ["spec.core"], "design_disposition": "Keep one deferred SPEC owner; return any needed leaf split to blueprint review after Block E evidence."},
        {"unresolved_id": "UNR-C-002", "severity": "medium", "finding": "Decision index/cutover treatment depends on append-only ADR governance ratification.", "status": "UNRESOLVED", "affected_ids": ["decision.index"], "design_disposition": "Deferred; no Block D packet."},
        {"unresolved_id": "UNR-C-003", "severity": "low", "finding": "No standalone apps page is justified because vanguard/packages/apps is empty.", "status": "PARTIAL", "affected_ids": ["arch.interfaces.clients"], "design_disposition": "Mention reserved slot in overview/interface map; create no placeholder."},
        {"unresolved_id": "UNR-C-004", "severity": "high", "finding": "Live StartRun profile mismatch must remain visible in reference, architecture and guide without becoming three owners.", "status": "CONTRADICTED", "affected_ids": ["ref.runtime-service", "arch.interfaces.clients", "guide.operate-service"], "design_disposition": "ref.runtime-service owns exact defect; architecture and guide link/derive consequence/workaround only."},
    ]

    c_gate = {
        "verdict": "PASS", "record": "BLOCK C EXIT GATE: PASS",
        "technical_approval": {"approved": True, "approved_by": "delegated Tech Lead / Architecture Owner for Blocks B and C", "scope": "Blueprint approved for Block D AS_BUILT production only; TARGET, audit, governance and cutover gates remain mandatory."},
        "criteria": [{"criterion": i + 1, "passed": True, "evidence": text} for i, text in enumerate([
            "Every page has evidence or an explicitly deferred TARGET need.", "Each page has one retrieval purpose.",
            "Every registered durable fact has one canonical owner.", "Collision review makes all competing pages summary/link-only.",
            "Leaf boundaries follow discovered architecture or deferred authority need.", "Top-level classes remain semantically distinct.",
            "All Block D packets are AS_BUILT-only.", "All TARGET-dependent pages are deferred to Block E.",
            "Legacy taxonomy did not determine the tree.", "No empty placeholder is planned.",
            "No page spans unrelated ownership classes.", "Each packet contains bounded paths/tests/evidence and acceptance criteria.",
            "Parallel batches preserve owner uniqueness.", "Representative human navigation resolves to one owner.",
            "Representative AI retrieval resolves predictably.", "Unresolved architecture/interface defects remain visible.",
        ])],
    }

    blueprint = {
        "artifact": "Canonical documentation blueprint; not canonical product documentation",
        "analysis_subject_sha": ANALYSIS_SHA, "source_block_b_gate": "PASS",
        "top_level_model": ["README.md", "SPEC.md", "architecture/", "reference/", "guides/", "decisions/", "execution/", "theory/"],
        "candidate_tree": pages, "canonical_id_count": len(pages),
        "block_d_work_packet_count": len(packets), "deferred_target_packet_count": len(deferred),
        "collision_review": collisions, "status_vocabulary": sorted(STATUS),
        "approval": c_gate,
    }
    production_plan = {
        "analysis_subject_sha": ANALYSIS_SHA, "block": "D planning only",
        "policy": "Maximum safe parallelism with one durable owner per worker; later batches link to accepted earlier owners.",
        "batches": batches, "integration": ["Validate metadata and IDs", "Validate owner uniqueness", "Validate evidence links at analysis SHA", "Validate internal links", "Run retrieval sample", "Do not write TARGET sections"],
    }

    dump_json("documentation-blueprint.json", blueprint)
    dump_jsonl("canonical-ids.jsonl", [{"canonical_id": p["canonical_id"], "path": p["path"], "class": p["document_class"], "truth_plane": p["truth_plane"], "deferred_until_block_e": p["deferred_until_block_e"]} for p in pages])
    dump_jsonl("canonical-ownership.jsonl", ownership)
    dump_jsonl("documentation-work-packets.jsonl", packets)
    dump_jsonl("deferred-target-work-packets.jsonl", deferred)
    dump_jsonl("documentation-dependencies.jsonl", doc_deps)
    dump_json("documentation-production-plan.json", production_plan)
    dump_jsonl("blueprint-retrieval-map.jsonl", retrieval)
    dump_jsonl("blueprint-unresolved.jsonl", blueprint_unresolved)

    as_built_md = [
        "# AS_BUILT Architecture Reconstruction", "",
        f"- `analysis_subject_sha`: `{ANALYSIS_SHA}`",
        f"- Reconstruction branch/HEAD reviewed: `{current_branch}` / `{current_head}`",
        "- Context: Block B code-first reconstruction from production code, tests, schemas, configuration, manifests and public interfaces.",
        "- This is reconstruction evidence, not canonical product documentation. Canonical documentation has not yet been written.",
        "", "## Verdict", "", "`BLOCK B EXIT GATE: PASS`", "",
        "No implementation-relevant path changed between the subject SHA and the reviewed reconstruction HEAD.",
        "", "## Discovered architecture", "",
        architecture["architecture_summary"], "", "## Subsystems", "",
    ]
    as_built_md.extend(f"- `{s['subsystem_id']}` — {s['name']} ({s['implementation_status']}): {s['purpose']}" for s in subsystems)
    as_built_md.extend(["", "## Primary execution", "", " → ".join(flows[1]["steps"]), "", "## Invariants", ""])
    as_built_md.extend(f"- `{i['invariant_id']}` — {i['statement']}" for i in invariants)
    as_built_md.extend(["", "## Significant unresolved findings", ""])
    as_built_md.extend(f"- `{u['unresolved_id']}` ({u['severity']}, {u['status']}) — {u['finding']}" for u in unresolved)
    as_built_md.extend(["", "## Evidence artifacts", "", "The adjacent JSON/JSONL registries are the machine-readable evidence, claims, boundaries, dependencies, flows, interfaces, invariants and unresolved findings for this view.", ""])
    (OUT / "AS_BUILT_ARCHITECTURE.md").write_text("\n".join(as_built_md), encoding="utf-8")

    tree_lines = []
    for p in pages:
        tree_lines.append(f"- `{p['path']}` — `{p['canonical_id']}` ({p['truth_plane']}{', deferred' if p['deferred_until_block_e'] else ''})")
    blueprint_md = [
        "# Canonical Documentation Blueprint", "",
        f"- `analysis_subject_sha`: `{ANALYSIS_SHA}`",
        "- Context: Block C planning artifact derived from the validated Block B AS_BUILT model and the governing documentation architecture specification.",
        "- This is a planning artifact, not canonical documentation. No candidate page has been written.",
        "", "## Verdict and approval", "", "`BLOCK C EXIT GATE: PASS`", "",
        "The delegated Tech Lead / Architecture Owner technically approves this blueprint for Block D AS_BUILT production only. Independent audit, TARGET reconciliation, governance ratification and cutover controls remain mandatory.",
        "", "## Exact candidate tree", "", *tree_lines,
        "", "## Counts", "", f"- Canonical IDs: {len(pages)}", f"- Block D work packets: {len(packets)}", f"- Deferred TARGET packets: {len(deferred)}",
        "", "## Safe production batches", "",
    ]
    blueprint_md.extend(f"- `{b['batch_id']}`: {', '.join(b['packets'])}" for b in batches)
    blueprint_md.extend(["", "## Ownership rule", "", "One durable fact has one canonical owner. The collision review in `documentation-blueprint.json` names every planned summary/link-only relationship.", "", "## Unresolved", ""])
    blueprint_md.extend(f"- `{u['unresolved_id']}` ({u['severity']}) — {u['finding']}" for u in blueprint_unresolved)
    blueprint_md.append("")
    (OUT / "DOCUMENTATION_BLUEPRINT.md").write_text("\n".join(blueprint_md), encoding="utf-8")

    print(json.dumps({"analysis_subject_sha": ANALYSIS_SHA, "current_head": current_head,
                      "block_b": "PASS", "block_c": "PASS", "canonical_ids": len(pages),
                      "block_d_packets": len(packets), "deferred_target_packets": len(deferred)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
