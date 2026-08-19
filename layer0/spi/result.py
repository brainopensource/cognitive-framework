"""Typed failure/success envelope. `instrument_error` is a first-class flag (SPI RFC)."""

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
