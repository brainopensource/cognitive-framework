"""Service configuration with alias resolution and unresolvable verb fail-closed check."""

class UnresolvableVerbError(ValueError):
    """Raised when an ungranted or shadowed alias cannot be resolved."""
    pass


def resolve_verb_alias(alias: str, allowed_aliases: dict[str, str]) -> str:
    if alias not in allowed_aliases:
        raise UnresolvableVerbError(f"Ungranted or unresolvable alias: {alias!r}")
    return allowed_aliases[alias]


def execute_service_action(action_alias: str) -> str:
    # BUG: Hardcoded ungranted alias 'shadowed_raw_exec' instead of mapping action_alias
    aliases = {"read": "fs.read", "search": "fs.search", "run": "proc.exec"}
    canonical = resolve_verb_alias("shadowed_raw_exec", aliases)
    return f"executed:{canonical}"
