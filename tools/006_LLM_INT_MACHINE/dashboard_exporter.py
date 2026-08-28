"""Automated HTML/SVG Dashboard Visualizer for 006_LLM_INT_MACHINE.

Generates self-contained interactive dashboards rendering execution tables, token cost breakdowns,
and comparison charts from RunReceipts or ExecutionReports.
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Sequence


def export_html_dashboard(runs: Sequence[Any], output_file: Path | str = "benchmark_dashboard.html") -> Path:
    """Generate an interactive HTML/SVG report from a sequence of run receipts or execution reports."""
    target_path = Path(output_file).resolve()

    rows_html = []
    for r in runs:
        success = getattr(r, "success", False)
        status_color = "#4ade80" if success else "#f87171"
        status_text = "PASS" if success else "FAIL"
        
        cfg_name = getattr(r, "config_name", "unknown")
        ch_id = getattr(r, "challenge_id", "unknown")
        turns = getattr(r, "turns_taken", 0)
        tokens = getattr(r, "total_tokens", 0)
        cost = getattr(r, "total_cost_usd", 0.0)
        duration = getattr(r, "duration_seconds", 0.0)
        ast_err = getattr(r, "ast_errors_prevented", 0)
        mut_score = getattr(r, "mutation_score", 1.0)
        pareto = getattr(r, "pareto_score", 0.0)
        
        rows_html.append(
            f"<tr>"
            f"<td><b>{cfg_name}</b></td>"
            f"<td>{ch_id}</td>"
            f"<td style='color: {status_color}; font-weight: bold;'>{status_text}</td>"
            f"<td>{turns}</td>"
            f"<td>{tokens:,}</td>"
            f"<td>${cost:.5f}</td>"
            f"<td>{duration:.2f}s</td>"
            f"<td>{ast_err}</td>"
            f"<td>{mut_score:.2f}</td>"
            f"<td>{pareto:,.1f}</td>"
            f"</tr>"
        )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>006_LLM_INT_MACHINE Benchmark Dashboard</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #0f172a;
            color: #f8fafc;
            margin: 40px;
        }}
        .header {{
            border-bottom: 2px solid #334155;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        h1 {{ margin: 0; color: #38bdf8; }}
        p.subtitle {{ color: #94a3b8; margin-top: 5px; }}
        .card {{
            background: #1e293b;
            border-radius: 10px;
            padding: 25px;
            border: 1px solid #334155;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        th, td {{
            padding: 14px;
            text-align: left;
            border-bottom: 1px solid #334155;
        }}
        th {{
            background: #0f172a;
            color: #94a3b8;
            text-transform: uppercase;
            font-size: 0.8rem;
            letter-spacing: 0.05em;
        }}
        tr:hover {{
            background: #273549;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 006_LLM_INT_MACHINE Telemetry Dashboard</h1>
        <p class="subtitle">Scientific Benchmark, Multi-Model Matrix, and Parametric Ablation Analysis</p>
    </div>

    <div class="card">
        <h2>Executive KPI Matrix</h2>
        <table>
            <thead>
                <tr>
                    <th>Configuration</th>
                    <th>Challenge</th>
                    <th>Status</th>
                    <th>Turns</th>
                    <th>Total Tokens</th>
                    <th>Cost ($USD)</th>
                    <th>Duration</th>
                    <th>AST Errors Intercepted</th>
                    <th>Mutation Score</th>
                    <th>Pareto Score</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows_html)}
            </tbody>
        </table>
    </div>
</body>
</html>"""

    target_path.write_text(html, encoding="utf-8")
    return target_path
