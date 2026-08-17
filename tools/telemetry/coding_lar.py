"""LAR for the coding instrument: offline gene *hypotheses* from session logs.

Never writes pack files. Never sits in the episode loop. A human or BETA
applies any accepted gene. Adjacent to A-05: this module does not grade the
same artifact the episode produced.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


def hypotheses_from_sessions(sessions: Sequence[Mapping[str, Any]]) -> list[dict[str, str]]:
    """Propose next pack experiments. Empty input → no hypotheses (not a pass)."""
    out: list[dict[str, str]] = []
    if not sessions:
        return out

    denials = sum(int(s.get("denialCount") or 0) for s in sessions)
    turns = [int(s.get("turnCount") or 0) for s in sessions]
    compact = sum(int(s.get("compactCount") or 0) for s in sessions)
    green = sum(1 for s in sessions if s.get("oracle_green"))
    missing = sum(1 for s in sessions if str(s.get("termination", "")).endswith("workspace_missing"))

    if missing:
        out.append({
            "slot": "workspace",
            "hypothesis": "BETA has not landed DOGFOOD/greenfield dirs; do not drop them from the denominator.",
            "gene": "none",
        })
    if denials and green == 0:
        out.append({
            "slot": "approval_policy",
            "hypothesis": "Privileged denials with zero oracle_green: thicken inspect-before-edit prompt; do not auto-approve.",
            "gene": "system-prompt.txt / approval_policy.json",
        })
    if turns and max(turns) <= 1 and green == 0:
        out.append({
            "slot": "loop",
            "hypothesis": "turnCount≤1 with no green: lab/run.py may still be a stub, or MOCK one-shot; do not invent a second loop.",
            "gene": "none (ALFA driver)",
        })
    if compact == 0 and any(t > 8 for t in turns):
        out.append({
            "slot": "compaction_policy",
            "hypothesis": "Long episodes with compactCount=0: check compaction gene is load-bearing, keep brief exempt.",
            "gene": "compaction_policy / context_policy",
        })
    if green == 0 and not missing:
        out.append({
            "slot": "skill",
            "hypothesis": "Workspaces present, none green: add pytest-green skill card (prefix index only; body via fs.read).",
            "gene": "skill artifact (BETA)",
        })
    return out


def write_review_artifact(hypotheses: Sequence[Mapping[str, str]], dest: Path | TextIO) -> None:
    """Write markdown under docs/scrum/.../evidence/. Refuses pack/manifest paths."""
    text = "# LAR coding hypotheses (offline)\n\nNot applied. BETA/human copies genes if accepted.\n\n"
    if not hypotheses:
        text += "_No hypotheses (insufficient session evidence)._\n"
    for item in hypotheses:
        text += f"- **{item.get('slot', '?')}** (`{item.get('gene', 'none')}`): {item.get('hypothesis', '')}\n"
    if isinstance(dest, Path):
        resolved = dest.resolve()
        parts = {p.lower() for p in resolved.parts}
        if "manifests" in parts or dest.suffix == ".json" and "vg-code" in dest.name:
            raise ValueError("LAR must not write pack genes; write a review artifact under docs/")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8")
        return
    dest.write(text)


def main() -> int:
    import argparse
    import sys
    parser = argparse.ArgumentParser(description="Offline LAR hypotheses from coding-session JSON")
    parser.add_argument("--sessions-json", help="JSON array of session objects")
    parser.add_argument("--out", help="Markdown review path under docs/")
    args = parser.parse_args()
    sessions: list[Any] = []
    if args.sessions_json:
        sessions = json.loads(Path(args.sessions_json).read_text(encoding="utf-8"))
    hyps = hypotheses_from_sessions(sessions)
    if args.out:
        write_review_artifact(hyps, Path(args.out))
    else:
        write_review_artifact(hyps, sys.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
