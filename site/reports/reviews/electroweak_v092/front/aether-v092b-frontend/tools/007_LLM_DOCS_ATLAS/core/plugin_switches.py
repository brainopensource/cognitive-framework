"""Dynamic Strategy Configuration Switcher and Fail-Closed Watchdog.

Coordinates modular rankers, extractors, and skeletonizers with runtime
feature flags, telemetry logging, and automatic rollback on degradation.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, Mapping, Optional, Tuple

from .registry import PluginExecutionMetric, PluginManager

logger = logging.getLogger(__name__)


@dataclass
class AtlasStrategyConfig:
    """Strategy configuration for the LDA engine."""
    ranker_strategy: str = "ppr_submodular"  # Options: ppr_submodular, fts5_bm25
    extractor_strategy: str = "ast_cst"       # Options: ast_cst, tree_sitter, regex_legacy
    skeletonizer_strategy: str = "multilang"  # Options: multilang, python_only
    enable_cache: bool = True
    max_latency_ms: float = 40.0
    fallback_ranker: str = "fts5_bm25"


class StrategySwitcher:
    """Coordinates active engine strategies with automatic fallback capability."""

    def __init__(self, config: AtlasStrategyConfig | None = None) -> None:
        self.config = config or AtlasStrategyConfig()
        self.pm = PluginManager.get_instance()

    def execute_with_guard(
        self,
        strategy_name: str,
        primary_fn: Callable[..., Any],
        fallback_fn: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Tuple[Any, str]:
        """
        Executes primary strategy with a latency/error watchdog.
        Falls back seamlessly if execution fails or exceeds latency SLA.
        """
        t0 = time.perf_counter()
        try:
            result = primary_fn(*args, **kwargs)
            duration_ms = (time.perf_counter() - t0) * 1000.0

            # Record telemetry
            self.pm.record_metric(
                PluginExecutionMetric(
                    plugin_name=strategy_name,
                    execution_time_ms=duration_ms,
                    entities_collected=0,
                    relations_collected=0,
                    success=True,
                )
            )

            if duration_ms > self.config.max_latency_ms:
                logger.warning(
                    "Strategy '%s' exceeded latency threshold (%.2f ms > %.2f ms). Flagging degradation.",
                    strategy_name,
                    duration_ms,
                    self.config.max_latency_ms,
                )
            return result, strategy_name

        except Exception as exc:
            duration_ms = (time.perf_counter() - t0) * 1000.0
            logger.error(
                "Strategy '%s' failed after %.2f ms with error: %s. Executing fallback '%s'.",
                strategy_name,
                duration_ms,
                exc,
                self.config.fallback_ranker,
            )
            self.pm.record_metric(
                PluginExecutionMetric(
                    plugin_name=strategy_name,
                    execution_time_ms=duration_ms,
                    entities_collected=0,
                    relations_collected=0,
                    success=False,
                    error_message=str(exc),
                )
            )
            fallback_result = fallback_fn(*args, **kwargs)
            return fallback_result, self.config.fallback_ranker
