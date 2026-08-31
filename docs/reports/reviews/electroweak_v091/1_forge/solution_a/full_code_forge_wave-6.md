---
id: report.electroweak.solution-a.full-code-forge-wave-6
class: report
authority: non-canonical
canonical_for: []
status: proposal
owner: repository-governance
version: 0.9.2a2
last_verified: 2026-08-31
---

# AETHER FORGE — Full Code Completion Manifest — Wave 6

## FORGE context compiler, loss-bounded distillation, ToolScript contracts, lowering, and sandbox policy

- Exact branch subject: `f242ced297216109736975376802f1e3dc4e29ce`.
- Backend FORGE only; frontend is excluded.
- This complement closes production integration omitted by waves 1–4.
- Code blocks contain complete affected modules or complete affected classes/functions so call sites can be changed without guessing signatures.
- Existing kernel invariants, authority, budgets, events, artifacts, and recovery remain authoritative.

## Required production delta

Add `forge-distill` as a registered context strategy over the existing compiler.
It must preserve the constitutional floor, task brief, active goal, hypothesis,
confirmed facts, rejected hypotheses, changed files, verification freshness,
unresolved blockers, child summaries, and artifact digests.  Old tool outputs
become artifact references rather than invented prose.  Add ToolScript as a
typed declarative program: no Python evaluation, shell source, imports, dynamic
tool discovery, direct filesystem handles, network handles, authority fields,
budget fields, or mutable runtime objects.  Each step lowers through ordinary
effect dispatch and therefore inherits kernel policy, capability checks,
reservations, settlement, events, receipts, and crash recovery.

## Exact edit map

1. Modify `agency/context/compaction.py`: register `forge-distill` and implement
   deterministic structured retention.
2. Modify `agency/context/compiler.py`: carry verification/evidence layers and
   record compaction provenance without importing runtime.
3. Modify `agency/context/layers.py`: define FORGE working-state block types.
4. Add `ports/toolscript.py`: immutable program, step, limits, and receipt port.
5. Add `runtime/forge/toolscript.py`: validator, template substitution, lowering,
   bounded result store, failure semantics, and resumable cursor.
6. Add `adapters/sandbox/toolscript.py`: optional isolated procedure adapter;
   adapter never imports kernel or agency.
7. Add manifest schemas for the small safe library: repository localization,
   test-failure compression, and API-impact search.
8. Add authority-expansion, filesystem-escape, shell-escape, result-size,
   timeout, crash-resume, and deterministic-replay falsifiers.

## ToolScript execution invariant

```text
validate immutable program
→ reserve declared maximum resources
→ lower exactly one step
→ normal authorize/execute/record path
→ bind receipt to program + step + workspace
→ artifactize large output
→ settle consumed resources
→ continue or return typed failure
```

## Complete affected code owners

### File: `vanguard/packages/agency/context/compiler.py`

**Repository path:** `vanguard/packages/agency/context/compiler.py`

