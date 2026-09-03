"""Constructs stable, cache-friendly prompt prefixes without ephemeral timestamps."""

from __future__ import annotations

from typing import Sequence


def build_stable_prefix(
    constitutional_rules: Sequence[str],
    role_contract: str,
    tool_schemas_summary: str,
) -> str:
    """Combine stable prompt segments into a cache-optimal invariant prefix."""
    parts = []
    if constitutional_rules:
        parts.append("# Core Constraints")
        parts.extend(f"- {rule}" for rule in constitutional_rules)
    if role_contract:
        parts.append("\n# Role Contract")
        parts.append(role_contract.strip())
    if tool_schemas_summary:
        parts.append("\n# Available Operations")
        parts.append(tool_schemas_summary.strip())
    return "\n".join(parts)
