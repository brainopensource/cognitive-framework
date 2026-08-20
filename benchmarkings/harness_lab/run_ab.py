"""harness_lab — compile a harness from a manifest, run it against N model routes,
and record what the harness *did to* each turn.

This is a workflow inspector, not a new engine. It reuses the composition root
(`Runtime.compose` / `Runtime.execute_harness`), the same kernel, the same
approval flow and the same sandbox as every other suite here. What it adds is a
tracer at the two seams a reader normally cannot see:

  * the model seam — what context went in, what raw tool call came back;
  * the translator seam — what the model's call was rewritten into before the
    kernel saw it (alias -> canonical verb, arguments -> bound resource).

Those two, plus the receipt, are the whole `observe -> propose -> authorize ->
effect -> receipt` lifecycle for one turn, so a run of this file prints the
lifecycle rather than asserting it happened.

Usage:
    python3 benchmarkings/harness_lab/run_ab.py \
        --task zero_hint_stats --profile profiles/qwen25-coder-14b.json \
        --profile profiles/deepseek-coder-v2-16b.json
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

SUITE = Path(__file__).resolve().parent
ROOT = SUITE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
_LAM = ROOT / "tools" / "002_LLM_API_MOCK"
if str(_LAM) not in sys.path:
    sys.path.insert(0, str(_LAM))

from verdict import (  # noqa: E402
    lab_operator_signer,
    lab_translator_spy,
    load_provider_secret,
    ollama_model,
    openrouter_model,
)
from benchmarkings.zero_hint_v1.run_live_agent import (  # noqa: E402
    CountingModel,
    LiveModel,
    SkipEvaluator,
    _http_post,
    _prepare_repo,
    _run_tests,
)
from vanguard.packages.runtime.root import Runtime, TaskContext  # noqa: E402

#: Hard spend ceiling for one invocation of this file, in US cents. A run that
#: would cross it stops before the next arm rather than after it: an overrun
#: discovered in the bill is not a control.
BUDGET_CENTS_DEFAULT = 50

HARNESS_DIR = SUITE / "harness"
CHALLENGE_DIR = SUITE / "challenge"
DEFAULT_HARNESS = "vg-mini-coder"

#: Interpreter byproducts. Running the public tests writes `__pycache__`, so
#: staging the workspace stages them too. They are not agent edits, and
#: counting them as out-of-scope changes marks every passing run as a scope
#: violation — the measurement fails closed against the truth.
_ARTIFACT_MARKERS = ("__pycache__/", ".pytest_cache/", ".ruff_cache/")


def _is_artifact(path: str) -> bool:
    return path.endswith((".pyc", ".pyo")) or any(m in path for m in _ARTIFACT_MARKERS)


# ---------------------------------------------------------------------------
# Task + profile loading
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TaskSpec:
    task_id: str
    title: str
    harness: str
    prompt: str
    fixture: Path
    oracle: Path
    public_cmd: tuple[str, ...]
    oracle_cmd: tuple[str, ...]
    allowed_paths: tuple[str, ...]
    max_turns: int


def load_task(task_id: str) -> TaskSpec:
    path = CHALLENGE_DIR / task_id
    meta = json.loads((path / "preregistration.json").read_text(encoding="utf-8"))
    workspace = meta["workspace"]
    return TaskSpec(
        task_id=meta["taskId"],
        title=meta["title"],
        harness=str(meta.get("harness") or DEFAULT_HARNESS),
        prompt=(path / "prompt.txt").read_text(encoding="utf-8").strip(),
        fixture=path / "fixture" / "initial",
        oracle=path / "oracle",
        public_cmd=tuple(workspace["publicTestCommand"]),
        oracle_cmd=tuple(workspace["oracleTestCommand"]),
        allowed_paths=tuple(workspace["allowedChangedPaths"]),
        max_turns=int(meta.get("limits", {}).get("maxTurns", 10)),
    )


def _ollama_host() -> str:
    """Accept the conventional scheme-less `OLLAMA_HOST=host:port` spelling.

    `urllib` raises "unknown url type" on a scheme-less URL, so a machine using
    Ollama's own documented environment form could not run this suite at all.
    """
    raw = (os.environ.get("OLLAMA_HOST") or "").strip().rstrip("/")
    if not raw:
        return "http://127.0.0.1:11434"
    if "://" not in raw:
        return f"http://{raw}"
    return raw


def _usd_cents(profile: Mapping[str, Any], prompt_tokens: int,
               completion_tokens: int) -> float:
    """Cost of one arm from the route's own declared per-million prices."""
    pricing = profile.get("pricing") or {}
    prompt_rate = float(pricing.get("promptPerMillionUsd") or 0.0)
    completion_rate = float(pricing.get("completionPerMillionUsd") or 0.0)
    usd = (prompt_tokens * prompt_rate + completion_tokens * completion_rate) / 1_000_000
    return usd * 100


