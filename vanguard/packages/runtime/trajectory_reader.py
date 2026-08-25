"""Trajectory reader and run comparison tool (M4-04, EVIDENCE.md, ADR-0094).

Provides reproducible analysis and diffing across trajectory runs, isolating
every execution variable (D_H, D_R, models, contexts, proposals, costs, outcomes).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

__all__ = [
    "TrajectoryDiff",
    "TrajectoryReader",
    "diff_trajectories",
]


@dataclass(frozen=True, slots=True)
class TrajectoryDiff:
    """Structured diff between two runs of a task."""

    match: bool
    left_run_id: str
    right_run_id: str
    differing_variables: tuple[str, ...]
    details: Mapping[str, Mapping[str, Any]]
    summary: str


class TrajectoryReader:
    """Reader for mhf.trajectory/1 records from stores, files, or dictionaries."""

    @classmethod
    def load(cls, source: Any) -> dict[str, Any]:
        """Load a trajectory dict from an in-memory dict, JSON file, or SQLite store."""
        if isinstance(source, Mapping):
            if "schema" in source and "turns" in source:
                return dict(source)
            if "trajectory" in source and isinstance(source["trajectory"], Mapping):
                return dict(source["trajectory"])
            return dict(source)

        if isinstance(source, (str, Path)):
            path = Path(source)
            if path.is_file():
                text = path.read_text(encoding="utf-8").strip()
                try:
                    data = json.loads(text)
                    if isinstance(data, Mapping):
                        if "trajectory" in data and isinstance(data["trajectory"], Mapping):
                            return dict(data["trajectory"])
                        return dict(data)
                except json.JSONDecodeError:
                    pass
                # JSONL file: search for EpisodeCompleted event with trajectory payload
                for line in reversed(text.splitlines()):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        record = json.loads(line)
                        if isinstance(record, Mapping):
                            payload = record.get("payload", {})
                            if isinstance(payload, Mapping) and "trajectory" in payload:
                                return dict(payload["trajectory"])
                            if "schema" in record and "turns" in record:
                                return dict(record)
                    except Exception:
                        continue
                raise ValueError(f"no mhf.trajectory record found in {path}")

        # Check for SqliteEventStore or similar store object
        if hasattr(source, "read_all"):
            events = source.read_all()
            for ev in reversed(events):
                payload = getattr(ev, "payload", {})
                if isinstance(payload, Mapping) and "trajectory" in payload:
                    return dict(payload["trajectory"])
            raise ValueError("no trajectory found in event store")

        raise TypeError(f"unsupported trajectory source type: {type(source).__name__}")

    @classmethod
    def extract_variables(cls, trajectory: Mapping[str, Any]) -> dict[str, Any]:
        """Extract all observable execution variables from a trajectory."""
        turns = []
        for t in trajectory.get("turns", ()):
            t_dict = dict(t) if isinstance(t, Mapping) else {}
            turns.append({
                "turn": t_dict.get("turn"),
                "context_digest": t_dict.get("context_digest"),
                "context_ref": t_dict.get("context_ref"),
                "proposal": t_dict.get("proposal"),
                "receipts": t_dict.get("receipts"),
                "cost": t_dict.get("cost"),
                "model_route": t_dict.get("model_route"),
            })

        return {
            "schema": trajectory.get("schema", "mhf.trajectory/1"),
            "project_id": trajectory.get("project_id", ""),
            "run_id": trajectory.get("run_id", ""),
            "episode_id": trajectory.get("episode_id", ""),
            "harness_digest": trajectory.get("harness_digest", ""),
            "run_digest": trajectory.get("run_digest", ""),
            "activation_digest": trajectory.get("activation_digest", ""),
            "task_digest": trajectory.get("task_digest", ""),
            "preregistration_digest": trajectory.get("preregistration_digest", ""),
            "state_digest": trajectory.get("state_digest", ""),
            "model_routes_used": trajectory.get("model_routes_used", ()),
            "turns_count": len(turns),
            "turns": turns,
            "cost": trajectory.get("cost", {}),
            "outcome": trajectory.get("outcome", ""),
            "verdict": trajectory.get("verdict"),
            "verdict_absence_reason": trajectory.get("verdict_absence_reason"),
        }


def diff_trajectories(left_source: Any, right_source: Any) -> TrajectoryDiff:
    """Diff two trajectories and report every variable that materially differed."""
    t1 = TrajectoryReader.load(left_source)
    t2 = TrajectoryReader.load(right_source)

    v1 = TrajectoryReader.extract_variables(t1)
    v2 = TrajectoryReader.extract_variables(t2)

    differing: list[str] = []
    details: dict[str, dict[str, Any]] = {}

    scalar_keys = [
        "harness_digest",
        "run_digest",
        "activation_digest",
        "task_digest",
        "preregistration_digest",
        "state_digest",
        "outcome",
        "verdict_absence_reason",
    ]

    for key in scalar_keys:
        val1, val2 = v1.get(key), v2.get(key)
        if val1 != val2:
            differing.append(key)
            details[key] = {"left": val1, "right": val2}

    # Compare model routes
    if v1.get("model_routes_used") != v2.get("model_routes_used"):
        differing.append("model_routes_used")
        details["model_routes_used"] = {
            "left": v1.get("model_routes_used"),
            "right": v2.get("model_routes_used"),
        }

    # Compare total cost
    c1, c2 = v1.get("cost", {}), v2.get("cost", {})
    for dim in ("tokens", "usd_micros", "bytes", "millis"):
        if c1.get(dim) != c2.get(dim):
            differing.append(f"cost.{dim}")
            details[f"cost.{dim}"] = {"left": c1.get(dim), "right": c2.get(dim)}

    # Compare turns
    turns1 = v1.get("turns", [])
    turns2 = v2.get("turns", [])
    if len(turns1) != len(turns2):
        differing.append("turns_count")
        details["turns_count"] = {"left": len(turns1), "right": len(turns2)}

    min_len = min(len(turns1), len(turns2))
    for i in range(min_len):
        t1_i = turns1[i]
        t2_i = turns2[i]
        if t1_i.get("context_digest") != t2_i.get("context_digest"):
            differing.append(f"turns[{i}].context_digest")
            details[f"turns[{i}].context_digest"] = {
                "left": t1_i.get("context_digest"),
                "right": t2_i.get("context_digest"),
            }
        if t1_i.get("proposal") != t2_i.get("proposal"):
            differing.append(f"turns[{i}].proposal")
            details[f"turns[{i}].proposal"] = {
                "left": t1_i.get("proposal"),
                "right": t2_i.get("proposal"),
            }
        if t1_i.get("receipts") != t2_i.get("receipts"):
            differing.append(f"turns[{i}].receipts")
            details[f"turns[{i}].receipts"] = {
                "left": t1_i.get("receipts"),
                "right": t2_i.get("receipts"),
            }

    match = len(differing) == 0
    left_id = str(v1.get("run_id") or "left")
    right_id = str(v2.get("run_id") or "right")

    if match:
        summary = f"Runs {left_id} and {right_id} are identical across all observable execution variables."
    else:
        summary = (
            f"Runs {left_id} and {right_id} differ on {len(differing)} variable(s): "
            + ", ".join(differing[:8])
            + ("..." if len(differing) > 8 else "")
        )

    return TrajectoryDiff(
        match=match,
        left_run_id=left_id,
        right_run_id=right_id,
        differing_variables=tuple(differing),
        details=details,
        summary=summary,
    )
