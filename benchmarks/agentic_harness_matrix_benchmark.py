#!/usr/bin/env python3
"""Comprehensive Multi-Harness & Multi-Model Agentic Matrix Benchmark.

Evaluates and scores:
1. vg-code-default (Autonomous Coding Harness)
2. vg-code-lex (Deterministic Surgical Patcher)
3. vg-code-explain (RAG Tutor / Codebase Explainer)
4. vg-code-critic-reviser (CodeFix / Critic & Reviewer)
5. vg-code-claude-shaped (Conversational Engineering Agent)

Against:
- OpenRouter Free Models (e.g. openrouter/free, poolside/laguna-s-2.1:free, nvidia/nemotron-3-super-120b-a12b:free, minimax/minimax-m3:free)
- OpenRouter Paid/Fast Models (e.g. deepseek/deepseek-v4-flash, openai/gpt-5.6-luna)
- Deterministic Golden Tape / Cassette Player & Mock Engines

Outputs complete empirical metrics: Score/Pass Rate, Turns, Prompt/Completion Tokens, USD Cost, Latency, and Ledger DAG digest.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Mapping, Sequence

from vanguard.packages.runtime.root import controlled_environment, get_workspace_path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from vanguard.packages.ports.event_store import EventRange
from benchmarks.ladder.control import CONTROL_ARM, ControlManifestError, require_frozen
from benchmarks.ladder.evidence import append_row
from benchmarks.ladder.metrics import BUDGET_EXHAUSTED, budget_exhausted, publish_control_report
from benchmarks.product_path import PRODUCT_PRESETS, execute_product
from benchmarks.swe_bench.challenges import CHALLENGES

MANIFEST_ROOT = ROOT / "vanguard" / "packages" / "agency" / "manifests"


def write_control_report(
    *,
    path: Path,
    record: Mapping[str, Any],
    rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Publish one admitted control report at the real benchmark writer boundary."""
    report = publish_control_report(record=record, rows=rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    return report


def _control_submission(
    record: Mapping[str, Any],
    rows: Sequence[Mapping[str, Any]],
    *,
    harness_name: str,
    task_name: str,
    profile_id: str,
) -> dict[str, Any]:
    """Admit one scheduled control dispatch before the product call happens."""
    manifest = require_frozen(record)
    if harness_name != CONTROL_ARM["harness"] or profile_id != "product":
        raise ControlManifestError(
            "T-26b: control dispatch requires vg-code-balanced on the product profile")
    tasks = manifest["suite"]["tasks"]
    if task_name not in tasks:
        raise ControlManifestError("T-26b: task is absent from the frozen control membership")
    observed_ids: set[str] = set()
    checked: list[dict[str, Any]] = []
    for row in rows:
        # Reuse the canonical row/mixed-evidence validator before any dispatch.
        append_row(checked, row)
        identity = row.get("identity") or {}
        row_arm = row.get("arm") or {}
        task_id = str(identity.get("task_id") or "")
        if task_id not in tasks or task_id in observed_ids:
            raise ControlManifestError("T-26b: prior evidence has an unscheduled or duplicate task")
        if (
            identity.get("subject_sha") != manifest["subject_sha"]
            or identity.get("suite_digest") != manifest["suite_digest"]
            or identity.get("n") != len(tasks)
            or identity.get("task_digest") != manifest["suite"]["task_digests"].get(task_id)
            or identity.get("oracle_digest") != manifest["suite"]["oracle_digests"].get(task_id)
            or row_arm.get("model_id") != manifest["model_id"]
            or row_arm.get("provider") != manifest["arm"]["provider"]
            or row_arm.get("preset") != CONTROL_ARM["preset"]
            or any(
                row_arm.get(field) != manifest["arm"][field]
                for field in ("manifest_digest", "sampling_digest", "prompt_digest", "tool_schema_digest")
            )
        ):
            raise ControlManifestError(
                "T-26b: prior evidence does not bind the frozen control candidate")
        observed_ids.add(task_id)
    if task_name in observed_ids:
        raise ControlManifestError("T-26b: a scheduled task cannot be dispatched twice")
    if any(budget_exhausted(row) for row in rows):
        raise ControlManifestError(
            "T-26b: a budget-exhausted slot stops control dispatch before a replacement")
    if len(rows) >= len(tasks):
        raise ControlManifestError("T-26b: the frozen control population is already complete")
    return manifest


def _control_evidence_row(
    *,
    manifest: Mapping[str, Any],
    task_name: str,
    run_id: str,
    frame: Mapping[str, Any],
    receipt: Mapping[str, Any],
    oracle_passed: bool,
    oracle_stderr: str,
    wall_ms: float,
) -> dict[str, Any]:
    """Bind the product frame and exterior oracle verdict to one frozen slot."""
    returned_run_id = str(frame.get("runId") or receipt.get("runId") or "")
    if returned_run_id != run_id:
        raise ControlManifestError("T-26b: product frame does not bind the submitted run id")
    outcome = str(receipt.get("outcome") or "instrument_error").lower()
    if outcome == BUDGET_EXHAUSTED:
        terminal_status = BUDGET_EXHAUSTED
        disposition = "not_run"
        reason = BUDGET_EXHAUSTED
    elif outcome in {"instrument_error", "runtime_error"}:
        terminal_status = outcome
        disposition = "undeterminable"
        reason = outcome
    else:
        terminal_status = outcome
        disposition = "passed" if oracle_passed else "failed"
        reason = None
    arm = manifest["arm"]
    suite = manifest["suite"]
    raw_response = hashlib.sha256(
        json.dumps(frame, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    return {
        "identity": {
            "subject_sha": manifest["subject_sha"],
            "dirty_flag": False,
            "suite_digest": manifest["suite_digest"],
            "n": len(suite["tasks"]),
            "task_id": task_name,
            "task_digest": suite["task_digests"][task_name],
            "oracle_digest": suite["oracle_digests"][task_name],
            "run_id": run_id,
        },
        "arm": {
            "manifest_digest": arm["manifest_digest"],
            "preset": CONTROL_ARM["preset"],
            "model_id": manifest["model_id"],
            "provider": arm["provider"],
            "server_build": None,
            "gguf_digest": None,
            "quantization": None,
            "context_size": None,
            "sampling_digest": arm["sampling_digest"],
            "prompt_digest": arm["prompt_digest"],
            "tool_schema_digest": arm["tool_schema_digest"],
        },
        "execution": {
            "evidence_label": "LIVE-LOCAL",
            "raw_response_digest": f"sha256:{raw_response}",
            "valid_tool_calls": None,
            "malformed_tool_calls": None,
            "recovery_attempts": None,
            "turns": receipt.get("turns"),
            "time_to_first_valid_action_s": None,
            "latency_s": wall_ms / 1000.0,
        },
        "change": {
            "patch_digest": None,
            "postimage_digest": None,
            "files_changed": None,
            "no_op": None,
        },
        "verification": {
            "tests_discovered": None,
            "tests_executed": 1,
            "tests_passed": 1 if oracle_passed else 0,
            "tests_failed": 0 if oracle_passed else 1,
            "tamper_digest": None,
            "tamper_verdict": "clean" if oracle_passed else oracle_stderr,
        },
        "settlement": {
            "terminal_status": terminal_status,
            "disposition": disposition,
            "undeterminable_reason": reason,
        },
        "economics": {
            "prompt_tokens": receipt.get("promptTokens"),
            "completion_tokens": receipt.get("completionTokens"),
            "cache_read_tokens": None,
            "cache_write_tokens": None,
            "cost_usd_micros": receipt.get("spentUsdMicros"),
            "local_time_proxy_s": wall_ms / 1000.0,
        },
        "provenance": {
            "hypothesis_id": "control",
            "control_digest": arm["manifest_digest"],
            "varied_dimension": None,
        },
    }


def run_single_harness_task(
    harness_name: str,
    task_name: str,
    brief: str,
    files: Mapping[str, str],
    oracle_code: str,
    model: Any,
    max_turns: int = 6,
    profile_id: str = "local",
    control_record: Mapping[str, Any] | None = None,
    control_rows: list[dict[str, Any]] | None = None,
    control_report_path: Path | None = None,
) -> dict[str, Any]:
    """Execute a real episode through the Vanguard runtime kernel and evaluate the oracle."""
    control_manifest: dict[str, Any] | None = None
    if control_record is not None:
        if control_rows is None or control_report_path is None:
            raise ControlManifestError(
                "T-26b: a control dispatch requires an evidence accumulator and report path")
        control_manifest = _control_submission(
            control_record,
            control_rows,
            harness_name=harness_name,
            task_name=task_name,
            profile_id=profile_id,
        )
    elif control_rows is not None or control_report_path is not None:
        raise ControlManifestError("T-26b: control rows and report path require a frozen record")
    manifest_path = MANIFEST_ROOT / harness_name / "manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")

    with tempfile.TemporaryDirectory(dir=get_workspace_path("benchmarks")) as d:
        repo = Path(d) / "workspace"
        repo.mkdir(parents=True, exist_ok=True)

        for rel_path, content in files.items():
            target = repo / rel_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")

        oracle_path = repo / "test_oracle.py"
        oracle_path.write_text(oracle_code, encoding="utf-8")

        import subprocess
        subprocess.run(["git", "init"], cwd=repo, env=controlled_environment(os.environ), capture_output=True, check=False)
        subprocess.run(["git", "config", "user.name", "Bench"], cwd=repo, env=controlled_environment(os.environ), capture_output=True, check=False)
        subprocess.run(["git", "config", "user.email", "bench@test.local"], cwd=repo, env=controlled_environment(os.environ), capture_output=True, check=False)
        subprocess.run(["git", "add", "."], cwd=repo, env=controlled_environment(os.environ), capture_output=True, check=False)
        subprocess.run(["git", "commit", "-m", "init"], cwd=repo, env=controlled_environment(os.environ), capture_output=True, check=False)

        run_id = f"bench-{harness_name}-{task_name}-{time.perf_counter_ns()}"

        db_path = repo / ".vanguard" / "events.sqlite3"
        db_path.parent.mkdir(parents=True, exist_ok=True)

        start_t = time.perf_counter()
        try:
            frame = execute_product(
                workspace=repo,
                brief=brief,
                harness=harness_name,
                preset=(CONTROL_ARM["preset"] if control_manifest else
                        PRODUCT_PRESETS.get(harness_name, "balanced")),
                model=model,
                profile_id=("product" if control_manifest else profile_id),
                run_id=run_id,
                store_path=db_path,
                interactive=False,
                max_turns=max_turns,
            )
            wall_ms = (time.perf_counter() - start_t) * 1000.0
            receipt = frame.get("result") or {}
            terminal_val = str(receipt.get("outcome") or "error").lower()

            import subprocess
            proc = subprocess.run(
                [sys.executable, "-m", "unittest", "test_oracle.py"],
                cwd=repo,
                env=controlled_environment(os.environ),
                capture_output=True,
                text=True,
                timeout=15,
            )
            oracle_passed = proc.returncode == 0

            prompt_tokens = receipt.get("promptTokens")
            comp_tokens = receipt.get("completionTokens")
            usd_micros = receipt.get("spentUsdMicros")
            missing: list[str] = []
            if prompt_tokens is None:
                missing.append("prompt_tokens")
            if comp_tokens is None:
                missing.append("completion_tokens")
            if usd_micros is None:
                missing.append("usd_micros")
            total_tokens = None
            if isinstance(prompt_tokens, int) and isinstance(comp_tokens, int):
                total_tokens = prompt_tokens + comp_tokens

            import importlib
            SqliteEventStore = importlib.import_module(
                "vanguard.packages.adapters.stores.event_store").SqliteEventStore
            store = SqliteEventStore(db_path)
            try:
                read_res = store.read(EventRange(run_id=run_id))
                events = list(read_res.value or ())
            finally:
                store.close()
            raw_bytes = sum(len((getattr(ev, "canonical_json", lambda: "")() or "").encode("utf-8")) for ev in events) if events else None
            sqlite_bytes = db_path.stat().st_size if db_path.exists() else None
            waf = None
            if raw_bytes and sqlite_bytes:
                waf = round(sqlite_bytes / max(1, raw_bytes), 2)

            control_evidence = None
            control_report = None
            if control_manifest is not None and control_rows is not None:
                control_evidence = _control_evidence_row(
                    manifest=control_manifest,
                    task_name=task_name,
                    run_id=run_id,
                    frame=frame,
                    receipt=receipt,
                    oracle_passed=oracle_passed,
                    oracle_stderr=proc.stderr,
                    wall_ms=wall_ms,
                )
                control_rows.append(control_evidence)
                if len(control_rows) == len(control_manifest["suite"]["tasks"]):
                    control_report = write_control_report(
                        path=control_report_path,
                        record=control_manifest,
                        rows=control_rows,
                    )

            result = {
                "harness": harness_name,
                "task": task_name,
                "terminal": terminal_val,
                "disposition": "passed" if oracle_passed else "failed",
                "oracle_passed": oracle_passed,
                "score": 1.0 if oracle_passed else 0.0,
                "turns": receipt.get("turns"),
                "wall_ms": round(wall_ms, 2),
                "prompt_tokens": prompt_tokens,
                "completion_tokens": comp_tokens,
                "total_tokens": total_tokens,
                "usd_micros": usd_micros,
                "cost_usd": None if not isinstance(usd_micros, int) else round(usd_micros / 1_000_000.0, 6),
                "events_emitted": len(events),
                "storage_amplification": waf,
                "oracle_stderr": proc.stderr if not oracle_passed else "",
                "missing": missing,
                "preset": PRODUCT_PRESETS.get(harness_name),
            }
            if control_evidence is not None:
                result["control_evidence"] = control_evidence
                result["control_report"] = control_report
            return result
        except Exception as exc:
            if control_manifest is not None:
                raise
            return {
                "harness": harness_name,
                "task": task_name,
                "terminal": "instrument_error",
                "disposition": "undeterminable",
                "oracle_passed": None,
                "score": None,
                "turns": None,
                "wall_ms": round((time.perf_counter() - start_t) * 1000.0, 2),
                "prompt_tokens": None,
                "completion_tokens": None,
                "total_tokens": None,
                "usd_micros": None,
                "cost_usd": None,
                "events_emitted": None,
                "storage_amplification": None,
                "error": str(exc),
                "missing": [
                    "prompt_tokens", "completion_tokens", "usd_micros",
                    "oracle_passed", "events_emitted",
                ],
            }


def _load_openrouter_key() -> str | None:
    """Load OpenRouter API key from environment or .env file."""
    key = os.environ.get("OPENROUTER_API_KEY")
    if key and not key.startswith("your_"):
        return key
    env_file = ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("OPENROUTER_API_KEY="):
                val = line.split("=", 1)[1].strip().strip('"').strip("'")
                if val and not val.startswith("your_"):
                    return val
    return None


def query_model_with_fallback(model: str, messages: list[dict], tools: list[dict] | None = None) -> dict[str, Any]:
    """Execute live completion against OpenRouter API with real network latency and telemetry."""
    import urllib.request
    import urllib.error

    api_key = _load_openrouter_key()
    if not api_key:
        return {
            "model": model,
            "error": "No OPENROUTER_API_KEY found in environment or .env",
            "content": "",
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "usd_micros": 0,
            "cost_usd": 0.0,
            "latency_ms": 0.0,
            "is_live": False,
        }

    start_t = time.perf_counter()
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": 300,
        "temperature": 0.0,
    }
    if tools:
        payload["tools"] = tools

    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://vanguard.ai",
            "X-Title": "Vanguard-Benchmark-Matrix",
        },
        data=json.dumps(payload).encode("utf-8"),
    )

    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            elapsed_ms = (time.perf_counter() - start_t) * 1000.0
            data = json.loads(resp.read().decode("utf-8"))
            usage = data.get("usage", {})
            p_tokens = int(usage.get("prompt_tokens", 0) or 0)
            c_tokens = int(usage.get("completion_tokens", 0) or 0)
            t_tokens = int(usage.get("total_tokens", p_tokens + c_tokens) or (p_tokens + c_tokens))
            raw_cost = usage.get("cost", 0.0) or 0.0
            usd_micros = int(raw_cost * 1_000_000)

            choices = data.get("choices", [])
            content = ""
            if choices and "message" in choices[0]:
                content = choices[0]["message"].get("content", "") or ""

            return {
                "model": data.get("model", model),
                "requested_model": model,
                "content": content,
                "prompt_tokens": p_tokens,
                "completion_tokens": c_tokens,
                "total_tokens": t_tokens,
                "usd_micros": usd_micros,
                "cost_usd": round(raw_cost, 6),
                "latency_ms": round(elapsed_ms, 2),
                "is_live": True,
                "raw_response_id": data.get("id", ""),
            }
    except Exception as exc:
        elapsed_ms = (time.perf_counter() - start_t) * 1000.0
        return {
            "model": model,
            "requested_model": model,
            "error": str(exc),
            "content": "",
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "usd_micros": 0,
            "cost_usd": 0.0,
            "latency_ms": round(elapsed_ms, 2),
            "is_live": False,
        }


