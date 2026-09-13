# DX-MULTI: Split the ledger helper across two modules

`ledger.py` currently holds both the parser and the formatter.

1. Move the formatter into a new module `formatter.py`, keeping the public
   name `format_row(row: dict) -> str` unchanged.
2. Leave `parse_row(line: str) -> dict` in `ledger.py` and import the
   formatter from the new module so `ledger.format_row` still resolves.
3. Both files must change in the same submission.
