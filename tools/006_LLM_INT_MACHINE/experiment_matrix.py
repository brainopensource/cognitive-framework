"""Scientific Parametric Experiment Runner, Multi-Trial Aggregator, and Matrix Comparator for 006_LLM_INT_MACHINE.

Supports:
- Centralized preset selection (--preset v1.0_baseline_react, v2.3_compound_full, etc.)
- Dynamic parameter overrides (--override "use_code_graph=True,use_sbfl_localization=True")
- Multi-run statistical aggregation (--repeats N) to eliminate stochastic LLM noise
- Automated HTML dashboard generation and historical run catalog comparison
"""

from __future__ import annotations
import argparse
import math
import sys
import tempfile
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

try:
    from .config import (
        HarnessConfig,
        CONFIG_V1_0_BASELINE,
        CONFIG_V1_1_VANGUARD_CORE,
        CONFIG_V1_2_SOTA_FULL,
        CONFIG_V2_0_SBFL_GRAPH,
        CONFIG_V2_1_MCTS_SPECULATIVE,
        CONFIG_V2_2_MUTATION_ROBUST,
        CONFIG_V2_3_COMPOUND_FULL,
        PRESET_REGISTRY,
        get_preset,
    )
    from .challenges import CHALLENGES, setup_challenge_workspace, evaluate_challenge_oracle
    from .engine import IntelligentMachineEngine, ExecutionReport
    from .llm_client import OpenRouterClient, OllamaClient, MockLLMClient
    from .catalog import RunCatalog, RunReceipt
    from .dashboard_exporter import export_html_dashboard
except ImportError:
    from config import (
        HarnessConfig,
        CONFIG_V1_0_BASELINE,
        CONFIG_V1_1_VANGUARD_CORE,
        CONFIG_V1_2_SOTA_FULL,
        CONFIG_V2_0_SBFL_GRAPH,
        CONFIG_V2_1_MCTS_SPECULATIVE,
        CONFIG_V2_2_MUTATION_ROBUST,
        CONFIG_V2_3_COMPOUND_FULL,
        PRESET_REGISTRY,
        get_preset,
    )
    from challenges import CHALLENGES, setup_challenge_workspace, evaluate_challenge_oracle
    from engine import IntelligentMachineEngine, ExecutionReport
    from llm_client import OpenRouterClient, OllamaClient, MockLLMClient
    from catalog import RunCatalog, RunReceipt
    from dashboard_exporter import export_html_dashboard


@dataclass
class AggregatedExperimentStats:
    """Statistical summary across N repeated experiment trials."""
    config_name: str
    challenge_id: str
    model: str
    trials: int
    pass_rate: float
    turns_mean: float
    turns_std: float
    tokens_mean: float
    tokens_std: float
    cost_mean: float
    cost_std: float
    duration_mean: float
    duration_std: float
    pareto_mean: float
    ast_errors_total: int
    reports: list[ExecutionReport]


def parse_override_string(override_str: str) -> dict[str, Any]:
    """Parse comma-separated key=value strings into typed dictionary."""
    overrides: dict[str, Any] = {}
    if not override_str.strip():
        return overrides
    
    for item in override_str.split(","):
        if "=" not in item:
            continue
        key, val = item.split("=", 1)
        key = key.strip()
        val = val.strip()
        
        # Type conversions
        if val.lower() in ("true", "1", "yes"):
            overrides[key] = True
        elif val.lower() in ("false", "0", "no"):
            overrides[key] = False
        elif val.isdigit():
            overrides[key] = int(val)
        else:
            try:
                overrides[key] = float(val)
            except ValueError:
                overrides[key] = val
                
    return overrides


