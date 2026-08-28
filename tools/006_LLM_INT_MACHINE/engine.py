"""The Main Autonomous Turn Engine for 006_LLM_INT_MACHINE."""

from __future__ import annotations
import json
import re
import time
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Sequence

try:
    from .config import HarnessConfig
    from .context_engine import ContextEngine
    from .llm_client import OpenRouterClient, MockLLMClient, LLMResponse
    from .reproducer_protocol import ReproducerManager
    from .tools import ToolWorkspace, TOOL_DEFINITIONS, ToolExecutionResult
except ImportError:
    from config import HarnessConfig
    from context_engine import ContextEngine
    from llm_client import OpenRouterClient, MockLLMClient, LLMResponse
    from reproducer_protocol import ReproducerManager
    from tools import ToolWorkspace, TOOL_DEFINITIONS, ToolExecutionResult


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
    error_message: str = ""
    turns_detail: list[dict[str, Any]] = field(default_factory=list)


DEFAULT_SYSTEM_PROMPT = """You are an expert autonomous software engineer solving a code defect.
Follow this methodology:
1. Examine the codebase structure and locate the issue using `fs_search` and `fs_read`.
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
    ) -> None:
        self.workspace_dir = Path(workspace_dir).resolve()
        self.config = config
        self.client = llm_client or OpenRouterClient()
        self.oracle_fn = oracle_fn
        self.workspace = ToolWorkspace(self.workspace_dir, config)
        self.reproducer = ReproducerManager(self.workspace, enabled=config.use_reproduce_first)

    def _extract_fallback_tool_calls(self, content: str) -> list[dict[str, Any]]:
        """Extract tool calls if model outputs them inside JSON markdown codeblocks."""
        calls: list[dict[str, Any]] = []
        if not content:
            return calls
        
        # Regex for json code blocks
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
        context = ContextEngine(self.config, DEFAULT_SYSTEM_PROMPT, task_brief)
        
        report = ExecutionReport(
            config_name=self.config.config_name,
            challenge_id=challenge_id,
            success=False,
        )

        if self.config.use_speculative_rollback:
            self.workspace.git_checkpoint("initial_clean_state")

        for turn_idx in range(1, self.config.max_turns + 1):
            report.turns_taken = turn_idx
            
            if report.total_cost_usd >= self.config.max_cost_usd:
                report.error_message = f"Budget limit (${self.config.max_cost_usd}) reached."
                break
            if turn_idx >= self.config.max_api_calls:
                report.error_message = "Max API calls reached."
                break

            messages = context.compile_messages()
            
            try:
                resp: LLMResponse = self.client.complete(
                    messages=messages,
                    tools=TOOL_DEFINITIONS,
                    model=self.config.model,
                    temperature=self.config.temperature,
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
                    break
                elif "complete" in resp.content.lower() or "fixed" in resp.content.lower() or turn_idx > 3:
                    if self.oracle_fn and self.oracle_fn(self.workspace_dir):
                        report.success = True
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

                tool_res = self._dispatch_tool(name, args)
                
                if tool_res.is_ast_error:
                    report.ast_errors_prevented += 1

                context.add_tool_receipt(name, tool_res.output, is_large=(tool_res.bytes_produced > 1000))

            if self.oracle_fn and self.oracle_fn(self.workspace_dir):
                report.success = True
                break

        report.duration_seconds = time.perf_counter() - start_time
        report.ast_errors_prevented = self.workspace.ast_errors_caught
        report.reproducer_created = self.reproducer.state.repro_file_created
        report.git_diff_lines = self._get_git_diff_lines()

        if self.oracle_fn and self.oracle_fn(self.workspace_dir):
            report.success = True

        return report

    def _dispatch_tool(self, name: str, args: dict[str, Any]):
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
