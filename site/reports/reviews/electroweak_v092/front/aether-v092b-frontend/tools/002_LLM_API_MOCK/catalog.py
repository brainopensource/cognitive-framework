"""Immutable, validated Markdown/JSON answer catalog for the LAM mock server.

Provides stateless multi-turn replay by searching message histories for prior
turn responses or counting tool result observations.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any


class CatalogValidationError(ValueError):
    """Raised before serving when one or more catalog files are invalid."""

    def __init__(self, errors: list[str]) -> None:
        self.errors = tuple(errors)
        super().__init__("invalid answer bank:\n" + "\n".join(f"- {error}" for error in errors))


@dataclass(frozen=True)
class ToolCallSpec:
    """A scripted tool call specification."""

    call_id: str
    name: str
    arguments: str


@dataclass(frozen=True)
class Reply:
    """A single conversational or tool response turn."""

    scenario_key: str
    tier: int
    turn: int
    text: str
    relpath: str
    sha256: str
    tool_calls: tuple[ToolCallSpec, ...] = ()
    observed: Mapping[str, Any] = MappingProxyType({})


@dataclass(frozen=True)
class Scenario:
    """A collection of multi-tier, multi-turn replies for a specific task."""

    key: str
    keywords: tuple[str, ...]
    replies: Mapping[int, tuple[Reply, ...]]
    exhaustion: str = "repeat_last"
    sha256: str = ""


@dataclass(frozen=True)
class Catalog:
    """The complete immutable answer bank."""

    scenarios: Mapping[str, Scenario]
    ordered_scenario_keys: tuple[str, ...]
    default_key: str
    sha256: str

    @property
    def default_scenario(self) -> Scenario:
        return self.scenarios[self.default_key]


@dataclass(frozen=True)
class ReplySelection:
    """Result of a stateless selection decision."""

    reply: Reply
    requested_turn: int
    matched_reply: Reply | None
    exhausted: bool


def _find_latest_prior_reply(scenario: Scenario, prompt: str) -> Reply | None:
    """Find the latest turn response that appears verbatim in the prompt history."""
    matches: list[tuple[int, int, int, int, Reply]] = []
    for tier, turns in scenario.replies.items():
        for turn in turns:
            idx = prompt.rfind(turn.text)
            if idx >= 0:
                # Prioritize: latest index, longest text, highest turn, smallest relpath
                matches.append((idx, len(turn.text), turn.turn, -tier, turn))
    if not matches:
        return None
    matches.sort(key=lambda item: (-item[0], -item[1], -item[2], item[3]))
    return matches[0][4]


def select_reply(scenario: Scenario, effective_tier: int, prompt: str) -> ReplySelection:
    """Stateless selection: advances turn if prior turn's text is quoted in prompt."""
    matched_reply = _find_latest_prior_reply(scenario, prompt)
    requested_turn = 1 if matched_reply is None else matched_reply.turn + 1
    turns = scenario.replies.get(effective_tier, scenario.replies.get(1, ()))
    if not turns:
        raise ValueError(f"No turns found for tier {effective_tier} in scenario {scenario.key}")
    exhausted = requested_turn > len(turns)
    reply = turns[-1] if exhausted else turns[requested_turn - 1]
    return ReplySelection(
        reply=reply,
        requested_turn=requested_turn,
        matched_reply=matched_reply,
        exhausted=exhausted,
    )


def select_tool_step(scenario: Scenario, effective_tier: int, *, tool_results_seen: int) -> ReplySelection:
    """Stateless selection for tool calling: advances turn based on tool observations count."""
    turns = scenario.replies.get(effective_tier, scenario.replies.get(1, ()))
    if not turns:
        raise ValueError(f"No turns found for tier {effective_tier} in scenario {scenario.key}")
    requested_turn = tool_results_seen + 1
    if tool_results_seen == 0:
        return ReplySelection(reply=turns[0], requested_turn=1, matched_reply=None, exhausted=False)
    exhausted = requested_turn > len(turns)
    reply = turns[-1] if exhausted else turns[requested_turn - 1]
    matched_reply = turns[min(tool_results_seen, len(turns)) - 1]
    return ReplySelection(
        reply=reply,
        requested_turn=requested_turn,
        matched_reply=matched_reply,
        exhausted=exhausted,
    )