```python
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

from ...domain.artifacts.skill_index import SkillCard, format_skill_index
from ...domain.canonicalisation.digest import digest_of
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
    "CONTEXT_POLICY_VERSION",
    "CacheBreakpointCeilingExceeded",
    "CompetencePriorRecorder",
    "ContextBudgetExceeded",
    "ContextCompiler",
]

#: How many decimal places of a prior survive to the ledger. Four is well past
#: the resolution any calibration set of this size can distinguish, and fixing
#: it makes the wire form canonical rather than host-float-dependent.
_PRIOR_PLACES = 4

#: Bumped whenever the *meaning* of `selection_identity()` changes, so a
#: reader can tell two records apart that happen to name the same strategy.
CONTEXT_POLICY_VERSION = "1"


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
        skill_cards: Sequence[SkillCard] = (),
        skill_index_ceiling: int = 4000,
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
        # `W12-B`: the skill index is stable within a task, so it rides `L3`
        # with the environment map -- named/described only, ceiling-bounded
        # (`≤4k` names+descriptions); bodies stay on disk behind `fs.read`.
        skill_text = format_skill_index(skill_cards, ceiling=skill_index_ceiling) if skill_cards else ""
        env_with_skills = "\n\n".join(part for part in (environment, skill_text) if part)
        self._prefix = self._render_prefix(system_core, tool_schemas, env_with_skills, source)
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

        # The candidate preimage, taken before `_fit` mutates the lists in
        # place. `_fit` is the only thing that can remove material, so this is
        # the last moment the un-compacted vector exists.
        candidates = self._prefix + tuple(task) + tuple(notes_blocks) + tuple(dialogue_blocks)
        candidate = digest_of([block.identity() for block in candidates])
        candidate_tokens = sum(block.token_estimate for block in candidates)

        elided, dropped = self._fit(floor, notes_blocks, dialogue_blocks)

        return CompiledContext(
            blocks=self._prefix + tuple(task) + tuple(notes_blocks) + tuple(dialogue_blocks),
            breakpoints=breakpoints,
            elided=tuple(elided),
            dropped=tuple(dropped),
            candidate_digest=candidate,
            candidate_tokens=candidate_tokens,
        )

    # -- provenance identity (pure; this object still cannot log) ---------

    def selection_identity(self) -> Mapping[str, Any]:
        """Who decided what this prompt contains, and under which parameters.

        `EVIDENCE.md`: *any variable that can materially affect a result MUST
        have observable identity and provenance*. Compaction strategy and its
        options are exactly such a variable, and they are resolved here at
        construction where nothing downstream can see them.

        This is a **read**, not a sink. The compiler stays a pure function of
        its arguments (`VG-03 §10`): a caller may ask what it is, and cannot
        make it behave differently by asking. Runtime owns writing the answer
        somewhere durable.
        """
        strategy = type(self._compaction_strategy).__name__
        parameters: dict[str, Any] = {
            "tokenCeiling": self._token_ceiling,
            "breakpointCeiling": self._breakpoint_ceiling,
        }
        # Only scalars: an option value that was itself a structure would put
        # unbounded (and possibly sensitive) material into a ledger fact.
        for key in sorted(self._compaction_options):
            value = self._compaction_options[key]
            if isinstance(value, (str, int, float, bool)) or value is None:
                parameters[str(key)] = value
        return {
            "policyId": f"agency.context-compiler/{strategy}",
            "policyVersion": CONTEXT_POLICY_VERSION,
            "parameters": parameters,
        }

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
```

### File: `vanguard/packages/agency/context/compaction.py`

**Repository path:** `vanguard/packages/agency/context/compaction.py`

```python
"""Compaction strategy protocol and registry (S8-B-02, VG-03 §10.3).

Provides pluggable dialogue compaction strategies selected by manifest context_policy
and frozen at composition time.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol, Sequence, runtime_checkable

from .layers import Block, Layer


def _receipt_for(block: Block) -> Block:
    """What `result_eviction` leaves behind: the fact, without the body.

    `VG-03 §10.3` — "keep that a file was read; drop the body once superseded".
    """
    return Block(
        layer=block.layer,
        source=block.source,
        label=block.label,
        text=f"[{block.label} from {block.source}: {block.byte_length} bytes elided after use]",
        evictable=False,
    )


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
            if not block.evictable:
                continue
            dialogue[index] = _receipt_for(block)
            elided.append(block.label)

        while total() > ceiling and dialogue:
            removed = dialogue.pop(0)
            dropped.append(removed.label)
            if removed.label in elided:
                elided.remove(removed.label)

        while total() > ceiling and notes:
            dropped.append(notes.pop(0).label)

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

        # 1. Truncate dialogue to the recency window limit
        while len(dialogue) > max_items:
            removed = dialogue.pop(0)
            dropped.append(removed.label)

        def total() -> int:
            return floor + sum(b.token_estimate for b in notes) + sum(b.token_estimate for b in dialogue)

        # 2. Result eviction over remaining dialogue
        for index, block in enumerate(dialogue):
            if total() <= ceiling:
                break
            if not block.evictable:
                continue
            dialogue[index] = _receipt_for(block)
            elided.append(block.label)

        # 3. If still exceeding ceiling, drop oldest dialogue items
        while total() > ceiling and dialogue:
            removed = dialogue.pop(0)
            dropped.append(removed.label)
            if removed.label in elided:
                elided.remove(removed.label)

        # 4. If still exceeding ceiling, drop oldest notes
        while total() > ceiling and notes:
            dropped.append(notes.pop(0).label)

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
            b = dialogue.pop(0)
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
                b = dialogue.pop(1)
                dropped.append(b.label)

        while total() > ceiling and notes:
            dropped.append(notes.pop(0).label)

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
```

