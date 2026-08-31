"""SOTA health, coverage, and hygiene diagnostics for a repository index (`lda check`).

Produces a deterministic, structured report that agents and humans can trust as
a single command: profile resolution, knowledge-base validity, fact-graph
health, per-language coverage, orphan/stale facts, low-signal leakage, and
HEAD-binding freshness. `status` FAILS OPEN on degraded conditions with an
actionable `index_hint`, and never falsely reports HEALTHY.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import AtlasContext
from .profile import RepositoryProfile


def _check(checks: List[dict[str, Any]], check_id: str, status: str, message: str) -> None:
    checks.append({"id": check_id, "status": status, "message": message})


def run_healthcheck(
    ctx: AtlasContext,
    storage: Any,
    sample_limit: int = 300,
) -> Dict[str, Any]:
    """Run every diagnostic and return a structured health report."""
    checks: List[dict[str, Any]] = []
    recommendations: List[str] = []
    profile = ctx.profile

    # 1. Configuration & profile
    config_paths = [ctx.root / name for name in ("lda.yaml", "lda.yml", "lda.toml")]
    explicit = any(p.is_file() for p in config_paths)
    _check(checks, "config.profile", "ok" if explicit else "warn",
           f"active profile: {profile.name} (explicit={explicit})")
    if not explicit:
        recommendations.append(
            "No lda.yaml/lda.toml: using generic defaults. Create one to declare "
            "authority vocabulary, exclusions and code extensions.")

    # 2. Knowledge base (single emitter: read-only)
    catalog = ctx.knowledge / "catalog.jsonl"
    catalog_rows = 0
    kb_status = "missing"
    if catalog.is_file():
        try:
            catalog_rows = sum(1 for _ in catalog.open(encoding="utf-8"))
        except Exception:
            catalog_rows = 0
        report = ctx.knowledge / "report.json"
        if report.is_file():
            try:
                kb_status = json.loads(report.read_text(encoding="utf-8")).get("status", "UNKNOWN")
            except Exception:
                kb_status = "UNPARSEABLE"
        else:
            kb_status = "present"
    _check(checks, "knowledge.catalog", "ok" if catalog_rows > 0 else ("warn" if profile.name == "generic" else "error"),
           f"catalog rows: {catalog_rows} (status: {kb_status})")
    if catalog_rows == 0 and profile.name != "generic":
        recommendations.append(
            "catalog.jsonl is missing/empty: run the canonical generator "
            "(`just docs-knowledge` in AETHER) before trusting packets.")

    # 3. Fact-graph index
    stats = storage.get_stats()
    index_healthy = bool(stats.get("files", 0) > 0 and stats.get("documents", 0) > 0)
    _check(checks, "index.graph", "ok" if index_healthy else "error",
           f"files={stats.get('files', 0)} documents={stats.get('documents', 0)} "
           f"symbols={stats.get('symbols', 0)} relations={stats.get('relations', 0)}")
    if not index_healthy:
        recommendations.append(
            "Index is cold/empty: run `lda index` (or `lda index --rebuild`) "
            "before relying on lda_context/lda_symbol.")

    # 4. Coverage by language
    coverage = storage.coverage_by_language()
    langs = list(coverage.get("files", {}).keys())
    _check(checks, "index.coverage", "ok" if langs else "warn",
           f"languages: {', '.join(langs) if langs else 'none'}")

    # 5. Orphan FTS / stale facts
    orphans = storage.count_orphan_fts()
    _check(checks, "hygiene.orphan_fts", "ok" if orphans == 0 else "warn",
           f"orphan FTS rows: {orphans}")
    if orphans and orphans > 0:
        recommendations.append(
            "Orphan FTS rows detected: run `lda index --rebuild` to purge stale facts.")

    stale = 0
    for path in storage.sample_symbol_paths(limit=sample_limit):
        if not path:
            continue
        if not (ctx.root / path).exists():
            stale += 1
    _check(checks, "hygiene.stale_symbols", "ok" if stale == 0 else "warn",
           f"stale symbol file paths (of {sample_limit} sampled): {stale}")
    if stale:
        recommendations.append("Symbols reference deleted files: rebuild the index.")

    # 6. Low-signal leakage
    leakage = 0
    for path in storage.sample_symbol_paths(limit=sample_limit):
        if profile.is_low_signal(path):
            leakage += 1
    _check(checks, "hygiene.low_signal", "ok" if leakage == 0 else "warn",
           f"low-signal symbol paths (of {sample_limit} sampled): {leakage}")
    if leakage:
        recommendations.append(
            "low_signal_patterns match indexed symbols; rebuild cleans them from FTS.")

    # 7. HEAD binding
    head = ctx.head_sha
    latest_run = storage.latest_index_run()
    _check(checks, "freshness.head", "ok" if head else "warn",
           f"workspace HEAD: {head[:12] if head else 'not a git worktree'}")
    _check(checks, "freshness.index_run",
           "ok" if latest_run else "warn",
           f"latest index run: {latest_run.get('id', 'none') if latest_run else 'none'}")

    # 8. Budget / bounded growth invariant
    ceiling = int(getattr(profile, "max_global_symbols", 500))
    _check(checks, "budget.symbol_ceiling", "ok" if ceiling > 0 else "error",
           f"max_global_symbols={ceiling}")

    # 9. Knowledge health: consolidation + drift (warn-only; diagnostic value,
    #    never blocks a healthy index on editorial signals).
    try:
        from .consolidation import run_consolidation

        consolidation = run_consolidation(storage)
        n_dup = len(consolidation["duplicate_documents"])
        n_conf = len(consolidation["authority_conflicts"])
        _check(checks, "knowledge.consolidation",
               "ok" if n_dup == 0 and n_conf == 0 else "warn",
               consolidation["summary"])
        if n_dup:
            recommendations.append(
                "Duplicate document content detected: run `lda consolidate` and merge under one canonical owner.")
        if n_conf:
            recommendations.append(
                "Conflicting authority claims for the same topic: run `lda consolidate` to resolve.")
    except Exception as exc:  # pragma: no cover - diagnostics must not crash check
        _check(checks, "knowledge.consolidation", "warn", f"consolidation diagnostics unavailable: {exc}")

    try:
        from .drift import detect_drift

        drift = detect_drift(storage, ctx.root, sample_limit=min(sample_limit, 200))
        _check(checks, "knowledge.drift",
               "ok" if drift["status"] == "HEALTHY" else "warn",
               drift["summary"])
        if drift["status"] != "HEALTHY":
            recommendations.append(
                "Documentation drift detected: run `lda drift` for the stale-path / "
                "undocumented-symbol / orphan-document breakdown.")
    except Exception as exc:  # pragma: no cover
        _check(checks, "knowledge.drift", "warn", f"drift diagnostics unavailable: {exc}")

    status = "HEALTHY" if not any(c["status"] == "error" for c in checks) else "DEGRADED"
    return {
        "status": status,
        "profile": profile.name,
        "head_sha": head,
        "checks": checks,
        "coverage": coverage,
        "index_healthy": index_healthy,
        "recommendations": recommendations,
        "index_hint": (
            "index is populated" if index_healthy
            else "index is EMPTY or cold; run 'uv run lda index' — agents should "
            "verify .generated/knowledge/report.json status=VALIDATED first and "
            "fall back to tools/docs_rag_v0.py when unhealthy"
        ),
    }


__all__ = ["run_healthcheck"]