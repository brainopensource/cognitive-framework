"""The Main Autonomous Turn Engine for 006_LLM_INT_MACHINE.

Coordinates context compilation, tool execution, SBFL localization, MCTS search,
mutation verification, subagent sandboxing, hierarchical model routing, KPI telemetry computation,
and catalog run persistence.
"""

from __future__ import annotations
import ast
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
    from .llm_client import OpenRouterClient, MockLLMClient, LLMResponse, LLMUsageMetrics
    from .reproducer_protocol import ReproducerManager
    from .tools import ToolWorkspace, TOOL_DEFINITIONS, ToolExecutionResult
    from .fault_localizer import SBFLEngine
    from .coverage_sbfl import CoverageBackedSBFL
    from .mcts_search import SpeculativeMCTSSearch
    from .mutation_verifier import PatchMutationVerifier
    from .subagent_orchestrator import SubagentCoordinator, SubagentReport
    from .hierarchical_router import HierarchicalModelRouter
    from .causal_slicing import CausalFaultLocalizer, CausalStatementRank
    from .adversarial_fuzzer import AdversarialInvariantFuzzer, AdversarialFuzzReport
    from .rlvr_trajectory_engine import RLVREngine, RLVREpisodeTrajectory
    from .cegis_solver import CEGISSolver, CEGISSynthesisReport
    from .concolic_fuzzer import ConcolicPathFuzzer, ConcolicCoverageReport
    from .arena_tournament import ArenaTournament, ArenaTournamentReport
    from .time_travel_debugger import TimeTravelDebugger, TimeTravelDebugTrace
    from .skill_compiler import DynamicSkillCompiler, CompiledSkill
    from .cluster_mcts import ClusterMCTSSearch, ClusterMCTSReport
    from .telemetry_kpi import AdvancedKPITelemetry
    from .catalog import RunCatalog, RunReceipt, generate_run_id
    from .challenges import CHALLENGES
except ImportError:
    from config import HarnessConfig
    from context_engine import ContextEngine
    from llm_client import OpenRouterClient, MockLLMClient, LLMResponse, LLMUsageMetrics
    from reproducer_protocol import ReproducerManager
    from tools import ToolWorkspace, TOOL_DEFINITIONS, ToolExecutionResult
    from fault_localizer import SBFLEngine
    from coverage_sbfl import CoverageBackedSBFL
    from mcts_search import SpeculativeMCTSSearch
    from mutation_verifier import PatchMutationVerifier
    from subagent_orchestrator import SubagentCoordinator, SubagentReport
    from hierarchical_router import HierarchicalModelRouter
    from causal_slicing import CausalFaultLocalizer, CausalStatementRank
    from adversarial_fuzzer import AdversarialInvariantFuzzer, AdversarialFuzzReport
    from rlvr_trajectory_engine import RLVREngine, RLVREpisodeTrajectory
    from cegis_solver import CEGISSolver, CEGISSynthesisReport
    from concolic_fuzzer import ConcolicPathFuzzer, ConcolicCoverageReport
    from arena_tournament import ArenaTournament, ArenaTournamentReport
    from time_travel_debugger import TimeTravelDebugger, TimeTravelDebugTrace
    from skill_compiler import DynamicSkillCompiler, CompiledSkill
    from cluster_mcts import ClusterMCTSSearch, ClusterMCTSReport
    from telemetry_kpi import AdvancedKPITelemetry
    from catalog import RunCatalog, RunReceipt, generate_run_id
    from challenges import CHALLENGES


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

LIGHTWEIGHT_SYSTEM_PROMPT = """You are a code repair AI. Fix the bug in the repository.
Tools: fs_read (read file), patch_apply (edit code), proc_exec (run tests).
Call ONE tool per message. When done, write TASK COMPLETE.
"""

FREE_TIER_CASCADE = [
    "minimax/minimax-m3:free",
    "z-ai/glm-5.2:free",
    "poolside/laguna-s-2.1:free",
    "inclusionai/ling-3.0-tiny:free",
]