### File: `vanguard/packages/agency/context/layers.py`

**Repository path:** `vanguard/packages/agency/context/layers.py`

```python
"""The layer model and the values rendered into it (`VG-03 §10.1`).

Values only: no clock, no sink, no authority. A block knows what it says, who
produced it and how much of the window it costs; it does not know whether it
will survive the budget, because that decision belongs to the assembly step
that can see the whole vector.

The five layers are ordered by **mutation rate**, not by importance, and that
is the whole design. `L1`–`L3` do not move within a run, so a provider can
cache them; `L4` moves per task; `L5` moves every turn. Anything appended to
`L1`–`L4` mid-run destroys every downstream cache hit (`VG-03 §10.2`), which
is why the compiler freezes the first three at composition rather than
offering a method that could append to them later.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping, Sequence

from ...domain.canonicalisation.digest import digest_of

__all__ = [
    "BREAKPOINT_LAYERS",
    "Block",
    "CompiledContext",
    "Fragment",
    "Layer",
    "PREFIX_LAYERS",
    "ROLE_FOR_LAYER",
    "estimate_tokens",
]


class Layer(str, Enum):
    """`VG-03 §10.1`. The value is the wire tag; the order is the render order."""

    SYSTEM = "L1"        # role + output contract       stable across the run
    TOOLS = "L2"         # tool schemas                 stable; rides the request
    ENVIRONMENT = "L3"   # conventions, retrieved priors stable within a task
    TASK = "L4"          # the brief and its notes      stable within a task
    DIALOGUE = "L5"      # turns, results, notes        mutates every turn


#: Render order. Iterating the enum would work today and break the moment
#: someone inserts a member, so the order is stated rather than inherited.
LAYER_ORDER: tuple[Layer, ...] = (
    Layer.SYSTEM, Layer.TOOLS, Layer.ENVIRONMENT, Layer.TASK, Layer.DIALOGUE,
)

#: The cached region. Byte-for-byte stable across every turn of a run, or the
#: provider charges full price for a prompt it has already seen.
PREFIX_LAYERS: tuple[Layer, ...] = (Layer.SYSTEM, Layer.TOOLS, Layer.ENVIRONMENT)

#: Where a cache breakpoint may sit (`VG-03 §10.2`). `L2` is inside the prefix
#: but carries no breakpoint of its own: it rides on the request and is bounded
#: by the `L3` boundary immediately after it. `L5` is absent on purpose — it is
#: the only layer permitted to mutate, and marking it stable is a lie to the
#: provider about what is stable.
BREAKPOINT_LAYERS: tuple[Layer, ...] = (Layer.SYSTEM, Layer.ENVIRONMENT, Layer.TASK)

#: One message per non-empty layer, and a role for each (`VG-03 §10.1`).
ROLE_FOR_LAYER: Mapping[Layer, str] = {
    Layer.SYSTEM: "system",
    Layer.TOOLS: "system",
    Layer.ENVIRONMENT: "system",
    Layer.TASK: "user",
    Layer.DIALOGUE: "user",
}


def estimate_tokens(text: str) -> int:
    """A character heuristic (~4 chars/token), deliberately local to `agency`.

    The budget this feeds is a *pre-flight* bound over block text; the provider
    adapter owns the real count, including its own message framing, and the two
    numbers answer different questions. `agency` may not import `adapters`
    (`ICD §7.4`), and a shared estimator in `domain` would imply the two are
    the same number. They are not: this one must be cheap and monotone, and it
    may only ever over-count relative to a tokeniser it cannot see.
    """
    if not text:
        return 0
    return max(1, (len(text) + 3) // 4)


@dataclass(frozen=True, slots=True)
class Fragment:
    """A candidate for `L4` or `L5`, before the budget has ruled on it.

    `evictable` marks a tool-result body: `result_eviction` keeps the fact that
    the result arrived and drops the body once superseded (`VG-03 §10.3`). A
    fragment that is not a result body is dropped whole or not at all, because
    half an operator note is a lie rather than a summary.
    """

    source: str
    label: str
    text: str
    evictable: bool = False


@dataclass(frozen=True, slots=True)
class Block:
    """One rendered block, tagged with its producing source (`REQ-CTX-001`)."""

    layer: Layer
    source: str
    label: str
    text: str
    evictable: bool = False

    @property
    def byte_length(self) -> int:
        return len(self.text.encode("utf-8"))

    @property
    def token_estimate(self) -> int:
        return estimate_tokens(self.text)

    @property
    def provenance(self) -> Mapping[str, Any]:
        """What a reviewer needs to attribute this block when it is the
        poisoned one: who produced it, which fragment it was, and its size."""
        return {
            "layer": self.layer.value,
            "source": self.source,
            "label": self.label,
            "bytes": self.byte_length,
            "tokens": self.token_estimate,
        }

    def identity(self) -> Mapping[str, Any]:
        """The digestible form. Text included — a prefix digest that ignored
        the text would report stability the provider does not see."""
        return {
            "layer": self.layer.value,
            "source": self.source,
            "label": self.label,
            "text": self.text,
        }


@dataclass(frozen=True, slots=True)
class CompiledContext:
    """One assembled prompt vector, and the record of what the budget cost.

    `elided` and `dropped` are disjoint: a fragment whose body was elided and
    which was then removed entirely is reported only as dropped, because the
    receipt that eviction promised to keep is no longer there either.
    """

    blocks: tuple[Block, ...]
    breakpoints: tuple[Layer, ...]
    elided: tuple[str, ...] = ()
    dropped: tuple[str, ...] = ()
    #: The vector as it stood *before* the budget ruled on it (`ADR-0096
    #: §14`). `digest` alone reports what was selected; without the candidate
    #: preimage nobody can tell a context that fit from one that was cut to
    #: fit, which is exactly the variable compaction provenance exists to
    #: attribute. Defaults to empty for callers constructing a context
    #: directly, so this stays additive.
    candidate_digest: str = ""
    #: Token cost of that same candidate vector. `total_tokens` is the cost
    #: after the budget ruled; the difference between the two is exactly what
    #: compaction removed, which no consumer can compute from `digest` alone.
    candidate_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return sum(block.token_estimate for block in self.blocks)

    @property
    def total_bytes(self) -> int:
        return sum(block.byte_length for block in self.blocks)

    @property
    def prefix_digest(self) -> str:
        """The cache-stability metric. Constant across a run, or the prefix
        moved and every downstream cache hit was lost (`VG-03 §10.2`)."""
        return digest_of([block.identity() for block in self.blocks
                          if block.layer in PREFIX_LAYERS])

    @property
    def digest(self) -> str:
        """The whole vector. What a competence prior is a prior *for*."""
        return digest_of([block.identity() for block in self.blocks])

    def layer_blocks(self, layer: Layer) -> tuple[Block, ...]:
        return tuple(block for block in self.blocks if block.layer is layer)

    def messages(self) -> tuple[Mapping[str, Any], ...]:
        """One message per non-empty layer, in order (`VG-03 §10.1`)."""
        rendered: list[Mapping[str, Any]] = []
        for layer in LAYER_ORDER:
            blocks = self.layer_blocks(layer)
            if not blocks:
                continue
            rendered.append({
                "layer": layer.value,
                "role": ROLE_FOR_LAYER[layer],
                "cacheBreakpoint": layer in self.breakpoints,
                "content": "\n\n".join(block.text for block in blocks),
                "provenance": tuple(block.provenance for block in blocks),
                # Provider adapters that need observation cardinality (the
                # stateless LAM is one) can consume the same immutable block
                # boundaries without guessing from rendered text.
                "fragments": tuple({"label": block.label, "content": block.text}
                                    for block in blocks),
            })
        return tuple(rendered)

    def bundle(self) -> Mapping[str, Any]:
        """The `ContextBundle` a `ModelPort` consumes (`ICD §4`).

        A mapping rather than this type, so no adapter has to import `agency`
        to call `propose` — the seam stays structural.

        `messages` carries `role` and `content` and nothing else, because a
        provider adapter forwards it to a wire API that rejects — or worse,
        silently retains — fields it does not know. The layer tags, breakpoints
        and provenance a caller needs for cache accounting are the *same*
        messages under `layers`, in the same order, so nothing is lost by
        sending the narrow form.
        """
        rendered = self.messages()
        return {
            "messages": tuple({"role": message["role"], "content": message["content"]}
                              for message in rendered),
            "layers": rendered,
            "promptDigest": self.digest,
            "prefixDigest": self.prefix_digest,
            "tokens": self.total_tokens,
            "elided": self.elided,
            "dropped": self.dropped,
        }


