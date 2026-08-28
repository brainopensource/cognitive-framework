"""Scientific Experiment Runner and Matrix Comparator for 006_LLM_INT_MACHINE."""

from __future__ import annotations
import argparse
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Sequence

try:
    from .config import (
        HarnessConfig,
        CONFIG_BASELINE_REACT,
        CONFIG_VANGUARD_CORE,
        CONFIG_SOTA_FULL,
    )
    from .challenges import CHALLENGES, setup_challenge_workspace, evaluate_challenge_oracle
    from .engine import IntelligentMachineEngine, ExecutionReport
    from .llm_client import OpenRouterClient, MockLLMClient
except ImportError:
    from config import (
        HarnessConfig,
        CONFIG_BASELINE_REACT,
        CONFIG_VANGUARD_CORE,
        CONFIG_SOTA_FULL,
    )
    from challenges import CHALLENGES, setup_challenge_workspace, evaluate_challenge_oracle
    from engine import IntelligentMachineEngine, ExecutionReport
    from llm_client import OpenRouterClient, MockLLMClient


def run_single_experiment(
    challenge_id: str,
    config: HarnessConfig,
    model_override: str | None = None,
    client: OpenRouterClient | MockLLMClient | None = None,
) -> ExecutionReport:
    temp_dir = Path(tempfile.mkdtemp(prefix=f"int_machine_{challenge_id}_{config.config_name}_"))
    try:
        challenge = setup_challenge_workspace(challenge_id, temp_dir)
        
        active_config = config
        if model_override:
            active_config = HarnessConfig(
                config_name=config.config_name,
                use_l1_l5_prefix_stability=config.use_l1_l5_prefix_stability,
                use_ast_preflight=config.use_ast_preflight,
                use_reproduce_first=config.use_reproduce_first,
                use_speculative_rollback=config.use_speculative_rollback,
                use_dialogue_compaction=config.use_dialogue_compaction,
                use_dead_ends_tracking=config.use_dead_ends_tracking,
                use_paged_output=config.use_paged_output,
                model=model_override,
                max_turns=config.max_turns,
            )

        oracle = lambda d: evaluate_challenge_oracle(challenge_id, d)
        engine = IntelligentMachineEngine(
            workspace_dir=temp_dir,
            config=active_config,
            llm_client=client,
            oracle_fn=oracle,
        )

        report = engine.run(task_brief=challenge.brief, challenge_id=challenge_id)
        return report
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def run_experiment_matrix(
    challenge_id: str,
    configs: Sequence[HarnessConfig] | None = None,
    model: str = "openrouter/free",
    client: OpenRouterClient | MockLLMClient | None = None,
) -> list[ExecutionReport]:
    test_configs = configs or [CONFIG_BASELINE_REACT, CONFIG_VANGUARD_CORE, CONFIG_SOTA_FULL]
    reports: list[ExecutionReport] = []

    print(f"\n=================================================================")
    print(f"🚀 RUNNING EXPERIMENT MATRIX ON: {challenge_id} (Model: {model})")
    print(f"=================================================================\n")

    for cfg in test_configs:
        print(f"--> Testing Configuration: [{cfg.config_name}] ...")
        rep = run_single_experiment(challenge_id, cfg, model_override=model, client=client)
        reports.append(rep)
        status_emoji = "✅ PASS" if rep.success else "❌ FAIL"
        print(f"    Result: {status_emoji} | Turns: {rep.turns_taken} | Tokens: {rep.total_tokens:,} | Cost: ${rep.total_cost_usd:.5f} | Time: {rep.duration_seconds:.2f}s")
        if rep.ast_errors_prevented > 0:
            print(f"    AST Pre-Flight Errors Prevented: {rep.ast_errors_prevented}")
        if rep.error_message:
            print(f"    Note: {rep.error_message}")

    return reports


def render_markdown_comparison_table(reports: Sequence[ExecutionReport]) -> str:
    lines = [
        "### 📊 Scientific Experiment Matrix: Autonomous Coding Harness Comparison",
        "",
        "| Configuration | Solved | Turns | Total Tokens | Cached Tokens | Cost ($USD) | Latency (s) | AST Errors Caught | Diff Lines |",
        "|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|",
    ]
    for r in reports:
        status = "✅ YES" if r.success else "❌ NO"
        cached_pct = f"{(r.total_cached_tokens / max(1, r.total_tokens)) * 100:.1f}%" if r.total_cached_tokens > 0 else "0%"
        lines.append(
            f"| **{r.config_name}** | {status} | {r.turns_taken} | {r.total_tokens:,} | {cached_pct} | ${r.total_cost_usd:.5f} | {r.duration_seconds:.2f}s | {r.ast_errors_prevented} | {r.git_diff_lines} |"
        )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run 006_LLM_INT_MACHINE Experiment Matrix")
    parser.add_argument("--challenge", default="tier1_lru_cache", choices=list(CHALLENGES.keys()))
    parser.add_argument("--model", default="openrouter/free", help="Model name on OpenRouter")
    parser.add_argument("--mock", action="store_true", help="Use offline Mock LLM client for testing")
    args = parser.parse_args()

    client = MockLLMClient() if args.mock else OpenRouterClient()
    reports = run_experiment_matrix(args.challenge, model=args.model, client=client)
    
    print("\n" + render_markdown_comparison_table(reports) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