def _digest_tree(root: Path) -> str:
    hasher = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        if path.is_file():
            hasher.update(str(path.relative_to(root)).encode("utf-8"))
            hasher.update(path.read_bytes())
    return hasher.hexdigest()


def load_catalog(root: Path) -> Catalog:
    """Load and validate the answer bank directory."""
    errors: list[str] = []
    root = root.resolve()
    if not root.is_dir():
        raise CatalogValidationError([f"answer bank root {root} is not a directory"])

    index_path = root / "index.json"
    if not index_path.is_file():
        raise CatalogValidationError([f"missing index.json in {root}"])

    try:
        index_data = json.loads(index_path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise CatalogValidationError([f"invalid index.json: {exc}"])

    default_key = index_data.get("default_scenario", "")
    scenario_keys = index_data.get("scenarios", [])
    if not scenario_keys:
        raise CatalogValidationError(["index.json has no scenarios declared"])
    if default_key not in scenario_keys:
        errors.append(f"default_scenario '{default_key}' not in scenarios list")

    scenarios: dict[str, Scenario] = {}

    for key in scenario_keys:
        scenario_dir = root / key
        if not scenario_dir.is_dir():
            errors.append(f"scenario directory {scenario_dir} does not exist")
            continue

        meta_path = scenario_dir / "scenario.json"
        if not meta_path.is_file():
            errors.append(f"missing scenario.json in {scenario_dir}")
            continue

        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"invalid scenario.json in {scenario_dir}: {exc}")
            continue

        keywords = tuple(meta.get("keywords", []))
        tiers_data = meta.get("tiers", {})
        exhaustion = meta.get("turn_exhaustion", "repeat_last")

        replies_by_tier: dict[int, tuple[Reply, ...]] = {}

        for tier_str, tier_info in tiers_data.items():
            try:
                tier = int(tier_str)
            except ValueError:
                continue

            turns_info = tier_info.get("turns", [])
            loaded_turns: list[Reply] = []

            for turn_idx, turn_item in enumerate(turns_info, start=1):
                content_file = turn_item.get("content_file", "")
                content_path = scenario_dir / content_file
                if not content_path.is_file():
                    errors.append(f"{scenario_dir} tier {tier} turn {turn_idx}: missing content_file '{content_file}'")
                    continue

                raw_bytes = content_path.read_bytes()
                text = raw_bytes.decode("utf-8")
                sha256 = hashlib.sha256(raw_bytes).hexdigest()

                tool_calls: list[ToolCallSpec] = []
                for tc in turn_item.get("tool_calls", []):
                    tool_calls.append(
                        ToolCallSpec(
                            call_id=tc.get("call_id", f"call-{turn_idx}"),
                            name=tc.get("name", "tool"),
                            arguments=json.dumps(tc.get("arguments", {}), sort_keys=True),
                        )
                    )

                loaded_turns.append(
                    Reply(
                        scenario_key=key,
                        tier=tier,
                        turn=turn_idx,
                        text=text,
                        relpath=str(content_path.relative_to(root)),
                        sha256=sha256,
                        tool_calls=tuple(tool_calls),
                        observed=MappingProxyType(dict(turn_item.get("observed", {}))),
                    )
                )

            if loaded_turns:
                replies_by_tier[tier] = tuple(loaded_turns)

        if not replies_by_tier:
            errors.append(f"scenario '{key}' has no valid tiers")
            continue

        scenarios[key] = Scenario(
            key=key,
            keywords=keywords,
            replies=MappingProxyType(replies_by_tier),
            exhaustion=exhaustion,
            sha256=_digest_tree(scenario_dir),
        )

    if errors:
        raise CatalogValidationError(errors)

    return Catalog(
        scenarios=MappingProxyType(scenarios),
        ordered_scenario_keys=tuple(scenario_keys),
        default_key=default_key,
        sha256=_digest_tree(root),
    )
