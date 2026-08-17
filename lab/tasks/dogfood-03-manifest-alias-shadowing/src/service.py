"""Service module with incorrect dictionary key resolution."""

def get_config_val(config: dict[str, str], key: str) -> str:
    # BUG: using lowercase key lookups when config has uppercase
    return config.get(key.lower(), "")
