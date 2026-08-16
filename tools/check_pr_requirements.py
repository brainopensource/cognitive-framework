#!/usr/bin/env python3
"""Require implementation pull requests to cite valid Active MVP req_ids."""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

from repo_paths import active_mvp_contract

CONTRACT = active_mvp_contract()
REQ_PATTERN = re.compile(r"\bREQ-[A-Z]+-[0-9]{3}\b")


def main() -> int:
    event_name = os.environ.get("GITHUB_EVENT_NAME", "")
    if event_name != "pull_request":
        print("PR REQUIREMENTS SKIP: not a pull_request event")
        return 0

    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path:
        print("PR REQUIREMENTS FAIL: GITHUB_EVENT_PATH is missing")
        return 1

    event = json.loads(Path(event_path).read_text(encoding="utf-8"))
    body = event.get("pull_request", {}).get("body") or ""
    cited = set(REQ_PATTERN.findall(body))
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    valid = {row["req_id"] for row in contract["requirements"]}

    if not cited:
        print("PR REQUIREMENTS FAIL: PR body cites no req_id")
        return 1
    unknown = cited - valid
    if unknown:
        print(f"PR REQUIREMENTS FAIL: unknown req_id(s): {', '.join(sorted(unknown))}")
        return 1

    print(f"PR REQUIREMENTS PASS: {', '.join(sorted(cited))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
