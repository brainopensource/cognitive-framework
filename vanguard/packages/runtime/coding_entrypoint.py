"""Thin generic product entrypoint for ``vg code`` and ``vg explain``."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Mapping

from ..adapters.models.openrouter import OpenRouterModel
from ..adapters.models.fake import FakeModel
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
    profile_id = str(request.get("profile") or "local")
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
    if command not in {"code", "explain"}:
        raise ValueError(f"unsupported coding command: {command!r}")
    brief = str(request.get("brief") or request.get("question") or "").strip()
    if not brief:
        raise ValueError("brief or question is required")
    run_id = str(request.get("runId") or "run-cli")
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
    selected_model = (
        FakeModel([{"kind": "finish", "note": "deterministic preview"}])
        if isinstance(fake_backend, str) and fake_backend
        else OpenRouterModel(model=str(request.get("plannerModel") or "openrouter/free"))
    )
    result = Runtime.execute_profiled(
        _manifest(command), task,
        profile_id=str(request.get("profile") or "local"),
        model=selected_model,
        interactive=bool(request.get("interactive", False)),
    )
    terminal = str(getattr(result.terminal, "value", result.terminal))
    outcome = "completed" if terminal in {"completed", "abstained"} else terminal
    return {"type": "result", "result": {
        "runId": run_id, "outcome": outcome, "phase": "complete", "attempts": 1,
        "turns": int(getattr(result.telemetry, "turns", 0)),
        "planDigest": result.run_digest or None, "activeStepId": None,
        "verifiedStepIds": [], "modelRoutes": [], "promptTokens": None,
        "completionTokens": None, "spentUsdMicros": None, "detail": result.detail,
        "projections": [{"kind": "complete", "outcome": outcome}],
    }}


def main() -> int:
    if "--stdin-json" not in sys.argv:
        print("coding_entrypoint requires --stdin-json", file=sys.stderr)
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
