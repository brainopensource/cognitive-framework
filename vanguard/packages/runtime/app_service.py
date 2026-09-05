"""Unified Application Service implementing Command / Query Separation (BETA-04, BETA-05, EVO-07).

Provides the shared boundary between user-facing transports (CLI, stdio JSON entrypoint,
Observatory daemon) and the runtime substrate.
"""

from __future__ import annotations

import hashlib
import importlib
import json
import os
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterator, Mapping, Sequence

from ..adapters.sandbox.platform import discover_platform
from ..adapters.stores.blob_store import FileBlobStore
from ..adapters.stores.event_store import SqliteEventStore
from ..domain.ledger.events import EventEnvelope
from ..ports.event_store import EventRange
from .bootstrap import RuntimeBootstrap
from .compose import TaskContext
from .model_selection import inspect_model_providers, select_model
from .profiles import ExecutionProfileError, SandboxUnavailable, resolve_profile
from .root import Runtime
from .results import RunResult, StatusResult, EvidenceResult, CostResult
from .task_state import CodingTaskState, episode_id_from_events, fold_task_state
from .state_contract import (
    StateDirectoryError,
    StateDirectoryUnwritableError,
    ensure_state_directory,
    inspect_state_directory,
    resolve_state_directory,
)


@dataclass(frozen=True, slots=True)
class DiagnosticCheck:
    name: str
    status: str  # "ok" | "warn" | "error" | "unavailable"
    detail: str
    remediation: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status,
            "detail": self.detail,
            "remediation": self.remediation,
        }


@dataclass(frozen=True, slots=True)
class DiagnosticsResult:
    health: str  # "healthy" | "degraded" | "unhealthy"
    readiness: str  # "ready" | "unready"
    checks: tuple[DiagnosticCheck, ...]
    version: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "health": self.health,
            "readiness": self.readiness,
            "version": self.version,
            "checks": [c.to_dict() for c in self.checks],
        }




@dataclass(frozen=True, slots=True)
class EventsResult:
    run_id: str
    events: tuple[Mapping[str, Any], ...]
    total: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "runId": self.run_id,
            "events": list(self.events),
            "total": self.total,
        }


@dataclass(frozen=True, slots=True)
class ArtifactResult:
    artifact_id: str | None
    digest: str
    content: bytes | None
    role: str
    verified: bool
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "artifactId": self.artifact_id,
            "digest": self.digest,
            "role": self.role,
            "verified": self.verified,
            "byteLength": len(self.content) if self.content is not None else 0,
            "error": self.error,
        }