def run_single_experiment(
    challenge_id: str,
    config: HarnessConfig,
    model_override: str | None = None,
    client: OpenRouterClient | MockLLMClient | None = None,
    catalog: RunCatalog | None = None,
) -> ExecutionReport:
    temp_dir = Path(tempfile.mkdtemp(prefix=f"int_machine_{challenge_id}_{config.config_name}_"))
    try:
        challenge = setup_challenge_workspace(challenge_id, temp_dir)
        
        active_config = config
        if model_override:
            active_config = config.derive(model=model_override)

        oracle = lambda d: evaluate_challenge_oracle(challenge_id, d)
        engine = IntelligentMachineEngine(
            workspace_dir=temp_dir,
            config=active_config,
            llm_client=client,
            oracle_fn=oracle,
            catalog=catalog,
        )

        report = engine.run(task_brief=challenge.brief, challenge_id=challenge_id)
        return report
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def run_multi_trial_experiment(
    challenge_id: str,
    config: HarnessConfig,
    model: str = "openrouter/free",
    repeats: int = 1,
    client: OpenRouterClient | MockLLMClient | None = None,
    catalog: RunCatalog | None = None,
) -> AggregatedExperimentStats:
    """Execute N independent trials of a configuration to compute mean and standard deviation."""
    reports: list[ExecutionReport] = []
    
    for i in range(1, repeats + 1):
        if repeats > 1:
            print(f"    [Trial {i}/{repeats}] ...")
        rep = run_single_experiment(challenge_id, config, model_override=model, client=client, catalog=catalog)
        reports.append(rep)

    n = len(reports)
    passes = sum(1 for r in reports if r.success)
    pass_rate = passes / n

    turns = [r.turns_taken for r in reports]
    tokens = [r.total_tokens for r in reports]
    costs = [r.total_cost_usd for r in reports]
    durations = [r.duration_seconds for r in reports]
    paretos = [r.pareto_score for r in reports]
    ast_errs = sum(r.ast_errors_prevented for r in reports)

    def calc_mean_std(data: list[float]) -> tuple[float, float]:
        m = sum(data) / len(data)
        var = sum((x - m) ** 2 for x in data) / max(1, len(data) - 1)
        return m, math.sqrt(var)

    t_mean, t_std = calc_mean_std(turns)
    tok_mean, tok_std = calc_mean_std(tokens)
    c_mean, c_std = calc_mean_std(costs)
    d_mean, d_std = calc_mean_std(durations)
    p_mean, _ = calc_mean_std(paretos)

    return AggregatedExperimentStats(
        config_name=config.config_name,
        challenge_id=challenge_id,
        model=model,
        trials=n,
        pass_rate=pass_rate,
        turns_mean=round(t_mean, 2),
        turns_std=round(t_std, 2),
        tokens_mean=round(tok_mean, 1),
        tokens_std=round(tok_std, 1),
        cost_mean=round(c_mean, 6),
        cost_std=round(c_std, 6),
        duration_mean=round(d_mean, 2),
        duration_std=round(d_std, 2),
        pareto_mean=round(p_mean, 1),
        ast_errors_total=ast_errs,
        reports=reports,
    )


def run_experiment_matrix(
    challenge_id: str,
    configs: Sequence[HarnessConfig] | None = None,
    model: str = "openrouter/free",
    repeats: int = 1,
    client: OpenRouterClient | MockLLMClient | None = None,
    catalog: RunCatalog | None = None,
) -> list[AggregatedExperimentStats]:
    test_configs = configs or [
        CONFIG_V1_0_BASELINE,
        CONFIG_V1_1_VANGUARD_CORE,
        CONFIG_V1_2_SOTA_FULL,
        CONFIG_V2_0_SBFL_GRAPH,
        CONFIG_V2_3_COMPOUND_FULL,
    ]
    aggregated_results: list[AggregatedExperimentStats] = []
    all_reports: list[ExecutionReport] = []

    print(f"\n=========================================================================================")
    print(f"🚀 SCIENTIFIC EXPERIMENT MATRIX: {challenge_id} | Model: {model} | Repeats: {repeats}")
    print(f"=========================================================================================\n")

    for cfg in test_configs:
        print(f"--> Testing Configuration: [{cfg.config_name}] (Hash: {cfg.config_hash()}) ...")
        agg = run_multi_trial_experiment(challenge_id, cfg, model=model, repeats=repeats, client=client, catalog=catalog)
        aggregated_results.append(agg)
        all_reports.extend(agg.reports)
        
        status_emoji = "✅ PASS" if agg.pass_rate == 1.0 else (f"🟡 {agg.pass_rate*100:.0f}%" if agg.pass_rate > 0 else "❌ FAIL")
        print(
            f"    Result: {status_emoji} | Turns: {agg.turns_mean}±{agg.turns_std} | "
            f"Tokens: {agg.tokens_mean:,.0f}±{agg.tokens_std:,.0f} | "
            f"Cost: ${agg.cost_mean:.5f} | Time: {agg.duration_mean}s±{agg.duration_std}s | "
            f"AST Errors Caught: {agg.ast_errors_total}"
        )

    # Auto-export HTML dashboard
    export_html_dashboard(all_reports, "benchmark_dashboard.html")
    return aggregated_results


