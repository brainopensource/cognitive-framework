"""Compaction strategy protocol and registry (S8-B-02, VG-03 §10.3).

Provides pluggable dialogue compaction strategies selected by manifest context_policy
and frozen at composition time.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol, Sequence, runtime_checkable

from .layers import (
    Block,
    Layer,
    GOAL_ECHO_SOURCE,
    PINNED_L4_SOURCES,
    PINNED_L5_SOURCES,
)


#: Lines a receipt keeps verbatim when the body around them goes. The header
#: is the first line — the action that ran or the finding that was made — and
#: an `artifact=` binding is the only route back to the bytes being dropped.
#: `NT-C05` requires both to survive the omission of the body they describe.
_ARTIFACT_LINE = "artifact="

#: A header names an action or a finding; it is not a log line. Clipping at
#: this width keeps a retained header from smuggling the body back in past the
#: eviction that was supposed to remove it.
_RECEIPT_HEADER_CHARS = 160


def _clip_line(line: str) -> str:
    text = " ".join(line.split())
    if len(text) <= _RECEIPT_HEADER_CHARS:
        return text
    return text[: _RECEIPT_HEADER_CHARS - 3] + "..."


def _retained_lines(block: Block) -> list[str]:
    """The identity lines eviction may not take with the body (`NT-C05`).

    A receipt that kept only "N bytes elided" would name neither what ran nor
    where the bytes went, which turns an eviction into a deletion. So the
    header and any artifact binding survive — they are identity rather than
    content, and both are bounded.

    A single-line block has no header: its one line *is* the body, and
    "retaining the header" there would retain exactly what eviction was asked
    to reclaim. Structure is the evidence that a header exists, and the clip
    is the guarantee that a long first line cannot become one.
    """
    lines = block.text.split("\n")
    if len(lines) < 2:
        return []
    retained = [_clip_line(lines[0])] if lines[0].strip() else []
    for line in lines[1:]:
        clipped = _clip_line(line)
        if line.startswith(_ARTIFACT_LINE) and clipped not in retained:
            retained.append(clipped)
    return retained


def _receipt_for(block: Block) -> Block:
    """What `result_eviction` leaves behind: the fact, without the body.

    `VG-03 §10.3` — "keep that a file was read; drop the body once superseded".
    `NT-C05` fixes what "the fact" means: the header that says which action
    produced the block and the artifact digest that still reaches the bytes.
    Dropping those alongside the body leaves a block that attests nothing.
    """
    retained = _retained_lines(block)
    marker = f"[{block.label} from {block.source}: {block.byte_length} bytes elided after use]"
    return Block(
        layer=block.layer,
        source=block.source,
        label=block.label,
        text="\n".join(retained + [marker]),
        evictable=False,
    )


#: The source the prompt assembler stamps on the durable task-state note it
#: compiles from `fold_task_state` (`runtime/prompt_assembler.py`).
_TASK_STATE_SOURCE = "task-state"

#: T-142. `PINNED_L4_SOURCES` carries the FEATURE_SPEC tier 0-1 findings.
#: The durable task-state note belongs beside them: it is the only L4 block
#: that carries the objective, the open obligations, the settled effects, the
#: aggregate consumption and the grant state at once, so dropping it to
#: satisfy a budget deletes the whole continuation rather than trimming it.
#: `Fragment.evictable` does not express this -- it marks a tool-result body
#: that may be elided into a receipt, and it defaults to `False` on every
#: ordinary note -- so the mandatory set is named here, where the drop policy
#: lives, rather than inferred from it.
_MANDATORY_L4_SOURCES: frozenset[str] = PINNED_L4_SOURCES | {_TASK_STATE_SOURCE}

#: T-142. Keys of the durable task-state note whose values are identity, not
#: content: they are bounded by construction and a continuation that loses one
#: cannot be reconciled against the run that produced it. They are retained
#: whole at every pressure level.
_TASK_STATE_IDENTITY_KEYS: tuple[str, ...] = (
    "objective", "overarchingGoal", "constraints", "taskClass", "runId",
    "revision", "nextAction", "activeStepId", "changedFilesTreeHash",
    "remainingBudgets", "lastVerification", "failureClass",
    "repositoryIdentity", "indexSnapshotDigest", "selectionPolicyIdentity",
    "recoveryState",
)

#: Collections a long session grows without bound. Under pressure each is
#: bounded to its newest entries and the omission is stated in place, so the
#: planner is told what it can no longer see instead of being shown a shorter
#: list that looks complete.
_TASK_STATE_BOUNDED_KEYS: tuple[str, ...] = (
    "inspectedFiles", "discoveries", "deadEnds", "routeDecisions",
    "hypotheses", "falsifiedHypotheses", "settledInvariants",
    "strategySteps", "verificationPlan", "plan", "backlog",
    "settledEffects", "modifiedFiles", "changeSurface", "todoItems",
)

#: The ladder `_bound_mandatory_note` walks. Each rung keeps fewer entries of
#: every bounded collection; the last rung keeps none, and even there the
#: identity keys and every unsatisfied obligation survive.
_TASK_STATE_KEEP_LADDER: tuple[int, ...] = (32, 16, 8, 4, 2, 1, 0)


def _is_open_obligation(item: Any) -> bool:
    """An obligation nobody has discharged. Bounding one away loses the work."""
    return isinstance(item, Mapping) and str(item.get("status", "pending")) != "complete"


def _bound_collection(key: str, value: Any, keep: int) -> tuple[Any, int]:
    """Bound one collection to `keep` newest entries. Returns (value, omitted).

    `todoItems` is the exception the name "preserves obligations" turns on:
    every still-open obligation is retained whatever the pressure, and only
    discharged ones are counted away.
    """
    if not isinstance(value, list) or len(value) <= keep:
        return value, 0
    if key == "todoItems":
        open_items = [item for item in value if _is_open_obligation(item)]
        closed = [item for item in value if not _is_open_obligation(item)]
        retained = open_items + closed[len(closed) - max(keep - len(open_items), 0):] \
            if keep > len(open_items) else open_items
        return retained, len(value) - len(retained)
    return value[len(value) - keep:] if keep else [], len(value) - keep


def _bound_mandatory_note(block: Block, keep: int) -> Block | None:
    """One rung of bounded task-state compaction, or None if it does not apply.

    T-142. A mandatory L4 note may not be dropped -- doing so takes the
    objective, the open obligations, the settled effects and the consumption
    with it, which is precisely the long-session failure this bounds. So the
    note is *bounded* instead: identity whole, unbounded collections trimmed
    newest-first, and an explicit `omitted` record of what was trimmed. This
    projects the same task state the run already produced; it does not author
    a second one.
    """
    try:
        state = json.loads(block.text)
    except (TypeError, ValueError):
        return None
    if not isinstance(state, dict):
        return None

    bounded: dict[str, Any] = {
        key: state[key] for key in _TASK_STATE_IDENTITY_KEYS if key in state
    }
    # Bounding is iterative: each rung of the ladder re-enters this function
    # with the previous rung's output. Counting only this pass would report
    # the last trim rather than everything compaction has taken, so prior
    # omissions are carried forward and added to.
    prior = state.get("boundedByCompaction")
    omitted: dict[str, int] = {
        str(key): int(value) for key, value in prior.items()
        if isinstance(value, int) and not isinstance(value, bool)
    } if isinstance(prior, Mapping) else {}
    for key in _TASK_STATE_BOUNDED_KEYS:
        if key not in state:
            continue
        value, dropped_count = _bound_collection(key, state[key], keep)
        bounded[key] = value
        if dropped_count:
            omitted[key] = omitted.get(key, 0) + dropped_count
    for key, value in state.items():
        if key not in bounded and key not in _TASK_STATE_BOUNDED_KEYS:
            bounded[key] = value
    if omitted:
        # Stated in place. A bounded list that did not say it was bounded
        # would read as a complete one, and the planner would conclude the
        # omitted work was never there.
        bounded["boundedByCompaction"] = omitted

    text = json.dumps(bounded, sort_keys=True, default=str)
    if len(text) >= len(block.text):
        return None
    return Block(
        layer=block.layer, source=block.source, label=block.label,
        text=text, evictable=block.evictable,
    )


def _drop_flexible_notes(notes: list[Block], dropped: list[str], elided: list[str],
                         total, ceiling: int) -> None:
    """T-15: drop flexible L4 notes under pressure; never FEATURE_SPEC pinned
    sources, and never a note that declares itself mandatory (T-142).

    Before T-142 the only exemption here was membership of
    `PINNED_L4_SOURCES`, so `block.evictable` -- which the prompt assembler
    sets to `False` on the durable task-state note -- was not read at all. A
    long enough session therefore dropped the whole of sigma: objective, open
    obligations, settled effects, aggregate consumption and grant state all
    left the prompt at once, silently, and the turn proceeded. A mandatory
    note is now bounded down the `_TASK_STATE_KEEP_LADDER` instead.
    """
    def _droppable(block: Block) -> bool:
        return block.source not in _MANDATORY_L4_SOURCES

    while total() > ceiling and notes:
        index = next((i for i, block in enumerate(notes) if _droppable(block)), None)
        if index is not None:
            dropped.append(notes.pop(index).label)
            continue
        if not _bound_mandatory_notes(notes, elided, total, ceiling):
            # Nothing further may be reclaimed here. Returning over the
            # ceiling is the honest outcome: the alternative is deleting
            # state the composition declared mandatory.
            break


def _bound_mandatory_notes(notes: list[Block], elided: list[str],
                           total, ceiling: int) -> bool:
    """Walk the keep ladder over mandatory notes. True if anything shrank."""
    progressed = False
    for keep in _TASK_STATE_KEEP_LADDER:
        for index, block in enumerate(notes):
            if block.source != _TASK_STATE_SOURCE:
                continue
            bounded = _bound_mandatory_note(block, keep)
            if bounded is None:
                continue
            notes[index] = bounded
            if block.label not in elided:
                elided.append(block.label)
            progressed = True
        if total() <= ceiling:
            return True
    return progressed


def _drop_flexible_dialogue(dialogue: list[Block], dropped: list[str], elided: list[str], total, ceiling: int) -> None:
    """T-36 / `NT-C04`: drop L5 oldest-first under pressure.

    Two L5 sources are exempt. The goal echo at the tail is the objective
    itself, and the newest complete interaction is the state the next action
    starts from; dropping either to satisfy a budget buys room by deleting the
    reason the turn exists. Their *bodies* may still be elided into receipts.
    """
    while total() > ceiling and dialogue:
        index = next((i for i, block in enumerate(dialogue)
                      if block.source not in PINNED_L5_SOURCES), None)
        if index is None:
            break
        removed = dialogue.pop(index)
        dropped.append(removed.label)
        if removed.label in elided:
            elided.remove(removed.label)


@runtime_checkable
class CompactionStrategy(Protocol):
    """Protocol for bringing context within token ceilings (S8-B-02)."""

    def compact(
        self,
        floor: int,
        ceiling: int,
        notes: list[Block],
        dialogue: list[Block],
        options: Mapping[str, Any] | None = None,
    ) -> tuple[list[str], list[str]]:
        """Compacts notes and dialogue in-place to fit within ceiling.

        Returns (elided_labels, dropped_labels).
        """
        ...


class ResultEvictionStrategy:
    """Default result eviction strategy (VG-03 §10.3).

    1. Elides evictable dialogue blocks into compact receipts (oldest first).
    2. Drops oldest dialogue blocks if still over ceiling.
    3. Drops oldest notes if still over ceiling.
    """

    def compact(
        self,
        floor: int,
        ceiling: int,
        notes: list[Block],
        dialogue: list[Block],
        options: Mapping[str, Any] | None = None,
    ) -> tuple[list[str], list[str]]:
        elided: list[str] = []
        dropped: list[str] = []

        def total() -> int:
            return floor + sum(b.token_estimate for b in notes) + sum(b.token_estimate for b in dialogue)

        for index, block in enumerate(dialogue):
            if total() <= ceiling:
                break
            if not block.evictable or block.source == GOAL_ECHO_SOURCE:
                continue
            dialogue[index] = _receipt_for(block)
            elided.append(block.label)

        _drop_flexible_dialogue(dialogue, dropped, elided, total, ceiling)

        _drop_flexible_notes(notes, dropped, elided, total, ceiling)

        return elided, dropped


class RecencyWindowStrategy:
    """Recency window compaction strategy (S8-B-02).

    1. Retains at most `maxItems` recent dialogue entries, dropping older entries.
    2. Elides evictable dialogue bodies into receipts to fit within token ceiling.
    3. Drops oldest dialogue fragments if still over ceiling.
    4. Drops oldest notes if still over ceiling.
    """

    def compact(
        self,
        floor: int,
        ceiling: int,
        notes: list[Block],
        dialogue: list[Block],
        options: Mapping[str, Any] | None = None,
    ) -> tuple[list[str], list[str]]:
        opts = options or {}
        max_items = opts.get("maxItems") or opts.get("max_items") or 64
        try:
            max_items = int(max_items)
        except (ValueError, TypeError):
            max_items = 64

        elided: list[str] = []
        dropped: list[str] = []

        # 1. Truncate dialogue to the recency window limit; keep the goal
        #    echo and the newest complete interaction (`NT-C04`).
        while len([b for b in dialogue if b.source not in PINNED_L5_SOURCES]) > max_items:
            index = next((i for i, block in enumerate(dialogue)
                          if block.source not in PINNED_L5_SOURCES), None)
            if index is None:
                break
            removed = dialogue.pop(index)
            dropped.append(removed.label)

        def total() -> int:
            return floor + sum(b.token_estimate for b in notes) + sum(b.token_estimate for b in dialogue)

        # 2. Result eviction over remaining dialogue
        for index, block in enumerate(dialogue):
            if total() <= ceiling:
                break
            if not block.evictable or block.source == GOAL_ECHO_SOURCE:
                continue
            dialogue[index] = _receipt_for(block)
            elided.append(block.label)

        # 3. If still exceeding ceiling, drop oldest flexible dialogue items
        _drop_flexible_dialogue(dialogue, dropped, elided, total, ceiling)

        # 4. If still exceeding ceiling, drop oldest flexible notes
        _drop_flexible_notes(notes, dropped, elided, total, ceiling)

        return elided, dropped


@dataclass
class StructuredRecord:
    """Structured compaction state tracking (S10-B-03, VG-03 §10.4)."""

    decisions: list[str] = field(default_factory=list)
    invariants: list[str] = field(default_factory=list)
    open_items: list[str] = field(default_factory=list)
    artifacts: list[str] = field(default_factory=list)
    dead_ends: list[str] = field(default_factory=list)

    def to_summary_text(self) -> str:
        lines = ["[Structured Consolidation Record]"]
        if self.decisions:
            lines.append("Decisions: " + "; ".join(self.decisions))
        if self.invariants:
            lines.append("Invariants: " + "; ".join(self.invariants))
        if self.open_items:
            lines.append("Open: " + "; ".join(self.open_items))
        if self.artifacts:
            lines.append("Artifacts: " + "; ".join(self.artifacts))
        if self.dead_ends:
            lines.append("DeadEnds (abandoned paths): " + "; ".join(self.dead_ends))
        return "\n".join(lines)


class StructuredConsolidateStrategy:
    """Consolidates dialogue into a StructuredRecord with deadEnds tracking (S10-B-03).
    
    Prevents re-exploring abandoned paths by preserving explicit deadEnds while reducing transcript tokens.
    """

    def compact(
        self,
        floor: int,
        ceiling: int,
        notes: list[Block],
        dialogue: list[Block],
        options: Mapping[str, Any] | None = None,
    ) -> tuple[list[str], list[str]]:
        elided: list[str] = []
        dropped: list[str] = []

        def total() -> int:
            return floor + sum(b.token_estimate for b in notes) + sum(b.token_estimate for b in dialogue)

        if total() <= ceiling:
            return elided, dropped

        # Extract structured information from dialogue blocks to be consolidated
        rec = StructuredRecord()
        to_consolidate: list[Block] = []

        while total() > ceiling and dialogue:
            index = next((i for i, block in enumerate(dialogue)
                          if block.source not in PINNED_L5_SOURCES), None)
            if index is None:
                break
            b = dialogue.pop(index)
            dropped.append(b.label)
            to_consolidate.append(b)
            # Scan text for dead ends / decisions
            if "failed" in b.text.lower() or "error" in b.text.lower() or "dead end" in b.text.lower():
                rec.dead_ends.append(f"{b.label}: {b.text[:60].strip()}")
            elif "decision" in b.text.lower() or "selected" in b.text.lower():
                rec.decisions.append(f"{b.label}: {b.text[:60].strip()}")

        if to_consolidate:
            summary_block = Block(
                layer=Layer.DIALOGUE,
                source="structured_consolidate",
                label="structured_record",
                text=rec.to_summary_text(),
                evictable=False,
            )
            dialogue.insert(0, summary_block)
            elided.append("structured_record")

            # If inserting summary_block pushed total over ceiling, drop remaining un-consolidated blocks
            while total() > ceiling and len(dialogue) > 1:
                index = next(
                    (i for i, block in enumerate(dialogue)
                     if block.source not in PINNED_L5_SOURCES
                     and block.label != "structured_record"),
                    None,
                )
                if index is None:
                    break
                b = dialogue.pop(index)
                dropped.append(b.label)

        _drop_flexible_notes(notes, dropped, elided, total, ceiling)

        return elided, dropped


class UnknownCompactionStrategyError(ValueError):
    """Raised when an unknown compaction strategy is requested (EVO-13 fail-closed)."""


COMPACTION_REGISTRY: dict[str, CompactionStrategy] = {
    "result_eviction": ResultEvictionStrategy(),
    "result-eviction": ResultEvictionStrategy(),
    "recency_window": RecencyWindowStrategy(),
    "recency-window": RecencyWindowStrategy(),
    "structured_consolidate": StructuredConsolidateStrategy(),
    "structured-consolidate": StructuredConsolidateStrategy(),
}


def resolve_compaction_strategy(
    policy: Mapping[str, Any] | str | None,
) -> tuple[CompactionStrategy, Mapping[str, Any]]:
    """Resolve compaction strategy and options from manifest context_policy dict or name.

    Fails closed if the strategy identifier is unknown.
    """
    if policy is None:
        return COMPACTION_REGISTRY["recency-window"], {}

    if isinstance(policy, str):
        kind = policy
        options: Mapping[str, Any] = {}
    elif isinstance(policy, Mapping):
        kind = str(policy.get("kind") or policy.get("strategy") or "recency-window")
        options = policy
    else:
        return COMPACTION_REGISTRY["recency-window"], {}

    strategy = COMPACTION_REGISTRY.get(kind)
    if strategy is None:
        raise UnknownCompactionStrategyError(
            f"unknown compaction strategy {kind!r}; registered: {sorted(COMPACTION_REGISTRY)}"
        )
    return strategy, options