class ApplicationService:
    """Production application boundary for Vanguard operations."""

    def __init__(self, workspace: Path | str | None = None) -> None:
        self.workspace = Path(workspace).resolve() if workspace is not None else Path.cwd()

    @staticmethod
    def _pack_completion_policy(manifest_path: Path) -> Any:
        """Bind coding completion policy from declared capabilities.

        Policy selection must not depend on a growing preset-name allowlist.
        Any manifest that grants patch application receives the code-pack
        completion policy; read-only compositions retain the generic gate.
        """
        try:
            declared = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None
        capabilities = declared.get("capabilities", ())
        if not any(isinstance(item, Mapping) and item.get("verb") == "patch.apply"
                   for item in capabilities):
            return None
        pack_root = Path(__file__).resolve().parents[3] / "packs" / "code-default"
        import sys
        if str(pack_root) not in sys.path:
            sys.path.insert(0, str(pack_root))
        module = importlib.import_module("middleware.repository.multi_file_completeness")
        return module.CodeDefaultCompletionPolicy()

    def run(
        self,
        *,
        brief: str,
        manifest_path: Path | str | None = None,
        profile_id: str = "product",
        run_id: str | None = None,
        model: Any = None,
        model_port: str | None = None,
        planner_model: str | None = None,
        state_dir: Path | str | None = None,
        interactive: bool = True,
        max_turns: int = 40,
        autonomous_approval: bool = False,
        allow_paid: bool = False,
    ) -> RunResult:
        """Execute a new run through the canonical runtime pipeline.

        ``autonomous_approval`` is an explicit opt-in (never default-on) that
        lets an unattended run answer its own approval-gated effects (e.g.
        ``proc.exec``) with a fresh, ephemeral, per-run Ed25519 governance
        signature -- the same ``OperatorSigner``-bound pattern already used by
        ``test/integration/test_lam_runtime_vertical.py`` and the falsifier
        suite, just reachable from the public application boundary. It never
        widens the harness's own declared capabilities: the signature only
        answers challenges for effects the manifest already scoped (e.g.
        ``proc://exec/allow/git,pytest,ruff,python3``). It has no effect
        unless ``interactive`` is also true, since ``interactive=False`` maps
        to the kernel's benchmark mode, which fails closed on every
        approval-gated effect regardless of any approver (``F-07``).
        """
        if not brief:
            raise ValueError("brief is required for run")

        resolved_run_id = run_id or f"run-{os.urandom(4).hex()}"
        task = TaskContext(
            brief=brief,
            repo_path=self.workspace,
            run_id=resolved_run_id,
            episode_id=f"episode-{resolved_run_id}",
            max_turns=max_turns,
        )

        resolved_state = resolve_state_directory(self.workspace, state_dir=state_dir)
        ensure_state_directory(resolved_state, durability_mode="sqlite-wal")
        store_path = resolved_state / "events.sqlite3"
        blobs = FileBlobStore(resolved_state / "blobs")

        if isinstance(model, str):
            model_id = model.strip()
            model = None
            if model_id:
                selected_model = select_model(
                    model_port or "openrouter",
                    model_name=model_id,
                    allow_paid=allow_paid,
                ).model
            else:
                selected_model = None
            if selected_model is not None:
                pass
            elif model_port:
                if isinstance(model_port, str):
                    selected_model = select_model(
                        model_port,
                        model_name=planner_model,
                        allow_paid=allow_paid,
                    ).model
                else:
                    selected_model = model_port
            elif profile_id in {"local", "ci", "fast"}:
                from ..adapters.models.fake import FakeModel
                selected_model = FakeModel([{"kind": "finish", "note": "local preview"}])
            else:
                selected_model = select_model("openrouter", model_name=planner_model, allow_paid=allow_paid).model
        elif model is None:
            if model_port:
                if isinstance(model_port, str):
                    selected_model = select_model(
                        model_port,
                        model_name=planner_model,
                        allow_paid=allow_paid,
                    ).model
                else:
                    selected_model = model_port
            elif profile_id in {"local", "ci", "fast"}:
                from ..adapters.models.fake import FakeModel
                selected_model = FakeModel([{"kind": "finish", "note": "local preview"}])
            else:
                selected_model = select_model("openrouter", model_name=planner_model, allow_paid=allow_paid).model
        else:
            selected_model = model

        # Default manifest if not provided
        if manifest_path is None:
            from importlib.resources import files
            manifest_resource = files("vanguard.packages.agency").joinpath(
                "manifests", "vg-code-default", "manifest.json"
            )
            manifest_p = Path(str(manifest_resource))
        else:
            manifest_p = Path(manifest_path).resolve()

        approver_kwargs: dict[str, Any] = {}
        if autonomous_approval and interactive:
            from .governance.approvals import OperatorSigner

            signer = OperatorSigner()
            approver_kwargs["approver"] = lambda challenge, _s=signer: _s.approve(challenge, reviewer="autonomous-operator")
            approver_kwargs["approval_key"] = signer.public_bytes

        completion_policy = (
            None if type(selected_model).__name__ in {"FakeModel", "ScriptedModel"}
            else self._pack_completion_policy(manifest_p)
        )
        exec_result = Runtime.execute_profiled(
            manifest_p,
            task,
            profile_id=profile_id,
            model=selected_model,
            store_path=str(store_path),
            interactive=interactive,
            blobs=blobs,
            completion_policy=completion_policy,
            **approver_kwargs,
        )

        terminal = str(getattr(exec_result.terminal, "value", exec_result.terminal))
        outcome = "completed" if terminal in {"completed", "abstained"} else terminal

        projections: list[dict[str, Any]] = []
        for rec in getattr(exec_result, "receipts", ()) or ():
            verb = getattr(rec, "verb", "")
            rec_outcome = getattr(rec, "outcome", "")
            rec_detail = getattr(rec, "detail", "")
            if verb == "fs.read":
                projections.append({"kind": "read", "path": rec_detail or "file"})
            elif verb in ("patch.apply", "fs.patch", "fs.write"):
                projections.append({"kind": "write", "path": rec_detail or "patch", "text": rec_outcome})
            elif verb == "proc.exec":
                projections.append({"kind": "test", "path": rec_detail or "exec", "exitCode": 0 if rec_outcome == "ok" else 1})

        projections.append({
            "kind": "complete",
            "outcome": outcome,
            "turns": int(getattr(exec_result.telemetry, "turns", 0)),
        })

        task_state = self._read_task_state(resolved_state, resolved_run_id, fallback=brief)
        return self._result_from_execution(
            run_id=resolved_run_id,
            outcome=outcome,
            phase="complete",
            turns=int(getattr(exec_result.telemetry, "turns", 0)),
            plan_digest=exec_result.run_digest or None,
            detail=exec_result.detail,
            projections=tuple(projections),
            episode_id=task.episode_id,
            execution=exec_result,
            task_state=task_state,
        )

    @staticmethod
    def _read_task_state(state_dir: Path, run_id: str, *, fallback: str = "") -> CodingTaskState:
        store = SqliteEventStore(state_dir / "events.sqlite3")
        result = store.read(EventRange(run_id=run_id))
        return fold_task_state(list(result.value or ()) if result.ok else (), objective=fallback)

    @staticmethod
    def _result_from_execution(
        *, run_id: str, outcome: str, phase: str, turns: int,
        plan_digest: str | None, detail: str,
        projections: tuple[Mapping[str, Any], ...], episode_id: str,
        execution: Any,
        task_state: CodingTaskState | None = None,
    ) -> RunResult:
        trajectory = execution.trajectory if isinstance(getattr(execution, "trajectory", None), Mapping) else {}
        telemetry = getattr(execution, "telemetry", None)
        prompt = getattr(telemetry, "prompt_tokens", None)
        completion = getattr(telemetry, "completion_tokens", None)
        usage = None
        if prompt is not None and completion is not None:
            usage = {"promptTokens": prompt, "completionTokens": completion, "totalTokens": prompt + completion}
        cost = trajectory.get("cost") if isinstance(trajectory.get("cost"), Mapping) else {}
        cost_status = (cost.get("measurement_status") or {}).get("usd_micros", {}) if isinstance(cost, Mapping) else {}
        observed_cost = cost.get("usd_micros") if cost_status.get("status") == "measured" else None
        routes = trajectory.get("model_routes_used") or ()
        route = dict(routes[0]) if routes and isinstance(routes[0], Mapping) else None
        artifacts = tuple(
            str(item.get("digest") or item.get("artifactId"))
            for item in trajectory.get("artifacts", ())
            if isinstance(item, Mapping) and (item.get("digest") or item.get("artifactId"))
        )
        missing = tuple(name for name, value in (
            ("taskDigest", trajectory.get("task_digest")),
            ("modelRoute", route),
            ("promptTokens", prompt),
            ("completionTokens", completion),
            ("observedCost", observed_cost),
        ) if value is None)
        return RunResult(
            run_id=run_id, episode_id=episode_id, outcome=outcome, phase=phase,
            terminal_state=outcome, turns=turns, plan_digest=plan_digest,
            task_digest=trajectory.get("task_digest"),
            composition_digest=getattr(execution, "composition_digest", None),
            next_action=task_state.next_action if task_state else None,
            todo_state=tuple(item.to_dict() for item in task_state.todo_items) if task_state else (),
            verification_identity=task_state.last_verification if task_state and task_state.last_verification else None,
            model_route=route, token_usage=usage,
            observed_cost=observed_cost, artifact_refs=artifacts,
            missing=missing, detail=detail, projections=projections,
        )

    def resume(
        self,
        *,
        run_id: str,
        state_dir: Path | str | None = None,
        profile_id: str = "product",
        model: Any = None,
        model_port: str | None = None,
    ) -> RunResult:
        """Resume an existing run from durable ledger state."""
        if not run_id:
            raise ValueError("run_id is required for resume")

        resolved_state = resolve_state_directory(self.workspace, state_dir=state_dir)
        store_path = resolved_state / "events.sqlite3"
        if not store_path.exists():
            raise FileNotFoundError(f"cannot resume run {run_id}: no database at {store_path}")

        store = SqliteEventStore(store_path)
        events_res = store.read(EventRange(run_id=run_id))
        if not events_res.ok or not events_res.value:
            raise ValueError(f"no events found to resume run {run_id}")

        events = list(events_res.value)
        recovered_brief = None
        for ev in events:
            payload = getattr(ev, "payload", {}) if isinstance(getattr(ev, "payload", None), dict) else {}
            b = payload.get("brief") or payload.get("goal") or payload.get("objective")
            if isinstance(b, str) and b.strip() and not b.startswith("Resume run "):
                recovered_brief = b.strip()
                break

        state = fold_task_state(events, objective=recovered_brief or "")
        if not state.objective:
            raise ValueError(f"run {run_id} has no durable original objective")

        terminal_kinds = {"EpisodeCompleted", "RunCompleted", "RunFailed"}
        if any((getattr(event, "payload", {}) or {}).get("kind") in terminal_kinds for event in events):
            status = self.status(run_id, state_dir=resolved_state)
            return RunResult(
                run_id=run_id, episode_id=episode_id_from_events(events, run_id=run_id), outcome=status.status,
                phase="complete", turns=len([e for e in events if (getattr(e, "payload", {}) or {}).get("kind") == "ProposalProduced"]),
                plan_digest=None, detail="run already has a durable terminal event",
                terminal_state=status.terminal_state, task_digest=status.task_digest,
                composition_digest=status.composition_digest, next_action=state.next_action,
                todo_state=tuple(item.to_dict() for item in state.todo_items),
                missing=("planDigest", "modelRoute", "tokenUsage", "observedCost"),
            )

        # Re-enter the canonical runtime directly. The original objective and
        # the ledger-derived turn budget are restored; no synthetic prompt is
        # emitted and HarnessSession.dispatch reuses settled idempotent effects.
        resolved_run_id = run_id
        brief = state.objective
        original_max_turns = next(
            (int((getattr(ev, "payload", {}) or {}).get("maxTurns"))
             for ev in events
             if isinstance(getattr(ev, "payload", None), Mapping)
             and str((getattr(ev, "payload", {}) or {}).get("maxTurns", "")).isdigit()),
            40,
        )
        original_interactive = next(
            (bool((getattr(ev, "payload", {}) or {}).get("interactive"))
             for ev in events
             if isinstance(getattr(ev, "payload", None), Mapping)
             and "interactive" in (getattr(ev, "payload", {}) or {})),
            True,
        )
        task = TaskContext(
            brief=brief, repo_path=self.workspace, run_id=resolved_run_id,
            episode_id=episode_id_from_events(events, run_id=resolved_run_id),
            max_turns=max(1, original_max_turns),
            resume_state=state.to_canonical_dict(),
        )
        resolved_state_dir = resolved_state
        if model is None:
            if model_port:
                selected_model = select_model(model_port).model
            elif profile_id in {"local", "ci", "fast"}:
                from ..adapters.models.fake import FakeModel
                selected_model = FakeModel([{"kind": "finish", "note": "resume"}])
            else:
                selected_model = select_model("openrouter").model
        else:
            selected_model = model
        manifest_p = self._manifest_path_for_resume(events, profile_id)
        completion_policy = (
            None if type(selected_model).__name__ in {"FakeModel", "ScriptedModel"}
            else self._pack_completion_policy(manifest_p)
        )
        exec_result = Runtime.execute_profiled(
            manifest_p, task, profile_id=profile_id, model=selected_model,
            store_path=str(resolved_state_dir / "events.sqlite3"),
            interactive=original_interactive,
            blobs=FileBlobStore(resolved_state_dir / "blobs"),
            completion_policy=completion_policy,
        )
        terminal = str(getattr(exec_result.terminal, "value", exec_result.terminal))
        resumed_events = list(getattr(exec_result, "events", ()) or ())
        projections = tuple({"kind": "resume", "runId": run_id},)
        return self._result_from_execution(
            run_id=run_id, outcome=("completed" if terminal in {"completed", "abstained"} else terminal),
            phase="complete", turns=int(getattr(exec_result.telemetry, "turns", 0)),
            plan_digest=exec_result.run_digest or None, detail=exec_result.detail,
            projections=projections, episode_id=task.episode_id, execution=exec_result,
            task_state=fold_task_state(resumed_events, objective=state.objective),
        )

    def _manifest_path_for_resume(self, events: Sequence[Any], profile_id: str) -> Path:
        from importlib.resources import files
        name = "vg-code-default"
        for event in events:
            payload = getattr(event, "payload", {})
            if isinstance(payload, Mapping):
                harness = str(payload.get("harness", ""))
                if harness.startswith("vg-code-"):
                    name = harness
                    break
        return Path(str(files("vanguard.packages.agency").joinpath("manifests", name, "manifest.json")))

    def status(
        self,
        run_id: str,
        *,
        state_dir: Path | str | None = None,
    ) -> StatusResult:
        """Query execution and event status for a run."""
        resolved_state = resolve_state_directory(self.workspace, state_dir=state_dir)
        store_path = resolved_state / "events.sqlite3"
        if not store_path.exists():
            return StatusResult(
                run_id=run_id,
                status="not_found",
                event_count=0,
                as_of_seq=0,
                manifest_path=None,
                repo_path=str(self.workspace),
                detail=f"no database at {store_path}",
                missing=("episodeId", "taskDigest", "compositionDigest", "terminalState", "nextAction"),
            )

        store = SqliteEventStore(store_path)
        res = store.read(EventRange(run_id=run_id))
        if not res.ok:
            return StatusResult(
                run_id=run_id,
                status="error",
                event_count=0,
                as_of_seq=0,
                manifest_path=None,
                repo_path=str(self.workspace),
                detail=str(getattr(res, "error", "store read failed")),
                missing=("episodeId", "taskDigest", "compositionDigest", "terminalState", "nextAction"),
            )

        events = res.value or ()
        count = len(events)
        latest_seq = events[-1].seq if count > 0 else 0
        terminal_kinds = {"RunCompleted", "RunFailed", "EpisodeCompleted"}
        has_terminal = any(e.payload.get("kind") in terminal_kinds for e in events)
        state = fold_task_state(list(events))
        started = next((e.payload for e in events if e.payload.get("kind") == "EpisodeStarted"), {})
        terminal_event = next((e.payload for e in reversed(events) if e.payload.get("kind") in terminal_kinds), {})
        status_value = "completed" if has_terminal else ("running" if count > 0 else "empty")
        missing = tuple(name for name, value in (
            ("taskDigest", started.get("taskDigest")),
            ("compositionDigest", started.get("compositionDigest")),
            ("nextAction", state.next_action),
        ) if value is None)

        return StatusResult(
            run_id=run_id,
            status=status_value,
            event_count=count,
            as_of_seq=int(latest_seq),
            manifest_path=None,
            repo_path=str(self.workspace),
            detail=f"{count} events recorded",
            episode_id=next((e.episode_id for e in events if e.episode_id), None),
            task_digest=started.get("taskDigest"),
            composition_digest=started.get("compositionDigest"),
            terminal_state=terminal_event.get("outcome") if has_terminal else None,
            next_action=state.next_action,
            todo_state=tuple(item.to_dict() for item in state.todo_items),
            verification_identity=state.last_verification or None,
            missing=missing,
        )

    def events(
        self,
        run_id: str,
        *,
        after_seq: int = 0,
        limit: int | None = None,
        state_dir: Path | str | None = None,
    ) -> EventsResult:
        """Query causally ordered events for a run."""
        resolved_state = resolve_state_directory(self.workspace, state_dir=state_dir)
        store_path = resolved_state / "events.sqlite3"
        if not store_path.exists():
            return EventsResult(run_id=run_id, events=(), total=0)

        store = SqliteEventStore(store_path)
        range_q = EventRange(run_id=run_id, after_seq=str(after_seq)) if after_seq > 0 else EventRange(run_id=run_id)
        res = store.read(range_q)
        if not res.ok:
            raise RuntimeError(f"failed to read events: {getattr(res, 'error', 'store error')}")

        envelopes = list(res.value or ())
        if limit is not None and limit > 0:
            envelopes = envelopes[:limit]

        dict_events = [e.to_dict() for e in envelopes]
        return EventsResult(run_id=run_id, events=tuple(dict_events), total=len(dict_events))

    def artifact(
        self,
        *,
        digest: str,
        role: str = "artifact",
        state_dir: Path | str | None = None,
    ) -> ArtifactResult:
        """Retrieve artifact bytes and verify content digest before returning."""
        resolved_state = resolve_state_directory(self.workspace, state_dir=state_dir)
        blobs = FileBlobStore(resolved_state / "blobs")

        if hasattr(digest, "value"):
            clean_digest = str(digest.value).strip()
        else:
            clean_digest = str(digest).strip()

        if not blobs.has(clean_digest):
            return ArtifactResult(
                artifact_id=None,
                digest=clean_digest,
                content=None,
                role=role,
                verified=False,
                error="not_found",
            )

        content_res = blobs.get(clean_digest)
        if not content_res.ok or content_res.value is None:
            return ArtifactResult(
                artifact_id=None,
                digest=clean_digest,
                content=None,
                role=role,
                verified=False,
                error="not_found",
            )

        content = content_res.value

        # Verify digest
        expected_hex = clean_digest[7:] if clean_digest.startswith("sha256:") else clean_digest
        actual_hex = hashlib.sha256(content).hexdigest()

        if actual_hex != expected_hex:
            return ArtifactResult(
                artifact_id=None,
                digest=clean_digest,
                content=None,
                role=role,
                verified=False,
                error=f"digest mismatch: expected {expected_hex} but computed {actual_hex}",
            )

        return ArtifactResult(
            artifact_id=None,
            digest=clean_digest,
            content=content,
            role=role,
            verified=True,
            error=None,
        )

    def evidence(self, run_id: str, *, state_dir: Path | str | None = None) -> EvidenceResult:
        """Return the run's durable evidence projection through one query path."""
        events = self.events(run_id, state_dir=state_dir).events
        trajectory = next((e.get("payload", {}).get("trajectory") for e in reversed(events)
                           if isinstance(e.get("payload"), Mapping) and e.get("payload", {}).get("trajectory")), None)
        return EvidenceResult(
            run_id=run_id,
            status=self.status(run_id, state_dir=state_dir).status,
            event_count=len(events),
            trajectory=trajectory,
            event_digests=tuple(e.get("digest") for e in events if e.get("digest")),
            missing=() if trajectory is not None else ("trajectory",),
        )

    def cost(self, run_id: str, *, state_dir: Path | str | None = None) -> CostResult:
        """Return observed budget settlement; absent dimensions remain absent."""
        events = self.events(run_id, state_dir=state_dir).events
        totals: dict[str, int] = {}
        for event in events:
            payload = event.get("payload", {})
            settlement = payload.get("settlement") if isinstance(payload, Mapping) else None
            if isinstance(settlement, Mapping):
                for key, value in settlement.items():
                    if isinstance(value, int) and not isinstance(value, bool):
                        totals[str(key)] = totals.get(str(key), 0) + value
        return CostResult(
            run_id=run_id,
            observed=bool(totals),
            observed_cost=totals.get("usd_micros"),
            settlement=totals,
            missing=() if "usd_micros" in totals else ("observedCost",),
        )

    def doctor(
        self,
        *,
        profile_id: str = "product",
        state_dir: Path | str | None = None,
    ) -> DiagnosticsResult:
        """Inspect process health, profile readiness, and safe redacted diagnostics."""
        try:
            from vanguard import __version__
        except ImportError:
            __version__ = "0.9.3"

        checks: list[DiagnosticCheck] = []
        checks.append(DiagnosticCheck(
            name="version",
            status="ok",
            detail=__version__,
        ))
        checks.append(DiagnosticCheck(
            name="python",
            status="ok",
            detail=sys.version.split()[0],
        ))

        # Workspace check
        if self.workspace.is_dir():
            checks.append(DiagnosticCheck(name="workspace", status="ok", detail=str(self.workspace)))
        else:
            checks.append(DiagnosticCheck(
                name="workspace",
                status="error",
                detail=f"missing workspace directory {self.workspace}",
                remediation="create workspace directory or navigate to a valid project root",
            ))

        # State directory check
        resolved_state = resolve_state_directory(self.workspace, state_dir=state_dir)
        state_rep = inspect_state_directory(resolved_state)
        if state_rep.exists and state_rep.writable:
            checks.append(DiagnosticCheck(
                name="state_directory",
                status="ok",
                detail=f"{resolved_state} (writable, WAL)",
            ))
        elif state_rep.writable:
            checks.append(DiagnosticCheck(
                name="state_directory",
                status="ok",
                detail=f"{resolved_state} (creatable on run)",
            ))
        else:
            checks.append(DiagnosticCheck(
                name="state_directory",
                status="error",
                detail=state_rep.error or f"{resolved_state} is unwritable",
                remediation="fix filesystem permissions or specify --state-dir",
            ))

        # Platform sandbox check
        platform_facts = discover_platform().to_dict()
        has_enforcement = platform_facts.get("enforcement") == "full"
        checks.append(DiagnosticCheck(
            name="platform_sandbox",
            status="ok" if has_enforcement else "warn",
            detail=f"isolation enforcement: {platform_facts.get('enforcement')}",
            remediation="install bubblewrap for hermetic container isolation" if not has_enforcement else None,
        ))

        # Model providers check
        providers = inspect_model_providers()
        for p in providers:
            status = "ok" if p["readiness"] in ("ready", "configured") else "warn"
            checks.append(DiagnosticCheck(
                name=f"model_provider:{p['port']}",
                status=status,
                detail=p["detail"],
                remediation="set OPENROUTER_API_KEY for live provider models" if p["port"] == "openrouter" and not p["hasCredentials"] else None,
            ))

        overall_health = "healthy"
        overall_readiness = "ready"
        if any(c.status == "error" for c in checks):
            overall_health = "unhealthy"
            overall_readiness = "unready"
        elif any(c.status == "warn" for c in checks):
            overall_health = "degraded"

        return DiagnosticsResult(
            health=overall_health,
            readiness=overall_readiness,
            checks=tuple(checks),
            version=__version__,
        )

    def record_cassette(
        self,
        run_id: str,
        output_path: Path | str,
        *,
        state_dir: Path | str | None = None,
    ) -> Path:
        """Extract recorded model interactions from run artifacts and compile to a Cassette JSON (EVO-13)."""
        from ..adapters.models.cassette import Cassette

        resolved_state = resolve_state_directory(self.workspace, state_dir=state_dir)
        events_path = resolved_state / "events.sqlite3"
        if not events_path.exists():
            events_path = resolved_state / "events.db"
        blobs_path = resolved_state / "blobs"

        if not events_path.exists():
            raise FileNotFoundError(f"No events database found at {events_path}")

        store = SqliteEventStore(events_path)
        blobs = FileBlobStore(blobs_path) if blobs_path.exists() else None

        res = store.read(EventRange(run_id=run_id))
        if not res.ok or not res.value:
            raise ValueError(f"Run {run_id} contains no recorded events")

        cassette = Cassette()
        # Collect model_io claims and artifact pairs
        for env in res.value:
            payload = env.payload if isinstance(env.payload, Mapping) else {}
            # Check model_io claim
            if payload.get("kind") == "EvidenceClaimProduced" and payload.get("reason") == "model_io":
                val = payload.get("value", {})
                in_dig = val.get("inputDigest")
                out_dig = val.get("outputDigest")
                if blobs and in_dig and out_dig:
                    in_res = blobs.get(in_dig)
                    out_res = blobs.get(out_dig)
                    in_bytes = in_res.value if hasattr(in_res, "value") else in_res
                    out_bytes = out_res.value if hasattr(out_res, "value") else out_res
                    if in_bytes and out_bytes:
                        try:
                            prompt_json = json.loads(in_bytes.decode("utf-8"))
                            output_json = json.loads(out_bytes.decode("utf-8"))
                            cassette.add_record(
                                context=prompt_json,
                                tools=prompt_json.get("tools", []),
                                sampling=prompt_json.get("sampling", {}),
                                proposal=output_json,
                                recorded_at=env.occurred_at,
                            )
                            continue
                        except Exception:
                            pass

            if payload.get("kind") == "TurnCompleted":
                context = payload.get("context", {})
                input_ref = context.get("model_input_ref")
                output_ref = context.get("model_output_ref")
                if blobs and input_ref and output_ref:
                    in_res = blobs.get(input_ref)
                    out_res = blobs.get(output_ref)
                    in_bytes = in_res.value if hasattr(in_res, "value") else in_res
                    out_bytes = out_res.value if hasattr(out_res, "value") else out_res
                    if in_bytes and out_bytes:
                        try:
                            prompt_json = json.loads(in_bytes.decode("utf-8"))
                            output_json = json.loads(out_bytes.decode("utf-8"))
                            cassette.add_record(
                                context=prompt_json,
                                tools=prompt_json.get("tools", []),
                                sampling=prompt_json.get("sampling", {}),
                                proposal=output_json,
                                recorded_at=env.occurred_at,
                            )
                            continue
                        except Exception:
                            pass
                if "proposal" in payload:
                    cassette.add_record(
                        context={"brief": payload.get("brief", "")},
                        tools=[],
                        sampling={},
                        proposal=payload["proposal"],
                        recorded_at=env.occurred_at,
                    )

        out_p = Path(output_path).resolve()
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(cassette.to_json(), encoding="utf-8")
        return out_p

    def export_diagnostic_bundle(
        self,
        output_path: Path | str,
        *,
        profile_id: str = "product",
        state_dir: Path | str | None = None,
    ) -> Path:
        """Export a scrubbed, secret-free diagnostic bundle (.zip) for support and debugging (EVO-15)."""
        import platform
        import re
        import zipfile

        out_p = Path(output_path).resolve()
        out_p.parent.mkdir(parents=True, exist_ok=True)

        diag = self.doctor(profile_id=profile_id, state_dir=state_dir)
        resolved_state = resolve_state_directory(self.workspace, state_dir=state_dir)

        system_info = {
            "platform": platform.platform(),
            "python_version": sys.version,
            "architecture": list(platform.architecture()),
            "processor": platform.processor(),
            "vanguard_version": diag.version,
            "workspace": str(self.workspace),
        }

        state_metrics: dict[str, Any] = {"state_dir": str(resolved_state), "exists": resolved_state.exists()}
        if resolved_state.exists():
            events_file = resolved_state / "events.db"
            state_metrics["events_db_size_bytes"] = events_file.stat().st_size if events_file.exists() else 0
            blobs_dir = resolved_state / "blobs"
            if blobs_dir.exists():
                blobs = list(blobs_dir.rglob("*"))
                state_metrics["blob_count"] = sum(1 for b in blobs if b.is_file())
            else:
                state_metrics["blob_count"] = 0

        with zipfile.ZipFile(out_p, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("system_info.json", json.dumps(system_info, indent=2))
            zf.writestr("doctor_report.json", json.dumps(diag.to_dict(), indent=2))
            zf.writestr("state_metrics.json", json.dumps(state_metrics, indent=2))

            logs_dir = resolved_state / "logs"
            if logs_dir.exists() and logs_dir.is_dir():
                for log_file in logs_dir.glob("*.log"):
                    try:
                        content = log_file.read_text(encoding="utf-8", errors="replace")
                        scrubbed = re.sub(r"(sk-[A-Za-z0-9_-]{20,})", "[REDACTED_API_KEY]", content)
                        scrubbed = re.sub(r"(Bearer\s+[A-Za-z0-9._-]{20,})", "Bearer [REDACTED_TOKEN]", scrubbed)
                        zf.writestr(f"logs/{log_file.name}", scrubbed)
                    except Exception:
                        pass

        return out_p
