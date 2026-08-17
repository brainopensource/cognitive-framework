"""The L1–L5 prefix-stable context compiler (`REQ-CTX-001`, `VG-03 §10`).

Two things live here and they are deliberately separate:

* **`ContextCompiler`** assembles a prompt vector. It is a pure function of its
  construction arguments and its call arguments — no clock, no sink, no
  kernel. It cannot log, so it cannot be the reason a prompt was assembled
  differently on the run where logging was enabled.
* **`CompetencePriorRecorder`** puts $P(\\text{success} \\mid \\text{task})$ on
  the wire before turn 1 (`S5-SA-002`).

**Why the prefix is frozen at construction.** `VG-03 §10.2`: anything appended
to `L1`–`L4` mid-run destroys every downstream cache hit, and mid-run additions
go to `L5`, always. A compiler that accepted the system core per call would
make prefix stability a property of *every* call site, provable only by
inspection of all of them. Freezing the first three layers at composition
(`VG-03 §5.3`, registries freeze at composition) makes it a property of the
type: there is no method on this object that can move the prefix.

**Why the brief is exempt from compaction.** `VG-03 §10.5`: work is checked
against the brief, never against the last summary of it, so the brief cannot be
the thing that is summarised. `L4` therefore holds two distinct kinds of
material — the immutable brief, and notes that may be dropped — and only the
second is reachable by the budget.

**What this module does not do.** It holds no authority, opens no lease and
touches no adapter. The prior it records is a value handed to it by the
composition root; deriving that value from a model is `ModelPort` work, and
scoring it is the Evidence plane's (`ICD §3`).
"""

from __future__ import annotations

import json
import math
from typing import Any, Mapping, Sequence

from ...kernel import Event
from .compaction import CompactionStrategy, resolve_compaction_strategy
from .layers import (
    BREAKPOINT_LAYERS,
    Block,
    CompiledContext,
    Fragment,
    Layer,
    blocks_of,
    estimate_tokens,
)

__all__ = [
    "CacheBreakpointCeilingExceeded",
    "CompetencePriorRecorder",
    "ContextBudgetExceeded",
    "ContextCompiler",
]

#: How many decimal places of a prior survive to the ledger. Four is well past
#: the resolution any calibration set of this size can distinguish, and fixing
#: it makes the wire form canonical rather than host-float-dependent.
_PRIOR_PLACES = 4


class ContextBudgetExceeded(ValueError):
    """The task plus the stable prefix exceeds the token budget (`VG-03 §10.2`)."""
    pass


class CacheBreakpointCeilingExceeded(ValueError):
    """More cache breakpoints requested than the ceiling (`VG-03 §10.2`)."""
    pass


class ContextCompiler:
    """The L1-L5 context compiler.

    Pure function: prompt vector in, compiled context out.
    """

    def __init__(
        self,
        *,
        system_core: str,
        tool_schemas: Sequence[Mapping[str, Any]] = (),
        environment: str = "",
        token_ceiling: int = 64_000,
        breakpoint_ceiling: int = 4,
        source: str = "manifest",
        context_policy: Mapping[str, Any] | str | None = None,
        compaction_strategy: CompactionStrategy | None = None,
    ) -> None:
        if token_ceiling <= 0:
            raise ValueError("token_ceiling must be positive")
        self._token_ceiling = token_ceiling
        self._breakpoint_ceiling = breakpoint_ceiling
        self._prefix = self._render_prefix(system_core, tool_schemas, environment, source)
        self._prefix_tokens = sum(block.token_estimate for block in self._prefix)

        if compaction_strategy is not None:
            self._compaction_strategy = compaction_strategy
            self._compaction_options = context_policy if isinstance(context_policy, Mapping) else {}
        else:
            strat, opts = resolve_compaction_strategy(context_policy)
            self._compaction_strategy = strat
            self._compaction_options = opts

    # -- composition-time rendering -------------------------------------

    @staticmethod
    def _render_prefix(system_core: str, tool_schemas: Sequence[Mapping[str, Any]],
                       environment: str, source: str) -> tuple[Block, ...]:
        """The cached region, rendered once.

        Tool schemas go through a sorted-key JSON dump rather than `str()` so
        that two composition roots naming the same tools produce the same
        bytes. A prefix whose stability depended on dictionary insertion order
        would be stable in tests and unstable in production.
        """
        rendered: list[Block] = []
        if system_core:
            rendered.append(Block(layer=Layer.SYSTEM, source=source,
                                  label="system-core", text=system_core))
        if tool_schemas:
            payload = json.dumps([dict(schema) for schema in tool_schemas],
                                 sort_keys=True, separators=(",", ":"),
                                 ensure_ascii=False)
            rendered.append(Block(layer=Layer.TOOLS, source=source,
                                  label="tool-schemas", text=payload))
        if environment:
            rendered.append(Block(layer=Layer.ENVIRONMENT, source=source,
                                  label="environment-map", text=environment))
        return tuple(rendered)

    # -- assembly --------------------------------------------------------

    def compile(
        self,
        *,
        brief: str,
        notes: Sequence[Fragment] = (),
        dialogue: Sequence[Fragment] = (),
    ) -> CompiledContext:
        """Assemble one prompt vector for one turn.

        `brief` is the immutable task statement (`VG-03 §10.5`). `notes` is the
        rest of `L4`. `dialogue` is `L5`, oldest first.
        """
        task = ((Block(layer=Layer.TASK, source="operator", label="brief", text=brief),)
                if brief else ())
        notes_blocks = list(blocks_of(Layer.TASK, notes))
        dialogue_blocks = list(blocks_of(Layer.DIALOGUE, dialogue))

        breakpoints = self._breakpoints(task_present=bool(task or notes_blocks))
        if len(breakpoints) > self._breakpoint_ceiling:
            raise CacheBreakpointCeilingExceeded(
                f"{len(breakpoints)} breakpoints exceeds the ceiling of "
                f"{self._breakpoint_ceiling} (VG-03 §10.2)")

        floor = self._prefix_tokens + sum(block.token_estimate for block in task)
        if floor > self._token_ceiling:
            raise ContextBudgetExceeded(
                f"L1-L3 plus the brief cost {floor} tokens against a ceiling of "
                f"{self._token_ceiling}; none of them may be truncated")

        elided, dropped = self._fit(floor, notes_blocks, dialogue_blocks)

        return CompiledContext(
            blocks=self._prefix + tuple(task) + tuple(notes_blocks) + tuple(dialogue_blocks),
            breakpoints=breakpoints,
            elided=tuple(elided),
            dropped=tuple(dropped),
        )

    def _breakpoints(self, *, task_present: bool) -> tuple[Layer, ...]:
        """A breakpoint on an empty layer is a breakpoint spent on nothing."""
        present = {block.layer for block in self._prefix}
        if task_present:
            present.add(Layer.TASK)
        return tuple(layer for layer in BREAKPOINT_LAYERS if layer in present)

    def _fit(self, floor: int, notes: list[Block],
             dialogue: list[Block]) -> tuple[list[str], list[str]]:
        """Bring the vector under the ceiling according to the configured CompactionStrategy."""
        return self._compaction_strategy.compact(
            floor=floor,
            ceiling=self._token_ceiling,
            notes=notes,
            dialogue=dialogue,
            options=self._compaction_options,
        )