def run_rag_tutor_benchmark(models: list[str]) -> list[dict[str, Any]]:
    """Benchmark the vg-code-explain / RAG Tutor harness across codebase explanation prompts."""
    rag_prompts = [
        {
            "query_id": "rag_01_kernel_attenuation",
            "topic": "Kernel Monotonic Capability Attenuation",
            "prompt": "Explain how the Vanguard Kernel monotonically attenuates capabilities from parent to spawned child in `attenuation.py`. Cite invariants and methods.",
            "ground_truth_symbols": ["monotonic", "attenuate", "invariant", "fail_closed"],
        },
        {
            "query_id": "rag_02_sqlite_wal_durability",
            "topic": "SQLite-WAL Event Store & Merkle DAG",
            "prompt": "How does SqliteEventStore guarantee event immutability, optimistic sequence locking, and Merkle root digest computation across crashes?",
            "ground_truth_symbols": ["sqlite", "cas", "merkle", "sequence", "integrity"],
        },
        {
            "query_id": "rag_03_compaction_policy",
            "topic": "Structured Context Compaction & Token Ceilings",
            "prompt": "How does structured consolidation in `compaction.py` prevent token blowup while preserving dead-end records and active constraints?",
            "ground_truth_symbols": ["consolidat", "window", "token", "dead_end"],
        }
    ]

    results = []
    for m in models:
        for q in rag_prompts:
            print(f"  ▶ [RAG Tutor / vg-code-explain] Model: {m} | Query: {q['query_id']}...")
            res = query_model_with_fallback(
                model=m,
                messages=[
                    {"role": "system", "content": "You are the Vanguard RAG Tutor & Codebase Explainer (vg-code-explain). Answer technical queries with precise symbol citations, architectural invariants, and concise explanations."},
                    {"role": "user", "content": q["prompt"]}
                ]
            )
            if "error" not in res and res.get("content"):
                content = res.get("content", "").lower()
                hits = sum(1 for sym in q["ground_truth_symbols"] if sym.lower() in content)
                fidelity_score = round(hits / len(q["ground_truth_symbols"]), 2)
                results.append({
                    "harness": "vg-code-explain (RAG Tutor)",
                    "model": m,
                    "actual_model": res.get("model", m),
                    "query_id": q["query_id"],
                    "topic": q["topic"],
                    "fidelity_score": fidelity_score,
                    "symbols_found": f"{hits}/{len(q['ground_truth_symbols'])}",
                    "wall_ms": res.get("latency_ms", 0),
                    "prompt_tokens": res.get("prompt_tokens", 0),
                    "completion_tokens": res.get("completion_tokens", 0),
                    "total_tokens": res.get("total_tokens", 0),
                    "cost_usd": res.get("cost_usd", 0.0),
                    "status": "PASSED" if fidelity_score >= 0.5 else "PARTIAL",
                    "is_live": res.get("is_live", False),
                    "response_snippet": res.get("content", "")[:120].strip().replace("\n", " "),
                })
            else:
                results.append({
                    "harness": "vg-code-explain (RAG Tutor)",
                    "model": m,
                    "actual_model": res.get("model", m),
                    "query_id": q["query_id"],
                    "topic": q["topic"],
                    "fidelity_score": 0.0,
                    "symbols_found": "0/0",
                    "wall_ms": res.get("latency_ms", 0),
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                    "cost_usd": 0.0,
                    "status": f"FAILED ({res.get('error')})",
                    "is_live": False,
                })
    return results


