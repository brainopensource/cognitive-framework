"""Tiered live benchmark ladder with full LLM trajectory recording.

Every model interaction is captured through `CassetteRecorder`, so a live run
is replayable at $0 afterwards. Nothing here fabricates a result: the verdict
always comes from re-running the challenge's own oracle in a subprocess after
the agent has finished, and a challenge whose baseline already passes is
refused rather than counted.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from benchmarks.run_20_eval_suite import (  # noqa: E402
    ALL_CHALLENGES,
    EASY_TIER_KEYS,
    HARD_TIER_KEYS,
    MEDIUM_TIER_KEYS,
    run_oracle_test,
    setup_workspace,
)
from benchmarks.sota_context import (  # noqa: E402
    CHALLENGES as SOTA_CHALLENGES,
    TIERS as SOTA_TIERS,
)
from benchmarks._env import load_benchmark_env
from vanguard.packages.runtime.root import (  # noqa: E402
    application_service,
    Cassette,
    CassetteRecorder,
    OpenRouterModel,
)

ALL_CHALLENGES = {**ALL_CHALLENGES, **SOTA_CHALLENGES}
TIERS = {
    "easy": EASY_TIER_KEYS,
    "medium": MEDIUM_TIER_KEYS,
    "hard": HARD_TIER_KEYS,
    **SOTA_TIERS,
}
OUT = ROOT / "benchmarks/artifacts/ladder"


class LiveBudgetExceeded(RuntimeError):
    """Raised before a provider call once the live-run ceiling is closed."""


class LiveBudget:
    """One fail-closed budget shared by every challenge in a ladder run."""

    def __init__(self, *, max_cost_usd: float, max_calls: int) -> None:
        if max_cost_usd <= 0 or max_calls <= 0:
            raise ValueError("live budget and call cap must be positive")
        self.max_cost_usd = max_cost_usd
        self.max_calls = max_calls
        self.calls = 0
        self.cost_usd = 0.0

    def guard(self, delegate: object) -> object:
        budget = self

        class _BudgetedModel:
            def propose(self, context, tools, sampling):
                if budget.calls >= budget.max_calls:
                    raise LiveBudgetExceeded(
                        f"provider call cap reached ({budget.calls}/{budget.max_calls})")
                if budget.cost_usd >= budget.max_cost_usd:
                    raise LiveBudgetExceeded(
                        f"provider cost cap reached (${budget.cost_usd:.6f}/"
                        f"${budget.max_cost_usd:.6f})")
                answer = delegate.propose(context, tools, sampling)
                budget.calls += 1
                value = getattr(answer, "value", None)
                proposal = value if isinstance(value, dict) else answer
                if isinstance(proposal, dict):
                    budget.cost_usd += float(proposal.get("cost_usd") or 0.0)
                return answer

            def __getattr__(self, name):
                return getattr(delegate, name)

        return _BudgetedModel()

    @property
    def closed(self) -> bool:
        return self.calls >= self.max_calls or self.cost_usd >= self.max_cost_usd


def _trajectory(cassette: Cassette) -> list[dict]:
    """Flatten the recorded tape into a readable per-turn trajectory."""
    steps = []
    for i, rec in enumerate(cassette.records):
        prop = dict(rec.proposal)
        ctx = rec.context if isinstance(rec.context, dict) else {}
        msgs = ctx.get("messages") or []
        last_tool = None
        for m in reversed(msgs):
            if isinstance(m, dict) and m.get("role") == "tool":
                last_tool = str(m.get("content", ""))[:1500]
                break
        steps.append({
            "turn": i,
            "kind": prop.get("kind"),
            "action": prop.get("action"),
            "args": prop.get("args"),
            "note": str(prop.get("note", ""))[:400],
            "text": str(prop.get("text", ""))[:800],
            "usage": prop.get("usage"),
            "cost_usd": prop.get("cost_usd"),
            "prior_tool_result": last_tool,
            "recovery_feedback": ctx.get("recoveryFeedback"),
        })
    return steps


def run_one(key: str, tier: str, model_name: str, max_turns: int,
            manifest: str, *, tag: str, live_budget: LiveBudget) -> dict:
    challenge = ALL_CHALLENGES[key]
    OUT.mkdir(parents=True, exist_ok=True)
    safe_tag = re.sub(r"[^A-Za-z0-9_.-]+", "_", tag).strip("._") or "run"
    safe_model = re.sub(r"[^A-Za-z0-9_.-]+", "_", model_name)
    artifact_stem = f"{safe_tag}__{key}__{safe_model}"
    tape_p = OUT / f"{artifact_stem}.cassette.json"

    with tempfile.TemporaryDirectory(prefix=f"ladder_{key}_") as td:
        ws = Path(td)
        setup_workspace(ws, challenge)

        baseline_pass, baseline_out = run_oracle_test(ws, challenge.oracle_code)
        if baseline_pass:
            return {"challenge": key, "tier": tier, "status": "INVALID_BASELINE",
                    "detail": "baseline already passes its own oracle",
                    "model": model_name}

        cassette = Cassette()
        live_model = OpenRouterModel(model=model_name, stream=False,
                                     reasoning_effort="none")
        recorder = CassetteRecorder(
            cassette,
            delegate=live_budget.guard(live_model),
            output_path=tape_p,
        )

        app = application_service(workspace=ws)
        manifest_p = ROOT / f"vanguard/packages/agency/manifests/{manifest}/manifest.json"
        start = time.monotonic()
        err = ""
        run_res = None
        try:
            run_res = app.run(
                brief=challenge.brief,
                manifest_path=manifest_p,
                model=recorder,
                interactive=True,
                autonomous_approval=True,
                max_turns=max_turns,
            )
        except Exception as exc:
            err = f"{type(exc).__name__}: {exc}\n{traceback.format_exc()[-2000:]}"
        elapsed = round(time.monotonic() - start, 2)

        oracle_pass, oracle_out = run_oracle_test(ws, challenge.oracle_code)
        modified = sorted(
            str(p.relative_to(ws)) for p in ws.rglob("*.py")
            if p.is_file() and str(p.relative_to(ws)) in challenge.files
            and p.read_text(encoding="utf-8", errors="replace") != challenge.files[str(p.relative_to(ws))]
        )

        spend = sum(float(r.proposal.get("cost_usd") or 0) for r in cassette.records)
        status = ("ERROR" if err else
                  "PASS" if oracle_pass else
                  "ABANDONED" if run_res is not None and run_res.terminal_state == "abandoned"
                  else "FAIL")

        row = {
            "challenge": key, "tier": tier, "title": challenge.title,
            "model": model_name, "manifest": manifest, "status": status,
            "llm_calls": len(cassette.records),
            "turns": getattr(run_res, "turns", 0) if run_res else 0,
            "terminal_state": getattr(run_res, "terminal_state", None) if run_res else None,
            "cost_usd": round(spend, 6),
            "latency_s": elapsed,
            "files_modified": modified,
            "oracle_output": oracle_out[-2500:] if not oracle_pass else "",
            "error": err,
            "terminal_detail": getattr(run_res, "detail", "") if run_res else "",
            "run_fields": {k: str(v)[:300] for k, v in vars(run_res).items()} if run_res and hasattr(run_res, "__dict__") else {},
            "cassette": str(tape_p.relative_to(ROOT)),
            "trajectory": _trajectory(cassette),
        }
        (OUT / f"{artifact_stem}.run.json").write_text(
            json.dumps(row, indent=2), encoding="utf-8")
        return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tier", default="easy", choices=list(TIERS))
    ap.add_argument("--model", default="deepseek/deepseek-v4-flash-0731")
    ap.add_argument("--max-turns", type=int, default=15)
    ap.add_argument("--manifest", default="vg-code-max-v2")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--only", default="")
    ap.add_argument("--budget-usd", type=float, default=0.15)
    ap.add_argument("--max-calls", type=int, default=300)
    ap.add_argument("--tag", default="run")
    args = ap.parse_args()

    keys = [args.only] if args.only else list(TIERS[args.tier])
    if args.limit:
        keys = keys[: args.limit]

    rows = []
    live_budget = LiveBudget(
        max_cost_usd=args.budget_usd,
        max_calls=args.max_calls,
    )
    for key in keys:
        if live_budget.closed:
            print(f"[budget] stopping: ${live_budget.cost_usd:.5f}/"
                  f"${args.budget_usd:.5f}, {live_budget.calls}/{args.max_calls} calls")
            break
        print(f"\n=== {key} ({args.tier}) via {args.model} ===", flush=True)
        row = run_one(
            key, args.tier, args.model, args.max_turns, args.manifest,
            tag=args.tag, live_budget=live_budget,
        )
        rows.append(row)
        print(f"  -> {row['status']} calls={row.get('llm_calls')} "
              f"turns={row.get('turns')} term={row.get('terminal_state')} "
              f"cost=${row.get('cost_usd')} files={row.get('files_modified')}",
              flush=True)

    passed = sum(1 for r in rows if r["status"] == "PASS")
    report = {
        "tier": args.tier, "model": args.model, "manifest": args.manifest,
        "max_turns": args.max_turns,
        "total": len(rows), "passed": passed,
        "pass_rate": f"{passed}/{len(rows)}" if rows else "0/0",
        "spend_usd": round(live_budget.cost_usd, 6),
        "llm_calls": live_budget.calls,
        "budget_usd": args.budget_usd,
        "max_calls": args.max_calls,
        "rows": [{k: v for k, v in r.items() if k != "trajectory"} for r in rows],
    }
    OUT.mkdir(parents=True, exist_ok=True)
    rp = OUT / f"report_{args.tag}_{args.tier}_{args.model.replace('/', '_')}.json"
    rp.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\n=== {passed}/{len(rows)} PASS | spend ${live_budget.cost_usd:.5f} | "
          f"calls {live_budget.calls}/{args.max_calls} | {rp.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    load_benchmark_env()
    raise SystemExit(main())
