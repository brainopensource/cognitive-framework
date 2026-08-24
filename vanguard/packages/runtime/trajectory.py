"""Assemble `mhf.trajectory/1` at episode completion (1.3-D, F-12, RF-23, ADR-0078)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from ..domain.canonicalisation.digest import digest_of
from ..kernel.model import Event


def signed_verdict_object(verdict: Any) -> Mapping[str, Any] | None:
    binding = getattr(verdict, "binding", None)
    signature = getattr(verdict, "signature", None)
    if not binding or not signature:
        return None
    return {**dict(binding), "signature": signature}


def _resolve_model_route(model: Any, ctx: Mapping[str, Any] | None = None) -> dict[str, Any]:
    provider = getattr(model, "provider", None) or (ctx.get("provider") if ctx else None)
    model_name = getattr(model, "model", None) or getattr(model, "model_name", None) or (ctx.get("model") if ctx else None)
    if not provider:
        cls_name = type(model).__name__.lower() if model is not None else ""
        if "fake" in cls_name:
            provider = "fake"
            model_name = model_name or "fake-model"
        elif "scripted" in cls_name:
            provider = "scripted"
            model_name = model_name or "scripted-cassette"
        elif "ollama" in cls_name:
            provider = "ollama"
            model_name = model_name or "deepseek-r1"
        elif "openrouter" in cls_name:
            provider = "openrouter"
            model_name = model_name or "openrouter-default"
        else:
            provider = "scripted"
            model_name = model_name or "default-model"
    else:
        model_name = model_name or "default-model"

    fingerprint = getattr(model, "model_fingerprint", None) or (ctx.get("model_fingerprint") if ctx else None)
    reason = getattr(model, "fingerprint_unavailable_reason", None) or (ctx.get("fingerprint_unavailable_reason") if ctx else None)
    if not fingerprint and not reason:
        reason = "provider_did_not_report"

    return {
        "provider": str(provider),
        "model": str(model_name),
        "model_fingerprint": fingerprint,
        "fingerprint_unavailable_reason": reason,
    }


def _compute_turn_cost(
    ctx: Mapping[str, Any],
    proposal_payload: Mapping[str, Any],
    route: dict[str, Any],
) -> dict[str, Any]:
    prompt_tokens = ctx.get("prompt_tokens")
    completion_tokens = ctx.get("completion_tokens")
    if prompt_tokens is not None or completion_tokens is not None:
        tokens = int(prompt_tokens or 0) + int(completion_tokens or 0)
        tokens_status = "measured"
    else:
        ctx_tokens = len(str(ctx).split())
        prop_tokens = len(str(proposal_payload).split())
        tokens = max(ctx_tokens + prop_tokens, 1)
        tokens_status = "estimated"

    ctx_bytes = len(str(ctx).encode("utf-8"))
    prop_bytes = len(str(proposal_payload).encode("utf-8"))
    bytes_val = max(ctx_bytes + prop_bytes, 1)
    bytes_status = "measured"

    cost_micros = ctx.get("usd_micros") or ctx.get("cost_micros")
    if cost_micros is not None:
        usd_micros = int(cost_micros)
        usd_status = "measured"
    elif route["provider"] in ("scripted", "fake", "mock", "ollama"):
        usd_micros = 0
        usd_status = "measured"
    else:
        usd_micros = 0
        usd_status = "unavailable"

    duration_ms = ctx.get("duration_ms") or ctx.get("millis")
    if duration_ms is not None:
        millis_val = int(duration_ms)
        millis_status = "measured"
    else:
        millis_val = 1
        millis_status = "measured"

    measurement_status = {
        "usd_micros": {"status": usd_status, "reason": None if usd_status != "unavailable" else "unpriced_provider"},
        "tokens": {"status": tokens_status, "reason": None},
        "bytes": {"status": bytes_status, "reason": None},
        "millis": {"status": millis_status, "reason": None},
    }

    return {
        "usd_micros": usd_micros,
        "tokens": tokens,
        "bytes": bytes_val,
        "millis": millis_val,
        "measurement_status": measurement_status,
    }


def assemble_trajectory(
    *,
    task: Any,
    harness_digest: str,
    terminal: str,
    receipts: Sequence[Any],
    contexts: Sequence[Mapping[str, Any]],
    events: Sequence[Any],
    verdict: Any,
    state_digest: str | None = None,
    model: Any = None,
    environment: Any = None,
    run_plan: Any = None,
) -> dict[str, Any]:
    turns: list[dict[str, Any]] = []
    proposals = [
        e for e in events
        if (getattr(e, "kind", None) or (getattr(e, "payload", {}).get("kind") if hasattr(e, "payload") else None)) == "ProposalProduced"
    ]
    model_routes_used: list[dict[str, Any]] = []
    seen_routes: set[tuple[str, str]] = set()

    for index, proposal in enumerate(proposals):
        ctx = contexts[index] if index < len(contexts) else {}
        context_digest = digest_of(dict(ctx) if ctx else {"turn": index})
        proposal_payload = dict(proposal.payload) if hasattr(proposal, "payload") and isinstance(proposal.payload, Mapping) else dict(proposal)

        route = _resolve_model_route(model, ctx)
        route_key = (route["provider"], route["model"])
        if route_key not in seen_routes:
            seen_routes.add(route_key)
            model_routes_used.append({"tier": 1, **route})

        turn_cost = _compute_turn_cost(ctx, proposal_payload, route)

        turn_receipts = []
        if index < len(receipts):
            rec = receipts[index]
            outcome = rec.outcome if getattr(rec, "outcome", None) in (
                "completed", "failed", "rejected", "undeterminable",
            ) else ("completed" if getattr(rec, "outcome", None) == "ok" else "failed")
            turn_receipts.append({
                "request_digest": getattr(rec, "descriptor_digest", None) or digest_of({"turn": index}),
                "outcome": outcome,
                "grant_digest": getattr(rec, "grant_digest", None),
                "lease_id": getattr(rec, "lease_id", None),
            })

        turns.append({
            "turn": index,
            "context_digest": context_digest,
            "proposal": proposal_payload,
            "receipts": turn_receipts,
            "model_route": route,
            "invocations": [{
                "tier": 1,
                "route": route,
                "cost": turn_cost,
            }],
            "cost": turn_cost,
        })

    if not model_routes_used and model is not None:
        default_route = _resolve_model_route(model)
        model_routes_used.append({"tier": 1, **default_route})
    elif not model_routes_used and turns:
        default_route = _resolve_model_route(None)
        model_routes_used.append({"tier": 1, **default_route})

    dimensions = ("usd_micros", "tokens", "bytes", "millis")
    total_cost: dict[str, Any] = {}
    total_measurement_status: dict[str, Any] = {}
    if not turns:
        for dim in dimensions:
            total_cost[dim] = 0
            total_measurement_status[dim] = {"status": "measured", "reason": None}
    else:
        for dim in dimensions:
            all_available = all(
                turn["cost"]["measurement_status"][dim]["status"] in ("measured", "estimated")
                for turn in turns
            )
            if all_available:
                total_cost[dim] = sum(turn["cost"][dim] for turn in turns)
                all_measured = all(
                    turn["cost"]["measurement_status"][dim]["status"] == "measured"
                    for turn in turns
                )
                total_measurement_status[dim] = {
                    "status": "measured" if all_measured else "estimated",
                    "reason": None,
                }
            else:
                total_cost[dim] = 0
                total_measurement_status[dim] = {
                    "status": "unavailable",
                    "reason": "turn_dimension_unavailable",
                }
    total_cost["measurement_status"] = total_measurement_status

    d_r_payload = {
        "harness_digest": harness_digest,
        "runtime": "vanguard-runtime/0.6.1",
        "environment": digest_of({
            "task": getattr(task, "brief", ""),
            "project": getattr(task, "project_id", ""),
        }),
        "models": [f"{r['provider']}:{r['model']}" for r in model_routes_used],
        "oracle": getattr(verdict, "oracle_id", "oracle-default") if verdict else "none",
    }
    execution_digest = getattr(run_plan, "run_digest", "") or digest_of(d_r_payload)

    seqs: list[int] = []
    for ev in events:
        s = getattr(ev, "seq", None)
        if s is None and hasattr(ev, "payload") and isinstance(ev.payload, Mapping):
            s = ev.payload.get("seq")
        if s is not None:
            try:
                seqs.append(int(s))
            except (ValueError, TypeError):
                pass

    if seqs:
        event_range = {
            "first_seq": min(seqs),
            "last_seq": max(seqs),
            "count": len(events),
        }
    else:
        event_range = {
            "first_seq": 0 if events else None,
            "last_seq": (len(events) - 1) if events else None,
            "count": len(events),
        }

    outcome_map = {
        "completed": "completed",
        "abandoned": "aborted",
        "budget_exhausted": "budget_exhausted",
        "runtime_error": "instrument_error",
        "cancelled": "aborted",
        "escalated": "aborted",
        "abstained": "completed",
    }
    terminal_name = getattr(terminal, "value", str(terminal)).lower()

    signed_verdict = signed_verdict_object(verdict)
    verdict_absence_reason = None if signed_verdict is not None else "no_evaluator_bound"

    return {
        "schema": "mhf.trajectory/1",
        "project_id": getattr(task, "project_id", "project-default"),
        "run_id": getattr(task, "run_id", "run-1"),
        "episode_id": getattr(task, "episode_id", "episode-1"),
        "parent_episode_id": getattr(task, "parent_episode_id", None),
        "principal_id": getattr(task, "principal", "agent-1"),
        "harness_digest": harness_digest,
        "activation_digest": getattr(run_plan, "activation_digest", None),
        "run_digest": execution_digest,
        "task_digest": getattr(run_plan, "task_digest", None),
        "execution_digest": execution_digest,
        "state_digest": state_digest,
        "event_range": event_range,
        "model_routes_used": model_routes_used,
        "turns": turns,
        "verdict": signed_verdict,
        "verdict_absence_reason": verdict_absence_reason,
        "cost": total_cost,
        "outcome": outcome_map.get(terminal_name, "aborted"),
    }


class DelayedTerminalEmitter:
    """Hold `EpisodeCompleted` until the trajectory (and verdict) are known."""

    def __init__(self, inner: Any) -> None:
        self._inner = inner
        self.pending: Event | None = None

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)

    def emit(self, event: Event) -> Any:
        if event.kind == "EpisodeCompleted":
            self.pending = event
            return None
        return self._inner.emit(event)

    def append_intent(self, event: Event) -> None:
        return self._inner.append_intent(event)

    def flush(self, trajectory: Mapping[str, Any]) -> None:
        if self.pending is None:
            return
        payload = {**dict(self.pending.payload), "trajectory": dict(trajectory)}
        flushed = Event(
            kind=self.pending.kind,
            reason=self.pending.reason,
            at=self.pending.at,
            run_id=self.pending.run_id,
            principal=self.pending.principal,
            payload=payload,
            alertable=self.pending.alertable,
        )
        self._inner.emit(flushed)
        self.pending = None
