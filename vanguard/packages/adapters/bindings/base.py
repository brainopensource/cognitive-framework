"""Base protocols and registry for namespaced domain binding providers.

Owning contract: ADR-0088 §1.7, REQ-HARN-001, GTS-13C §7.3.
Hexagonal boundary: Adapters package (imports only domain and ports).
"""

from __future__ import annotations

from typing import Any, Mapping, Protocol, Sequence, runtime_checkable


@runtime_checkable
class BindingProvider(Protocol):
    """Protocol for namespaced domain verb binding providers."""

    @property
    def namespace(self) -> str:
        """The domain namespace (e.g. 'table', 'code', 'math')."""
        ...

    @property
    def supported_verbs(self) -> tuple[str, ...]:
        """Canonical verbs supported by this provider (e.g. ('table.read', 'table.patch'))."""
        ...

    def create_adapter(self, verb: str, environment: Any, **kwargs: Any) -> Any:
        """Instantiate an effect adapter for the specified verb."""
        ...


class DomainBindingRegistry:
    """Registry of namespaced binding providers preventing global table sprawl."""

    def __init__(self, providers: Sequence[BindingProvider] | None = None) -> None:
        self._providers: dict[str, BindingProvider] = {}
        self._by_verb: dict[str, BindingProvider] = {}
        if providers:
            for provider in providers:
                self.register(provider)

    def register(self, provider: BindingProvider) -> None:
        namespace = provider.namespace
        verbs = tuple(provider.supported_verbs)
        if not isinstance(namespace, str) or not namespace:
            raise ValueError("binding provider namespace must be a non-empty string")
        if not verbs or any(not isinstance(verb, str) or not verb for verb in verbs):
            raise ValueError(f"binding provider {namespace!r} must declare non-empty verbs")
        if len(set(verbs)) != len(verbs):
            raise ValueError(f"binding provider {namespace!r} declares duplicate verbs")

        existing_provider = self._providers.get(namespace)
        if existing_provider is not None and existing_provider is not provider:
            raise ValueError(f"binding provider namespace already registered: {namespace!r}")
        collisions = [verb for verb in verbs
                      if (owner := self._by_verb.get(verb)) is not None and owner is not provider]
        if collisions:
            raise ValueError(f"binding verbs already registered: {sorted(collisions)!r}")

        self._providers[namespace] = provider
        for verb in verbs:
            self._by_verb[verb] = provider

    def get_provider(self, namespace: str) -> BindingProvider | None:
        return self._providers.get(namespace)

    def get_provider_for_verb(self, verb: str) -> BindingProvider | None:
        return self._by_verb.get(verb)

    def is_supported(self, verb: str) -> bool:
        return verb in self._by_verb

    @property
    def all_verbs(self) -> tuple[str, ...]:
        return tuple(sorted(self._by_verb.keys()))

    @classmethod
    def default(cls) -> "DomainBindingRegistry":
        from .code import CodeBindingProvider
        from .table import TableBindingProvider
        return cls([CodeBindingProvider(), TableBindingProvider()])
