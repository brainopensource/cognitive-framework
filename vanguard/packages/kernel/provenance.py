"""The authority predicate and the span accumulator (`05 §5`).

> Untrusted content may inform work; it may never authorise it.

A violation occurs when a request widens capability **and** any span
justifying it carries an untrusted label. Both operands have failed silently
in this project's history, and each has a must-fail test aimed at it:

* the widening operand as a hardcoded constant (`MF-KRN-001`, see
  `classifier.py`);
* the span operand reset between turns, which makes the untrusted branch
  unreachable dead code (`MF-KRN-002`, this module).

`K-33` is why `Accumulation` is a type rather than a list passed around: the
span set at turn *n* is the union of turn *n−1*'s spans, the model reply's
spans and the results' spans. Monotone, never reset within a run. Making the
union the *only* public mutation means a reset is not something a caller can
express by accident — it has to be written deliberately, which is exactly what
the broken counterpart does.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .model import Span, Trust

__all__ = ["Accumulation", "authority_violation", "combine", "weakest"]


def combine(*trusts: Trust) -> Trust:
    """`K-28`: labels never improve. The result is the weakest input."""
    if not trusts:
        return Trust.OPERATOR
    return max(trusts, key=lambda trust: trust.rank)


def weakest(spans: Iterable[Span]) -> Trust:
    """The weakest label present, or `OPERATOR` for an empty set."""
    return combine(*[span.trust for span in spans])


class Accumulation:
    """Monotone justifying-span accumulation for one run (`K-33`).

    Spans only ever enter. There is no removal, no replacement and no reset;
    a fresh run constructs a fresh accumulation, and a child operator's
    accumulation is separate — its *return value* re-enters the parent as
    untrusted-derived at minimum (`K-29`).
    """

    __slots__ = ("_spans", "_order", "_turn")

    def __init__(self, spans: Iterable[Span] = ()) -> None:
        self._spans: dict[str, Span] = {}
        self._order: list[str] = []
        self._turn = 0
        self.extend(spans)

    def extend(self, spans: Iterable[Span]) -> "Accumulation":
        """Union in more spans. The only mutation this type offers."""
        for span in spans:
            if span.span_id in self._spans:
                # A span may be re-observed; `K-28` means the recorded label
                # can only get weaker, never stronger, on re-entry.
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
        """`K-33`. Turn *n* = turn *n−1* ∪ reply(*n−1*) ∪ results(*n−1*).

        Tool output is untrusted at birth and is fed back to the model, so
        from the second round onward it can steer a tool call. Carrying the
        previous set forward is what keeps the untrusted branch reachable.
        """
        self._turn += 1
        self.extend(reply_spans)
        self.extend(result_spans)
        return self

    def child_return(self, value_spans: Iterable[Span]) -> "Accumulation":
        """A child operator's return value enters as untrusted-derived at
        minimum (`K-33`), whatever the child believed about it."""
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
    """Why the predicate decided what it decided. Denials must be explainable."""

    violated: bool
    widens_capability: bool
    untrusted_span_ids: tuple[str, ...]


def authority_violation(
    spans: Iterable[Span], *, widens_capability: bool
) -> PredicateResult:
    """Clause S1(e), evaluated at S5. Violation is `F-09`.

    Both operands are required: untrusted spans alone are fine (that is
    untrusted content informing work), and widening alone is fine (that is an
    ordinary privileged request). Only the conjunction is a violation.
    """
    untrusted = tuple(span.span_id for span in spans if span.trust.is_untrusted)
    return PredicateResult(
        violated=bool(widens_capability and untrusted),
        widens_capability=widens_capability,
        untrusted_span_ids=untrusted,
    )
