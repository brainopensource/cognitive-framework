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


CAPABILITY_TIER_DESCRIPTIONS: dict[int, str] = {
    0: "SWE-bench Verified Basics (single-file functions, string/clamp logic)",
    1: "SWE-bench Verified Easy (parsers, SemVer, basic data structures)",
    2: "SWE-bench Verified Medium (token bucket, trie router, connection pools, JSON schema)",
    3: "SWE-bench Verified Advanced (topological DAG, circuit breaker, event bus, caching engine)",
    4: "SWE-bench Pro Entry/Mid (protocol FSM, stream pipeline, ORM compiler, zero-copy RPC wire)",
    5: "SWE-bench Pro Hard / Frontier (distributed WAL, concurrent LSM, Raft consensus, 2PC engine, multi-tenant DRF scheduler)",
}

CAPABILITY_TIER_MAP: dict[int, tuple[int, ...]] = {
    0: (0,),
    1: (1,),
    2: (2,),
    3: (3,),
    4: (4, 7, 8),
    5: (5, 6, 9, 10),
}


class LamEngine:
    def __init__(self, scenarios: Sequence[Scenario]) -> None:
        self.scenarios = tuple(scenarios)
        self._by_id = {item.id: item for item in self.scenarios}
        self._by_scenario_tier: dict[int, list[Scenario]] = {}
        for s in self.scenarios:
            self._by_scenario_tier.setdefault(s.tier, []).append(s)

    @classmethod
    def from_directory(cls, directory: str | Path) -> "LamEngine":
        root = Path(directory)
        loaded: list[Scenario] = []
        for path in sorted(root.glob("t*.json")):
            raw = json.loads(path.read_text(encoding="utf-8"))
            turns = tuple(
                Turn(
                    tool_messages=int(turn.get("tool_messages") or turn.get("tool_messages_seen") or idx),
                    finish_reason=str(turn["finish_reason"]),
                    content=str(turn.get("content") or ""),
                    tool_calls=tuple(turn.get("tool_calls") or ()),
                )
                for idx, turn in enumerate(raw["turns"])
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

    def get_capability_tier_for_scenario(self, scenario_tier: int) -> int:
        """Map raw scenario tier (0..10) to 0..5 capability tier."""
        for cap_tier, scen_tiers in CAPABILITY_TIER_MAP.items():
            if scenario_tier in scen_tiers:
                return cap_tier
        return min(5, max(0, scenario_tier))

    def scenario(self, model: str, default_tier: int = 5) -> Scenario:
        name = model.split("/", 1)[-1] if model.startswith("lam/") else model
        if name in self._by_id:
            return self._by_id[name]

        # Handle capability tier aliases: tier-0..tier-5, iq-0..iq-5
        for prefix in ("tier-", "tier_", "iq-", "iq_"):
            if name.startswith(prefix):
                try:
                    cap_tier = int(name[len(prefix):])
                    prefix_matches = [s for s in self.scenarios if s.id.startswith(f"t{cap_tier}-")]
                    if prefix_matches:
                        return prefix_matches[0]
                    if cap_tier in CAPABILITY_TIER_MAP:
                        for st in CAPABILITY_TIER_MAP[cap_tier]:
                            st_matches = [s for s in self.scenarios if s.id.startswith(f"t{st}-")]
                            if st_matches:
                                return st_matches[0]
                except ValueError:
                    pass

        if name in ("", "default"):
            pref = [s for s in self.scenarios if s.id.startswith(f"t{default_tier}-")]
            if pref:
                return pref[0]
            if self.scenarios:
                return self.scenarios[0]

        raise KeyError(name)

    def complete(self, body: Mapping[str, Any], capability_tier: Optional[int] = None) -> dict[str, Any]:
        req_model = str(body.get("model") or "")
        effective_cap = capability_tier if capability_tier is not None else 5
        scenario = self.scenario(req_model, default_tier=effective_cap)

        messages = list(body.get("messages") or [])
        tool_count = sum(1 for item in messages if item.get("role") == "tool")
        turn = _select_turn(scenario.turns, tool_count, messages)

        # If model capability tier is lower than required scenario capability, simulate degraded output
        required_cap = self.get_capability_tier_for_scenario(scenario.tier)
        is_degraded = effective_cap < required_cap

        message: dict[str, Any] = {"role": "assistant", "content": turn.content}
        finish_reason = turn.finish_reason

        if is_degraded and effective_cap <= 1:
            # Low tier model: omit complex tool calls or emit partial exploration
            if turn.tool_calls and len(turn.tool_calls) > 1:
                message["tool_calls"] = [dict(turn.tool_calls[0])]
            elif turn.tool_calls:
                message["tool_calls"] = [dict(call) for call in turn.tool_calls]
            else:
                message["content"] = "I cannot determine how to solve this complex distributed systems problem."
                finish_reason = "stop"
        else:
            if turn.tool_calls:
                message["tool_calls"] = [dict(call) for call in turn.tool_calls]

        prompt_tokens = estimate_tokens(json.dumps(messages, ensure_ascii=False))
        completion_tokens = estimate_tokens(json.dumps(message, ensure_ascii=False))
        return {
            "id": f"lam-{scenario.id}-cap{effective_cap}-tools{tool_count}",
            "object": "chat.completion",
            "model": req_model,
            "choices": [
                {
                    "index": 0,
                    "finish_reason": finish_reason,
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
                "scenario_tier": scenario.tier,
                "capability_tier": effective_cap,
                "capability_description": CAPABILITY_TIER_DESCRIPTIONS.get(effective_cap, "Custom"),
                "required_capability_tier": required_cap,
                "is_downgrade": is_degraded,
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
