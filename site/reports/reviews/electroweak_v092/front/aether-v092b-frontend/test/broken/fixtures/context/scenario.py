#!/usr/bin/env python3
"""MF-CTX-001 / MF-CTX-002: Context compiler enforcement and turn-2 tool observation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from vanguard.packages.agency.context.compiler import ContextCompiler
from vanguard.packages.agency.context.layers import Fragment
from vanguard.packages.ports.event_store import Result


class FakeModel:
    def __init__(self) -> None:
        self.invocations: list[dict] = []

    def propose(self, context, tools, sampling):
        self.invocations.append(dict(context))
        if len(self.invocations) == 1:
            return Result.success({
                "text": "reading file",
                "toolCalls": [{"id": "c1", "name": "fs.read", "arguments": {"path": "a.txt"}}],
            })
        return Result.success({"text": "done with file", "toolCalls": []})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--variant",
        choices=("reference", "bypass-compiler", "dropped-observation"),
        required=True,
    )
    args = parser.parse_args()

    compiler = ContextCompiler(
        system_core="system instruction",
        tool_schemas=({"name": "fs.read", "schema": {"type": "object"}},),
        environment="repo=test",
    )

    model = FakeModel()
    dialogue: list[Fragment] = []

    # Turn 1
    if args.variant == "bypass-compiler":
        # Defect: model called with bypass raw dict
        context_turn_1 = {"raw_bypass": True, "messages": [{"role": "user", "content": "read a.txt"}]}
    else:
        compiled_1 = compiler.compile(brief="read a.txt", dialogue=tuple(dialogue))
        context_turn_1 = dict(compiled_1.bundle())

    if "layers" not in context_turn_1 or not any(l.get("layer") == "L1" for l in context_turn_1.get("layers", [])):
        raise AssertionError("compiled context bypassed")

    res1 = model.propose(context_turn_1, (), {})
    assert res1.ok

    # Simulate tool observation
    tool_output = "content of a.txt: hello"
    if args.variant != "dropped-observation":
        dialogue = [Fragment(source="fs.read", label="fs.read-1", text=tool_output)]

    # Turn 2
    compiled_2 = compiler.compile(brief="read a.txt", dialogue=tuple(dialogue))
    context_turn_2 = dict(compiled_2.bundle())
    res2 = model.propose(context_turn_2, (), {})
    assert res2.ok

    # Verify turn 2 has tool observation in L5 dialogue layers
    dialogue_layers = [
        l for l in context_turn_2.get("layers", [])
        if l.get("layer") == "L5" and "hello" in l.get("content", "")
    ]
    if not dialogue_layers:
        raise AssertionError("tool observation absent on turn 2")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
