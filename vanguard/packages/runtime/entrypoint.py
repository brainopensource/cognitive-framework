"""Thin generic product entrypoint for ``vg code`` and ``vg explain``."""

from __future__ import annotations

import json
import os
import sys
import uuid
from pathlib import Path
from typing import Any, Mapping

from ..adapters.models.openrouter import OpenRouterModel
from ..adapters.models.fake import FakeModel
from ..adapters.models.llama_cpp import LlamaCppModel
from ..adapters.stores.event_store import SqliteEventStore
from ..adapters.stores.blob_store import FileBlobStore
from ..adapters.sandbox.platform import discover_platform
from .compose import TaskContext
from .profiles import SandboxUnavailable, resolve_profile
from .root import Runtime


def _root() -> Path:
    return Path(os.environ.get("VANGUARD_ROOT", Path(__file__).resolve().parents[3]))


def _manifest(command: str) -> Path:
    name = "vg-code-explain" if command == "explain" else "vg-code-default"
    return _root() / "vanguard/packages/agency/manifests" / name / "manifest.json"


def _doctor(request: Mapping[str, Any]) -> dict[str, Any]:
    facts = dict(discover_platform().to_dict())
    profile_id = str(request.get("profile") or "product")
    run_id = str(request.get("runId") or "doctor")
    try:
        resolved = resolve_profile(
            profile_id, host_qualifies=facts.get("enforcement") == "full", host_facts=facts)
        outcome, detail = "completed", json.dumps(facts, sort_keys=True)
        digest = resolved.digest
    except SandboxUnavailable as exc:
        outcome, detail, digest = "unavailable", str(exc), None
    return {"type": "result", "runId": run_id, "result": {
        "runId": run_id, "outcome": outcome,
        "phase": "doctor", "attempts": 0, "turns": 0, "planDigest": digest,
        "activeStepId": None, "verifiedStepIds": [], "modelRoutes": [],
        "promptTokens": None, "completionTokens": None, "spentUsdMicros": None,
        "detail": detail, "projections": [{"kind": "route", "facts": facts}],
    }}


