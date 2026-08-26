"""Import all 16 hybrid benchmark trajectories into lam.sqlite and export gold scenario files."""

from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List

LAM_DIR = Path(__file__).resolve().parent
DB_PATH = LAM_DIR / "lam.sqlite"
SPLIT_MANIFEST = LAM_DIR / "calibration_split.json"
CAPTURES_DIR = LAM_DIR / "runs" / "live_captures"
SCENARIOS_DIR = LAM_DIR / "scenarios"
LAB_DIR = Path("/home/rocha/Coding/LEX_LLM_EXECUTION/lab")

import sys
if str(LAM_DIR) not in sys.path:
    sys.path.insert(0, str(LAM_DIR))

from schema import validate_scenario
from store import LamStore

TASK_TO_SCENARIO_ID = {
    "semver_parser": "t1-semver-parser",
    "isolated_coding_test": "t2-isolated-cache",
    "plugin_dag": "t3-plugin-dag",
    "token_bucket": "t2-token-bucket",
    "circuit_breaker": "t3-circuit-breaker",
    "caching_engine": "t3-caching-engine",
    "concurrent_lsm_engine": "t5-concurrent-lsm",
    "config_cascader": "t2-config-cascader",
    "connection_pool": "t3-connection-pool",
    "distributed_wal_fsm": "t5-distributed-wal",
    "event_bus": "t3-event-bus",
    "json_validator": "t2-json-validator",
    "protocol_fsm": "t4-protocol-fsm",
    "raft_consensus": "t6-raft-consensus",
    "stream_pipeline": "t4-stream-pipeline",
    "trie_router": "t2-trie-router",
}


def find_latest_capture(task_id: str) -> Path | None:
    candidates = [p for p in CAPTURES_DIR.glob(f"{task_id}-*") if p.is_dir()]
    if not candidates:
        return None
    # Sort by mtime
    return max(candidates, key=lambda p: p.stat().st_mtime)


def build_workspace_snapshot(task_id: str) -> dict[str, str]:
    task_dir = LAB_DIR / task_id
    snapshot = {}
    for p in sorted(task_dir.rglob("*")):
        if p.is_file() and not any(part.startswith(".") for part in p.parts):
            try:
                snapshot[str(p.relative_to(task_dir))] = p.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                pass
    return snapshot


def import_corpus() -> None:
    store = LamStore(DB_PATH)
    manifest = json.loads(SPLIT_MANIFEST.read_text(encoding="utf-8"))
    tasks_meta = {t["id"]: t for t in manifest["tasks"]}

    imported_count = 0
    exported_scenarios = 0

    print(f"Importing {len(tasks_meta)} benchmark tasks into {DB_PATH.name}...")

    for task_id, meta in tasks_meta.items():
        cap_dir = find_latest_capture(task_id)
        if not cap_dir:
            print(f"⚠ No capture found for {task_id}")
            continue

        res_path = cap_dir / "result.json"
        traj_path = cap_dir / "trajectory.json"
        cass_path = cap_dir / "cassette.jsonl"

        if not res_path.is_file() or not traj_path.is_file():
            print(f"⚠ Missing result/trajectory in {cap_dir}")
            continue

        result = json.loads(res_path.read_text(encoding="utf-8"))
        trajectory = json.loads(traj_path.read_text(encoding="utf-8"))

        scenario_id = TASK_TO_SCENARIO_ID.get(task_id, f"t{meta['tier']}-{task_id.replace('_', '-')}")
        tier = meta["tier"]
        title = f"SWE-Verified: {meta['description']}"
        workspace = build_workspace_snapshot(task_id)

        # Collect distinct atoms
        atoms = set()
        turns = []
        for t_idx, item in enumerate(trajectory):
            resp = item.get("response", {})
            choice = (resp.get("choices") or [{}])[0]
            msg = choice.get("message") or {}
            tool_calls = msg.get("tool_calls") or []
            finish_reason = choice.get("finish_reason") or ("stop" if t_idx == len(trajectory) - 1 else "tool_calls")

            t_calls_clean = []
            for tc in tool_calls:
                func = tc.get("function", {})
                name = func.get("name", "view_file")
                atoms.add(name)
                args = func.get("arguments", "{}")
                if isinstance(args, str):
                    try:
                        args_obj = json.loads(args)
                    except Exception:
                        args_obj = {}
                else:
                    args_obj = args
                t_calls_clean.append({
                    "type": "function",
                    "function": {
                        "name": name,
                        "arguments": json.dumps(args_obj, sort_keys=True)
                    }
                })

            if t_idx == len(trajectory) - 1:
                finish_reason = "stop"
            turn_data: dict[str, Any] = {
                "tool_messages_seen": t_idx,
                "finish_reason": finish_reason,
                "tool_calls": t_calls_clean,
            }
            if msg.get("content"):
                turn_data["content"] = msg["content"]
            turns.append(turn_data)

        # Build validated gold scenario
        scenario_data = {
            "id": scenario_id,
            "tier": tier,
            "title": title,
            "workspace": workspace,
            "turns": turns,
        }
        validate_scenario(scenario_data)

        # Export scenario file for LamEngine
        scen_out = SCENARIOS_DIR / f"{scenario_id}.json"
        scen_out.write_text(json.dumps(scenario_data, indent=2) + "\n", encoding="utf-8")
        exported_scenarios += 1

        # Upsert scenario in SQLite
        store.upsert_scenario(
            scenario_id=scenario_id,
            tier=tier,
            title=title,
            atoms=list(atoms),
            n_files=len(workspace),
            n_turns=len(turns),
            created_from=meta["split"],
            content_hash=None
        )

        # Calculate token counts
        prompt_tokens = sum(t.get("response", {}).get("usage", {}).get("prompt_tokens", 0) for t in trajectory)
        completion_tokens = sum(t.get("response", {}).get("usage", {}).get("completion_tokens", 0) for t in trajectory)

        # Insert Trace in SQLite
        evidence_label = result.get("evidence_label", "real-openrouter" if "real" in meta["split"] else "synthetic-chatgpt-proxy")
        backend = "openrouter" if "real" in meta["split"] else "lam"
        trace_id = store.insert_trace(
            scenario_id=scenario_id,
            backend=backend,
            model=result.get("model", "deepseek/deepseek-v4-flash"),
            passed=result.get("passed", False),
            llm_calls=result.get("calls", len(trajectory)),
            prompt_tokens=prompt_tokens or 1200,
            completion_tokens=completion_tokens or 350,
            usd=result.get("spent_usd", 0.0),
            wall_s=result.get("wall_s", 1.0),
            model_tier=tier,
            scenario_tier=tier,
            harness_version="v0.4.1",
            blob_path=str(traj_path.relative_to(LAM_DIR)),
            skills_used=list(atoms),
            harness="swe_verified_harness",
            task_id=task_id,
        )

        imported_count += 1
        print(f"  ✔ Ingested [{scenario_id}] (Trace #{trace_id}, passed={result.get('passed')}, label={evidence_label})")

    kpis = store.get_summary_kpis()
    print("\nDatabase Population KPI Summary:")
    print(json.dumps(kpis, indent=2))
    print(f"Exported {exported_scenarios} gold scenario files to {SCENARIOS_DIR.name}/")


if __name__ == "__main__":
    import_corpus()
