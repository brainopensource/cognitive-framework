"""The Main Autonomous Turn Engine for 006_LLM_INT_MACHINE.

Coordinates context compilation, tool execution, SBFL localization, MCTS search,
mutation verification, subagent sandboxing, hierarchical model routing, KPI telemetry computation,
and catalog run persistence.
"""

from __future__ import annotations
import json
import re
import time
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Sequence

try:
    from .config import HarnessConfig
    from .context_engine import ContextEngine
    from .llm_client import OpenRouterClient, MockLLMClient, LLMResponse
    from .reproducer_protocol import ReproducerManager
    from .tools import ToolWorkspace, TOOL_DEFINITIONS, ToolExecutionResult
    from .fault_localizer import SBFLEngine
    from .mcts_search import SpeculativeMCTSSearch
    from .mutation_verifier import PatchMutationVerifier
    from .subagent_orchestrator import SubagentCoordinator, SubagentReport
    from .hierarchical_router import HierarchicalModelRouter
    from .telemetry_kpi import AdvancedKPITelemetry
    from .catalog import RunCatalog, RunReceipt, generate_run_id
except ImportError:
    from config import HarnessConfig
    from context_engine import ContextEngine
    from llm_client import OpenRouterClient, MockLLMClient, LLMResponse
    from reproducer_protocol import ReproducerManager
    from tools import ToolWorkspace, TOOL_DEFINITIONS, ToolExecutionResult
    from fault_localizer import SBFLEngine
    from mcts_search import SpeculativeMCTSSearch
    from mutation_verifier import PatchMutationVerifier
    from subagent_orchestrator import SubagentCoordinator, SubagentReport
    from hierarchical_router import HierarchicalModelRouter
    from telemetry_kpi import AdvancedKPITelemetry
    from catalog import RunCatalog, RunReceipt, generate_run_id


@dataclass
class ExecutionReport:
    config_name: str
    challenge_id: str
    success: bool
    turns_taken: int = 0
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    total_cached_tokens: int = 0
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    duration_seconds: float = 0.0
    ast_errors_prevented: int = 0
    speculative_rollbacks: int = 0
    reproducer_created: bool = False
    git_diff_lines: int = 0
    mutation_score: float = 1.0
    pareto_score: float = 0.0
    run_id: str = ""
    receipt_path: str = ""
    error_message: str = ""
    kpi_metrics: dict[str, Any] = field(default_factory=dict)
    turns_detail: list[dict[str, Any]] = field(default_factory=list)
    subagent_reports: list[dict[str, Any]] = field(default_factory=list)


DEFAULT_SYSTEM_PROMPT = """You are an expert autonomous software engineer solving a code defect.
Follow this methodology:
1. Examine the codebase structure and locate the issue using `fs_search`, `fs_read`, or `code_find_definitions`.
2. Formulate a precise hypothesis of why the bug occurs.
3. If writing tests, create a standalone script reproducing the failure.
4. Apply minimal surgical fixes with `patch_apply`.
5. Run the test suite via `proc_exec` to confirm the fix passes with zero regressions.
6. When done, output a final message stating task complete.
"""


