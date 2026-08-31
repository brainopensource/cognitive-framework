"""Forge Reflexive Episode Engine and Closed-Loop Admission Gate.

Implements:
1. Fast-Cycle TDD Turn Loop with immediate traceback feedback.
2. GoalContract and ForgeAdmissionGate (strict atomic stop gate).
3. Deterministic Reflex Rules (repeated failure, no progress, stale verification).
4. Atomic patch execution and state tracking.
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
from ...domain.canonicalisation.jcs import canonicalise
from ...ports.model import ModelPort
from ...ports.sandbox import SandboxRunner
from ..context.layers import Block, Layer
from .compiler import (
    FORGE_SYSTEM_PROMPT,
    FORGE_TOOLS_SCHEMA,
    ForgeContextCompiler,
    ForgeWorkingState,
)
from .patcher import ForgeAtomicPatcher, PatchResult


@dataclass(frozen=True, slots=True)
class GoalContract:
    """Normative completion contract for a task."""

    task_digest: str
    mode: str = "write"  # "write" | "bugfix" | "greenfield" | "read" | "tutor"
    required_checks: tuple[str, ...] = ("workspace_changed", "verification_fresh", "zero_exit_code", "positive_test_count")
    required_files: tuple[str, ...] = ()
    forbidden_conditions: tuple[str, ...] = ("unresolved_syntax_error", "untested_patch")

    def to_dict(self) -> dict[str, Any]:
        return {
            "taskDigest": self.task_digest,
            "mode": self.mode,
            "requiredChecks": list(self.required_checks),
            "requiredFiles": list(self.required_files),
            "forbiddenConditions": list(self.forbidden_conditions),
        }

    def digest(self) -> str:
        return digest_of(self.to_dict())


@dataclass(frozen=True, slots=True)
class VerificationReceipt:
    """Cryptographic/hash-bound evidence of test execution in workspace."""

    exit_code: int
    executed_test_count: int
    workspace_digest: str
    task_digest: str = ""
    receipt_digest: str = ""
    command: str = ""
    test_summary: str = ""

    @property
    def passed(self) -> bool:
        return self.exit_code == 0 and self.executed_test_count > 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "exitCode": self.exit_code,
            "executedTestCount": self.executed_test_count,
            "workspaceDigest": self.workspace_digest,
            "taskDigest": self.task_digest,
            "receiptDigest": self.receipt_digest,
            "command": self.command,
            "testSummary": self.test_summary,
        }


@dataclass(frozen=True, slots=True)
class AdmissionVerdict:
    """Verdict returned by ForgeAdmissionGate."""

    admissible: bool
    reason: str
    rejection_feedback: str | None = None


class ForgeAdmissionGate:
    """Strict stop gate preventing unverified or premature task completion."""

    def __init__(self, require_patch_for_write: bool = True) -> None:
        self.require_patch_for_write = require_patch_for_write

    def evaluate(
        self,
        goal_contract: GoalContract,
        changed_files: Sequence[str],
        current_workspace_digest: str,
        verification: VerificationReceipt | None = None,
        inspected_files: Sequence[str] = (),
    ) -> AdmissionVerdict:
        is_write_mode = goal_contract.mode in ("write", "bugfix", "greenfield", "code")

        # 1. Read-only mode: no patch required
        if not is_write_mode or not self.require_patch_for_write:
            return AdmissionVerdict(admissible=True, reason="read_only_task_admissible")

        # 2. Write-mode: MUST produce at least one changed file
        if not changed_files:
            return AdmissionVerdict(
                admissible=False,
                reason="MISSING_SOURCE_PATCH",
                rejection_feedback=(
                    "FORGE ADMISSION GATE REJECTION: Completion rejected because no source code "
                    "modifications were detected. You MUST use `edit_file` or `patch_unified` to "
                    "apply your implementation before completing the task."
                ),
            )

        # 3. Verification Receipt must exist
        if verification is None:
            return AdmissionVerdict(
                admissible=False,
                reason="VERIFICATION_REQUIRED",
                rejection_feedback=(
                    "FORGE ADMISSION GATE REJECTION: Completion rejected because the test suite "
                    "has not been executed. Run the test suite with `run_command` and confirm "
                    "100% PASS before finishing."
                ),
            )

        # 4. Verification must have passed with 0 exit code and >0 tests
        if not verification.passed:
            return AdmissionVerdict(
                admissible=False,
                reason="VERIFICATION_FAILED",
                rejection_feedback=(
                    f"FORGE ADMISSION GATE REJECTION: Completion rejected because test verification "
                    f"failed (Exit Code: {verification.exit_code}, Tests Run: {verification.executed_test_count}). "
                    f"Summary:\n{verification.test_summary[:300]}\n"
                    f"Fix the failing assertions before marking completion."
                ),
            )

        # 5. Verification Freshness: Workspace digest MUST match the digest at test execution time
        if verification.workspace_digest != current_workspace_digest:
            return AdmissionVerdict(
                admissible=False,
                reason="VERIFICATION_STALE",
                rejection_feedback=(
                    "FORGE ADMISSION GATE REJECTION: Completion rejected because source files were modified "
                    "after the last test run. Re-run the test suite using `run_command` on the current workspace "
                    "to obtain a fresh verification receipt."
                ),
            )

        # 6. Check required files if specified
        if goal_contract.required_files:
            missing = [f for f in goal_contract.required_files if f not in changed_files]
            if missing:
                return AdmissionVerdict(
                    admissible=False,
                    reason="REQUIRED_FILES_MISSING",
                    rejection_feedback=(
                        f"FORGE ADMISSION GATE REJECTION: Required files were not modified: {missing}."
                    ),
                )

        return AdmissionVerdict(admissible=True, reason="completion_admissible")


@dataclass(frozen=True, slots=True)
class FailureFingerprint:
    """Normalized fingerprint of a test/tool failure."""

    tool_kind: str
    exit_code: int
    failing_tests: tuple[str, ...]
    exception_type: str | None = None
    top_stack_frame: str | None = None
    workspace_digest: str = ""

    def digest(self) -> str:
        return digest_of({
            "tool": self.tool_kind,
            "exit": self.exit_code,
            "failing": list(self.failing_tests),
            "exc": self.exception_type or "",
            "frame": self.top_stack_frame or "",
        })


@dataclass(frozen=True, slots=True)
class StrategyDirective:
    """Directive issued by Reflex policy to steer execution."""

    kind: str  # "redirect" | "abandon_hypothesis" | "change_verification" | "compact_context"
    reason: str
    feedback: str


class RepeatedFailureRule:
    """Detects repeated equivalent failures and steers the agent toward a different approach."""

    @staticmethod
    def evaluate(fingerprints: Sequence[FailureFingerprint]) -> StrategyDirective | None:
        if len(fingerprints) < 2:
            return None
        last = fingerprints[-1]
        prev = fingerprints[-2]
        if last.digest() == prev.digest():
            test_str = ", ".join(last.failing_tests) if last.failing_tests else "current suite"
            return StrategyDirective(
                kind="redirect",
                reason=f"Repeated identical failure on {test_str}",
                feedback=(
                    f"REFLEX ALERT: You repeated the exact same failure on {test_str}. "
                    "Your previous patch did not solve the root cause. Re-read the traceback, "
                    "re-inspect the specification, and formulate a fundamentally different fix."
                ),
            )
        return None


class NoProgressRule:
    """Detects when multiple turns elapse without new evidence or changed status."""

    @staticmethod
    def evaluate(turns_since_progress: int) -> StrategyDirective | None:
        if turns_since_progress >= 3:
            return StrategyDirective(
                kind="abandon_hypothesis",
                reason=f"No progress over {turns_since_progress} consecutive turns",
                feedback=(
                    "REFLEX ALERT: 3 consecutive turns without workspace changes or new test evidence. "
                    "Abandon the current hypothesis and try a new angle of investigation."
                ),
            )
        return None


def compute_workspace_digest(workspace_root: Path) -> str:
    """Compute sha256 digest of all files in workspace (ignoring caches)."""
    hasher = hashlib.sha256()
    for root, dirs, files in os.walk(workspace_root):
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", ".venv", "node_modules")]
        for f in sorted(files):
            if f.endswith(".pyc") or f in ("initial_state.sha256", ".DS_Store"):
                continue
            fp = Path(root, f)
            rel = str(fp.relative_to(workspace_root))
            try:
                content = fp.read_bytes()
                hasher.update(rel.encode("utf-8"))
                hasher.update(content)
            except Exception:
                pass
    return hasher.hexdigest()


def parse_test_output(output: str, exit_code: int) -> Tuple[int, tuple[str, ...], Optional[str], Optional[str]]:
    """Extract test count, failing test names, exception type, and top frame from test stdout/stderr."""
    failing: list[str] = []
    test_count = 0
    exc_type: Optional[str] = None
    top_frame: Optional[str] = None

    # Python unittest format: Ran X tests in Ys
    ran_match = re.search(r"Ran (\d+) tests?", output)
    if ran_match:
        test_count = int(ran_match.group(1))

    # pytest format: X passed, Y failed / X passed
    pyt_passed = re.search(r"(\d+) passed", output)
    pyt_failed = re.search(r"(\d+) failed", output)
    if pyt_passed or pyt_failed:
        p_count = int(pyt_passed.group(1)) if pyt_passed else 0
        f_count = int(pyt_failed.group(1)) if pyt_failed else 0
        test_count = max(test_count, p_count + f_count)

    # If all passed and exit_code == 0, fallback test_count to at least 1
    if exit_code == 0 and test_count == 0:
        if "OK" in output or "PASSED" in output or "pass" in output.lower():
            test_count = 1

    # Extract FAIL/ERROR test names
    for line in output.splitlines():
        fail_m = re.match(r"^(?:FAIL|ERROR):\s+([^\s]+)", line)
        if fail_m:
            failing.append(fail_m.group(1))
        # Pytest FAILED test_file.py::test_fn
        pyt_fail = re.search(r"FAILED\s+([^\s]+)", line)
        if pyt_fail:
            failing.append(pyt_fail.group(1))

    # Exception type
    exc_m = re.search(r"([A-Za-z_0-9]+Error|Exception|AssertionError):", output)
    if exc_m:
        exc_type = exc_m.group(1)

    # Top frame
    frame_m = re.search(r'File "([^"]+)", line (\d+), in (\w+)', output)
    if frame_m:
        top_frame = f"{frame_m.group(1)}:{frame_m.group(2)} ({frame_m.group(3)})"

    return test_count, tuple(dict.fromkeys(failing)), exc_type, top_frame


@dataclass
class ForgeOutcome:
    """Outcome of a complete 1-Forge execution."""

    status: str  # "COMPLETED" | "ABANDONED" | "FAILED" | "INSTRUMENT_ERROR"
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
        }


class ForgeEngine:
    """Reflexive Agentic Micro-Forge Engine."""

    def __init__(
        self,
        workspace_root: Path | str,
        model_port: Any,
        compiler: ForgeContextCompiler | None = None,
        patcher: ForgeAtomicPatcher | None = None,
        admission_gate: ForgeAdmissionGate | None = None,
        sandbox_runner: SandboxRunner | None = None,
        command_runner: Callable[[str, Path], Tuple[int, str]] | None = None,
        max_turns: int = 8,
        token_ceiling: int = 64_000,
        budget_limit_usd: float = 0.20,
    ) -> None:
        self.workspace_root = Path(workspace_root).resolve()
        self.model_port = model_port
        self.compiler = compiler or ForgeContextCompiler(token_ceiling=token_ceiling)
        self.patcher = patcher or ForgeAtomicPatcher(self.workspace_root)
        self.admission_gate = admission_gate or ForgeAdmissionGate()
        self.sandbox_runner = sandbox_runner
        self.command_runner = command_runner
        self.max_turns = max_turns
        self.budget_limit_usd = budget_limit_usd

    def execute_turn_tool(
        self,
        tool_name: str,
        args: Dict[str, Any],
        goal_contract: GoalContract,
        changed_files: list[str],
        inspected_files: list[str],
        last_receipt: list[Optional[VerificationReceipt]],
        last_verdict: list[Optional[AdmissionVerdict]] | None = None,
    ) -> Tuple[str, bool]:
        """Execute a single tool call from the model within the workspace."""
        try:
            if tool_name == "view_file":
                path_str = args.get("path", "")
                p = (self.workspace_root / path_str.lstrip("/")).resolve()
                if not str(p).startswith(str(self.workspace_root)):
                    return "Error: Path traversal outside workspace", False
                if not p.is_file():
                    return f"Error: File not found: {path_str}", False
                inspected_files.append(path_str)
                content = p.read_text(encoding="utf-8")
                return content, False

            elif tool_name == "edit_file":
                path_str = args.get("path", "")
                content = args.get("content", "")
                res = self.patcher.apply_file_write(path_str, content)
                if res.success:
                    for cf in res.changed_files:
                        if cf not in changed_files:
                            changed_files.append(cf)
                    # Any edit invalidates previous verification (workspace is dirty)
                    last_receipt[0] = None
                    return f"Successfully wrote {len(content)} chars to {path_str}", False
                return f"Error applying edit to {path_str}: {res.error}", False

            elif tool_name in ("surgical_patch", "patch_chunk", "resilient_patch"):
                path_str = args.get("path", "")
                target = args.get("target", "")
                replacement = args.get("replacement", "")
                res = self.patcher.apply_resilient_patch(path_str, target, replacement)
                if res.success:
                    for cf in res.changed_files:
                        if cf not in changed_files:
                            changed_files.append(cf)
                    last_receipt[0] = None
                    details_str = f" ({res.details[0]})" if res.details else ""
                    return f"Successfully applied surgical patch to {path_str}{details_str}", False
                return f"Error applying surgical patch to {path_str}: {res.error}", False

            elif tool_name == "patch_unified":
                diff_text = args.get("diff", "")
                res = self.patcher.apply_unified_diff(diff_text)
                if res.success:
                    for cf in res.changed_files:
                        if cf not in changed_files:
                            changed_files.append(cf)
                    last_receipt[0] = None
                    return f"Successfully applied diff modifying {len(res.changed_files)} files: {res.changed_files}", False
                return f"Error applying patch diff: {res.error}", False

            elif tool_name == "run_command":
                cmd = args.get("command", "")
                if not cmd:
                    return "Error: Empty command", False
                if self.command_runner is not None:
                    exit_code, output = self.command_runner(cmd, self.workspace_root)
                elif self.sandbox_runner is not None:
                    res = self.sandbox_runner.execute(cmd.split())
                    if hasattr(res, "value") and res.value:
                        exit_code = getattr(res.value.receipt, "exit_code", 0)
                        output = getattr(res.value.receipt, "stdout", "")
                    else:
                        exit_code = 1
                        output = f"Sandbox execution failed: {res}"
                else:
                    return "Error: No command runner or sandbox runner configured on ForgeEngine", False

                ws_digest = compute_workspace_digest(self.workspace_root)
                t_count, failing, exc_type, top_frame = parse_test_output(output, exit_code)

                # Capture verification receipt if tests ran
                receipt = VerificationReceipt(
                    exit_code=exit_code,
                    executed_test_count=t_count,
                    workspace_digest=ws_digest,
                    task_digest=goal_contract.task_digest,
                    receipt_digest=digest_of({"cmd": cmd, "exit": exit_code, "ws": ws_digest}),
                    command=cmd,
                    test_summary=output[:500],
                )
                last_receipt[0] = receipt

                summary_prefix = f"[Exit Code {exit_code}]"
                if t_count > 0:
                    summary_prefix += f" | {t_count} tests run"
                if failing:
                    summary_prefix += f" | Failing: {list(failing)}"
                if exc_type:
                    summary_prefix += f" | {exc_type}"

                return f"{summary_prefix}\n\nOutput:\n{output}", False

            elif tool_name == "list_dir":
                rel = args.get("path", ".") or "."
                target = (self.workspace_root / rel.lstrip("/")).resolve()
                if not target.is_dir():
                    return f"Error: Not a directory: {rel}", False
                entries = [f"{'[DIR] ' if c.is_dir() else '[FILE]'} {c.name}" for c in sorted(target.iterdir())]
                return "\n".join(entries) if entries else "(Empty directory)", False

            elif tool_name == "finish_task":
                current_ws_digest = compute_workspace_digest(self.workspace_root)
                verdict = self.admission_gate.evaluate(
                    goal_contract=goal_contract,
                    changed_files=changed_files,
                    current_workspace_digest=current_ws_digest,
                    verification=last_receipt[0],
                    inspected_files=inspected_files,
                )
                if last_verdict is not None:
                    last_verdict[0] = verdict
                if not verdict.admissible:
                    return verdict.rejection_feedback or f"Admission Rejected: {verdict.reason}", False

                return f"Goal Satisfied: {args.get('summary', 'Verified green.')}", True

            else:
                return f"Error: Unknown tool {tool_name}", False

        except TimeoutError:
            return "Error: Command timed out", False
        except Exception as exc:
            return f"Error executing tool {tool_name}: {exc}", False

    def run_episode(
        self,
        task_brief: str,
        goal_contract: GoalContract | None = None,
    ) -> ForgeOutcome:
        """Run the complete reflexive TDD episode loop."""
        t_start = time.perf_counter()
        task_digest = digest_of({"brief": task_brief})
        contract = goal_contract or GoalContract(task_digest=task_digest)

        working_state = ForgeWorkingState(task_brief=task_brief)
        changed_files: list[str] = []
        inspected_files: list[str] = []
        last_receipt_box: list[Optional[VerificationReceipt]] = [None]
        last_verdict_box: list[Optional[AdmissionVerdict]] = [None]
        fingerprints: list[FailureFingerprint] = []

        dialogue_blocks: list[Block] = []
        notes_blocks: list[Block] = []
        trajectory: list[dict[str, Any]] = []

        total_prompt_tokens = 0
        total_comp_tokens = 0
        total_cost_usd = 0.0
        turns_since_progress = 0
        last_changed_len = 0

        finished = False
        turn = 0
        terminal_status = "ABANDONED"
        diagnosis = "Max turns reached without verified admission"

        while turn < self.max_turns and not finished:
            turn += 1

            # 1. Evaluate Reflex Rules
            directive: Optional[StrategyDirective] = None
            rep_directive = RepeatedFailureRule.evaluate(fingerprints)
            if rep_directive:
                directive = rep_directive
            else:
                np_directive = NoProgressRule.evaluate(turns_since_progress)
                if np_directive:
                    directive = np_directive

            # 2. Update working state
            working_state = ForgeWorkingState(
                task_brief=task_brief,
                active_hypothesis=working_state.active_hypothesis,
                confirmed_facts=working_state.confirmed_facts,
                rejected_hypotheses=working_state.rejected_hypotheses,
                inspected_files=tuple(dict.fromkeys(inspected_files)),
                changed_files=tuple(dict.fromkeys(changed_files)),
                verification_evidence=(last_receipt_box[0].to_dict(),) if last_receipt_box[0] else (),
                dead_ends=working_state.dead_ends,
                next_action=directive.feedback if directive else None,
            )

            # 3. Context Compilation
            messages, meta = self.compiler.compile(
                brief=task_brief,
                working_state=working_state,
                notes=notes_blocks,
                dialogue=dialogue_blocks,
                reflex_directive=directive.feedback if directive else None,
            )

            # 4. Propose turn action via ModelPort / model provider
            sampling = {"temperature": 0.0, "max_tokens": 2048}
            context_bundle = {"messages": messages}

            try:
                res = self.model_port.propose(context_bundle, FORGE_TOOLS_SCHEMA, sampling)
            except Exception as exc:
                terminal_status = "INSTRUMENT_ERROR"
                diagnosis = f"Model provider exception: {exc}"
                break

            if not getattr(res, "ok", True) and getattr(res, "error", None):
                terminal_status = "INSTRUMENT_ERROR"
                diagnosis = f"Model error: {getattr(res.error, 'message', res.error)}"
                break

            val = res.value if hasattr(res, "value") else res
            choice_msg = val.get("message", val) if isinstance(val, dict) else {}
            content = choice_msg.get("content") or ""
            tool_calls = choice_msg.get("tool_calls") or []

            # Usage and Cost tracking
            usage = val.get("usage", {}) if isinstance(val, dict) else {}
            p_tok = usage.get("prompt_tokens", 0) or meta.get("total_tokens", 0)
            c_tok = usage.get("completion_tokens", 0) or len(content) // 4
            total_prompt_tokens += p_tok
            total_comp_tokens += c_tok
            cost = usage.get("cost", 0.0) or (p_tok * 1.5e-6 + c_tok * 6.0e-6)
            total_cost_usd += cost

            # Append model message to dialogue
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
                # Model provided conversational response without tools
                turns_since_progress += 1
                trajectory.append({"turn": turn, "model_text": content})
                continue

            # 5. Execute Tool Calls
            turn_actions: list[dict[str, Any]] = []
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

                output, is_terminal = self.execute_turn_tool(
                    fn_name,
                    args,
                    contract,
                    changed_files,
                    inspected_files,
                    last_receipt_box,
                    last_verdict_box,
                )

                turn_actions.append({"tool": fn_name, "args": args, "output_snippet": output[:120]})

                dialogue_blocks.append(
                    Block(
                        layer=Layer.DIALOGUE,
                        source="tool",
                        label=f"{fn_name}_result",
                        text=output,
                        evictable=True,
                    )
                )

                if fn_name == "run_command" and last_receipt_box[0]:
                    rec = last_receipt_box[0]
                    if not rec.passed:
                        t_cnt, failing, exc_t, top_f = parse_test_output(output, rec.exit_code)
                        fingerprints.append(
                            FailureFingerprint(
                                tool_kind="run_command",
                                exit_code=rec.exit_code,
                                failing_tests=failing,
                                exception_type=exc_t,
                                top_stack_frame=top_f,
                                workspace_digest=rec.workspace_digest,
                            )
                        )
                    else:
                        fingerprints.clear()

                if is_terminal:
                    finished = True
                    terminal_status = "COMPLETED"
                    diagnosis = "Task completed with fresh passing test verification"
                    break

            trajectory.append({"turn": turn, "actions": turn_actions})

            # Check progress
            if len(changed_files) > last_changed_len:
                turns_since_progress = 0
                last_changed_len = len(changed_files)
            else:
                turns_since_progress += 1

        total_latency = time.perf_counter() - t_start

        return ForgeOutcome(
            status=terminal_status,
            turns=turn,
            prompt_tokens=total_prompt_tokens,
            completion_tokens=total_comp_tokens,
            total_tokens=total_prompt_tokens + total_comp_tokens,
            cost_usd=total_cost_usd,
            latency_seconds=round(total_latency, 2),
            changed_files=tuple(dict.fromkeys(changed_files)),
            verification_receipt=last_receipt_box[0],
            diagnosis=diagnosis,
            trajectory=trajectory,
            admission_verdict=last_verdict_box[0],
        )
