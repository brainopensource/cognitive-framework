"""Model behaviour declarations (domain values, no provider imports)."""

from .profile import (
    EditMode,
    JsonReliability,
    ModelBehaviorProfile,
    PROFILES,
    ToolCallStyle,
    profile_for,
    register_profile,
)

__all__ = [
    "EditMode",
    "JsonReliability",
    "ModelBehaviorProfile",
    "PROFILES",
    "ToolCallStyle",
    "profile_for",
    "register_profile",
]