def blocks_of(layer: Layer, fragments: Sequence[Fragment]) -> tuple[Block, ...]:
    """Render fragments into a layer, preserving order."""
    return tuple(
        Block(layer=layer, source=fragment.source, label=fragment.label,
              text=fragment.text, evictable=fragment.evictable)
        for fragment in fragments
    )
```

### File: `vanguard/packages/ports/spi.py`

**Repository path:** `vanguard/packages/ports/spi.py`

```python
"""Frozen SPI protocols (SPEC §2.2, ADR-M0-03).

Owning contract: Wave-2 2.1-C. Moved from `layer0/spi/interfaces.py`
(ADR-0069, ADR-0072): the five Protocols are client conveniences of the wire,
not a sixth authority surface, so they land here as ports -- interfaces only,
importing only the generated wire types and the SPI `Result` ADT from
`domain/wire/`. No sixth SPI is added by this move (ADR-M0-03).
"""

from __future__ import annotations

from typing import ClassVar, Mapping, Protocol, Sequence, runtime_checkable

from ..domain.wire.result import Result
from ..domain.wire.types_gen import (
    ClaimRef,
    CompactionReport,
    ConsolidationReport,
    ContextBundle,
    EffectContext,
    EffectFailure,
    EffectRequest,
    EpisodeOutcome,
    EpisodeView,
    EvaluationRequestId,
    EvaluationSubject,
    GateDecision,
    Health,
    MemoryHit,
    MemoryId,
    MemoryQuery,
    MemoryRecord,
    OracleSpec,
    PreregistrationId,
    Proposal,
    Receipt,
    Reflection,
    Reservation,
    SignedVerdict,
    ToolSchema,
    TrajectoryRef,
)

