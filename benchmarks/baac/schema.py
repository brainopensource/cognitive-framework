"""BaaC Declarative Schemas, Taxonomy, and Contracts.

Defines:
1. Taxonomy Enums: Scope, ContextBracket, Tier, EvalType, Attribution.
2. Challenge Specification and Metadata Contract.
3. Execution Result and Telemetry Records.
4. Model Tier Banding and Cost Profiles.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
import hashlib
import json
from pathlib import Path
import time
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple, Union


class BenchmarkScope(str, Enum):
    SINGLE = "single"          # Single-file function/bugfix
    MULTI = "multi"            # Multi-file dependency/coordination
    GREENFIELD = "greenfield"  # From-scratch package/module construction
    REFACTOR = "refactor"      # AST refactoring & structural evolution
    SWE = "swe"                # Real-world repository issue / bug repair


class ContextBracket(str, Enum):
    C2K = "2K"      # <= 2,048 tokens
    C4K = "4K"      # <= 4,096 tokens
    C8K = "8K"      # <= 8,192 tokens
    C16K = "16K"    # <= 16,384 tokens
    C32K = "32K"    # <= 32,768 tokens
    C64K = "64K"    # <= 65,536 tokens
    C128K = "128K"  # <= 131,072 tokens
    C200K = "200K"  # <= 200,000+ tokens


class BenchmarkTier(str, Enum):
    TIER_1 = "tier-1"  # Easy: single-function logic, formula fix, clamp, basic parser
    TIER_2 = "tier-2"  # Medium-Easy: multi-file dependencies, import cycles, state sync
    TIER_3 = "tier-3"  # Medium: search & refactor, event bus, middleware, JSON patch
    TIER_4 = "tier-4"  # Medium-Hard: circuit breaker, rate limiter, saga, token bucket
    TIER_5 = "tier-5"  # Hard: persistent B-tree, immutable trie, async loop, DAG
    TIER_6 = "tier-6"  # Frontier / SOTA: Raft consensus, compiler optimizer, MVCC engine


class EvalType(str, Enum):
    ORACLE = "oracle"      # Automated deterministic unit/integration test oracle
    AI_JUDGE = "ai_judge"  # LLM-as-a-Judge semantic rubric evaluation
    HYBRID = "hybrid"      # Automated oracle + AI judge qualitative scoring
    HUMAN = "human"        # Human evaluation review hook


class RootAttribution(str, Enum):
    PASS = "PASS"                                  # 100% green verified assertions
    LLM_COGNITIVE_ERROR = "LLM_COGNITIVE_ERROR"    # Model generated faulty code / failed assertions
    HARNESS_ERROR = "HARNESS_ERROR"                # Agent harness exception, crash, or loop abandonment
    BUDGET_EXHAUSTED = "BUDGET_EXHAUSTED"          # Aborted due to token/cost/turn cap limit
    DATASET_INVALID = "DATASET_INVALID"            # Challenge source drift or broken oracle test script


@dataclass(frozen=True, slots=True)
class ChallengeMetadata:
    """Free-form and structured metadata associated with a benchmark challenge."""

    id: str
    name: str
    scope: str
    context_bracket: str
    tier: str
    difficulty: int
    timeout_seconds: int = 30
    entrypoint: str = "src/main.py"
    eval_type: str = "oracle"
    tags: tuple[str, ...] = ()
    extra: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> ChallengeMetadata:
        extra_keys = {
            k: v for k, v in data.items()
            if k not in {
                "id", "name", "scope", "context_bracket", "tier",
                "difficulty", "timeout_seconds", "entrypoint", "eval_type", "tags", "metadata"
            }
        }
        meta_field = dict(data.get("metadata", {}))
        meta_field.update(extra_keys)
        return cls(
            id=str(data.get("id", "")),
            name=str(data.get("name", "")),
            scope=str(data.get("scope", "single")),
            context_bracket=str(data.get("context_bracket", "2K")),
            tier=str(data.get("tier", "tier-1")),
            difficulty=int(data.get("difficulty", 1)),
            timeout_seconds=int(data.get("timeout_seconds", 30)),
            entrypoint=str(data.get("entrypoint", "src/main.py")),
            eval_type=str(data.get("eval_type", "oracle")),
            tags=tuple(data.get("tags", ())),
            extra=meta_field,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "scope": self.scope,
            "context_bracket": self.context_bracket,
            "tier": self.tier,
            "difficulty": self.difficulty,
            "timeout_seconds": self.timeout_seconds,
            "entrypoint": self.entrypoint,
            "eval_type": self.eval_type,
            "tags": list(self.tags),
            "metadata": dict(self.extra),
        }
