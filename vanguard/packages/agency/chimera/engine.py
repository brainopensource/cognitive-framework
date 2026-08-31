"""Chimera Autonomous Turn Loop and Execution Engine.

Unites:
L0: Fast Engineering Loop (Observe -> Act -> Verify -> Adapt)
L1: Deliberation & Search (BestFirstSearch, Parallel-Distill-Refine, Critical Checkpoints)
L2: Trajectory Recording & Online Bandit Adaptation
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
import hashlib
import json
import os
from pathlib import Path
import re
import time
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Tuple

from ...domain.canonicalisation.digest import digest_of
from ...ports.model import ModelPort
from ...ports.sandbox import SandboxRunner
from ..context.layers import Block, Layer
from ..forge.engine import (
    AdmissionVerdict,
    ForgeAdmissionGate,
    GoalContract,
    VerificationReceipt,
    compute_workspace_digest,
)
from .blackboard import (
    CognitiveBlackboard,
    CognitiveBudget,
    Fact,
    Hypothesis,
    PatchCandidate,
    TaskFeatures,
    TrajectorySummary,
)
from .compiler import (
    CHIMERA_SYSTEM_PROMPT,
    CHIMERA_TOOLS_SCHEMA,
    ChimeraContextCompiler,
)
from .governor import MetaCognitiveGovernor
from .patcher import ChimeraAtomicPatcher
from .retrieval import RetrievalMarket
from .router import CognitiveRouter
from .search import BestFirstEngineeringSearch, EngineeringState
from .symbolic import SymbolicCortex
from .verification import VerificationCortex, VerificationLevel


@dataclass
class ChimeraOutcome:
    """Outcome of a complete Chimera execution."""

    status: str  # "COMPLETED" | "ABANDONED" | "FAILED"
    turns: int
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: float
    latency_seconds: float
    changed_files: tuple[str, ...]
    verification_receipt: VerificationReceipt | None
    diagnosis: str
    trajectory: list[dict[str, Any]] = field(default_factory=list)
    admission_verdict: AdmissionVerdict | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "turns": self.turns,
            "promptTokens": self.prompt_tokens,
            "completionTokens": self.completion_tokens,
            "totalTokens": self.total_tokens,
            "costUsd": self.cost_usd,
            "latencySeconds": self.latency_seconds,
            "changedFiles": list(self.changed_files),
            "verification": self.verification_receipt.to_dict() if self.verification_receipt else None,
            "diagnosis": self.diagnosis,
            "trajectory": self.trajectory,
            "admissionVerdict": {
                "admissible": self.admission_verdict.admissible,
                "reason": self.admission_verdict.reason,
            } if self.admission_verdict else None,
        }


class ChimeraEngine:
    """Heterogeneous Neuro-Symbolic Agent Engine for Vanguard."""

    def __init__(
        self,
        workspace_root: Path | str,
        model_port: Any,
        compiler: ChimeraContextCompiler | None = None,
        patcher: ChimeraAtomicPatcher | None = None,
        governor: MetaCognitiveGovernor | None = None,
        router: CognitiveRouter | None = None,
        retrieval_market: RetrievalMarket | None = None,
        admission_gate: ForgeAdmissionGate | None = None,
        sandbox_runner: Any = None,
        command_runner: Callable[[str, Path], Tuple[int, str]] | None = None,
        max_turns: int = 15,
        token_ceiling: int = 64_000,
        budget_limit_usd: float = 0.20,
    ) -> None:
        self.workspace_root = Path(workspace_root)
        self.model_port = model_port
        self.compiler = compiler or ChimeraContextCompiler(token_ceiling=token_ceiling)
        self.patcher = patcher or ChimeraAtomicPatcher(workspace_root=workspace_root)
        self.governor = governor or MetaCognitiveGovernor()
        self.router = router or CognitiveRouter()
        self.retrieval_market = retrieval_market or RetrievalMarket(workspace_root=workspace_root)
        self.admission_gate = admission_gate or ForgeAdmissionGate(require_patch_for_write=True)
        self.sandbox_runner = sandbox_runner
        self.command_runner = command_runner
        self.max_turns = max_turns
        self.token_ceiling = token_ceiling
        self.budget_limit_usd = budget_limit_usd
        self.search_engine = BestFirstEngineeringSearch()

    def _run_command_safe(self, cmd: str) -> Tuple[int, str]:
        """Execute command safely via command_runner or sandbox_runner."""
        if self.command_runner is not None:
            return self.command_runner(cmd, self.workspace_root)
        if self.sandbox_runner is not None:
            try:
                res = self.sandbox_runner.execute(cmd.split()) if hasattr(self.sandbox_runner, "execute") else self.sandbox_runner.run(cmd)
                if hasattr(res, "value") and res.value:
                    exit_code = getattr(res.value.receipt, "exit_code", 0)
                    output = getattr(res.value.receipt, "stdout", "")
                    return exit_code, output
                return getattr(res, "exit_code", 1), getattr(res, "output", str(res))
            except Exception as exc:
                return 1, f"Sandbox execution error: {exc}"
        return 1, "Error: No command runner or sandbox runner configured on ChimeraEngine"

    def execute_tool_call(
        self,
        tool_name: str,
        args: Dict[str, Any],
        goal_contract: GoalContract,
        changed_files: list[str],
        inspected_files: list[str],
        last_receipt_box: list[Optional[VerificationReceipt]],
        last_verdict_box: list[Optional[AdmissionVerdict]],
    ) -> Tuple[str, bool]:
        """Execute a tool call within the workspace."""
        try:
            if tool_name == "view_file":
                path_str = args.get("path", "")
                p = (self.workspace_root / path_str.lstrip("/")).resolve()
                if not str(p).startswith(str(self.workspace_root)):
                    return "Error: Path traversal outside workspace", False
                if not p.is_file():
                    return f"Error: File not found: {path_str}", False
                inspected_files.append(path_str)
                return p.read_text(encoding="utf-8"), False

            elif tool_name in ("edit_file", "write_file"):
                path_str = args.get("path", "")
                content = args.get("content", "")
                res = self.patcher.write_file(path_str, content)
                if res.success:
                    for cf in res.changed_files:
                        if cf not in changed_files:
                            changed_files.append(cf)
                    last_receipt_box[0] = None  # Workspace is dirty
                    return f"Successfully wrote {len(content)} chars to {path_str}", False
                return f"Error writing file {path_str}: {res.error}", False

            elif tool_name == "surgical_patch":
                path_str = args.get("path", "")
                target = args.get("target", "")
                replacement = args.get("replacement", "")
                res = self.patcher.apply_resilient_patch(path_str, target, replacement)
                if res.success:
                    for cf in res.changed_files:
                        if cf not in changed_files:
                            changed_files.append(cf)
                    last_receipt_box[0] = None
                    return f"Successfully applied surgical patch to {path_str} (strategy: {res.strategy_used})", False
                return f"Error applying surgical patch to {path_str}: {res.error}", False

            elif tool_name == "patch_unified":
                diff_text = args.get("diff", "")
                res = self.patcher.apply_unified_diff(diff_text)
                if res.success:
                    for cf in res.changed_files:
                        if cf not in changed_files:
                            changed_files.append(cf)
                    last_receipt_box[0] = None
                    return f"Successfully applied unified diff modifying: {res.changed_files}", False
                return f"Error applying patch diff: {res.error}", False

            elif tool_name == "run_command":
                cmd = args.get("command", "")
                if not cmd:
                    return "Error: Empty command", False

                exit_code, output = self._run_command_safe(cmd)
                ws_digest = compute_workspace_digest(self.workspace_root)
                ver_record = VerificationCortex.parse_test_output(output, exit_code)

                # Capture verification receipt
                receipt = VerificationReceipt(
                    exit_code=exit_code,
                    executed_test_count=ver_record.executed_tests,
                    workspace_digest=ws_digest,
                    task_digest=goal_contract.task_digest,
                    receipt_digest=digest_of({"cmd": cmd, "exit": exit_code, "ws": ws_digest}),
                    command=cmd,
                    test_summary=output[:500],
                )
                last_receipt_box[0] = receipt

                status_label = "PASS" if receipt.passed else "FAIL"
                summary_line = f"[Exit Code {exit_code} | {status_label}] ({ver_record.executed_tests} tests run"
                if ver_record.failed_tests:
                    summary_line += f", Failing: {list(ver_record.failed_tests)}"
                summary_line += ")"

                return f"{summary_line}\n\nOutput:\n{output}", False

            elif tool_name == "list_dir":
                rel = args.get("path", ".") or "."
                target = (self.workspace_root / rel.lstrip("/")).resolve()
                if not target.is_dir():
                    return f"Error: Not a directory: {rel}", False
                entries = [f"{'[DIR] ' if c.is_dir() else '[FILE]'} {c.name}" for c in sorted(target.iterdir())]
                return "\n".join(entries) if entries else "(Empty directory)", False

            elif tool_name == "search_workspace":
                query = args.get("query", "")
                ranked_files, ranked_symbols = self.retrieval_market.query(query, seed_files=changed_files)
                res_lines = [f"Found {len(ranked_files)} relevant files:"]
                for rf in ranked_files:
                    res_lines.append(f"- {rf.path} (score: {rf.relevance_score:.2f}, provenance: {rf.reason})")
                if ranked_symbols:
                    res_lines.append("\nRelevant Symbols:")
                    for s in ranked_symbols[:5]:
                        res_lines.append(f"- {s.symbol_name} ({s.kind}) in {s.file_path}")
                return "\n".join(res_lines), False

            elif tool_name == "solve_invariants":
                problem = args.get("problem_statement", "")
                inv_res = SymbolicCortex.extract_and_solve_invariants(problem)
                return f"Symbolic Solution (success={inv_res.success}):\n{inv_res.solution_text}", False

            elif tool_name == "finish_task":
                current_ws_digest = compute_workspace_digest(self.workspace_root)
                verdict = self.admission_gate.evaluate(
                    goal_contract=goal_contract,
                    changed_files=changed_files,
                    current_workspace_digest=current_ws_digest,
                    verification=last_receipt_box[0],
                    inspected_files=inspected_files,
                )
                last_verdict_box[0] = verdict
                if not verdict.admissible:
                    return verdict.rejection_feedback or f"Admission Gate Rejected: {verdict.reason}", False

                return f"Goal Satisfied: {args.get('summary', 'Verified green.')}", True

            else:
                return f"Error: Unknown tool '{tool_name}'", False

        except Exception as exc:
            return f"Tool execution error: {exc}", False

    def run_episode(
        self,
        task_brief: str,
        goal_contract: GoalContract | None = None,
    ) -> ChimeraOutcome:
        """Execute the full autonomous neuro-symbolic Chimera loop."""
        t_start = time.perf_counter()
        task_digest = digest_of({"brief": task_brief})
        contract = goal_contract or GoalContract(task_digest=task_digest)

        # Detect task features
        is_greenfield = not any(self.workspace_root.iterdir()) if self.workspace_root.is_dir() else True
        features = TaskFeatures(
            language="python",
            kind="greenfield" if is_greenfield else "bugfix",
            repo_file_count=sum(1 for _ in self.workspace_root.rglob("*") if _.is_file()) if self.workspace_root.is_dir() else 0,
            issue_length=len(task_brief),
            multi_file=True if "multi" in task_brief.lower() or is_greenfield else False,
            mathematical_invariants=any(kw in task_brief.lower() for kw in ("equation", "math", "invariants", "segment", "quantum")),
        )

        board = CognitiveBlackboard.from_task(
            task_brief=task_brief,
            features=features,
            budget=CognitiveBudget(
                max_turns=self.max_turns,
                token_ceiling=self.token_ceiling,
                max_cost_usd=self.budget_limit_usd,
            ),
        )

        changed_files: list[str] = []
        inspected_files: list[str] = []
        last_receipt_box: list[Optional[VerificationReceipt]] = [None]
        last_verdict_box: list[Optional[AdmissionVerdict]] = [None]
        dialogue_blocks: list[Block] = []
        trajectory: list[dict[str, Any]] = []

        total_prompt_tokens = 0
        total_comp_tokens = 0
        total_cost_usd = 0.0
        failure_streak = 0
        turns_since_progress = 0
        last_changed_count = 0
        turn = 0
        terminal_status = "ABANDONED"
        diagnosis = "Max turns reached"

        # Pre-seed candidate files from retrieval market
        seed_files, seed_syms = self.retrieval_market.query(task_brief)
        if seed_files:
            board = board.update_candidates(files=seed_files, symbols=seed_syms)

        while turn < self.max_turns and board.budget.available:
            turn += 1

            # 1. Governor Decision
            directive = self.governor.decide(
                board=board,
                failure_streak=failure_streak,
                turns_since_progress=turns_since_progress,
            )

            if directive.kind.value == "finish":
                terminal_status = "COMPLETED"
                diagnosis = "Task completed and verified"
                break
            elif directive.kind.value == "stop":
                terminal_status = "ABANDONED"
                diagnosis = f"Stopped by governor: {directive.rationale_code}"
                break

            # 2. Router Selection
            route = self.router.select(directive, board)

            # 3. Context Compilation
            distilled = self.search_engine.distill_trajectory_summaries(board.trajectory_summaries)
            messages = self.compiler.compile(board, dialogue_blocks, distilled_dead_ends=distilled)

            # 4. Model Propose
            t0_prop = time.perf_counter()
            try:
                proposal = self.model_port.propose(
                    context={"messages": messages},
                    tools=CHIMERA_TOOLS_SCHEMA,
                    sampling={"temperature": 0.1, "route": route},
                )
            except Exception as exc:
                terminal_status = "FAILED"
                diagnosis = f"Model proposal failed: {exc}"
                break

            # Extract content & tool calls
            val = getattr(proposal, "value", None) or proposal
            if not isinstance(val, dict):
                val = getattr(val, "__dict__", {}) or {}

            content = val.get("content") or val.get("text") or ""
            tool_calls = val.get("tool_calls") or []
            usage = val.get("usage", {}) if isinstance(val, dict) else {}
            p_tok = usage.get("prompt_tokens", 0)
            c_tok = usage.get("completion_tokens", 0)
            cost = float(val.get("cost_usd") or usage.get("cost", 0.0) or (p_tok * 1.5e-6 + c_tok * 6.0e-6))

            total_prompt_tokens += p_tok
            total_comp_tokens += c_tok
            total_cost_usd += cost
            board = board.consume_budget(turns=1, tokens=p_tok + c_tok, cost_usd=cost)

            dialogue_blocks.append(
                Block(
                    layer=Layer.DIALOGUE,
                    source="model",
                    label=f"turn_{turn}_model",
                    text=content or "(Proposed Tool Calls)",
                    evictable=False,
                )
            )

            if not tool_calls:
                turns_since_progress += 1
                trajectory.append({"turn": turn, "model_text": content, "route": route})
                continue

            # 5. Tool Execution
            turn_actions: list[dict[str, Any]] = []
            is_finished = False
            for tc in tool_calls:
                fn_name = tc.get("function", {}).get("name") or tc.get("name")
                raw_args = tc.get("function", {}).get("arguments") or tc.get("args") or {}
                if isinstance(raw_args, str):
                    try:
                        args = json.loads(raw_args, strict=False)
                    except Exception:
                        try:
                            args = json.loads(raw_args)
                        except Exception:
                            args = {}
                elif isinstance(raw_args, (dict, Mapping)):
                    args = dict(raw_args)
                else:
                    args = {}

                output, is_term = self.execute_tool_call(
                    fn_name,
                    args,
                    contract,
                    changed_files,
                    inspected_files,
                    last_receipt_box,
                    last_verdict_box,
                )

                turn_actions.append({"tool": fn_name, "args": args, "output_snippet": output[:150]})
                dialogue_blocks.append(
                    Block(
                        layer=Layer.DIALOGUE,
                        source="tool",
                        label=f"{fn_name}_result",
                        text=output,
                        evictable=True,
                    )
                )

                # Record test verification if run_command was executed
                if fn_name == "run_command" and last_receipt_box[0]:
                    rec = last_receipt_box[0]
                    if rec.passed:
                        failure_streak = 0
                        # Record critical passing checkpoint
                        self.search_engine.record_checkpoint(
                            EngineeringState(
                                state_id=f"state_t{turn}",
                                hypothesis=directive.objective,
                                workspace_digest=rec.workspace_digest,
                                target_files=tuple(changed_files),
                                exit_code=0,
                                tests_passed=rec.executed_test_count,
                                cost_usd=total_cost_usd,
                                turn=turn,
                            )
                        )
                    else:
                        failure_streak += 1

                if is_term:
                    is_finished = True
                    terminal_status = "COMPLETED"
                    diagnosis = "Completed with verified passing receipt"
                    break

            trajectory.append({"turn": turn, "route": route, "actions": turn_actions})

            # Check progress
            if len(changed_files) > last_changed_count:
                turns_since_progress = 0
                last_changed_count = len(changed_files)
            else:
                turns_since_progress += 1

            if is_finished:
                break

        total_latency = time.perf_counter() - t_start

        return ChimeraOutcome(
            status=terminal_status,
            turns=turn,
            prompt_tokens=total_prompt_tokens,
            completion_tokens=total_comp_tokens,
            total_tokens=total_prompt_tokens + total_comp_tokens,
            cost_usd=round(total_cost_usd, 6),
            latency_seconds=round(total_latency, 2),
            changed_files=tuple(dict.fromkeys(changed_files)),
            verification_receipt=last_receipt_box[0],
            diagnosis=diagnosis,
            trajectory=trajectory,
            admission_verdict=last_verdict_box[0],
        )
