"""Typed failure/success envelope for the SPI wire. `instrument_error` is a
first-class flag (SPI RFC).

Owning contract: Wave-2 2.1-A/C. Moved from `layer0/spi/result.py`: the five
SPI Protocols (`ports/spi.py`) are typed against this ADT, so it moves with
them rather than staying a second `layer0` import every mover would still
need. Distinct from `ports/event_store.Result` (a single dataclass with an
`.ok` flag) -- that shape predates the SPI and nothing here proposes
unifying the two; see ADR-0076 before changing either.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar, Union

T = TypeVar("T")

__all__ = ["Err", "Ok", "Result"]


@dataclass(frozen=True, slots=True)
class Ok(Generic[T]):
    value: T


@dataclass(frozen=True, slots=True)
class Err:
    code: str
    message: str
    instrument_error: bool = False


Result = Union[Ok[T], Err]
