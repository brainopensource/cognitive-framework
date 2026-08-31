from __future__ import annotations

import importlib.metadata
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Mapping, Optional, Protocol, Sequence, Tuple

from .models import Diagnostic, Metric, ProviderResult


class AtlasContext(Protocol):
    root: object
    profile: Any


class Provider(Protocol):
    name: str
    def available(self, ctx: AtlasContext) -> bool: ...
    def collect(self, ctx: AtlasContext) -> ProviderResult: ...


class Analyzer(Protocol):
    name: str
    def analyze(self, ctx: AtlasContext, results: Sequence[ProviderResult]) -> Sequence[Diagnostic | Metric]: ...


@dataclass(frozen=True)
class PluginManifest:
    """Descriptor metadata for an LDA plugin."""
    name: str
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    enabled: bool = True
    tags: Tuple[str, ...] = field(default_factory=tuple)


@dataclass
class PluginExecutionMetric:
    """Execution telemetry for plugin performance tracking."""
    plugin_name: str
    execution_time_ms: float
    entities_collected: int
    relations_collected: int
    success: bool
    error_message: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


class Plugin(Protocol):
    """Extensible plugin protocol for repository intelligence."""
    manifest: PluginManifest

    def providers(self) -> Sequence[Provider]: ...
    def analyzers(self) -> Sequence[Analyzer]: ...
    def skeletonizers(self) -> Mapping[str, Callable[[str], str]]: ...


class ProviderRegistry:
    def __init__(self) -> None:
        self._providers: list[Provider] = []

    def register(self, provider: Provider) -> None:
        self._providers.append(provider)

    def providers(self) -> tuple[Provider, ...]:
        return tuple(self._providers)


class PluginManager:
    """Authoritative lifecycle and execution engine for LDA plugins."""

    _instance: Optional[PluginManager] = None

    def __init__(self) -> None:
        self._plugins: Dict[str, Any] = {}
        self._enabled: Dict[str, bool] = {}
        self._custom_skeletonizers: Dict[str, Callable[[str], str]] = {}
        self._metrics_log: List[PluginExecutionMetric] = []

    @classmethod
    def get_instance(cls) -> PluginManager:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register_plugin(self, plugin: Any) -> None:
        """Register a plugin instance with optional providers, analyzers, and skeletonizers."""
        name = getattr(plugin, "name", None) or getattr(getattr(plugin, "manifest", None), "name", None) or plugin.__class__.__name__
        self._plugins[name] = plugin
        self._enabled[name] = True

        # Register custom skeletonizers if exposed
        if hasattr(plugin, "skeletonizers") and callable(plugin.skeletonizers):
            for ext, fn in plugin.skeletonizers().items():
                self._custom_skeletonizers[ext.lower()] = fn

    def unregister_plugin(self, name: str) -> None:
        """Unregister / remove a plugin."""
        self._plugins.pop(name, None)
        self._enabled.pop(name, None)

    def set_plugin_enabled(self, name: str, enabled: bool) -> bool:
        """Toggle a plugin (for fast rollback if performance or quality degrades)."""
        if name in self._plugins:
            self._enabled[name] = enabled
            return True
        return False

    def is_plugin_enabled(self, name: str) -> bool:
        return self._enabled.get(name, False)

    def list_plugins(self) -> List[Dict[str, Any]]:
        """List registered plugins with their active status."""
        out = []
        for name, p in self._plugins.items():
            manifest = getattr(p, "manifest", None)
            out.append({
                "name": name,
                "version": getattr(manifest, "version", "1.0.0") if manifest else "1.0.0",
                "description": getattr(manifest, "description", "") if manifest else "",
                "enabled": self._enabled.get(name, True),
            })
        return out

    def get_providers(self) -> List[Provider]:
        """Collect all providers from active plugins."""
        providers: List[Provider] = []
        for name, p in self._plugins.items():
            if not self._enabled.get(name, True):
                continue
            if hasattr(p, "providers") and callable(p.providers):
                providers.extend(p.providers())
        return providers

    def get_analyzers(self) -> List[Analyzer]:
        """Collect all analyzers from active plugins."""
        analyzers: List[Analyzer] = []
        for name, p in self._plugins.items():
            if not self._enabled.get(name, True):
                continue
            if hasattr(p, "analyzers") and callable(p.analyzers):
                analyzers.extend(p.analyzers())
        return analyzers

    def get_custom_skeletonizer(self, extension: str) -> Optional[Callable[[str], str]]:
        return self._custom_skeletonizers.get(extension.lower())

    def record_metric(self, metric: PluginExecutionMetric) -> None:
        self._metrics_log.append(metric)

    def get_metrics_summary(self) -> List[Dict[str, Any]]:
        """Return execution metrics aggregated by plugin."""
        summary: Dict[str, Dict[str, Any]] = {}
        for m in self._metrics_log:
            if m.plugin_name not in summary:
                summary[m.plugin_name] = {
                    "runs": 0,
                    "total_time_ms": 0.0,
                    "total_entities": 0,
                    "total_relations": 0,
                    "errors": 0,
                }
            s = summary[m.plugin_name]
            s["runs"] += 1
            s["total_time_ms"] += m.execution_time_ms
            s["total_entities"] += m.entities_collected
            s["total_relations"] += m.relations_collected
            if not m.success:
                s["errors"] += 1
        return [
            {
                "plugin_name": k,
                "avg_time_ms": round(v["total_time_ms"] / max(v["runs"], 1), 3),
                "total_entities": v["total_entities"],
                "total_relations": v["total_relations"],
                "errors": v["errors"],
            }
            for k, v in summary.items()
        ]

    def discover_installed_plugins(self) -> int:
        """Auto-discover plugins registered via setuptools/pip entry_points."""
        discovered = 0
        try:
            eps = importlib.metadata.entry_points(group="lda.plugins")
            for ep in eps:
                try:
                    plugin_cls = ep.load()
                    plugin_instance = plugin_cls()
                    self.register_plugin(plugin_instance)
                    discovered += 1
                except Exception:
                    pass
        except Exception:
            pass
        return discovered


__all__ = [
    "Analyzer",
    "AtlasContext",
    "Plugin",
    "PluginExecutionMetric",
    "PluginManager",
    "PluginManifest",
    "Provider",
    "ProviderRegistry",
]

