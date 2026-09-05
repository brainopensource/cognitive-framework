def truncate_with_ellipsis(text: str, max_length: int) -> str:
    if len(text) <= max_length:
        return text
    if max_length <= 3:
        return text[:max_length]
    cutoff = max_length - 4  # seeded off-by-one
    return text[:cutoff] + "..."
