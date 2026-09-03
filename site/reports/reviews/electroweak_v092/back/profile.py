"""ModelBehaviorProfile: the declared, measurable behaviour of a provider model.

Owning contract: the agency emits ONE canonical intent. It never branches on
provider. Everything that differs between an OpenAI-style tool caller, an
Ollama text model, and a reasoning model is declared here as *data*, and the
dialect compiler (adapters/models/dialect.py) consumes this data to render the
provider-specific wire form.

This module is domain: pure values, no I/O, no provider imports. A profile is
content-addressable so a run can record exactly which behavioural assumptions
were in force when a proposal was produced.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Any, Mapping

from ..canonicalisation.digest import digest_of

__all__ = [
    "EditMode",
    "JsonReliability",
    "ToolCallStyle",
    "ModelBehaviorProfile",
    "PROFILES",
    "profile_for",
    "register_profile",
]


class ToolCallStyle(str, Enum):
    """How the model can be asked to select an action."""

    #: Provider exposes a native `tools`/`functions` array and returns a
    #: structured tool_call block. Highest fidelity.
    NATIVE = "native"
    #: No native tool API; the model is asked to emit a JSON object matching a
    #: schema we inline into the prompt.
    JSON_SCHEMA = "json_schema"
    #: Model is unreliable at raw JSON; we fence the payload in a delimiter
    #: block and extract it. Used for small local models.
    FENCED_JSON = "fenced_json"
    #: Last resort: a line-oriented `ACTION: x` / `ARGS: {...}` grammar that
    #: survives chatty preambles.
    TEXT_GRAMMAR = "text_grammar"


class JsonReliability(str, Enum):
    """Observed probability that a requested JSON payload parses first try."""

    HIGH = "high"        # >0.98 — retry budget of 1 is enough
    MEDIUM = "medium"    # ~0.90 — expect a reformat pass
    LOW = "low"          # <0.75 — always use a reduced schema on retry


class EditMode(str, Enum):
    """How this model is most reliable at expressing a code change."""

    UNIFIED_DIFF = "unified_diff"
    SEARCH_REPLACE = "search_replace"
    WHOLE_FILE = "whole_file"
    SHELL = "shell"


@dataclass(frozen=True, slots=True)
class ModelBehaviorProfile:
    """Declared behaviour of one model. Data only — the compiler does the work.

    `model_id` is the resolved provider identifier (e.g.
    ``anthropic/claude-sonnet-4``), not an alias, so a profile is never
    ambiguous about which weights it describes.
    """

    model_id: str
    tool_call_style: ToolCallStyle = ToolCallStyle.JSON_SCHEMA
    json_reliability: JsonReliability = JsonReliability.MEDIUM
    context_tokens: int = 8_192
    #: Tokens we refuse to spend on input, leaving room for the reply. The
    #: context compiler treats this as a hard ceiling, not a target.
    max_input_tokens: int = 6_144
    supports_parallel_tool_calls: bool = False
    supports_streaming: bool = True
    supports_system_role: bool = True
    #: The model emits explicit reasoning tokens that must NOT be fed back as
    #: assistant content on the next turn (they are not part of the transcript).
    emits_reasoning: bool = False
    supports_prompt_caching: bool = False
    preferred_edit_mode: EditMode = EditMode.UNIFIED_DIFF
    #: Cost in micro-USD per 1M tokens, so integer arithmetic stays exact and
    #: the budget kernel never sees a float.
    input_usd_micros_per_mtok: int = 0
    output_usd_micros_per_mtok: int = 0
    typical_latency_millis: int = 4_000
    #: When the model is handed a tool error, does it correct course or does it
    #: loop on the same call? Drives the recovery policy's retry allowance.
    recovers_from_tool_error: bool = True
    #: Cheap models are eligible for the mechanical roles (ranking, log
    #: summarisation, failure classification) and nothing else.
    eligible_roles: tuple[str, ...] = ("implementer",)
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.model_id.strip():
            raise ValueError("model_id must be non-empty")
        if self.max_input_tokens > self.context_tokens:
            raise ValueError(
                f"max_input_tokens ({self.max_input_tokens}) exceeds context "
                f"({self.context_tokens}) for {self.model_id!r}"
            )
        for name in ("context_tokens", "max_input_tokens", "typical_latency_millis"):
            if getattr(self, name) <= 0:
                raise ValueError(f"{name} must be positive")
        for name in ("input_usd_micros_per_mtok", "output_usd_micros_per_mtok"):
            if getattr(self, name) < 0:
                raise ValueError(f"{name} must be non-negative")
        if not self.eligible_roles:
            raise ValueError("a profile must permit at least one role")

    # -- derived policy ----------------------------------------------------

    @property
    def json_retry_budget(self) -> int:
        """How many reformat attempts the recovery policy may spend."""
        return {
            JsonReliability.HIGH: 1,
            JsonReliability.MEDIUM: 2,
            JsonReliability.LOW: 3,
        }[self.json_reliability]

    @property
    def needs_reduced_schema_on_retry(self) -> bool:
        """LOW-reliability models get a stripped schema rather than the same one."""
        return self.json_reliability is not JsonReliability.HIGH

    def permits_role(self, role: str) -> bool:
        return role in self.eligible_roles

    def cost_usd_micros(self, input_tokens: int, output_tokens: int) -> int:
        """Exact integer cost. Rounds up so we never under-report spend."""
        if input_tokens < 0 or output_tokens < 0:
            raise ValueError("token counts must be non-negative")
        total = (
            input_tokens * self.input_usd_micros_per_mtok
            + output_tokens * self.output_usd_micros_per_mtok
        )
        return -(-total // 1_000_000)  # ceiling division

    @property
    def digest(self) -> str:
        """Content address of the behavioural assumptions, for the ledger."""
        return digest_of(self.to_dict())

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_id": self.model_id,
            "tool_call_style": self.tool_call_style.value,
            "json_reliability": self.json_reliability.value,
            "context_tokens": self.context_tokens,
            "max_input_tokens": self.max_input_tokens,
            "supports_parallel_tool_calls": self.supports_parallel_tool_calls,
            "supports_streaming": self.supports_streaming,
            "supports_system_role": self.supports_system_role,
            "emits_reasoning": self.emits_reasoning,
            "supports_prompt_caching": self.supports_prompt_caching,
            "preferred_edit_mode": self.preferred_edit_mode.value,
            "input_usd_micros_per_mtok": self.input_usd_micros_per_mtok,
            "output_usd_micros_per_mtok": self.output_usd_micros_per_mtok,
            "typical_latency_millis": self.typical_latency_millis,
            "recovers_from_tool_error": self.recovers_from_tool_error,
            "eligible_roles": list(self.eligible_roles),
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "ModelBehaviorProfile":
        """Rebuild from a manifest/ledger payload. Unknown keys are ignored."""
        if not isinstance(raw, Mapping) or not raw.get("model_id"):
            raise ValueError("profile payload requires a model_id")
        return cls(
            model_id=str(raw["model_id"]),
            tool_call_style=ToolCallStyle(raw.get("tool_call_style", "json_schema")),
            json_reliability=JsonReliability(raw.get("json_reliability", "medium")),
            context_tokens=int(raw.get("context_tokens", 8_192)),
            max_input_tokens=int(raw.get("max_input_tokens", 6_144)),
            supports_parallel_tool_calls=bool(raw.get("supports_parallel_tool_calls", False)),
            supports_streaming=bool(raw.get("supports_streaming", True)),
            supports_system_role=bool(raw.get("supports_system_role", True)),
            emits_reasoning=bool(raw.get("emits_reasoning", False)),
            supports_prompt_caching=bool(raw.get("supports_prompt_caching", False)),
            preferred_edit_mode=EditMode(raw.get("preferred_edit_mode", "unified_diff")),
            input_usd_micros_per_mtok=int(raw.get("input_usd_micros_per_mtok", 0)),
            output_usd_micros_per_mtok=int(raw.get("output_usd_micros_per_mtok", 0)),
            typical_latency_millis=int(raw.get("typical_latency_millis", 4_000)),
            recovers_from_tool_error=bool(raw.get("recovers_from_tool_error", True)),
            eligible_roles=tuple(raw.get("eligible_roles") or ("implementer",)),
            notes=str(raw.get("notes", "")),
        )

    def degraded(self) -> "ModelBehaviorProfile":
        """The profile to use after a protocol failure: strictly more defensive.

        Used by the recovery policy so a second attempt does not repeat the
        assumption that just failed.
        """
        downgrade = {
            ToolCallStyle.NATIVE: ToolCallStyle.JSON_SCHEMA,
            ToolCallStyle.JSON_SCHEMA: ToolCallStyle.FENCED_JSON,
            ToolCallStyle.FENCED_JSON: ToolCallStyle.TEXT_GRAMMAR,
            ToolCallStyle.TEXT_GRAMMAR: ToolCallStyle.TEXT_GRAMMAR,
        }
        return replace(
            self,
            tool_call_style=downgrade[self.tool_call_style],
            supports_parallel_tool_calls=False,
            json_reliability=JsonReliability.LOW,
        )


#: The catalog. Conservative on purpose: an unknown model gets a profile that
#: assumes the *least* capability, so we degrade rather than break.
_DEFAULT = ModelBehaviorProfile(
    model_id="unknown",
    tool_call_style=ToolCallStyle.FENCED_JSON,
    json_reliability=JsonReliability.LOW,
    context_tokens=8_192,
    max_input_tokens=5_000,
    preferred_edit_mode=EditMode.SEARCH_REPLACE,
    eligible_roles=("implementer", "ranker", "summariser"),
    notes="fail-soft default for unregistered models",
)

PROFILES: dict[str, ModelBehaviorProfile] = {
    "anthropic/claude-sonnet-4": ModelBehaviorProfile(
        model_id="anthropic/claude-sonnet-4",
        tool_call_style=ToolCallStyle.NATIVE,
        json_reliability=JsonReliability.HIGH,
        context_tokens=200_000,
        max_input_tokens=180_000,
        supports_parallel_tool_calls=True,
        supports_prompt_caching=True,
        preferred_edit_mode=EditMode.SEARCH_REPLACE,
        input_usd_micros_per_mtok=3_000_000,
        output_usd_micros_per_mtok=15_000_000,
        typical_latency_millis=6_000,
        eligible_roles=("planner", "implementer", "reviewer", "synthesizer", "verifier"),
    ),
    "openai/gpt-4o-mini": ModelBehaviorProfile(
        model_id="openai/gpt-4o-mini",
        tool_call_style=ToolCallStyle.NATIVE,
        json_reliability=JsonReliability.HIGH,
        context_tokens=128_000,
        max_input_tokens=110_000,
        supports_parallel_tool_calls=True,
        preferred_edit_mode=EditMode.UNIFIED_DIFF,
        input_usd_micros_per_mtok=150_000,
        output_usd_micros_per_mtok=600_000,
        typical_latency_millis=2_500,
        eligible_roles=("implementer", "ranker", "summariser", "classifier"),
    ),
    "qwen2.5-coder:7b": ModelBehaviorProfile(
        model_id="qwen2.5-coder:7b",
        tool_call_style=ToolCallStyle.FENCED_JSON,
        json_reliability=JsonReliability.LOW,
        context_tokens=32_768,
        max_input_tokens=24_000,
        supports_system_role=True,
        preferred_edit_mode=EditMode.SEARCH_REPLACE,
        typical_latency_millis=9_000,
        recovers_from_tool_error=False,
        eligible_roles=("implementer", "ranker", "summariser", "classifier"),
        notes="local via ollama; zero marginal cost, high latency",
    ),
    "fake": ModelBehaviorProfile(
        model_id="fake",
        tool_call_style=ToolCallStyle.JSON_SCHEMA,
        json_reliability=JsonReliability.HIGH,
        context_tokens=1_000_000,
        max_input_tokens=900_000,
        typical_latency_millis=1,
        eligible_roles=("planner", "implementer", "reviewer", "synthesizer",
                        "verifier", "ranker", "summariser", "classifier"),
        notes="deterministic test double",
    ),
}


def register_profile(profile: ModelBehaviorProfile) -> None:
    """Add or replace a profile. Used by manifest loading and by measurement."""
    if not isinstance(profile, ModelBehaviorProfile):
        raise TypeError("register_profile requires a ModelBehaviorProfile")
    PROFILES[profile.model_id] = profile


def profile_for(model_id: str | None) -> ModelBehaviorProfile:
    """Resolve a profile, never raising. Unknown models get the cautious default.

    Matching is exact first, then on the bare model name after the provider
    prefix, so ``openrouter:openai/gpt-4o-mini`` and ``openai/gpt-4o-mini``
    resolve to the same behaviour.
    """
    if not model_id:
        return _DEFAULT
    key = model_id.strip()
    if key in PROFILES:
        return PROFILES[key]
    for prefix in ("openrouter:", "ollama:", "openai:", "anthropic:"):
        if key.startswith(prefix):
            bare = key[len(prefix):]
            if bare in PROFILES:
                return PROFILES[bare]
            key = bare
            break
    if key in PROFILES:
        return PROFILES[key]
    # Tolerate version suffixes: `model-name:tag` / `model-name@date`.
    base = key.split("@")[0]
    if base in PROFILES:
        return PROFILES[base]
    return replace(_DEFAULT, model_id=model_id)