__all__ = [
    "IContextManager",
    "IEvaluationGate",
    "IMemoryEngine",
    "IPlanner",
    "IToolkit",
]


@runtime_checkable
class IPlanner(Protocol):
    """Turn-level cognition. Inner planners emit Proposals."""

    spi_version: ClassVar[str]

    def plan(self, view: EpisodeView, budget: Reservation) -> Result[Proposal]: ...

    def observe(self, receipts: Sequence[Receipt], view: EpisodeView) -> None: ...

    def reflect(
        self, outcome: EpisodeOutcome, trajectory: TrajectoryRef,
    ) -> Result[Reflection | None]: ...


@runtime_checkable
class IContextManager(Protocol):
    """Prefix-stable prompt assembly. L1–L3 frozen at composition."""

    spi_version: ClassVar[str]

    def compile(self, view: EpisodeView, budget_tokens: int) -> Result[ContextBundle]: ...

    def ingest(self, receipts: Sequence[Receipt]) -> None: ...

    def compact(self, pressure: float) -> Result[CompactionReport]: ...

    def reground(self, error: EffectFailure) -> Result[ContextBundle]: ...


@runtime_checkable
class IToolkit(Protocol):
    """Effect adapters. Toolkits never see grants — only verified, leased work."""

    spi_version: ClassVar[str]

    def verbs(self) -> Mapping[str, ToolSchema]: ...

    def execute(self, request: EffectRequest, ctx: EffectContext) -> Result[Receipt]: ...

    def compensate(self, receipt: Receipt) -> Result[Receipt]: ...

    def health(self) -> Health: ...


