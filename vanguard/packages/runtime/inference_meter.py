"""Inference accounting: the model call settles against the same `Governor`.

Why this module exists
----------------------
Every privileged *effect* traverses the kernel's S0-S12 dispatch and is
reserved, committed and released against `kernel.budget.Governor`. The *model
call* did not. It was invoked directly (`agency/episode/engine.py`, via the
runtime's layered operator) and its token usage and cost were recorded as
diagnostics on the proposal event -- telemetry, never a debit.

So the dominant cost of a coding episode sat outside the budget algebra the
architecture is built on. Measured on the product path through the public
entrypoint, a `balanced` run declaring a `$0.15 / 40,000 token` ceiling
reported `$0.50` and `78,000` tokens and terminated on the *turn* bound: the
other two declared ceilings were decorative. `RUN-09(8)` names the escalation
half of that gap; this is the base case, which needs no escalation to occur.

What it does and does not do
----------------------------
This meter reserves before the provider call and settles after it, against the
same governor the kernel uses, so one aggregate budget covers effects and
inference alike (`RUN-10`: *one aggregate resource budget across escalation*).

It is deliberately **not** in the kernel. The TCB stays domain-blind and its
LOC ceiling is untouched: this is ordinary runtime composition around a
`ModelPort`, the same shape as any other adapter decoration.

Honesty rules it inherits from the spec
---------------------------------------
- **Unknown cost is unsettled, never zero** (`RUN-12`). An unpriced route
  reserves no USD and records `unpriced`; it does not pretend the call was free.
- **A reservation is a ceiling, not consent.** Denial is fail-closed and typed;
  it never degrades into "proceed and hope".
- **Overruns are charged, not clamped** -- `Governor.commit` already refuses to
  clamp a negative settlement (`MF-KRN-007`), and this module does not
  re-introduce the clamp on the way in.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from ..kernel.budget import BudgetDenied, Governor, Lease

__all__ = [
    "InferenceMeter",
    "InferenceReservation",
    "InferenceSettlement",
    "INFERENCE_DENIED_KIND",
]

#: The typed failure kind a denied inference reservation returns. The episode
#: engine maps it to `RunTermination.BUDGET_EXHAUSTED`; it must never be
#: collapsed into `instrument_error`, which would move a spend refusal into the
#: model-failure bucket and corrupt the missingness taxonomy (`DIR-D2`).
INFERENCE_DENIED_KIND = "budget_exhausted"

#: Completion ceiling assumed when a turn's sampling declares none. This is a
#: *reservation* bound, refunded on commit, so an over-estimate costs headroom
#: for one call and nothing at all afterwards. Under-estimating would let a
#: long completion overrun the ceiling it was supposed to bound.
DEFAULT_MAX_COMPLETION_TOKENS = 4096


@dataclass(frozen=True, slots=True)
class InferenceReservation:
    """What one turn's provider call was allowed to consume."""

    lease: Lease
    prompt_tokens: int
    max_completion_tokens: int
    usd_micros: int
    priced: bool

    @property
    def tokens(self) -> int:
        return self.prompt_tokens + self.max_completion_tokens


@dataclass(frozen=True, slots=True)
class InferenceSettlement:
    """What it actually consumed, and what remained unknown."""

    tokens: int
    usd_micros: int
    unpriced: bool
    usage_observed: bool
    settlement: Mapping[str, int] = field(default_factory=dict)

    def as_payload(self) -> Mapping[str, Any]:
        """Durable shape. Absence stays absent; it is never rendered as zero."""
        payload: dict[str, Any] = {
            "tokens": self.tokens,
            "usageObserved": self.usage_observed,
            "unpriced": self.unpriced,
        }
        payload["usdMicros"] = None if self.unpriced else self.usd_micros
        return payload


def _int_or_none(value: Any) -> int | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(float(value))
        except ValueError:
            return None
    return None


def observed_usage(raw: Any) -> tuple[int | None, int | None]:
    """Read `(tokens, usd_micros)` off a provider response.

    Both are three-valued: a count the provider did not report comes back as
    `None` and stays `None` all the way into the event. Adapters already place
    these fields on the raw proposal (`_DIAGNOSTIC_FIELDS` in the engine); this
    reads the same vocabulary rather than inventing a second one.
    """
    if not isinstance(raw, Mapping):
        return (None, None)

    # A composed adapter may know that the returned usage covers only its
    # final attempt (for example, a fallback after a failed primary).  Partial
    # usage must not be mistaken for complete accounting: retaining the
    # reservation and marking the call unsettled is the fail-closed result.
    if raw.get("usage_complete") is False:
        return (None, None)

    tokens: int | None = None
    usage = raw.get("usage")
    if isinstance(usage, Mapping):
        total = _int_or_none(usage.get("total_tokens") or usage.get("totalTokens"))
        if total is not None:
            tokens = total
        else:
            prompt = _int_or_none(usage.get("prompt_tokens") or usage.get("promptTokens"))
            completion = _int_or_none(
                usage.get("completion_tokens") or usage.get("completionTokens"))
            if prompt is not None or completion is not None:
                tokens = (prompt or 0) + (completion or 0)

    usd = _int_or_none(raw.get("usd_micros"))
    if usd is None:
        cost = raw.get("cost_usd")
        cost_value = None if isinstance(cost, bool) else cost
        if isinstance(cost_value, (int, float)):
            usd = int(round(float(cost_value) * 1_000_000))
    return (tokens, usd)


