"""Prompt Assembler (EVO-05, GTS-13C §7.4, ADR-0060).

Compiles layered context (L1–L5), memory fragments, and dialogue history for each turn,
delegating to ContextCompiler while preserving strict prefix stability.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Callable, Mapping, Sequence

from ..agency.context import (
    CompetencePriorRecorder,
    CompiledContext,
    ContextCompiler,
    Fragment,
    Layer,
)
from ..agency.provenance import ProvenanceSink
from ..ports.memory import MemoryBinding, require_retrieval_provenance
from .compose import TaskContext

__all__ = [
    "PromptAssembler",
]


def _memory_now(clock: Any) -> datetime:
    value = clock.now() if hasattr(clock, "now") else clock
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc)
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
        except ValueError as exc:
            raise PermissionError("memory authorization clock is invalid") from exc
    raise PermissionError("memory authorization clock is unavailable")


class PromptAssembler:
    """Assembles prompt vectors, memory fragments, and task context for inference."""

    def __init__(
        self,
        compiler: ContextCompiler,
        task: TaskContext,
        clock: Any,
        *,
        recorder: CompetencePriorRecorder | None = None,
        provenance: ProvenanceSink | None = None,
        memory: MemoryBinding | None = None,
    ) -> None:
        self._compiler = compiler
        self._task = task
        self._clock = clock
        self._recorder = recorder
        self._provenance = provenance
        self._memory = memory
        self._dialogue: list[Fragment] = []

    @property
    def compiler(self) -> ContextCompiler:
        return self._compiler

    @property
    def dialogue(self) -> Sequence[Fragment]:
        return tuple(self._dialogue)

    def note(self, label: str, source: str, text: str, *, evictable: bool = True) -> None:
        """Admit one turn's outcome to L5 dialogue history."""
        self._dialogue.append(Fragment(source=source, label=label, text=text, evictable=evictable))

    def tool_call(
        self,
        *,
        turn: int,
        name: str,
        args: Mapping[str, Any],
        thought: str = "",
    ) -> None:
        """Admit the assistant half of a provider tool exchange to L5.

        Keeping this as an ordinary fragment means the existing context
        ceiling and compaction policy account for tool arguments too. The
        structured wire role is reconstructed only after compilation, at the
        provider boundary.
        """
        payload = json.dumps(
            {
                "call_id": f"call_{turn}",
                "name": name,
                "args": dict(args),
                "thought": thought,
            },
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        self.note(
            label=f"tool-call-{turn}",
            source="assistant_tool_call",
            text=payload,
            evictable=False,
        )

    def memory_fragments(self) -> tuple[tuple[Fragment, ...], str]:
        """Retrieve authorized memory context immediately before compiling a turn."""
        if self._memory is None:
            return (), ""
        access = self._memory.authorize("read", now=_memory_now(self._clock))
        result = self._memory.port.recall(self._memory.query, access, self._memory.limit)
        selected = require_retrieval_provenance(result)
        if selected and len(result.texts) != len(selected):
            raise PermissionError("memory result has no complete materialized context")
        fragments = tuple(
            Fragment(
                source=f"memory:{result.provenance.policy_identity}",
                label=f"memory:{record_id}",
                text=text,
            )
            for record_id, text in zip(selected, result.texts)
            if isinstance(text, str) and text
        )
        if len(fragments) != len(selected):
            raise PermissionError("memory result contains invalid context text")
        return fragments, result.provenance.digest() if selected else ""

    def assemble(
        self,
        view: Mapping[str, Any],
        turn: int,
    ) -> tuple[dict[str, Any], CompiledContext]:
        """Compile L1-L5 layers and construct the provider ContextBundle."""
        mem_fragments, memory_digest = self.memory_fragments()
        compiled: CompiledContext = self._compiler.compile(
            brief=self._task.brief,
            dialogue=tuple(self._dialogue) + mem_fragments,
        )

        if self._recorder is not None and self._task.competence_prior is not None and turn == 0:
            self._recorder.record(
                episode_id=self._task.episode_id,
                run_id=self._task.run_id,
                principal=self._task.principal,
                prior=self._task.competence_prior,
                context=compiled,
            )

        bundle = dict(compiled.bundle())
        # L5 is a mutation layer, not a dialogue role. Render ordinary L5
        # notes as user messages while preserving assistant/tool alternation
        # for mediated effects. The prior implementation flattened every L5
        # fragment into one user message, leaving tool results orphaned from
        # the assistant calls that produced them.
        messages = [
            {"role": message["role"], "content": message["content"]}
            for message in compiled.messages()
            if message["layer"] != "L5"
        ]
        for block in compiled.layer_blocks(Layer.DIALOGUE):
            if block.source == "assistant_tool_call":
                try:
                    step = json.loads(block.text)
                except (TypeError, json.JSONDecodeError):
                    messages.append({"role": "user", "content": block.text})
                    continue
                messages.append({
                    "role": "assistant",
                    "content": step.get("thought") or None,
                    "tool_calls": [{
                        "id": step.get("call_id", "call_0"),
                        "type": "function",
                        "function": {
                            "name": step.get("name", ""),
                            "arguments": json.dumps(
                                step.get("args", {}), sort_keys=True,
                                separators=(",", ":"), ensure_ascii=False),
                        },
                    }],
                })
            elif block.source == "tool_result":
                messages.append({
                    "role": "tool",
                    "tool_call_id": f"call_{block.label.removeprefix('tool-result-')}",
                    "content": block.text,
                })
            else:
                messages.append({"role": "user", "content": block.text})
        bundle["messages"] = tuple(messages)
        if memory_digest:
            bundle["memoryRetrievalDigest"] = memory_digest

        digest = view.get("lastReceiptDigest")
        if digest:
            token = f"justifying_receipt={digest} progress={view.get('lastProgressSignal') or ''}"
            messages = list(bundle.get("messages") or ())
            messages.append({"role": "user", "content": token})
            bundle["messages"] = tuple(messages)
            bundle["lastReceiptDigest"] = digest

        self.record_selection_provenance(compiled, turn)
        return bundle, compiled

    def record_selection_provenance(self, compiled: CompiledContext, turn: int) -> None:
        """Record context-selection and compaction provenance for one turn."""
        if self._provenance is None or not hasattr(self._provenance, "record_context_selection"):
            return
        identity = self._compiler.selection_identity()
        selected = [block.label for block in compiled.blocks]
        layer_counts: dict[str, int] = {}
        for block in compiled.blocks:
            key = block.layer.value
            layer_counts[key] = layer_counts.get(key, 0) + block.token_estimate
        self._provenance.record_context_selection(
            identity=identity,
            candidate_digest=compiled.candidate_digest,
            selected_digest=compiled.digest,
            prefix_digest=compiled.prefix_digest,
            selected=selected,
            dropped=compiled.dropped,
            elided=compiled.elided,
            tokens=compiled.total_tokens,
            layer_counts=layer_counts,
            turn=turn,
        )
        self._provenance.record_compaction(
            identity=identity,
            input_digest=compiled.candidate_digest,
            output_digest=compiled.digest,
            dropped=compiled.dropped,
            elided=compiled.elided,
            tokens_before=compiled.candidate_tokens,
            tokens_after=compiled.total_tokens,
            turn=turn,
        )
