"""Preregister, validate, and dry-run the Vanguard v0.9 benchmark.

The dry runner deliberately never calls a provider and never emits empirical
scores.  It exercises the locked matrix, manifest composition, input digests,
cache hygiene, and immutable per-row evidence boundaries.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from random import Random
from tempfile import TemporaryDirectory
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
MANIFESTS = ROOT / "vanguard/packages/agency/manifests"
ARTIFACTS = ROOT / "benchmarks/frontier_v090/artifacts"
MODEL = "deepseek/deepseek-v4-flash-0731"
PRESETS = (
    ("Coding", "vg-code-v090-react-control", ("Easy", "Medium", "Hard"), ("CODE-E", "CODE-M", "CODE-H")),
    ("Coding", "vg-code-v090-claude-shaped", ("Easy", "Medium", "Hard"), ("CODE-E", "CODE-M", "CODE-H")),
    ("Coding", "vg-code-v090-opencode-shaped", ("Easy", "Medium", "Hard"), ("CODE-E", "CODE-M", "CODE-H")),
    ("Coding", "vg-code-v090-lex-surgical", ("Easy", "Medium", "Hard"), ("CODE-E", "CODE-M", "CODE-H")),
    ("Coding", "vg-code-v090-lim-falsifier", ("Easy", "Medium", "Hard"), ("CODE-E", "CODE-M", "CODE-H")),
    ("Tutor", "vg-tutor-v090-v1-read-search", ("Easy", "Hard"), ("TUTOR-E", "TUTOR-H")),
    ("Tutor", "vg-tutor-v090-v2-evidence-graph", ("Easy", "Hard"), ("TUTOR-E", "TUTOR-H")),
    ("Research", "vg-research-v090-v1-local", ("Easy", "Hard"), ("RESEARCH-E", "RESEARCH-H")),
    ("Research", "vg-research-v090-v2-web-corroborated", ("Easy", "Hard"), ("RESEARCH-E", "RESEARCH-H")),
    ("Bugfix", "vg-bugfix-v090-v1-direct", ("Easy", "Hard"), ("BUG-E", "BUG-H")),
    ("Bugfix", "vg-bugfix-v090-v2-reproduce-verify", ("Easy", "Hard"), ("BUG-E", "BUG-H")),
)


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def digest_tree(root: Path, paths: tuple[str, ...]) -> str:
    rows: list[list[str]] = []
    for base in paths:
        candidate = root / base
        if candidate.is_file():
            files = (candidate,)
        else:
            files = (p for p in candidate.rglob("*") if p.is_file())
        for path in sorted(files):
            if "__pycache__" in path.parts or "artifacts" in path.parts or path.suffix in {".pyc", ".pyo"}:
                continue
            rows.append([path.relative_to(root).as_posix(), sha256_bytes(path.read_bytes())])
    return sha256_bytes(json.dumps(rows, separators=(",", ":"), ensure_ascii=True).encode())


def manifest_digest(name: str) -> str:
    return digest_tree(MANIFESTS, (name,))


@dataclass(frozen=True)
class Row:
    run_id: str
    ordinal: int
    class_name: str
    preset: str
    difficulty: str
    challenge: str
    model: str = MODEL
    status: str = "PLANNED"
    planned_score: str = "TBD"


def rows() -> list[Row]:
    result: list[Row] = []
    ordinal = 1
    for class_name, preset, difficulties, challenges in PRESETS:
        for difficulty, challenge in zip(difficulties, challenges):
            result.append(Row(f"v090-{ordinal:02d}", ordinal, class_name, preset, difficulty, challenge))
            ordinal += 1
    return result


def preregistration() -> dict[str, Any]:
    frozen = ("vanguard/packages/domain", "vanguard/packages/ports", "vanguard/packages/kernel",
              "vanguard/packages/agency/episode", "vanguard/packages/agency/context",
              "vanguard/packages/runtime", "vanguard/packages/adapters", "schemas")
    subject = ("benchmarks/frontier_v090", "tools/benchmark-drivers", "vanguard/packages/agency/manifests")
    order = rows()
    Random(90090).shuffle(order)
    body: dict[str, Any] = {
        "schema": "aether.frontier-benchmark-preregistration/1", "authority": "non-authorizing",
        "status": "proposed", "model": MODEL, "provider": "openrouter", "temperature": 0,
        "streaming": True, "retry_policy": {"max_attempts": 2}, "timeout_seconds": 1800,
        "global_token_ceiling": 1_000_000, "global_cost_usd": 0.50, "stop_tokens": 950_000,
        "randomization": {"seed": 90090, "algorithm": "python-random-shuffle"},
        "framework_digest": digest_tree(ROOT, frozen), "subject_digest": digest_tree(ROOT, subject),
        "manifest_ids": [p[1] for p in PRESETS], "planned_measurements": 27,
        "rows": [asdict(r) for r in order], "score_schema": "aether.frontier-benchmark/1",
        "non_goals": ["no provider calls during dry-run", "no empirical scores from cassette/fake runs"],
    }
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    body["preregistration_digest"] = sha256_bytes(canonical)
    return body


def clean_cache(path: Path) -> None:
    for item in path.rglob("*"):
        if item.is_dir() and item.name == "__pycache__":
            shutil.rmtree(item)
        elif item.is_file() and item.suffix in {".pyc", ".pyo"}:
            item.unlink()


def compose_check(preset: str) -> None:
    sys.path.insert(0, str(ROOT))
    from vanguard.packages.agency.manifests.loader import ManifestLoader
    from vanguard.packages.agency.manifests.validator import validate_manifest
    path = MANIFESTS / preset / "manifest.json"
    validate_manifest(path)
    ManifestLoader(MANIFESTS).load_pack(preset)


def dry_run() -> dict[str, Any]:
    registration = preregistration()
    prereg_path = ARTIFACTS / "preregistration.json"
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    if prereg_path.exists() and prereg_path.read_bytes() != (json.dumps(registration, sort_keys=True, indent=2) + "\n").encode():
        raise RuntimeError("immutable preregistration already differs")
    prereg_path.write_text(json.dumps(registration, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")
    evidence: list[dict[str, Any]] = []
    with TemporaryDirectory(prefix="v090-dry-") as temp:
        workspace = Path(temp)
        for row in registration["rows"]:
            clean_cache(workspace)
            compose_check(row["preset"])
            evidence.append({"schema": "aether.frontier-benchmark/1", "run_id": row["run_id"],
                "preregistration_digest": registration["preregistration_digest"],
                "framework_digest": registration["framework_digest"], "manifest_digest": manifest_digest(row["preset"]),
                "task_digest": sha256_bytes(row["challenge"].encode()), "model_requested": MODEL,
                "model_returned": None, "provider": "cassette/fake", "terminal": "DRY_RUN_COMPLETE",
                "failure_taxonomy": [], "non_empirical": True, "oracle": {"instrument_valid": True, "result": None},
                "telemetry": {"reason": "provider_not_called; telemetry_not_available"}, "patch": None,
                "trajectory_digest": None})
    report = {"schema": "aether.frontier-benchmark-report/1", "non_empirical": True, "rows": evidence}
    report_path = ARTIFACTS / "dry_run_report.json"
    if report_path.exists():
        raise RuntimeError("refusing to overwrite existing dry-run report")
    report_path.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")
    return {"preregistration": prereg_path, "report": report_path, "rows": len(evidence)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preregister", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--validate-subset", action="store_true")
    args = parser.parse_args()
    if not (args.preregister or args.dry_run or args.validate_subset):
        parser.error("choose --preregister, --dry-run, or --validate-subset")
    if args.preregister:
        print(json.dumps(preregistration(), indent=2, sort_keys=True))
    if args.dry_run:
        result = dry_run()
        print(f"dry-run complete: {result['rows']} rows; non-empirical")
    if args.validate_subset:
        from benchmarks.frontier_v090.runner import validate_subset
        print(json.dumps(validate_subset(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
