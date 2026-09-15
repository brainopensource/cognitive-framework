"""Ledger row parsing and formatting (pre-split)."""


def parse_row(line: str) -> dict:
    key, _, value = line.partition("=")
    return {"key": key.strip(), "value": value.strip()}


def format_row(row: dict) -> str:
    return f"{row['key']}={row['value']}"
