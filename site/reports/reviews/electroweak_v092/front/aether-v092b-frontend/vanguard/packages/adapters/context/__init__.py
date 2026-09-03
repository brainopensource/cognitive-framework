"""Context adapter family; sibling adapter families must not import this package."""

from .window import DefaultContextAdapter

__all__ = ["DefaultContextAdapter"]
