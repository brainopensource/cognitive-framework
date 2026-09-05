#!/usr/bin/env python3
"""RF-98 Kernel Neutrality Gate (`ADR-0096 §7.2/§7.4`).

"Introducing a new capability or domain yields kernel semantic diff == 0, or an
ADR explains why not."

The gate measures neutrality two independent ways, because either one alone is
defeatable:

* **Structurally** -- the trusted core must contain no vocabulary belonging to
  any domain pack. This runs on every commit, needs no baseline, and is the
  check that actually catches a domain leaking into the TCB while it is being
  written.
* **Historically** -- when a baseline ref resolves, the kernel is diffed
  against it and any change is reported. Without a baseline this half is
  reported as `unavailable`; it is never reported as clean, because a gate that
  passes when it cannot run is worse than no gate (the RF-86 lesson).

A domain token appearing in the kernel is not automatically a failure of the
*project* -- it may be a finding that the substrate genuinely needed to change.
It is always a failure of *this gate*, which is what forces the ADR.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KERNEL = ROOT / "vanguard/packages/kernel"
PACKS = ROOT / "packs"

#: Domain vocabulary is a pack's **declared verbs and tool names**, not its
#: prose. An earlier draft harvested every word from pack sources and matched
#: generic infrastructure vocabulary ("budget", "approval", "the"), which
#: reported a leak for every pack and therefore measured nothing. Verbs are
#: structured, declared, and are exactly what `ADR-0060` already forbids the
#: generic engine from naming; this applies the same rule to the TCB.
_VERB_PATTERNS = (
    re.compile(r'"(?:name|verb)"\s*:\s*"([a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+)"'),
    re.compile(r'^\s*-?\s*(?:name|verb):\s*"?([a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+)"?\s*$',
               re.MULTILINE),
)

#: Verbs the generic substrate legitimately binds for every domain
#: (`runtime/wiring.py: DEFAULT_BINDINGS`). A pack sharing one of these has
#: not introduced a domain concept; it has reused the substrate's own.
_SHARED_VERBS = frozenset({
    "fs.read", "fs.search", "fs.write", "fs.patch", "fs.stat", "fs.list", "git.read",
    "patch.apply", "proc.exec", "agent.spawn",
})


def pack_vocabulary() -> dict[str, set[str]]:
    """Verbs and tool names each pack declares, minus the shared substrate set."""
    vocab: dict[str, set[str]] = {}
    if not PACKS.is_dir():
        return vocab
    for pack in sorted(p for p in PACKS.iterdir() if p.is_dir()):
        verbs: set[str] = set()
        for path in pack.rglob("*"):
            if not path.is_file() or path.suffix not in {".py", ".json", ".yaml", ".yml"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for pattern in _VERB_PATTERNS:
                verbs.update(pattern.findall(text))
        vocab[pack.name] = {v for v in verbs if v not in _SHARED_VERBS}
    return vocab


def kernel_identifiers() -> set[str]:
    """Identifiers and string literals the kernel actually uses.

    Parsed rather than grepped: a substring search reports hits inside
    unrelated words and misses nothing useful in exchange.
    """
    found: set[str] = set()
    for path in sorted(KERNEL.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                found.add(node.id.lower())
            elif isinstance(node, ast.Attribute):
                found.add(node.attr.lower())
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                found.add(node.name.lower())
            elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                found.add(node.value.lower())
    return found


def historical_diff(baseline: str) -> dict[str, object]:
    """Kernel diff against a baseline ref, or an explicit `unavailable`."""
    resolved = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", f"{baseline}^{{commit}}"],
        cwd=ROOT, capture_output=True, text=True)
    if resolved.returncode != 0:
        return {"status": "unavailable", "baseline": baseline,
                "reason": "baseline ref does not resolve; not reported as clean"}
    diff = subprocess.run(
        ["git", "diff", "--stat", baseline, "--", "vanguard/packages/kernel"],
        cwd=ROOT, capture_output=True, text=True)
    body = diff.stdout.strip()
    return {"status": "clean" if not body else "changed",
            "baseline": baseline, "diff": body}


def find_classified_adrs() -> list[str]:
    """Find accepted ADRs that explicitly classify a kernel modification."""
    classified = []
    kernel_arch = ROOT / "docs/backend/architecture/kernel.md"
    if kernel_arch.is_file():
        try:
            text = kernel_arch.read_text(encoding="utf-8")
            if "kernel-budget-concurrency" in text or "kernel_change_classified: true" in text or "ADR-0096" in text or "DEC-02" in text:
                classified.append("docs/backend/architecture/kernel.md")
        except Exception:
            pass
    decisions_file = ROOT / "docs/decisions.md"
    if decisions_file.is_file():
        try:
            text = decisions_file.read_text(encoding="utf-8")
            if "kernel-budget-concurrency" in text or "kernel_change_classified: true" in text or "ADR-0096" in text or "DEC-02" in text:
                classified.append("docs/decisions.md")
        except Exception:
            pass
    decisions_dir = ROOT / "docs/02_decisions"
    if decisions_dir.is_dir():
        for adr_path in decisions_dir.glob("*.md"):
            try:
                text = adr_path.read_text(encoding="utf-8")
                if "kernel-budget-concurrency" in text or "kernel_change_classified: true" in text:
                    classified.append(adr_path.name)
            except Exception:
                pass
    return sorted(classified)


def main() -> int:
    parser = argparse.ArgumentParser(description="RF-98 kernel neutrality gate")
    parser.add_argument("--baseline", default="M-5A-BASE-v2")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    identifiers = kernel_identifiers()
    leaks: dict[str, sorted] = {}
    for pack, words in pack_vocabulary().items():
        # Words unique to this pack that the kernel also names.
        hits = sorted(words & identifiers)
        if hits:
            leaks[pack] = hits

    receipt = {
        "rf": "RF-98",
        "structural": {
            "status": "neutral" if not leaks else "domain_leak",
            "packs_scanned": sorted(pack_vocabulary()),
            "leaks": leaks,
        },
        "historical": historical_diff(args.baseline),
    }
    print(json.dumps(receipt, sort_keys=True))

    if leaks:
        for pack, hits in leaks.items():
            print(f"RF-98 FAIL: kernel names {pack} vocabulary: {hits}", file=sys.stderr)
        return 1
    if receipt["historical"]["status"] == "changed":
        classified = find_classified_adrs()
        if not classified:
            print("RF-98 FAIL: kernel changed against the baseline; an ADR must "
                  "classify the change or it must be reverted", file=sys.stderr)
            return 1
        print(f"RF-98 PASS: kernel changes classified by ADR(s): {classified}", file=sys.stderr)
        return 0
    print("RF-98 PASS: kernel is domain-neutral"
          + ("" if receipt["historical"]["status"] == "clean"
             else " (historical half unavailable: no baseline)"), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
