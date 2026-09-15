"""Planted domain I/O — must fail check_boundaries / check_domain_blindness."""

from pathlib import Path


def load() -> str:
    return Path("secret.toml").read_text(encoding="utf-8")
