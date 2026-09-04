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
    "PINNED_L4_SOURCES",
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

#: FEATURE_SPEC tiers 0–1 on L4. Compaction must not evict these sources.
PINNED_L4_SOURCES: frozenset[str] = frozenset({
    "settled-invariant",
    "falsified-hypothesis",
    "dead-end",
})


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
