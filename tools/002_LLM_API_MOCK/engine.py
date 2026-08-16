"""Stateless LAM engine: OpenAI-shaped completions from a scenario bank."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from pricing import estimate_tokens, sonnet_usd

__all__ = ["LamEngine", "Scenario"]


@dataclass(frozen=True, slots=True)
class Turn:
    tool_messages: int
    finish_reason: str
    content: str
    tool_calls: tuple[Mapping[str, Any], ...] = ()


@dataclass(frozen=True, slots=True)
class Scenario:
    id: str
    tier: int
    title: str
    workspace: Mapping[str, str]
    turns: tuple[Turn, ...]


class LamEngine:
    def __init__(self, scenarios: Sequence[Scenario]) -> None:
        self.scenarios = tuple(scenarios)
        self._by_id = {item.id: item for item in self.scenarios}

    @classmethod
    def from_directory(cls, directory: str | Path) -> "LamEngine":
        root = Path(directory)
        loaded: list[Scenario] = []
        for path in sorted(root.glob("t*.json")):
            raw = json.loads(path.read_text(encoding="utf-8"))
            turns = tuple(
                Turn(
                    tool_messages=int(turn.get("tool_messages", turn.get("tool_messages_seen", 0))),
                    finish_reason=str(turn["finish_reason"]),
                    content=str(turn.get("content") or ""),
                    tool_calls=tuple(turn.get("tool_calls") or ()),
                )
                for turn in raw["turns"]
            )
            loaded.append(
                Scenario(
                    id=raw["id"],
                    tier=int(raw["tier"]),
                    title=raw["title"],
                    workspace=dict(raw.get("workspace") or {}),
                    turns=turns,
                )
            )
        return cls(loaded)

    def scenario(self, model: str) -> Scenario:
        name = model.split("/", 1)[-1] if model.startswith("lam/") else model
        if name not in self._by_id:
            raise KeyError(name)
        return self._by_id[name]

    def complete(self, body: Mapping[str, Any]) -> dict[str, Any]:
        scenario = self.scenario(str(body.get("model") or ""))
        messages = list(body.get("messages") or [])
        tool_count = sum(1 for item in messages if item.get("role") == "tool")
        turn = _select_turn(scenario.turns, tool_count, messages)
        message: dict[str, Any] = {"role": "assistant", "content": turn.content}
        if turn.tool_calls:
            message["tool_calls"] = [dict(call) for call in turn.tool_calls]
        prompt_tokens = estimate_tokens(json.dumps(messages, ensure_ascii=False))
        completion_tokens = estimate_tokens(json.dumps(message, ensure_ascii=False))
        return {
            "id": f"lam-{scenario.id}-tools{tool_count}",
            "object": "chat.completion",
            "model": body.get("model"),
            "choices": [
                {
                    "index": 0,
                    "finish_reason": turn.finish_reason,
                    "message": message,
                }
            ],
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
            "lam": {
                "scenario": scenario.id,
                "tier": scenario.tier,
                "tool_messages": tool_count,
                "estimated_usd_if_sonnet": sonnet_usd(prompt_tokens, completion_tokens),
            },
        }


def _select_turn(turns: Sequence[Turn], tool_count: int, messages: Sequence[Mapping[str, Any]]) -> Turn:
    last_user = ""
    for item in reversed(messages):
        if item.get("role") == "user":
            last_user = str(item.get("content") or "")
            break
    if "passed" in last_user.lower() or "pytest" in last_user.lower():
        stops = [turn for turn in turns if turn.finish_reason == "stop"]
        if stops:
            return stops[-1]
    exact = [turn for turn in turns if turn.tool_messages == tool_count]
    if exact:
        return exact[0]
    later = [turn for turn in turns if turn.tool_messages <= tool_count]
    if later:
        return later[-1]
    return turns[0]