@runtime_checkable
class IMemoryEngine(Protocol):
    """Episodic and semantic memory. Graph is a negotiated capability, not a sixth SPI."""

    spi_version: ClassVar[str]

    def write(self, record: MemoryRecord) -> Result[MemoryId]: ...

    def recall(self, query: MemoryQuery, budget_tokens: int) -> Result[tuple[MemoryHit, ...]]: ...

    def consolidate(self, since: int) -> Result[ConsolidationReport]: ...

    def invalidate(self, claim: ClaimRef, reason: str) -> Result[None]: ...

    def capabilities(self) -> frozenset[str]: ...


@runtime_checkable
class IEvaluationGate(Protocol):
    """Agent-side evidence plane. Requests judgment; never renders it."""

    spi_version: ClassVar[str]

    def request(self, subject: EvaluationSubject) -> Result[EvaluationRequestId]: ...

    def gate(self, verdicts: Sequence[SignedVerdict]) -> GateDecision: ...

    def preregister(self, oracle: OracleSpec) -> Result[PreregistrationId]: ...
```

## ToolScript standard library contracts

### `forge.repo_localize/1`

Inputs: issue text artifact, repository root selector, maximum results.
Steps: repository map lookup, lexical search, optional symbol lookup, canonical
deduplication, rank fusion.  Output: ordered file/symbol candidates with source
and score provenance.  Read-only.

### `forge.failure_compress/1`

Inputs: process receipt and stdout/stderr artifacts.  Steps: parse test runner,
normalize failure IDs, extract exception and top stack frames, bind workspace
digest.  Output: `FailureFingerprint` plus compact evidence references.
Read-only.

### `forge.api_impact/1`

Inputs: changed symbol or file.  Steps: symbol references, imports, dependency
edges, test ownership, git-neighborhood facts.  Output: affected symbols/files
and candidate targeted tests.  Read-only.

## Required focused tests

- compaction preserves every required structural field;
- compaction never fabricates an evidence digest;
- compaction with no removed block emits no compaction claim;
- unknown strategy fails closed;
- unknown ToolScript tool fails before dispatch;
- authority/budget keys fail before dispatch;
- executable outside allowlist fails before dispatch;
- each step consumes ordinary effect budget;
- maximum steps and output bytes are enforced;
- crash after step N resumes at N+1 without repeating a settled effect;
- program identity changes when normalized source or policy changes;
- equal programs and inputs produce equal ordered receipts.

## Minimal validation commands

```bash
python3 -m unittest test.agency.test_context_compiler -v
python3 -m unittest test.agency.test_structured_compaction -v
python3 -m unittest test.runtime.test_evidence_capture -v
python3 tools/linters/check_boundaries.py
python3 tools/linters/check_duplication.py --enforce
```
