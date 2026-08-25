"""Thin generic product entrypoint for ``vg code`` and ``vg explain``."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Mapping

from ..adapters.models.openrouter import OpenRouterModel
from ..adapters.models.fake import FakeModel
from ..adapters.models.ollama import OllamaModel
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
    try:
        resolved = resolve_profile(
            profile_id, host_qualifies=facts.get("enforcement") == "full", host_facts=facts)
        outcome, detail = "completed", json.dumps(facts, sort_keys=True)
        digest = resolved.digest
    except SandboxUnavailable as exc:
        outcome, detail, digest = "unavailable", str(exc), None
    return {"type": "result", "result": {
        "runId": str(request.get("runId") or "doctor"), "outcome": outcome,
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
    run_id = str(request.get("runId") or request.get("resumeFrom") or "run-cli")
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
    # choice.  It must reach the same Runtime path without touching a provider;
    # it is never promotion-eligible evidence.
    fake_backend = request.get("fakeBackend")
    model_port = str(request.get("modelPort") or "").strip().lower()
    planner_model = str(request.get("plannerModel") or "openrouter/free")
    if isinstance(fake_backend, str) and fake_backend:
        selected_model = FakeModel([{"kind": "finish", "note": "deterministic preview"}])
    elif model_port == "lam":
        from .model_selection import select_model
        selected_model = select_model("lam", model_name=planner_model if planner_model != "openrouter/free" else None).model
    elif model_port == "ollama":
        selected_model = OllamaModel(
            model=planner_model,
            endpoint=os.environ.get("VANGUARD_OLLAMA_ENDPOINT", "http://127.0.0.1:11434/api/chat"),
            timeout_seconds=float(request.get("modelTimeoutSeconds") or 300.0),
        )
    else:
        selected_model = OpenRouterModel(model=planner_model)
    result = Runtime.execute_profiled(
        _manifest(command), task,
        profile_id=str(request.get("profile") or "product"),
        model=selected_model,
        store_path=(str(request["storePath"]) if request.get("storePath") else None),
        interactive=bool(request.get("interactive", True)),
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
    projections.append({"kind": "complete", "outcome": outcome, "turns": int(getattr(result.telemetry, "turns", 0))})
    return {"type": "result", "result": {
        "runId": run_id, "outcome": outcome, "phase": "complete", "attempts": 1,
        "turns": int(getattr(result.telemetry, "turns", 0)),
        "planDigest": result.run_digest or None, "activeStepId": None,
        "verifiedStepIds": [], "modelRoutes": [], "promptTokens": None,
        "completionTokens": None, "spentUsdMicros": None, "detail": result.detail,
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
            frame = {"type": "result", "result": {
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
