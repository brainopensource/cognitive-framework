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
from ...domain.task_state import Evidence, MemoryView, critical_state
from ...kernel import Event
from .compaction import CompactionStrategy, resolve_compaction_strategy
from .distiller import distill_tool_output, verification_receipt_from
from .layers import (
    BREAKPOINT_LAYERS,
    CAPABILITY_PREFIX_CEILING,
    GOAL_ECHO_SOURCE,
    NEWEST_INTERACTION_SOURCE,
    PINNED_L4_SOURCES,
    Block,
    CompiledContext,
    ContextBudget,
    Fragment,
    Interaction,
    Layer,
    blocks_of,
    estimate_tokens,
)

__all__ = [
    "CONTEXT_POLICY_VERSION",
    "CacheBreakpointCeilingExceeded",
    "CapabilityPrefixExceeded",
    "CompetencePriorRecorder",
    "ContextBudget",
    "ContextBudgetExceeded",
    "ContextCompiler",
    "Interaction",
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


class CapabilityPrefixExceeded(ValueError):
    """The capability-card prefix is over its character ceiling (`NT-C05`).

    A `ValueError`, because every existing caller that guards the ceiling
    catches that; a distinct type, because "the cards are too long" and "the
    window is too small" are different repairs and a caller that cannot tell
    them apart will attempt the wrong one.
    """
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
        capability_cards: str = "",
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
        # `NT-C05`: the bound is characters, and it is checked here rather
        # than against the token budget. A route whose tokenizer is generous
        # must not be able to enlarge the injected capability prefix.
        if len(capability_cards) > CAPABILITY_PREFIX_CEILING:
            raise CapabilityPrefixExceeded(
                f"capability prefix is {len(capability_cards)} characters "
                f"against a ceiling of {CAPABILITY_PREFIX_CEILING} (NT-C05)")
        self._token_ceiling = token_ceiling
        self._breakpoint_ceiling = breakpoint_ceiling
        self._capability_cards = capability_cards
        # `W12-B`: the skill index is stable within a task, so it rides `L3`
        # with the environment map -- named/described only, ceiling-bounded
        # (`≤4k` names+descriptions); bodies stay on disk behind `fs.read`.
        skill_text = format_skill_index(skill_cards, ceiling=skill_index_ceiling) if skill_cards else ""
        env_with_skills = "\n\n".join(part for part in (environment, skill_text) if part)
        self._prefix = self._render_prefix(
            system_core, capability_cards, tool_schemas, env_with_skills, source)
        self._prefix_tokens = sum(block.token_estimate for block in self._prefix)

        if compaction_strategy is not None:
            self._compaction_strategy = compaction_strategy
            self._compaction_options = context_policy if isinstance(context_policy, Mapping) else {}
        else:
            strat, opts = resolve_compaction_strategy(context_policy)
            self._compaction_strategy = strat
            self._compaction_options = opts

        # `NT-C01`: the epoch is taken once, here, over the frozen bytes and
        # the policy that produced them. Computing it per call would let a
        # temporarily narrowed ceiling (`compile_packet` does exactly that)
        # report a different epoch for an unchanged composition.
        self._composition_epoch = digest_of({
            "prefix": [block.identity() for block in self._prefix],
            "policy": self._policy_identity(),
        })

    # -- composition-time rendering -------------------------------------

    @staticmethod
    def _render_prefix(system_core: str, capability_cards: str,
                       tool_schemas: Sequence[Mapping[str, Any]],
                       environment: str, source: str) -> tuple[Block, ...]:
        """The cached region, rendered once.

        Four declared regions in one fixed order (`NT-C01`): system
        instructions, the capability-card prefix, the ordered canonical tool
        schemas, and the environment/composition contract.

        Tool schemas go through a sorted-key JSON dump rather than `str()` so
        that two composition roots naming the same tools produce the same
        bytes. A prefix whose stability depended on dictionary insertion order
        would be stable in tests and unstable in production.
        """
        rendered: list[Block] = []
        if system_core:
            rendered.append(Block(layer=Layer.SYSTEM, source=source,
                                  label="system-core", text=system_core))
        if capability_cards:
            # The cards describe what the agent may do. They belong with the
            # instructions that frame every turn, not with the turn-local
            # material, or the first card injection would move the prefix.
            rendered.append(Block(layer=Layer.SYSTEM, source=source,
                                  label="capability-cards", text=capability_cards))
        if tool_schemas:
            ordered = sorted(
                (dict(schema) for schema in tool_schemas),
                key=lambda schema: str(schema.get("name") or schema.get("verb") or ""),
            )
            payload = json.dumps(ordered, sort_keys=True, separators=(",", ":"),
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
        goal_echo: str | None = None,
    ) -> CompiledContext:
        """Assemble one prompt vector for one turn.

        `brief` is the immutable task statement (`VG-03 §10.5`). `notes` is the
        rest of `L4`. `dialogue` is `L5`, oldest first. FEATURE_SPEC tiers 0–1
        (settled invariants, falsified hypotheses, dead ends) are L4 head and
        are not reachable by the budget; pressure caps L5 only.

        `goal_echo` is the `L5` trailing echo (`NT-C05`). Passed explicitly it
        is rendered **whole**, after every dynamic fragment: the objective and
        its constraints are the one thing a turn may not lose, and a truncated
        restatement of a constraint is a different constraint. With no echo
        supplied the legacy short restatement of the brief is kept, because a
        brief is frequently a serialized structure whose head is not a goal.
        """
        task = ((Block(layer=Layer.TASK, source="operator", label="brief", text=brief),)
                if brief else ())
        pinned_notes, flexible_notes = _partition_l4_notes(notes)
        pinned_blocks = list(blocks_of(Layer.TASK, pinned_notes))
        notes_blocks = list(blocks_of(Layer.TASK, flexible_notes))
        dialogue_blocks = list(blocks_of(Layer.DIALOGUE, dialogue))
        echo = goal_echo if goal_echo is not None else (
            f"Goal: {brief if len(brief) <= 240 else brief[:237] + '...'}" if brief else None)
        if echo:
            dialogue_blocks.append(Block(
                layer=Layer.DIALOGUE,
                source=GOAL_ECHO_SOURCE,
                label="goal-echo",
                text=echo,
                evictable=False,
            ))

        breakpoints = self._breakpoints(task_present=bool(task or pinned_blocks or notes_blocks))
        if len(breakpoints) > self._breakpoint_ceiling:
            raise CacheBreakpointCeilingExceeded(
                f"{len(breakpoints)} breakpoints exceeds the ceiling of "
                f"{self._breakpoint_ceiling} (VG-03 §10.2)")

        floor = (self._prefix_tokens
                 + sum(block.token_estimate for block in task)
                 + sum(block.token_estimate for block in pinned_blocks))
        if floor > self._token_ceiling:
            raise ContextBudgetExceeded(
                f"L1-L3 plus the brief and pinned L4 cost {floor} tokens against a "
                f"ceiling of {self._token_ceiling}; none of them may be truncated")

        # The candidate preimage, taken before `_fit` mutates the lists in
        # place. `_fit` is the only thing that can remove material, so this is
        # the last moment the un-compacted vector exists.
        candidates = (self._prefix + tuple(task) + tuple(pinned_blocks)
                      + tuple(notes_blocks) + tuple(dialogue_blocks))
        candidate = digest_of([block.identity() for block in candidates])
        candidate_tokens = sum(block.token_estimate for block in candidates)

        elided, dropped = self._fit(floor, notes_blocks, dialogue_blocks)

        return CompiledContext(
            blocks=(self._prefix + tuple(task) + tuple(pinned_blocks)
                    + tuple(notes_blocks) + tuple(dialogue_blocks)),
            breakpoints=breakpoints,
            elided=tuple(elided),
            dropped=tuple(dropped),
            candidate_digest=candidate,
            candidate_tokens=candidate_tokens,
        )

    # -- provenance identity (pure; this object still cannot log) ---------

    @property
    def composition_epoch(self) -> str:
        """The identity of the frozen region (`NT-C01`).

        It is a function of the system instructions, the capability-card
        prefix, the ordered tool schemas, the environment contract and the
        context policy — and of nothing dynamic. Two runs sharing an epoch
        share prefix bytes; a changed epoch is the record that an old freeze,
        and any cache identity derived from it, may not be reused.
        """
        return self._composition_epoch

    def _policy_identity(self) -> Mapping[str, Any]:
        """Strategy, version and scalar options — the policy half of the epoch."""
        parameters: dict[str, Any] = {
            "tokenCeiling": self._token_ceiling,
            "breakpointCeiling": self._breakpoint_ceiling,
            "capabilityPrefixChars": len(self._capability_cards),
        }
        # Only scalars: an option value that was itself a structure would put
        # unbounded (and possibly sensitive) material into a ledger fact.
        for key in sorted(self._compaction_options):
            value = self._compaction_options[key]
            if isinstance(value, (str, int, float, bool)) or value is None:
                parameters[str(key)] = value
        return {
            "policyId": f"agency.context-compiler/{type(self._compaction_strategy).__name__}",
            "policyVersion": CONTEXT_POLICY_VERSION,
            "parameters": parameters,
        }

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
        return {**self._policy_identity(), "compositionEpoch": self._composition_epoch}

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

    def compile_packet(
        self,
        view: MemoryView,
        subject: str,
        turns: Sequence[Interaction] = (),
        *,
        budget: ContextBudget | None = None,
        capability_cards: str = "",
    ) -> CompiledContext:
        """NT-C01–C06 selection on the existing compiler. No inference.

        The order of operations is the contract, not an implementation
        detail. Cardinality and body size are bounded *before* the budget is
        consulted, because a selection that first assembles an unbounded
        vector has already paid for the material it is about to throw away.
        Eviction then follows `NT-C04` exactly: stale evidence, bodies,
        low-priority evidence, oldest complete interactions — and never the
        newest complete interaction, which is the state the next action starts
        from. Mandatory state may sit above the low watermark; nothing may sit
        above hard usable, and an irreducible vector raises
        `CONTEXT_BUDGET_EXCEEDED` here rather than being posted and truncated
        by a provider.
        """
        if not isinstance(view, MemoryView):
            raise TypeError("compile_packet requires a MemoryView")
        if not str(subject).strip():
            raise ValueError("subject digest is required")
        if len(capability_cards) > CAPABILITY_PREFIX_CEILING:
            raise CapabilityPrefixExceeded(
                f"capability prefix is {len(capability_cards)} characters "
                f"against a ceiling of {CAPABILITY_PREFIX_CEILING} (NT-C05)")
        if capability_cards and capability_cards != self._capability_cards:
            # `NT-C01`: the prefix is frozen for the composition epoch. A
            # per-call card set that differed from the frozen one would move
            # L1 mid-run, which is the failure the freeze exists to prevent.
            raise CapabilityPrefixExceeded(
                "the capability prefix is frozen at composition; a per-call "
                "prefix cannot replace it (NT-C01)")
        if len({turn.key for turn in turns}) != len(turns):
            raise ValueError("duplicate interaction key")
        policy = budget or ContextBudget(window=self._token_ceiling)
        usable = policy.usable
        omissions: list[tuple[str, str]] = []
        #: label -> the text this fragment collapses to once its body goes.
        receipts: dict[str, str] = {}

        notes = self._select_evidence(view, subject, policy, omissions, receipts)
        dialogue = self._select_interactions(turns, subject, policy, omissions, receipts)

        brief = json.dumps(
            critical_state(view), sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        )
        echo = _goal_echo_text(view)

        # The floor is everything eviction may not touch: the frozen prefix,
        # the mandatory-state brief and the trailing goal echo.
        floor = (self._prefix_tokens + estimate_tokens(brief) + estimate_tokens(echo))
        self._fit_packet(floor=floor, notes=notes, dialogue=dialogue,
                         policy=policy, omissions=omissions, receipts=receipts)

        previous_ceiling = self._token_ceiling
        self._token_ceiling = usable
        try:
            compiled = self.compile(brief=brief, notes=tuple(notes),
                                    dialogue=tuple(dialogue), goal_echo=echo)
        except ContextBudgetExceeded as exc:
            raise ContextBudgetExceeded(f"CONTEXT_BUDGET_EXCEEDED: {exc}") from exc
        finally:
            self._token_ceiling = previous_ceiling
        if compiled.total_tokens > usable:
            raise ContextBudgetExceeded(
                f"CONTEXT_BUDGET_EXCEEDED: irreducible state costs "
                f"{compiled.total_tokens} tokens against usable {usable}"
            )
        already = set(omissions)
        note_keys = {item.label for item in notes}
        residual = [
            (label, "evidence_dropped" if label in note_keys else "interaction_dropped")
            for label in compiled.dropped
            if (label, "evidence_dropped" if label in note_keys else "interaction_dropped")
            not in already
        ]
        ledger = tuple(omissions) + tuple(residual)
        # `elided` and `dropped` report the same events the omission ledger
        # records, so a consumer that reads only the compiled context sees the
        # packet-level evictions too, not merely the ones the compaction
        # strategy happened to perform. They stay disjoint: material that was
        # elided and then dropped has no receipt left to report.
        dropped = _unique(
            _labels(ledger, ("evidence_dropped", "interaction_dropped")) + compiled.dropped)
        elided = _unique(tuple(
            label for label in _labels(ledger, ("body_elided",)) + compiled.elided
            if label not in dropped))
        return CompiledContext(
            blocks=compiled.blocks,
            breakpoints=compiled.breakpoints,
            elided=elided,
            dropped=dropped,
            candidate_digest=compiled.candidate_digest,
            candidate_tokens=compiled.candidate_tokens,
            omissions=ledger,
        )

    # -- bounded selection (NT-C04 step 0: bound before you select) -------

    def _select_evidence(
        self,
        view: MemoryView,
        subject: str,
        policy: ContextBudget,
        omissions: list[tuple[str, str]],
        receipts: dict[str, str],
    ) -> list[Fragment]:
        """Fresh, subject-bound, cardinality-capped evidence, oldest first."""
        fresh: list[Evidence] = []
        for evidence in view.evidence:
            if evidence.subject != subject:
                # `NT-C04` step one. Stale evidence is removed, not summarised:
                # a finding about another subject is not weaker evidence about
                # this one, it is evidence about something else.
                omissions.append((evidence.key, "stale"))
                continue
            fresh.append(evidence)
        if len(fresh) > policy.max_items:
            for evidence in fresh[:-policy.max_items]:
                omissions.append((evidence.key, "evidence_dropped"))
            fresh = fresh[-policy.max_items:]

        selected: list[Fragment] = []
        for evidence in fresh:
            body = evidence.body
            full = evidence.finding if not body else f"{evidence.finding}\n{body}"
            receipt, text, elided = _bound_result(
                label=evidence.key, header=evidence.finding,
                body=body or evidence.finding, full=full,
                artifact=evidence.artifact, subject=subject, policy=policy, fresh=True,
            )
            receipts[evidence.key] = receipt
            if elided:
                omissions.append((evidence.key, "body_elided"))
            selected.append(Fragment(source="evidence", label=evidence.key,
                                     text=text, evictable=True))
        return selected

    def _select_interactions(
        self,
        turns: Sequence[Interaction],
        subject: str,
        policy: ContextBudget,
        omissions: list[tuple[str, str]],
        receipts: dict[str, str],
    ) -> list[Fragment]:
        """Complete action/result units only, cardinality-capped, oldest first.

        `NT-C04`: an action whose result never arrived is an orphan tool call.
        Retaining one invites the model to treat a dispatched effect as a
        settled one, so the pair is admitted together or not at all.
        """
        complete: list[Interaction] = []
        for turn in turns:
            if not turn.result.strip():
                omissions.append((turn.key, "incomplete_interaction"))
                continue
            complete.append(turn)
        if len(complete) > policy.max_items:
            for turn in complete[:-policy.max_items]:
                omissions.append((turn.key, "interaction_dropped"))
            complete = complete[-policy.max_items:]

        selected: list[Fragment] = []
        for index, turn in enumerate(complete):
            full = f"{turn.action}\n{turn.result}"
            receipt, text, elided = _bound_result(
                label=turn.key, header=turn.action, body=turn.result, full=full,
                artifact=turn.artifact, subject=subject, policy=policy, fresh=True,
            )
            receipts[turn.key] = receipt
            if elided:
                omissions.append((turn.key, "body_elided"))
            newest = index == len(complete) - 1
            selected.append(Fragment(
                source=NEWEST_INTERACTION_SOURCE if newest else "interaction",
                label=turn.key, text=text, evictable=True,
            ))
        return selected

    # -- NT-C04 eviction order -------------------------------------------

    def _fit_packet(
        self,
        *,
        floor: int,
        notes: list[Fragment],
        dialogue: list[Fragment],
        policy: ContextBudget,
        omissions: list[tuple[str, str]],
        receipts: dict[str, str],
    ) -> None:
        """Bring a packet to the low watermark in the declared order.

        Hysteresis (`NT-C04`): nothing is removed until the candidate crosses
        the high watermark, and once it does the target is the low watermark —
        compacting to exactly the high watermark would compact again next turn
        and every turn after it. What cannot be reduced is left above low; the
        caller still refuses anything above hard usable.
        """
        def cost() -> int:
            return (floor
                    + sum(estimate_tokens(item.text) for item in notes)
                    + sum(estimate_tokens(item.text) for item in dialogue))

        if cost() <= policy.high_watermark:
            return
        target = policy.low_watermark

        # Step two: elide bodies into receipts, lowest priority first.
        # Evidence outranks nothing; the transcript outranks it only in
        # recency, so evidence bodies go before interaction bodies.
        for sequence in (notes, dialogue):
            for index, item in enumerate(sequence):
                if cost() <= target:
                    return
                receipt = receipts.get(item.label)
                if receipt is None or estimate_tokens(receipt) >= estimate_tokens(item.text):
                    # Eliding a body into a receipt that costs as much as the
                    # body buys nothing and loses the body.
                    continue
                sequence[index] = Fragment(source=item.source, label=item.label,
                                           text=receipt, evictable=item.evictable)
                omissions.append((item.label, "body_elided"))

        # Step three: drop low-priority evidence, oldest first.
        while cost() > target and notes:
            omissions.append((notes.pop(0).label, "evidence_dropped"))

        # Step four: drop the oldest complete interactions. The newest one is
        # never a candidate: its body may already be a receipt, but the fact
        # that it happened is the state the next action starts from.
        while cost() > target and len(dialogue) > 1:
            omissions.append((dialogue.pop(0).label, "interaction_dropped"))


def _is_pinned_l4(fragment: Fragment) -> bool:
    return fragment.source in PINNED_L4_SOURCES


def _partition_l4_notes(
    notes: Sequence[Fragment],
) -> tuple[tuple[Fragment, ...], tuple[Fragment, ...]]:
    """FEATURE_SPEC: invariants then dead ends at L4 head; only the rest may drop."""
    invariants: list[Fragment] = []
    negatives: list[Fragment] = []
    other_pinned: list[Fragment] = []
    flexible: list[Fragment] = []
    for note in notes:
        pinned = Fragment(source=note.source, label=note.label, text=note.text, evictable=False)
        if note.source == "settled-invariant":
            invariants.append(pinned)
        elif note.source in {"falsified-hypothesis", "dead-end"}:
            negatives.append(pinned)
        elif _is_pinned_l4(note):
            other_pinned.append(pinned)
        else:
            flexible.append(note)
    return tuple(invariants + negatives + other_pinned), tuple(flexible)


def _labels(ledger: Sequence[tuple[str, str]], reasons: Sequence[str]) -> tuple[str, ...]:
    return tuple(label for label, reason in ledger if reason in reasons)


def _unique(labels: Sequence[str]) -> tuple[str, ...]:
    """Order-preserving deduplication: one event, reported once."""
    seen: set[str] = set()
    ordered: list[str] = []
    for label in labels:
        if label not in seen:
            seen.add(label)
            ordered.append(label)
    return tuple(ordered)


def _goal_echo_text(view: MemoryView) -> str:
    """The complete objective and constraints, for the `L5` tail (`NT-C05`).

    Rendered from the durable task state rather than from any message, so no
    quantity of untrusted tool output can become the operative goal: the last
    thing the model reads is the thing the operator asked for.
    """
    task = view.task
    lines = [f"Objective: {task.objective}"]
    if task.constraints:
        lines.append("Constraints:")
        lines.extend(f"- {constraint}" for constraint in task.constraints)
    return "\n".join(lines)


def _bound_result(
    *,
    label: str,
    header: str,
    body: str,
    full: str,
    artifact: str,
    subject: str,
    policy: ContextBudget,
    fresh: bool,
) -> tuple[str, str, bool]:
    """Bound one result at the door, and say what it collapses to later.

    Three values: the *eviction receipt* (`NT-C04` step two leaves this behind
    when the body goes), the text admitted now, and whether admitting it
    already omitted the raw body.

    A verification body collapses immediately, whatever its size. What the
    working state needs from a suite run is which command ran, where, against
    which subject, how many tests it collected and executed, with which exit
    status and how fresh (`NT-C05`) — never the passing log, which is the
    largest and least informative part of it. An ordinary body is kept
    verbatim until it crosses the declared byte bound, and is then capped
    head/tail against its full preimage digest.
    """
    verification = verification_receipt_from(
        body, subject=subject, artifact=artifact, fresh=fresh)
    if verification is not None:
        receipt = f"{header}\n{verification.render()}"
        return receipt, receipt, estimate_tokens(receipt) < estimate_tokens(full)

    # The eviction receipt is identity, not content: after eviction the body
    # is reachable by artifact and nothing else of it is claimed.
    receipt = (f"{header}\nartifact={artifact}\n"
               f"[{label}: {len(body.encode('utf-8'))} bytes elided after use]")
    if len(full.encode("utf-8")) > policy.max_body_bytes:
        distilled = distill_tool_output(body, cap_chars=policy.max_body_bytes)
        return receipt, f"{header}\nartifact={artifact}\n{distilled.compact_text}", True
    return receipt, full, False


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
__all__ += ["Block", "CompiledContext", "ContextBudget", "Fragment", "Interaction", "Layer", "estimate_tokens"]
