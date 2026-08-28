"""Time-Travel Record-Replay Debugger & Deterministic Execution Trace Engine.

Records fine-grained instruction step snapshots, enables backward time-travel stepping,
and pinpoints the exact temporal moment t* of state corruption in concurrent / stateful programs.
"""

from __future__ import annotations
import copy
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Sequence


@dataclass
class ExecutionFrameSnapshot:
    step_index: int
    file_path: str
    function_name: str
    line_number: int
    local_variables: dict[str, Any]
    event_type: str  # 'call', 'line', 'return', 'exception'
    timestamp: float = field(default_factory=time.time)


@dataclass
class TimeTravelDebugTrace:
    total_steps_recorded: int
    first_divergence_step: int | None
    divergence_reason: str
    snapshots: list[ExecutionFrameSnapshot] = field(default_factory=list)


class TimeTravelDebugger:
    """Records deterministic execution traces and enables backward time-travel inspection."""

    def __init__(self, max_history_steps: int = 1000):
        self.max_steps = max_history_steps
        self.history: list[ExecutionFrameSnapshot] = []
        self.cursor: int = 0

    def record_frame(
        self,
        file_path: str,
        function_name: str,
        line_number: int,
        locals_dict: dict[str, Any],
        event_type: str = "line",
    ) -> ExecutionFrameSnapshot:
        if len(self.history) >= self.max_steps:
            self.history.pop(0)

        # Sanitize locals to prevent circular unpickleable structures
        clean_locals = {}
        for k, v in locals_dict.items():
            try:
                if isinstance(v, (int, float, str, bool, list, dict, set, type(None))):
                    clean_locals[k] = repr(v)[:100]
                else:
                    clean_locals[k] = f"<{type(v).__name__}>"
            except Exception:
                clean_locals[k] = "<unserializable>"

        snap = ExecutionFrameSnapshot(
            step_index=len(self.history) + 1,
            file_path=file_path,
            function_name=function_name,
            line_number=line_number,
            local_variables=clean_locals,
            event_type=event_type,
        )
        self.history.append(snap)
        self.cursor = len(self.history) - 1
        return snap

    def step_backward(self, steps: int = 1) -> ExecutionFrameSnapshot | None:
        """Step backward in execution history and inspect past variable state."""
        if not self.history:
            return None
        self.cursor = max(0, self.cursor - steps)
        return self.history[self.cursor]

    def step_forward(self, steps: int = 1) -> ExecutionFrameSnapshot | None:
        """Step forward in execution history."""
        if not self.history:
            return None
        self.cursor = min(len(self.history) - 1, self.cursor + steps)
        return self.history[self.cursor]

    def find_state_corruption_point(
        self,
        invariant_predicate: Callable[[dict[str, Any]], bool],
    ) -> tuple[int | None, ExecutionFrameSnapshot | None]:
        """Finds the first temporal step where local state violated an expected invariant."""
        for snap in self.history:
            try:
                if not invariant_predicate(snap.local_variables):
                    return snap.step_index, snap
            except Exception:
                return snap.step_index, snap
        return None, None

    def export_trace_summary(self, top_k_frames: int = 5) -> str:
        if not self.history:
            return "No time-travel trace steps recorded."

        lines = [
            f"### ⏱️ Time-Travel Execution Trace ({len(self.history)} steps recorded):",
            f"Showing last {min(top_k_frames, len(self.history))} steps leading to current state:",
        ]
        for snap in self.history[-top_k_frames:]:
            vars_str = ", ".join(f"{k}={v}" for k, v in list(snap.local_variables.items())[:3])
            lines.append(
                f"- Step {snap.step_index}: `{snap.file_path}:{snap.line_number}` in `{snap.function_name}()` [{vars_str}]"
            )
        return "\n".join(lines)