def _receipt_for(block: Block) -> Block:
    """What `result_eviction` leaves behind: the fact, without the body.

    `VG-03 §10.3` — "keep that a file was read; drop the body once superseded".
    An evicted result that vanished entirely would let the operator re-issue
    the same read forever, which is the failure eviction exists to avoid.
    """
    return Block(
        layer=block.layer,
        source=block.source,
        label=block.label,
        text=f"[{block.label} from {block.source}: "
             f"{block.byte_length} bytes elided after use]",
        evictable=False,
    )


class CompetencePriorRecorder:
    """`S5-SA-002` — logs $P(\\text{success} \\mid \\text{task})$ before turn 1.

    Emitted straight to the event sink rather than through `Kernel.dispatch`,
    for the same reason the episode loop appends `ProposalProduced` itself
    (`VG-03 §6.1`): the prior is produced *outside* the dispatch sequence, and
    it authorises nothing. Every effect still has exactly one path (`AT-01`);
    this is not an effect.

    The payload carries digests, never prompt text (`REQ-TRUST-001`): a brief
    may quote a secret, and an event store is the one place from which nothing
    can be withdrawn.
    """

    def __init__(self, *, clock: Any, events: Any) -> None:
        self._clock = clock
        self._events = events
        self._recorded: set[tuple[str, str]] = set()

    def record(
        self,
        *,
        episode_id: str,
        run_id: str,
        principal: str,
        prior: float,
        context: CompiledContext,
        before_turn: int = 0,
    ) -> bool:
        """Emit `CompetencePriorRecorded`. Returns whether it reached the sink.

        Refuses a second prior for the same episode: a *pre-action* prior
        recorded twice is two priors, and the second is conditioned on evidence
        the first never saw. Scoring the pair as one would corrupt the Brier
        set rather than enrich it.
        """
        value = float(prior)
        if not math.isfinite(value) or not 0.0 <= value <= 1.0:
            raise ValueError(f"a competence prior must lie in [0, 1]; got {prior!r}")

        key = (run_id, episode_id)
        if key in self._recorded:
            return False

        event = Event(
            kind="CompetencePriorRecorded",
            reason="pre_action",
            at=self._clock.now(),
            run_id=run_id,
            principal=principal,
            payload={
                "episodeId": episode_id,
                "beforeTurn": before_turn,
                "prior": f"{value:.{_PRIOR_PLACES}f}",
                "promptDigest": context.digest,
                "prefixDigest": context.prefix_digest,
                "tokens": context.total_tokens,
                "elided": len(context.elided),
                "dropped": len(context.dropped),
            },
        )
        try:
            self._events.emit(event)
        except Exception:
            # `F-25`: emission failure never fails the work it describes. The
            # episode proceeds without a prior; the calibration set is one row
            # short, which is a measurement gap and not a task failure.
            return False
        self._recorded.add(key)
        return True


# Re-exported for callers that only ever import the compiler module.
__all__ += ["Block", "CompiledContext", "Fragment", "Layer", "estimate_tokens"]
