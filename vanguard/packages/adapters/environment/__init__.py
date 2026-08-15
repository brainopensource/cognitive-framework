"""Environment adapters family (ICD §4)."""

from .fake import FakeEnvironment
from .git import GitEnvironment

__all__ = ["FakeEnvironment", "GitEnvironment"]