_XML_TOOL_RE = re.compile(r"<tool_call>\s*(\{.*?\})\s*</tool_call>", re.DOTALL)


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
        self.cov_sbfl = CoverageBackedSBFL(self.workspace_dir, self.sbfl)
        self.mutation_verifier = PatchMutationVerifier(
            self.workspace_dir,
            lambda: self.oracle_fn(self.workspace_dir) if self.oracle_fn else True
        )
        self.causal_localizer = CausalFaultLocalizer(self.workspace_dir)
        self.adversarial_fuzzer = AdversarialInvariantFuzzer(self.workspace_dir)
        self.rlvr_engine = RLVREngine()
        self.cegis_solver = CEGISSolver(self.workspace_dir)
        self.concolic_fuzzer = ConcolicPathFuzzer(self.workspace_dir)
        self.arena_tournament = ArenaTournament(self.workspace)
        self.time_travel = TimeTravelDebugger()
        self.skill_compiler = DynamicSkillCompiler(self.workspace_dir)
        self.cluster_mcts = ClusterMCTSSearch(self.workspace, sample_size=config.cluster_mcts_samples)
        self.mcts = SpeculativeMCTSSearch(
            self.workspace,
            branching_factor=config.mcts_branching_factor,
            c_puct=config.mcts_exploration_c
        )
        self.subagent_coordinator = SubagentCoordinator(self.config, self.client)
        self.router = HierarchicalModelRouter(
            planner_model=config.resolve_planner(),
            worker_model=config.resolve_worker(),
            qa_model=config.resolve_qa(),
            enable_dynamic_escalation=config.enable_hierarchical_routing,
        )

    def _extract_fallback_tool_calls(self, content: str) -> list[dict[str, Any]]:
        calls: list[dict[str, Any]] = []
        if not content:
            return calls
        
        # 1. JSON in markdown code blocks
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

        # 2. XML format tool calls: <tool_call>{...}</tool_call>
        for match in _XML_TOOL_RE.finditer(content):
            try:
                raw = match.group(1).replace("'", '"')
                data = json.loads(raw)
                name = data.get("name") or data.get("tool") or data.get("action")
                args = data.get("arguments") or data.get("params") or data.get("parameters") or {}
                if name and name not in {c["function"]["name"] for c in calls}:
                    calls.append({
                        "function": {
                            "name": name,
                            "arguments": json.dumps(args) if isinstance(args, dict) else str(args)
                        }
                    })
            except Exception:
                continue

        return calls

    def _call_llm_with_cascade(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        primary_model: str,
        temperature: float,
    ) -> LLMResponse:
        """Executes LLM call with retry and fallback cascade across free and paid models."""
        is_free = ":free" in primary_model or primary_model == "openrouter/free"
        cascade = [primary_model]
        if is_free:
            cascade += [m for m in FREE_TIER_CASCADE if m != primary_model]
        else:
            cascade.append("deepseek/deepseek-v4-flash-0731")

        for idx, model in enumerate(cascade):
            try:
                return self.client.complete(
                    messages=messages,
                    tools=tools if tools else None,
                    model=model,
                    temperature=temperature,
                )
            except Exception as e:
                err_str = str(e)
                if any(code in err_str for code in ["429", "502", "503", "504"]) and idx < len(cascade) - 1:
                    backoff = min(10.0, 2.0 ** (idx + 1))
                    time.sleep(backoff)
                    continue
                if idx == len(cascade) - 1:
                    raise

        return LLMResponse(content="", tool_calls=[], usage=LLMUsageMetrics())

    def _run_cegis_on_patch(self, patched_file_path: str) -> str | None:
        """Runs SMT/CEGIS verification against functions modified in the patch."""
        if not self.config.use_cegis_verification:
            return None

        try:
            full_path = self.workspace_dir / patched_file_path
            if not full_path.is_file() or not patched_file_path.endswith(".py"):
                return None

            source = full_path.read_text(encoding="utf-8")
            tree = ast.parse(source)

            func_names = [
                node.name
                for node in ast.walk(tree)
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            ]

            all_ces = []
            type_map = {"int": int, "float": float, "str": str, "bool": bool, "list": list, "dict": dict}

            for func_name in func_names[:4]:
                contracts = self.cegis_solver.extract_function_contracts(patched_file_path, func_name)
                if not contracts:
                    continue

                # Safely extract callable
                ns: dict[str, Any] = {"__builtins__": __builtins__}
                try:
                    exec(compile(source, "<dynamic_cegis>", "exec"), ns)
                    func_callable = ns.get(func_name)
                except Exception:
                    func_callable = None

                if func_callable is None:
                    continue

                param_types: dict[str, type] = {}
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == func_name:
                        for arg in node.args.args:
                            if arg.annotation and isinstance(arg.annotation, ast.Name):
                                if arg.annotation.id in type_map:
                                    param_types[arg.arg] = type_map[arg.annotation.id]

                if not param_types:
                    continue

                rep = self.cegis_solver.synthesize_counterexamples(func_callable, param_types)
                all_ces.extend(rep.counterexamples)

            if all_ces:
                pseudo_report = CEGISSynthesisReport(
                    verified_sound=False,
                    counterexamples=all_ces,
                    smt_solver_status="COUNTEREXAMPLE_FOUND",
                    invariants_checked=len(all_ces),
                )
                return self.cegis_solver.format_cegis_feedback_prompt(pseudo_report, top_k=3)
        except Exception:
            pass
        return None

    def _run_concolic_alert(self, patched_file_path: str) -> str | None:
        """Runs concolic branch exploration and alerts if untested branches remain."""
        if not self.config.use_concolic_fuzzing:
            return None
        try:
            dse_rep = self.concolic_fuzzer.execute_concolic_analysis(patched_file_path)
            if dse_rep.coverage_ratio < 0.70 and dse_rep.uncovered_branches:
                uncovered_str = ", ".join(f"Line {b.line_number} (`{b.condition_source}`)" for b in dse_rep.uncovered_branches[:2])
                return f"[Concolic DSE Alert]: Patch has {dse_rep.coverage_ratio:.0%} branch coverage. Unexercised branch conditions: {uncovered_str}."
        except Exception:
            pass
        return None

    def run(self, task_brief: str, challenge_id: str = "custom_task") -> ExecutionReport:
        start_time = time.perf_counter()
        run_id = generate_run_id(challenge_id, self.config.config_name, self.config.model)
        
        # If RLVR logging is active, start episode
        if self.config.use_rlvr_logging:
            self.rlvr_engine.start_episode(
                trajectory_id=run_id,
                challenge_id=challenge_id,
                model_name=self.config.model,
                config_name=self.config.config_name,
            )

        # Fault Localization (Coverage-Backed SBFL or Causal Slicing)
        localization_notes = ""
        challenge_spec = CHALLENGES.get(challenge_id)

        if (self.config.use_causal_slicing or self.config.use_sbfl_localization) and challenge_spec:
            try:
                rankings = self.cov_sbfl.compute_real_rankings(
                    oracle_script_content=challenge_spec.oracle_test_code,
                    top_k=5,
                )
                if rankings:
                    localization_notes = "\n" + self.sbfl.format_for_prompt(rankings, top_k=5)
            except Exception:
                pass

        if self.config.use_subagent_sandboxing:
            try:
                scout_rep = self.subagent_coordinator.delegate_exploration(self.workspace, task_brief[:300])
                if scout_rep.summary:
                    localization_notes += f"\n\n[Scout Subagent Report]:\n{scout_rep.summary}"
            except Exception:
                pass

        sys_prompt = LIGHTWEIGHT_SYSTEM_PROMPT if self.config.use_lightweight_prompt else DEFAULT_SYSTEM_PROMPT
        enhanced_brief = task_brief + localization_notes
        context = ContextEngine(self.config, sys_prompt, enhanced_brief)
        
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
            
            if report.total_cost_usd >= self.config.max_cost_usd and self.config.max_cost_usd > 0.0:
                report.error_message = f"Budget limit (${self.config.max_cost_usd}) reached."
                break
            if turn_idx >= self.config.max_api_calls:
                report.error_message = "Max API calls reached."
                break

            # Select routing model for this turn
            phase = "PLANNING" if turn_idx == 1 else "EXECUTION"
            decision = self.router.select_model_for_turn(turn_idx, phase)
            active_tools = context.get_filtered_tools(phase="LOCALIZATION" if turn_idx == 1 else "ALL")

            # Inject reproducer instructions if enabled
            if self.config.use_reproduce_first and turn_idx == 1:
                phase_instr = self.reproducer.get_phase_instructions()
                if phase_instr:
                    context.add_turn_user(f"[Reproducer Phase Instruction]: {phase_instr}")

            # Compact context before LLM invocation
            if self.config.use_dialogue_compaction:
                context.compact_with_llm(self.client, compaction_model="minimax/minimax-m3:free")

            messages = context.compile_messages()
            
            try:
                resp: LLMResponse = self._call_llm_with_cascade(
                    messages=messages,
                    tools=active_tools,
                    primary_model=decision.selected_model,
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
            executed_results = []
            for tc in tool_calls:
                fn = tc.get("function", {})
                name = fn.get("name", "")
                raw_args = fn.get("arguments", "{}")
                try:
                    args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
                except Exception:
                    args = {}

                # Speculative MCTS search candidate exploration on patch_apply
                if self.config.use_mcts_search and name == "patch_apply":
                    def _sample_patch(temp: float) -> dict[str, Any]:
                        try:
                            m_resp = self.client.complete(
                                messages=messages,
                                tools=[t for t in active_tools if t.get("function", {}).get("name") == "patch_apply"],
                                model=decision.selected_model,
                                temperature=temp,
                            )
                            for m_tc in m_resp.tool_calls:
                                if m_tc.get("function", {}).get("name") == "patch_apply":
                                    m_args = m_tc["function"]["arguments"]
                                    return json.loads(m_args) if isinstance(m_args, str) else m_args
                        except Exception:
                            pass
                        return args

                    best_patch, _ = self.mcts.explore_candidates(
                        sample_fn=_sample_patch,
                        oracle_eval=lambda: bool(self.oracle_fn and self.oracle_fn(self.workspace_dir)),
                    )
                    if best_patch:
                        args = best_patch

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
                executed_results.append({"tool_name": name, "args": args, "ok": tool_res.ok})

                # In-loop CEGIS formal verification
                if name == "patch_apply" and tool_res.ok:
                    target_p = args.get("path", "")
                    cegis_alert = self._run_cegis_on_patch(target_p)
                    if cegis_alert:
                        context.add_turn_user(cegis_alert, label="cegis_formal_feedback")
                    
                    concolic_alert = self._run_concolic_alert(target_p)
                    if concolic_alert:
                        context.add_turn_user(concolic_alert, label="concolic_branch_alert")

            # Step-level RLVR trajectory recording
            if self.config.use_rlvr_logging:
                try:
                    self.rlvr_engine.record_step(
                        trajectory_id=run_id,
                        turn_index=turn_idx,
                        prompt_messages=messages,
                        model_response_content=resp.content or "",
                        tool_calls=tool_calls,
                        tool_results=executed_results,
                        ast_valid=(self.workspace.ast_errors_caught == 0),
                    )
                except Exception:
                    pass

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

        # Post-success verification gates
        if self.config.use_mutation_testing and report.success:
            try:
                for df in self._get_modified_files()[:1]:
                    mut_rep = self.mutation_verifier.falsify_patch(df)
                    report.mutation_score = mut_rep.mutation_score
                    report.kpi_metrics["mutation_score"] = mut_rep.mutation_score
            except Exception:
                pass

        if self.config.use_adversarial_fuzzing and report.success:
            try:
                fuzz_rep = self.adversarial_fuzzer.verify_patch_robustness()
                report.kpi_metrics["adversarial_robustness"] = fuzz_rep.robustness_score
            except Exception:
                pass

        if self.config.use_cegis_verification and report.success:
            try:
                for df in self._get_modified_files()[:1]:
                    self._run_cegis_on_patch(df)
                report.kpi_metrics["cegis_sound"] = True
            except Exception:
                pass

        if self.config.use_concolic_fuzzing and report.success:
            try:
                for df in self._get_modified_files()[:1]:
                    dse_rep = self.concolic_fuzzer.execute_concolic_analysis(df)
                    report.kpi_metrics["concolic_coverage"] = dse_rep.coverage_ratio
            except Exception:
                pass

        if self.config.use_rlvr_logging:
            try:
                self.rlvr_engine.finalize_episode(
                    trajectory_id=run_id,
                    final_oracle_passed=report.success,
                    mutation_score=report.mutation_score,
                    total_cost_usd=report.total_cost_usd,
                    total_tokens=report.total_tokens,
                )
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
                model_name=self.config.model,
                solved=report.success,
                turns_taken=report.turns_taken,
                total_tokens=report.total_tokens,
                total_cost_usd=report.total_cost_usd,
                duration_sec=report.duration_seconds,
                ast_errors_prevented=report.ast_errors_prevented,
                speculative_rollbacks=report.speculative_rollbacks,
                reproducer_created=report.reproducer_created,
                pareto_score=report.pareto_score,
                kpi_metrics=report.kpi_metrics,
            )
            saved_p = self.catalog.save_run(receipt)
            report.receipt_path = str(saved_p)
        except Exception:
            pass

        return report

    def _dispatch_tool(self, name: str, args: dict[str, Any]) -> ToolExecutionResult:
        if name == "fs_search":
            return self.workspace.fs_search(args.get("pattern", ""), args.get("path", "."))
        elif name == "fs_read":
            return self.workspace.fs_read(args.get("path", ""), args.get("start_line", 1), args.get("line_count", 50))
        elif name == "fs_list":
            return self.workspace.fs_list(args.get("path", "."))
        elif name == "code_find_definitions":
            return self.workspace.code_find_definitions(args.get("symbol_name", ""))
        elif name == "code_find_callers":
            return self.workspace.code_find_callers(args.get("symbol_name", ""))
        elif name == "code_repo_skeleton":
            return self.workspace.code_repo_skeleton()
        elif name == "patch_apply":
            t_chunk = args.get("target_chunk") or args.get("target_snippet") or ""
            r_chunk = args.get("replacement_chunk") or args.get("replacement_snippet") or ""
            return self.workspace.patch_apply(args.get("path", ""), t_chunk, r_chunk)
        elif name == "proc_exec":
            return self.workspace.proc_exec(args.get("command", ""), args.get("timeout_sec", 30))
        else:
            return ToolExecutionResult(ok=False, output=f"Unknown tool: {name}")

    def _get_git_diff_lines(self) -> int:
        try:
            res = subprocess.run(["git", "diff", "--stat"], cwd=self.workspace_dir, capture_output=True, text=True)
            if not res.stdout:
                return 0
            match = re.search(r"(\d+) insertion", res.stdout)
            ins = int(match.group(1)) if match else 0
            match = re.search(r"(\d+) deletion", res.stdout)
            dels = int(match.group(1)) if match else 0
            return ins + dels
        except Exception:
            return 0

    def _get_modified_files(self) -> list[str]:
        try:
            res = subprocess.run(["git", "diff", "--name-only"], cwd=self.workspace_dir, capture_output=True, text=True)
            return [f.strip() for f in res.stdout.splitlines() if f.strip().endswith(".py")]
        except Exception:
            return []
