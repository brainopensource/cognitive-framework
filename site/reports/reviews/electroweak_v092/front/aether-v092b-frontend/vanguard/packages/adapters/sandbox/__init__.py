"""Sandbox adapter family; sibling adapter families must not import this package."""

from .fake import NON_CONTAINED_MARK, FakeSandboxRunner
from .rootless import RootlessSandboxRunner

__all__ = ["FakeSandboxRunner", "NON_CONTAINED_MARK", "RootlessSandboxRunner"]
