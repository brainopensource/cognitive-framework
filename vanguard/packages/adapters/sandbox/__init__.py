"""Sandbox adapter family; sibling adapter families must not import this package."""

from .fake import NON_CONTAINED_MARK, FakeSandboxRunner

__all__ = ["FakeSandboxRunner", "NON_CONTAINED_MARK"]
