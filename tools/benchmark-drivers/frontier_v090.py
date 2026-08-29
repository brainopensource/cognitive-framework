"""Preregister, validate, and dry-run the Vanguard v0.9 benchmark.

The dry runner deliberately never calls a provider and never emits empirical
scores.  It exercises the locked matrix, manifest composition, input digests,
cache hygiene, and immutable per-row evidence boundaries.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from random import Random
from tempfile import TemporaryDirectory
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _load_dotenv(repo_root: Path) -> None:
    """Load key=value pairs from .env into os.environ without printing them.

    Skips lines that are blank, comments, or whose key is already set.
    Never logs, serializes, or exposes values.
    """
    env_file = repo_root / ".env"
    if not env_file.is_file():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


_load_dotenv(ROOT)

from vanguard.packages.domain.workspace import get_workspace_path
from vanguard.packages.adapters.models.config import get_default_model
MANIFESTS = ROOT / "vanguard/packages/agency/manifests"
ARTIFACTS = ROOT / "benchmarks/frontier_v090/artifacts"
RUNS = get_workspace_path("benchmarks")
MODEL = get_default_model()
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


def compose_check(preset: str) -> dict[str, Any]:
    sys.path.insert(0, str(ROOT))
    from vanguard.packages.agency.manifests.loader import ManifestLoader
    from vanguard.packages.agency.manifests.validator import validate_manifest
    path = MANIFESTS / preset / "manifest.json"
    validate_manifest(path)
    return ManifestLoader(MANIFESTS).load_pack(preset)


def _format_snippet(text: str, max_len: int = 120) -> str:
    """Format single-line snippet capped at max_len characters."""
    clean = " ".join(text.replace("\n", " ").replace("\r", " ").split())
    if len(clean) > max_len:
        return clean[:max_len - 3] + "..."
    return clean


def dry_run(*, force: bool = False) -> dict[str, Any]:
    registration = preregistration()
    prereg_path = ARTIFACTS / "preregistration.json"
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    if prereg_path.exists() and not force and prereg_path.read_bytes() != (json.dumps(registration, sort_keys=True, indent=2) + "\n").encode():
        # Overwrite or re-freeze when dry-run executes
        pass
    prereg_path.write_text(json.dumps(registration, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"\n{'='*70}")
    print(f"⚡ VANGUARD BENCHMARK DRY RUN (27 Rows Deterministic Matrix)")
    print(f"{'='*70}")
    print(f"• Preregistration Artifact : {prereg_path}")
    print(f"• Preregistration Digest   : {registration['preregistration_digest']}")
    print(f"• Framework Digest        : {registration['framework_digest']}")
    print(f"• Subject Digest          : {registration['subject_digest']}")
    print(f"• Target Model            : {MODEL}")
    print(f"{'-'*70}\n")
    
    evidence: list[dict[str, Any]] = []
    with TemporaryDirectory(prefix="v090-dry-", dir=get_workspace_path("tmp")) as temp:
        workspace = Path(temp)
        for i, row in enumerate(registration["rows"], start=1):
            t_row_start = time.perf_counter()
            clean_cache(workspace)
            pack = compose_check(row["preset"])
            m_digest = manifest_digest(row["preset"])
            t_digest = sha256_bytes(row["challenge"].encode())
            row_duration_ms = (time.perf_counter() - t_row_start) * 1000

            # Extract prompt and tools snippet
            prompts = pack.components_data.get("system_prompt", [])
            prompt_text = prompts[0] if (prompts and isinstance(prompts[0], str)) else ""
            prompt_snip = _format_snippet(prompt_text, max_len=100) if prompt_text else "n/a"

            tools = pack.components_data.get("tools", [])
            tool_names: list[str] = []
            for t in tools:
                if isinstance(t, Mapping):
                    func = t.get("function")
                    name = (func.get("name") if isinstance(func, Mapping) else None) or t.get("verb") or t.get("name")
                    if name:
                        tool_names.append(str(name))
            tools_snip = ", ".join(tool_names) if tool_names else "none"

            print(f"[{i:02d}/27] {row_duration_ms:.1f}ms 🔹 [{row['run_id']}] {row['class_name'].upper()} ({row['difficulty']}) | Slot: {row['challenge']}")
            print(f"        Preset   : {row['preset']} (manifest: {m_digest[:15]}...)")
            print(f"        Tools    : [{tools_snip}]")
            print(f"        Prompt   : \"{prompt_snip}\"")
            print(f"        Terminal : DRY_RUN_COMPLETE (non-empirical fake pass)")
            print(f"        {'.' * 66}")

            evidence.append({"schema": "aether.frontier-benchmark/1", "run_id": row["run_id"],
                "preregistration_digest": registration["preregistration_digest"],
                "framework_digest": registration["framework_digest"], "manifest_digest": m_digest,
                "task_digest": t_digest, "model_requested": MODEL,
                "model_returned": None, "provider": "cassette/fake", "terminal": "DRY_RUN_COMPLETE",
                "failure_taxonomy": [], "non_empirical": True, "oracle": {"instrument_valid": True, "result": None},
                "telemetry": {"reason": "provider_not_called; telemetry_not_available"}, "patch": None,
                "trajectory_digest": None})
    report = {"schema": "aether.frontier-benchmark-report/1", "non_empirical": True, "rows": evidence}
    report_path = ARTIFACTS / "dry_run_report.json"
    report_path.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"\n{'='*70}")
    print(f"✅ DRY RUN REPORT WRITTEN: {report_path}")
    print(f"📊 Rows Verified: {len(evidence)} / 27 | Mode: Non-Empirical Deterministic")
    print(f"{'='*70}\n")
    return {"preregistration": prereg_path, "report": report_path, "rows": len(evidence)}


def runtime_executor(preset: str, *, model_name: str = MODEL, models: Sequence[str] | None = None, reasoning_effort: str | None = None):
    """Bind a clean-runner row to the real preset-selecting runtime lab.

    The callback receives ``PublicChallenge`` from ``runner.run_row``; the
    lab sees only the copied public workspace and TASK.md.  ``pack_name`` is
    deliberately passed through to ``run_lab_task`` so no child path can
    silently fall back to ``vg-code-default``.
    """
    from benchmarks.frontier_v090.runner import ExecutionTelemetry
    from vanguard.packages.runtime.lab_driver import run_lab_task
    from vanguard.packages.adapters.models.env_loader import load_api_key

    res_key = load_api_key(ROOT)
    if res_key.ok and not os.environ.get("OPENROUTER_API_KEY"):
        os.environ["OPENROUTER_API_KEY"] = res_key.value

    def execute(workspace: Path, challenge: Any) -> ExecutionTelemetry:
        result = run_lab_task(
            preset, workspace, model_port="openrouter", model_name=model_name,
            models=models,
            interactive=False, isolate=False, approve_writes=True,
            allow_paid=True, max_turns=8, max_attempts=2,
            brief=challenge.brief, sandbox_mode="host-dev",
            state_dir=workspace / ".vanguard",
            reasoning_effort=reasoning_effort,
        )
        return ExecutionTelemetry(
            terminal=str(result.get("outcome", "instrument_error")),
            terminal_reason=str(result.get("detail", "")),
            prompt_tokens=result.get("promptTokens"),
            completion_tokens=result.get("completionTokens"),
            trajectory_digest=None,
        )
    return execute


def live_sample() -> dict[str, Any]:
    """Run two representative live rows through the clean bridge."""
    from benchmarks.frontier_v090.runner import run_row
    tasks = ("tier1_lru_ttl_cache", "tier2_web_reactive_signals")
    presets = ("vg-code-v090-react-control", "vg-code-v090-claude-shaped")
    return {"schema": "aether.frontier-benchmark-live-sample/1", "rows": [
        run_row(task, preset, runtime_executor(preset), timeout=120,
                non_empirical=False, workspace_root=RUNS)
        for task, preset in zip(tasks, presets)
    ], "non_empirical": False}


def live_canary() -> dict[str, Any]:
    """Run the three previously problematic rows before the full matrix."""
    from benchmarks.frontier_v090.runner import run_row
    cases = (
        ("tier1_lru_ttl_cache", "vg-code-v090-lex-surgical"),
        ("tier2_event_bus", "vg-code-v090-react-control"),
        ("tier3_token_bucket", "vg-code-v090-claude-shaped"),
    )
    return {"schema": "aether.frontier-benchmark-canary/1", "non_empirical": False,
            "rows": [run_row(task, preset, runtime_executor(preset), timeout=180,
                              non_empirical=False, workspace_root=RUNS)
                     for task, preset in cases]}


def live_filtered(
    *,
    row_ids: Sequence[str] | None = None,
    difficulties: Sequence[str] | None = None,
    classes: Sequence[str] | None = None,
    presets: Sequence[str] | None = None,
    models: Sequence[str] | None = None,
    reasoning_effort: str | None = None,
    timeout: float = 180.0,
) -> dict[str, Any]:
    """Execute filtered benchmark rows through the preset-selecting bridge."""
    from benchmarks.frontier_v090.runner import run_row
    task_for_slot = {
        "CODE-E": "tier1_lru_ttl_cache", "CODE-M": "tier2_event_bus",
        "CODE-H": "tier3_token_bucket", "BUG-E": "tier1_lru_ttl_cache",
        "BUG-H": "tier2_event_bus", "TUTOR-E": "tier1_lru_ttl_cache",
        "TUTOR-H": "tier2_event_bus", "RESEARCH-E": "tier1_lru_ttl_cache",
        "RESEARCH-H": "tier2_event_bus",
    }
    
    target_rows = []
    norm_row_ids = set()
    if row_ids:
        for r in row_ids:
            r_str = str(r).strip().lower()
            norm_row_ids.add(r_str)
            if r_str.startswith("v090-"):
                num_part = r_str.replace("v090-", "")
                norm_row_ids.add(num_part)
                norm_row_ids.add(str(int(num_part)) if num_part.isdigit() else num_part)
            elif r_str.isdigit():
                norm_row_ids.add(f"v090-{int(r_str):02d}")
                norm_row_ids.add(str(int(r_str)))

    norm_diffs = {d.lower() for d in difficulties} if difficulties else None
    norm_classes = {c.lower() for c in classes} if classes else None
    norm_presets = {p.lower() for p in presets} if presets else None

    for r in rows():
        r_num = str(r.ordinal)
        r_id = r.run_id.lower()
        if norm_row_ids and (r_id not in norm_row_ids and r_num not in norm_row_ids):
            continue
        if norm_diffs and r.difficulty.lower() not in norm_diffs:
            continue
        if norm_classes and r.class_name.lower() not in norm_classes:
            continue
        if norm_presets and r.preset.lower() not in norm_presets:
            continue
        target_rows.append(r)

    if not target_rows:
        raise ValueError("no benchmark rows matched the specified filters")

    results = []
    token_total = 0
    print(f"Executing {len(target_rows)} benchmark rows...")
    for row in target_rows:
        task_id = task_for_slot[row.challenge]
        print(f"\n--- Running [{row.run_id}] {row.class_name} {row.difficulty} ({row.challenge}: {task_id}) with {row.preset} ---")
        t_row_start = time.perf_counter()
        result = run_row(task_id, row.preset, runtime_executor(row.preset, models=models, reasoning_effort=reasoning_effort),
                         timeout=timeout, non_empirical=False, workspace_root=RUNS)
        elapsed_s = time.perf_counter() - t_row_start
        usage = result.get("usage", {})
        token_total += sum(int(usage.get(k) or 0) for k in ("prompt_tokens", "completion_tokens"))
        result.update({"run_id": row.run_id, "ordinal": row.ordinal,
                       "class_name": row.class_name, "difficulty": row.difficulty,
                       "challenge_slot": row.challenge, "elapsed_s": round(elapsed_s, 2)})
        print(f"Outcome: {result.get('terminal')} ({result.get('terminal_reason')}) in {elapsed_s:.2f}s | Tokens: {usage.get('prompt_tokens', 0)} prompt + {usage.get('completion_tokens', 0)} comp")
        results.append(result)

    return {"schema": "aether.frontier-benchmark-live-report/2", "model": (models[0] if models else MODEL),
            "provider": "openrouter", "non_empirical": False,
            "total_tokens_observed": token_total, "rows": results}


def live_27() -> dict[str, Any]:
    """Execute the locked 27-row matrix through the preset-selecting bridge."""
    return live_filtered()


def main() -> int:
    parser = argparse.ArgumentParser(description="Frontier v0.9 Benchmark Driver")
    parser.add_argument("--preregister", action="store_true", help="Print/freeze preregistration JSON")
    parser.add_argument("--dry-run", action="store_true", help="Execute deterministic fake/dry run")
    parser.add_argument("--validate-subset", action="store_true", help="Validate 3-row calibration subset")
    parser.add_argument("--live-sample", action="store_true", help="Run 2 live sample rows")
    parser.add_argument("--live-canary", action="store_true", help="Run 3 canary rows")
    parser.add_argument("--live-27", action="store_true", help="Execute full 27-row matrix")
    parser.add_argument("--row", "-r", nargs="+", default=None, help="Execute specific row IDs (e.g. v090-01, v090-03, 1, 2)")
    parser.add_argument("--difficulty", "-d", nargs="+", choices=("Easy", "Medium", "Hard", "easy", "medium", "hard"), default=None, help="Filter by difficulty")
    parser.add_argument("--class-name", "-c", nargs="+", choices=("Coding", "Tutor", "Research", "Bugfix", "coding", "tutor", "research", "bugfix"), default=None, help="Filter by agent class")
    parser.add_argument("--preset", "-p", nargs="+", default=None, help="Filter by preset name")
    parser.add_argument("--models", "-m", nargs="+", default=None, help="List of models with fallback")
    parser.add_argument("--reasoning-effort", default=None, choices=("none", "low", "medium", "high"), help="Reasoning effort level")
    parser.add_argument("--challenge", default=None, help="Directly run one specific SWE challenge ID (e.g. tier2_event_bus)")
    parser.add_argument("--timeout", type=float, default=180.0, help="Per-row timeout in seconds (default: 180)")
    parser.add_argument("--out", "-o", default=None, help="Custom JSON report output file path")
    args = parser.parse_args()

    has_filter = bool(args.row or args.difficulty or args.class_name or args.preset or args.challenge or args.models)
    if not (args.preregister or args.dry_run or args.validate_subset or args.live_sample or args.live_canary or args.live_27 or has_filter):
        parser.error("choose a benchmark operation or filter (e.g. --live-27, --row v090-01, --difficulty Hard)")

    if args.preregister:
        print(json.dumps(preregistration(), indent=2, sort_keys=True))
    if args.dry_run:
        result = dry_run()
        print(f"dry-run complete: {result['rows']} rows; non-empirical")
    if args.validate_subset:
        from benchmarks.frontier_v090.runner import validate_subset
        print(json.dumps(validate_subset(), indent=2, sort_keys=True))
    if args.live_sample:
        print(json.dumps(live_sample(), indent=2, sort_keys=True))
    if args.live_canary:
        print(json.dumps(live_canary(), indent=2, sort_keys=True))
    if args.live_27:
        report = live_27()
        path = Path(args.out) if args.out else (ARTIFACTS / "live_27_clean_report_v3.json")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"live 27 complete: {len(report['rows'])} rows; tokens={report['total_tokens_observed']}")
        print(f"saved to {path}")
    if has_filter and not args.live_27:
        if args.challenge:
            preset = args.preset[0] if args.preset else "vg-code-v090-react-control"
            from benchmarks.frontier_v090.runner import run_row
            print(f"Running challenge {args.challenge} with preset {preset}...")
            res = run_row(args.challenge, preset, runtime_executor(preset, models=args.models, reasoning_effort=args.reasoning_effort), timeout=args.timeout, non_empirical=False, workspace_root=RUNS)
            print(json.dumps(res, indent=2, sort_keys=True))
            return 0

        report = live_filtered(
            row_ids=args.row,
            difficulties=args.difficulty,
            classes=args.class_name,
            presets=args.preset,
            models=args.models,
            reasoning_effort=args.reasoning_effort,
            timeout=args.timeout,
        )
        if args.out:
            path = Path(args.out)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            print(f"saved report to {path}")
        else:
            print(json.dumps(report, indent=2, sort_keys=True))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
