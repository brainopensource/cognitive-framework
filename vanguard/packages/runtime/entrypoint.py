"""Thin generic product entrypoint for ``vg code`` and ``vg explain``."""

from __future__ import annotations

import json
import sys
import uuid
from pathlib import Path
from typing import Any, Mapping

from ..adapters.models.fake import FakeModel
from ..adapters.stores.blob_store import FileBlobStore
from ..adapters.stores.event_store import SqliteEventStore
from ..adapters.sandbox.platform import discover_platform
from ..ports.event_store import EventRange
from .app_service import project_receipts, project_terminal_outcome
from .compose import TaskContext
from .evidence_capture import (
    last_kind_payload,
    qualify_candidate_identity,
    submitted_workspace_digests,
)
from . import pack_catalog
from .profiles import SandboxUnavailable, resolve_profile
from .root import Runtime
from .session import WorkspaceSnapshotRefused
from ..agency.context.packet import ContextPacketError
from .task_state import episode_id_from_events, fold_task_state


def _manifest(command: str, preset: str | None = None) -> Path:
    """Resolve the installed manifest a product command selects.

    T-102. The preset allowlist and the manifest lookup both live in
    ``pack_catalog``; this surface owns no second copy of either.
    """
    if command == "explain":
        return pack_catalog.manifest_path("vg-code-explain")
    if command == "code":
        return pack_catalog.preset_manifest_path(preset)
    return pack_catalog.manifest_path("vg-code-default")


def _resolve_turn_ceiling(preset: str, explicit: Any) -> int:
    """Loop bound: omitted uses the catalog; explicit may only attenuate."""
    return pack_catalog.turn_ceiling(preset, explicit)


def _completion_policy(manifest_path: Path) -> Any:
    """Resolve the pack-owned completion policy for the public product path."""
    from .app_service import ApplicationService

    return ApplicationService._pack_completion_policy(manifest_path)


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


def _durable_turn_ceiling(events: Any) -> int | None:
    """The turn ceiling this run was actually opened under, from the ledger.

    `EpisodeStarted` records `maxTurns` before a provider sees a prompt, so it
    is the authorised bound rather than whatever the current ingress resolved.
    The *first* such record wins: a later episode in the same run inherits the
    ceiling it was opened with, and taking the maximum would let one widened
    re-entry raise the bound for every continuation after it.
    """
    for event in events:
        payload = getattr(event, "payload", None)
        if not isinstance(payload, Mapping):
            continue
        raw = payload.get("maxTurns")
        if isinstance(raw, bool):
            continue
        if isinstance(raw, int) or (isinstance(raw, str) and raw.isdigit()):
            return int(raw)
    return None


