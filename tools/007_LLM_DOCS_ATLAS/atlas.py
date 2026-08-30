from __future__ import annotations
from pathlib import Path
from .core.config import AtlasContext
from .core.models import ProviderResult
from .core.registry import ProviderRegistry
from .providers.git import GitProvider
from .providers.knowledge import KnowledgeProvider

def default_registry() -> ProviderRegistry:
    registry = ProviderRegistry(); registry.register(KnowledgeProvider()); registry.register(GitProvider()); return registry

def collect(ctx: AtlasContext, registry: ProviderRegistry | None = None) -> list[ProviderResult]:
    results = []
    for provider in (registry or default_registry()).providers():
        try:
            if provider.available(ctx): results.append(provider.collect(ctx))
        except Exception as exc:
            from .core.models import Diagnostic
            results.append(ProviderResult(provider.name, diagnostics=[Diagnostic("error", "PROVIDER_FAILURE", str(exc), provider=provider.name)]))
    return results
