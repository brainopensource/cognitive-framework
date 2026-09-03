#!/usr/bin/env python3
"""Project a coding-session log from a ledger JSONL file (no second DB).

  python3 tools/export_coding_session.py --jsonl path/to/episode.jsonl
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent
_ROOT = _TOOLS.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from vanguard.packages.adapters.stores.ledger_jsonl import import_jsonl
from vanguard.packages.domain.ledger.session_projection import project_session


def main() -> int:
    parser = argparse.ArgumentParser(description="Export a coding session projection from ledger JSONL")
    parser.add_argument("--jsonl", required=True, help="Path to episode ledger JSONL")
    args = parser.parse_args()
    path = Path(args.jsonl)
    with path.open(encoding="utf-8") as reader:
        envelopes = import_jsonl(reader)
    print(json.dumps(project_session(envelopes), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
