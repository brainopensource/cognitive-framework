"""Domain binding providers package."""

from __future__ import annotations

from .base import BindingProvider, DomainBindingRegistry
from .code import CodeAdapterOutcome, CodeBindingProvider, CodeEffectAdapter
from .repo import RepoAdapterOutcome, RepoBindingProvider, RepoEffectAdapter
from .table import TableAdapterOutcome, TableBindingProvider, TableEffectAdapter

__all__ = [
    "BindingProvider",
    "CodeAdapterOutcome",
    "CodeBindingProvider",
    "CodeEffectAdapter",
    "DomainBindingRegistry",
    "RepoAdapterOutcome",
    "RepoBindingProvider",
    "RepoEffectAdapter",
    "TableAdapterOutcome",
    "TableBindingProvider",
    "TableEffectAdapter",
]