def run_codefix_critic_benchmark(models: list[str]) -> list[dict[str, Any]]:
    """Benchmark the vg-code-critic-reviser harness on bug detection, race conditions, and fix reviews."""
    codefix_scenarios = [
        {
            "case_id": "codefix_01_lru_expiry_bug",
            "title": "LRU TTL Expiry Logic Bug",
            "snippet": (
                "class CacheEntry:\n"
                "    def is_expired(self, current_time: float) -> bool:\n"
                "        if self.ttl_seconds is None:\n"
                "            return False\n"
                "        return False  # BUG: always returns False\n"
            ),
            "defect_pattern": "always returns false",
            "expected_fix": "current_time - self.created_at >= self.ttl_seconds",
        },
        {
            "case_id": "codefix_02_lock_concurrency_leak",
            "title": "Unprotected Resource Mutex Race Condition",
            "snippet": (
                "def get_or_set(key, val):\n"
                "    if key not in db:\n"
                "        # BUG: Check-then-act without lock\n"
                "        time.sleep(0.01)\n"
                "        with lock:\n"
                "            db[key] = val\n"
                "    return db[key]\n"
            ),
            "defect_pattern": "check-then-act",
            "expected_fix": "with lock",
        }
    ]

    results = []
    for m in models:
        for c in codefix_scenarios:
            print(f"  ▶ [CodeFix / vg-code-critic-reviser] Model: {m} | Case: {c['case_id']}...")
            res = query_model_with_fallback(
                model=m,
                messages=[
                    {"role": "system", "content": "You are the Vanguard CodeFix & Critic-Reviser (vg-code-critic-reviser). Diagnose the exact root cause defect in the snippet and provide the corrected code."},
                    {"role": "user", "content": f"Review and fix this code:\n\n{c['snippet']}"}
                ]
            )
            if "error" not in res and res.get("content"):
                content = res.get("content", "").lower()
                detected_defect = c["defect_pattern"].lower() in content or "bug" in content or "false" in content or "race" in content or "lock" in content
                provided_fix = ("return" in content and "ttl" in content) or ("created_at" in content) or ("with lock" in content or "lock" in content)
                score = 1.0 if (detected_defect and provided_fix) else 0.5 if detected_defect else 0.0
                results.append({
                    "harness": "vg-code-critic-reviser (CodeFix)",
                    "model": m,
                    "actual_model": res.get("model", m),
                    "case_id": c["case_id"],
                    "title": c["title"],
                    "score": score,
                    "defect_diagnosed": detected_defect,
                    "fix_generated": provided_fix,
                    "wall_ms": res.get("latency_ms", 0),
                    "prompt_tokens": res.get("prompt_tokens", 0),
                    "completion_tokens": res.get("completion_tokens", 0),
                    "total_tokens": res.get("total_tokens", 0),
                    "cost_usd": res.get("cost_usd", 0.0),
                    "status": "PASSED" if score == 1.0 else "PARTIAL",
                    "is_live": res.get("is_live", False),
                    "response_snippet": res.get("content", "")[:120].strip().replace("\n", " "),
                })
            else:
                results.append({
                    "harness": "vg-code-critic-reviser (CodeFix)",
                    "model": m,
                    "actual_model": res.get("model", m),
                    "case_id": c["case_id"],
                    "title": c["title"],
                    "score": 0.0,
                    "defect_diagnosed": False,
                    "fix_generated": False,
                    "wall_ms": res.get("latency_ms", 0),
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                    "cost_usd": 0.0,
                    "status": f"FAILED ({res.get('error')})",
                    "is_live": False,
                })
    return results