def render_aggregated_markdown_table(stats_list: Sequence[AggregatedExperimentStats]) -> str:
    lines = [
        "### 📊 Scientific Experiment Matrix: Parametric Ablation & Statistical Noise Reduction",
        "",
        "| Configuration | Trials | Pass Rate | Turns (μ±σ) | Tokens (μ±σ) | Cost ($USD) | Latency (s) | AST Intercepts | Pareto Score |",
        "|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|",
    ]
    for s in stats_list:
        pass_str = f"✅ {s.pass_rate*100:.0f}%" if s.pass_rate == 1.0 else (f"🟡 {s.pass_rate*100:.0f}%" if s.pass_rate > 0 else "❌ 0%")
        lines.append(
            f"| **{s.config_name}** | {s.trials} | {pass_str} | {s.turns_mean} ± {s.turns_std} | "
            f"{s.tokens_mean:,.0f} ± {s.tokens_std:,.0f} | ${s.cost_mean:.5f} | "
            f"{s.duration_mean:.2f}s ± {s.duration_std:.2f}s | {s.ast_errors_total} | {s.pareto_mean:,.1f} |"
        )
    return "\n".join(lines)


def compare_historical_runs(catalog: RunCatalog, challenge_id: str | None = None) -> str:
    runs = catalog.list_runs(challenge_id=challenge_id, limit=20)
    if not runs:
        return "No historical runs found in catalog."
    
    lines = [
        "### 📜 Historical Experiment Catalog Runs",
        "",
        "| Run ID | Timestamp | Challenge | Config | Model | Solved | Turns | Tokens | Cost ($USD) | Time (s) |",
        "|---|---|---|---|---|:---:|:---:|:---:|:---:|:---:|",
    ]
    for r in runs:
        solved_str = "✅ YES" if r.success else "❌ NO"
        lines.append(
            f"| `{r.run_id[:22]}...` | {r.timestamp_utc[11:19]} | {r.challenge_id} | {r.config_name} | "
            f"{r.model.split('/')[-1]} | {solved_str} | {r.turns_taken} | {r.total_tokens:,} | "
            f"${r.total_cost_usd:.5f} | {r.duration_seconds:.2f}s |"
        )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="006_LLM_INT_MACHINE Parametric Experimentation Runner")
    parser.add_argument("--challenge", default="tier1_lru_cache", choices=list(CHALLENGES.keys()))
    parser.add_argument("--preset", default=None, help="Preset configuration name (e.g. v1.0_baseline_react, v2.3_compound_full)")
    parser.add_argument("--override", default="", help="Comma-separated parameter overrides (e.g. 'use_code_graph=True,max_turns=10')")
    parser.add_argument("--model", default="openrouter/free", help="Model name on OpenRouter or Ollama")
    parser.add_argument("--repeats", type=int, default=1, help="Number of repeated trials for statistical variance reduction")
    parser.add_argument("--mock", action="store_true", help="Use offline Mock LLM client")
    parser.add_argument("--ollama", action="store_true", help="Use local Ollama instance on Windows/WSL2 (http://localhost:11434)")
    parser.add_argument("--history", action="store_true", help="Display historical run catalog table")
    args = parser.parse_args()

    catalog = RunCatalog()

    if args.history:
        print("\n" + compare_historical_runs(catalog, challenge_id=args.challenge) + "\n")
        return 0

    if args.mock:
        client = MockLLMClient()
    elif args.ollama or any(m in args.model for m in ("qwen", "deepseek-coder", "codestral", "llama3.2", "granite")):
        client = OllamaClient()
    else:
        client = OpenRouterClient()

    if args.preset:
        base_cfg = get_preset(args.preset)
        overrides = parse_override_string(args.override)
        active_cfg = base_cfg.derive(**overrides)
        stats = run_multi_trial_experiment(args.challenge, active_cfg, model=args.model, repeats=args.repeats, client=client, catalog=catalog)
        print("\n" + render_aggregated_markdown_table([stats]) + "\n")
    else:
        stats_list = run_experiment_matrix(args.challenge, model=args.model, repeats=args.repeats, client=client, catalog=catalog)
        print("\n" + render_aggregated_markdown_table(stats_list) + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
