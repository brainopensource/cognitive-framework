"""The authority predicate and the span accumulator."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .model import Span, Trust

__all__ = ["Accumulation", "authority_violation", "combine", "weakest"]


def combine(*trusts: Trust) -> Trust:
    if not trusts:
        return Trust.OPERATOR
    return max(trusts, key=lambda trust: trust.rank)


def weakest(spans: Iterable[Span]) -> Trust:
    return combine(*[span.trust for span in spans])


class Accumulation:
    __slots__ = ("_spans", "_order", "_turn")

    def __init__(self, spans: Iterable[Span] = ()) -> None:
        self._spans: dict[str, Span] = {}
        self._order: list[str] = []
        self._turn = 0
        self.extend(spans)

    def extend(self, spans: Iterable[Span]) -> "Accumulation":
        for span in spans:
            if span.span_id in self._spans:
                existing = self._spans[span.span_id]
                if span.trust.rank > existing.trust.rank:
                    self._spans[span.span_id] = span
                continue
            self._spans[span.span_id] = span
            self._order.append(span.span_id)
        return self

    def advance_turn(
        self,
        *,
        reply_spans: Iterable[Span] = (),
        result_spans: Iterable[Span] = (),
    ) -> "Accumulation":
        self._turn += 1
        self.extend(reply_spans)
        self.extend(result_spans)
        return self

    def child_return(self, value_spans: Iterable[Span]) -> "Accumulation":
        self.extend(
            Span(span.span_id, combine(span.trust, Trust.UNTRUSTED_DERIVED), span.source_class)
            for span in value_spans
        )
        return self

    @property
    def turn(self) -> int:
        return self._turn

    @property
    def spans(self) -> tuple[Span, ...]:
        return tuple(self._spans[span_id] for span_id in self._order)

    @property
    def weakest_trust(self) -> Trust:
        return weakest(self.spans)

    @property
    def has_untrusted(self) -> bool:
        return any(span.trust.is_untrusted for span in self.spans)

    def __len__(self) -> int:
        return len(self._spans)


@dataclass(frozen=True, slots=True)
class PredicateResult:
    violated: bool
    widens_capability: bool
    untrusted_span_ids: tuple[str, ...]


def authority_violation(
    spans: Iterable[Span], *, widens_capability: bool
) -> PredicateResult:
    untrusted = tuple(span.span_id for span in spans if span.trust.is_untrusted)
    return PredicateResult(
        violated=bool(widens_capability and untrusted),
        widens_capability=widens_capability,
        untrusted_span_ids=untrusted,
    )
