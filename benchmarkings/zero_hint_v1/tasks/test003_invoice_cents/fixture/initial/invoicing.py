"""Invoice totals expressed as integer cents."""

from __future__ import annotations

import re

_PRICE = re.compile(r"^(0|[1-9][0-9]*)\.([0-9]{2})$")


def line_cents(quantity: int, unit_price: str) -> int:
    if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity < 0:
        raise ValueError("quantity must be a non-negative integer")
    if not isinstance(unit_price, str) or _PRICE.fullmatch(unit_price) is None:
        raise ValueError("unit_price must be a two-decimal dollar amount")
    return int(quantity * float(unit_price) * 100)


def invoice_cents(lines: list[tuple[int, str]]) -> int:
    return sum(line_cents(quantity, price) for quantity, price in lines)
