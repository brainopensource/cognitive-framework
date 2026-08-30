from __future__ import annotations
from typing import Protocol
from .models import ProviderResult

class AtlasContext(Protocol):
    root: object

class Provider(Protocol):
    name: str
    def available(self, ctx: AtlasContext) -> bool: ...
    def collect(self, ctx: AtlasContext) -> ProviderResult: ...

class ProviderRegistry:
    def __init__(self) -> None: self._providers: list[Provider] = []
    def register(self, provider: Provider) -> None: self._providers.append(provider)
    def providers(self) -> tuple[Provider, ...]: return tuple(self._providers)