def execute(request: Mapping[str, Any]) -> dict[str, Any]:
    command = str(request.get("command", "code"))
    if command == "doctor":
        return _doctor(request)
    if command not in {"code", "explain", "resume"}:
        raise ValueError(f"unsupported coding command: {command!r}")
    resume_target = request.get("resumeFrom") or (request.get("runId") if command == "resume" else None)
    if resume_target and str(resume_target).strip():
        run_id = str(resume_target).strip()
    elif request.get("runId") and str(request["runId"]).strip():
        run_id = str(request["runId"]).strip()
    else:
        run_id = f"run-{uuid.uuid4().hex}"
    brief = str(request.get("brief") or request.get("question") or (f"Resume run {run_id}" if command == "resume" else "")).strip()
    if not brief:
        raise ValueError("brief or question is required")
    task = TaskContext(
        brief=brief, repo_path=Path(str(request.get("workspace", "."))).resolve(),
        run_id=run_id, episode_id=f"episode-{run_id}",
        project_id=str(request.get("projectId") or "coding-preview"),
        max_turns=int(request.get("maxTurnsPerEpisode") or 40),
    )
    # The client-side deterministic smoke backend is an explicit, non-release
    fake_backend = request.get("fakeBackend")
    from .model_selection import select_model
    if fake_backend:
        selected_model = FakeModel([{"kind": "finish", "note": "deterministic preview"}])
    else:
        model_port = str(request.get("modelPort") or "openrouter").strip().lower()
        planner_model = str(request.get("plannerModel") or "")
        selected_model = select_model(
            model_port,
            model_name=planner_model if planner_model and planner_model not in {"free", "default", "openrouter/free"} else None,
            timeout_seconds=float(request.get("modelTimeoutSeconds") or 300.0) if request.get("modelTimeoutSeconds") else None,
            allow_paid=bool(request.get("allowPaid", False)) or (int(request.get("budgetUsdMicros") or 0) > 0) or (int(request.get("maxPaidCalls") or 0) > 0),
        ).model
    # A deterministic preview is a hermetic smoke path, not a durable run.
    # Keep it out of the product profile's default persistent ledger: a
    # fixed identity would otherwise resume stale approval
    # events from a previous invocation and exhaust the episode budget.
    preview_store = SqliteEventStore(":memory:") if fake_backend else None
    configured_store_path = (
        Path(str(request["storePath"])) if request.get("storePath") else
        task.repo_path / ".vanguard" / "events.sqlite3"
    )
    # Product runs and explicit previews use a real content-addressed store;
    # topology artifact edges must never point at ephemeral process state.
    # The fake model remains an explicit preview choice, but its captured
    # material is still kept in the same installation state directory.
    result = Runtime.execute_profiled(
        _manifest(command), task,
        profile_id=str(request.get("profile") or "product"),
        model=selected_model,
        store=preview_store,
        store_path=(str(configured_store_path) if not fake_backend else None),
        interactive=bool(request.get("interactive", True)),
        blobs=FileBlobStore(configured_store_path.parent / "blobs"),
    )
    terminal = str(getattr(result.terminal, "value", result.terminal))
    outcome = "completed" if terminal in {"completed", "abstained"} else terminal
    projections: list[dict[str, Any]] = []
    for rec in getattr(result, "receipts", ()) or ():
        verb = getattr(rec, "verb", "")
        rec_outcome = getattr(rec, "outcome", "")
        rec_detail = getattr(rec, "detail", "")
        if verb == "fs.read":
            projections.append({"kind": "read", "path": rec_detail or "file"})
        elif verb in ("patch.apply", "fs.patch", "fs.write"):
            projections.append({"kind": "write", "path": rec_detail or "patch", "text": rec_outcome})
        elif verb == "proc.exec":
            projections.append({"kind": "test", "path": rec_detail or "exec", "exitCode": 0 if rec_outcome == "ok" else 1})
    # The ledger already carries verification, spend, approval, recovery and
    # sub-agent lifecycle. Projecting only fs/proc receipts left `--headless`
    # unable to report why a run failed or what it cost, so fold the event
    # stream too. Unknown kinds are skipped, never guessed at (CT-44).
    last_note = ""
    spent_micros = 0
    for ev in getattr(result, "events", ()) or ():
        kind = getattr(ev, "kind", "")
        payload = getattr(ev, "payload", {}) or {}

        if kind == "ProposalProduced":
            note = payload.get("note")
            if note:
                last_note = str(note)
        elif kind == "ReflectionProduced":
            text = payload.get("reflection") or payload.get("text")
            if text:
                projections.append({"kind": "reflect", "text": str(text)})
        elif kind == "PlanRevised":
            steps = payload.get("steps")
            entry: dict[str, Any] = {"kind": "plan"}
            if isinstance(steps, (list, tuple)):
                entry["stepTotal"] = len(steps)
            if payload.get("plan"):
                entry["text"] = str(payload["plan"])
            projections.append(entry)
        elif kind == "EffectFailed":
            projections.append({
                "kind": "error",
                "detail": str(payload.get("error") or payload.get("reason") or "effect failed"),
            })
        elif kind == "EffectRejected":
            projections.append({
                "kind": "error",
                "detail": str(payload.get("reason") or "rejected by policy"),
            })
        elif kind == "VerdictRecorded":
            entry = {"kind": "verdict", "verdict": str(payload.get("verdict") or "recorded")}
            if payload.get("detail"):
                entry["detail"] = str(payload["detail"])
            projections.append(entry)
        elif kind in ("ApprovalRequested", "ApprovalResolved"):
            projections.append({
                "kind": "approval",
                "status": "requested" if kind == "ApprovalRequested" else str(
                    payload.get("decision") or "resolved"
                ),
                "action": str(payload.get("action") or "mutating action"),
            })
        elif kind == "CheckpointCreated":
            projections.append({
                "kind": "checkpoint",
                "checkpointId": str(payload.get("checkpointId") or payload.get("id") or "created"),
                "branchId": str(payload.get("branchId") or "main"),
            })
        elif kind == "ChildSpawned":
            projections.append({
                "kind": "child",
                "childId": str(payload.get("childRunId") or payload.get("childId") or ""),
                "role": str(payload.get("role") or "sub-agent"),
            })
        elif kind == "ChildReturned":
            projections.append({
                "kind": "child",
                "childId": str(payload.get("childRunId") or payload.get("childId") or ""),
                "role": str(payload.get("role") or "sub-agent"),
                "outcome": str(payload.get("outcome") or "returned"),
            })
        elif kind == "ContextCompacted":
            entry = {"kind": "context"}
            for src, dst in (("beforeTokens", "beforeTokens"), ("afterTokens", "afterTokens")):
                value = payload.get(src)
                if isinstance(value, int):
                    entry[dst] = value
            projections.append(entry)
        elif kind == "ConflictDetected":
            projections.append({
                "kind": "conflict",
                "detail": str(payload.get("summary") or payload.get("detail") or "detected"),
            })
        elif kind in ("CapabilityGranted", "CapabilityRevoked", "CapabilityAttenuated"):
            projections.append({
                "kind": "capability",
                "status": kind.replace("Capability", "").lower(),
                "capability": str(payload.get("capability") or payload.get("name") or "unnamed"),
            })
        elif kind == "BudgetCommitted":
            micros = payload.get("usdMicros") or payload.get("costMicros")
            if isinstance(micros, int):
                spent_micros += micros
        elif kind == "BudgetExhausted":
            projections.append({
                "kind": "budget",
                "detail": str(payload.get("dimension") or "limit reached"),
            })

    if last_note:
        projections.append({"kind": "note", "text": last_note})
    projections.append({"kind": "complete", "outcome": outcome, "turns": int(getattr(result.telemetry, "turns", 0))})
    return {"type": "result", "runId": run_id, "result": {
        "runId": run_id, "outcome": outcome, "phase": "complete", "attempts": 1,
        "turns": int(getattr(result.telemetry, "turns", 0)),
        "planDigest": result.run_digest or None, "activeStepId": None,
        "verifiedStepIds": [], "modelRoutes": [], "promptTokens": None,
        "completionTokens": None,
        "spentUsdMicros": spent_micros or None, "detail": result.detail,
        "projections": projections,
    }}


def main() -> int:
    if "--stdin-json" not in sys.argv:
        print("entrypoint requires --stdin-json", file=sys.stderr)
        return 2
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            frame = execute(json.loads(line))
        except Exception as exc:
            frame = {"type": "result", "runId": "unknown", "result": {
                "runId": "unknown", "outcome": "instrument_error", "phase": "failed",
                "attempts": 0, "turns": 0, "planDigest": None, "activeStepId": None,
                "verifiedStepIds": [], "modelRoutes": [], "promptTokens": None,
                "completionTokens": None, "spentUsdMicros": None, "detail": str(exc),
                "projections": [],
            }}
        print(json.dumps(frame, separators=(",", ":")), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