class InferenceMeter:
    """Reserve before the provider call; settle after it. One governor.

    `pricing` is `(prompt_micros_per_mtok, completion_micros_per_mtok)` or
    `None` when the route's price is not known. `None` does not mean free: it
    means the USD dimension cannot be bounded ahead of the call, so the meter
    bounds tokens exactly and settles USD from whatever the provider reports.
    """

    def __init__(
        self,
        governor: Governor,
        run_id: str,
        *,
        pricing: tuple[int, int] | None = None,
        default_max_completion_tokens: int = DEFAULT_MAX_COMPLETION_TOKENS,
    ) -> None:
        self._governor = governor
        self._run_id = run_id
        self._pricing = pricing
        self._default_completion = int(default_max_completion_tokens)
        self._unsettled_calls = 0
        self._observed_tokens = 0
        self._observed_usd_micros = 0

    # -- reporting ---------------------------------------------------------

    @property
    def unsettled_calls(self) -> int:
        """Calls whose cost the provider never reported. Never folded into 0."""
        return self._unsettled_calls

    @property
    def observed_tokens(self) -> int:
        return self._observed_tokens

    @property
    def observed_usd_micros(self) -> int:
        return self._observed_usd_micros

    # -- the two halves ----------------------------------------------------

    def reserve(
        self,
        *,
        prompt_tokens: int,
        sampling: Mapping[str, Any] | None = None,
    ) -> InferenceReservation:
        """S7 for inference. Raises `BudgetDenied` when the ceiling refuses.

        `prompt_tokens` is the *compiled* prompt, not an estimate: the layered
        operator has already assembled the vector by the time it calls this, so
        the input half of the reservation is exact and only the completion half
        is a bound.
        """
        max_completion = self._default_completion
        if isinstance(sampling, Mapping):
            declared = _int_or_none(sampling.get("maxTokens") or sampling.get("max_tokens"))
            if declared is not None and declared > 0:
                max_completion = declared

        prompt = max(int(prompt_tokens), 0)
        tokens = prompt + max_completion

        usd_micros = 0
        priced = self._pricing is not None
        if self._pricing is not None:
            prompt_rate, completion_rate = self._pricing
            usd_micros = (
                -(-(prompt * prompt_rate) // 1_000_000)
                + -(-(max_completion * completion_rate) // 1_000_000)
            )

        wanted: dict[str, int] = {}
        if tokens:
            wanted["tokens"] = tokens
        if usd_micros:
            wanted["usd_micros"] = usd_micros

        lease = self._governor.reserve(self._run_id, _MeterReservation(wanted))
        return InferenceReservation(
            lease=lease,
            prompt_tokens=prompt,
            max_completion_tokens=max_completion,
            usd_micros=usd_micros,
            priced=priced,
        )

    def settle(self, reservation: InferenceReservation, raw: Any) -> InferenceSettlement:
        """S10 for inference. Debits reality, including an overrun.

        Called on **every** path out of the provider call, success or failure:
        a call that failed after the tokens were spent still spent them, and a
        call that never reached the provider releases its whole reservation.
        """
        tokens, usd = observed_usage(raw)
        usage_observed = tokens is not None

        actual: dict[str, int] = {}
        if tokens is None:
            # The provider told us nothing. We may not invent a zero, and we may
            # not silently refund: charge the reservation we actually held, and
            # record the call as unsettled so the report can say so.
            actual["tokens"] = reservation.tokens
            self._unsettled_calls += 1
        else:
            actual["tokens"] = max(tokens, 0)
            self._observed_tokens += actual["tokens"]

        unpriced = usd is None
        if usd is not None:
            actual["usd_micros"] = max(usd, 0)
            self._observed_usd_micros += actual["usd_micros"]
        elif reservation.usd_micros:
            actual["usd_micros"] = reservation.usd_micros

        settlement = self._governor.commit(reservation.lease, actual)
        return InferenceSettlement(
            tokens=actual.get("tokens", 0),
            usd_micros=actual.get("usd_micros", 0),
            unpriced=unpriced,
            usage_observed=usage_observed,
            settlement=dict(settlement),
        )

    def release(self, reservation: InferenceReservation) -> None:
        """S11. The call never happened; the whole reservation comes back."""
        self._governor.release(reservation.lease)


class _MeterReservation:
    """The four additive dimensions, in the shape `Governor.reserve` reads.

    The governor refuses any dimension outside its additive set, so `turns` and
    `depth` -- structural ceilings that nobody spends -- are deliberately
    absent rather than passed and ignored.
    """

    __slots__ = ("_wanted",)

    def __init__(self, wanted: Mapping[str, int]) -> None:
        self._wanted = dict(wanted)

    def as_map(self) -> Mapping[str, int]:
        return dict(self._wanted)


__all__.append("BudgetDenied")
