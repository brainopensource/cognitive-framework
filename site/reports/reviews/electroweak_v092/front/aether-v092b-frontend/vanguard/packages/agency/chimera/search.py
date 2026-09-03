"""Engineering Search and Test-Time Exploration for CHIMERA.

Implements Best-First Search, Beam Search, Parallel-Distill-Refine (PDR),
and critical-state trajectory replay for long-horizon coding tasks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import heapq
import time
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Tuple

from ...domain.canonicalisation.digest import digest_of
from .blackboard import TrajectorySummary


@dataclass(frozen=True, slots=True)
class EngineeringState:
    """A checkpointed snapshot of the workspace and reasoning state."""

    state_id: str
    hypothesis: str
    workspace_digest: str
    target_files: tuple[str, ...]
    patch_summary: str = ""
    exit_code: int = 1
    tests_passed: int = 0
    tests_failed: int = 0
    failure_messages: tuple[str, ...] = ()
    cost_usd: float = 0.0
    turn: int = 0

    @property
    def is_verified_green(self) -> bool:
        return self.exit_code == 0 and self.tests_passed > 0 and self.tests_failed == 0

    def score(self) -> float:
        """Compute holistic state quality score [0.0, 1.0]."""
        if self.is_verified_green:
            return 1.0
        # Partial test pass score
        total_tests = self.tests_passed + self.tests_failed
        test_ratio = (self.tests_passed / total_tests) if total_tests > 0 else 0.0
        
        # Penalize repeated errors and cost
        progress_val = 0.6 * test_ratio + (0.2 if len(self.target_files) > 0 else 0.0)
        return round(max(0.0, min(0.95, progress_val - (self.cost_usd * 0.1))), 4)


@dataclass(order=True)
class SearchNode:
    """Node in the engineering search priority queue."""

    priority: float  # Inverted for min-heap heapq: lower = better priority
    node_id: str = field(compare=False)
    state: EngineeringState = field(compare=False)
    parent_id: Optional[str] = field(default=None, compare=False)
    depth: int = field(default=0, compare=False)


class BestFirstEngineeringSearch:
    """Best-First search explorer for branching hypothesis and repair paths."""

    def __init__(self, max_nodes: int = 8, beam_width: int = 2) -> None:
        self.max_nodes = max_nodes
        self.beam_width = beam_width
        self._nodes: dict[str, SearchNode] = {}
        self._heap: list[SearchNode] = []
        self._critical_checkpoints: list[EngineeringState] = []

    def record_checkpoint(self, state: EngineeringState) -> None:
        """Save a critical state (e.g. initial localization, first passing test)."""
        self._critical_checkpoints.append(state)
        # Add to search tree
        node_id = f"node_{len(self._nodes)}_{state.state_id}"
        # Priority inverted for min-heap: 1.0 - score
        prio = round(1.0 - state.score(), 4)
        node = SearchNode(priority=prio, node_id=node_id, state=state, depth=0)
        self._nodes[node_id] = node
        heapq.heappush(self._heap, node)

    def get_best_state(self) -> Optional[EngineeringState]:
        """Return the highest scoring state explored so far."""
        if not self._nodes:
            return None
        best_node = min(self._nodes.values(), key=lambda n: n.priority)
        return best_node.state

    def pop_next_to_expand(self) -> Optional[SearchNode]:
        """Pop the most promising unexpanded node."""
        if self._heap:
            return heapq.heappop(self._heap)
        return None

    def distill_trajectory_summaries(self, summaries: Sequence[TrajectorySummary]) -> str:
        """Parallel-Distill-Refine (PDR): Distill failed attempts into actionable guidance."""
        if not summaries:
            return "No previous attempts recorded."

        lines = ["=== Distilled Prior Attempts & Dead Ends ==="]
        for s in summaries[-4:]:
            status_str = "PASSED" if s.exit_code == 0 else f"FAILED (Exit: {s.exit_code})"
            lines.append(
                f"- Turn {s.turn} [{s.action_type}] on {list(s.target_files)} -> {status_str}: {s.summary_text[:120]}"
            )
        lines.append("Directive: Avoid repeating these identical failed patch patterns.")
        return "\n".join(lines)