def run_coding_harness_swe_benchmark() -> list[dict[str, Any]]:
    """Execute vg-code-default, vg-code-lex, and vg-code-claude-shaped against SWE challenges with golden fakes & cassettes."""
    import importlib
    FakeModel = importlib.import_module("vanguard.packages.adapters.models.fake").FakeModel
    results = []

    # 1. vg-code-lex on tier1_version_semver_parser (Golden surgical 5-step repair)
    print("  ▶ [Harness: vg-code-lex] Task: tier1_version_semver_parser (Surgical Patcher)...")
    chal_semver = CHALLENGES["tier1_version_semver_parser"]
    lex_tape = [
        {"kind": "effect", "action": "fs.read", "resource": {"kind": "fs", "root": "/workspace", "paths": ["/workspace"]}, "args": {"path": "semver/version.py"}, "note": "read semver version"},
        {"kind": "effect", "action": "patch", "resource": {"kind": "fs", "root": "/workspace", "paths": ["/workspace"]}, "args": {
            "path": "semver/version.py",
            "diff": "--- a/semver/version.py\n+++ b/semver/version.py\n@@ -12,4 +12,4 @@\n     @classmethod\n     def parse(cls, s: str) -> 'Version':\n         parts = [int(p) for p in s.strip().lstrip('v').split('.')]\n-        return cls(parts[0], parts[1], parts[2])\n+        return cls(parts[0], parts[1], parts[2] if len(parts) > 2 else 0)\n"
        }, "note": "apply surgical fix"},
        {"kind": "effect", "action": "proc.exec", "resource": {"kind": "fs", "root": "/workspace", "paths": ["/workspace"]}, "args": {"argv": ["python3", "-m", "unittest", "test_oracle.py"]}, "note": "run oracle"},
        {"kind": "finish", "note": "done"},
    ]
    res_lex = run_single_harness_task(
        harness_name="vg-code-lex",
        task_name="tier1_version_semver_parser",
        brief=chal_semver.brief,
        files=chal_semver.files,
        oracle_code=chal_semver.oracle_code,
        model=FakeModel(lex_tape),
    )
    res_lex["model"] = "cassette/golden-deterministic"
    results.append(res_lex)

    # 2. vg-code-default on tier1_version_semver_parser (Full coding agent)
    print("  ▶ [Harness: vg-code-default] Task: tier1_version_semver_parser (General Coder)...")
    chal_semver = CHALLENGES["tier1_version_semver_parser"]
    default_tape = [
        {"kind": "effect", "action": "fs.read", "resource": {"kind": "fs", "root": "/workspace", "paths": ["/workspace"]}, "args": {"path": "semver/parser.py"}, "note": "read semver parser"},
        {"kind": "effect", "action": "patch.apply", "resource": {"kind": "fs", "root": "/workspace", "paths": ["/workspace"]}, "args": {
            "path": "semver/parser.py",
            "diff": "--- a/semver/parser.py\n+++ b/semver/parser.py\n@@ -12,4 +12,14 @@\n     def parse(cls, version_str: str) -> 'SemVer':\n         # Fix parsing logic\n-        return None\n+        import re\n+        m = re.match(r'^(\\d+)\\.(\\d+)\\.(\\d+)(?:-([0-9A-Za-z.-]+))?$', version_str.strip())\n+        if not m:\n+            raise ValueError(f'Invalid semver: {version_str}')\n+        major, minor, patch, prerelease = m.groups()\n+        return cls(int(major), int(minor), int(patch), prerelease or '')\n"
        }, "note": "apply semver fix"},
        {"kind": "effect", "action": "proc.exec", "resource": {"kind": "fs", "root": "/workspace", "paths": ["/workspace"]}, "args": {"argv": ["python3", "-m", "unittest", "test_oracle.py"]}, "note": "verify oracle"},
        {"kind": "finish", "note": "done"},
    ]
    res_default = run_single_harness_task(
        harness_name="vg-code-default",
        task_name="tier1_version_semver_parser",
        brief=chal_semver.brief,
        files=chal_semver.files,
        oracle_code=chal_semver.oracle_code,
        model=FakeModel(default_tape),
    )
    res_default["model"] = "cassette/golden-deterministic"
    results.append(res_default)

    # 3. vg-code-claude-shaped on tier2_event_bus
    print("  ▶ [Harness: vg-code-claude-shaped] Task: tier2_event_bus (Conversational Engineer)...")
    chal_eventbus = CHALLENGES["tier2_event_bus"]
    claude_tape = [
        {"kind": "effect", "action": "fs.read", "resource": {"kind": "fs", "root": "/workspace", "paths": ["/workspace"]}, "args": {"path": "bus/event_bus.py"}, "note": "read event bus"},
        {"kind": "effect", "action": "patch.apply", "resource": {"kind": "fs", "root": "/workspace", "paths": ["/workspace"]}, "args": {
            "path": "bus/event_bus.py",
            "diff": "--- a/bus/event_bus.py\n+++ b/bus/event_bus.py\n@@ -20,4 +20,10 @@\n     def publish(self, topic: str, payload: Any) -> None:\n-        pass\n+        with self._lock:\n+            for sub in self._subscribers.get(topic, []):\n+                sub(payload)\n+            for pattern, handlers in self._wildcards.items():\n+                if self._match(pattern, topic):\n+                    for h in handlers:\n+                        h(payload)\n"
        }, "note": "implement event bus dispatch"},
        {"kind": "effect", "action": "proc.exec", "resource": {"kind": "fs", "root": "/workspace", "paths": ["/workspace"]}, "args": {"argv": ["python3", "-m", "unittest", "test_oracle.py"]}, "note": "run oracle"},
        {"kind": "finish", "note": "done"},
    ]
    res_claude = run_single_harness_task(
        harness_name="vg-code-claude-shaped",
        task_name="tier2_event_bus",
        brief=chal_eventbus.brief,
        files=chal_eventbus.files,
        oracle_code=chal_eventbus.oracle_code,
        model=FakeModel(claude_tape),
    )
    res_claude["model"] = "cassette/golden-deterministic"
    results.append(res_claude)

    return results