def _events_to_hydrate(command: str, events: Any) -> list[Any]:
    """Durable events that must hydrate this ingress.

    Hydration is keyed on **state**, not on the command verb. ``command`` is
    accepted so a mutation probe can restore the pre-T-145
    ``command == "resume"`` guard and prove the suite reds (`DIR-5.5`).
    """
    del command
    return list(events)


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
    preset = str(request.get("preset") or "balanced").strip().lower()
    harness_override = str(request.get("harness") or "").strip()
    explicit_turns = request.get("maxTurnsPerEpisode")
    if harness_override:
        manifest_path = pack_catalog.manifest_path(harness_override)
        max_turns = (
            pack_catalog.DEFAULT_TURN_CEILING if explicit_turns in (None, "")
            else int(explicit_turns))
    else:
        # ``_manifest`` validates the preset against the catalog, so this
        # surface raises on an unknown preset without holding its own list.
        manifest_path = _manifest(command, preset if command == "code" else None)
        if command == "code":
            max_turns = _resolve_turn_ceiling(preset, explicit_turns)
        else:
            max_turns = (
                pack_catalog.DEFAULT_TURN_CEILING if explicit_turns in (None, "")
                else int(explicit_turns))
    repo_path = Path(str(request.get("workspace", "."))).resolve()
    configured_store_path = (
        Path(str(request["storePath"])) if request.get("storePath") else
        repo_path / ".vanguard" / "events.sqlite3"
    )
    resume_state = None
    episode_id = f"episode-{run_id}"
    project_id = str(request.get("projectId") or "coding-preview")
    # `E-CLI-2`. Hydration is keyed on **durable state**, not on the command
    # verb. A run whose store already holds events for its `run_id` is a
    # continuation whatever the operator typed; conditioning continuity on
    # `command == "resume"` meant a `code` re-invocation of a known run started
    # with no spent budget, no revoked grants and no effect in flight -- the
    # continuity T-131.7 and T-142 establish, bypassed by a word.
    #
    # Nothing here trusts the durable state. `fold_task_state` derives spend,
    # transitively-revoked authority and unresolved effects from the ledger, so
    # hydration cannot replenish a budget or re-widen a grant; and the folded
    # `selectionPolicyIdentity` carries the prior `behaviorIdentity`, which
    # `HarnessSession._assert_resume_behavior_identity` rejects on a changed
    # composition, preset, model route or context policy. This ingress adds the
    # one revalidation the ledger records and the session cannot see: the turn
    # ceiling, which is resolved *here* from the preset and would otherwise let
    # a continuation buy turns the original run never had.
    store = SqliteEventStore(str(configured_store_path))
    try:
        read = store.read(EventRange(run_id=run_id))
    finally:
        store.close()
    if command == "resume" and not read.ok:
        detail = read.error.message if read.error is not None else "ledger unavailable"
        raise ValueError(f"resume state unavailable: {detail}")
    events = list(read.value or ()) if read.ok else []
    if command == "resume" and not events:
        raise ValueError(f"resume state unavailable: no durable events for {run_id}")
    events = _events_to_hydrate(command, events)
    if events:
        resumed = fold_task_state(events, objective=brief)
        resume_state = resumed.to_canonical_dict()
        if resumed.objective:
            brief = resumed.objective
        episode_id = episode_id_from_events(events, run_id=run_id)
        first_project = next(
            (str(getattr(event, "project_id", "")) for event in events
             if str(getattr(event, "project_id", ""))),
            "",
        )
        if first_project and not request.get("projectId"):
            project_id = first_project
        durable_turns = _durable_turn_ceiling(events)
        if durable_turns is not None and max_turns > durable_turns:
            # Fail closed, and closed means the *narrower* bound is refused
            # rather than silently applied: a continuation that asked for more
            # turns than the run was authorised is a different run, and
            # quietly clamping it would report the operator's ceiling back to
            # them as if it had been honoured.
            raise ValueError(
                f"resume state unavailable: run {run_id} was authorised for "
                f"{durable_turns} turns; this ingress resolved {max_turns}. "
                "A continuation may not widen the turn ceiling.")
    task = TaskContext(
        brief=brief, repo_path=repo_path,
        run_id=run_id, episode_id=episode_id,
        project_id=project_id, max_turns=max_turns,
        resume_state=resume_state,
    )
    # The client-side deterministic smoke backend is an explicit, non-release
    fake_backend = request.get("fakeBackend")
    from .model_selection import select_model
    injected = request.get("injectedModel")
    if injected is not None:
        selected_model = injected
    elif fake_backend:
        selected_model = FakeModel([{"kind": "finish", "note": "deterministic preview"}])
    else:
        model_port = str(request.get("modelPort") or "openrouter").strip().lower()
        planner_model = str(request.get("plannerModel") or "")
        selected_model = select_model(
            model_port,
            model_name=planner_model if planner_model and planner_model not in {"free", "default", "openrouter/free"} else None,
            timeout_seconds=float(request.get("modelTimeoutSeconds") or 300.0) if request.get("modelTimeoutSeconds") else None,
            # A ceiling limits already-authorised spend; it is not itself
            # consent to spend. Product clients set ``allowPaid`` from an
            # explicit operator action (for the CLI, ``--budget-usd``).
            allow_paid=bool(request.get("allowPaid", False)),
        ).model
    # Product runs and explicit previews use a real content-addressed store;
    # topology artifact edges must never point at ephemeral process state.
    # The fake model remains an explicit preview choice, but its captured
    # material is still kept in the same installation state directory.
    try:
        result = Runtime.execute_profiled(
            manifest_path, task,
            profile_id=str(request.get("profile") or "product"),
            model=selected_model,
            store_path=str(configured_store_path),
            interactive=bool(request.get("interactive", True)),
            blobs=FileBlobStore(configured_store_path.parent / "blobs"),
            completion_policy=_completion_policy(manifest_path),
        )
    except (WorkspaceSnapshotRefused, ContextPacketError) as refused:
        # `E4`. A fail-closed refusal must reach the operator as a *terminal*,
        # not as a traceback. Two kinds arrive here:
        #
        # `WorkspaceSnapshotRefused` (`E-CLI-1`(b)) -- admission already
        # refuses an unobservable workspace, so nothing should reach here; the
        # other workspace-identity bindings raise the same typed refusal and
        # must not escape either.
        #
        # `ContextPacketError` (`E-CLI-2`) -- the revalidation that rejects a
        # continuation whose composition, preset, model route or context
        # policy moved. Hydrating on durable state made this guard reachable
        # from every ingress rather than only from `resume`, so its refusal
        # became a public-route outcome and had to become a typed one.
        #
        # Neither is ever converted into a completion: `undeterminable` is
        # what the run genuinely is when identity could not be established.
        kind = getattr(refused, "kind", "") or type(refused).__name__
        code = ("WORKSPACE_UNOBSERVABLE"
                if isinstance(refused, WorkspaceSnapshotRefused)
                else "CONTINUATION_REVALIDATION_REFUSED")
        message = getattr(refused, "message", "") or str(refused)
        return {"type": "result", "runId": run_id, "result": {
            "runId": run_id, "outcome": "undeterminable",
            "phase": "complete", "attempts": 0, "turns": 0,
            "planDigest": None, "activeStepId": None, "verifiedStepIds": [],
            "modelRoutes": [], "promptTokens": None, "completionTokens": None,
            "spentUsdMicros": None,
            "detail": f"{code}[{kind}]: {message}",
            "projections": [
                {"kind": "error", "detail": f"{code}: {message}"},
                {"kind": "complete", "outcome": "undeterminable", "turns": 0},
            ],
        }}
    # NT-B04. One projection rule, shared with the application service; this
    # surface does not own a second copy of it.
    outcome = project_terminal_outcome(result.terminal)
    if str(getattr(result, "detail", "") or "").startswith("WORKSPACE_UNOBSERVABLE"):
        # Session already typed the refusal as a RunResult. Do not project
        # `abandoned` as if the model gave up: the workspace was unobservable.
        outcome = "undeterminable"
    projections: list[dict[str, Any]] = project_receipts(result)
    # The ledger already carries verification, spend, approval, recovery and
    # sub-agent lifecycle. Projecting only fs/proc receipts left `--headless`
    # unable to report why a run failed or what it cost, so fold the event
    # stream too. Unknown kinds are skipped, never guessed at (CT-44).
    last_note = ""
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
        elif kind == "BudgetExhausted":
            projections.append({
                "kind": "budget",
                "detail": str(payload.get("dimension") or "limit reached"),
            })

    if last_note:
        projections.append({"kind": "note", "text": last_note})
    projections.append({"kind": "complete", "outcome": outcome, "turns": int(getattr(result.telemetry, "turns", 0))})
    # T-85. The receipt is projected through the *same* mapping the
    # application service uses (`_result_from_execution`), so the product
    # path cannot drift from a second, private receipt algebra. Verified
    # steps come from the folded ledger, never from a bespoke event this
    # function emits for itself.
    from .app_service import ApplicationService

    state_dir = configured_store_path.parent
    task_state = ApplicationService._read_task_state(
        state_dir, run_id, fallback=brief,
    )
    run_result = ApplicationService._result_from_execution(
        run_id=run_id, outcome=outcome, phase="complete",
        turns=int(getattr(result.telemetry, "turns", 0)),
        plan_digest=result.run_digest or None, detail=result.detail,
        projections=tuple(projections), episode_id=task.episode_id,
        execution=result, task_state=task_state,
    )
    # A step counts as verified when the ledger carries both a terminal
    # status and the receipt that earned it. A `complete` TODO with no
    # receipt digest is an unevidenced claim and is not projected.
    verified_step_ids = [
        str(item.todo_id) for item in task_state.todo_items
        if item.status == "complete" and item.receipt_digest
    ]
    active_step_id = next(
        (str(item.todo_id) for item in task_state.todo_items
         if item.status == "in_progress"), None,
    )
    usage = run_result.token_usage or {}
    # T-131.6. Qualify the published receipt against the submitted tree using
    # the existing candidate snapshot and DIR-D1 carriers. A green claim that
    # names any other tree is an instrument failure, not a terminal mapping.
    events = getattr(result, "events", ()) or ()
    verification = last_kind_payload(events, "VerificationRecorded")
    if verification is None and run_result.verification_identity:
        verification = dict(run_result.verification_identity)
    trajectory = result.trajectory if isinstance(getattr(result, "trajectory", None), Mapping) else {}
    artifacts = trajectory.get("artifacts") if isinstance(trajectory.get("artifacts"), (list, tuple)) else ()
    qualification = qualify_candidate_identity(
        submitted_digests=submitted_workspace_digests(task.repo_path),
        task_digest=run_result.task_digest,
        composition_digest=run_result.composition_digest,
        verification=verification,
        change_surface=last_kind_payload(events, "ChangeSurfaceUpdated"),
        captured_artifacts=artifacts,
    )
    detail = run_result.detail
    claims_green = (
        outcome == "completed"
        and isinstance(verification, Mapping)
        and verification.get("exitCode") == 0
    )
    if claims_green and not qualification["qualified"]:
        outcome = "instrument_error"
        reason = qualification.get("reason") or "VERIFICATION_STALE"
        detail = f"EVIDENCE_IDENTITY: {reason}"
        if projections and projections[-1].get("kind") == "complete":
            projections[-1] = {**projections[-1], "outcome": outcome}
    identity = qualification.get("identity") or run_result.verification_identity
    return {"type": "result", "runId": run_id, "result": {
        "runId": run_id, "outcome": outcome, "phase": "complete", "attempts": 1,
        "turns": run_result.turns,
        "planDigest": run_result.plan_digest, "activeStepId": active_step_id,
        "verifiedStepIds": verified_step_ids,
        "modelRoutes": [run_result.model_route] if run_result.model_route else [],
        "promptTokens": usage.get("promptTokens"),
        "completionTokens": usage.get("completionTokens"),
        "spentUsdMicros": run_result.observed_cost,
        "taskDigest": run_result.task_digest,
        "compositionDigest": run_result.composition_digest,
        "candidateDigest": qualification.get("candidateDigest"),
        "verificationIdentity": dict(identity) if identity else None,
        "projections": projections,
        "detail": detail,
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
