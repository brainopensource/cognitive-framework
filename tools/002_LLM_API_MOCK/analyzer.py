"""Harness Pipeline Analyzer & Pareto Cost-Efficiency Engine."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List

from store import DEFAULT_DB_PATH, LamStore


class HarnessAnalyzer:
    def __init__(self, db_path: Path | str = DEFAULT_DB_PATH) -> None:
        self.store = LamStore(db_path)

    def generate_kpi_summary(self) -> Dict[str, Any]:
        kpis = self.store.get_summary_kpis()
        with self.store._get_connection() as conn:
            # Query downgrade performance
            cur = conn.execute("""
                SELECT model, model_tier, scenario_tier, COUNT(*) as attempts, SUM(passed) as passes,
                       AVG(prompt_tokens + completion_tokens) as avg_tokens, AVG(wall_s) as avg_latency
                FROM traces
                WHERE is_downgrade = 1
                GROUP BY model, model_tier, scenario_tier;
            """)
            downgrades = [dict(r) for r in cur.fetchall()]

            # Query cost per tier
            cur = conn.execute("""
                SELECT scenario_tier, COUNT(*) as trace_count, SUM(passed) as pass_count,
                       SUM(usd) as total_usd, AVG(prompt_tokens + completion_tokens) as avg_tokens
                FROM traces
                GROUP BY scenario_tier;
            """)
            tier_costs = [dict(r) for r in cur.fetchall()]

        return {
            "summary": kpis,
            "tier_downgrade_matrix": downgrades,
            "tier_cost_distribution": tier_costs,
        }

    def render_markdown_report(self) -> str:
        report = self.generate_kpi_summary()
        s = report["summary"]

        md = []
        md.append("# Harness Pipeline Optimization & Pareto Cost Report")
        md.append(f"**Total Scenarios:** {s['total_scenarios']} | **Total Traces:** {s['total_traces']}")
        md.append(f"**Total LLM Calls:** {s['total_calls']} | **Total Tokens:** {s['total_tokens']:,}")
        md.append(f"**Total Direct Spend:** ${s['total_usd']:.4f} USD | **Avg Wall Latency:** {s['avg_wall_s']}s")
        md.append(f"**Tier-Downgrade Pass Rate:** {s['downgrade_pass_rate'] * 100:.1f}%\n")

        md.append("## 1. Model Tier Ceilings")
        md.append("| Model | Band | Ceiling Tier | Evidence Trace ID |")
        md.append("| :--- | :--- | :--- | :--- |")
        for c in s["model_ceilings"]:
            md.append(f"| `{c['model']}` | {c['band']} | Tier {c['ceiling_tier']} | Trace #{c['evidence_trace_id']} |")

        md.append("\n## 2. Tier Cost & Token Efficiency")
        md.append("| Scenario Tier | Traces Evaluated | Pass Count | Total USD | Avg Tokens / Task |")
        md.append("| :--- | :--- | :--- | :--- | :--- |")
        for tc in report["tier_cost_distribution"]:
            md.append(
                f"| Tier {tc['scenario_tier']} | {tc['trace_count']} | {tc['pass_count']} | ${tc['total_usd']:.4f} | {int(tc['avg_tokens'] or 0):,} tok |"
            )

        return "\n".join(md)
