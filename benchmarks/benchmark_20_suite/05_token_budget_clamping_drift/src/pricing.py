def calculate_cost_usd(tokens: int, rate_per_million: float) -> float:
    return (tokens / 1_000_000.0) * rate_per_million