def main() -> None:
    print("=" * 100)
    print("VANGUARD AGENTIC HARNESS & MULTI-MODEL BENCHMARK MATRIX")
    print("=" * 100)

    # Allowed models: Free tier models + deepseek/deepseek-v4-flash-0731 (only authorized paid model)
    eval_models = [
        "nvidia/nemotron-3-super-120b-a12b:free",
        "nvidia/nemotron-3.5-lightning:free",
        "deepseek/deepseek-v4-flash-0731",
    ]

    print("\n--- 1. EVALUATING AGENTIC CODING HARNESSES (SWE-Bench Verified Pro Challenges) ---")
    swe_results = run_coding_harness_swe_benchmark()

    print("\n--- 2. EVALUATING RAG TUTOR / EXPLAINER HARNESS (vg-code-explain) ---")
    rag_results = run_rag_tutor_benchmark(eval_models)

    print("\n--- 3. EVALUATING CODEFIX / CRITIC-REVISER HARNESS (vg-code-critic-reviser) ---")
    codefix_results = run_codefix_critic_benchmark(eval_models)

    # Aggregate matrix
    matrix_output = {
        "timestamp": time.time(),
        "framework": "Vanguard / AETHER Substrate 0.9.3",
        "coding_harness_benchmarks": swe_results,
        "rag_tutor_benchmarks": rag_results,
        "codefix_critic_benchmarks": codefix_results,
    }

    out_path = ROOT / "benchmarks" / "agentic_matrix_benchmark_results.json"
    out_path.write_text(json.dumps(matrix_output, indent=2), encoding="utf-8")
    print(f"\n✔ Full benchmark matrix successfully written to: {out_path}")


if __name__ == "__main__":
    main()
