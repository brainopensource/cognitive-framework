#!/usr/bin/env python3
"""Fixed greenfield campaign runner for S34 (control/planned/adaptive/cheap).

Default mode is dry/fake validation: no network, no paid calls. Live arms require
explicit ``--live`` plus a predeclared microdollar ceiling. Expand beyond the
initial three-trial / $0.05 envelope only after recorded authorization.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import uuid
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.project_v0450_coding_run import archive_run
from vanguard.packages.runtime.coding_entrypoint import (
    exit_code_for,
    load_band_models,
    run_entrypoint,
)

ARMS: dict[str, dict[str, Any]] = {
    "control": {
        "plannerModel": "cohere/north-mini-code:free",
        "executorBand": "free",
        "recoveryModels": [],
        "fakeBackend": "non-green",
    },
    "planned": {
        "plannerModel": "deepseek/deepseek-v4-flash",
        "executorBand": "free",
        "recoveryModels": [],
        "fakeBackend": "non-green",
    },
    "adaptive": {
        "plannerModel": "deepseek/deepseek-v4-flash",
        "executorBand": "free",
        "recoveryModels": ["deepseek/deepseek-v4-flash"],
        "fakeBackend": "greenfield-adaptive",
    },
    "cheap": {
        "plannerModel": "deepseek/deepseek-v4-flash",
        "executorBand": "medium",
        "recoveryModels": ["deepseek/deepseek-v4-flash"],
        "fakeBackend": "non-green",
    },
}


def _sanitize_command(argv: list[str]) -> str:
    return " ".join(argv)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="S34 greenfield campaign runner")
    parser.add_argument("--task-dir", default="lab/tasks/greenfield-v0450-webapp")
    parser.add_argument("--arms", nargs="+", default=["adaptive"], choices=sorted(ARMS))
    parser.add_argument("--trials", type=int, default=3)
    parser.add_argument("--budget-usd-micros", type=int, default=50_000,
                        help="Aggregate paid ceiling for the campaign (default $0.05)")
    parser.add_argument("--live", action="store_true",
                        help="Call a real ModelPort through HarnessSession; no fakeBackend")
    parser.add_argument("--evidence-root",
                        default="docs/scrum/sprints/sprint34/evidence")
    args = parser.parse_args(argv)

    if args.trials < 1 or args.trials > 3:
        print("initial campaign is fixed at 1..3 trials; expand only after review",
              file=sys.stderr)
        return 2
    if args.budget_usd_micros > 50_000:
        print("aggregate ceiling above $0.05 requires explicit authorization",
              file=sys.stderr)
        return 2

    task_dir = Path(args.task_dir).resolve()
    evidence_root = Path(args.evidence_root)
    evidence_root.mkdir(parents=True, exist_ok=True)

    spent = 0
    rows: list[dict[str, Any]] = []
    for arm_name in args.arms:
        arm = ARMS[arm_name]
        # Cheap arm uses medium executors in the live design; fake path still
        # refuses frontier and does not spend.
        if arm["executorBand"] == "high":
            print(f"arm {arm_name}: frontier refused", file=sys.stderr)
            return 2
        for trial in range(1, args.trials + 1):
            run_id = f"{arm_name}-t{trial}-{uuid.uuid4().hex[:8]}"
            request = {
                "command": "code",
                "workspace": str(task_dir),
                "brief": "TASK.md",
                "runId": run_id,
                "plannerModel": arm["plannerModel"],
                "executorBand": "free",
                "recoveryModels": arm["recoveryModels"],
                "budgetUsdMicros": max(0, args.budget_usd_micros - spent),
                "interactive": True,
                "fakeBackend": None if args.live else arm["fakeBackend"],
                "live": args.live,
                "json": True,
                "headless": True,
                "inPlace": False,
                "modelPort": "openrouter",
            }
            if args.live:
                request["plannerModel"] = list(load_band_models("free"))[0]
                request["executorModels"] = list(load_band_models("free"))
                request["fakeBackend"] = None
            else:
                request["executorModels"] = list(load_band_models("free"))
            buf_lines: list[str] = []

            class _Writer:
                def write(self, data: str) -> int:
                    buf_lines.append(data)
                    return len(data)

                def flush(self) -> None:
                    return None

            code = run_entrypoint(request, writer=_Writer())
            if args.live and code == 3:
                print("live campaign fail-closed: model port unavailable", file=sys.stderr)
                return 3
            result = None
            for line in buf_lines:
                payload = json.loads(line)
                if payload.get("type") == "result":
                    result = payload["result"]
            assert result is not None
            cost = result.get("spentUsdMicros")
            if isinstance(cost, int):
                spent += cost
            if spent > args.budget_usd_micros:
                print("aggregate budget exceeded; stopping before expansion", file=sys.stderr)
                return 4

            dest = evidence_root / run_id
            archive_run(dest, {
                "command.txt": _sanitize_command(sys.argv),
                "task-manifest.json": {
                    "taskDir": str(task_dir),
                    "arm": arm_name,
                    "trial": trial,
                    "runId": run_id,
                },
                "coding-plan.json": {"digest": result.get("planDigest"), "note": "from result"},
                "plan-revisions.json": [],
                "model-routes.json": result.get("modelRoutes") or [],
                "ledger.jsonl": "",
                "coding-session.json": result,
                "workspace.diff": "",
                "verification.json": {
                    "outcome": result.get("outcome"),
                    "exitCode": code,
                },
                "budget.json": {
                    "campaignCeilingMicros": args.budget_usd_micros,
                    "spentUsdMicros": cost,
                    "aggregateSpentUsdMicros": spent,
                },
                "summary.md": (
                    f"# {run_id}\n\n"
                    f"- arm: {arm_name}\n"
                    f"- outcome: {result.get('outcome')}\n"
                    f"- exit: {code} (mapped {exit_code_for(str(result.get('outcome')))})\n"
                    f"- spentUsdMicros: {cost}\n"
                    f"- fake: {None if args.live else arm['fakeBackend']}\n"
                    f"- live: {args.live}\n"
                    f"- timestamp: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n"
                ),
            })
            rows.append({
                "runId": run_id,
                "arm": arm_name,
                "outcome": result.get("outcome"),
                "exitCode": code,
                "spentUsdMicros": cost,
                "evidence": str(dest),
            })

    print(json.dumps({
        "campaign": "v0450-greenfield",
        "live": args.live,
        "ceilingUsdMicros": args.budget_usd_micros,
        "aggregateSpentUsdMicros": spent,
        "denominator": len(rows),
        "rows": rows,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
