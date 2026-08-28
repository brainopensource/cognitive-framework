"""Immutable Experiment Run Catalog and Provenance Ledger for 006_LLM_INT_MACHINE.

Persists every execution run as a canonical JSON receipt under tools/006_LLM_INT_MACHINE/runs/
and provides querying, filtering, and statistical comparison methods.
"""

from __future__ import annotations
import json
import os
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

RUNS_DIR = Path(__file__).parent / "runs"


@dataclass
class RunReceipt:
    """Immutable execution receipt for an experiment run."""
    run_id: str
    timestamp_utc: str
    challenge_id: str
    config_name: str
    version_tag: str
    config_hash: str
    model: str
    seed: int
    success: bool
    turns_taken: int
    total_tokens: int
    cached_tokens: int
    total_cost_usd: float
    duration_seconds: float
    git_diff_lines: int
    ast_errors_prevented: int
    mutation_score: float
    pareto_score: float
    config_snapshot: dict[str, Any]
    kpi_metrics: dict[str, Any]
    turn_events: list[dict[str, Any]]
    error_message: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class RunCatalog:
    """Manages creation, storage, and retrieval of experiment run receipts."""

    def __init__(self, storage_dir: Path | None = None):
        self.dir = storage_dir or RUNS_DIR
        self.dir.mkdir(parents=True, exist_ok=True)

    def save_run(self, receipt: RunReceipt) -> Path:
        """Persist a RunReceipt as a pretty canonical JSON file."""
        filename = f"{receipt.run_id}.json"
        target_path = self.dir / filename
        data = receipt.to_dict()
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, sort_keys=True)
        return target_path

    def load_run(self, run_id: str) -> RunReceipt | None:
        """Load a RunReceipt by run_id or file path."""
        target_path = self.dir / (f"{run_id}.json" if not run_id.endswith(".json") else run_id)
        if not target_path.is_file():
            return None
        with open(target_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return RunReceipt(**data)

    def list_runs(
        self,
        challenge_id: str | None = None,
        config_name: str | None = None,
        model: str | None = None,
        limit: int = 50,
    ) -> list[RunReceipt]:
        """List and filter historical experiment receipts."""
        receipts: list[RunReceipt] = []
        if not self.dir.is_dir():
            return receipts

        for f in sorted(self.dir.glob("run_*.json"), key=os.path.getmtime, reverse=True):
            try:
                with open(f, "r", encoding="utf-8") as fp:
                    data = json.load(fp)
                rec = RunReceipt(**data)
                if challenge_id and rec.challenge_id != challenge_id:
                    continue
                if config_name and rec.config_name != config_name:
                    continue
                if model and rec.model != model:
                    continue
                receipts.append(rec)
                if len(receipts) >= limit:
                    break
            except Exception:
                continue

        return receipts


def generate_run_id(challenge_id: str, config_name: str, model: str) -> str:
    """Generate a readable, timestamped, sortable Run ID."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    clean_model = model.replace("/", "_").replace(":", "_").replace("-", "_")
    return f"run_{ts}_{challenge_id}_{config_name}_{clean_model}"