class IntelligentMachineEngine:
    def __init__(
        self,
        workspace_dir: Path | str,
        config: HarnessConfig,
        llm_client: OpenRouterClient | MockLLMClient | None = None,
        oracle_fn: Callable[[Path], bool] | None = None,
        catalog: RunCatalog | None = None,
    ) -> None:
        self.workspace_dir = Path(workspace_dir).resolve()
        self.config = config
        self.client = llm_client or OpenRouterClient()
        self.oracle_fn = oracle_fn
        self.catalog = catalog or RunCatalog()
        self.workspace = ToolWorkspace(self.workspace_dir, config)
        self.reproducer = ReproducerManager(self.workspace, enabled=config.use_reproduce_first)
        self.sbfl = SBFLEngine(self.workspace_dir)
        self.mutation_verifier = PatchMutationVerifier(
            self.workspace_dir,
            lambda: self.oracle_fn(self.workspace_dir) if self.oracle_fn else True
        )
        self.mcts = SpeculativeMCTSSearch(
            self.workspace,
            branching_factor=config.mcts_branching_factor,
            c_puct=config.mcts_exploration_c
        )
        self.subagent_coordinator = SubagentCoordinator(self.config, self.client)
        self.router = HierarchicalModelRouter(planner_model=config.model, worker_model=config.model)

    def _extract_fallback_tool_calls(self, content: str) -> list[dict[str, Any]]:
        calls: list[dict[str, Any]] = []
        if not content:
            return calls
        
        blocks = re.findall(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL)
        for block in blocks:
            try:
                data = json.loads(block)
                name = data.get("name") or data.get("tool") or data.get("action")
                args = data.get("arguments") or data.get("parameters") or data.get("args") or data
                if name:
                    calls.append({
                        "function": {
                            "name": name,
                            "arguments": json.dumps(args) if isinstance(args, dict) else str(args)
                        }
                    })
            except Exception:
                continue
        return calls

    def run(self, task_brief: str, challenge_id: str = "custom_task") -> ExecutionReport:
        start_time = time.perf_counter()
        run_id = generate_run_id(challenge_id, self.config.config_name, self.config.model)
        
        # If SBFL is enabled, execute pre-flight fault localization
        sbfl_notes = ""
        if self.config.use_sbfl_localization and self.oracle_fn:
            try:
                failed_run, failing_trace = self.sbfl.record_execution(lambda: not self.oracle_fn(self.workspace_dir))
                if failing_trace:
                    rankings = self.sbfl.compute_rankings([failing_trace], [])
                    sbfl_notes = "\n" + self.sbfl.format_for_prompt(rankings, top_k=5)
            except Exception:
                pass

        enhanced_brief = task_brief + sbfl_notes
        context = ContextEngine(self.config, DEFAULT_SYSTEM_PROMPT, enhanced_brief)
        
        report = ExecutionReport(
            config_name=self.config.config_name,
            challenge_id=challenge_id,
            success=False,
            run_id=run_id,
        )

        if self.config.use_speculative_rollback:
            self.workspace.git_checkpoint("initial_clean_state")

        useful_tokens = 0
        total_patch_attempts = 0
        subprocess_time = 0.0

        for turn_idx in range(1, self.config.max_turns + 1):
            report.turns_taken = turn_idx
            
            if report.total_cost_usd >= self.config.max_cost_usd:
                report.error_message = f"Budget limit (${self.config.max_cost_usd}) reached."
                break
            if turn_idx >= self.config.max_api_calls:
                report.error_message = "Max API calls reached."
                break

            # Select routing model for this turn
            phase = "LOCALIZATION" if turn_idx == 1 else "EXECUTION"
            decision = self.router.select_model_for_turn(turn_idx, phase)
            active_tools = context.get_filtered_tools(phase=phase if turn_idx == 1 else "ALL")

            messages = context.compile_messages()
            
            try:
                resp: LLMResponse = self.client.complete(
                    messages=messages,
                    tools=active_tools,
                    model=decision.selected_model,
                    temperature=decision.temperature,
                )
            except Exception as e:
                report.error_message = f"LLM API Error on turn {turn_idx}: {str(e)}"
                break

            report.total_prompt_tokens += resp.usage.prompt_tokens
            report.total_completion_tokens += resp.usage.completion_tokens
            report.total_cached_tokens += resp.usage.cached_tokens
            report.total_tokens += resp.usage.total_tokens
            report.total_cost_usd += resp.usage.cost_usd

            tool_calls = list(resp.tool_calls)
            if not tool_calls and resp.content:
                fallback_calls = self._extract_fallback_tool_calls(resp.content)
                if fallback_calls:
                    tool_calls = fallback_calls

            turn_info = {
                "turn": turn_idx,
                "model": decision.selected_model,
                "phase": decision.phase,
                "content": resp.content[:200] if resp.content else "",
                "tool_calls": len(tool_calls),
                "tokens": resp.usage.total_tokens,
            }
            report.turns_detail.append(turn_info)

            if resp.content:
                context.add_turn_assistant(resp.content)

            # If no tool calls, check oracle
            if not tool_calls:
                if self.oracle_fn and self.oracle_fn(self.workspace_dir):
                    report.success = True
                    self.router.record_turn_outcome(True)
                    break
                elif "complete" in resp.content.lower() or "fixed" in resp.content.lower() or turn_idx > 3:
                    if self.oracle_fn and self.oracle_fn(self.workspace_dir):
                        report.success = True
                        self.router.record_turn_outcome(True)
                        break

            # Execute tool calls
            for tc in tool_calls:
                fn = tc.get("function", {})
                name = fn.get("name", "")
                raw_args = fn.get("arguments", "{}")
                try:
                    args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
                except Exception:
                    args = {}

                if name == "patch_apply":
                    total_patch_attempts += 1

                t_exec_start = time.perf_counter()
                tool_res = self._dispatch_tool(name, args)
                if name == "proc_exec":
                    subprocess_time += (time.perf_counter() - t_exec_start)
                
                if tool_res.ok:
                    useful_tokens += resp.usage.total_tokens // max(1, len(tool_calls))
                if tool_res.is_ast_error:
                    report.ast_errors_prevented += 1

                context.add_tool_receipt(name, tool_res.output, is_large=(tool_res.bytes_produced > 1000))

            if self.oracle_fn and self.oracle_fn(self.workspace_dir):
                report.success = True
                self.router.record_turn_outcome(True)
                break
            else:
                self.router.record_turn_outcome(False)

        # Check if oracle passed at the end
        if self.oracle_fn and self.oracle_fn(self.workspace_dir):
            report.success = True

        report.duration_seconds = time.perf_counter() - start_time
        report.ast_errors_prevented = self.workspace.ast_errors_caught
        report.reproducer_created = self.reproducer.state.repro_file_created
        report.git_diff_lines = self._get_git_diff_lines()

        # Collect subagent reports
        report.subagent_reports = [
            {"id": s.subagent_id, "role": s.role, "summary": s.summary, "tokens": s.tokens_consumed}
            for s in self.subagent_coordinator.execution_history
        ]

        # If mutation testing is enabled and run succeeded, compute mutation score
        if self.config.use_mutation_testing and report.success:
            try:
                diff_files = self._get_modified_files()
                for df in diff_files:
                    m_res = self.mutation_verifier.falsify_patch(df)
                    report.mutation_score = m_res.mutation_score
            except Exception:
                pass

        # Calculate 15 derived KPIs
        kpi = AdvancedKPITelemetry(
            turns_taken=report.turns_taken,
            total_tokens=report.total_tokens,
            cached_tokens=report.total_cached_tokens,
            total_cost_usd=report.total_cost_usd,
            duration_seconds=report.duration_seconds,
            git_diff_lines=report.git_diff_lines,
            ast_errors_prevented=report.ast_errors_prevented,
            pmsi_mutation_score=report.mutation_score,
        )
        kpi.calculate_derived_metrics(
            useful_tokens=useful_tokens,
            total_patch_attempts=max(1, total_patch_attempts),
            solved=report.success,
            subprocess_time_sec=subprocess_time,
        )
        report.kpi_metrics = kpi.to_dict()
        report.pareto_score = kpi.mps_model_pareto_score

        # Auto-persist execution receipt into Catalog
        try:
            receipt = RunReceipt(
                run_id=run_id,
                timestamp_utc=datetime.now(timezone.utc).isoformat(),
                challenge_id=challenge_id,
                config_name=self.config.config_name,
                version_tag=self.config.version_tag,
                config_hash=self.config.config_hash(),
                model=self.config.model,
                seed=self.config.seed,
                success=report.success,
                turns_taken=report.turns_taken,
                total_tokens=report.total_tokens,
                cached_tokens=report.total_cached_tokens,
                total_cost_usd=report.total_cost_usd,
                duration_seconds=report.duration_seconds,
                git_diff_lines=report.git_diff_lines,
                ast_errors_prevented=report.ast_errors_prevented,
                mutation_score=report.mutation_score,
                pareto_score=report.pareto_score,
                config_snapshot=self.config.to_dict(),
                kpi_metrics=report.kpi_metrics,
                turn_events=report.turns_detail,
                error_message=report.error_message,
            )
            saved_p = self.catalog.save_run(receipt)
            report.receipt_path = str(saved_p)
        except Exception:
            pass

        return report

    def _dispatch_tool(self, name: str, args: dict[str, Any]) -> ToolExecutionResult:
        if name == "fs_read":
            return self.workspace.fs_read(
                path=args.get("path", ""),
                start_line=args.get("start_line", 1),
                line_count=args.get("line_count", 100),
            )
        elif name == "fs_search":
            return self.workspace.fs_search(
                pattern=args.get("pattern", ""),
                path=args.get("path", "."),
            )
        elif name == "fs_list":
            return self.workspace.fs_list(path=args.get("path", "."))
        elif name == "code_find_definitions":
            return self.workspace.code_find_definitions(symbol_name=args.get("symbol_name", ""))
        elif name == "code_find_callers":
            return self.workspace.code_find_callers(symbol_name=args.get("symbol_name", ""))
        elif name == "code_repo_skeleton":
            return self.workspace.code_repo_skeleton()
        elif name == "patch_apply":
            return self.workspace.patch_apply(
                path=args.get("path", ""),
                target_chunk=args.get("target_chunk", ""),
                replacement_chunk=args.get("replacement_chunk", ""),
            )
        elif name == "proc_exec":
            return self.workspace.proc_exec(
                command=args.get("command", ""),
            )
        else:
            return ToolExecutionResult(ok=False, output=f"Unknown tool: '{name}'")

    def _get_git_diff_lines(self) -> int:
        try:
            res = subprocess.run(
                ["git", "diff"],
                cwd=str(self.workspace_dir),
                capture_output=True,
                text=True,
                check=False,
            )
            return len(res.stdout.splitlines())
        except Exception:
            return 0

    def _get_modified_files(self) -> list[str]:
        try:
            res = subprocess.run(
                ["git", "diff", "--name-only"],
                cwd=str(self.workspace_dir),
                capture_output=True,
                text=True,
                check=False,
            )
            return [f.strip() for f in res.stdout.splitlines() if f.strip().endswith(".py")]
        except Exception:
            return []