def load_profile(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("provider") == "ollama":
        payload.setdefault("endpoint", f"{_ollama_host()}/api/chat")
    return payload


# ---------------------------------------------------------------------------
# The tracer — the only thing this file adds to the standard runner
# ---------------------------------------------------------------------------


def _brief_context(context: Mapping[str, Any]) -> dict[str, Any]:
    """Summarise the compiled context bundle without reprinting it whole.

    The layers are what the harness controls: `L1` is the frozen system prompt,
    the brief is the task, and the receipt notes are what previous turns earned.
    A reader wants their sizes and identities, not their bytes.
    """
    out: dict[str, Any] = {}
    for key, value in context.items():
        if isinstance(value, str):
            out[key] = {"chars": len(value), "head": value[:160]}
        elif isinstance(value, (list, tuple)):
            out[key] = {"items": len(value),
                        "labels": [str(getattr(v, "label", None) or
                                       (v.get("label") if isinstance(v, Mapping) else "") or
                                       type(v).__name__)[:40] for v in value[:8]]}
        elif isinstance(value, Mapping):
            out[key] = {"keys": sorted(str(k) for k in value)[:12]}
        else:
            out[key] = {"repr": repr(value)[:80]}
    return out


def _brief_value(value: Any, limit: int = 300) -> Any:
    if isinstance(value, str):
        return value if len(value) <= limit else value[:limit] + f"... (+{len(value)-limit} chars)"
    if isinstance(value, Mapping):
        return {k: _brief_value(v, limit) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_brief_value(v, limit) for v in value]
    return value


class TracingModel:
    """Records the model seam: context in, raw proposal out."""

    def __init__(self, inner: Any, trace: list[dict[str, Any]]) -> None:
        self._inner = inner
        self._trace = trace

    def propose(self, context: Mapping[str, Any], tools: Any, sampling: Mapping[str, Any]) -> Any:
        turn = len(self._trace) + 1
        entry: dict[str, Any] = {
            "turn": turn,
            "observe": {
                "context": _brief_context(context),
                "tools_offered": [
                    (t.get("name") if isinstance(t, Mapping) else str(t))
                    for t in (tools or [])
                ],
            },
        }
        started = time.perf_counter()
        result = self._inner.propose(context, tools, sampling)
        entry["model_ms"] = int((time.perf_counter() - started) * 1000)
        if getattr(result, "ok", False):
            value = getattr(result, "value", {}) or {}
            entry["propose"] = {
                "kind": value.get("kind"),
                "action": value.get("action"),
                "args": _brief_value(value.get("args")),
                "resource": value.get("resource"),
                "note": _brief_value(value.get("note"), 4000),
            }
        else:
            error = getattr(result, "error", None)
            entry["propose"] = {"error": getattr(error, "message", "") or "provider failure"}
        self._trace.append(entry)
        return result


# ---------------------------------------------------------------------------
# One arm
# ---------------------------------------------------------------------------


def run_arm(task: TaskSpec, profile: Mapping[str, Any], *, out_dir: Path,
            manifest_path: Path) -> dict[str, Any]:
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    label = str(profile.get("label") or profile["model"])
    run_dir = out_dir / f"{run_id}_{task.task_id}_{label}"
    run_dir.mkdir(parents=True, exist_ok=True)

    composed = Runtime.compose(manifest_path, episode_id=f"harness-lab-{task.task_id}")
    provider = str(profile["provider"])
    max_tokens = int(profile.get("sampling", {}).get("maxTokens", 2048))
    secret, secret_source = load_provider_secret(ROOT)
    if provider == "openrouter" and not secret:
        record = {"taskId": task.task_id, "arm": label, "status": "FAIL",
                  "terminal": "instrument_error", "error": "OPENROUTER_API_KEY unset"}
        (run_dir / "result.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        return record

    if provider == "ollama":
        inner = ollama_model(model=str(profile["model"]),
                             endpoint=str(profile.get("endpoint") or f"{_ollama_host()}/api/chat"),
                             timeout_seconds=600.0)
    else:
        environ = dict(os.environ)
        if secret:
            environ["OPENROUTER_API_KEY"] = secret
        inner = openrouter_model(model=str(profile["model"]),
                                 endpoint=str(profile.get("endpoint") or
                                              "https://openrouter.ai/api/v1/chat/completions"),
                                 environ=environ, stream=False, max_retries=0,
                                 jitter=False, transport=_http_post)

    trace: list[dict[str, Any]] = []
    counting = CountingModel(LiveModel(inner, max_tokens=max_tokens))
    model = TracingModel(counting, trace)
    translate_rows: list[dict[str, Any]] = []
    uninstall_spy = lab_translator_spy(translate_rows)
    signer = lab_operator_signer(b"harness-lab-operator-key")

    started = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix=f"vg-lab-{task.task_id}-") as tmp:
        root = Path(tmp)
        repo = _prepare_repo(root, task.fixture)
        public_before = _run_tests(repo, task.public_cmd)
        try:
            result = Runtime.execute_harness(
                manifest_path,
                TaskContext(
                    brief=task.prompt,
                    repo_path=repo,
                    run_id=f"harness-lab-{task.task_id}-{run_id}",
                    episode_id=f"harness-lab-episode-{task.task_id}",
                    principal="harness-lab-agent",
                    max_turns=task.max_turns,
                ),
                interactive=True,
                model=model,
                approver=lambda challenge: signer.approve(challenge, reviewer="lab-auto"),
                verifier=SkipEvaluator(),
                approval_key=signer.public_bytes,
            )
            terminal = result.terminal.value
            detail = result.detail
            receipts = [{"verb": r.verb, "outcome": r.outcome,
                         "detail_tail": (r.detail or "")[-1200:]} for r in result.receipts]
            events = [{"kind": e.kind, "reason": getattr(e, "reason", None)}
                      for e in (result.events or [])]
        except Exception as exc:  # a runner fault is data, not a crash
            terminal, detail = "runner_error", f"{type(exc).__name__}: {exc}"
            receipts, events = [], []
        finally:
            uninstall_spy()

        public_after = _run_tests(repo, task.public_cmd)
        eval_root = root / "eval"
        shutil.copytree(repo, eval_root)
        shutil.copytree(task.oracle, eval_root / "oracle")
        oracle_after = _run_tests(eval_root, task.oracle_cmd)
        # Stage first: a greenfield task creates *untracked* files, and plain
        # `git diff` cannot see them. Reporting `changedPaths: []` for a run
        # that wrote a new module makes the out-of-scope check vacuous exactly
        # where it matters most.
        subprocess.run(["git", "add", "-A"], cwd=repo, check=False, capture_output=True)
        (run_dir / "final.diff").write_bytes(subprocess.run(
            ["git", "diff", "--cached", "--binary"], cwd=repo,
            check=False, capture_output=True).stdout)
        changed = [row for row in subprocess.run(
            ["git", "diff", "--cached", "--name-only"], cwd=repo,
            check=False, capture_output=True, text=True).stdout.split()
            if not _is_artifact(row)]
        for rel in changed:
            src = repo / rel
            if src.is_file():
                dest = run_dir / "workspace" / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest)

    # Stitch the three seams into one row per turn.
    for index, row in enumerate(translate_rows):
        if index < len(trace):
            trace[index]["translate"] = row
    for index, receipt in enumerate(receipts):
        if index < len(trace):
            trace[index]["receipt"] = receipt

    record = {
        "schemaVersion": "1.0",
        "suite": "harness_lab",
        "taskId": task.task_id,
        "arm": label,
        "runId": run_id,
        "harness": {
            "name": composed.harness,
            "compositionDigest": composed.composition_digest,
            "verbs": sorted(composed.verbs),
            "capabilitySelectors": list(composed.capability_selectors),
            "toolNames": [t.get("name") for t in composed.tool_schemas],
            "systemPromptChars": len(composed.system_core),
        },
        "model": {"provider": provider, "model": profile["model"],
                  "secretSource": secret_source if provider == "openrouter" else "ollama-local",
                  "calls": counting.calls, "actions": counting.actions,
                  "errors": counting.errors,
                  "promptTokens": counting.prompt_tokens,
                  "completionTokens": counting.completion_tokens,
                  "usdCents": round(_usd_cents(profile, counting.prompt_tokens,
                                               counting.completion_tokens), 4)},
        "labDepartures": ["auto_approve_privileged", "SkipEvaluator_in_episode",
                          "oracle_run_after_episode_not_isolated_daemon"],
        "terminal": terminal,
        "detail": detail,
        "publicTestsBefore": public_before,
        "publicTestsAfter": public_after,
        "oracleAfter": oracle_after,
        "changedPaths": changed,
        "allowedChangedPaths": list(task.allowed_paths),
        "outOfScopeChanges": [c for c in changed if c not in task.allowed_paths],
        "receipts": receipts,
        "events": events,
        "workflow": trace,
        "elapsedMs": int((time.perf_counter() - started) * 1000),
    }
    record["oracleGreen"] = bool(oracle_after.get("passed")) and not record["outOfScopeChanges"]
    record["status"] = "PASS" if record["oracleGreen"] else "FAIL"
    (run_dir / "result.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return record


# ---------------------------------------------------------------------------
# Presentation
# ---------------------------------------------------------------------------


def print_workflow(record: Mapping[str, Any]) -> None:
    print(f"\n{'='*78}\nARM: {record['arm']}   harness={record['harness']['name']} "
          f"{record['harness']['compositionDigest'][:19]}\n{'='*78}")
    for turn in record.get("workflow", []):
        print(f"\n--- turn {turn['turn']} ---")
        ctx = turn.get("observe", {}).get("context", {})
        shown = {k: v for k, v in ctx.items() if k in ("system", "brief", "notes", "messages")}
        print(f"  observe   : {json.dumps(shown or ctx)[:220]}")
        prop = turn.get("propose", {})
        if "error" in prop:
            print(f"  propose   : ERROR {prop['error'][:120]}")
        else:
            print(f"  propose   : kind={prop.get('kind')} action={prop.get('action')} "
                  f"args={json.dumps(prop.get('args'))[:160]}")
        tr = turn.get("translate")
        if tr:
            if tr.get("rejected"):
                print(f"  translate : REJECTED {tr['rejected'][:120]}")
            else:
                arrow = "->" if tr.get("rewritten") else "=="
                print(f"  translate : {tr.get('tool_called')} {arrow} {tr.get('canonical_verb')}"
                      f"  resource={json.dumps(tr.get('bound_resource'))}")
        rec = turn.get("receipt")
        if rec:
            print(f"  receipt   : {rec['verb']} {rec['outcome']} | "
                  f"{(rec['detail_tail'] or '')[:120].replace(chr(10), ' ')}")
        else:
            print("  receipt   : (none — denied or no dispatch)")
    print(f"\n  terminal  : {record['terminal']} ({record.get('detail')})")
    print(f"  changed   : {record['changedPaths']}")
    print(f"  public    : {record['publicTestsAfter'].get('passed')}   "
          f"oracle: {record['oracleAfter'].get('passed')}   -> {record['status']}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="harness_lab A/B workflow inspector")
    parser.add_argument("--task", action="append", dest="tasks",
                        help="Repeatable. Default: zero_hint_stats")
    parser.add_argument("--profile", action="append", dest="profiles", required=True)
    parser.add_argument("--harness", default=None,
                        help="Harness name under harness/ (default: the task's own)")
    parser.add_argument("--out-dir", default=str(SUITE / "runs"))
    parser.add_argument("--budget-cents", type=float, default=BUDGET_CENTS_DEFAULT,
                        help="Stop before an arm that would cross this ceiling")
    parser.add_argument("--quiet", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    task_ids = args.tasks or ["zero_hint_stats"]
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    profiles = []
    for raw in args.profiles:
        path = Path(raw)
        if not path.is_absolute():
            path = SUITE / raw
        profiles.append(load_profile(path))

    spent = 0.0
    records: list[dict[str, Any]] = []
    for task_id in task_ids:
        task = load_task(task_id)
        harness_name = args.harness or task.harness
        manifest_path = HARNESS_DIR / harness_name / "manifest.json"
        print(f"\ntask    : {task.task_id} — {task.title}")
        print(f"harness : {harness_name}")
        for profile in profiles:
            label = str(profile.get("label") or profile["model"])
            if spent >= args.budget_cents:
                print(f"  SKIP {label}: budget ceiling {args.budget_cents}c reached "
                      f"(spent {spent:.2f}c)")
                continue
            print(f"\n  running {label} ...")
            record = run_arm(task, profile, out_dir=out_dir, manifest_path=manifest_path)
            spent += float(record.get("model", {}).get("usdCents") or 0.0)
            records.append(record)
            if not args.quiet:
                print_workflow(record)
            print(f"  [spend so far: {spent:.2f}c of {args.budget_cents}c]")

    print(f"\n{'='*92}\nSUMMARY\n{'='*92}")
    print(f"{'task':<24}{'arm':<26}{'calls':>6}{'changed':>8}{'public':>8}"
          f"{'oracle':>8}{'cents':>8}  status")
    for record in records:
        print(f"{record['taskId']:<24}{record['arm']:<26}"
              f"{record['model']['calls']:>6}{len(record['changedPaths']):>8}"
              f"{str(record['publicTestsAfter'].get('passed')):>8}"
              f"{str(record['oracleAfter'].get('passed')):>8}"
              f"{record['model'].get('usdCents', 0):>8.3f}  {record['status']}")
    print(f"\ntotal spend: {spent:.2f} US cents")
    summary = {"tasks": task_ids, "totalCents": round(spent, 4),
               "arms": [{k: r[k] for k in ("taskId", "arm", "status", "terminal",
                                           "changedPaths", "oracleGreen")} | 
                        {"cents": r["model"].get("usdCents")} for r in records]}
    (out_dir / "summary_openrouter.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
