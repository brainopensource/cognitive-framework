"""Deterministic retrieval benchmark harness for LDA (``lda bench``).

Builds a fixture repository, runs the golden query set through each ranking
strategy, and reports recall@k, MRR, and latency. Pure stdlib, fully
deterministic — used as a regression gate for retrieval quality.
"""
from __future__ import annotations

import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

STRATEGIES = ("fts5_bm25", "ppr_submodular", "hybrid_rrf")


def build_fixture_repo(root: Path) -> None:
    """Deterministic fixture repo with known ground truth per query."""
    def w(rel: str, content: str) -> None:
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")

    w("docs/spec.md", (
        "# Spec\n\n## Budget Algebra\n\nBudgets are typed, monotonic, and "
        "attenuated across spawn boundaries. Violations fail closed.\n"
    ))
    w("docs/compaction.md", (
        "# Compaction\n\nStructured compaction preserves obligations and "
        "evidence while dropping low-signal turns.\n"
    ))
    w("docs/bakery.md", (
        "# Bakery\n\nSourdough fermentation schedules and hydration ratios "
        "for home ovens.\n"
    ))
    w("src/kernel/budget.py", (
        "class BudgetGovernor:\n"
        '    """Typed monotonic budget algebra for child agents."""\n'
        "    def commit(self, delta: int) -> bool:\n"
        "        ...\n"
    ))
    w("src/kernel/spawn.py", (
        "def spawn_child():\n"
        '    """Spawn an attenuated child agent with reduced budgets."""\n'
        "    ...\n"
    ))
    w("test/kernel/test_budget.py", (
        "def test_budget_commit_fails_closed():\n"
        "    ...\n"
    ))


def golden_queries() -> List[Dict[str, Any]]:
    """Query -> expected locator substrings (any-of counts as a hit)."""
    return [
        {"query": "budget algebra attenuation spawn", "expect": ["budget", "spawn"], "intent": "bugfix"},
        {"query": "structured compaction obligations evidence", "expect": ["compaction"], "intent": "explain"},
        {"query": "sourdough hydration fermentation", "expect": ["bakery"], "intent": "research"},
        {"query": 'fix crash: File "src/kernel/budget.py", line 3', "expect": ["budget"], "intent": "bugfix"},
    ]


def _mrr(ranked_locators: List[str], expect: List[str]) -> float:
    for i, locator in enumerate(ranked_locators, start=1):
        if any(e in locator for e in expect):
            return 1.0 / i
    return 0.0


def _recall(ranked_locators: List[str], expect: List[str], k: int) -> float:
    top = ranked_locators[:k]
    hits = sum(1 for e in expect if any(e in loc for loc in top))
    return hits / max(len(expect), 1)


def run_bench(budget: int = 2000, k: int = 5) -> Dict[str, Any]:
    """Benchmark all strategies on the fixture repo."""
    from ..atlas import compile_task_context, get_storage, index_repository

    with tempfile.TemporaryDirectory(prefix="lda-bench-") as tmp:
        root = Path(tmp)
        build_fixture_repo(root)
        index_repository(root, rebuild=True)
        storage = get_storage(root)

        results: Dict[str, Any] = {}
        for strategy in STRATEGIES:
            per_query: List[Dict[str, Any]] = []
            recalls: List[float] = []
            mrrs: List[float] = []
            latencies: List[float] = []
            for g in golden_queries():
                start = time.perf_counter()
                packet = compile_task_context(root, g["query"], budget=budget, strategy=strategy)
                elapsed_ms = (time.perf_counter() - start) * 1000.0
                ranked = [c.locator for c in packet.documents + packet.symbols]
                recalls.append(_recall(ranked, g["expect"], k))
                mrrs.append(_mrr(ranked, g["expect"]))
                latencies.append(elapsed_ms)
                per_query.append({
                    "query": g["query"],
                    "recall@k": _recall(ranked, g["expect"], k),
                    "mrr": _mrr(ranked, g["expect"]),
                    "latency_ms": round(elapsed_ms, 2),
                })
            results[strategy] = {
                f"recall@{k}": round(sum(recalls) / len(recalls), 4),
                "mrr": round(sum(mrrs) / len(mrrs), 4),
                "mean_latency_ms": round(sum(latencies) / len(latencies), 2),
                "queries": per_query,
            }
        results["fixture"] = "deterministic 6-file repo (docs + kernel + tests)"
        results["k"] = k
        results["budget"] = budget
        return results


__all__ = ["STRATEGIES", "golden_queries", "run_bench"]
